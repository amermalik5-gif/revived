"""
Daftra API wrapper — read-only access to stock, invoices, expenses, suppliers, clients.
Base URL: https://{subdomain}.daftra.com/api2
Auth: apikey header
"""

import httpx
from datetime import datetime, timedelta
from config import DAFTRA_API_KEY, DAFTRA_SUBDOMAIN

BASE_URL = f"https://{DAFTRA_SUBDOMAIN}.daftra.com/api2"
HEADERS = {
    "apikey": DAFTRA_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json",
}
TIMEOUT = 30


async def _get_all_pages(endpoint: str, key: str, params: dict = None) -> list:
    """Fetch all pages for a paginated endpoint and extract items by key."""
    items = []
    page = 1
    params = params or {}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        while True:
            r = await client.get(
                f"{BASE_URL}/{endpoint}",
                headers=HEADERS,
                params={**params, "page": page, "limit": 100},
            )
            data = r.json()
            if data.get("code") != 200:
                break
            batch = data.get("data", [])
            if not batch:
                break
            items.extend([item[key] for item in batch if key in item])
            pagination = data.get("pagination", {})
            if page >= int(pagination.get("page_count", 1)):
                break
            page += 1
    return items


# ── Products / Stock ──────────────────────────────────────────────────────────

async def get_all_products() -> list:
    """Return all products with stock_balance, unit_price, buy_price, etc."""
    return await _get_all_pages("products.json", "Product")


async def search_products(query: str) -> list:
    """Return products whose name contains the query (case-insensitive)."""
    products = await get_all_products()
    q = query.strip().lower()
    return [p for p in products if q in (p.get("name") or "").lower()]


async def get_out_of_stock() -> list:
    """Return products with stock_balance == 0 and track_stock == True."""
    products = await get_all_products()
    return [
        p for p in products
        if p.get("track_stock") and float(p.get("stock_balance") or 0) <= 0
    ]


async def get_low_stock() -> list:
    """Return products where stock_balance <= low_stock_threshold (and tracked)."""
    products = await get_all_products()
    result = []
    for p in products:
        if not p.get("track_stock"):
            continue
        balance = float(p.get("stock_balance") or 0)
        threshold = float(p.get("low_stock_thershold") or 0)
        if balance <= 0:
            result.append({**p, "_status": "out"})
        elif threshold and balance <= threshold:
            result.append({**p, "_status": "low"})
    return result


async def get_stock_transactions(product_id: int = None, limit: int = 20) -> list:
    """Return recent stock transactions, optionally filtered by product."""
    params = {"limit": limit}
    if product_id:
        params["product_id"] = product_id
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(
            f"{BASE_URL}/stock_transactions.json",
            headers=HEADERS,
            params=params,
        )
        data = r.json()
        if data.get("code") == 200:
            return [item["StockTransaction"] for item in data.get("data", []) if "StockTransaction" in item]
    return []


# ── Invoices / Sales ──────────────────────────────────────────────────────────

async def get_invoices(date_from: str = None, date_to: str = None) -> list:
    """Return sales invoices, optionally filtered by date range (YYYY-MM-DD)."""
    params = {}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return await _get_all_pages("invoices.json", "Invoice", params)


async def get_todays_invoices() -> list:
    today = datetime.now().strftime("%Y-%m-%d")
    return await get_invoices(date_from=today, date_to=today)


async def get_this_week_invoices() -> list:
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    week_end = today.strftime("%Y-%m-%d")
    return await get_invoices(date_from=week_start, date_to=week_end)


async def get_this_month_invoices() -> list:
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    month_end = today.strftime("%Y-%m-%d")
    return await get_invoices(date_from=month_start, date_to=month_end)


async def get_outstanding_invoices() -> list:
    """Invoices where balance (amount_due) > 0 — i.e., not fully paid."""
    invoices = await get_invoices()
    return [
        inv for inv in invoices
        if float(inv.get("balance") or inv.get("amount_due") or 0) > 0
    ]


# ── Expenses ──────────────────────────────────────────────────────────────────

async def get_expenses(date_from: str = None, date_to: str = None) -> list:
    params = {}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return await _get_all_pages("expenses.json", "Expense", params)


async def get_this_month_expenses() -> list:
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    month_end = today.strftime("%Y-%m-%d")
    return await get_expenses(date_from=month_start, date_to=month_end)


# ── Suppliers ─────────────────────────────────────────────────────────────────

async def get_suppliers() -> list:
    return await _get_all_pages("suppliers.json", "Supplier")


# ── Clients ───────────────────────────────────────────────────────────────────

async def get_clients() -> list:
    return await _get_all_pages("clients.json", "Client")


async def get_clients_with_balance() -> list:
    """Clients who owe money (positive balance)."""
    clients = await get_clients()
    return [c for c in clients if float(c.get("balance") or 0) > 0]
