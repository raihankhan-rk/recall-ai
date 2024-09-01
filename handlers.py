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

async def activate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Please enter your license key:")
    context.user_data['awaiting_license'] = True

async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if await is_user_activated(user_id=user_id):
        await update.message.reply_text("Your account is already activated.")
        return

    if not context.args:
        await update.message.reply_text("Please provide your license key after the /activate command.")
        return

    license_key = context.args[0]
    success, message = await activate_user(user_id, username, license_key)
    await update.message.reply_text(message)

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
    
    Other commands:
    /start - Start the bot
    /help - Show this help message
    /activate <LICENSE_KEY> - Activate your account with a license key
    """
    await update.message.reply_text(help_text)

async def handle_license_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_license'):
        license_key = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username
        success, message = await activate_user(user_id, username, license_key)
        if success:
            context.user_data['awaiting_license'] = False
            await update.message.reply_text(message + " You can now start using Recall AI.")
        else:
            await update.message.reply_text(message)
    else:
        # If not awaiting license, treat as normal text
        await handle_text(update, context)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to start using Recall. You can use /activate <LICENSE_KEY> to activate your account.")
        return
    doc = update.message.document
    username = update.message.from_user.username
    print(f"User {username} sent a document: {doc.file_name}")
    await process_document(doc, username)
    await update.message.reply_text("Sure! Will remember that")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to start using Recall. You can use /activate <LICENSE_KEY> to activate your account.")
        return
    photo = update.message.photo[-1]  # Get the largest photo
    username = update.message.from_user.username
    print(f"User {username} sent a photo")
    await process_photo(photo, username)
    await update.message.reply_text("Sure! Will remember that")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to start using Recall. You can use /activate <LICENSE_KEY> to activate your account.")
        return
    audio = update.message.audio
    username = update.message.from_user.username
    print(f"User {username} sent an audio file: {audio.file_name}")
    await process_audio(audio, username)
    await update.message.reply_text("Sure! Will remember that")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to start using Recall. You can use /activate <LICENSE_KEY> to activate your account.")
        return
    text = update.message.text
    username = update.message.from_user.username
    print(f"User {username} sent a text message: {text}")
    if text.startswith(('http://', 'https://')):
        await process_url(text, username)
    else:
        await process_text(text, username)
    await update.message.reply_text("Sure! Will remember that")

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_activated(update.effective_user.id):
        await update.message.reply_text("Please activate your account to start using Recall. You can use /activate <LICENSE_KEY> to activate your account.")
        return
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Please provide a question after the /ask command.")
        return
    username = update.message.from_user.username
    print(f"User {username} asked a question: {query}")
    result = await query_knowledge_base(query, username)
    await update.message.reply_text(result)