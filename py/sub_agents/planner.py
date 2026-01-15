import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from config import httpx_client, httpx_async_client, mcp_client
from data.definitions import PROFESSION_OF_FAITH, AgentState


prompt_template = """你是一個基督徒聖經學者。你的信仰如下：
{profession_of_faith}

你可以提供以下服務項目 (服務名稱: 描述)：
{service_items}

你即將要處裡一個使用者的請求。請根據你的信仰和服務項目，提出一個詳細的計畫。
你的回應將會是一個以 JSON 物件描述的 DAG (directed acyclic graph)，其中包含一個或多個節點，每個節點代表一個任務或步驟。
每個節點應包含以下欄位：
- id: 任務的唯一識別碼，integer
- service: 服務名稱 (必須是你能提供的服務項目之一)
- input: 服務的輸入參數 (str)
- children: 子任務的 id 陣列 (可以是空陣列)

請確保你的回應是有效的 JSON 格式，並且符合以下結構。

{{
    "root": <root_node_id>,
    "nodes": [
        {{
            "id": <node_id>,
            "service": <service_name>,
            "input": <service_input>,
            "children": [<child_node_id_1>, <child_node_id_2>, ...]
        }},
        ...
    ]
}}

請注意：
- 有可能使用者的請求並不複雜，因此計畫可能只有一個節點。

現在，請根據以下使用者的請求，生成計畫。
使用者請求：{user_request}
"""

services = {
    "question_answering": "回答有關聖經內容的問題",
    "small_group_discussion": "提供小組討論的指引和問題",
    "misc": "其他相關 (或非相關) 的聖經學習服務",}


def _encode_service_items(services_: dict = services) -> str:
    items = []
    for k in services_.keys():
        items.append(f"- {k}: {services_[k]}")
    return "\n".join(items)


async def create_agent() -> StateGraph:
    mcp_tools = await mcp_client.get_tools()
    tools = mcp_tools

    llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14",
                     http_client=httpx_client,
                     http_async_client=httpx_async_client,)
    llm_with_tools = llm.bind_tools(tools)

    def call_llm(state: AgentState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_llm)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile()


@tool("make_plan", description="根據使用者的請求，生成計畫。")
async def make_plan(user_request: str) -> dict:
    """
    According to the user's request, generate a plan.
    The plan should be a JSON object describing a directed acyclic graph (DAG),
    """
    agent = await create_agent()
    prompt = prompt_template.format(
        profession_of_faith=PROFESSION_OF_FAITH,
        service_items=_encode_service_items(services),
        user_request=user_request,
    )
    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })
    assert isinstance(response, dict), f"Invalid response type: {type(response)}"
    last_message: AIMessage = response["messages"][-1]
    assert isinstance(last_message, AIMessage), "Last message is not an AIMessage"

    plan = json.loads(last_message.content)
    return plan


if __name__ == "__main__":
    import asyncio
    async def main():
        plan = await make_plan.ainvoke({
            "user_request": "遵守神的命令會帶來真正的喜樂嗎?為什麼?"})
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    asyncio.run(main())