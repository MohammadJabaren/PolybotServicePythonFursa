import flask
from flask import request
import os
from polybot.bot import ImageProcessingBot
from loguru import logger
app = flask.Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BOT_APP_URL = os.environ['BOT_APP_URL']
TYPE_ENV = os.environ['TYPE_ENV']



@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_BOT_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    logger.info(f'App Enviroment is : \n\n{TYPE_ENV}')
    if TYPE_ENV == "dev":
        bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, "https://jabaren.fursa.click")
    else:
        bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, "https://jabarenprod.fursa.click")
    app.run(host='0.0.0.0', port=8443)
