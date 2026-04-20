from abc import ABC
from typing import AsyncGenerator
from jumo_server.llm.llm import make_llm_tool_call, anthropic_client, openai_client
from jumo_server.memory.messages_collection import Message


class LLM(ABC):
    MESSAGE_COUNT = 0

    def stream(
        self, messages: list[Message], system: str, temperature=0.1
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError


__all__ = ["make_llm_tool_call", "anthropic_client", "openai_client"]
