from datetime import datetime, timedelta
from typing import List

from pyrogram import Client, Filters, Message
from pyrogram.errors import PeerIdInvalid
from tgvoip_pyrogram import VoIPFileStreamService

from bot import zzlib
from bot.texts.texts import HelpTexts

from .calls_dao import CallsDAO
from .megacall import all_mentions

"""
This module requires a telegram user client.
Using a whitelist of chat groups to avoids bad use of the running bot.
"""


# async def stop_after(call, seconds):
#     print("ENTERING")
#     await asyncio.sleep(seconds)
#     print("STOPPING")
#     del call


def load(
    bot_client: Client,
    dao: CallsDAO,
    bot_name: str,
    user_name: str,
    help_texts: HelpTexts,
    user_client: Client = None,
    voip: VoIPFileStreamService = None,
    whitelisted_chats=[],
):
    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=bot_name)

    # temporz message logic
    # ---------------------
    @bot_client.on_message(
        Filters.chat(whitelisted_chats) & Filters.command(_expand_commands(["temp"]))
    )
    def temporized(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 3:
            name = params[1].lower()
            minutes = params[2]
            if minutes.isdecimal() and int(minutes) <= 1000:
                minutes = int(minutes)
                call = dao.get_call(chat_id, name)
                if call:

                    # to prevent calls to people outside of the group...
                    members = client.get_chat_members(chat_id, offset=0, limit=200)
                    users_in_group = [
                        member.user.id for member in members if not member.user.is_bot
                    ]

                    # write to doppelganger
                    mentions = all_mentions(client, chat_id)
                    client.send_message(
                        chat_id=user_name, text=mentions, parse_mode="html"
                    )

                    text = f"Temporized message ⏰\n"
                    text += f"To call: **{call.name}**\n"
                    text += f"Text: __{call.desc}__\n"
                    text += f"When: in {minutes} minutes."

                    client.send_message(chat_id=chat_id, text=text, parse_mode="md")
                    ts = int(
                        datetime.timestamp(datetime.now() + timedelta(minutes=minutes))
                    )
                    for user in call.users:
                        if user.uid in users_in_group:
                            try:
                                user_client.send_message(
                                    chat_id=user.uid,
                                    text=call.desc,
                                    parse_mode="md",
                                    schedule_date=ts,
                                )
                            except PeerIdInvalid as e:
                                print("FAILED!", e.NAME)
                    return

        help_texts(client, chat_id, "temp")

    # cast message logic
    # ---------------------
    @bot_client.on_message(
        Filters.chat(whitelisted_chats)
        & Filters.command(_expand_commands(["cast", "priv"]))
    )
    def private(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) >= 2:
            name = params[1].lower()

            call = dao.get_call(chat_id, name)
            if call:

                cast_text = " ".join(params[2:]) if len(params) > 2 else call.desc

                # to prevent calls to people outside of the group...
                members = client.get_chat_members(chat_id, offset=0, limit=200)
                users_in_group = [
                    member.user.id for member in members if not member.user.is_bot
                ]

                # write to doppelganger
                mentions = all_mentions(client, chat_id)
                client.send_message(chat_id=user_name, text=mentions, parse_mode="html")

                text = f"Priv message's gonna be broadcasted.\n"
                text += f"To call: **{call.name}**\n"
                text += f"Text: __{cast_text}__"
                client.send_message(chat_id=chat_id, text=text, parse_mode="md")

                for user in call.users:
                    if user.uid in users_in_group:
                        # bot_peers = client.get_users([user.uid])
                        # user_peers = user_client.get_users([user.uid])
                        # client.resolve_peer(user.uid)
                        # bot_client.resolve_peer(user.uid)
                        # client.fetch_peers(peers)

                        try:
                            user_client.send_message(
                                chat_id=user.uid, text=cast_text, parse_mode="md",
                            )
                        except PeerIdInvalid as e:
                            print("FAILED!", e.NAME)

                return

        help_texts(client, chat_id, "cast")

    # making outgoing calls
    @bot_client.on_message(
        Filters.chat(whitelisted_chats) & Filters.command(_expand_commands(["ring"]))
    )
    def ring(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 2:
            name = params[1].lower()

            call = dao.get_call(chat_id, name)
            if call:

                # to prevent calls to people outside of the group...
                members = client.get_chat_members(chat_id, offset=0, limit=200)
                users_in_group = [
                    member.user.id for member in members if not member.user.is_bot
                ]

                # write to doppelganger
                mentions = all_mentions(client, chat_id)
                client.send_message(chat_id=user_name, text=mentions, parse_mode="html")

                text = f"Ringin bastards ☎\n"
                text += f"To call: **{call.name}**"

                client.send_message(chat_id=chat_id, text=text, parse_mode="md")

                for user in call.users:
                    if user.uid in users_in_group:
                        try:
                            phone_call = voip.start_call(user.uid)
                            # print(type(phone_call), dir(phone_call))
                            phone_call.stop()
                        except PeerIdInvalid as e:
                            print("FAILED!", e.NAME)
                return

        help_texts(client, chat_id, "ring")

    # @bot_client.on_message(
    #     Filters.chat(whitelisted_chats)
    #     & Filters.command(_expand_commands(["phone", "audio"]))
    # )
    # def voice(client: Client, message: Message):
    #     params = message.text.split()
    #     chat_id = message.chat.id

    #     if len(params) >= 2:
    #         name = params[1].lower()

    #         call = dao.get_call(chat_id, name)
    #         if call:
    #             msg = " ".join(params[2:]) if len(params) > 2 else call.desc

    #             # to prevent calls to people outside of the group...
    #             members = client.get_chat_members(chat_id, offset=0, limit=200)
    #             users_in_group = [
    #                 member.user.id for member in members if not member.user.is_bot
    #             ]

    #             text = f"Callin bastards via phone ☎\n"
    #             text += f"To call: **{call.name}**\n"
    #             text += f"Text: __{msg}__"

    #             client.send_message(chat_id=chat_id, text=text, parse_mode="md")

    #             for user in call.users:
    #                 if user.uid in users_in_group:
    #                     try:
    #                         call = voip.start_call(user.uid)
    #                         call.play("audio.raw")
    #                     except PeerIdInvalid as e:
    #                         print("FAILED!", e.NAME)

    #         return

    #     # help_texts(client, chat_id, "phone")

    print("Advanced calls module loaded.")
