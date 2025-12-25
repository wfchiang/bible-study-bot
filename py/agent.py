import os
import datetime
from typing import List

from dotenv import load_dotenv

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from config import config
from tools import search_bible_chunks

load_dotenv()

# 1. Global variable for the system prompt. You can edit this!
SYSTEM_PROMPT = config["system_prompt"]


def check_env_vars() -> None:
    """
    Checks if the required environment variables are set.
    Raises an exception if any are missing.
    """
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


def create_agent() -> StateGraph:
    check_env_vars()

    tools: List = []
    tools += create_web_search_tool()
    tools.append(search_bible_chunks)

    llm = ChatOpenAI(model="gpt-4o")
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
    agent = create_agent()
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "甚麼是 '義人'"}
        ]
    })
    # result = agent.invoke({
    #     "messages": [
    #         {"role": "user", "content": "今天是幾月幾號? 天氣如何?"}
    #     ]
    # })
    print(result)
