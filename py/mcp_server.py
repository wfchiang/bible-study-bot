import logging

import fastmcp

from config import config, get_reranker_model
from db.vector_store import search_text_chunks


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp_app = fastmcp.FastMCP("Bible-study-bot MCP")

reranker_model = get_reranker_model()
reranker_threshold = config["models"]["reranker"].get("threshold", 0.5)


@mcp_app.tool(
        name="search_bible_chunks",
        description="搜寻与查找相关的圣经经文或文本片段，以回答用户关于特定主题、经文或神学概念的问题。")
async def search_bible_chunks(
        query: str,
        threshold: float = reranker_threshold,
        top_k: int = 10) -> list[dict]:
    """
    Search for Bible verses or text chunks relevant to the query.
    Use this tool to find relevant scripture when the user asks about specific topics, verses, or theological concepts in the Bible.
    """
    assert top_k > 0, "top_k must be greater than 0"
    logger.info("Searching Bible chunks for query: %s", query)

    text_chunks = search_text_chunks(
        query,
        filters={"category": "bible"},
        top_k=top_k * 5,)
    logger.info("Found %s text chunks", len(text_chunks))

    # Rerank the results using the reranker model
    points_text = [tc["text"] for tc in text_chunks]
    reranker_result = reranker_model.rank(
        query=query, documents=points_text)
    reranker_result = [
        rr for rr in reranker_result if rr["score"] >= threshold]

    ranked_bible_chunks = [
        text_chunks[rr["corpus_id"]]
        for rr in reranker_result]
    if len(ranked_bible_chunks) > top_k:
        ranked_bible_chunks = ranked_bible_chunks[:top_k]
    logger.info("Returning %s ranked Bible chunks", len(ranked_bible_chunks))
    return ranked_bible_chunks


if __name__ == "__main__":
    # Use streamable-http transport for production
    mcp_app.run(
        transport=config["mcp"]["server"]["transport"],
        host="0.0.0.0", port=config["mcp"]["server"]["port"])
