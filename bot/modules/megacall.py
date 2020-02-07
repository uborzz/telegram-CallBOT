
from pyrogram import Client, Filters, Message
from typing import List

from bot import zzlib


def load(bot_client: Client, name: str):

    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=name)

    @bot_client.on_message(Filters.command(_expand_commands(["megacall"])))
    def megacall(client: Client, message: Message):
        print("megacall")
        chat_id = message.chat.id
        try:
            participants = client.get_chat_members(chat_id, offset=0, limit=200)
            print(participants)
            users = [(user['user']['id'], user['user']['first_name']) for user in participants if
                    user['user']['is_bot'] is False]
            print(users)
            mentions = ''.join(
                ['<a href="tg://user?id={}">{}</a> '.format(user[0], user[1]) for user in users])
            text = "FUCKING MEGACALL!!!\n" + mentions
            client.send_message(message.chat.id, text, parse_mode="html")
        except ValueError:
            client.send_message(
                message.chat.id, 'Megacall only works in groups!', parse_mode="html")

    print("Megacall module loaded.")