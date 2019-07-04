# -*- coding: utf-8 -*-

from telegram.ext import Updater
import json
import requests
import pymongo
import random
import creds
from datetime import datetime, timedelta
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler

client = pymongo.MongoClient(creds.mongo_host, creds.mongo_port)
db = client.callsdb

rootpwr = 'https://api.telegram.org/bot'
vend = '&parse_mode=HTML&mtproto=true'

# pyrogram
from pyrogram import Client, Filters
from pyrogram.api import functions, types


def limpieza_expirados():
    print("rutina limpia...")
    time_now = datetime.now()
    doomed.delete_many({'ts_reset': {'$gt': time_now}})
    # result = doomed.delete_many({'ts_lib': {'$gt': time_now}})
    # print(result)


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(limpieza_expirados, "interval", minutes=10)
# scheduler.add_job(limpieza_expirados, "interval", minutes=1)

app = Client(creds.token,
             api_id=creds.id,
             api_hash=creds.hash)

updater = Updater(token=creds.token)
dispatcher = updater.dispatcher

doomed = db['doomed']
q = doomed.find({}, {"uid": 1})


#######################################################
#                GENERAL HELP METHODS
#######################################################
def help(bot, update):
    # print(update.message)
    bot.send_message(chat_id=update.message.chat_id, text="CallBOT v4.1! Commands: "
                                                          "\n/create - /delete - /list"
                                                          "\n/call - /join - /leave"
                                                          "\n/megacall - /calla"
                                                          "\n/helproll : help for /roll")


def help_call(client, chat_id):
    client.send_message(chat_id=chat_id, text="How to: /call <name>"
                                                          "\n* name must be a previously created call"
                                                          "\n/list or /detail to check the calls"
                                                          "\n/megacall for calling everyone in the group")


def help_create(client, chat_id):
    client.send_message(chat_id=chat_id, text="How to: /create <name> <(description)>"
                                              "\n* description is optional*")


def help_join(client, chat_id):
    client.send_message(chat_id=chat_id, text="How to: /join <name>"
                                              "\n* name must exist")


def help_leave(client, chat_id):
    client.send_message(chat_id=chat_id, text="How to: /leave <name>")


def help_delete(client, chat_id):
    client.send_message(chat_id=chat_id, text="How to: /delete <name>"
                                              "\nOnly group admins and call creators can delete calls")


#######################################################
#                  ROLL METHODS
#######################################################
def help_roll(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Roll: Use integer numbers: "
                                                          "\n/roll - random between 0 & 100"
                                                          "\n/roll <max> - between 0 & <max>"
                                                          "\n/roll <min> <max> - try to guess... "
                                                          "\n/flip - headz or tailz!")


def roll(bot, update):
    try:
        values = [0, 100]
        params = update.message.text.split()
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
        user = update.message.from_user.first_name + " " + update.message.from_user.last_name
        user = user.rstrip()
        text_to_return = "Random en [{}, {}]".format(values[0], values[1]) + \
                         "\nResult ({}): {}!".format(user, result)
        bot.send_message(chat_id=update.message.chat_id, text=text_to_return)
    except:
        help_roll(bot, update)


def flip(bot, update):
    if random.randint(0, 1):
        result = "Headz!"
    else:
        result = "Tailz!"
    user = update.message.from_user.first_name + " " + update.message.from_user.last_name
    user = user.rstrip()
    text_to_return = "Coin flip ({}): {}".format(user, result)
    bot.send_message(chat_id=update.message.chat_id, text=text_to_return)



#######################################################
#                LIST AND DETAILS
#######################################################

@app.on_message(Filters.command(["list", "list@uborzbot"]))
def lista(client, message):
    group = message.chat.id
    q = db.calls.find({'group': group}, {'name': 1, 'desc': 1, '_id': 0})
    info = ['''\n<b>{}</b>: "{}"'''.format(ele['name'], ele['desc']) for ele in q]
    text = ''.join(info)

    if text:
        client.send_message(chat_id=group,
                            text="Calls in this group:{}"
                                 "\n/create to create a new call"
                                 "\n/modify to edit description"
                                 "\n/detail to show more info".format(text),
                            parse_mode="html")
    else:
        client.send_message(chat_id=group, text="No calls found in this group"
                                             "\n/create to create a new call"
                                             "\n/help to list more commands")


@app.on_message(Filters.command(["detail", "details", "detail@uborzbot", "details@uborzbot"]))
def detail(client, message):
    group = message.chat.id
    q = db.calls.find({'group': group}, {'name': 1, 'users': 1, 'owner': 1, '_id': 0})
    info = list()
    for element in q:
        owner = ''.join('<a href="tg://user?id={}">{}</a>'.format(element["owner"]["uid"], element["owner"]["fname"]))
        if element["users"]:
            users = ", ".join([user['fname'] for user in element['users']])
        else:
            users = "-Empty call-"
        info.append("\n<b>{}</b> (owner {}): {}".format(element['name'], owner, users))

    if info:
        client.send_message(chat_id=group, text="Calls in this group:{}".format(''.join(info)), parse_mode="html")
    else:
        client.send_message(chat_id=group, text="No calls found in this group"
                                                "\n/create to create a new call"
                                                "\n/help to list more commands")


#######################################################
#             CREATE AND MODIFY
#######################################################
@app.on_message(Filters.command(["create", "create@uborzbot"]))
def create(client, message):
    # print(message)
    params = message.text.split()
    chat_id = message.chat.id

    if len(params) == 1:
        help_create(client, chat_id)

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


@app.on_message(Filters.command(["modify", "modify@uborzbot"]))
def modify(client, message):
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
@app.on_message(Filters.command(["delete", "delete@uborzbot"]))
def delete(client, message):
    params = message.text.split()
    chat_id = message.chat.id

    caller = message.from_user.id
    admins = client.get_chat_members(chat_id=chat_id, filter="administrators").chat_members

    if len(params) == 2:
        name = params[1].lower()
        query_result = db.calls.find_one({'name': name, 'group': chat_id}, {'owner': 1, '_id': 0})
        admin_ids = [user['user']['id'] for user in admins]
        if query_result:
            creator_id = query_result['owner']['uid']
            admin_ids.append(creator_id)
        print(admin_ids)

        if caller in admin_ids:
            print("delete", name)
            try:
                q = db.calls.find_one_and_delete({'name': name, 'group': chat_id})
            except:
                print("Error")
        else:
            help_delete(client, chat_id)

    else:
        help_delete(client, chat_id)


#######################################################
#        JOIN AND LEAVE CALLS (USER HIMSELF)
#######################################################
@app.on_message(Filters.command(["join", "join@uborzbot"]))
def join(client, message):
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
                help_join(client, chat_id)

        except:
            print("Nope")

    else:
        help_join(client, chat_id)


@app.on_message(Filters.command(["leave", "leave@uborzbot"]))
def leave(client, message):
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
        help_leave(client, chat_id)


#######################################################
#                 CALL & MENTION LOGIC
#######################################################
@app.on_message(Filters.command(["call", "call@uborzbot"]))
def call(client, message):
    params = message.text.split()
    chat_id = message.chat.id

    if len(params) == 1:
        help_call(client, chat_id)

    elif len(params) >= 2:
        name = params[1].lower()
        query = db.calls.find_one({'group': chat_id,
                                  'name': name}, {'desc': 1, 'users': 1, '_id': 0})
        if query:
            mentions = ''.join(['<a href="tg://user?id={}">{}</a> '.format(user["uid"], user["fname"]) for user in query['users']])
            text = query['desc'] + "\n" + mentions
            client.send_message(message.chat.id, text, parse_mode="html")

        else:
            help_call(client, chat_id)


#######################################################
#                 MEGACALL
#######################################################
@app.on_message(Filters.command(["megacall", "megacall@uborzbot"]))
def megacall(client, message):
    print("megacall")
    chat_id = message.chat.id
    try:
        participants = app.get_chat_members(chat_id, offset=0, limit=200)
        users = [(user['user']['id'], user['user']['first_name']) for user in participants['chat_members'] if
                 user['user']['is_bot'] is False]
        print(users)
        mentions = ''.join(['<a href="tg://user?id={}">{}</a> '.format(user[0], user[1]) for user in users])
        text = "FUCKING MEGACALL!!!\n" + mentions
        client.send_message(message.chat.id, text, parse_mode="html")
    except ValueError:
        client.send_message(message.chat.id, 'Megacall only works in groups!', parse_mode="html")


#######################################################
#       LA MALDICIÓN DEL 'CALLA QUE ME LEVANTO'
#######################################################
@app.on_message(Filters.command(["calla", "calla@uborzbot", "stfu", "stfu@uborzbot"]))
def calla(client, message):
    chat_id = message.chat.id
    try:
        # message.reply("reply :)", quote=True)
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            if user['is_bot']:
                client.send_message(message.chat.id, 'No le hagas /calla a un bot, cabrón.', parse_mode="html")
            else:
                try:
                    r = doomed.find_one({"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
                    if r:
                        text = '<a href="tg://user?id={}">{}</a> '.format(user['id'], user['first_name'])
                        text = text + " ya ha sido maldito recientemente... dale un fucking break, ok?"
                    else:
                        date_first_message = datetime.utcfromtimestamp(message.date)
                        date_liberation = date_first_message + timedelta(minutes=10)
                        date_reset = date_first_message + timedelta(hours=3)
                        doomed.insert_one({"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id,
                                           "ts_doom": date_first_message, "ts_lib": date_liberation,
                                           "ts_reset": date_reset})
                        text = '<a href="tg://user?id={}">{}</a> '.format(user['id'], user['first_name'])
                        text = text + " is DOOMED now!"
                    client.send_message(message.chat.id, text, parse_mode="html")
                except Exception as e:
                    print(e)
        else:
            client.send_message(message.chat.id, 'Usa /calla en reply a un mensaje.', parse_mode="html")
    except ValueError as e:
        print(e)
        # client.send_message(message.chat.id, 'ValueError! /megacall sólo funciona en grupos.', parse_mode="html")


# TODO Revisar esto, no lee todos los mensajes...
@app.on_message(~Filters.bot)
def doom(client, message):
    # print("doom")
    time_now = datetime.utcnow()
    # print(message)
    user = message.from_user
    chat_id = message.chat.id
    r = doomed.find_one({"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
    if r and time_now >= r['ts_reset']:
        doomed.delete_one({"uid": user['id'], "first_name": user['first_name'], "chat_id": chat_id})
    elif r and time_now <= r['ts_lib']:
        # print("AHORA", time_now)
        # print("TIME LIB", r['ts_lib'])

        message_random = random.randint(1, 6)
        if message_random >= 6:
            message.reply("QUE ME LEVANTO!", quote=True)
        elif message_random >= 4:
            message.reply("CALLAAAAAAAAAA!!", quote=True)
        else:
            message.reply("CALLA!", quote=True)
    # elif r:
    #     # print("AHORA PYTHON", time_now)
    #     # print("TIME LIBERA", r['ts_lib'])
    #     # print("TIME RESET", r['ts_reset'])
    #     pass
    else:
        # print("AHORA", time_now)
        pass


# ToDO: add members to groups (admins, or users?)
#######################################################
#                  EN DESARROLLO
#######################################################

def add_user(uid, nick, collection):
    new_user = {'uid': uid, 'nick': nick}
    found = False
    users = db[collection].find()
    for user in users:
        if user['uid'] == uid:
            found = True
            break
    if not found:
        db[collection].insert_one(new_user)
        print(new_user, 'added to ' + collection[:4])
    else:
        print(new_user, 'already in the database')


def rm_user(uid, collection):
    found = False
    users = db[collection].find()
    for user in users:
        if user['uid'] == uid:
            found = True
            break
    if found:
        db[collection].delete_many({'uid': uid})

# def add_to_group(bot, update):
#     # params = update.message.text.split()
#
#     # if len(params) <= 2:
#     #     helpadd(bot, update)
#     #
#     # elif len(params) >= 3:
#     #     nombre = params[1]
#     #     prov = params[2:]
#     print("HOLA ADD")
#     entera=update.message.parse_entities()
#     print(entera)
#     ents=update.message.entities
#     print(ents)
#     for ent in ents:
#         print(ent, entera[ent])
#
#     print(bot.getChatMember(update.message.chat_id, "@uborzz"))
#
#     # print("join")
#     # fname = update.message.from_user.first_name
#     # uid = update.message.from_user.id
#     # user = {'uid': uid, 'fname': fname}
#     # try:
#     #     print(nombre, update.message.chat_id)
#     #     q = db.calls.find_one_and_update({'nombre': nombre, 'group': update.message.chat_id},
#     #                              {"$addToSet": {'users': user}})
#     #     print(q)
#     # except:
#     #     print("Nope")
#
#
# def helpadd(bot,update):
#     bot.send_message(chat_id=update.message.chat_id, text="/insert <nombre> <@miembros>"
#                                                           "\nNecesario usar un call creado."
#                                                           "\nNecesario mencionar miembros (@)."
#                                                           "\nLos miembros deben ser parte del grupo.")


from telegram.ext import CommandHandler
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('helproll', help_roll))
dispatcher.add_handler(CommandHandler('calls', lista))
dispatcher.add_handler(CommandHandler('flip', flip))
dispatcher.add_handler(CommandHandler('roll', roll))
dispatcher.add_handler(CommandHandler('random', roll))
updater.start_polling()
app.run()
# updater.idle()
