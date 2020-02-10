# -*- coding: utf-8 -*-
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from pymongo import MongoClient
from pyrogram import Client

from bot.bot import Bot

load_dotenv()


# constants
# ---------
SESSION_NAME = os.getenv("SESSION_NAME")
BOT_ID = os.getenv("BOT_ID")
BOT_HASH = os.getenv("BOT_HASH")
MONGO_URI = os.getenv("MONGO_URI")
BOT_NAME = "uborzz_bot"
DB_NAME = "calls_db"


def main():

    print("Creating the scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.start()

    print("Connecting to the database...")
    db_client = MongoClient(MONGO_URI)
    database = db_client[DB_NAME]

    print("Instantiating the Pyrogram client...")
    pyrogram_client = Client(
        session_name=SESSION_NAME, api_id=BOT_ID, api_hash=BOT_HASH
    )

    print("Instantiating the bot...")
    bot = Bot(
        name=BOT_NAME,
        bot_client=pyrogram_client,
        database=database,
        scheduler=scheduler,
    )

    bot.load_modules()
    bot.run()


if __name__ == "__main__":
    main()
