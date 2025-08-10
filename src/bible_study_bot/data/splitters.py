from abc import ABC
from typing import List

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


class AbstractSplitter(ABC):
    def split(self, text: str) -> List[str]:
        raise NotImplementedError("AbstractSplitter does not implement 'split'")
    

class HFSemanticSplitter(AbstractSplitter):
    def __init__(self, hf_embedding_model: str):
        self.hf_embedding_model_name_or_path = hf_embedding_model
        self.hf_embedding_model = HuggingFaceEmbeddings(
            model_name=self.hf_embedding_model_name_or_path,
            model_kwargs={
                "trust_remote_code": False})
        self.splitter = SemanticChunker(self.hf_embedding_model)
