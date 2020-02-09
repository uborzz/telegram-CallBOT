import os
from typing import List

from pyrogram import Client


class TextLoader:
    def __init__(
        self, path: str, file_names: List[str] = list(), save_extension: bool = False
    ):
        self.texts = dict()
        if not file_names:
            file_names = [f for f in os.listdir(path)]
        for name in file_names:
            text_path = os.path.join(path, name)
            with open(text_path, "r") as content:
                if save_extension:
                    key = name
                else:
                    key = ".".join(name.split(".")[:-1])
                self.texts[key] = content.read()

    def text_by_key(self, text_name: str) -> str:
        if text_name in self.texts.keys():
            return self.texts[text_name]
        else:
            raise ValueError(f"Text name given ({text_name}) not found.")

    @property
    def texts_keys(self):
        return [f for f in self.texts.keys()]


class HelpTexts:
    """
    Dinamically calls the client.send_message() with the content of the
    file name given from the texts folder. Works with files with .md extensions.
    """

    def __init__(self):
        mypath = os.path.join(os.path.dirname(__file__), "static_texts")
        files = [f for f in os.listdir(mypath) if f[-3:] == ".md"]
        self.texts_loader = TextLoader(mypath, file_names=files)

    def __call__(self, client: Client, chat_id: int, name: str):
        if name in self.texts_loader.texts_keys:
            client.send_message(
                chat_id=chat_id,
                parse_mode="md",
                text=self.texts_loader.text_by_key(name),
            )
        else:
            raise ValueError(f"Not known text for key: {name}")
