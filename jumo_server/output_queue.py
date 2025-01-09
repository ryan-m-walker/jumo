import asyncio
from asyncio import Queue
from typing import Union, Literal
from typing_extensions import TypedDict

from jumo_server.chat import event_manager


class TextEvent(TypedDict):
    type: Literal["NewTextChunk"]
    content: str


class EmoteEvent(TypedDict):
    type: Literal["Emote"]
    emote: str


Event = Union[TextEvent, EmoteEvent]

EMOTE_DELAY = 1
TEXT_DELAY = 0.02


# throttle the output queue so that emotes match up roughly with reading pace
class OutputQueue:
    def __init__(self):
        self.queue = Queue()
        self.running = False

    async def put(self, event: Event):
        await self.queue.put(event)

    def get_delay_for_event(self, event: Event) -> float:
        if event["type"] == "Emote":
            return EMOTE_DELAY
        return TEXT_DELAY

    async def start_consuming(self) -> int:
        self.running = True
        events_processed = 0

        token_count_since_last_emote = 0

        while self.running:
            if not self.queue.empty():
                event = await self.queue.get()

                if event["type"] == "NewTextChunk":
                    token_count_since_last_emote += len(event["content"])
                    await event_manager.broadcast_to_all(event)
                    await asyncio.sleep(TEXT_DELAY)
                else:
                    delay = token_count_since_last_emote / 500
                    token_count_since_last_emote = 0
                    await asyncio.sleep(delay)
                    await event_manager.broadcast_to_all(event)

                events_processed += 1
            else:
                await asyncio.sleep(0.01)

        return events_processed

    async def flush(self):
        while not self.queue.empty():
            await asyncio.sleep(EMOTE_DELAY)
        self.running = False
