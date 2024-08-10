import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from processors import (
    process_document,
    process_photo,
    process_audio,
    process_text,
    process_url,
    query_knowledge_base
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! I'm Recall AI, your second brain. Send me any information, and I'll remember it for you.")

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

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document
    username = update.message.from_user.username
    await update.message.reply_text("Processing your document. This might take a moment...")
    result = await process_document(doc, username)
    await update.message.reply_text(f"I'll remember the document: {result}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]  # Get the largest photo
    username = update.message.from_user.username
    await update.message.reply_text("Analyzing your image. One moment please...")
    result = await process_photo(photo, username)
    await update.message.reply_text(f"I'll remember the image: {result}")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio = update.message.audio
    username = update.message.from_user.username
    await update.message.reply_text("Transcribing your audio. This might take a while...")
    result = await process_audio(audio, username)
    await update.message.reply_text(f"I'll remember the audio: {result}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    query = update.message.text.replace('/ask', '').strip()
    if not query:
        await update.message.reply_text("Please provide a question after the /ask command.")
        return
    username = update.message.from_user.username
    result = await query_knowledge_base(query, username)
    await update.message.reply_text(result)