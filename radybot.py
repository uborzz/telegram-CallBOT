# -*- coding: utf-8 -*-

from telegram.ext import Updater
import json
import requests
import pymongo
import random

client = pymongo.MongoClient('localhost', 27017)
db = client.callsdb

rootpwr = 'https://api.pwrtelegram.xyz/bot'
vend = '&parse_mode=HTML&mtproto=true'

with open('token.txt') as f:
    TOKEN = f.read()

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
                    
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="CallBot Version Dofitos. /help para aiuda! ")
    
def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="CallBOT lista de comandos:"
                                                          "\n/cs : Call CS."
                                                          "\n/hots ó /hos : Call HotS."
                                                          "\n/joincs y /leavecs "
                                                          "\n/joinhots y /leavehots "
                                                          "\n/flip : Coin flip")
    
def flip(bot, update):
    if random.randint(0,2):
        result = "Headz!"
    else:
        result = "Tailz!"
    return_text = "Coin flip: " + result
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
    url = rootpwr + TOKEN + vmid + text + vend
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
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

start_handler = CommandHandler('help', help)
dispatcher.add_handler(start_handler)

start_handler = CommandHandler('help', flip)
dispatcher.add_handler(start_handler)

hots_handler = CommandHandler('hots', hots)
dispatcher.add_handler(hots_handler)
hots_handler = CommandHandler('hos', hots)
dispatcher.add_handler(hots_handler)

hots_handler = CommandHandler('cs', cs)
dispatcher.add_handler(hots_handler)

hots_handler = CommandHandler('joincs', joincs)
dispatcher.add_handler(hots_handler)
hots_handler = CommandHandler('joinhots', joinhots)
dispatcher.add_handler(hots_handler)
hots_handler = CommandHandler('leavecs', leavecs)
dispatcher.add_handler(hots_handler)
hots_handler = CommandHandler('leavehots', leavehots)
dispatcher.add_handler(hots_handler)

updater.start_polling()
updater.idle()
