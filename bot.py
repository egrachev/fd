# -*- coding: utf-8 -*-

# @FaceCoverBot

from __future__ import unicode_literals

import sys
import time
import telepot
import logging
import cv2

from pprint import pprint
from config import *
from db import *
from messages import *
from detect import make_overlay


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

    # make user images dir
    user_dir = os.path.join(USER_IMAGES_DIR, '%s_%s' % (first_name, last_name))
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    # make draw features dir
    user_dir_features = os.path.join(user_dir, USER_FEATURES_DIR_NAME)
    if not os.path.exists(user_dir_features):
        os.mkdir(user_dir_features)

    # user upload photo
    if message_type == 'photo':
        # take big photo
        photo = message['photo'][-1]

        # create photo
        if not photo_exists(photo['file_id']):
            photo_path = os.path.join(user_dir, photo['file_id'])

            if not os.path.exists(photo_path):
                bot.download_file(photo['file_id'], photo_path)

            create_photo(photo_path, photo['width'], photo['height'], photo['file_id'])
            log('create photo: photo_path=%s', photo_path)

        photo_id = get_current_photo_id()
        file_origin = get_file_origin(photo_id)
        image = cv2.imread(file_origin)

        # draw features on uploaded photo
        features_list = [SELECT_FEATURE_TITLE]
        for f in get_features():
            cv2.rectangle(image, (f.x1, f.y1), (f.x2, f.y2), f.get_color(), thickness=2)
            features_list.append('/select %s (%s)' % (f.id, f.type.name))

            log('draw rectangle: x=%s y=%s width=%s height=%s', f.x1, f.y1, f.width, f.height)

        bot.sendMessage(chat_id, '\n'.join(features_list))

        # save draw features
        photo_rects = os.path.join(user_dir_features, '%s_all.jpg' % photo['file_id'])
        cv2.imwrite(photo_rects, image)

        # send result
        with open(photo_rects) as f:
            bot.sendPhoto(chat_id, f)

    # handle commands
    if 'text' in message and message['text'].startswith('/'):
        parts = message['text'].split(' ')
        command = ''
        param1 = ''
        param2 = ''

        if len(parts) == 1:
            command = parts[0]

        if len(parts) == 2:
            command, param1 = parts

        if len(parts) == 3:
            command, param1, param2 = parts

        command = command.strip().lower()
        param1 = param1.strip().lower()
        param2 = param2.strip().lower()

        if command == '/help':
            bot.sendMessage(chat_id, BOT_HELP)
            log('print help')

        elif command == '/start':
            bot.sendMessage(chat_id, BOT_HELP)
            create_user(first_name, last_name, username)

            log('create user: first_name=%s last_name=%s username=%s', first_name, last_name, username)

        elif command == '/new':
            session_name = param1
            create_session(session_name, chat_id, user_id)
            bot.sendMessage(chat_id, COMMAND_SESSION_NEW % session_name)
            bot.sendMessage(chat_id, COMMAND_SESSION_SEND_PHOTO)

            log('new session: name=%s chat_id=%s', session_name, chat_id)

        elif command == '/use':
            try:
                session_id = int(param1)
            except ValueError:
                session_id = get_session_by_name(param1)

            use_session(user_id, session_id)
            bot.sendMessage(chat_id, COMMAND_SESSION_CURRENT % (get_session_name(session_id), session_id))

            photo_id = get_current_photo_id()
            if not photo_id:
                bot.sendMessage(chat_id, COMMAND_SESSION_SEND_PHOTO)

            log('use session: user_id=%s session_id=%s', user_id, session_id)

        elif command == '/list':
            session_list = get_session_list(user_id)
            sessions_text = '\n'.join(['%s [%d]' % (s.name, s.id) for s in session_list])
            bot.sendMessage(chat_id, COMMAND_SESSION_LIST % sessions_text)

            log('session list: user_id=%s', user_id)

        elif command == '/select':
            feature_id = int(param1)
            feature = get_feature(feature_id)

            photo_id = get_current_photo_id()
            file_origin = get_file_origin(photo_id)
            image = cv2.imread(file_origin)

            cv2.rectangle(
                image,
                (feature.x1, feature.y1),
                (feature.x2, feature.y2),
                feature.get_color(),
                thickness=2
            )

            photo_rect = os.path.join(user_dir_features, '%s_%s_%s.jpg' % (photo_id, feature_id, feature.type.name))
            cv2.imwrite(photo_rect, image)

            # send result
            with open(photo_rect) as f:
                bot.sendPhoto(chat_id, f)

        elif command == '/overlay_show':
            pass

        elif command == '/overlay_list':
            response = []
            for overlay in get_overlays():
                response.append('%s %s' % (overlay.name, overlay.type.name))

            overlay_text = '\n'.join(response)
            bot.sendMessage(chat_id, overlay_text)

        elif command == '/overlay':
            feature_id = int(param1)
            feature = get_feature(feature_id)

            overlay = get_overlay_by_name(param2)
            overlay_add(feature_id, overlay.id)

            photo_id = get_current_photo_id()
            image_path = get_file_origin(photo_id)
            image = make_overlay(image_path, overlay.image,
                                 feature.x1, feature.y1, feature.width, feature.height)

            photo_overlay = os.path.join(user_dir_features, '%s_%s_%s_%s.jpg' % (
                photo_id, feature_id, feature.type.name, param2))
            cv2.imwrite(photo_overlay, image)

            with open(photo_overlay) as f:
                bot.sendPhoto(chat_id, f)

        elif command == '/show':
            pass

        elif command == '/close':
            try:
                session_id = int(param1)
            except ValueError:
                session_id = get_session_by_name(param1)

            close_session(session_id)
            bot.sendMessage(chat_id, COMMAND_SESSION_CLOSE % session_id)

            log('session close: session_id=%s', session_id)

        else:
            log('command unknown: message=%s', message)
            bot.sendMessage(chat_id, COMMAND_UNKNOWN)

    # show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
    # bot.sendMessage(999999999, 'This is a custom keyboard', reply_markup=show_keyboard)



    # keyboard handle
    # flavor = telepot.flavor(msg)
    #
    # if flavor == 'chat':
    #     print ('Chat message')
    # elif flavor == 'callback_query':
    #     print ('Callback query')






log('start bot')
bot.message_loop(handle_message, run_forever=True)
