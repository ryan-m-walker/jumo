from typing import AsyncGenerator
from anthropic.types.message_param import MessageParam
from typing_extensions import override

from anthropic import AsyncAnthropic
from jumo_server.llm import LLM
from jumo_server.memory.messages_collection import Message


class Claude(LLM):
    MESSAGE_COUNT = 50

    _client = AsyncAnthropic()

    @override
    async def stream(
        self, messages: list[Message], system: str, temperature=0.1
    ) -> AsyncGenerator[str, None]:
        stream = await self._client.messages.create(
            model="claude-3-5-sonnet-latest",
            stream=True,
            messages=[self._message_to_content(message) for message in messages],
            max_tokens=2024,
            temperature=temperature,
            system=system,
        )

        async for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    yield event.delta.text

    def _message_to_content(self, message: Message) -> MessageParam:
        return {"role": message["role"], "content": message["content"]}
