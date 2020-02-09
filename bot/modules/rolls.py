import random
from typing import List

from pyrogram import Client, Filters, Message

from bot import zzlib
from bot.texts.texts import HelpTexts


def load(bot_client: Client, name: str, help_texts: HelpTexts):
    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=name)

    @bot_client.on_message(Filters.command(_expand_commands(["helproll"])))
    def help_roll_listener(client: Client, message: Message):
        help_texts(client=client, chat_id=message.chat.id, name="roll")

    @bot_client.on_message(
        Filters.command(_expand_commands(["roll", "random", "dados"]))
    )
    def roll(client: Client, message: Message):
        try:
            params = message.text.split()
            lower, upper = [0, 100]

            if len(params) == 1:
                result = random.randint(0, 100)
            elif len(params) == 2:
                upper = int(params[1])
                result = random.randint(0, upper)
            elif len(params) == 3:
                lower = int(params[1])
                upper = int(params[2])
                if lower > upper:
                    lower, upper = upper, lower
                result = random.randint(lower, upper)
            else:
                help_texts(client, message.chat.id, "roll")
                return

            user = zzlib.get_user_name(message.from_user)
            text_to_return = f"Random en [{lower}, {upper}]\nResult ({user}): {result}!"
            client.send_message(chat_id=message.chat.id, text=text_to_return)

        except ValueError:
            help_texts(client, message.chat.id, "roll")

    @bot_client.on_message(Filters.command(_expand_commands(["flip", "coin"])))
    def flip(client: Client, message: Message):
        if random.randint(0, 1):
            result = "Headz!"
        else:
            result = "Tailz!"

        user = zzlib.get_user_name(message.from_user)
        text_to_return = f"Coin flip ({user}): {result}"
        client.send_message(chat_id=message.chat.id, text=text_to_return)

    print("Rolls module loaded.")
