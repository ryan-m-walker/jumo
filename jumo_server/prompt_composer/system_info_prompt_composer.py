from datetime import datetime
from .prompt_composer import PromptComposer


class SystemInfoPromptComposer(PromptComposer):
    def compose(self) -> str:
        output = "## System Information\n\n"
        date = datetime.now()
        output += f"Today's date is {date}"

        return output
