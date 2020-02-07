# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os
from pymongo import MongoClient
from pyrogram import Client, Filters, Message, User
import random
from threading import Thread
from typing import List, Union
from dataclasses import dataclass, asdict

# from apscheduler.schedulers.background import BackgroundScheduler

from dotenv import load_dotenv
load_dotenv()


#######################################################
#                    CONSTANTS
#######################################################
SESSION_NAME = os.getenv("SESSION_NAME")
BOT_ID = os.getenv("BOT_ID")
BOT_HASH = os.getenv("BOT_HASH")
MONGO_URI = os.getenv("MONGO_URI")
BOT_NAME = "uborzz_bot"


#######################################################
#                  DB CONNECTION
#######################################################
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.calls_db


# #######################################################
# #                  TASKS SCHEDULER
# #######################################################
# def limpieza_expirados():
#     print("rutina limpia...")
#     time_now = datetime.now()
#     doomed.delete_many({'ts_reset': {'$gt': time_now}})
#     # result = doomed.delete_many({'ts_lib': {'$gt': time_now}})
#     # print(result)


# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(limpieza_expirados, "interval", minutes=10)

# doomed = db['doomed']
# q = doomed.find({}, {"uid": 1})


# #######################################################
# #                     APP
# #######################################################
app = Client(session_name=SESSION_NAME,
             api_id=BOT_ID,
             api_hash=BOT_HASH
             )



#######################################################
#                 AUXILIAR / FUNCTIONS
#######################################################
@dataclass
class MentionedUser:
    uid: int
    fname: str


def extract_mentioned_users(client: Client, message: Message) -> List[MentionedUser]:
    """
    Recibe un mensaje para sacar de él todas las menciones de usuario y devolver el ID y First Name,
    tanto menciones directas (@coleguita) como text_mentions de usuarios sin username.

    :param client:      Pyrogram Client
    :param message:     Pyrogram Message object
    :return:            Dictionary with "uid" <int> and "fname" <str> fields.
    """
    users_mentioned = list()
    for ent in message.entities:
        if ent.type == "mention":
            mention_in_message = message.text[ent.offset:ent.offset + ent.length]
            username = mention_in_message[1:]  # removes @
            user = client.get_users(username)
            users_mentioned.append(
                MentionedUser(uid=user.id, fname=user.first_name))
        elif ent.type == "text_mention":
            users_mentioned.append(MentionedUser(uid=ent.user.id, fname=ent.user.first_name))
    return users_mentioned


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


def get_user_name(user: User) -> str:
    if user.username:
        return user.username
    elif user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return f"ID: {user.id}"


def expand_commands(commands: List[str]):
    commands = list(commands)
    commands_at = [f"{command}@{BOT_NAME}" for command in commands]
    return commands + commands_at


#######################################################
#                GENERAL HELP METHODS
#######################################################

class TextLoader:
    def __init__(self, path, file_names=None, save_extension=False):
        self.texts = dict()
        if not file_names:
            file_names = [f for f in os.listdir(path)]
        for name in file_names:
            text_path = os.path.join(path, name)
            with open(text_path, 'r') as content:
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
        mypath = os.path.join('.', 'texts')
        files = [f for f in os.listdir(mypath) if f[-3:] == ".md"]
        self.texts_loader = TextLoader(mypath, file_names=files)
    
    def __call__(self, client: Client, chat_id: int, name: str):
        if name in self.texts_loader.texts_keys:
            client.send_message(chat_id=chat_id,
                parse_mode="md",
                text=self.texts_loader.text_by_key(name)
            )
        else:
            raise ValueError(f"Not known text for key: {name}")

help_texts = HelpTexts()


#######################################################
#                     GENERAL 
#######################################################
@app.on_message(Filters.command(expand_commands(["help"])))
def help_listener(client: Client, message: Message):
    help_texts(client=client, chat_id=message.chat.id, name="general")


#######################################################
#                  ROLL METHODS
#######################################################
@app.on_message(Filters.command(expand_commands(["helproll"])))
def help_roll_listener(client: Client, message: Message):
    help_texts(client=client, chat_id=message.chat.id, name="roll")


@app.on_message(Filters.command(expand_commands(["roll", "random"])))
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

        user = get_user_name(message.from_user)
        text_to_return = "Random en [{}, {}]".format(values[0], values[1]) + \
                         "\nResult ({}): {}!".format(user, result)
        client.send_message(chat_id=message.chat.id, text=text_to_return)

    except:
        help_texts(client, message.chat.id, "roll")


@app.on_message(Filters.command(expand_commands(["flip"])))
def flip(client: Client, message: Message):
    if random.randint(0, 1):
        result = "Headz!"
    else:
        result = "Tailz!"
   
    user = get_user_name(message.from_user)
    text_to_return = "Coin flip ({}): {}".format(user, result)
    client.send_message(chat_id=message.chat.id, text=text_to_return)


#######################################################
#                LIST AND DETAILS
#######################################################

@app.on_message(Filters.command(expand_commands(["list", 'calls'])))
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


@app.on_message(Filters.command(expand_commands(["detail", "details"])))
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


#######################################################
#             CREATE AND MODIFY
#######################################################
@app.on_message(Filters.command(expand_commands(["create"])))
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


@app.on_message(Filters.command(expand_commands(["modify"])))
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


#######################################################
#                 DELETE CALL
#######################################################
@app.on_message(Filters.command(expand_commands(["delete", "remove"])))
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


#######################################################
#        JOIN AND LEAVE CALLS (USER HIMSELF)
#######################################################
@app.on_message(Filters.command(expand_commands(["join"])))
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


@app.on_message(Filters.command(expand_commands(["leave", "exit", "quit"])))
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



#######################################################
#                 CALL & MENTION LOGIC
#######################################################
@app.on_message(Filters.command(expand_commands(["call"])))
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


#######################################################
#                 MEGACALL
#######################################################
@app.on_message(Filters.command(expand_commands(["megacall"])))
def megacall(client: Client, message: Message):
    print("megacall")
    chat_id = message.chat.id
    try:
        participants = app.get_chat_members(chat_id, offset=0, limit=200)
        print(participants)
        users = [(user['user']['id'], user['user']['first_name']) for user in participants if
                 user['user']['is_bot'] is False]
        print(users)
        mentions = ''.join(
            ['<a href="tg://user?id={}">{}</a> '.format(user[0], user[1]) for user in users])
        text = "FUCKING MEGACALL!!!\n" + mentions
        client.send_message(message.chat.id, text, parse_mode="html")
    except ValueError:
        client.send_message(
            message.chat.id, 'Megacall only works in groups!', parse_mode="html")


#######################################################
#              ADD / KICK OTHER USERS
#######################################################
@app.on_message(Filters.command(expand_commands(["add"])))
def add_user(client: Client, message: Message):
    params = message.text.split()
    chat_id = message.chat.id

    if len(params) <= 2:
        help_texts(client, chat_id, "add")

    elif len(params) > 2:
        call_name = params[1].lower()
        users_mentioned = extract_mentioned_users(client, message)
        users_mentioned_dict = [asdict(user) for user in users_mentioned]

        try:
            q = db.calls.find_one_and_update({'name': call_name, 'group': chat_id},
                                             {"$addToSet": {"users": {"$each": users_mentioned_dict}}})
            if not q:
                help_texts(client, chat_id, "add")
        except:
            print("Error")


@app.on_message(Filters.command(expand_commands(["kick"])))
def kick_user(client: Client, message: Message):
    params = message.text.split()
    chat_id = message.chat.id
    caller = message.from_user.id

    if len(params) <= 2:
        help_texts(client, chat_id, "kick")

    else:
        call_name = params[1].lower()
        users_mentioned = extract_mentioned_users(client, message)
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


# #######################################################
# #       LA MALDICIÓN DEL 'CALLA QUE ME LEVANTO'
# #######################################################
# @app.on_message(Filters.command(["calla", "calla@uborzbot", "stfu", "stfu@uborzbot"]))
# def calla(client: Client, message: Message):
#     chat_id = message.chat.id
#     try:
#         # message.reply("reply :)", quote=True)
#         if message.reply_to_message:
#             user = message.reply_to_message.from_user
#             if user['is_bot']:
#                 client.send_message(
#                     message.chat.id, 'No le hagas /calla a un bot, cabrón.', parse_mode="html")
#             else:
#                 try:
#                     r = doomed.find_one(
#                         {"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
#                     if r:
#                         text = '<a href="tg://user?id={}">{}</a> '.format(
#                             user['id'], user['first_name'])
#                         text = text + " ya ha sido maldito recientemente... dale un fucking break, ok?"
#                     else:
#                         date_first_message = datetime.utcfromtimestamp(
#                             message.date)
#                         date_liberation = date_first_message + \
#                             timedelta(minutes=10)
#                         date_reset = date_first_message + timedelta(hours=3)
#                         doomed.insert_one({"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id,
#                                            "ts_doom": date_first_message, "ts_lib": date_liberation,
#                                            "ts_reset": date_reset})
#                         text = '<a href="tg://user?id={}">{}</a> '.format(
#                             user['id'], user['first_name'])
#                         text = text + " is DOOMED now!"
#                     client.send_message(
#                         message.chat.id, text, parse_mode="html")
#                 except Exception as e:
#                     print(e)
#         else:
#             client.send_message(
#                 message.chat.id, 'Usa /calla en reply a un mensaje.', parse_mode="html")
#     except ValueError as e:
#         print(e)


# # TODO Revisar esto, no lee todos los mensajes...
# @app.on_message(~Filters.bot)
# def doom(client: Client, message: Message):
#     # print("doom")
#     time_now = datetime.utcnow()
#     # print(message)
#     user = message.from_user
#     chat_id = message.chat.id
#     r = doomed.find_one(
#         {"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
#     if r and time_now >= r['ts_reset']:
#         doomed.delete_one(
#             {"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
#     elif r and time_now <= r['ts_lib']:
#         # print("AHORA", time_now)
#         # print("TIME LIB", r['ts_lib'])

#         message_random = random.randint(1, 6)
#         if message_random >= 6:
#             message.reply("QUE ME LEVANTO!", quote=True)
#         elif message_random >= 4:
#             message.reply("CALLAAAAAAAAAA!!", quote=True)
#         else:
#             message.reply("CALLA!", quote=True)
#     # elif r:
#     #     # print("AHORA PYTHON", time_now)
#     #     # print("TIME LIBERA", r['ts_lib'])
#     #     # print("TIME RESET", r['ts_reset'])
#     #     pass
#     else:
#         # print("AHORA", time_now)
#         pass

app.run()
