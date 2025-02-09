from abc import ABC
from typing import AsyncGenerator, AsyncIterator, Coroutine
from typing_extensions import Any, Generator
from jumo_server.llm.llm import make_llm_tool_call, anthropic_client, openai_client


class LLM(ABC):
    def stream(self, input: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError


__all__ = ["make_llm_tool_call", "anthropic_client", "openai_client"]
