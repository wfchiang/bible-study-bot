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

    def _encode_verse_range(
            from_verse: BibleVerse, to_verse: BibleVerse) -> str:
        from_chapter = from_verse.chapter
        to_chapter = to_verse.chapter
        assert from_verse.chapter <= to_verse.chapter
        from_v = from_verse.verse
        to_v = to_verse.verse
        if from_chapter == to_chapter:
            assert from_v <= to_v
            if from_v == to_v:
                return f"{bible_book.book} {from_chapter}:{from_v}"
            else:
                return f"{bible_book.book} {from_chapter}:{from_v}-{to_v}"
        else:
            return f"{bible_book.book} {from_chapter}:{from_v}-{to_chapter}:{to_v}"

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
                    "range": _encode_verse_range(
                        verse_cache[0], verse_cache[-1]),}))
            while len(verse_cache) > 0 and len(_get_verses_text(verse_cache)) > overlap:
                verse_cache.pop(0)
        verse_cache.append(verse)
    if verse_cache:
        chunks.append(TextChunk(
            text=_get_verses_text(verse_cache),
            metadata={
                "category": "bible",
                "range": _encode_verse_range(
                    verse_cache[0], verse_cache[-1]),}))
    return chunks
