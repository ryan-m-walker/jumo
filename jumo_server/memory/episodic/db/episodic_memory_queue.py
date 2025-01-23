from typing_extensions import TypedDict
from pymongo.asynchronous.collection import AsyncCollection
from jumo_server.db.mongo import db
from jumo_server.db.mongo.collections.messages import Message


class EpisodicMemoryQueue(TypedDict):
    short_term_summary_queue: list[Message]


episodic_memory_queue_collection: AsyncCollection[EpisodicMemoryQueue] = db[
    "episodic_memory_queue"
]


async def init_episodic_memory_queue():
    if not await episodic_memory_queue_collection.find_one({}):
        await episodic_memory_queue_collection.insert_one(
            {"short_term_summary_queue": []}
        )
