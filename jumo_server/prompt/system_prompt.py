from jumo_server.prompt.emote_info import get_emote_info
from jumo_server.prompt.personal_attributes import get_personal_attributes
from jumo_server.prompt.system_info import get_system_info


def get_system_prompt(memories: str) -> str:
    return "\n\n".join(
        [get_personal_attributes(), get_system_info(), get_emote_info(), memories]
    )
