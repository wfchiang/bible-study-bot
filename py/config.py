import os
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
import yaml


# Load configuration
config_file_path = os.environ.get(
    "BSB_CONFIG_PATH", str(Path(__file__).parents[1] / "config.yaml"))
config = None
with open(config_file_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


# Load the embedding model
embedding_model = OpenAIEmbeddings(
        model=config["embedding"]["openai_model"],
        chunk_size=config["embedding"]["openai_batch_size"],
        max_retries=config["embedding"]["openai_max_retries"])

embedding_length = len(embedding_model.embed_query("This is a test"))
