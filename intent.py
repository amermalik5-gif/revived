"""
Intent detection for bilingual (Arabic / English) natural language queries.
Uses keyword/regex matching — no external NLP service needed.
"""

import re

# ── Intent patterns ───────────────────────────────────────────────────────────
INTENTS = [
    # Stock queries
    ("stock_query",       r"stock|مخزون|مخزن|كمية|كم متبقي|كم باقي|كم عندي|موجود|inventory"),
    ("low_stock",         r"low.?stock|ناقص|نفد|خلص|منتهي|out.?of.?stock|نقص"),
    ("stock_movement",    r"movement|حركة|دخل|خرج|وارد|صادر|transaction|history|تاريخ"),
    ("all_stock",         r"all.?stock|كل المخزون|كل المنتجات|قائمة المنتجات|all product"),

    # Sales / invoices
    ("today_sales",       r"today.?sale|today.?revenue|مبيعات اليوم|إيرادات اليوم|اليوم"),
    ("week_sales",        r"week.?sale|this.?week|مبيعات الأسبوع|الأسبوع"),
    ("month_sales",       r"month.?sale|this.?month|مبيعات الشهر|الشهر"),
    ("outstanding",       r"outstanding|unpaid|overdue|مديونية|دين|فاتورة غير مدفوعة|مستحق"),

    # Suppliers
    ("suppliers",         r"supplier|مورد|موردين|payable|مستحق للمورد"),

    # Expenses & profit
    ("expenses",          r"expense|مصروف|مصاريف|تكاليف|cost"),
    ("profit",            r"profit|ربح|أرباح|net|صافي"),

    # Summary
    ("daily_summary",     r"summary|ملخص|تقرير|report|morning|صباح"),

    # Help
    ("help",              r"help|مساعدة|ماذا تعرف|ايش تعرف|وش تعرف|كيف تساعد|commands"),
]

COMPILED = [(intent, re.compile(pattern, re.IGNORECASE)) for intent, pattern in INTENTS]


def detect_intent(text: str) -> str:
    """Return the first matching intent, or 'unknown'."""
    for intent, pattern in COMPILED:
        if pattern.search(text):
            return intent
    return "unknown"


def extract_product_name(text: str) -> str | None:
    """
    Try to extract a product name from the query.
    Strips common question words and returns what's left (best-effort).
    """
    # Remove common filler words
    cleaned = re.sub(
        r"(stock|مخزون|كمية|كم|what is|what's|كم عندي|كم باقي|موجود|ما هو|ما|of|من|عن|for|ل)",
        " ", text, flags=re.IGNORECASE
    ).strip()
    # Remove trailing punctuation / question marks
    cleaned = re.sub(r"[؟?]+$", "", cleaned).strip()
    return cleaned if len(cleaned) > 1 else None


def is_arabic(text: str) -> bool:
    """Return True if the message contains Arabic characters."""
    return bool(re.search(r"[؀-ۿ]", text))
