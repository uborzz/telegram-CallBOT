from pymongo.database import Database
from pyrogram import Client, Filters, Message
from apscheduler.schedulers.background import BackgroundScheduler

from .texts.texts import HelpTexts
from .modules import rolls, megacall, calls, doom


class Bot:

    def __init__(self, name: str, bot_client: Client,
                 database: Database = None,
                 scheduler: BackgroundScheduler = None):
        self.name = name
        self.client = bot_client
        self.db = database
        self.scheduler = scheduler
        self.help_texts = HelpTexts()

    def load(self,
             module_megacall: bool = True,
             module_calls: bool = True,
             module_roll: bool = True,
             module_doom: bool = True):

        # general help message
        @self.client.on_message(Filters.command(["help", f"help@{self.name}"]))
        def help_listener(client: Client, message: Message):
            self.help_texts(
                client=client, chat_id=message.chat.id, name="general")

        if module_megacall:
            megacall.load(bot_client=self.client, name=self.name)
        if module_calls:
            collection = self.db.calls
            calls.load(bot_client=self.client, db=collection,
                       bot_name=self.name, help_texts=self.help_texts)
        if module_roll:
            rolls.load(bot_client=self.client, name=self.name,
                       help_texts=self.help_texts)
        if module_doom:
            collection = self.db.doomed
            doom.load(bot_client=self.client, db=collection,
                      bot_name=self.name, scheduler=self.scheduler)

        print(f"㋡ Bot: {self.name} fully loaded!!!")
        return self

    def run(self):
        print(f"Running bot client...")
        self.client.run()
