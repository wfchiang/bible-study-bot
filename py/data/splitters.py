from abc import ABC
from typing import List

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .definitions import BibleBook, BibleVerse, TextChunk


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


def _get_verses_text(verses: List[BibleVerse]) -> str:
    return " ".join(v.text for v in verses)


def split_bible_book(
        bible_book: BibleBook,
        chunk_size: int =400, overlap: int = 30) -> List[TextChunk]:
    chunks = []
    verse_cache = []
    for verse in bible_book.verses:
        cached_text = _get_verses_text(verse_cache)
        proposed_chunk_text = cached_text + verse.text
        if len(proposed_chunk_text) > chunk_size and verse_cache:
            chunks.append(TextChunk(
                text=cached_text,
                metadata={
                    "category": "bible",
                    "book": bible_book.book,
                    "chapter": verse.chapter,
                    "verses": [v.verse for v in verse_cache]}))
            while len(verse_cache) > 0 and len(_get_verses_text(verse_cache)) > overlap:
                verse_cache.pop(0)
        verse_cache.append(verse)
    if verse_cache:
        chunks.append(TextChunk(
            text=_get_verses_text(verse_cache),
            metadata={
                "book": bible_book.book,
                "chapter": verse_cache[0].chapter,
                "verses": [v.verse for v in verse_cache]}))
    return chunks