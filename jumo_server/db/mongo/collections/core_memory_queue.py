from datetime import date, datetime
from typing_extensions import TypedDict
from bson.objectid import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from jumo_server.db.mongo.collections.messages import Message
from jumo_server.db.mongo import db


class CoreMemoryQueue(TypedDict):
    messages: list[Message]
    last_processed_chunk: ObjectId
    last_processed_time: date


class CoreMemoryQueueCollection:
    _collection: AsyncCollection[CoreMemoryQueue] = db["core_memory_queue"]

    async def push(self, message: Message):
        await self._collection.update_one(
            {}, {"$push": {"messages": message}}, upsert=True
        )

    async def empty(self) -> list[Message]:
        document = await self._collection.find_one({})

        if document is None:
            return []

        messages = document["messages"]

        await self._collection.update_one(
            {},
            {
                "$set": {
                    "messages": [],
                    "last_processed_time": datetime.now(),
                }
            },
            upsert=True,
        )

        return sorted(messages, key=lambda x: x["created_at"], reverse=True)

    async def check(self, queue_size: int = 50):
        document = await self._collection.find_one({})

        if document is None:
            return False

        return len(document["messages"]) >= queue_size


core_memory_queue_collection = CoreMemoryQueueCollection()
