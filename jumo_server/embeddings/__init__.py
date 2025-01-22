from typing import List
from jumo_server.llm.llm import openai_client


class Embedder:
    async def embed(self, input: str, dimensions=1536) -> List[float]:
        response = await openai_client().embeddings.create(
            input=input.replace("\n", " "),
            model="text-embedding-3-small",
            dimensions=dimensions,
        )

        return response.data[0].embedding
