
import asyncio
from jumo_server.db.messages import Message
from jumo_server.llm.llm import anthropic_client
from jumo_server.memory.episodic.db.episodic_memory_queue import episodic_memory_queue_collection
from jumo_server.memory.episodic.db.short_term_collection import short_term_episodic_memory_db
from jumo_server.memory.episodic.prompts import SHORT_TERM_EPISOIC_MEMORY_SUMMARY_PROMPT


SHORT_TERM_SUMMARY_QUEUE_SIZE = 4


class EpisodicMemory:
    async def process_messages(self, messages: list):
        await self.push_to_short_term_summary_queue(messages)

    async def push_to_short_term_summary_queue(self, messages: list):
        await episodic_memory_queue_collection.update_one({}, {
            "$push": {
                "short_term_summary_queue": {
                    "$each": messages
                }
            }
        })

        updated = await episodic_memory_queue_collection.find_one({})

        if not updated:
            return

        if len(updated['short_term_summary_queue']) >= SHORT_TERM_SUMMARY_QUEUE_SIZE:
            asyncio.create_task(
                self.process_short_term_summary_queue(
                    updated['short_term_summary_queue']
                )
            )

            await episodic_memory_queue_collection.update_one({}, {
                "$set": {
                    "short_term_summary_queue": []
                }
            })


    async def process_short_term_summary_queue(self, messages: list[Message]):
        id = await short_term_episodic_memory_db.start_processing(messages)

        formatted = []

        for message in messages:
            role = "Jumo" if message['role'] == "agent" else "user"
            formatted .append(f"{role}: {message['content']}")

        system = SHORT_TERM_EPISOIC_MEMORY_SUMMARY_PROMPT
        query = "Please analyze the following message:\n\n" + "\n".join(formatted)

        result = await anthropic_client().messages.create(
            model="claude-3-5-sonnet-20240620",
            messages=[
                {"role": "user", "content": query}
            ],
            system=system,
            max_tokens=2024,
        )

        output = result.content[0]

        if output.type == "text":
            return await short_term_episodic_memory_db.update_summary(id, output.text)


episodic_memory = EpisodicMemory()

