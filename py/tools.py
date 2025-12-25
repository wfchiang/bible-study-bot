from langchain_core.tools import tool

from db.vector_store import search_text_chunks


@tool
def search_bible_chunks(query: str) -> list[str]:
    """
    Search for Bible verses or text chunks relevant to the query.
    Use this tool to find relevant scripture when the user asks about specific topics, verses, or theological concepts in the Bible.
    """
    return search_text_chunks(
        query,
        filters={"category": "bible"}
    )
