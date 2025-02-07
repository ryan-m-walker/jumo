from datetime import datetime
from bson.objectid import ObjectId
from jumo_server.db.mongo.collections.core_memory_queue import (
    core_memory_queue_collection,
)
from jumo_server.memory.core.prompts import (
    get_core_memory_extraction_prompt,
)
from jumo_server.db.mongo.collections.core_memories import core_memory_collection
from jumo_server.db.mongo.collections.messages import Message
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.memory.core.tools import ExtractCoreMemoryTool


class CoreMemory:
    async def process_message(self, message: Message):
        await core_memory_queue_collection.push(message)

        if await core_memory_queue_collection.check():
            messages = await core_memory_queue_collection.empty()
            await self.extract_core_memory(messages)

    async def extract_core_memory(self, messages: list[Message]):
        previous_memories = await core_memory_collection.get_messages()

        query = "Please analyze the following messages and extract core memories."

        for message in messages:
            speaker = "Ryan" if message["role"] == "user" else "Jumo"
            query += f"\n\n({message['created_at']}) {speaker}: {message['content']}"

        result = await make_llm_tool_call(
            query=query,
            system=get_core_memory_extraction_prompt(previous_memories),
            tool=ExtractCoreMemoryTool(),
        )

        if result and result["memories"]:
            await core_memory_collection.insert_many(
                [
                    {"_id": ObjectId(), "created_at": datetime.now(), **memory}
                    for memory in result["memories"]
                ]
            )
