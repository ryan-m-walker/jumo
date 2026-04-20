import os
from typing import AsyncGenerator
from google.genai import types
from typing_extensions import override
from jumo_server.llm import LLM
from google import genai

from jumo_server.memory.messages_collection import Message


class Gemini(LLM):
    MESSAGE_COUNT = 200

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    @override
    async def stream(
        self, messages: list[Message], system: str, temperature=0.1
    ) -> AsyncGenerator[str, None]:
        stream = await self._client.aio.models.generate_content_stream(
            model="gemini-2.0-flash-exp",
            contents=[self._message_to_content(message) for message in messages],
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system,
                max_output_tokens=2024,
            ),
        )

        input_token_count = 0
        output_token_count = 0

        async for chunk in stream:
            if chunk.usage_metadata:
                output_token_count += chunk.usage_metadata.candidates_token_count or 0
                input_token_count += chunk.usage_metadata.prompt_token_count or 0

            if chunk.text:
                yield chunk.text

        print(f"Input token count: {input_token_count}")
        print(f"Output token count: {output_token_count}")

    def _message_to_content(self, message: Message) -> types.Content:
        return types.Content(
            role=message["role"],
            parts=[
                types.Part(
                    text=message["content"],
                )
            ],
        )
