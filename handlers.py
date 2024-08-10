from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from processors import (
    process_document,
    process_photo,
    process_audio,
    process_text,
    process_url,
    query_knowledge_base
)
from database import activate_user_license, get_user_license_status, create_new_license

AWAITING_LICENSE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if get_user_license_status(user_id):
        await update.message.reply_text("Welcome back! I'm your second brain. Send me any information, and I'll remember it for you.")
    else:
        await update.message.reply_text("Welcome! To start using the bot, please activate your license using the /activate command.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
    Here's what I can do:
    - Remember text messages
    - Process documents (PDF, DOC)
    - Analyze images
    - Transcribe audio
    - Extract information from URLs
    
    Just send me any of these, and I'll store the information. Ask me anything, and I'll try to recall it!

    To activate your license, use the /activate command.
    """
    await update.message.reply_text(help_text)

async def activate_license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if get_user_license_status(user_id):
        await update.message.reply_text("Your license is already active.")
        return ConversationHandler.END

    if context.args:
        license_key = context.args[0]
        if activate_user_license(user_id, license_key):
            await update.message.reply_text("License activated successfully! You can now use all features of the bot.")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Invalid license key. Please try again or contact support.")
            return ConversationHandler.END

    await update.message.reply_text("Please enter your license key:")
    return AWAITING_LICENSE

async def handle_license_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    license_key = update.message.text

    if activate_user_license(user_id, license_key):
        await update.message.reply_text("License activated successfully! You can now use all features of the bot.")
    else:
        await update.message.reply_text("Invalid license key. Please try again or contact support.")

    return ConversationHandler.END

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document
    await update.message.reply_text("Processing your document. This might take a moment...")
    result = await process_document(doc)
    await update.message.reply_text(f"Document processed: {result}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]  # Get the largest photo
    await update.message.reply_text("Analyzing your image. One moment please...")
    result = await process_photo(photo)
    await update.message.reply_text(f"Image analyzed: {result}")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio = update.message.audio
    await update.message.reply_text("Transcribing your audio. This might take a while...")
    result = await process_audio(audio)
    await update.message.reply_text(f"Audio transcribed: {result}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text.startswith(('http://', 'https://')):
        await update.message.reply_text("Processing the URL. One moment...")
        result = await process_url(text)
        await update.message.reply_text(f"URL processed: {result}")
    else:
        result = await process_text(text)
        if result.startswith("Query:"):
            response = await query_knowledge_base(result[6:])
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(f"Stored: {result}")