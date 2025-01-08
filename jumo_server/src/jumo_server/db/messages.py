from datetime import datetime
from pydantic import BaseModel
from jumo_server.db.mongo import db

messages_collection = db["messages"]

class Message(BaseModel):
    user_id: str
    role: str
    content: str
    created_at: datetime

def save_message(message: Message):
    messages_collection.insert_one(message.model_dump())

async def get_messages(limit: int):
    return [Message(**message) for message in messages_collection.find({}).limit(limit).sort([("created_at", -1)])]
