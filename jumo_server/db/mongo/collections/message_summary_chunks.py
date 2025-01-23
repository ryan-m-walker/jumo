from datetime import datetime
from bson.objectid import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import Literal, NotRequired, TypedDict

from jumo_server.db.mongo import db
from jumo_server.db.mongo.collections import MessageSummary


MessageSummaryChunkStatus = Literal["pending", "completed", "error"]


class MessageSummaryChunk(TypedDict):
    _id: ObjectId
    status: MessageSummaryChunkStatus
    text: str
    start: datetime
    end: datetime
    summaries: list[MessageSummary]
    created_at: datetime
    completed_at: NotRequired[datetime]


class MessageSummaryChunkCollection:
    _collection: AsyncCollection[MessageSummaryChunk] = db["message_summary_chunk"]

    async def insert(self, message_summary_chunk: MessageSummaryChunk):
        return await self._collection.insert_one(message_summary_chunk)

    async def complete(self, message_summary_chunk_id: ObjectId):
        return await self._collection.update_one(
            {"_id": message_summary_chunk_id},
            {"$set": {"status": "completed", "completed_at": datetime.now()}},
        )


message_summary_chunk_collection = MessageSummaryChunkCollection()
