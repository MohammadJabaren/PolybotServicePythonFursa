import telebot
from loguru import logger
import os
import uuid
import time
import boto3
import requests
from dotenv import load_dotenv
from telebot.types import InputFile
from polybot.img_proc import Img


load_dotenv()

PHOTO_DIR = 'photos'
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

YOLO_IP = os.getenv("YOLO_IP")
s3 = boto3.client("s3")
S3_BUCKET = os.getenv("AWS_S3_BUCKET")

class Bot:

    def __init__(self, token, telegram_chat_url):
        self.telegram_bot_client = telebot.TeleBot(token)
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')
        self.media_group_cache = {}

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def download_user_photo(self, msg):
        if not self.is_current_msg_photo(msg):
            raise RuntimeError("Message content of type 'photo' expected")

        try:
            file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
            data = self.telegram_bot_client.download_file(file_info.file_path)

            ext = os.path.splitext(file_info.file_path)[1]
            image_name = f"{uuid.uuid4().hex}{ext}"

            # Save the image in the specified 'photos' directory
            local_image_path = os.path.join(PHOTO_DIR, image_name)
            with open(local_image_path, 'wb') as f:
                f.write(data)
            logger.info(f"Image uploaded successfully with name: {image_name}")
            # Ensure the file was saved before proceeding
            if not os.path.exists(local_image_path):
                raise RuntimeError(f"Failed to save the image locally at {local_image_path}")

            # Upload image to S3
            with open(local_image_path, 'rb') as f:
                s3.put_object(Bucket=S3_BUCKET, Key=image_name, Body=f)

            logger.info(f"Image uploaded successfully with name: {image_name}")

            return local_image_path

        except Exception as e:
            logger.error(f"Error downloading or uploading image: {e}")
            raise RuntimeError("Error processing the image. Please try again.")


    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])

class ImageProcessingBot(Bot):
    def send_welcome_message(self, chat_id):
        self.send_text(chat_id,
                       "👋 Hello! I'm your image processing bot.\n\n"
                       "📷 Send me a photo with one of these captions to apply a filter:\n"
                       "- blur\n- contour\n- rotate\n- segment\n- salt and pepper\n- gamma correction\n- posterize\n- inverse\n- detection\n\n"
                       "🖼️ To concatenate two images, send them as a media group (album) with one of these captions:\n"
                       "- concat horizontal\n- concat vertical\n"
                       "❓ Type /help for more instructions!")

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
            "- **salt and pepper**: Add salt-and-pepper noise to the image.\n"
            "- **detection**: Perform object detection on the image.\n\n"
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

            if self.is_text_command(msg):
                self.handle_text_command(msg, chat_id)
                return

            if media_group_id:
                self.handle_media_group(msg, chat_id, media_group_id)
                return

            if not self.is_current_msg_photo(msg):
                self.send_text(chat_id,
                               "Send a photo with one of these captions:\n"
                               "- blur\n- contour\n- rotate\n- segment\n- salt and pepper\n- gamma correction\n- posterize\n- inverse- detection\n"
                               "- concat horizontal or concat vertical (send 2 photos as album)")
                return

            if caption.startswith('concat'):
                self.send_text(chat_id, "Please send two images as a media group (album) for concatenation.")
                return

            self.handle_single_image(msg, chat_id, caption)

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(msg['chat']['id'], "Something went wrong... please try again.")

    def is_text_command(self, msg):
        return 'text' in msg and msg['text'].strip().lower() in ["/start", "/help"]

    def handle_text_command(self, msg, chat_id):
        text = msg['text'].strip().lower()
        if text == "/start":
            self.send_welcome_message(chat_id)
        elif text == "/help":
            self.send_help_message(chat_id)

    def handle_media_group(self, msg, chat_id, media_group_id):
        if media_group_id not in self.media_group_cache:
            self.media_group_cache[media_group_id] = []
        self.media_group_cache[media_group_id].append(msg)

        if len(self.media_group_cache[media_group_id]) < 2:
            return

        msg1, msg2 = self.media_group_cache[media_group_id][:2]
        caption = msg1.get("caption", "").strip().lower() or msg2.get("caption", "").strip().lower()

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

    def handle_single_image(self, msg, chat_id, caption):
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
        elif caption == 'detection':
            self.handle_detection(chat_id, img_path)
            return
        else:
            self.send_text(chat_id, f"Unsupported filter: {caption}")
            return

        result_path = image.save_img()
        self.send_photo(chat_id, result_path)

    def handle_detection(self, chat_id, img_path):
        self.send_text(chat_id, "Processing the image for object detection...")

        try:
            # Extract the image name from the path (just for logging or any other purpose)
            image_name = os.path.basename(img_path)
            data = {
                "s3_key": image_name
            }

            response = requests.post(f"{YOLO_IP}/predict", data=data)
            if response.status_code == 200:
                detection_result = response.json()
                uid = detection_result.get("prediction_uid")
                logger.info(f'uid: {uid}')

                prediction_response = requests.get(f"{YOLO_IP}/prediction/{uid}")
                if prediction_response.status_code == 200:
                    prediction_data = prediction_response.json()
                    detection_objects = prediction_data.get("detection_objects", [])
                    detected_labels = [obj["label"] for obj in detection_objects if "label" in obj]
                    objects_message = "Detected objects: " + ", ".join(
                        detected_labels) if detected_labels else "No objects detected."
                    self.send_text(chat_id, objects_message)

                else:
                    self.send_text(chat_id, "Error: Unable to retrieve prediction results.")
            else:
                self.send_text(chat_id,
                               f"Error: Could not process image for object detection. Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            self.send_text(chat_id, f"Error: Unable to reach the Yolo service. {e}")