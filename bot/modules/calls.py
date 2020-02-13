from typing import List

from pymongo.collection import Collection
from pyrogram import Client, Filters, Message

from bot import zzlib
from bot.texts.texts import HelpTexts
from bot.zzlib import SimplifiedUser

from . import advanced_calls
from .calls_dao import Call, CallsDAO


def load(
    bot_client: Client,
    db: Collection,
    bot_name: str,
    user_name: str,
    help_texts: HelpTexts,
    user_client: Client = None,
    voip=None,
    advanced_options: bool = False,
    whitelisted_chats: List[int] = [],
):

    # loads its DAO
    dao = CallsDAO(db)

    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=bot_name)

    def get_admin_and_creator_ids(
        client: Client, chat_id: int, call_name: str
    ) -> List[int]:
        """
        Devuelve lista con los ids de los administradores del canal/grupo
        y el creador de la call.

        :param client:      Pyrogram Client
        :param chat_id:     Group ID
        :param call_name:   Call name
        :return:            List of user ids
        """
        admins = client.get_chat_members(chat_id=chat_id, filter="administrators")
        creator = dao.get_call_creator(chat_id, call_name)

        admin_ids = [admin.user.id for admin in admins]
        if creator:
            admin_ids.append(creator.uid)
        return admin_ids

    # list and details
    # ----------------
    @bot_client.on_message(Filters.command(_expand_commands(["list", "calls"])))
    def lista(client: Client, message: Message):
        chat_id = message.chat.id
        calls_list = dao.get_group_calls(chat_id)
        info = [
            '''\n<b>{}</b>: "{}"'''.format(call.name, call.desc) for call in calls_list
        ]
        text = "".join(info)

        if text:
            client.send_message(
                chat_id=chat_id,
                text="Calls in this group:{}"
                "\n/create to create a new call"
                "\n/modify to edit description"
                "\n/detail to show more info".format(text),
                parse_mode="html",
            )
        else:
            help_texts(client, chat_id, "empty_calls")

    @bot_client.on_message(Filters.command(_expand_commands(["detail", "details"])))
    def detail(client: Client, message: Message):
        chat_id = message.chat.id
        calls_list = dao.get_group_calls(chat_id)
        info = list()
        for call in calls_list:
            owner = "".join(zzlib.text_mention(call.owner.uid, call.owner.fname))
            if call.users:
                users = ", ".join([user.fname for user in call.users])
            else:
                users = "-Empty call-"
            info.append(f"\n<b>{call.name}</b> (owner {owner}): {users}")

        if info:
            client.send_message(
                chat_id=chat_id,
                text=f'Calls in this group:{"".join(info)}',
                parse_mode="html",
            )
        else:
            help_texts(client, chat_id, "empty_calls")

    # create and modify
    # -----------------
    @bot_client.on_message(Filters.command(_expand_commands(["create"])))
    def create(client: Client, message: Message):
        # print(message)
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 1:
            help_texts(client, chat_id, "create")

        elif len(params) >= 2:
            exists = dao.check_call_exists(chat_id=chat_id, call_name=params[1])
            if not exists:
                desc = " ".join(params[2:]) if len(params) >= 3 else None
                call = Call(
                    group=chat_id,
                    name=params[1],
                    desc=desc,
                    owner=SimplifiedUser(
                        uid=message.from_user.id, fname=message.from_user.first_name,
                    ),
                )
                dao.create_call(call)
            else:
                help_texts(client, chat_id, "already_created")

    @bot_client.on_message(Filters.command(_expand_commands(["modify"])))
    def modify(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) >= 3:
            desc = " ".join(params[2:])
            success = dao.modify_call_description(
                chat_id=chat_id, name=params[1], desc=desc
            )
            if not success:
                help_texts(client, chat_id, "call_no_exists")

        else:
            help_texts(client, chat_id, "modify")

    # delete call
    # -----------
    @bot_client.on_message(Filters.command(_expand_commands(["delete", "remove"])))
    def delete(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id
        caller_id = message.from_user.id

        if len(params) == 2:
            call_name = params[1].lower()
            admin_ids = get_admin_and_creator_ids(client, chat_id, call_name)

            if caller_id in admin_ids:
                dao.delete_call(chat_id, call_name)
            else:
                help_texts(client, chat_id, "delete")

        else:
            help_texts(client, chat_id, "delete")

    # join and leave calls (user himself)
    # -----------------------------------
    @bot_client.on_message(Filters.command(_expand_commands(["join"])))
    def join(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 2:
            call_name = params[1].lower()
            user = SimplifiedUser(
                uid=message.from_user.id, fname=message.from_user.first_name,
            )

            result = dao.add_users_to_call(
                chat_id=chat_id, name=call_name, users=[user]
            )
            if not result:
                help_texts(client, chat_id, "join")

        else:
            help_texts(client, chat_id, "join")

    @bot_client.on_message(Filters.command(_expand_commands(["leave", "exit", "quit"])))
    def leave(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 2:
            name = params[1].lower()
            user = SimplifiedUser(
                uid=message.from_user.id, fname=message.from_user.first_name,
            )
            dao.remove_users_from_call(chat_id=chat_id, name=name, users_ids=[user.uid])
        else:
            help_texts(client, chat_id, "leave")

    # add / kick other users
    # ----------------------
    @bot_client.on_message(Filters.command(_expand_commands(["add"])))
    def add_user(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) <= 2:
            help_texts(client, chat_id, "add")

        elif len(params) > 2:
            call_name = params[1].lower()
            users, errors = zzlib.extract_mentioned_users(client, message)

            result = dao.add_users_to_call(chat_id=chat_id, name=call_name, users=users)
            if not result:
                help_texts(client, chat_id, "add")
            elif errors:
                help_texts(client, chat_id, "add_users_errors")

    @bot_client.on_message(Filters.command(_expand_commands(["kick"])))
    def kick_user(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id
        caller = message.from_user.id

        if len(params) <= 2:
            help_texts(client, chat_id, "kick")

        else:
            call_name = params[1].lower()
            users, _ = zzlib.extract_mentioned_users(client, message)
            users_ids = [user.uid for user in users]
            admins_ids = get_admin_and_creator_ids(client, chat_id, call_name)

            if caller in admins_ids:
                dao.remove_users_from_call(
                    chat_id=chat_id, name=call_name, users_ids=users_ids
                )
            else:
                help_texts(client, chat_id, "kick")

    # call - mention logic
    # --------------------
    @bot_client.on_message(Filters.command(_expand_commands(["call"])))
    def call(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 1:
            help_texts(client, chat_id, "call")

        elif len(params) >= 2:
            name = params[1].lower()
            call = dao.get_call(chat_id, name)
            if call:
                mentions = " ".join(
                    [zzlib.text_mention(user.uid, user.fname) for user in call.users]
                )
                text = call.desc + "\n" + mentions
                client.send_message(message.chat.id, text, parse_mode="html")

            else:
                help_texts(client, chat_id, "call")

    print("Calls module loaded.")

    if advanced_options:
        advanced_calls.load(
            bot_client=bot_client,
            dao=dao,
            bot_name=bot_name,
            user_name=user_name,
            help_texts=help_texts,
            whitelisted_chats=whitelisted_chats,
            user_client=user_client,
            voip=voip,
        )
