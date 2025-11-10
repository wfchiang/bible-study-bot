
import logging
import uuid
from pathlib import Path
from qdrant_client import QdrantClient, models, grpc
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))
from data.definitions import TextChunk
from config import embedding_model, QDRANT_URL, COLLECTION_NAME, embedding_length

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("vector_store")

# --- Global instances (initialized once for efficiency) ---
# Initialize the Qdrant client.
qdrant_client = QdrantClient(url=QDRANT_URL)


def create_collection_if_not_exists() -> None:
    """
    Creates the Qdrant collection if it does not already exist.
    """
    try:
        collections_response: grpc.GetCollectionInfoResponse = qdrant_client.get_collection(collection_name=COLLECTION_NAME)
        if collections_response.vectors_config:
            logger.info("Collection '%s' already exists.", COLLECTION_NAME)
            return
    except Exception as e:
        # Assuming an exception means the collection does not exist.
        # A more specific exception type could be caught if the client library provides it.
        logger.error("Error checking collection existence: assuming it does not exist.", e, exc_info=True)

    logger.info("Collection '%s' does not exist. Creating it...", COLLECTION_NAME)
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=embedding_length(),
            distance=models.Distance.COSINE,
        ),
    )
    logger.info("Collection '%s' created successfully.", COLLECTION_NAME)


def add_text_chunk(text_chunk: TextChunk) -> None:
    """
    Generates an embedding for a TextChunk and upserts it with its metadata
    into the Qdrant collection.
    """
    vector = embedding_model.embed_documents([text_chunk.text])[0]
    payload = {"text": text_chunk.text, **text_chunk.metadata}
    point_id = str(uuid.uuid4())

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[models.PointStruct(id=point_id, vector=vector, payload=payload)],
        wait=True,
    )
    logger.info("Successfully added chunk with id %s to Qdrant collection '%s'.", point_id, COLLECTION_NAME)
