from datetime import datetime
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import Literal, TypedDict
from jumo_server.db.mongo import db

class Message(TypedDict):
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

messages_collection: AsyncCollection[Message] = db["messages"]


async def save_message(message: Message):
    await messages_collection.insert_one(message)

async def get_messages(limit: int):
    return await messages_collection.find({}).limit(limit).sort([("created_at", -1)]).to_list()
