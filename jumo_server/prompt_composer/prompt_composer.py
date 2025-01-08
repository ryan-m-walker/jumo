from abc import ABC, abstractmethod


class PromptComposer(ABC):
    @abstractmethod
    def compose(self) -> str:
        pass
