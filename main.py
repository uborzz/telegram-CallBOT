# -*- coding: utf-8 -*-
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from pymongo import MongoClient
from pyrogram import Client
from tgvoip_pyrogram import VoIPFileStreamService

from bot.bot import Bot

load_dotenv()


# constants
# ---------
BOT_SESSION_NAME = os.getenv("BOT_SESSION_NAME")
USER_SESSION_NAME = os.getenv("USER_SESSION_NAME")
APP_ID = os.getenv("APP_ID")
APP_HASH = os.getenv("APP_HASH")
MONGO_URI = os.getenv("MONGO_URI")
BOT_NAME = "bot_acc"
USER_NAME = "user_acc"
DB_NAME = "calls_db"


def main():

    print("Creating the scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.start()

    print("Connecting to the database...")
    db_client = MongoClient(MONGO_URI)
    database = db_client[DB_NAME]

    print("Instantiating the Pyrogram bot client...")
    pyrogram_bot_client = Client(
        session_name=BOT_SESSION_NAME, api_id=APP_ID, api_hash=APP_HASH
    )

    print("Instantiating the Pyrogram user client...")
    pyrogram_user_client = Client(
        session_name=USER_SESSION_NAME, api_id=APP_ID, api_hash=APP_HASH
    )

    voip_service = VoIPFileStreamService(pyrogram_user_client, receive_calls=False)

    print("Instantiating the bot...")

    # prov test group. TODO manage with database and admin commands.
    whitelist = [
        -341964353,
    ]
    bot = Bot(
        name=BOT_NAME,
        user_name=USER_NAME,
        bot_client=pyrogram_bot_client,
        user_client=pyrogram_user_client,
        database=database,
        scheduler=scheduler,
        voip_service=voip_service,
        whitelisted_chats=whitelist,
    )

    bot.load_modules(submodule_advanced_calls=True)
    bot.run()


if __name__ == "__main__":
    main()
