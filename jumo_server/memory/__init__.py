import asyncio
from anthropic.types.message_param import MessageParam
from mem0 import Memory as Mem0Memory

from jumo_server.db.messages import Message, save_message
from jumo_server.embeddings import Embedder
from jumo_server.memory.graph import GraphMemory
from jumo_server.memory.messages_summary_collection import messages_summary_collection
from jumo_server.memory.factual import FactualMemory
from jumo_server.prompts import MEMORY_EXTRACTION_PROMPT
from jumo_server.memory.messages_collection import messages_collection


config = {
    "version": "v1.1",
    "llm": {
        "provider": "anthropic",
        "config": {
            "model": "claude-3-5-sonnet-latest",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        },
    },
    "custom_prompt": MEMORY_EXTRACTION_PROMPT,
}

memory = None


def memory_client():
    global memory

    if memory is None:
        memory = Mem0Memory.from_config(config)

    return memory


class Memory:
    factual_memory = FactualMemory()
    graph_memory = GraphMemory()
    embedder = Embedder()

    async def process_messages(self, messages: list[Message]):
        for message in messages:
            await self.process_message(message)

    async def process_message(self, message: Message):
        await asyncio.gather(save_message(message), self.factual_memory.save(message))

    async def get_recent_messages(self, limit: int = 24) -> list[Message]:
        messages = (
            await messages_collection.find({})
            .sort([("created_at", -1)])
            .limit(limit)
            .to_list()
        )
        return list(reversed(messages))

    async def get_recent_message_params(self, limit: int = 24) -> list[MessageParam]:
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in await self.get_recent_messages(limit)
        ]

    async def get_message_summary(self) -> str:
        summaries = (
            await messages_summary_collection.find({})
            .sort([("created_at", -1)])
            .limit(200)
            .to_list()
        )
        return "\n".join(list(reversed([s["content"] for s in summaries])))

    async def save_message(self, message: Message):
        await messages_collection.insert_one(message)

    async def search(self, query: str):
        """
        Returns the raw factual memory results for a given query
        """
        return await self.factual_memory.search(query)

    async def search_formatted(self, query: str):
        """
        Returns factual memory formatted as a string for the LLM system prompt
        """
        memories = await self.factual_memory.search(query)
        output: list[str] = []

        for memory in memories:
            if memory.payload:
                output.append(
                    f"<memory created_at={memory.payload['created_at']}>\n{memory.payload['content']}\n</memory>"
                )

        return "\n".join(output)
