"""
Telegram message handlers — routes natural language to Daftra API calls.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import daftra
import responses as fmt
from intent import detect_intent, extract_product_name, is_arabic
from config import AUTHORIZED_USER_ID

logger = logging.getLogger(__name__)


def authorized_only(func):
    """Decorator: only respond to the authorized manager."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != AUTHORIZED_USER_ID:
            await update.message.reply_text("⛔ Unauthorized")
            return
        return await func(update, context)
    return wrapper


async def _reply(update: Update, text: str):
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@authorized_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    arabic = is_arabic(text)
    intent = detect_intent(text)

    logger.info(f"Intent: {intent} | Text: {text[:60]}")

    try:
        if intent == "help" or not text.strip():
            await _reply(update, fmt.fmt_help(arabic))

        elif intent == "stock_query":
            product_name = extract_product_name(text)
            if product_name and len(product_name) > 1:
                products = await daftra.search_products(product_name)
                if products:
                    msg = "\n\n".join(fmt.fmt_product_stock(p, arabic) for p in products[:5])
                else:
                    msg = f"❌ لم أجد منتجاً باسم *{product_name}*" if arabic else f"❌ No product found matching *{product_name}*"
            else:
                # Show all stock if no specific product mentioned
                products = await daftra.get_all_products()
                msg = fmt.fmt_all_stock(products, arabic)
            await _reply(update, msg)

        elif intent == "all_stock":
            products = await daftra.get_all_products()
            msg = fmt.fmt_all_stock(products, arabic)
            await _reply(update, msg)

        elif intent == "low_stock":
            products = await daftra.get_low_stock()
            msg = fmt.fmt_low_stock_list(products, arabic)
            await _reply(update, msg)

        elif intent == "stock_movement":
            product_name = extract_product_name(text)
            if product_name and len(product_name) > 1:
                matched = await daftra.search_products(product_name)
                if matched:
                    product = matched[0]
                    txns = await daftra.get_stock_transactions(product_id=product["id"])
                    msg = fmt.fmt_stock_movement(txns, product["name"], arabic)
                else:
                    msg = f"❌ لم أجد منتجاً باسم *{product_name}*" if arabic else f"❌ No product found: *{product_name}*"
            else:
                txns = await daftra.get_stock_transactions()
                msg = fmt.fmt_stock_movement(txns, "all" if not arabic else "الكل", arabic)
            await _reply(update, msg)

        elif intent == "today_sales":
            invoices = await daftra.get_todays_invoices()
            period = "اليوم" if arabic else "Today"
            msg = fmt.fmt_sales_summary(invoices, period, arabic)
            await _reply(update, msg)

        elif intent == "week_sales":
            invoices = await daftra.get_this_week_invoices()
            period = "هذا الأسبوع" if arabic else "This Week"
            msg = fmt.fmt_sales_summary(invoices, period, arabic)
            await _reply(update, msg)

        elif intent == "month_sales":
            invoices = await daftra.get_this_month_invoices()
            period = "هذا الشهر" if arabic else "This Month"
            msg = fmt.fmt_sales_summary(invoices, period, arabic)
            await _reply(update, msg)

        elif intent == "outstanding":
            invoices = await daftra.get_outstanding_invoices()
            msg = fmt.fmt_outstanding_invoices(invoices, arabic)
            await _reply(update, msg)

        elif intent == "suppliers":
            suppliers = await daftra.get_suppliers()
            msg = fmt.fmt_suppliers(suppliers, arabic)
            await _reply(update, msg)

        elif intent == "expenses":
            expenses = await daftra.get_this_month_expenses()
            period = "هذا الشهر" if arabic else "This Month"
            msg = fmt.fmt_expenses(expenses, period, arabic)
            await _reply(update, msg)

        elif intent == "profit":
            invoices = await daftra.get_this_month_invoices()
            expenses = await daftra.get_this_month_expenses()
            total_sales = sum(float(inv.get("total") or 0) for inv in invoices)
            total_exp = sum(float(e.get("total") or e.get("amount") or 0) for e in expenses)
            profit = total_sales - total_exp
            period = "هذا الشهر" if arabic else "This Month"
            if arabic:
                msg = (
                    f"📊 *الأرباح — {period}*\n\n"
                    f"  💵 المبيعات: *{fmt._cur(total_sales)}*\n"
                    f"  💸 المصاريف: *{fmt._cur(total_exp)}*\n"
                    f"  {'✅' if profit >= 0 else '🔴'} صافي الربح: *{fmt._cur(profit)}*"
                )
            else:
                msg = (
                    f"📊 *Profit — {period}*\n\n"
                    f"  💵 Sales: *{fmt._cur(total_sales)}*\n"
                    f"  💸 Expenses: *{fmt._cur(total_exp)}*\n"
                    f"  {'✅' if profit >= 0 else '🔴'} Net Profit: *{fmt._cur(profit)}*"
                )
            await _reply(update, msg)

        elif intent == "daily_summary":
            today_invoices = await daftra.get_todays_invoices()
            out_of_stock = await daftra.get_out_of_stock()
            outstanding = await daftra.get_outstanding_invoices()
            msg = fmt.fmt_daily_summary(today_invoices, out_of_stock, outstanding, arabic)
            await _reply(update, msg)

        else:
            if arabic:
                await _reply(update, "❓ لم أفهم سؤالك. اكتب *مساعدة* لرؤية ما أستطيع فعله.")
            else:
                await _reply(update, "❓ I didn't understand that. Type *help* to see what I can do.")

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        err = "⚠️ حدث خطأ أثناء جلب البيانات. حاول مرة أخرى." if arabic else "⚠️ Error fetching data. Please try again."
        await _reply(update, err)


@authorized_only
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arabic = is_arabic(update.message.text or "")
    await _reply(update, fmt.fmt_help(arabic))
