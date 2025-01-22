from typing import List, TypeVar
from anthropic.types.model_param import ModelParam
from openai import AsyncOpenAI
from anthropic import NOT_GIVEN, AsyncAnthropic

from jumo_server.tools.tool import Tool


_openai = None


def openai_client():
    global _openai

    if _openai is None:
        _openai = AsyncOpenAI()

    return _openai


_anthropic = None


def anthropic_client():
    global _anthropic

    if _anthropic is None:
        _anthropic = AsyncAnthropic()

    return _anthropic


async def query_llm(
    input: str,
    system: str,
    model: str = "claude-3-5-sonnet-latest",
    tools: List[Tool] | None = None,
):
    tool_input = [tool.json() for tool in tools] if tools else NOT_GIVEN

    response = await anthropic_client().messages.create(
        system=system,
        model=model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": input,
            }
        ],
        tools=tool_input,
    )

    return response.content


T = TypeVar("T")
U = TypeVar("U")


async def make_llm_tool_call(
    query: str,
    system: str,
    tool: Tool[T, U],
    model: ModelParam = "claude-3-5-sonnet-latest",
) -> U | None:
    print("BEFORE")
    response = await anthropic_client().messages.create(
        system=system,
        model=model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        tool_choice={"type": "tool", "name": tool.name},
        tools=[tool.json()],
    )

    tool_call = next(
        (block for block in response.content if block.type == "tool_use"), None
    )

    print("TOOL_CALL")
    print(tool_call)

    # TODO: error if not called? retry?
    if tool_call:
        return await tool.impl(tool_call.input)
