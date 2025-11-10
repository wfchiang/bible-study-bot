import os
from typing import List

from dotenv import load_dotenv
from langchain.agents import create_agent as create_langchain_agent
from langchain_tavily import TavilySearch

from .config import config

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# 1. Global variable for the system prompt. You can edit this!
SYSTEM_PROMPT = config["system_prompt"]


def check_env_vars() -> None:
    """
    Checks if the required environment variables are set.
    Raises an exception if any are missing.
    """
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


def create_agent():
    """
    Creates a LangChain agent equipped with a web search tool.

    The agent uses the ReAct (Reasoning and Acting) framework to determine
    which tool to use to best answer the user's query.

    Make sure to set the following environment variables:
    - OPENAI_API_KEY: Your API key for OpenAI.
    - TAVILY_API_KEY: Your API key for Tavily Search.

    Returns:
        An initialized LangChain AgentExecutor.
    """
    check_env_vars()

    tools: List= [TavilySearch(max_results=3)]

    agent = create_langchain_agent(
        model="gpt-4o",
        # tools=tools,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


if __name__ == "__main__":
    agent = create_agent()
    # result = agent.invoke({
    #     "messages": [
    #         {"role": "user", "content": "甚麼是 '義人'"}
    #     ]
    # })
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "今天是幾月幾號? 天氣如何?"}
        ]
    })
    print(result)
