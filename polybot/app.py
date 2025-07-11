import flask
from flask import request,jsonify
import os
from polybot.bot import ImageProcessingBot
from dotenv import load_dotenv
app = flask.Flask(__name__)

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TYPE_ENV = os.getenv('TYPE_ENV')
STRORAGE_TYPE = os.getenv('STRORAGE_TYPE')




@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_BOT_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


@app.route("/notify", methods=["POST"])
def notify_user_with_image():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    chat_id = data.get("chat_id")
    if not chat_id:
        return jsonify({"error": "Missing chat_id"}), 400

    # Case 1: DynamoDB (UID provided, fetch and send image)
    if STRORAGE_TYPE == "dynamodb":
        uid = data.get("uid")
        success = bot.send_prediction_image(chat_id, uid)
        if success:
            return jsonify({"status": "sent"}), 200
        else:
            return jsonify({"error": "Failed to send image"}), 500

    # Case 2: SQLite (Labels provided)
    else:
        try:
            labels = data.get("labels")
            label_text = ", ".join(labels)
            bot.send_text(chat_id, f"Objects detected: {label_text}")
            return jsonify({"status": "labels sent"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to send labels: {e}"}), 500


if __name__ == "__main__":
    if TYPE_ENV == "dev":
        bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, "https://jabaren.dev.fursa.click")
    else:
        bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, "https://jabarenprod.fursa.click")
    app.run(host='0.0.0.0', port=8443)
