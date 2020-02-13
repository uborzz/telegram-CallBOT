from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from pymongo.database import Database
from pyrogram import Client, Filters, Message
from tgvoip_pyrogram import VoIPFileStreamService

from .modules import calls, doom, megacall, rolls
from .texts.texts import HelpTexts


class Bot:
    def __init__(
        self,
        name: str,
        user_name: str,
        bot_client: Client,
        user_client: Client,
        voip_service: VoIPFileStreamService,
        database: Database = None,
        scheduler: BackgroundScheduler = None,
        whitelisted_chats: List[int] = None,  # move to module
    ):
        self.name = name
        self.user_name = user_name
        self.client = bot_client
        self.user_client = user_client
        self.db = database
        self.scheduler = scheduler
        self.voip_service = voip_service
        self.help_texts = HelpTexts()
        self.whitelisted_chats = whitelisted_chats

    def load_modules(
        self,
        module_megacall: bool = True,
        module_calls: bool = True,
        module_roll: bool = True,
        module_doom: bool = True,
        submodule_advanced_calls: bool = False,
    ):

        # general help message
        @self.client.on_message(Filters.command(["help", f"help@{self.name}"]))
        def help_listener(client: Client, message: Message):
            self.help_texts(client=client, chat_id=message.chat.id, name="general")

        # general help message
        @self.client.on_message(
            Filters.command(["groupinfo", f"groupinfo@{self.name}"])
        )
        def help_groupinfo(client: Client, message: Message):
            client.send_message(message.chat.id, text=message.chat)

        if module_megacall:
            text = "FUCKING MEGACALL!!!\n"
            megacall.load(bot_client=self.client, name=self.name, megacall_text=text)
        if module_calls:
            collection = self.db.calls
            calls.load(
                bot_name=self.name,
                user_name=self.user_name,
                bot_client=self.client,
                user_client=self.user_client,
                db=collection,
                advanced_options=submodule_advanced_calls,
                voip=self.voip_service,
                help_texts=self.help_texts,
                whitelisted_chats=self.whitelisted_chats,
            )
        if module_roll:
            rolls.load(
                bot_client=self.client, name=self.name, help_texts=self.help_texts
            )
        if module_doom:
            collection = self.db.doomed
            doom.load(
                bot_client=self.client,
                collection=collection,
                bot_name=self.name,
                scheduler=self.scheduler,
                whitelisted_chats=self.whitelisted_chats,
            )

        print(f"㋡ Bot: {self.name} fully loaded!!!")
        return self

    def run(self):
        print(f"Running bot clients...")
        self.user_client.start()
        self.client.run()
        print("pyrogram bot client stopped.")
        self.user_client.stop()
        print("pyrogram user client stopped.")
