from mem0 import Memory
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.tools.save_memories import SaveMemmoriesTool


async def process_memory_batch(self, messages: List[Message], prompt: str, memory_type: MemoryType):
    formatted = []

    for message in messages:
        role = "Jumo" if message['role'] == "agent" else "user"
        formatted .append(f"{role}: {message['content']}")

    query = "Please analyze the following message:\n\n" + "\n".join(formatted)
    tool = SaveMemmoriesTool()

    tool_output = await make_llm_tool_call(
        query=query,
        system=prompt,
        tool=tool
    )

    if tool_output:
        memory_data: list[Memory] = []

        print(f"Creating memories for {memory_type}:")

        for memory in tool_output:
            embedding = await create_embedding(memory)
            id = str(uuid.uuid4())
            await insert_vector(vector_id=id, vector=embedding, text=memory)
            memory_data.append({"id": id, "value": memory})
            print(memory)

        await add_memory_batch(
            messages=messages,
            memory_type=memory_type,
            memories=memory_data
        )

    return {"ok": True}
