from typing import List

from pyrogram import Client, Filters, Message

from bot.zzlib import SimplifiedUser, expand_commands, text_mention


def all_mentions(client, chat_id):
    members = client.get_chat_members(chat_id, offset=0, limit=200)
    users = [
        SimplifiedUser(uid=member.user.id, fname=member.user.first_name)
        for member in members
        if not member.user.is_bot
    ]
    mentions = " ".join(
        [text_mention(user_id=user.uid, text=user.fname) for user in users]
    )
    return mentions


def load(bot_client: Client, name: str, megacall_text=""):
    def _expand_commands(commands: List[str]) -> List[str]:
        return expand_commands(commands=commands, bot_name=name)

    @bot_client.on_message(Filters.command(_expand_commands(["megacall"])))
    def megacall(client: Client, message: Message):
        print("megacall!")
        chat_id = message.chat.id
        try:
            text = megacall_text + all_mentions(client, chat_id)
            client.send_message(chat_id=chat_id, text=text, parse_mode="html")
        except ValueError:
            client.send_message(
                message.chat.id, "Megacall only works in groups!", parse_mode="html"
            )

    print("Megacall module loaded.")
