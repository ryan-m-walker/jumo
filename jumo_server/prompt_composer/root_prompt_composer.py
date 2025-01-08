from typing import Iterable
from .prompt_composer import PromptComposer


class RootPromptComposer(PromptComposer):
    def __init__(self, composers: Iterable[PromptComposer] = []):
        self._composers = composers

    def compose(self) -> str:
        output = ""

        for composer in self._composers:
            output += composer.compose()
            output += "\n\n"

        return output
