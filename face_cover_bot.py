# @FaceCoverBot

import telepot
from pprint import pprint


TELEGRAM_BOT_TOKEN = open('bot_token.txt').read()


bot = telepot.Bot(TELEGRAM_BOT_TOKEN)
print bot.getMe()