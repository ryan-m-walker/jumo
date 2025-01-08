
from typing import List
from jumo_server.llm.llm import openai_client


async def create_embedding(input: str) -> List[float]:
    response = await openai_client().embeddings.create(
        input=input.replace("\n", " "),
        model="text-embedding-3-small",
        dimensions=1536

    )
    return response.data[0].embedding

