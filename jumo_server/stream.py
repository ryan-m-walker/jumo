from typing import AsyncGenerator

from jumo_server.output_queue import OutputQueue


async def handle_stream(stream: AsyncGenerator[str, None], queue: OutputQueue):
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

    async for chunk in stream:
        # if event.type == 'content_block_start':
        #     if event.content_block.type == 'tool_use':
        #         tool_id = event.content_block.id
        #         tool_name = event.content_block.name

        # if event.type == "content_block_delta":
        # if event.delta.type == "text_delta":
        #     chunk = event.delta.text

        if partial_tag:
            chunk = partial_tag + chunk
            partial_tag = ""

        i = 0

        while i < len(chunk):
            lookahead_start_slice = chunk[i : len(OPEN_TAG) + i]

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
                lookahead_end_slice = chunk[i : len(CLOSE_TAG) + i]

                if len(lookahead_end_slice) < len(CLOSE_TAG):
                    partial_tag = chunk[i:]
                    break

                if chunk[i : i + 8] == "</emote>":
                    await queue.put({"type": "Emote", "emote": emote_buffer.strip()})

                    emote_buffer = ""
                    in_emote = False
                    i += 8
                    full_buffer += "</emote>"

                    continue

                emote_buffer += chunk[i]

            full_buffer += chunk[i]

            i += 1

            # else:
            #     event.delta
            #     json_buffer += event.delta.partial_json

    if main_buffer:
        main_buffer = ""

    # if tool_id and tool_name:
    #     tool_instance = next((tool for tool in tools if tool.name == tool_name), None)
    #
    #     # TODO: reprompt with tool result message
    #     # TODO: error handling
    #     if tool_instance:
    #         await tool_instance.impl(json_buffer)

    return full_buffer
