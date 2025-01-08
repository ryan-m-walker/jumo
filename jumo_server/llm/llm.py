from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


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
