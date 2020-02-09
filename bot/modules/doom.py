from datetime import datetime, timedelta
from random import randint
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from pymongo.collection import Collection
from pyrogram import Client, Filters, Message

from bot import zzlib

from .doom_dao import DoomDAO, DoomedUser


def load(
    bot_client: Client,
    collection: Collection,
    bot_name: str,
    scheduler: BackgroundScheduler,
    doom_duration: int = 10,
    doom_cooldown: int = 180,
):

    # loads its DAO
    dao = DoomDAO(collection)

    # configures its scheduled tasks
    def cleansing():
        print("running cleansin rutine...")
        time_now = datetime.now()
        dao.clear(time_now)

    scheduler.add_job(cleansing, "interval", minutes=10)

    # aux functs
    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=bot_name)

    @bot_client.on_message(Filters.command(_expand_commands(["doom", "calla", "stfu"])))
    def calla(client: Client, message: Message):
        chat_id = message.chat.id
        command = message.command[0]

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            if user.is_bot:
                client.send_message(
                    chat_id,
                    f"No le hagas {command} a un bot, cabrón.",
                    parse_mode="html",
                )
            else:
                doomed_user: DoomedUser = dao.find(uid=user.id, chat_id=chat_id)
                if doomed_user:
                    text = f'<a href="tg://user?id={doomed_user.uid}">{doomed_user.first_name}</a> ya ha sido maldito recientemente... dale un fucking break, ok?'
                else:
                    date_first_message = datetime.utcfromtimestamp(message.date)
                    doomed_user = DoomedUser(
                        uid=user.id,
                        first_name=user.first_name,
                        chat_id=chat_id,
                        ts_doom=date_first_message,
                        ts_lib=date_first_message + timedelta(minutes=doom_duration),
                        ts_reset=date_first_message + timedelta(minutes=doom_cooldown),
                    )
                    dao.doom(doomed_user)
                    text = f'<a href="tg://user?id={user.id}">{user.first_name}</a> is DOOMED now!'
                client.send_message(message.chat.id, text, parse_mode="html")

        else:
            client.send_message(
                message.chat.id,
                f"Usa /{command} en reply a un mensaje.",
                parse_mode="html",
            )

    @bot_client.on_message(~Filters.bot)
    def doom(_: Client, message: Message):
        time_now = datetime.utcnow()
        user = message.from_user
        chat_id = message.chat.id
        doomed_user = dao.find(uid=user.id, chat_id=chat_id)
        if doomed_user and time_now >= doomed_user.ts_reset:
            dao.undoom(doomed_user)
        elif doomed_user and time_now <= doomed_user.ts_lib:
            message_random = randint(1, 6)
            if message_random >= 6:
                message.reply("QUE ME LEVANTO!", quote=True)
            elif message_random >= 4:
                message.reply("CALLAAAAAAAAAA!!", quote=True)
            else:
                message.reply("CALLA!", quote=True)

    print("DOOM module loaded.")
