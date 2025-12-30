import fastmcp

from config import config
from db.vector_store import search_text_chunks


# Create MCP server
mcp_app = fastmcp.FastMCP("Bible-study-bot MCP")


@mcp_app.tool()
async def search_bible_chunks(query: str) -> list[str]:
    """
    Search for Bible verses or text chunks relevant to the query.
    Use this tool to find relevant scripture when the user asks about specific topics, verses, or theological concepts in the Bible.
    """
    return search_text_chunks(
        query,
        filters={"category": "bible"}
    )


if __name__ == "__main__":
    # Use streamable-http transport for production
    mcp_app.run(
        transport=config["mcp"]["server"]["transport"],
        host="0.0.0.0", port=config["mcp"]["server"]["port"])
