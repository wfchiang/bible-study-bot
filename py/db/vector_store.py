
import logging
import uuid
from qdrant_client import QdrantClient, models, grpc
from typing import Dict, List, Optional

from data.definitions import TextChunk
from config import embedding_model, QDRANT_API_KEY, QDRANT_URL, COLLECTION_NAME, embedding_length

logger = logging.getLogger("vector_store")

# --- Global instances (initialized once for efficiency) ---
# Initialize the Qdrant client.
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    https=QDRANT_URL.startswith("https://"),)


def create_collection_if_not_exists() -> None:
    """
    Creates the Qdrant collection if it does not already exist.
    """
    try:
        collection_response: grpc.GetCollectionInfoResponse = qdrant_client.get_collection(collection_name=COLLECTION_NAME)
        collection_status = str(collection_response.status).lower()
        if collection_status == "green":
            logger.info("Collection '%s' already exists.", COLLECTION_NAME)
            return
        raise RuntimeError(f"Unrecognized collection status: {collection_status}")
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


def search_text_chunks(text: str, top_k: int = 5, filters: Optional[Dict] = None) -> List[str]:
    vector = embedding_model.embed_documents([text])[0]

    query_filter = None
    if filters:
        conditions = [
            models.FieldCondition(key=k, match=models.MatchValue(value=v))
            for k, v in filters.items()
        ]
        query_filter = models.Filter(must=conditions)

    search_results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True, with_vectors=False)
    return [
        srel.payload["text"]
        for srel in search_results.points]
