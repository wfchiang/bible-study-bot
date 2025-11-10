import os
from pathlib import Path
from typing import Any, Dict

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
    model_name_or_path = get_embedding_model_name()
    return HuggingFaceEmbeddings(model_name=model_name_or_path)


def get_embedding_model_name() -> str:
    config = load_config()
    return config["models"]["embedding"]


def get_vector_store_config() -> Dict[str, Any]:
    config = load_config()
    return config["vector_store"]


embedding_model = get_embedding_model()
vector_store_config = get_vector_store_config()

QDRANT_URL = f"{vector_store_config['client_args']['schema']}://{vector_store_config['client_args']['host']}:{vector_store_config['client_args']['port']}"
COLLECTION_NAME = vector_store_config["collection_name"]

config = load_config()
