from jumo_server.llm import LLM
from jumo_server.llm.gemini import Gemini


def get_llm() -> LLM:
    return Gemini()
