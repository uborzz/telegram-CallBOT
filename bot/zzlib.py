from dataclasses import dataclass, asdict
from typing import List

from pyrogram import Client, Message, User
from pyrogram.errors import BadRequest


@dataclass
class SimplifiedUser:
    uid: int
    fname: str

    @property
    def asdict(self):
        return asdict(self)


def extract_mentioned_users(client: Client, message: Message) -> List[SimplifiedUser]:
    """
    Recibe un mensaje para sacar de él todas las menciones de usuario y devolver
    el ID y First Name, tanto menciones directas (@coleguita) como text_mentions de
    usuarios sin username.

    :param client:      Pyrogram Client
    :param message:     Pyrogram Message object
    :return:            Dictionary with "uid" <int> and "fname" <str> fields.
    """
    users_mentioned = list()
    for entity in message.entities:
        errors = False
        try:
            if entity.type == "mention":
                mention_in_message = message.text[
                    entity.offset : entity.offset + entity.length
                ]
                username = mention_in_message[1:]  # removes @
                user = client.get_users(username)
                users_mentioned.append(
                    SimplifiedUser(uid=user.id, fname=user.first_name)
                )
            elif entity.type == "text_mention":
                users_mentioned.append(
                    SimplifiedUser(uid=entity.user.id, fname=entity.user.first_name)
                )
        except BadRequest:
            errors = True

    return users_mentioned, errors


def text_mention(user_id: int, text: str) -> str:
    return f'<a href="tg://user?id={user_id}">{text}</a>'


def get_user_name(user: User) -> str:
    if user.username:
        return user.username
    elif user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return f"ID: {user.id}"


def expand_commands(commands: List[str], bot_name: str):
    commands = list(commands)
    commands_at = [f"{command}@{bot_name}" for command in commands]
    return commands + commands_at
