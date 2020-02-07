
from dataclasses import asdict
from pyrogram import Client, Filters, Message
from typing import List
from pymongo.collection import Collection

from bot import zzlib
from bot.texts.texts import HelpTexts


def load(bot_client: Client, db: Collection, bot_name: str, help_texts: HelpTexts):
    
    def _expand_commands(commands: List[str]) -> List[str]:
        return zzlib.expand_commands(commands=commands, bot_name=bot_name)

    def get_admin_and_creator_ids(client: Client, chat_id: int, call_name: str) -> List[int]:
        """
        Devuelve lista con los ids de los administradores del canal/grupo y el creador de la call.

        :param client:      Pyrogram Client
        :param chat_id:     Group ID
        :param call_name:   Call name
        :return:            List of user ids
        """
        admins = client.get_chat_members(
            chat_id=chat_id, filter="administrators")
        query_result = db.calls.find_one(
            {'name': call_name, 'group': chat_id}, {'owner': 1, '_id': 0})
        admin_ids = [user.user.id for user in admins]
        if query_result:
            creator_id = query_result['owner']['uid']
            admin_ids.append(creator_id)
        return admin_ids


    # list and details
    # ----------------
    @bot_client.on_message(Filters.command(_expand_commands(["list", 'calls'])))
    def lista(client: Client, message: Message):
        group = message.chat.id
        q = db.calls.find({'group': group}, {'name': 1, 'desc': 1, '_id': 0})
        info = [
            '''\n<b>{}</b>: "{}"'''.format(ele['name'], ele['desc']) for ele in q]
        text = ''.join(info)

        if text:
            client.send_message(chat_id=group,
                                text="Calls in this group:{}"
                                    "\n/create to create a new call"
                                    "\n/modify to edit description"
                                    "\n/detail to show more info".format(text),
                                parse_mode="html")
        else:
            help_texts(client, group, "empty_calls")


    @bot_client.on_message(Filters.command(_expand_commands(["detail", "details"])))
    def detail(client: Client, message: Message):
        group = message.chat.id
        q = db.calls.find({'group': group}, {'name': 1,
                                            'users': 1, 'owner': 1, '_id': 0})
        info = list()
        for element in q:
            owner = ''.join('<a href="tg://user?id={}">{}</a>'.format(
                element["owner"]["uid"], element["owner"]["fname"]))
            if element["users"]:
                users = ", ".join([user['fname'] for user in element['users']])
            else:
                users = "-Empty call-"
            info.append(
                "\n<b>{}</b> (owner {}): {}".format(element['name'], owner, users))

        if info:
            client.send_message(chat_id=group, text="Calls in this group:{}".format(
                ''.join(info)), parse_mode="html")
        else:
            help_texts(client, group, "empty_calls")


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
            q = db.calls.find_one({'group': chat_id,
                                'name': params[1].lower()})
            # print(q)
            if not q:
                if len(params) >= 3:
                    prov = params[2:]
                    desc = ' '.join(prov)
                else:
                    desc = "CALL: {}!".format(params[1].upper())
                fields = {'group': chat_id,
                        'name': params[1].lower(),
                        'desc': desc,
                        'owner': {'uid': message.from_user.id, 'fname': message.from_user.first_name},
                        'users': list()}
                # print(fields)
                db.calls.insert_one(fields)
                # print("created")
            else:
                print("already created")


    @bot_client.on_message(Filters.command(_expand_commands(["modify"])))
    def modify(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) >= 3:
            prov = params[2:]
            desc = ' '.join(prov)
            q = db.calls.find_one_and_update({'name': params[1].lower(), 'group': chat_id},
                                            {'$set': {'desc': desc}})
            if not q:
                client.send_message(chat_id=chat_id, text="Specified call does not exist"
                                                        "\n/create <name> <(desc)>")
            else:
                print("HOLA")
        else:
            client.send_message(chat_id=chat_id, text="Specify the name and description"
                                                    "\n/modify <name> <desc>")

    # delete call
    # -----------
    @bot_client.on_message(Filters.command(_expand_commands(["delete", "remove"])))
    def delete(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id
        caller = message.from_user.id

        if len(params) == 2:
            call_name = params[1].lower()
            admin_ids = get_admin_and_creator_ids(client, chat_id, call_name)

            if caller in admin_ids:
                try:
                    db.calls.find_one_and_delete(
                        {'name': call_name, 'group': chat_id})
                except:
                    print("Error")
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
            fname = message.from_user.first_name
            uid = message.from_user.id
            user = {'uid': uid, 'fname': fname}
            try:
                # print(call_name, update.message.chat_id)
                q = db.calls.find_one_and_update({'name': call_name, 'group': chat_id},
                                                {"$addToSet": {'users': user}})
                if not q:
                    help_texts(client, chat_id, "join")

            except:
                print("Nope")

        else:
            help_texts(client, chat_id, "join")


    @bot_client.on_message(Filters.command(_expand_commands(["leave", "exit", "quit"])))
    def leave(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id

        if len(params) == 2:
            name = params[1].lower()
            print("leave")
            fname = message.from_user.first_name
            uid = message.from_user.id
            user = {'uid': uid, 'fname': fname}
            try:
                print(name, chat_id)
                q = db.calls.find_one_and_update({'name': name, 'group': chat_id},
                                                {"$pull": {'users': user}})
                print(q)
            except:
                print("Nope")

        else:
            help_texts(client, chat_id, "leave")


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
            query = db.calls.find_one({'group': chat_id,
                                    'name': name}, {'desc': 1, 'users': 1, '_id': 0})
            if query:
                mentions = ''.join(
                    ['<a href="tg://user?id={}">{}</a> '.format(user["uid"], user["fname"]) for user in query['users']])
                text = query['desc'] + "\n" + mentions
                client.send_message(message.chat.id, text, parse_mode="html")

            else:
                help_texts(client, chat_id, "call")



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
            users_mentioned = zzlib.extract_mentioned_users(client, message)
            users_mentioned_dict = [asdict(user) for user in users_mentioned]

            try:
                q = db.calls.find_one_and_update({'name': call_name, 'group': chat_id},
                                                {"$addToSet": {"users": {"$each": users_mentioned_dict}}})
                if not q:
                    help_texts(client, chat_id, "add")
            except:
                print("Error")


    @bot_client.on_message(Filters.command(_expand_commands(["kick"])))
    def kick_user(client: Client, message: Message):
        params = message.text.split()
        chat_id = message.chat.id
        caller = message.from_user.id

        if len(params) <= 2:
            help_texts(client, chat_id, "kick")

        else:
            call_name = params[1].lower()
            users_mentioned = zzlib.extract_mentioned_users(client, message)
            users_mentioned_ids = [user.uid for user in users_mentioned]
            admin_and_creator_ids = get_admin_and_creator_ids(
                client, chat_id, call_name)
            print(users_mentioned_ids)

            if caller in admin_and_creator_ids:
                try:
                    q = db.calls.find_one_and_update({'name': call_name, 'group': chat_id},
                                                    {"$pull": {
                                                        "users": {"uid": {"$in": users_mentioned_ids}}}},
                                                    {"multi": True})
                    print(q)
                except:
                    print("Error")
            else:
                help_texts(client, chat_id, "kick")

    print("Calls module loaded.")