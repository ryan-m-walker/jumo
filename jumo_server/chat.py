# import asyncio
# from collections.abc import Iterable
# from datetime import datetime
#
# from anthropic.types.message_param import MessageParam
# from jumo_server.llm.llm import anthropic_client
# from jumo_server.events import event_manager
# from jumo_server.memory.manager import memory_manager
#
# from jumo_server.prompt_composer.agent_info_prompt_composer import (
#     AgentInfoPromptComposer,
# )
# from jumo_server.prompt_composer.emote_prompt_composer import EmotePromptComposer
# from jumo_server.prompt_composer.short_term_summary_prompt_composer import ShortTermSummaryPromptComposer
# from jumo_server.prompt_composer.memory_prompt_composer import Mem0MemoryPromptComposer, MemoryPromptComposer
# from jumo_server.prompt_composer.note_pad_prompt_composer import NotePadPromptComposer
# from jumo_server.prompt_composer.personality_prompt_composer import (
#     PersonalityPromptComposer,
# )
# from jumo_server.prompt_composer.root_prompt_composer import RootPromptComposer
#
# from jumo_server.db.messages import Message, messages_collection, save_message
# from jumo_server.prompt_composer.system_info_prompt_composer import (
#     SystemInfoPromptComposer,
# )
# from jumo_server.stream import handle_stream
# from jumo_server.tools.set_mode import SetModeTool
# from jumo_server.tools.tool import Tool
#
#
# user_id = "ryan"
#
# tools: list[Tool]  = [
#     SetModeTool()
# ]
#
#
# async def chat(input: str):
#     # embedding model does not like newline characters it seems so need to replace them
#     query = input.strip().replace("\n", "")
#
#     if query == "":
#         return ""
#
#     recent_messages = await messages_collection.find(
#         {"user_id": user_id}, sort=[("created_at", -1)], limit=50
#     ).to_list()
#
#     message_history: Iterable[MessageParam] = []
#
#     for msg in reversed(list(recent_messages)):
#         message_history.append({
#             "role": msg["role"],
#             "content": msg["content"]
#         })
#
#     message_history.append({"role": "user", "content": query})
#
#     short_term_summary_prompt_composer = ShortTermSummaryPromptComposer()
#     memory_prompt_composer = MemoryPromptComposer(query)
#
#     await asyncio.gather(
#         memory_prompt_composer.prep(),
#         short_term_summary_prompt_composer.prep()
#     )
#
#     prompt_composer = RootPromptComposer(
#         [
#             AgentInfoPromptComposer(),
#             SystemInfoPromptComposer(),
#             PersonalityPromptComposer(),
#             NotePadPromptComposer(),
#             EmotePromptComposer(),
#             short_term_summary_prompt_composer,
#             Mem0MemoryPromptComposer(query, user_id),
#             memory_prompt_composer,
#         ]
#     )
#
#     system_prompt = prompt_composer.compose()
#
#     stream = await anthropic_client().messages.create(
#         model="claude-3-5-sonnet-latest",
#         stream=True,
#         messages=message_history,
#         max_tokens=2024,
#         system=system_prompt,
#         tools=[tool.json() for tool in tools],
#     )
#
#     await event_manager.broadcast_to_all({"type": "NewMessage"})


    # consumer = asyncio.create_task(queue.start_consuming())
    # producer = asyncio.create_task(handle_stream(stream, queue))
    #
    # full_buffer = await producer
    #
    # await queue.flush()
    # await consumer
    #
    # message_history.append({"role": "assistant", "content": full_buffer})
    #
    # input_message = Message(
    #     user_id=user_id,
    #     role="user",
    #     content=query,
    #     created_at=datetime.now(),
    #     system_prompt=None
    # )
    #
    # output_message = Message(
    #     user_id=user_id,
    #     role="assistant",
    #     content=full_buffer,
    #     created_at=datetime.now(),
    #     system_prompt=system_prompt
    # )
    #
    # await save_message(input_message)
    # await save_message(output_message)
    #
    # await memory_manager.process_exchange([input_message, output_message])
    #
    # return {"response": full_buffer}
    #

