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
    def send_welcome_message(self, chat_id):
        self.send_text(chat_id,
                       "👋 Hello! I'm your image processing bot.\n\n"
                       "📷 Send me a photo with one of these captions to apply a filter:\n"
                       "- blur\n- contour\n- rotate\n- segment\n- salt and pepper\n- gamma correction\n- posterize\n- inverse\n\n"
                       "🖼️ To concatenate two images, send them as a media group (album) with one of these captions:\n"
                       "- concat horizontal\n- concat vertical"
                       "❓ If you need more details or assistance, feel free to type /help for further instructions!")

    def send_help_message(self, chat_id):
        help_text = (
            "Here's how to use the Image Processing Bot:\n\n"
            "- **/start**: Get a welcome message and instructions on available features.\n"
            "- **/help**: Show this help message with all available commands.\n\n"
            "For image processing, you can send a photo and add a caption like:\n"
            "- **blur**: Apply blur effect on the image.\n"
            "- **contour**: Apply contour effect on the image.\n"
            "- **rotate**: Rotate the image.\n"
            "- **segment**: Apply image segmentation.\n"
            "- **gamma correction**: Adjust the brightness of the image using gamma correction.\n"
            "- **inverse**: Invert the colors of the image.\n"
            "- **posterize**: Reduce the number of colors in the image for a stylized effect.\n"
            "- **salt and pepper**: Add salt-and-pepper noise to the image.\n\n"
            "You can also concatenate two images with captions like:\n"
            "- **concat horizontal**: Combine two images side by side.\n"
            "- **concat vertical**: Combine two images top to bottom.\n\n"
            "To concatenate images, send them as a media group (album) with the respective caption!"
        )
        self.send_text(chat_id, help_text)

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        try:
            chat_id = msg['chat']['id']
            caption = msg.get("caption", "").strip().lower()
            media_group_id = msg.get('media_group_id')

            if 'text' in msg:
                text = msg['text'].strip().lower()

                if text == "/start":
                    self.send_welcome_message(chat_id)
                    return
                elif text == "/help":
                    self.send_help_message(chat_id)
                    return

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
                               "- blur\n- contour\n- rotate\n- segment\n- salt and pepper\n- gamma correction\n- posterize\n- inverse\n"
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
            elif caption == 'gamma correction':
                image.gamma_correction()
            elif caption == 'posterize':
                image.posterize()
            elif caption == 'inverse':
                image.inverse()
            else:
                self.send_text(chat_id, f"Unsupported filter: {caption}")
                return

            result_path = image.save_img()
            self.send_photo(chat_id, result_path)

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(msg['chat']['id'], "Something went wrong... please try again.")
