from abc import ABC
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .definitions import BibleBook, TextChunk
from .utils import extract_verses_text, make_bible_quote


class AbstractSplitter(ABC):
    def split_text(self, text: str) -> List[str]:
        raise NotImplementedError("AbstractSplitter does not implement 'split'")


class ByLengthSplitter(AbstractSplitter):
    def __init__(self, chunk_size: int = 400, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = ["\n\n", "\n", "。", "？", "！", "；", "，", ",", ""]

        self.splitter = self._create_splitter()
        self.split_text = self.splitter.split_text

    def _create_splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False)


def split_bible_book(
        bible_book: BibleBook,
        chunk_size: int =400, overlap: int = 30) -> list[TextChunk]:
    chunks = []
    verse_cache = []
    for verse in bible_book.verses:
        cached_text = extract_verses_text(verse_cache)
        proposed_chunk_text = cached_text + verse.text
        if len(proposed_chunk_text) > chunk_size and verse_cache:
            bible_quote = make_bible_quote(
                book=bible_book.book, verses=verse_cache)
            bible_quote.metadata["category"] = "bible"
            chunks.append(bible_quote)
            while len(verse_cache) > 0 and len(extract_verses_text(verse_cache)) > overlap:
                verse_cache.pop(0)
        verse_cache.append(verse)
    if verse_cache:
        bible_quote = make_bible_quote(
            book=bible_book.book, verses=verse_cache)
        bible_quote.metadata["category"] = "bible"
        chunks.append(bible_quote)
    return chunks
