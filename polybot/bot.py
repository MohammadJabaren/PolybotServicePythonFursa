import telebot
from loguru import logger
import os
from telebot.types import InputFile
from polybot.img_proc import Img
import time

class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')
        self.media_group_cache = {}

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"] )


class ImageProcessingBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        try:
            chat_id = msg['chat']['id']
            caption = msg.get("caption", "").strip().lower()
            media_group_id = msg.get('media_group_id')

            if media_group_id:
                if media_group_id not in self.media_group_cache:
                    self.media_group_cache[media_group_id] = []
                self.media_group_cache[media_group_id].append(msg)

                if len(self.media_group_cache[media_group_id]) < 2:
                    return  # wait for second image

                msg1, msg2 = self.media_group_cache[media_group_id][:2]

                caption1 = msg1.get("caption", "").strip().lower()
                caption2 = msg2.get("caption", "").strip().lower()
                caption = caption1 or caption2

                if caption not in ["concat horizontal", "concat vertical"]:
                    self.send_text(chat_id, "Please use a valid caption: 'concat horizontal' or 'concat vertical'.")
                    self.media_group_cache.pop(media_group_id, None)
                    return

                img_path_1 = self.download_user_photo(msg1)
                img_path_2 = self.download_user_photo(msg2)

                img1 = Img(img_path_1)
                img2 = Img(img_path_2)

                direction = 'horizontal' if caption == 'concat horizontal' else 'vertical'
                img1.concat(img2, direction=direction)
                result_path = img1.save_img()
                self.send_photo(chat_id, result_path)

                self.media_group_cache.pop(media_group_id, None)
                return

            if not self.is_current_msg_photo(msg):
                self.send_text(chat_id,
                               "Send a photo with one of these captions:\n"
                               "- blur\n- contour\n- rotate\n- segment\n- salt and pepper\n"
                               "- concat horizontal or concat vertical (send 2 photos as album)"
                               )
                return

            if caption.startswith('concat'):
                self.send_text(chat_id, "Please send two images as a media group (album) for concatenation.")
                return

            img_path = self.download_user_photo(msg)
            image = Img(img_path)

            if caption == 'blur':
                image.blur()
            elif caption == 'contour':
                image.contour()
            elif caption == 'rotate':
                image.rotate()
            elif caption == 'salt and pepper':
                image.salt_n_pepper()
            elif caption == 'segment':
                image.segment()
            else:
                self.send_text(chat_id, f"Unsupported filter: {caption}")
                return

            result_path = image.save_img()
            self.send_photo(chat_id, result_path)

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(msg['chat']['id'], "Something went wrong... please try again.")
