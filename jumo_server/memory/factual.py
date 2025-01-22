from datetime import datetime
import uuid
from qdrant_client.models import Distance, PointStruct, VectorParams
from jumo_server.db.qdrant import qdrant_client
from jumo_server.embeddings import Embedder
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.memory.messages_summary_collection import MessageSummary, messages_summary_collection
from jumo_server.memory.messages_collection import Message
from jumo_server.memory.prompts import FACT_MEMORY_EXTRACTION_PROMPT
from jumo_server.tools.save_memories import SaveMemmoriesTool


FACTUAL_MEMORY_COLLECTION_NAME = "jumo_factual_memory"


class FactualMemory:
    embedder = Embedder()

    async def save(self, message: Message):
        role = "Jumo" if message["role"] == "agent" else "Ryan"
        query = f"Please analyze the following message from {role}:\n\n\"{message['content']}\""
        tool = SaveMemmoriesTool()

        tool_output = await make_llm_tool_call(
            query=query,
            system=FACT_MEMORY_EXTRACTION_PROMPT,
            tool=tool,
        )

        id = str(uuid.uuid4())
        output: list[str] = []

        if tool_output:
            for fact in tool_output:
                vector = await self.embedder.embed(fact)
                output.append(fact)

                summary: MessageSummary = {
                    "content": fact,
                    "created_at": datetime.now(),
                }

                await messages_summary_collection.insert_one(summary)

                if not await qdrant_client.collection_exists(FACTUAL_MEMORY_COLLECTION_NAME):
                    await qdrant_client.create_collection(
                        collection_name=FACTUAL_MEMORY_COLLECTION_NAME,
                        vectors_config=VectorParams(size=1536, distance=Distance.DOT),
                    )

                existing = await qdrant_client.search(
                    collection_name=FACTUAL_MEMORY_COLLECTION_NAME,
                    query_vector=vector,
                    score_threshold=0.7,
                    limit=1,
                )

                print('Existing:')
                print(existing)

                await qdrant_client.upsert(
                    collection_name=FACTUAL_MEMORY_COLLECTION_NAME,
                    points=[
                        PointStruct(
                            id=id,
                            vector=vector,
                            payload={
                                "content": fact,
                                "created_at": datetime.now().isoformat(),
                                "role": message["role"],
                            }
                        )
                    ]
                )

        return output


    async def search(self, query: str):
        vector = await self.embedder.embed(query)

        if not await qdrant_client.collection_exists(FACTUAL_MEMORY_COLLECTION_NAME):
            await qdrant_client.create_collection(
                collection_name=FACTUAL_MEMORY_COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.DOT),
            )

        return await qdrant_client.search(
            collection_name=FACTUAL_MEMORY_COLLECTION_NAME,
            query_vector=vector,
        )

