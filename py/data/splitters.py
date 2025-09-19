from abc import ABC
from typing import List

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class AbstractSplitter(ABC):
    def split(self, text: str) -> List[str]:
        raise NotImplementedError("AbstractSplitter does not implement 'split'")


class ByLengthSplitter(AbstractSplitter):
    def __init__(self, chunk_size: int = 400, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = ["\n\n", "\n", "。", "？", "！", "；", "，", ",", ""]

        self.splitter = self._create_splitter()
        self.split = self.splitter.split_text

    def _create_splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False)
        

class BySemanticSplitter(AbstractSplitter):
    def __init__(
            self, model_name_or_path: str,
            breakpoint_threshold_type: str = "percentile",
            breakpoint_threshold_amount: float = 95.0):
        self.model_name_or_path = model_name_or_path
        self.breakpoint_threshold_type = breakpoint_threshold_type
        self.breakpoint_threshold_amount = breakpoint_threshold_amount
        self.embedding = HuggingFaceEmbeddings(model_name=self.model_name_or_path)

        self.splitter = self._create_splitter()
        self.split = self.splitter.split_text

    def _create_splitter(self):
        return SemanticChunker(
            embeddings=self.embedding,
            breakpoint_threshold_type=self.breakpoint_threshold_type,
            breakpoint_threshold_amount=self.breakpoint_threshold_amount)