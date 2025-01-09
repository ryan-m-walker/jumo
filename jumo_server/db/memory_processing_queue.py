import asyncio
from typing import List
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import TypedDict

from jumo_server.db.messages import Message
from jumo_server.db.mongo import db
from jumo_server.memory.manager import memory_manager

FACT_QUEUE_SIZE = 4
SHORT_TERM_QUEUE_SIZE = 50
HIGHER_ORDER_QUEUE_SIZE = 100

class LastProcessed(TypedDict):
    fact_queue: int
    short_term_queue: int
    higher_order_queue: int

class MemoryProcessingQueue(TypedDict):
    fact_queue: List[Message]
    short_term_queue: List[Message]
    higher_order_queue: List[str]
    last_processed: LastProcessed

# memory_processing_queue: Collection[MemoryProcessingQueue] = db['memory_processing_queue']
memory_processing_queue: AsyncCollection[MemoryProcessingQueue] = db['memory_processing_queue']

async def init():
    """Initialize the singleton memory processing queue document if it doesn't exist."""
    existing = await memory_processing_queue.find_one({})

    if not existing:
        await memory_processing_queue.insert_one({
            "fact_queue": [],
            "short_term_queue": [],
            "higher_order_queue": [],
            "last_processed": {
                "fact_queue": 0,
                "short_term_queue": 0,
                "higher_order_queue": 0
            }
        })

async def push_to_facts(messages: List[Message]):
    await memory_processing_queue.update_one({}, {
        "$push": {
            "fact_queue": {
                "$each": messages
            }
        }
    })

    updated = await memory_processing_queue.find_one({})

    if not updated:
        return

    if len(updated['fact_queue']) >= FACT_QUEUE_SIZE:
        asyncio.create_task(memory_manager.process_fact_queue(updated['fact_queue']))


async def clear_fact_queue():
    await memory_processing_queue.update_one({}, {
        "$set": {
            "fact_queue": []
        }
    })


async def push_to_short_term_memories(messages: List[Message]):
    await memory_processing_queue.update_one({}, {
        "$push": {
            "short_term_queue": {
                "$each": messages
            }
        }
    })

    updated = await memory_processing_queue.find_one({})

    if not updated:
        return

    if len(updated['short_term_queue']) >= SHORT_TERM_QUEUE_SIZE:
        asyncio.create_task(memory_manager.process_short_term_queue(updated['short_term_queue']))

async def clear_short_term_memories():
    await memory_processing_queue.update_one({}, {
        "$set": {
            "short_term_queue": []
        }
    })

async def push_to_higher_order_memories(memories: List[str]):
    await memory_processing_queue.update_one({}, {
        "$push": {
            "higher_order_queue": {
                "$each": memories
            }
        }
    })
