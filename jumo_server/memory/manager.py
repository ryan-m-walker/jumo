from typing import List
import uuid


from jumo_server.db.messages import Message
from jumo_server.db.qdrant import insert_vector
from jumo_server.embeddings import create_embedding
from jumo_server.llm.llm import anthropic_client
from jumo_server.memory.prompts import MEMORY_PROMPT


class MemoryManager:
    def __init__(self):
        self.data = []

    async def process_batch(self, batch: List[Message]):
        formatted = []

        for message in batch:
            role = "Jumo" if message['role'] == "agent" else "user"
            formatted .append(f"{role}: {message['content']}")

        result = await anthropic_client().messages.create(
            system=MEMORY_PROMPT,
            model="claude-3-5-sonnet-latest",
            max_tokens=2056,
            messages=[
                {
                    "role": "user",
                    "content": "Please analyze the following message:\n\n" + "\n".join(formatted),
                }
            ],
            tools=[
                {
                    "name": "save_memories",
                    "description": "Save the memories for future use. Provide a list of all memories you have extracted",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "memories": {
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
            memories = tool_call.input['memories']
            
            for memory in memories:
                embedding = await create_embedding(memory)
                id = str(uuid.uuid4())
                await insert_vector(vector_id=id, vector=embedding, text=memory)

        return {"ok": True}




memory_manager = MemoryManager()
