"""
Intent detection for bilingual (Arabic / English) natural language queries.
"""

import re

# ORDER MATTERS — more specific patterns must come before general ones
INTENTS = [
    # All stock list (must be before stock_query)
    ("all_stock",      r"all.?stock|show.?me.?all|show.?all|كل المخزون|كل المنتجات|قائمة المنتجات|all product|list.?stock|list.?product"),

    # Low stock (must be before stock_query)
    ("low_stock",      r"low.?stock|out.?of.?stock|ناقص|نفد|نفذ|خلص|منتهي|نقص|أي منتجات|اي منتجات"),

    # Stock movement (must be before stock_query)
    ("stock_movement", r"movement|حركة|دخل|خرج|وارد|صادر|transaction|history|تاريخ"),

    # Specific product stock query
    ("stock_query",    r"stock|مخزون|مخزن|كمية|كم متبقي|كم باقي|كم عندي|موجود|inventory|كم ال"),

    # Sales — yesterday before today (more specific first)
    ("yesterday_sales", r"yesterday|امس|أمس|مبارح|البارح"),
    ("today_sales",     r"today.?sale|today.?revenue|مبيعات اليوم|إيرادات اليوم|اليوم"),
    ("week_sales",      r"week.?sale|this.?week|مبيعات الأسبوع|الأسبوع"),
    ("month_sales",     r"month.?sale|this.?month|مبيعات الشهر|الشهر"),
    ("outstanding",     r"outstanding|unpaid|overdue|مديونية|دين|فاتورة غير مدفوعة|مستحق"),

    # Suppliers
    ("suppliers",  r"supplier|مورد|موردين|payable|مستحق للمورد"),

    # Expenses & profit
    ("expenses", r"expense|مصروف|مصاريف|تكاليف|cost"),
    ("profit",   r"profit|ربح|أرباح|net|صافي"),

    # Summary
    ("daily_summary", r"summary|ملخص|تقرير|report|morning|صباح"),

    # Help
    ("help", r"help|مساعدة|ماذا تعرف|ايش تعرف|وش تعرف|كيف تساعد|commands"),
]

COMPILED = [(intent, re.compile(pattern, re.IGNORECASE)) for intent, pattern in INTENTS]


def detect_intent(text: str) -> str:
    for intent, pattern in COMPILED:
        if pattern.search(text):
            return intent
    return "unknown"


def extract_product_name(text: str) -> str | None:
    cleaned = re.sub(
        r"(stock|مخزون|كمية|كم|what is|what'?s|كم عندي|كم باقي|موجود|ما هو|ما|of|من|عن|for|ل|show|me|all|list)",
        " ", text, flags=re.IGNORECASE
    ).strip()
    cleaned = re.sub(r"[؟?]+$", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) > 1 else None


def is_arabic(text: str) -> bool:
    return bool(re.search(r"[؀-ۿ]", text))
