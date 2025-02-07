import asyncio
from anthropic.types.message_param import MessageParam
from mem0 import Memory as Mem0Memory

from jumo_server.consts import MESSAGE_WINDOW_COUNT
from jumo_server.db.mongo.collections import message_collection, Message
from jumo_server.embeddings import Embedder
from jumo_server.memory.core import CoreMemory
from jumo_server.memory.graph import GraphMemory
from jumo_server.memory.messages_summary_collection import messages_summary_collection
from jumo_server.memory.summarizer import Summarizer
from jumo_server.prompts import MEMORY_EXTRACTION_PROMPT


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
    _graph_memory = GraphMemory()
    _summarizer = Summarizer()
    _core_memory = CoreMemory()
    _embedder = Embedder()

    async def process_messages(self, messages: list[Message]):
        for message in messages:
            await self.process_message(message)

    async def process_message(self, message: Message):
        await asyncio.gather(
            message_collection.save_message(message),
            self._summarizer.process_message(message),
            self._graph_memory.process_message(message),
            self._core_memory.process_message(message),
        )

    async def get_recent_messages(
        self, limit: int = MESSAGE_WINDOW_COUNT
    ) -> list[Message]:
        messages = await message_collection.get_messages(limit)
        return list(reversed(messages))

    async def get_recent_message_params(
        self, limit: int = MESSAGE_WINDOW_COUNT
    ) -> list[MessageParam]:
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

    async def save_message(self, message: Message) -> None:
        await message_collection.save_message(message)

    async def query_formatted(self, query: str) -> str:
        prompts = await asyncio.gather(
            self._summarizer.get_formatted(), self._graph_memory.query_formatted(query)
        )
        return "\n\n".join(prompts)
