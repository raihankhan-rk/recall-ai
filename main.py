import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import start, help_command, handle_document, handle_photo, handle_audio, handle_text, activate_license,  AWAITING_LICENSE
from utils import setup_logging, verify_license
from database import init_db, get_db_connection

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

logger = setup_logging()

def main() -> None:
    # Initialize database
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for license activation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("activate", activate_license)],
        states={
            AWAITING_LICENSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_license)]
        },
        fallbacks=[CommandHandler("cancel", lambda update, context: ConversationHandler.END)]
    )

    application.add_handler(conv_handler)

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # application.add_handler(MessageHandler(filters.DOCUMENT, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))

    # Add license verification middleware
    application.add_handler(MessageHandler(filters.ALL, verify_license), group=-1)

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()