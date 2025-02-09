from typing import AsyncGenerator, override

from anthropic import AsyncAnthropic
from jumo_server.llm import LLM


class Claude(LLM):
    _client = AsyncAnthropic()

    @override
    async def stream(self, input: str) -> AsyncGenerator[str, None]:
        stream = await self._client.messages.create(
            model="claude-3-5-sonnet-latest",
            stream=True,
            messages=[{"role": "user", "content": input}],
            max_tokens=2024,
            temperature=0.1,
        )

        async for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    yield event.delta.text
