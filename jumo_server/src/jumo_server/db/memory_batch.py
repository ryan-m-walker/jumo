import asyncio
from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo.synchronous.collection import Collection

from jumo_server.db.mongo import db
from jumo_server.db.messages import Message
from jumo_server.memory import memory_client
from jumo_server.consts import user_id

BATCH_SIZE = 4


memory_batch_collection = db['memory_batch']

BatchStatus = Literal["pending", "processing", "processed"]

class MemoryBatch(BaseModel):
    messages: List[Message] = []
    status: BatchStatus = "pending"
    created_at: datetime


def process_batch(batch):
    result = memory_client().add(messages=batch['messages'], user_id=user_id)

    print(result)

    memory_batch_collection.update_one({
        "_id": batch['_id']
    }, {
        "$set": {
            "status": "processed"
        }
    })

async def add_message_to_batch(message: Message):
    memory_batch_collection.update_one({
        "status": "pending"
    }, {
        "$push": {
            "messages": message.model_dump()
        }
    }, upsert=True)

    updated = memory_batch_collection.find_one({
        "status": "pending"
    })

    if updated and len(updated['messages']) >= BATCH_SIZE:
        memory_batch_collection.update_one({
            "status": "pending"
        }, {
            "$set": {
                "status": "processing"
            }
        })

        await asyncio.to_thread(process_batch, updated)



