from typing import Iterable

from anthropic.types.message_param import MessageParam
from jumo_server.db.messages import Message


def db_messages_to_input(messages: list[Message]) -> Iterable[MessageParam]:
    return [
        {
            "role": message['role'],
            "content": message['content'],
        }
        for message in messages
    ]

