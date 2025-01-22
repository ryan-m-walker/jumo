from datetime import datetime
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import TypedDict
from jumo_server.db.mongo import db


class MessageSummary(TypedDict):
    content: str
    created_at: datetime


messages_summary_collection: AsyncCollection[MessageSummary] = db["messages_summary"]
