from datetime import datetime
from bson.objectid import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import TypedDict
from jumo_server.db.mongo import db


class CoreMemory(TypedDict):
    _id: ObjectId
    type: str
    category: str
    insight: str
    impact: str
    created_at: datetime


class CoreMemoryCollection:
    _collection: AsyncCollection[CoreMemory] = db["core_memories"]

    async def save_memory(self, memory: CoreMemory):
        return await self._collection.insert_one(memory)

    async def get_messages(self, limit: int = 20):
        return (
            await self._collection.find({})
            .limit(limit)
            .sort([("created_at", -1)])
            .to_list()
        )

    async def insert_many(self, memories: list[CoreMemory]):
        return await self._collection.insert_many(memories)


core_memory_collection = CoreMemoryCollection()
