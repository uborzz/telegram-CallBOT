# -*- coding: utf-8 -*-
import telegram
from telegram.ext import Updater
import json
import requests
import pymongo

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
                                                          "\n/joinhots y /leavehots ")
    
def hots(bot, update):
    send_call('hots', 'CALL: HEROES OF THE STORM!', str(update.message.chat_id))
    #bot.send_message(chat_id=update.message.chat_id, text="OLD!!! CALL: HEROES OF THE STORM! \n + @gtorres @druscaelan @uborzz \n A partir cabezas!")

def cs(bot, update):
    send_call('csgo', 'CALL: COUNTER STRIKE!',str(update.message.chat_id))


def add_user(uid, nick, call):
    new_user = {'uid': uid, 'nick': nick}
    found = False
    if call == 'csgo':
        users = db.csgo.find()
    elif call == 'hots':
        users = db.hots.find()
    for user in users:
        if user['uid'] == uid:
            found = True
            break
    if not found:
        if call == 'csgo':
            db.csgo.insert_one(new_user)
            print(new_user, 'added to csgo')
        elif call == 'hots':
            db.hots.insert_one(new_user)
            print(new_user, 'added to hots')
    else:
        print(new_user, 'already inside')

def rm_user(uid, nick, call):
    found = False
    if call == 'csgo':
        users = db.csgo.find()
    elif call == 'hots':
        users = db.hots.find()
    for user in users:
        if user['uid'] == uid:
            found = True
            break
    if found:
        if call == 'csgo':
            db.csgo.delete_many({'uid':uid})
        elif call == 'hots':
            db.hots.delete_many({'uid':uid})

def joincs(bot, update):
    chatid = update.message.chat_id
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    #print('join', chatid, fname)
    add_user(uid, fname, 'csgo')
    
def leavecs(bot, update):
    chatid = update.message.chat_id
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    #print('leave', chatid, fname)
    rm_user(uid, fname, 'csgo')
    
def joinhots(bot, update):
    chatid = update.message.chat_id
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    #print('join', chatid, fname)
    add_user(uid, fname, 'hots')
    
def leavehots(bot, update):
    chatid = update.message.chat_id
    fname = update.message.from_user.first_name
    uid = update.message.from_user.id
    #print('leave', chatid, fname)
    rm_user(uid, fname, 'hots')

def send_call(calls, text, ch):
    text = text + '\n' + comp_text(calls)
    vmid = '/sendmessage?chat_id=' + ch + '&text='
    url = rootpwr + TOKEN + vmid + text + vend
    #print(url)
    # calls = '<a href="mention:{}">{}</a> '.format(str(uid), fname)
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content
    # print()

def comp_text(calls):
    result = ''
    if calls == 'csgo':
        users = db.csgo.find()
        for user in users:
            user['uid']
            result += '<a href="mention:{}">{}</a> '.format(user['uid'], user['nick'])
    elif calls == 'hots':
        users = db.hots.find()
        for user in users:
            user['uid']
            result += '<a href="mention:{}">{}</a> '.format(user['uid'], user['nick'])
    return result
       
from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

start_handler = CommandHandler('help', help)
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
