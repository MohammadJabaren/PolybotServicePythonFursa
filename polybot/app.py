import flask
from flask import request
import os
from polybot.bot import ImageProcessingBot
import logging
from loguru import logger

TYPE_ENV = os.environ['TYPE_ENV']

app = flask.Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

'''BOT_APP_URL = os.environ['BOT_APP_URL']
'''


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_BOT_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    # Extract headers
    real_ip = request.headers.get('X-Real-IP')
    forwarded_for = request.headers.get('X-Forwarded-For')
    host = request.headers.get('Host')

    # Log header info
    logging.info(f"Received headers - X-Real-IP: {real_ip}, X-Forwarded-For: {forwarded_for}, Host: {host}")
    logging.info(f"Received message: {req}")
    bot.handle_message(req['message'])
    return 'Ok'

#test
if __name__ == "__main__":
    logger.info(f'App Enviroment is : \n\n{TYPE_ENV}')
    if TYPE_ENV == "dev":
        bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, "https://jabaren.fursa.click")
    else:
        bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, "https://jabarenprod.fursa.click")

    app.run(host='0.0.0.0', port=8443)
