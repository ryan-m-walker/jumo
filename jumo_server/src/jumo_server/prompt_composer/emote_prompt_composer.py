from .prompt_composer import PromptComposer

EMOTES = [
    "NEUTRAL_SMILE",
    "SMILEY",
    "HAPPY",
    "SUNGLASSES",
    "WINK",
    "NEUTRAL",
    "EXPRESSIONLESS",
    "SMILE",
    "SWEAT_SMILE",
    "UPSIDE_DOWN",
    "CURIOUS",
    "THINKING",
    "CONCERNED",
]


class EmotePromptComposer(PromptComposer):
    def compose(self) -> str:
        output = "## Emoting\n\n"

        output += "You can express yourself using emotes to show your emotions. To do an emote you just need to wrap an emote keyword in an <emote> tag."
        output += "For example, if you are happy you can do something like: 'I am happy! <emote>SMILE</emote>'\n"
        output += "The way your emote will be rendered will be something like this:\n"
        output += "For the emote HAPPY,  it will be rendered as:\n"
        output += """\

     ▞▀▀▚           ▞▀▀▚

            ▚▄▄▄▞
"""
        output += "Here are some examples of the basic emote format to work with. It roughly uses the 'Kaomoji' style of emotes but you should always try to use ascii instead of UTF-8 characters"

        for emote in EMOTES:
            output += f"\n\n- {emote}"

        return output
