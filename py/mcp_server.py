import logging
from pathlib import Path

import fastmcp

from config import config
from data.definitions import BibleBook, BibleVerse
from data.utils import make_bible_quote
from data.loaders import load_bible_from_dir
from db.vector_store import search_text_chunks


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp_app = fastmcp.FastMCP("Bible-study-bot MCP")

bible_versions = {}
for bible_version_path in config["data"]["bible_versions"]:
    bible_version = load_bible_from_dir(
        Path(bible_version_path))
    bible_versions[bible_version.version] = bible_version
assert len(bible_versions) > 0


@mcp_app.tool(
        name="get_bible_verses",
        description="提取特定的圣经经文或经文范围。")
async def get_bible_verses(
        book: str,
        from_chapter: int,
        from_verse: int,
        to_chapter: int | None = None,
        to_verse: int | None = None,
        version: str | None = None) -> dict:
    to_chapter = to_chapter or from_chapter
    to_verse = to_verse or from_verse

    assert 1 <= from_chapter <= to_chapter
    assert 1 <= from_verse and 1 <= to_verse
    if from_chapter == to_chapter:
        assert from_verse <= to_verse

    version = version or list(bible_versions.keys())[0]
    bible_version = bible_versions[version]

    bible_book = None
    for bb in bible_version.books:
        if bb.book == book:
            bible_book = bb
            break
    assert isinstance(bible_book, BibleBook)

    got_from_v = False
    got_to_v = False
    verses = []
    for bv in bible_book.verses:
        if not got_from_v:
            if bv.chapter == from_chapter and bv.verse == from_verse:
                got_from_v = True
        if got_from_v:
            verses.append(bv)
        if not got_to_v:
            if bv.chapter == to_chapter and bv.verse == to_verse:
                got_to_v = True
        if got_to_v:
            break
    assert got_from_v, "Invalid 'from' verse"
    assert got_to_v, "Invalid 'to' verse"

    bible_quote = make_bible_quote(
        book=book, verses=verses)
    return bible_quote.model_dump()


@mcp_app.tool(
        name="search_bible_chunks",
        description="搜寻与查找相关的圣经经文或文本片段，以回答用户关于特定主题、经文或神学概念的问题。")
async def search_bible_chunks(
        query: str,
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

    ranked_bible_chunks = text_chunks
    if len(ranked_bible_chunks) > top_k:
        ranked_bible_chunks = ranked_bible_chunks[:top_k]
    logger.info("Returning %s ranked Bible chunks", len(ranked_bible_chunks))
    return ranked_bible_chunks


if __name__ == "__main__":
    # Use streamable-http transport for production
    mcp_app.run(
        transport=config["mcp"]["server"]["transport"],
        host="0.0.0.0", port=config["mcp"]["server"]["port"])
