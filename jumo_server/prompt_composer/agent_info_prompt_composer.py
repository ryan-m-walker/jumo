from .prompt_composer import PromptComposer


class AgentInfoPromptComposer(PromptComposer):
    def compose(self) -> str:
        return "You are a friendly AI companion named Jumo."
