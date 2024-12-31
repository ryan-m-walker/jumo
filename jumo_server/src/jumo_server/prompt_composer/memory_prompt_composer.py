from jumo_server.memory import memory_client
from .prompt_composer import PromptComposer


class MemoryPromptComposer(PromptComposer):
    def __init__(self, query: str, user_id: str):
        self._query = query
        self._user_id = user_id

    def compose(self) -> str:
        memories = memory_client().search(query=self._query, user_id=self._user_id)

        output = "## Memories are things that you remember from past interactions:\n\n"
        output += "<memories>\n"

        for m in memories["results"]:
            output += f"<memory score=\"{m['score']}\" created_at=\"{m['created_at']}\" updated_at=\"{m['updated_at']}\">{m['memory']}</memory>\n"

        output += "</memories>\n"

        return output
