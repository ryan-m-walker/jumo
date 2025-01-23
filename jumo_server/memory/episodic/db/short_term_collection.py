from datetime import datetime
from typing import Literal
from typing_extensions import TypedDict
from pymongo.asynchronous.collection import AsyncCollection
from jumo_server.db.mongo import db
from jumo_server.db.mongo.collections.messages import Message

ProcessState = Literal["pending", "processing", "processed", "error"]


class ShortTermMemorySummary(TypedDict):
    state: ProcessState
    messages: list[Message]
    summary: str
    created_at: str
    start_timestamp: str
    end_timestamp: str


short_term_episodic_memory_collection: AsyncCollection[ShortTermMemorySummary] = db[
    "short_term_episodic_memory"
]


class ShortTermEpisodicMemoryDB:
    async def start_processing(self, messages: list[Message]):
        sorted_messages = sorted(messages, key=lambda x: x["created_at"])

        result = await short_term_episodic_memory_collection.insert_one(
            {
                "state": "processing",
                "messages": messages,
                "summary": "",
                "created_at": datetime.now().isoformat(),
                "start_timestamp": sorted_messages[0]["created_at"].isoformat(),
                "end_timestamp": sorted_messages[-1]["created_at"].isoformat(),
            }
        )

        return result.inserted_id

    async def update_summary(self, id: str, summary: str):
        await short_term_episodic_memory_collection.update_one(
            {"_id": id}, {"$set": {"state": "processed", "summary": summary}}
        )


short_term_episodic_memory_db = ShortTermEpisodicMemoryDB()
