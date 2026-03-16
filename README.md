# 🤖 Telegram Trading Signal Bot
### TradingView → Webhook → Telegram

---

## STEP 1 — Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name e.g. `Gemini 3 Pro Legacy Trading Bot`
4. Choose a username e.g. `gemini3pro_bot`
5. BotFather gives you a **BOT TOKEN** — copy it (looks like `7123456789:AAF...`)

---

## STEP 2 — Get Your Chat ID

**Option A — Personal chat:**
1. Message your bot once (send `/start`)
2. Open this URL in browser (replace YOUR_TOKEN):
   `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
3. Find `"chat":{"id":XXXXXXX}` — that number is your Chat ID

**Option B — Group chat:**
1. Add your bot to the group as admin
2. Send a message in the group
3. Use the same getUpdates URL above — the chat ID will be negative e.g. `-100123456789`

---

## STEP 3 — Deploy the Bot (Free on Railway)

1. Go to **railway.app** → New Project → Deploy from GitHub
2. Upload these files or paste into a repo
3. Set environment variables in Railway dashboard:

```
TELEGRAM_BOT_TOKEN = your_token_from_step1
TELEGRAM_CHAT_ID   = your_chat_id_from_step2
WEBHOOK_SECRET     = make_up_any_password_eg_abc123
BOT_NAME           = Gemini 3 Pro Legacy Trading Bot
```

4. Railway gives you a public URL like:
   `https://your-bot-name.up.railway.app`

**Alternative free hosts:** Render.com, Fly.io, or a VPS

---

## STEP 4 — Configure TradingView Alert

1. Open TradingView → Create Alert on your chart
2. In **"Alert Actions"** → tick **Webhook URL**
3. Enter your webhook URL:
   `https://your-bot-name.up.railway.app/webhook?secret=YOUR_SECRET`
4. In the **Message box**, paste this JSON (edit TP/SL values):

```json
{
  "symbol": "{{ticker}}",
  "side": "Long",
  "entry": "{{close}}",
  "tp1": "78925",
  "tp2": "83418",
  "tp3": "84636",
  "sl": "68873",
  "timeframe": "{{interval}}",
  "note": "4H Fib breakout confirmed"
}
```

5. Click **Create** — every time alert fires, Telegram gets the signal!

---

## STEP 5 — Test It

Visit in your browser:
`https://your-bot-name.up.railway.app/test`

You should get a sample signal posted to your Telegram immediately.

---

## Sample Output in Telegram

```
🤖 Gemini 3 Pro Legacy Trading Bot
━━━━━━━━━━━━━━━━━━━━
🟢 NEW SIGNAL — BTCUSDT
━━━━━━━━━━━━━━━━━━━━
📌 Direction: Long
💰 Entry: $74060
⏱ Timeframe: 4H

🎯 Take Profit 1: $78925
🎯 Take Profit 2: $83418
🎯 Take Profit 3: $84636
🛑 Stop Loss: $68873
━━━━━━━━━━━━━━━━━━━━
📝 0.382 Fib breakout confirmed ✅
🕐 2026-03-16 02:20 UTC

⚠️ Trade at your own risk. DYOR.
```

---

## Running Locally (for testing)

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export WEBHOOK_SECRET="your_secret"
python bot.py
```

Then test with:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"Long","entry":"74060","tp1":"78925","sl":"68873","timeframe":"4H"}'
```

---

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Main bot server |
| `requirements.txt` | Python dependencies |
| `tradingview_alert_templates.json` | Copy-paste alert JSON templates |
| `README.md` | This guide |
