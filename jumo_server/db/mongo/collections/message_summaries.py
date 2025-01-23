from datetime import datetime
from jumo_server.db.mongo import db
from bson.objectid import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import TypedDict


class MessageSummary(TypedDict):
    _id: ObjectId
    message_id: ObjectId
    content: str
    speaker: str
    created_at: datetime


class MessageSummaryCollection:
    _collection: AsyncCollection[MessageSummary] = db["message_summaries"]

    async def save_message_summary(self, message_summary: MessageSummary):
        return await self._collection.insert_one(message_summary)

    async def get_message_summaries(self, limit: int = 100, skip: int = 0):
        return (
            await self._collection.find({})
            .skip(skip)
            .limit(limit)
            .sort([("created_at", -1)])
            .to_list()
        )


message_summary_collection = MessageSummaryCollection()
