"""
Scheduled jobs:
  1. Morning summary — sent daily at configured hour
  2. Low stock check — runs every N hours, alerts if anything is out of stock
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot
from telegram.constants import ParseMode

import daftra
import responses as fmt
from config import (
    AUTHORIZED_USER_ID,
    MORNING_SUMMARY_HOUR,
    MORNING_SUMMARY_MINUTE,
    TIMEZONE,
    LOW_STOCK_CHECK_INTERVAL_HOURS,
)

logger = logging.getLogger(__name__)

# Track last alerted out-of-stock product ids to avoid repeated pings
_last_oos_ids: set = set()


async def send_morning_summary(bot: Bot):
    logger.info("Running morning summary job")
    try:
        today_invoices = await daftra.get_todays_invoices()
        out_of_stock = await daftra.get_out_of_stock()
        outstanding = await daftra.get_outstanding_invoices()
        msg = fmt.fmt_daily_summary(today_invoices, out_of_stock, outstanding, arabic=False)
        await bot.send_message(
            chat_id=AUTHORIZED_USER_ID,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
        )
        logger.info("Morning summary sent")
    except Exception as e:
        logger.error(f"Morning summary failed: {e}", exc_info=True)


async def check_low_stock(bot: Bot):
    global _last_oos_ids
    logger.info("Running low-stock check job")
    try:
        out_of_stock = await daftra.get_out_of_stock()
        oos_ids = {p["id"] for p in out_of_stock}

        # Only alert for newly out-of-stock products
        new_oos = [p for p in out_of_stock if p["id"] not in _last_oos_ids]

        if new_oos:
            msg = fmt.fmt_low_stock_list(new_oos, arabic=False)
            await bot.send_message(
                chat_id=AUTHORIZED_USER_ID,
                text=msg,
                parse_mode=ParseMode.MARKDOWN,
            )
            logger.info(f"Low-stock alert sent for {len(new_oos)} products")

        _last_oos_ids = oos_ids
    except Exception as e:
        logger.error(f"Low-stock check failed: {e}", exc_info=True)


def start_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # Morning summary
    scheduler.add_job(
        send_morning_summary,
        trigger=CronTrigger(
            hour=MORNING_SUMMARY_HOUR,
            minute=MORNING_SUMMARY_MINUTE,
            timezone=TIMEZONE,
        ),
        args=[bot],
        id="morning_summary",
        name="Daily Morning Summary",
        replace_existing=True,
    )

    # Low stock check
    scheduler.add_job(
        check_low_stock,
        trigger=IntervalTrigger(hours=LOW_STOCK_CHECK_INTERVAL_HOURS),
        args=[bot],
        id="low_stock_check",
        name="Low Stock Alert",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started — morning summary at {MORNING_SUMMARY_HOUR:02d}:{MORNING_SUMMARY_MINUTE:02d} {TIMEZONE}, "
        f"stock check every {LOW_STOCK_CHECK_INTERVAL_HOURS}h"
    )
    return scheduler
