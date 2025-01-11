from typing import List
from openai import AsyncOpenAI
from anthropic import NOT_GIVEN, AsyncAnthropic

from jumo_server.tools.tool import Tool


openai = None


def openai_client():
    global openai

    if openai is None:
        openai = AsyncOpenAI()

    return openai


anthropic = None

def anthropic_client():
    global anthropic

    if anthropic is None:
        anthropic = AsyncAnthropic()

    return anthropic

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
        tools=tool_input
    )

    return response.content

async def make_llm_tool_call(
    query: str,
    system: str,
    tool: Tool,
    model="claude-3-5-sonnet-latest",
):
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
        tools=[tool.json()]
    )

    tool_call = next((block for block in response.content if block.type == "tool_use"), None)

    # TODO: error if not called? retry?
    if tool_call:
        return await tool.impl(tool_call.input)
