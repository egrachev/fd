# @FaceCoverBot

import sys
import time
import telepot

from pprint import pprint


TELEGRAM_BOT_TOKEN = open('bot_token.txt').read()


bot = telepot.Bot(TELEGRAM_BOT_TOKEN)


def handle(message):
    content_type, chat_type, chat_id = telepot.glance(message)
    # bot.download_file(u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABEn8PaFUzRhBGHQAAgI', 'save/to/path')
    # bot.sendMessage(999999999, 'Good morning!')

    # show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
    # bot.sendMessage(999999999, 'This is a custom keyboard', reply_markup=show_keyboard)

    # f = open('zzzzzzzz.jpg', 'rb')  # some file on local disk
    # response = bot.sendPhoto(999999999, f)

    print (content_type, chat_type, chat_id)




bot.message_loop(handle)
print ('Listening ...')


while 1:
    time.sleep(10)
