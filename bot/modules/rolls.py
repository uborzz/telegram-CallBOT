
from pyrogram import Client, Filters, Message
import random
from typing import List

from bot import zzlib
from bot.texts.texts import HelpTexts


def load(bot_client: Client, name: str, help_texts: HelpTexts):
    
    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=name)

    @bot_client.on_message(Filters.command(_expand_commands(["helproll"])))
    def help_roll_listener(client: Client, message: Message):
        help_texts(client=client, chat_id=message.chat.id, name="roll")


    @bot_client.on_message(Filters.command(_expand_commands(["roll", "random"])))
    def roll(client: Client, message: Message):
        try:
            values = [0, 100]
            params = message.text.split()
            result = None
            if len(params) == 1:
                result = random.randint(0, 100)
            else:
                if len(params) == 2:
                    result = random.randint(0, int(params[1]))
                    values[1] = params[1]
                elif len(params) == 3:
                    result = random.randint(int(params[1]), int(params[2]))
                    values[0] = params[1]
                    values[1] = params[2]

            if result is None:
                help_texts(client, message.chat.id, "roll")

            user = zzlib.get_user_name(message.from_user)
            text_to_return = "Random en [{}, {}]".format(values[0], values[1]) + \
                            "\nResult ({}): {}!".format(user, result)
            client.send_message(chat_id=message.chat.id, text=text_to_return)

        except ValueError:
            help_texts(client, message.chat.id, "roll")


    @bot_client.on_message(Filters.command(_expand_commands(["flip"])))
    def flip(client: Client, message: Message):
        if random.randint(0, 1):
            result = "Headz!"
        else:
            result = "Tailz!"
    
        user = zzlib.get_user_name(message.from_user)
        text_to_return = "Coin flip ({}): {}".format(user, result)
        client.send_message(chat_id=message.chat.id, text=text_to_return)

    print("Rolls module loaded.")