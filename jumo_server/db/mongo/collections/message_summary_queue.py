from datetime import date, datetime
from typing_extensions import TypedDict
from bson.objectid import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from jumo_server.db.mongo import db
from jumo_server.db.mongo.collections import MessageSummary


class MessageSummaryQueue(TypedDict):
    summaries: list[MessageSummary]
    last_processed_chunk: ObjectId
    last_processed_time: date


class MessageSummaryQueueCollection:
    _collection: AsyncCollection[MessageSummaryQueue] = db["message_summary_queue"]

    async def push(self, summary: MessageSummary):
        await self._collection.update_one(
            {}, {"$push": {"summaries": summary}}, upsert=True
        )

    async def empty(self):
        document = await self._collection.find_one({})

        if document is None:
            return []

        summaries = document["summaries"]

        await self._collection.update_one(
            {},
            {
                "$set": {
                    "summaries": [],
                    "last_processed_time": datetime.now(),
                }
            },
            upsert=True,
        )

        return sorted(summaries, key=lambda x: x["created_at"], reverse=True)

    async def check(self, char_limit: int = 500):
        document = await self._collection.find_one({})

        if document is None:
            return False

        summaries = document["summaries"]
        joined = "\n".join([summary["content"] for summary in summaries])

        return len(joined) >= char_limit


message_summary_queue_collection = MessageSummaryQueueCollection()
