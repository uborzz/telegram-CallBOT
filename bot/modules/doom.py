
from datetime import datetime, timedelta
from pyrogram import Client, Filters, Message
from typing import List
from pymongo.collection import Collection
from apscheduler.schedulers.background import BackgroundScheduler
from random import randint

from bot import zzlib


def load(bot_client: Client, db: Collection, bot_name: str, scheduler: BackgroundScheduler):

    def limpieza_expirados():
        print("rutina limpia...")
        time_now = datetime.now()
        db.delete_many({'ts_reset': {'$gt': time_now}})

    scheduler.add_job(limpieza_expirados, "interval", minutes=10)

    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=bot_name)

    @bot_client.on_message(Filters.command(_expand_commands(["calla", "stfu"])))
    def calla(client: Client, message: Message):
        chat_id = message.chat.id
        try:
            if message.reply_to_message:
                user = message.reply_to_message.from_user
                if user['is_bot']:
                    client.send_message(
                        message.chat.id, 'No le hagas /calla a un bot, cabrón.', parse_mode="html")
                else:
                    try:
                        r = db.find_one(
                            {"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
                        if r:
                            text = '<a href="tg://user?id={}">{}</a> '.format(
                                user['id'], user['first_name'])
                            text = text + " ya ha sido maldito recientemente... dale un fucking break, ok?"
                        else:
                            date_first_message = datetime.utcfromtimestamp(
                                message.date)
                            date_liberation = date_first_message + \
                                timedelta(minutes=10)
                            date_reset = date_first_message + timedelta(hours=3)
                            db.insert_one({"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id,
                                               "ts_doom": date_first_message, "ts_lib": date_liberation,
                                               "ts_reset": date_reset})
                            text = '<a href="tg://user?id={}">{}</a> '.format(
                                user['id'], user['first_name'])
                            text = text + " is DOOMED now!"
                        client.send_message(
                            message.chat.id, text, parse_mode="html")
                    except Exception as e:
                        print(e)
            else:
                client.send_message(
                    message.chat.id, 'Usa /calla en reply a un mensaje.', parse_mode="html")
        except ValueError as e:
            print(e)


    @bot_client.on_message(~Filters.bot)
    def doom(_: Client, message: Message):
        time_now = datetime.utcnow()
        user = message.from_user
        chat_id = message.chat.id
        r = db.find_one(
            {"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
        if r and time_now >= r['ts_reset']:
            db.delete_one(
                {"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
        elif r and time_now <= r['ts_lib']:
            message_random = randint(1, 6)
            if message_random >= 6:
                message.reply("QUE ME LEVANTO!", quote=True)
            elif message_random >= 4:
                message.reply("CALLAAAAAAAAAA!!", quote=True)
            else:
                message.reply("CALLA!", quote=True)

    print("DOOM module loaded.")