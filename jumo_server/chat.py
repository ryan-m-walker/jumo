import asyncio
from collections.abc import Iterable
from datetime import datetime

from anthropic import AsyncStream
from anthropic.types.message_param import MessageParam
from anthropic.types.raw_message_stream_event import RawMessageStreamEvent
from jumo_server.llm.llm import anthropic_client
from jumo_server.events import event_manager
from jumo_server.memory.manager import memory_manager

from jumo_server.output_queue import OutputQueue
from jumo_server.prompt_composer import memory_prompt_composer
from jumo_server.prompt_composer.agent_info_prompt_composer import (
    AgentInfoPromptComposer,
)
from jumo_server.prompt_composer.emote_prompt_composer import EmotePromptComposer
from jumo_server.prompt_composer.memory_prompt_composer import Mem0MemoryPromptComposer, MemoryPromptComposer
from jumo_server.prompt_composer.note_pad_prompt_composer import NotePadPromptComposer
from jumo_server.prompt_composer.personality_prompt_composer import (
    PersonalityPromptComposer,
)
from jumo_server.prompt_composer.root_prompt_composer import RootPromptComposer

from jumo_server.db.messages import Message, messages_collection, save_message
from jumo_server.prompt_composer.system_info_prompt_composer import (
    SystemInfoPromptComposer,
)
from jumo_server.tools.set_mode import SetModeTool


user_id = "ryan"

tools  = [
    SetModeTool()
]


async def chat(input: str):
    # embedding model does not like newline characters it seems so need to replace them
    query = input.strip().replace("\n", "")

    if query == "":
        return ""

    recent_messages = await messages_collection.find(
        {"user_id": user_id}, sort=[("created_at", -1)], limit=50
    ).to_list()

    message_history: Iterable[MessageParam] = []

    for msg in reversed(list(recent_messages)):
        message_history.append({
            "role": msg["role"],
            "content": msg["content"]
        })


    # message_history: Iterable[MessageParam] = [
    #     {"role": msg["role"], "content": msg["content"]}
    #     for msg in reversed(list(recent_messages))
    # ]

    message_history.append({"role": "user", "content": query})

    memory_prompt_composer = MemoryPromptComposer(query)
    await memory_prompt_composer.prep()

    prompt_composer = RootPromptComposer(
        [
            AgentInfoPromptComposer(),
            SystemInfoPromptComposer(),
            PersonalityPromptComposer(),
            NotePadPromptComposer(),
            EmotePromptComposer(),
            Mem0MemoryPromptComposer(query, user_id),
            memory_prompt_composer,
        ]
    )

    system_prompt = prompt_composer.compose()

    # tools: Iterable[ToolParam] = tools.map(lambda tool: tool.json())

    stream = await anthropic_client().messages.create(
        model="claude-3-5-sonnet-latest",
        stream=True,
        messages=message_history,
        max_tokens=2024,
        system=system_prompt,
        tools=[tool.json() for tool in tools],
    )

    await event_manager.broadcast_to_all({"type": "NewMessage"})

    queue = OutputQueue()

    consumer = asyncio.create_task(queue.start_consuming())
    producer = asyncio.create_task(handle_stream(stream, queue))

    full_buffer = await producer

    await queue.flush()
    await consumer

    message_history.append({"role": "assistant", "content": full_buffer})

    input_message = Message(
        user_id=user_id,
        role="user",
        content=query,
        created_at=datetime.now()
    )

    output_message = Message(
        user_id=user_id,
        role="assistant",
        content=full_buffer,
        created_at=datetime.now()
    )

    await save_message(input_message)
    await save_message(output_message)

    await memory_manager.process_exchange([input_message, output_message])

    return {"response": full_buffer}


async def handle_stream(stream: AsyncStream[RawMessageStreamEvent], queue: OutputQueue):
    OPEN_TAG = "<emote>"
    CLOSE_TAG = "</emote>"

    full_buffer = ""
    main_buffer = ""
    emote_buffer = ""

    partial_tag = ""
    in_emote = False

    tool_id: str | None = None
    tool_name: str | None = None
    json_buffer = ""

    async for event in stream:
        if event.type == 'content_block_start':
            if event.content_block.type == 'tool_use':
                tool_id = event.content_block.id
                tool_name = event.content_block.name

        if event.type == "content_block_delta":

            if event.delta.type == "text_delta":
                chunk = event.delta.text

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
            else:
                event.delta
                json_buffer += event.delta.partial_json

    if main_buffer:
        main_buffer = ""

    if tool_id and tool_name:
        tool_instance = next((tool for tool in tools if tool.json()["name"] == tool_name), None)

        # TODO: reprompt with tool result message
        # TODO: error handling
        if tool_instance:
            await tool_instance.execute(json_buffer)

    return full_buffer
