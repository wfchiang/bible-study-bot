import asyncio
import httpx
import os
import json
from typing import List

from langchain_core.messages import SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from config import config


class CustomHTTPClient(httpx.Client):
    def __init__(self, *args, **kwargs):
        kwargs.pop("proxies", None)  # To fix an OpenAI issue: Remove the 'proxies' argument if present
        super().__init__(*args, **kwargs)

class CustomHTTPAsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        kwargs.pop("proxies", None)  # To fix an OpenAI issue: Remove the 'proxies' argument if present
        super().__init__(*args, **kwargs)


# 1. Global variable for the system prompt. You can edit this!
SYSTEM_PROMPT = config["system_prompt"]


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

    httpx_client = CustomHTTPClient()
    httpx_async_client = CustomHTTPAsyncClient()

    mcp_client = MultiServerMCPClient({
        "service": {
            "transport": config["mcp"]["transport"],
            "url": os.environ["BSB_MCP_SERVER"],
        }
    })

    mcp_tools = await mcp_client.get_tools()
    tools: List = mcp_tools + create_web_search_tool()

    llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14",
                     http_client=httpx_client,
                     http_async_client=httpx_async_client,)
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: MessagesState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
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
