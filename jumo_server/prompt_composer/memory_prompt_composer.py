import asyncio
from typing import List

from qdrant_client.models import ScoredPoint
from jumo_server.db.qdrant import search_vector
from jumo_server.embeddings import Embedder
from jumo_server.memory import memory_client
from .prompt_composer import PromptComposer

from rich.console import Console

console = Console()
embedder = Embedder()


class Mem0MemoryPromptComposer(PromptComposer):
    def __init__(self, query: str, user_id: str):
        self._query = query
        self._user_id = user_id

    def compose(self) -> str:
        memories = memory_client().search(query=self._query, user_id=self._user_id)

        output = "## (Mem0 memory system): Memories are things that you remember from past interactions:\n\n"
        output += "<memories>\n"

        for m in memories["results"]:
            output += f'<memory score="{m["score"]}" created_at="{m["created_at"]}" updated_at="{m["updated_at"]}">{m["memory"]}</memory>\n'

        output += "</memories>\n"

        return output


# Deprecated
class MemoryPromptComposer(PromptComposer):
    def __init__(self, query: str):
        self._query = query
        self._memories: List[ScoredPoint] = []

    async def prep(self):
        self._memories = []

        # messages = await memor get_messages(limit=6)
        messages = []

        messages_text = [message["content"] for message in messages]
        messages_text.append(self._query)

        embeddings = await asyncio.gather(
            *[embedder.embed(message) for message in messages_text]
        )
        memory_results = await asyncio.gather(
            *[search_vector(embedding) for embedding in embeddings]
        )

        for memory in memory_results:
            for m in memory:
                self._memories.append(m)

    def compose(self) -> str:
        output = "## (New Custom Memory System): Memories are things that you remember from past interactions:\n\n"
        output += "<memories>\n"

        for m in self._memories:
            if m.payload:
                output += f"<memory created_at='{m.payload['created_at']}'>{m.payload['text']}</memory>\n"

        output += "</memories>\n"

        return output
