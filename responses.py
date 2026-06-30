"""
Format Daftra data into clean Telegram messages.
Supports Arabic and English output.
"""

from datetime import datetime


def _cur(amount, currency="JOD") -> str:
    try:
        return f"{float(amount):,.2f} {currency}"
    except (TypeError, ValueError):
        return f"{amount} {currency}"


def _inv_currency(inv: dict) -> str:
    return inv.get("currency_code") or "JOD"


def _client_name(inv: dict) -> str:
    name = inv.get("client_business_name") or ""
    if not name:
        c = inv.get("Client") or {}
        name = c.get("businessname") or c.get("firstname") or "—"
    return name or "—"


# ── Stock ─────────────────────────────────────────────────────────────────────

def fmt_product_stock(product: dict, arabic: bool = False) -> str:
    name = product.get("name", "—")
    balance = float(product.get("stock_balance") or 0)
    price = product.get("unit_price") or 0
    buy = product.get("buy_price") or 0
    code = product.get("product_code") or "—"
    threshold = float(product.get("low_stock_thershold") or 0)

    status_icon = "✅" if balance > (threshold or 0) else ("⚠️" if balance > 0 else "🚫")

    if arabic:
        return (
            f"{status_icon} *{name}*\n"
            f"  📦 الكمية: *{balance:.0f}*\n"
            f"  💰 سعر البيع: {_cur(price)}\n"
            f"  🏷️ سعر الشراء: {_cur(buy)}\n"
            f"  🔢 الكود: `{code}`"
        )
    return (
        f"{status_icon} *{name}*\n"
        f"  📦 Qty: *{balance:.0f}*\n"
        f"  💰 Sell price: {_cur(price)}\n"
        f"  🏷️ Buy price: {_cur(buy)}\n"
        f"  🔢 Code: `{code}`"
    )


def fmt_low_stock_list(products: list, arabic: bool = False) -> str:
    if not products:
        return "✅ كل المنتجات بخير 🎉" if arabic else "✅ All products are well-stocked 🎉"

    lines = ["⚠️ *تنبيه المخزون*\n" if arabic else "⚠️ *Stock Alert*\n"]
    for p in products:
        name = p.get("name", "—")
        balance = float(p.get("stock_balance") or 0)
        status = p.get("_status", "low")
        icon = "🚫" if status == "out" else "⚠️"
        label = ("نفد" if status == "out" else "منخفض") if arabic else ("OUT" if status == "out" else "LOW")
        lines.append(f"{icon} {name} — {label} ({balance:.0f})")

    return "\n".join(lines)


def fmt_stock_movement(transactions: list, product_name: str, arabic: bool = False) -> str:
    if not transactions:
        return f"لا توجد حركة لـ *{product_name}*" if arabic else f"No movement found for *{product_name}*"

    header = f"📊 *حركة المخزون — {product_name}*\n\n" if arabic else f"📊 *Stock Movement — {product_name}*\n\n"
    lines = [header]
    for t in transactions[:10]:
        t_type = t.get("transaction_type", "")
        qty = t.get("quantity") or 0
        date = (t.get("date") or "")[:10]
        balance = t.get("balance_to_date") or "—"
        icon = "📥" if "1" in str(t_type) else "📤"
        direction = ("وارد" if "1" in str(t_type) else "صادر") if arabic else ("IN" if "1" in str(t_type) else "OUT")
        lines.append(f"{icon} {direction}  qty: {qty}  |  balance: {balance}  |  {date}")

    return "\n".join(lines)


def fmt_all_stock(products: list, arabic: bool = False) -> str:
    if not products:
        return "لا توجد منتجات" if arabic else "No products found"

    header = f"📦 *قائمة المخزون* ({len(products)} منتج)\n\n" if arabic else f"📦 *Stock List* ({len(products)} products)\n\n"
    lines = [header]
    for p in products:
        name = p.get("name", "—")
        balance = float(p.get("stock_balance") or 0)
        icon = "🚫" if balance <= 0 else "✅"
        lines.append(f"{icon} {name}: *{balance:.0f}*")

    return "\n".join(lines)


# ── Sales / Invoices ──────────────────────────────────────────────────────────

def fmt_sales_summary(invoices: list, period: str, arabic: bool = False) -> str:
    currency = invoices[0].get("currency_code", "JOD") if invoices else "JOD"
    total = sum(float(inv.get("summary_total") or 0) for inv in invoices)
    paid = sum(float(inv.get("summary_paid") or 0) for inv in invoices)
    unpaid = sum(float(inv.get("summary_unpaid") or 0) for inv in invoices)
    count = len(invoices)

    if arabic:
        return (
            f"💵 *مبيعات {period}*\n\n"
            f"  🧾 عدد الفواتير: *{count}*\n"
            f"  💰 الإجمالي: *{_cur(total, currency)}*\n"
            f"  ✅ المحصّل: *{_cur(paid, currency)}*\n"
            f"  ⏳ المتبقي: *{_cur(unpaid, currency)}*"
        )
    return (
        f"💵 *Sales — {period}*\n\n"
        f"  🧾 Invoices: *{count}*\n"
        f"  💰 Total: *{_cur(total, currency)}*\n"
        f"  ✅ Collected: *{_cur(paid, currency)}*\n"
        f"  ⏳ Outstanding: *{_cur(unpaid, currency)}*"
    )


def fmt_outstanding_invoices(invoices: list, arabic: bool = False) -> str:
    if not invoices:
        return "✅ لا توجد فواتير غير مدفوعة" if arabic else "✅ No outstanding invoices"

    currency = invoices[0].get("currency_code", "JOD") if invoices else "JOD"
    total_due = sum(float(inv.get("summary_unpaid") or 0) for inv in invoices)
    header = (
        f"📋 *الفواتير غير المدفوعة* ({len(invoices)})\n"
        f"الإجمالي المستحق: *{_cur(total_due, currency)}*\n\n"
    ) if arabic else (
        f"📋 *Outstanding Invoices* ({len(invoices)})\n"
        f"Total due: *{_cur(total_due, currency)}*\n\n"
    )
    lines = [header]
    for inv in invoices[:15]:
        client = _client_name(inv)
        due = float(inv.get("summary_unpaid") or 0)
        inv_no = inv.get("no") or inv.get("id") or "—"
        date = (inv.get("date") or "")[:10]
        lines.append(f"• {client} — *{_cur(due, currency)}* | #{inv_no} | {date}")

    return "\n".join(lines)


# ── Suppliers ─────────────────────────────────────────────────────────────────

def fmt_suppliers(suppliers: list, arabic: bool = False) -> str:
    if not suppliers:
        return "لا يوجد موردون" if arabic else "No suppliers found"

    total_payable = sum(float(s.get("balance") or 0) for s in suppliers if float(s.get("balance") or 0) > 0)

    header = (
        f"🏭 *الموردون* ({len(suppliers)} مورد)\n"
        f"إجمالي المستحق: *{_cur(total_payable)}*\n\n"
    ) if arabic else (
        f"🏭 *Suppliers* ({len(suppliers)})\n"
        f"Total payable: *{_cur(total_payable)}*\n\n"
    )
    lines = [header]
    for s in suppliers[:20]:
        name = s.get("name") or "—"
        balance = float(s.get("balance") or 0)
        icon = "🔴" if balance > 0 else ("🟢" if balance < 0 else "⚪")
        lines.append(f"{icon} {name}: *{_cur(balance)}*")

    return "\n".join(lines)


# ── Expenses ──────────────────────────────────────────────────────────────────

def fmt_expenses(expenses: list, period: str, arabic: bool = False) -> str:
    total = sum(float(e.get("total") or e.get("amount") or 0) for e in expenses)
    count = len(expenses)

    if arabic:
        return (
            f"💸 *المصاريف — {period}*\n\n"
            f"  🔢 عدد: *{count}*\n"
            f"  💰 الإجمالي: *{_cur(total)}*"
        )
    return (
        f"💸 *Expenses — {period}*\n\n"
        f"  🔢 Count: *{count}*\n"
        f"  💰 Total: *{_cur(total)}*"
    )


# ── Daily Morning Summary ─────────────────────────────────────────────────────

def fmt_daily_summary(
    today_invoices: list,
    out_of_stock: list,
    outstanding: list,
    arabic: bool = False,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    currency = today_invoices[0].get("currency_code", "JOD") if today_invoices else "JOD"
    sales_total = sum(float(inv.get("summary_total") or 0) for inv in today_invoices)
    sales_collected = sum(float(inv.get("summary_paid") or 0) for inv in today_invoices)
    sales_count = len(today_invoices)
    oos_count = len(out_of_stock)
    outstanding_total = sum(float(inv.get("summary_unpaid") or 0) for inv in outstanding)

    if arabic:
        msg = (
            f"☀️ *ملخص الصباح — {today}*\n\n"
            f"💵 *مبيعات اليوم*\n"
            f"  🧾 {sales_count} فاتورة | إجمالي: *{_cur(sales_total, currency)}*\n"
            f"  ✅ محصّل: *{_cur(sales_collected, currency)}*\n\n"
            f"📦 *المخزون*\n"
            f"  {'🚫 ' + str(oos_count) + ' منتج نفد' if oos_count else '✅ كل المنتجات متوفرة'}\n\n"
            f"📋 *الفواتير المستحقة*\n"
            f"  {'⚠️ ' + _cur(outstanding_total, currency) + ' مستحق' if outstanding else '✅ لا يوجد مستحقات'}"
        )
    else:
        msg = (
            f"☀️ *Morning Summary — {today}*\n\n"
            f"💵 *Today's Sales*\n"
            f"  🧾 {sales_count} invoices | Total: *{_cur(sales_total, currency)}*\n"
            f"  ✅ Collected: *{_cur(sales_collected, currency)}*\n\n"
            f"📦 *Stock*\n"
            f"  {'🚫 ' + str(oos_count) + ' products out of stock' if oos_count else '✅ All products in stock'}\n\n"
            f"📋 *Outstanding Invoices*\n"
            f"  {'⚠️ ' + _cur(outstanding_total, currency) + ' due' if outstanding else '✅ No outstanding invoices'}"
        )

    if oos_count:
        msg += "\n\n🚫 *" + ("نفد المخزون:" if arabic else "Out of stock:") + "*\n"
        for p in out_of_stock[:5]:
            msg += f"  • {p.get('name', '—')}\n"
        if oos_count > 5:
            msg += f"  ... +{oos_count - 5} {'أخرى' if arabic else 'more'}"

    return msg





def fmt_product_search_results(products: list, query: str, arabic: bool = False) -> str:
    """Compact list: cost + stock. Single result = full detail; multiple = compact list."""
    if not products:
        return ("\u274c \u0644\u0645 \u0623\u062c\u062f \u0645\u0646\u062a\u062c\u0627\u064b \u064a\u0637\u0627\u0628\u0642 " + repr(query)) if arabic else ("\u274c No products found matching " + repr(query))

    if len(products) == 1:
        return fmt_product_stock(products[0], arabic)

    count = len(products)
    header = (
        ("\U0001f50d *\u0646\u062a\u0627\u0626\u062c \u0627\u0644\u0628\u062d\u062b: " + query + "* (" + str(count) + " \u0645\u0646\u062a\u062c)\n\n")
        if arabic else
        ("\U0001f50d *Search: " + query + "* (" + str(count) + " products)\n\n")
    )
    lines = [header]
    for p in products[:25]:
        name = p.get("name", "\u2014")
        balance = float(p.get("stock_balance") or 0)
        buy = float(p.get("buy_price") or 0)
        sell = float(p.get("unit_price") or 0)
        icon = "\u2705" if balance > 0 else "\U0001f6ab"
        if arabic:
            lines.append(
                icon + " *" + name + "*\n"
                "   \U0001f4e6 \u0627\u0644\u0643\u0645\u064a\u0629: " + str(int(balance)) +
                " | \U0001f3f7 \u062a\u0643\u0644\u0641\u0629: " + _cur(buy) +
                " | \U0001f4b0 \u0633\u0639\u0631: " + _cur(sell) + "\n"
            )
        else:
            lines.append(
                icon + " *" + name + "*\n"
                "   \U0001f4e6 Stock: " + str(int(balance)) +
                " | \U0001f3f7 Cost: " + _cur(buy) +
                " | \U0001f4b0 Price: " + _cur(sell) + "\n"
            )
    if count > 25:
        lines.append("... +" + str(count - 25) + (" \u0623\u062e\u0631\u0649" if arabic else " more"))
    return "\n".join(lines)
