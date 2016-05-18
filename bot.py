# -*- coding: utf-8 -*-

# @FaceCoverBot

from __future__ import unicode_literals

import sys
import time
import telepot
import logging

from pprint import pprint
from config import *
from db import *
from messages import *


TELEGRAM_BOT_TOKEN = open('bot_token.txt').read()
BOT_HELP = open('bot_help.txt').read()

bot = telepot.Bot(TELEGRAM_BOT_TOKEN)
log = logging.getLogger('bot').debug


def handle_message(message):
    message_type, chat_type, chat_id = telepot.glance(message)
    log('receive message: message_type=%s chat_type=%s chat_id=%s', message_type, chat_type, chat_id)

    first_name = message['chat']['first_name']
    last_name = message['chat']['last_name']
    username = message['chat']['username']

    user_id = get_user_id(first_name, last_name)

    if message_type == 'photo':
        photo = message['photo'][-1]

        user_dir = os.path.join(USER_IMAGES_DIR, '%s_%s' % (first_name, last_name))
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)

        photo_path = os.path.join(user_dir, photo['file_id'])
        if not os.path.exists(photo_path):
            bot.download_file(photo['file_id'], photo_path)

        create_photo(user_id, photo_path, chat_id, photo['width'], photo['height'], photo['file_id'])



        log('create photo: photo_path=%s', photo_path)

    # handle commands
    if 'text' in message and message['text'].startswith('/'):
        command, param = message['text'].split(' ')
        command = command.strip().lower()
        param = param.strip().lower()

        if command == '/help':
            bot.sendMessage(chat_id, BOT_HELP)
            log('print help')

        elif command == '/start':
            bot.sendMessage(chat_id, BOT_HELP)
            create_user(first_name, last_name, username)

            log('create user: first_name=%s last_name=%s username=%s', first_name, last_name, username)

        elif command == '/new':
            session_name = param
            create_session(session_name, chat_id, user_id)
            bot.sendMessage(chat_id, COMMAND_SESSION_NEW % session_name)

            log('new session: name=%s chat_id=%s', session_name, chat_id)

        elif command == '/use':
            try:
                session_id = int(param)
            except ValueError:
                session_id = get_session_by_name(param)

            use_session(user_id, session_id)
            bot.sendMessage(chat_id, COMMAND_SESSION_CURRENT % session_id)

            log('use session: user_id=%s session_id=%s', user_id, session_id)

        elif command == '/list':
            session_list = get_session_list(user_id)
            sessions_text = '\n'.join(['%s [%d]' % (s.name, s.id) for s in session_list])
            bot.sendMessage(chat_id, sessions_text)

            log('session list: user_id=%s', user_id)

        elif command == '/close':
            try:
                session_id = int(param)
            except ValueError:
                session_id = get_session_by_name(param)

            close_session(session_id)
            bot.sendMessage(chat_id, COMMAND_SESSION_CLOSE % session_id)

            log('session close: session_id=%s', session_id)

        else:
            log('command unknown: message=%s', message)
            bot.sendMessage(chat_id, COMMAND_UNKNOWN)

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
