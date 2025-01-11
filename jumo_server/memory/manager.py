import asyncio
from typing import Iterable, List
import uuid

from jumo_server.db.memory_batch import Memory, MemoryType, add_memory_batch
from jumo_server.db.messages import Message
from jumo_server.db import memory_processing_queue
from jumo_server.db.qdrant import insert_vector
from jumo_server.embeddings import create_embedding
from jumo_server.llm.llm import anthropic_client
from jumo_server.memory.prompts import FACT_MEMORY_EXTRACTION_PROMPT, SHORT_TERM_MEMORY_EXTRACTION_PROMPT 

SAVE_MEMORIES_TOOL_NAME = "save_memories"


class MemoryManager:
    async def process_exchange(self, messages: List[Message]):
        await asyncio.gather(
            memory_processing_queue.push_to_facts(messages),
            memory_processing_queue.push_to_short_term_memories(messages)
        )

    async def process_fact_queue(self, messages: List[Message]):
        # TODO: clear queue first and make batch doc, process and then add memories
        # TODO: retry mechanism on fail? but avoid infinite retry loop
        await self.process_batch(
            messages=messages,
            prompt=FACT_MEMORY_EXTRACTION_PROMPT,
            memory_type="fact"
        )
        await memory_processing_queue.clear_fact_queue()

    async def process_short_term_queue(self, messages: List[Message]):
        # TODO: clear queue first and make batch doc, process and then add memories
        # TODO: retry mechanism on fail? but avoid infinite retry loop
        await self.process_batch(
            messages=messages,
            prompt=SHORT_TERM_MEMORY_EXTRACTION_PROMPT,
            memory_type="short_term"
        )
        await memory_processing_queue.clear_short_term_memories()

    # async def process_core_memory(self, messages: List[Message]):
    #     # await self.process_batch(
    #     #     messages=messages,
    #     #     prompt=SHORT_TERM_MEMORY_EXTRACTION_PROMPT,
    #     #     memory_type="core"
    #     # )



    async def process_batch(self, messages: List[Message], prompt: str, memory_type: MemoryType):
        formatted = []

        for message in messages:
            role = "Jumo" if message['role'] == "agent" else "user"
            formatted .append(f"{role}: {message['content']}")

        result = await anthropic_client().messages.create(
            system=prompt,
            model="claude-3-5-sonnet-latest",
            max_tokens=2056,
            messages=[
                {
                    "role": "user",
                    "content": "Please analyze the following message:\n\n" + "\n".join(formatted),
                }
            ],
            tool_choice={"type": "tool", "name": SAVE_MEMORIES_TOOL_NAME},
            tools=[
                {
                    "name": SAVE_MEMORIES_TOOL_NAME,
                    "description": "Save the memories for future use. Provide a list of all memories you have extracted",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "facts": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                        },
                    }
                }
            ]
        )

        tool_call = next((block for block in result.content if block.type == "tool_use"), None)

        if tool_call is not None:
            memories = tool_call.input['facts']

            memory_data: Iterable[Memory] = []

            print(f"Creating memories for {memory_type}:")

            for memory in memories:
                embedding = await create_embedding(memory)
                id = str(uuid.uuid4())
                await insert_vector(vector_id=id, vector=embedding, text=memory)
                memory_data.append({"id": id, "value": memory})
                print(memory)

            await add_memory_batch(messages=messages, memory_type=memory_type, memories=memories)

        return {"ok": True}



memory_manager = MemoryManager()
