# -*- coding: utf-8 -*-

from telegram.ext import Updater
import json
import requests
import pymongo
import random
import creds

# client = pymongo.MongoClient(creds.mongo_host, creds.mongo_port)
# db = client.callsdb

rootpwr = 'https://api.telegram.org/bot'
vend = '&parse_mode=HTML&mtproto=true'

# pyrogram
from pyrogram import Client, Filters
from pyrogram.api import functions, types

app = Client(creds.token,
    api_id=creds.id,
    api_hash=creds.hash)


updater = Updater(token=creds.token)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="CallBOT v3.0! /help para aiuda! ")


def help(bot, update):
    print(update.message)
    bot.send_message(chat_id=update.message.chat_id, text="CallBOT v3.0! Comandos: "
                                                          "\n Disabled atm..."
                                                          "\n/call - /create - /delete"
                                                          "\n/list - /join - /leave"
                                                          "\n Already ported:"
                                                          "\n/megacall"    
                                                          "\n/helproll : ayuda de /roll"
                                                          "\n/helpold : old commands")

def helpold(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="CallBOT old v.Dofitos:"
                                                          "\n/cs : Call CS."
                                                          "\n/hots ó /hos : Call HotS."
                                                          "\n/joincs y /leavecs "
                                                          "\n/joinhots y /leavehots ")

def helproll(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Roll: utiliza numeros enteros: "
                                                           "\n/roll - random entre 0 y 100"
                                                           "\n/roll <max> - entre 0 y <max>" 
                                                           "\n/roll <min> <max> - adivina... "
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
            print(result)
        user = update.message.from_user.first_name + " " + update.message.from_user.last_name
        user = user.rstrip()
        ttr = "Random en [{}, {}]".format(values[0], values[1]) + \
              "\nResult ({}): {}!".format(user, result)
        print(ttr)
        bot.send_message(chat_id=update.message.chat_id, text=ttr)
    except:
        helproll(bot, update)


def flip(bot, update):
    if random.randint(0,1):
        result = "Headz!"
    else:
        result = "Tailz!"
    return_text = "Coin flip: " + result
    print(return_text)
    bot.send_message(chat_id=update.message.chat_id, text=return_text)


def hots(bot, update):
    print('hots llamado')
    ret = send_call('hots', 'CALL: HEROES OF THE STORM!', str(update.message.chat_id))
    print('hots explicando')
    print(ret)
    #bot.send_message(chat_id=update.message.chat_id, text="OLD!!! CALL: HEROES OF THE STORM! \n + @gtorres @druscaelan @uborzz \n A partir cabezas!")


def cs(bot, update):
    print('cs llamado')
    send_call('csgo', 'CALL: COUNTER STRIKE!',str(update.message.chat_id))
    print('cs explicando')


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
        print(new_user, 'added to ' + colletion[:4])
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
        db[collection].delete_many({'uid':uid})


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
            print(q)
        except:
            print("Nope")



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


def call(bot,update):
    params = update.message.text.split()

    if len(params) == 1:
        helpcall(bot, update)

    elif len(params) >= 2:
        nombre = params[1]
        group = update.message.chat_id
        text = db.calls.find_one({'group': group,
                                  'nombre': nombre}, {'desc':1, '_id':0})
        if text:
            text = text['desc']
            print('llamando', nombre, text)
            ret = cast_call(nombre, text, group)
            print(ret)

        else:
            helpcall(bot, update)

def helpcall(bot,update):
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

def lista(bot, update):
    group = update.message.chat_id
    q = db.calls.find({'group': group}, {'nombre': 1, 'desc': 1, 'owner': 1, '_id': 0})
    info = ['''\n{}: "{}"'''.format(ele['nombre'], ele['desc']) for ele in q]

    text = ''.join(info)
    if text:
        bot.send_message(chat_id=group, text="Calls de este grupo:" + text
                         + "\n/create para nuevo call"
                           "\n/modify para editar texto")
    else:
        bot.send_message(chat_id=group, text="No hay Calls en este grupo."
                                             "\n/create para crear nuevo call."
                                             "\n/help para ver comandos.")


@app.on_message(Filters.command(["megacall", "megacall@uborzbot"]))
def megacall(client, message):
    print("megacall")
    chat_id = message.chat.id
    participants = app.get_chat_members(chat_id, offset=0, limit = 200)

    users = [(user['user']['id'], user['user']['first_name']) for user in participants['chat_members'] if user['user']['is_bot'] == False]
    print(users)

    mentions = ''.join(['<a href="tg://user?id={}">{}</a> '.format(user[0], user[1]) for user in users])
    text = "FUCKING MEGACALL!!!\n" + mentions
    client.send_message(message.chat.id, text, parse_mode="html")

def helpcreate(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="/create <nombre> <(opcional)descripcion>")

def helpjoin(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /join <nombre>")

def helpleave(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /leave <nombre>")

def helpdelete(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Cómo se usa... /delete <nombre>"
                                                          "\nNecesario ser admin o creador del call.")

def joincs(bot, update):
    collection = 'csgo' + str(update.message.chat_id)
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    add_user(uid, fname, collection)

def leavecs(bot, update):
    collection = 'csgo' + str(update.message.chat_id)
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    rm_user(uid, collection)

def joinhots(bot, update):
    collection = 'hots' + str(update.message.chat_id)
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    add_user(uid, fname, collection)

def leavehots(bot, update):
    collection = 'hots' + str(update.message.chat_id)
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    rm_user(uid, collection)

def send_call(calls, text, chatid_str):
    text = text + '\n' + comp_text(calls+chatid_str)
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
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('helproll', helproll))
dispatcher.add_handler(CommandHandler('helpold', helpold))
dispatcher.add_handler(CommandHandler('create', create))
dispatcher.add_handler(CommandHandler('join', join))
dispatcher.add_handler(CommandHandler('leave', leave))
dispatcher.add_handler(CommandHandler('delete', delete))
dispatcher.add_handler(CommandHandler('call', call))
dispatcher.add_handler(CommandHandler('modify', modify))
dispatcher.add_handler(CommandHandler('list', lista))
dispatcher.add_handler(CommandHandler('calls', lista))
dispatcher.add_handler(CommandHandler('flip', flip))
dispatcher.add_handler(CommandHandler('roll', roll))
dispatcher.add_handler(CommandHandler('random', roll))
dispatcher.add_handler(CommandHandler('hots', hots))
dispatcher.add_handler(CommandHandler('hos', hots))
dispatcher.add_handler(CommandHandler('cs', cs))
dispatcher.add_handler(CommandHandler('joincs', joincs))
dispatcher.add_handler(CommandHandler('joinhots', joinhots))
dispatcher.add_handler(CommandHandler('leavecs', leavecs))
dispatcher.add_handler(CommandHandler('leavehots', leavehots))
updater.start_polling()
app.run()
# updater.idle()