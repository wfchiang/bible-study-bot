import os
from pathlib import Path
from typing import Any, Dict, Tuple

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import yaml


CONFIG_FILE_PATH = os.environ.get(
    "BSB_CONFIG_PATH", str(Path(__file__).parents[1] / "config.yaml"))


def embedding_length() -> int:
    emb = embedding_model.embed_query("This is a test")
    return len(emb)


def load_config() -> Dict:
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_embedding_model() -> HuggingFaceEmbeddings:
    name_or_path, kwargs = get_embedding_model_config()
    return HuggingFaceEmbeddings(
        model_name=name_or_path,
        model_kwargs=kwargs)


def get_embedding_model_config() -> Tuple[str, Dict]:
    """
    Return a tuple of (model_name_or_path, model_kwargs)
    """
    config = load_config()
    model_name_or_path = config["models"]["embedding"]["name_or_path"]
    model_kwargs = config["models"]["embedding"]["kwargs"]
    return model_name_or_path, model_kwargs


def get_vector_store_config() -> Dict[str, Any]:
    config = load_config()
    return config["vector_store"]


embedding_model = get_embedding_model()
vector_store_config = get_vector_store_config()

QDRANT_URL = vector_store_config['client_args']['url']
QDRANT_API_KEY = os.environ[vector_store_config['client_args']['token_var']]
COLLECTION_NAME = vector_store_config["collection_name"]

config = load_config()
