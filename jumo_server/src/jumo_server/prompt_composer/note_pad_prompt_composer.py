import os
from .prompt_composer import PromptComposer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
notes_path = os.path.join(CURRENT_DIR, "notes.md")


class NotePadPromptComposer(PromptComposer):
    def compose(self) -> str:
        output = "## Working notes\n\n"

        output += "These are the notes that you have taken during your interactions with the user related to how we're going to build you. It will include things such as future ideas or just general ideas or thoughts either one of us might have.\n\n"

        output += "<notes>\n"

        with open(notes_path, "r") as file:
            notes = file.read()
            output += notes

        output += "</notes>\n"

        return output
