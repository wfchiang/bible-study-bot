import logging

import fastmcp

from config import config
from db.vector_store import search_text_chunks


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp_app = fastmcp.FastMCP("Bible-study-bot MCP")


@mcp_app.tool(
        name="search_bible_chunks",
        description="Search for Bible verses or text chunks relevant to the query.")
async def search_bible_chunks(query: str) -> list[str]:
    """
    Search for Bible verses or text chunks relevant to the query.
    Use this tool to find relevant scripture when the user asks about specific topics, verses, or theological concepts in the Bible.
    """
    logger.info("Searching Bible chunks for query: %s", query)
    text_chunks = search_text_chunks(
        query,
        filters={"category": "bible"}
    )
    logger.info("Found %s text chunks", len(text_chunks))
    return [
        tc["text"]
        for tc in text_chunks]


if __name__ == "__main__":
    # Use streamable-http transport for production
    mcp_app.run(
        transport=config["mcp"]["server"]["transport"],
        host="0.0.0.0", port=config["mcp"]["server"]["port"])
