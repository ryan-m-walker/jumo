import asyncio
from typing import List
import uuid

from jumo_server.db.memory_batch import Memory, MemoryType, add_memory_batch
from jumo_server.db import memory_processing_queue
from jumo_server.db.mongo.collections.messages import Message
from jumo_server.db.qdrant import insert_vector
from jumo_server.embeddings import Embedder
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.memory.prompts import (
    FACT_MEMORY_EXTRACTION_PROMPT,
    SHORT_TERM_MEMORY_EXTRACTION_PROMPT,
)
from jumo_server.tools.save_memories import SaveMemmoriesTool
from jumo_server.memory.episodic import episodic_memory

SAVE_MEMORIES_TOOL_NAME = "save_memories"

embedder = Embedder()


class MemoryManager:
    async def process_exchange(self, messages: List[Message]):
        await asyncio.gather(
            memory_processing_queue.push_to_facts(messages),
            memory_processing_queue.push_to_short_term_memories(messages),
            episodic_memory.process_messages(messages),
        )

    async def process_fact_queue(self, messages: List[Message]):
        # TODO: clear queue first and make batch doc, process and then add memories
        # TODO: retry mechanism on fail? but avoid infinite retry loop
        await self.process_batch(
            messages=messages, prompt=FACT_MEMORY_EXTRACTION_PROMPT, memory_type="fact"
        )
        await memory_processing_queue.clear_fact_queue()

    async def process_short_term_queue(self, messages: List[Message]):
        # TODO: clear queue first and make batch doc, process and then add memories
        # TODO: retry mechanism on fail? but avoid infinite retry loop
        await self.process_batch(
            messages=messages,
            prompt=SHORT_TERM_MEMORY_EXTRACTION_PROMPT,
            memory_type="short_term",
        )
        await memory_processing_queue.clear_short_term_memories()

    async def process_batch(
        self, messages: List[Message], prompt: str, memory_type: MemoryType
    ):
        formatted = []

        for message in messages:
            role = "Jumo" if message["role"] == "assistant" else "user"
            formatted.append(f"{role}: {message['content']}")

        query = "Please analyze the following message:\n\n" + "\n".join(formatted)
        tool = SaveMemmoriesTool()

        tool_output = await make_llm_tool_call(query=query, system=prompt, tool=tool)

        if tool_output:
            memory_data: list[Memory] = []

            print(f"Creating memories for {memory_type}:")

            for memory in tool_output:
                embedding = await embedder.embed(memory)
                id = str(uuid.uuid4())
                await insert_vector(vector_id=id, vector=embedding, text=memory)
                memory_data.append({"id": id, "value": memory})
                print(memory)

            await add_memory_batch(
                messages=messages, memory_type=memory_type, memories=memory_data
            )

        return {"ok": True}


memory_manager = MemoryManager()
