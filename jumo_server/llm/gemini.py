import os
from typing import AsyncGenerator
from jumo_server.llm import LLM
from google import genai


class Gemini(LLM):
    _client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    # @override
    async def stream(self, input: str) -> AsyncGenerator[str, None]:
        chat = self._client.aio.chats.create(model="gemini-2.0-flash-exp")
        stream = await chat.send_message_stream(input)

        async for chunk in await stream:
            if chunk.text:
                yield chunk.text
