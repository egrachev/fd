# -*- coding: utf-8 -*-

# @FaceCoverBot

from __future__ import unicode_literals

import sys
import time
import telepot
import logging

from pprint import pprint
from config import *
from messages import *


TELEGRAM_BOT_TOKEN = open('bot_token.txt').read()
BOT_HELP = open('bot_help.txt').read()

bot = telepot.Bot(TELEGRAM_BOT_TOKEN)
log = logging.getLogger('bot').debug


def handle_message(message):
    message_type, chat_type, chat_id = telepot.glance(message)
    log('receive message: message_type=%s chat_type=%s chat_id=%s', message_type, chat_type, chat_id)

    command = message['text'].strip().lower()

    if command == '/help':
        bot.sendMessage(chat_id, BOT_HELP)
    elif command == '/start':
        bot.sendMessage(chat_id, BOT_HELP)
        # create user
    elif command == '/new':
        bot.sendMessage(chat_id, COMMAND_NEW_TEXT)
        # create session

    elif command == '/list':
        # list sessions
        pass

    elif command == '/end':
        # close session
        pass

    else:
        log('bad message: message=%s', message)
        bot.sendMessage(chat_id, 'Command not supported')


    # bot.download_file(u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABEn8PaFUzRhBGHQAAgI', 'save/to/path')
    # bot.sendMessage(999999999, 'Good morning!')

    # show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
    # bot.sendMessage(999999999, 'This is a custom keyboard', reply_markup=show_keyboard)

    # f = open('zzzzzzzz.jpg', 'rb')  # some file on local disk
    # response = bot.sendPhoto(999999999, f)

    # keyboard handle
    # flavor = telepot.flavor(msg)
    #
    # if flavor == 'chat':
    #     print ('Chat message')
    # elif flavor == 'callback_query':
    #     print ('Callback query')






log('start bot')
bot.message_loop(handle_message, run_forever=True)
