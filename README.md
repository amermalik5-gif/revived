# Revive Manager Bot 🤖

A Telegram personal assistant for the Revive manager, powered by the Daftra API.

## What it does

- **Stock queries** — ask about any product's quantity, price, movement history
- **Low stock alerts** — automatic alerts when products go out of stock
- **Sales summary** — today's, this week's, this month's sales
- **Outstanding invoices** — who owes money and how much
- **Supplier balances** — what you owe suppliers
- **Expenses & profit** — monthly breakdown
- **Daily morning summary** — automatic report every morning
- **Bilingual** — responds in Arabic or English based on what you write

---

## Setup (one time)

### Step 1 — Create your Telegram bot

1. Open Telegram → search `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the **bot token** you receive

### Step 2 — Get your Telegram user ID

1. Open Telegram → search `@userinfobot`
2. Send `/start` — it will show your **user ID** (a number like `123456789`)

### Step 3 — Get your Daftra API key

1. Log in to Daftra
2. Go to **Settings → API → API Key**
3. Generate or copy your key

### Step 4 — Configure the bot

```bash
cd telegram-bot
cp .env.example .env
# Edit .env and fill in all values
```

### Step 5 — Deploy to Railway (free)

1. Go to [railway.app](https://railway.app) and sign up
2. Click **New Project → Deploy from GitHub repo**
3. Push this folder to a GitHub repo first, then connect it
4. In Railway: go to **Variables** and add all values from your `.env` file
5. Railway will auto-detect the `Procfile` and start the bot

**Alternative — run locally:**
```bash
pip install -r requirements.txt
python bot.py
```

---

## Example queries

| You type | Bot does |
|---|---|
| `كم الكمية من شامبو كيراستاس` | Stock level for that product |
| `أي منتجات نفدت؟` | Lists out-of-stock items |
| `حركة مخزون البروتين` | Stock movement for Protein |
| `مبيعات اليوم` | Today's sales total |
| `الفواتير غير المدفوعة` | Outstanding invoices |
| `مصاريف الشهر` | This month's expenses |
| `ملخص اليوم` | Full morning summary |
| `stock of keratin` | English also works |
| `today's sales` | ✅ |
| `help` | Shows all commands |

---

## File structure

```
telegram-bot/
├── bot.py          # Entry point
├── config.py       # Environment variables
├── daftra.py       # Daftra API wrapper (read-only)
├── intent.py       # Arabic/English intent detection
├── handlers.py     # Telegram message handlers
├── scheduler.py    # Morning summary + stock alerts
├── responses.py    # Message formatting
├── requirements.txt
├── Procfile        # For Railway/Render
└── .env.example    # Config template
```
