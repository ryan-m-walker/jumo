import asyncio
from datetime import datetime

from jumo_server.llm.llm import anthropic_client
from jumo_server.memory import Memory
from jumo_server.events import event_manager
from jumo_server.memory.messages_collection import Message
from jumo_server.output_queue import OutputQueue
from jumo_server.stream import handle_stream
from jumo_server.system_prompt import get_system_prompt


class Jumo:
    memory = Memory()

    async def prompt(self, input: str):
        query = input.strip().replace("\n", "")

        if query == "":
            return ""

        user_message: Message = {
            "user_id": "ryan",
            "role": "user",
            "content": query,
            "system_prompt": "",
            "created_at": datetime.now(),
        }

        messages = await self.memory.get_recent_message_params()
        messages.append({"role": "user", "content": query})

        memories = await self.memory.search_formatted(input)
        summary = await self.memory.get_message_summary()

        system = get_system_prompt(summary=summary, memories=memories)

        stream = await anthropic_client().messages.create(
            model="claude-3-5-sonnet-latest",
            stream=True,
            messages=messages,
            max_tokens=2024,
            system=system,
        )

        await event_manager.broadcast_to_all({"type": "NewMessage"})

        queue = OutputQueue()

        consumer = asyncio.create_task(queue.start_consuming())
        producer = asyncio.create_task(handle_stream(stream, queue))

        full_buffer = await producer

        await queue.flush()
        await consumer

        assistant_message: Message = {
            "user_id": "ryan",
            "role": "assistant",
            "content": full_buffer,
            "created_at": datetime.now(),
            "system_prompt": system,
        }

        asyncio.create_task(
            self.memory.process_messages(
                [
                    user_message,
                    assistant_message,
                ]
            )
        )

        return full_buffer
