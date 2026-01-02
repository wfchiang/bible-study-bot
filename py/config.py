import os
from pathlib import Path
from typing import Any, Dict, Tuple

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
import yaml


CONFIG_FILE_PATH = os.environ.get(
    "BSB_CONFIG_PATH", str(Path(__file__).parents[1] / "config.yaml"))


def embedding_length(
        embedding_model: HuggingFaceEmbeddings) -> int:
    emb = embedding_model.embed_query("This is a test")
    return len(emb)


def load_config() -> Dict:
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_embedding_model() -> HuggingFaceEmbeddings:
    config = load_config()
    name_or_path = config["models"]["embedding"]["name_or_path"]
    kwargs = config["models"]["embedding"]["kwargs"]
    return HuggingFaceEmbeddings(
        model_name=name_or_path,
        model_kwargs=kwargs)


def get_reranker_model() -> CrossEncoder:
    config = load_config()
    name_or_path = config["models"]["reranker"]["name_or_path"]
    kwargs = config["models"]["reranker"]["kwargs"]
    return CrossEncoder(model_name=name_or_path, **kwargs)


config = load_config()
