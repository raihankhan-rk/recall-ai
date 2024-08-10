import logging
import os
from dotenv import load_dotenv
import openai
import secrets
from database import get_user_license_status
from telegram import Update
from telegram.ext import ContextTypes

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)

async def extract_text_from_image(image_file):
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image? Extract all important text."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_file.read().encode('base64')}",
                        }
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message['content']

async def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        max_tokens=150
    )
    return response.choices[0].message['content']

async def verify_license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not get_user_license_status(user_id):
        await update.message.reply_text("Your license is not active. Please use the /activate command to activate your license.")
        return False
    return True