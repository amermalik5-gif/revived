import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
DAFTRA_API_KEY = os.getenv("DAFTRA_API_KEY")
DAFTRA_SUBDOMAIN = os.getenv("DAFTRA_SUBDOMAIN")  # e.g. "revive" from revive.daftra.com
MORNING_SUMMARY_HOUR = int(os.getenv("MORNING_SUMMARY_HOUR", "8"))
MORNING_SUMMARY_MINUTE = int(os.getenv("MORNING_SUMMARY_MINUTE", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Riyadh")
LOW_STOCK_CHECK_INTERVAL_HOURS = int(os.getenv("LOW_STOCK_CHECK_INTERVAL_HOURS", "6"))
