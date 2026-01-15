import os
import json
from typing import List

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from config import httpx_client, httpx_async_client, mcp_client
from data.definitions import AgentState, PROFESSION_OF_FAITH
from sub_agents.planner import make_plan as tool_make_plan


# 1. Global variable for the system prompt. You can edit this!
SYSTEM_PROMPT = """你是一位聖經學習助手，專注於幫助使用者理解和學習聖經內容。請根據使用者的問題，本著聖經的信息來回到以聖經為出發點的答案。
你的信仰宣言如下：
{profession_of_faith}

請先制定計畫，再回答問題。
""".format(
    profession_of_faith=PROFESSION_OF_FAITH)


def check_env_vars() -> None:
    """
    Checks if the required environment variables are set.
    Raises an exception if any are missing.
    """
    required_vars = ["BSB_MCP_SERVER", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


async def create_agent() -> StateGraph:
    check_env_vars()

    mcp_tools = await mcp_client.get_tools()
    tools: List = mcp_tools + create_web_search_tool() + [tool_make_plan]

    llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14",
                     http_client=httpx_client,
                     http_async_client=httpx_async_client,)
    llm_with_tools = llm.bind_tools(tools)

    def call_llm(state: AgentState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
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


def create_web_search_tool() -> List:
    """
    Seek for the environment variables and return the web search tool.
    """
    tools = []
    if "TAVILY_API_KEY" in os.environ:
        tools.append(TavilySearch(max_results=3))
    return tools


if __name__ == "__main__":
    import asyncio
    async def main():
        agent = await create_agent()

        result = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "遵守神的命令會帶來真正的喜樂嗎?為什麼?"}
            ]
        })
        print(json.dumps(
            [m.model_dump() if hasattr(m, "model_dump") else m.dict() for m in result["messages"]],
            indent=4,
            ensure_ascii=False
        ))
    asyncio.run(main())
