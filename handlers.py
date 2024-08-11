import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from processors import (
    process_document,
    process_photo,
    process_audio,
    process_text,
    process_url,
    query_knowledge_base
)
from database import is_user_activated, activate_user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if await is_user_activated(user.id):
        await update.message.reply_text("Welcome back! Your Recall AI is ready to use.")
    else:
        keyboard = [[InlineKeyboardButton("Activate Recall", callback_data='activate')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome to Recall AI! Please activate your account to start using the bot.",
            reply_markup=reply_markup
        )

# Activation button callback
async def activate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Please enter your license key:")
    context.user_data['awaiting_license'] = True

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
    Here's what I can do:
    - Remember text messages
    - Process documents (PDF, DOC)
    - Analyze images
    - Transcribe audio
    - Extract information from URLs
    
    Just send me any of these, and I'll store the information.
    To ask a question, use the /ask command followed by your question.
    """
    await update.message.reply_text(help_text)

# Handle license key input
async def handle_license_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_license'):
        license_key = update.message.text
        success, message = await activate_user(update.effective_user.id, license_key)
        if success:
            context.user_data['awaiting_license'] = False
            await update.message.reply_text(message + " You can now use Recall AI.")
        else:
            await update.message.reply_text(message)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to use this feature.")
        return
    doc = update.message.document
    username = update.message.from_user.username
    await update.message.reply_text("Processing your document. This might take a moment...")
    result = await process_document(doc, username)
    await update.message.reply_text(f"I'll remember the document: {result}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to use this feature.")
        return
    photo = update.message.photo[-1]  # Get the largest photo
    username = update.message.from_user.username
    await update.message.reply_text("Analyzing your image. One moment please...")
    result = await process_photo(photo, username)
    await update.message.reply_text(f"I'll remember the image: {result}")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to use this feature.")
        return
    audio = update.message.audio
    username = update.message.from_user.username
    await update.message.reply_text("Transcribing your audio. This might take a while...")
    result = await process_audio(audio, username)
    await update.message.reply_text(f"I'll remember the audio: {result}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to use this feature.")
        return
    text = update.message.text
    username = update.message.from_user.username
    if text.startswith(('http://', 'https://')):
        await update.message.reply_text("Processing the URL. One moment...")
        result = await process_url(text, username)
        await update.message.reply_text(f"URL processed: {result}")
    else:
        result = await process_text(text, username)
        await update.message.reply_text(f"I've stored this information: {result}")

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to use this feature.")
        return
    query = update.message.text.replace('/ask', '').strip()
    if not query:
        await update.message.reply_text("Please provide a question after the /ask command.")
        return
    username = update.message.from_user.username
    result = await query_knowledge_base(query, username)
    await update.message.reply_text(result)