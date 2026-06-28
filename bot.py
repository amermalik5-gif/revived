"""
Revive Manager Bot — entry point.
Run: python bot.py
"""

import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN, AUTHORIZED_USER_ID
from handlers import handle_message, handle_start, handle_debug, handle_debug2, handle_debug3, handle_debug4, handle_debug5
from scheduler import start_scheduler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")
    if not AUTHORIZED_USER_ID:
        raise ValueError("AUTHORIZED_USER_ID is not set in .env")

    logger.info(f"Starting Revive Manager Bot | Authorized user: {AUTHORIZED_USER_ID}")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("help", handle_start))
    app.add_handler(CommandHandler("debug", handle_debug))
    app.add_handler(CommandHandler("debug2", handle_debug2))
    app.add_handler(CommandHandler("debug3", handle_debug3))
    app.add_handler(CommandHandler("debug4", handle_debug4))
    app.add_handler(CommandHandler("debug5", handle_debug5))

    # All text messages → NLP handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start scheduler (morning summary + stock alerts)
    scheduler = start_scheduler(app.bot)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
