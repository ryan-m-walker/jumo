from datetime import datetime
from typing import List, Literal
from typing_extensions import TypedDict
from pymongo.asynchronous.collection import AsyncCollection

from jumo_server.db.mongo import db
from jumo_server.memory.messages_collection import Message

BATCH_SIZE = 4

MemoryType = Literal["fact", "short_term", "higher_order"]


class Memory(TypedDict):
    id: str
    value: str


class MemoryBatch(TypedDict):
    memory_type: MemoryType
    messages: List[Message]
    memories: List[Memory]
    created_at: datetime


memory_batch_collection: AsyncCollection[MemoryBatch] = db["memory_batch"]

BatchStatus = Literal["pending", "processing", "processed"]


async def add_memory_batch(
    messages: List[Message], memory_type: MemoryType, memories: List[Memory]
):
    await memory_batch_collection.insert_one(
        {
            "memory_type": memory_type,
            "messages": messages,
            "memories": memories,
            "created_at": datetime.now(),
        }
    )
