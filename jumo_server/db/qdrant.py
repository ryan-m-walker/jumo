from datetime import datetime
from typing import List
from typing_extensions import TypedDict
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

client = AsyncQdrantClient(host="localhost", port=6333)

VECTOR_DB_COLLECTION = "jumo"

class MemoryData(TypedDict):
    create_at: str
    text: str

async def initialize_qdrant_client():
    if not await client.collection_exists(VECTOR_DB_COLLECTION):
        await client.create_collection(
            collection_name=VECTOR_DB_COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.DOT),
        )



async def insert_vector(vector_id: str, vector: List[float], text: str):
    return await client.upsert(
        collection_name=VECTOR_DB_COLLECTION,
        points=[
            PointStruct(
                id=vector_id,
                vector=vector,
                payload={"text": text, "created_at": datetime.now().isoformat()},
            )
        ]
    )

async def search_vector(vector: List[float]):
    return await client.search(
        collection_name=VECTOR_DB_COLLECTION,
        query_vector=vector,
    )
