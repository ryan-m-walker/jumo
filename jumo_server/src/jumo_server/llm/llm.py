from openai import OpenAI
from anthropic import AsyncAnthropic


openai = None


def open_ai_client():
    global openai

    if openai is None:
        openai = OpenAI()

    return openai


anthropic = None


def anthropic_client():
    global anthropic

    if anthropic is None:
        anthropic = AsyncAnthropic()

    return anthropic
