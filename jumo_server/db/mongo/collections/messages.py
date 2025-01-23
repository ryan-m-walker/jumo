from datetime import datetime
from bson.objectid import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import Literal, TypedDict
from jumo_server.db.mongo import db


class Message(TypedDict):
    _id: ObjectId
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    system_prompt: str | None


class MessageCollection:
    _collection: AsyncCollection[Message] = db["messages"]

    async def save_message(self, message: Message):
        return await self._collection.insert_one(message)

    async def get_messages(self, limit: int):
        return (
            await self._collection.find({})
            .limit(limit)
            .sort([("created_at", -1)])
            .to_list()
        )


message_collection = MessageCollection()
