import asyncio
from datetime import datetime
from jumo_server.llm.llm import anthropic_client
from jumo_server.events import event_manager
from jumo_server.memory import memory_client

from jumo_server.tools import ReflectionTool
from jumo_server.output_queue import OutputQueue
from jumo_server.prompt_composer.agent_info_prompt_composer import (
    AgentInfoPromptComposer,
)
from jumo_server.prompt_composer.emote_prompt_composer import EmotePromptComposer
from jumo_server.prompt_composer.memory_prompt_composer import MemoryPromptComposer
from jumo_server.prompt_composer.note_pad_prompt_composer import NotePadPromptComposer
from jumo_server.prompt_composer.personality_prompt_composer import (
    PersonalityPromptComposer,
)
from jumo_server.prompt_composer.root_prompt_composer import RootPromptComposer

from jumo_server.db.mongo import messages_collection
from jumo_server.prompt_composer.system_info_prompt_composer import (
    SystemInfoPromptComposer,
)


user_id = "ryan"


async def chat(input: str):
    # embedding model does not like newline characters it seems so need to replace them
    query = input.strip().replace("\n", "")

    if query == "":
        return ""

    recent_messages = messages_collection.find(
        {"user_id": user_id}, sort=[("created_at", -1)], limit=50
    )

    message_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in reversed(list(recent_messages))
    ]

    message_history.append({"role": "user", "content": query})

    prompt_composer = RootPromptComposer(
        [
            AgentInfoPromptComposer(),
            SystemInfoPromptComposer(),
            PersonalityPromptComposer(),
            NotePadPromptComposer(),
            EmotePromptComposer(),
            MemoryPromptComposer(query, user_id),
        ]
    )

    system_prompt = prompt_composer.compose()

    stream = await anthropic_client().messages.create(
        model="claude-3-5-sonnet-latest",
        stream=True,
        messages=message_history,
        max_tokens=2024,
        system=system_prompt,
        # tools=[ReflectionTool()],
    )

    await event_manager.broadcast_to_all({"type": "NewMessage"})

    queue = OutputQueue()

    consumer = asyncio.create_task(queue.start_consuming())
    producer = asyncio.create_task(handle_stream(stream, queue))

    full_buffer = await producer

    await queue.flush()
    await consumer

    message_history.append({"role": "assistant", "content": full_buffer})

    messages_collection.insert_one(
        {
            "user_id": user_id,
            "role": "user",
            "content": query,
            "created_at": datetime.now(),
        }
    )

    messages_collection.insert_one(
        {
            "user_id": user_id,
            "role": "assistant",
            "content": full_buffer,
            "created_at": datetime.now(),
        }
    )

    # try:
    memory_client().add("User query: " + query, user_id=user_id)
    memory_client().add("Jumo response: " + full_buffer, user_id=user_id)
    # except Exception as e:
    #     print("Unexpected error occurred while adding memory:")
    #     print(e)

    return {"response": full_buffer}


async def handle_stream(stream, queue):
    OPEN_TAG = "<emote>"
    CLOSE_TAG = "</emote>"

    full_buffer = ""
    main_buffer = ""
    emote_buffer = ""

    partial_tag = ""
    in_emote = False

    async for event in stream:
        if event.type == "content_block_delta":
            chunk: str = event.delta.text

            if partial_tag:
                chunk = partial_tag + chunk
                partial_tag = ""

            i = 0

            while i < len(chunk):
                lookahead_start_slice = chunk[i: len(OPEN_TAG) + i]

                if not in_emote:
                    if chunk[i] == "<" and len(lookahead_start_slice) < len(OPEN_TAG):
                        partial_tag = chunk[i:]
                        break

                    if lookahead_start_slice == OPEN_TAG:
                        if main_buffer:
                            main_buffer = ""
                        in_emote = True
                        i += 7
                        full_buffer += "<emote>"
                        continue

                    await queue.put({"type": "NewTextChunk", "content": chunk[i]})

                    main_buffer += chunk[i]

                else:
                    lookahead_end_slice = chunk[i: len(CLOSE_TAG) + i]

                    if len(lookahead_end_slice) < len(CLOSE_TAG):
                        partial_tag = chunk[i:]
                        break

                    if chunk[i: i + 8] == "</emote>":
                        await queue.put(
                            {"type": "Emote", "emote": emote_buffer.strip()}
                        )

                        emote_buffer = ""
                        in_emote = False
                        i += 8
                        full_buffer += "</emote>"

                        continue

                    emote_buffer += chunk[i]

                full_buffer += chunk[i]

                i += 1

    if main_buffer:
        main_buffer = ""

    return full_buffer
