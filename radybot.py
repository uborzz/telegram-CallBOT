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
#                GENERAL METHODS
#######################################################
def help(bot, update):
    print(update.message)
    bot.send_message(chat_id=update.message.chat_id, text="CallBOT v4.0! Commands: "
                                                          "\n/call - /create - /delete"
                                                          "\n/list - /join - /leave"
                                                          "\n/megacall"
                                                          "\n/calla - /stfu"
                                                          "\n/helproll : help for /roll")


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


#######################################################
#                  PORTANDO
#######################################################

@app.on_message(Filters.command(["create", "create@uborzbot"]))
def create(bot, update):
    params = update.message.text.split()

    if len(params) == 1:
        helpcreate(bot, update)

    elif len(params) >= 2:
        q = db.calls.find_one({'group': update.message.chat_id,
                               'nombre': params[1]})
        print(q)
        if not q:
            if len(params) >= 3:
                prov = params[2:]
                print(prov)
                desc = ' '.join(prov)
                print(desc)
            else:
                desc = "CALL: {}!".format(params[1].upper())
            fields = {'group': update.message.chat_id,
                      'nombre': params[1],
                      'desc': desc,
                      'owner': update.message.from_user.id,
                      'users': list()}
            print(fields)
            db.calls.insert_one(fields)
            print("created")
        else:
            print("already created")


def modify(bot, update):
    params = update.message.text.split()

    if len(params) >= 3:
        prov = params[2:]
        desc = ' '.join(prov)
        q = db.calls.find_one_and_update({'nombre': params[1], 'group': update.message.chat_id},
                                         {'$set': {'desc': desc}})
        if not q:
            bot.send_message(chat_id=update.message.chat_id, text="El canal no está creado"
                                                                  "\n/create <nombre> <(opcional)desc>.")
        else:
            print("HOLA")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Especifica texto del call"
                                                              "\n/modify <nombre> <text>.")


def join(bot, update):
    params = update.message.text.split()

    if len(params) == 1:
        helpjoin(bot, update)

    elif len(params) == 2:
        nombre = params[1]
        print("join")
        fname = update.message.from_user.first_name
        uid = update.message.from_user.id
        user = {'uid': uid, 'fname': fname}
        try:
            print(nombre, update.message.chat_id)
            q = db.calls.find_one_and_update({'nombre': nombre, 'group': update.message.chat_id},
                                             {"$addToSet": {'users': user}})
            if not q:
                helpjoin(bot, update)

        except:
            print("Nope")


# ToDO: add members to groups (admins, or users?)
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


def leave(bot, update):
    params = update.message.text.split()

    if len(params) == 1:
        helpleave(bot, update)

    elif len(params) == 2:
        nombre = params[1]
        print("leave")
        fname = update.message.from_user.first_name
        uid = update.message.from_user.id
        user = {'uid': uid, 'fname': fname}
        try:
            print(nombre, update.message.chat_id)
            q = db.calls.find_one_and_update({'nombre': nombre, 'group': update.message.chat_id},
                                             {"$pull": {'users': user}})
            print(q)
        except:
            print("Nope")


def delete(bot, update):
    params = update.message.text.split()
    caller = update.message.from_user.id
    admins = bot.getChatAdministrators(update.message.chat_id)
    grupo = update.message.chat_id

    if len(params) == 1:
        helpdelete(bot, update)

    elif len(params) == 2:
        nombre = params[1]
        creador = db.calls.find_one({'nombre': nombre, 'group': grupo}, {'owner': 1, '_id': 0})['owner']
        admins = [ele['user']['id'] for ele in admins]
        admins.append(creador)
        print(admins)

        if caller in admins:
            print("delete", nombre)
            try:
                q = db.calls.find_one_and_delete({'nombre': nombre, 'group': grupo})
                print(q)
            except:
                print("Nope")
        else:
            helpdelete(bot, update)


def call(bot, update):
    params = update.message.text.split()

    if len(params) == 1:
        helpcall(bot, update)

    elif len(params) >= 2:
        nombre = params[1]
        group = update.message.chat_id
        text = db.calls.find_one({'group': group,
                                  'nombre': nombre}, {'desc': 1, '_id': 0})
        if text:
            text = text['desc']
            print('llamando', nombre, text)
            ret = cast_call(nombre, text, group)
            print(ret)

        else:
            helpcall(bot, update)


def helpcall(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /call <nombre>"
                                                          "\nNecesario usar un call creado."
                                                          "\n/list o /calls para ver los calls."
                                                          "\n/megacall para llamada a todos.")


def cast_call(nombre, desc, chatid):
    text = desc + '\n' + mentions(nombre, chatid)
    vmid = '/sendmessage?chat_id=' + str(chatid) + '&text='
    url = rootpwr + creds.token + vmid + text + vend
    print(url)
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def mentions(nombre, chatid):
    print('mentions...')
    users = db.calls.find_one({'nombre': nombre, 'group': chatid}, {'users': 1, '_id': 0})
    users = users['users']
    if users:
        result = ''.join(['<a href="mention:{}">{}</a> '.format(user['uid'], user['fname']) for user in users])
    else:
        result = 'Grupo vacío... shit!'

    return result


@app.on_message(Filters.command(["list", "list@uborzbot"]))
def lista(client, message):
    group = message.chat.id
    q = db.calls.find({'group': group}, {'nombre': 1, 'desc': 1, 'owner': 1, '_id': 0})
    info = ['''\n{}: "{}"'''.format(ele['nombre'], ele['desc']) for ele in q]
    text = ''.join(info)

    if text:
        client.send_message(chat_id=group, text="Calls de este grupo:{}"
                                                "\n/create para nuevo call"
                                                "\n/modify para editar texto".format(text))
    else:
        client.send_message(chat_id=group, text="No hay Calls en este grupo."
                                             "\n/create para crear nuevo call."
                                             "\n/help para ver comandos.")


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
        client.send_message(message.chat.id, 'ValueError! megacall sólo funciona en grupos.', parse_mode="html")


@app.on_message(Filters.command(["calla", "calla@uborzbot", "stfu", "stfu@uborzbot"]))
def calla(client, message):
    print("calla")
    # print(message)
    chat_id = message.chat.id
    # print(type(message))
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


def helpcreate(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="/create <nombre> <(opcional)descripcion>")


def helpjoin(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /join <nombre>")


def helpleave(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /leave <nombre>")


def helpdelete(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /delete <nombre>"
                                                          "\nNecesario ser admin o creador del call.")


def send_call(calls, text, chatid_str):
    text = text + '\n' + comp_text(calls + chatid_str)
    vmid = '/sendmessage?chat_id=' + chatid_str + '&text='
    url = rootpwr + creds.token + vmid + text + vend
    print(url)
    # calls = '<a href="mention:{}">{}</a> '.format(str(uid), fname)
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content
    # print()


def comp_text(collection):
    result = ''
    users = db[collection].find()
    for user in users:
        user['uid']
        result += '<a href="mention:{}">{}</a> '.format(user['uid'], user['nick'])
    return result


from telegram.ext import CommandHandler
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('helproll', help_roll))
dispatcher.add_handler(CommandHandler('create', create))
dispatcher.add_handler(CommandHandler('join', join))
dispatcher.add_handler(CommandHandler('leave', leave))
dispatcher.add_handler(CommandHandler('delete', delete))
dispatcher.add_handler(CommandHandler('call', call))
dispatcher.add_handler(CommandHandler('modify', modify))
dispatcher.add_handler(CommandHandler('calls', lista))
dispatcher.add_handler(CommandHandler('flip', flip))
dispatcher.add_handler(CommandHandler('roll', roll))
dispatcher.add_handler(CommandHandler('random', roll))
updater.start_polling()
app.run()
# updater.idle()
