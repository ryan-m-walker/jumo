from datetime import datetime
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import Literal, TypedDict
from jumo_server.db.mongo import db


class Message(TypedDict):
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    system_prompt: str | None


messages_collection: AsyncCollection[Message] = db["messages"]
