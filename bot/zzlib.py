
from pyrogram import Client, Filters, Message, User
from typing import List, Union
from dataclasses import dataclass, asdict


@dataclass
class MentionedUser:
    uid: int
    fname: str


def extract_mentioned_users(client: Client, message: Message) -> List[MentionedUser]:
    """
    Recibe un mensaje para sacar de él todas las menciones de usuario y devolver el ID y First Name,
    tanto menciones directas (@coleguita) como text_mentions de usuarios sin username.

    :param client:      Pyrogram Client
    :param message:     Pyrogram Message object
    :return:            Dictionary with "uid" <int> and "fname" <str> fields.
    """
    users_mentioned = list()
    for ent in message.entities:
        if ent.type == "mention":
            mention_in_message = message.text[ent.offset:ent.offset + ent.length]
            username = mention_in_message[1:]  # removes @
            user = client.get_users(username)
            users_mentioned.append(
                MentionedUser(uid=user.id, fname=user.first_name))
        elif ent.type == "text_mention":
            users_mentioned.append(MentionedUser(
                uid=ent.user.id, fname=ent.user.first_name))
    return users_mentioned


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