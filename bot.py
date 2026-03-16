"""
Telegram Trading Signal Bot
Receives TradingView webhook alerts and posts formatted signals to Telegram
"""

from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────────
# CONFIGURATION — fill these in before running
# ─────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID_HERE")
WEBHOOK_SECRET     = os.getenv("WEBHOOK_SECRET",      "YOUR_SECRET_KEY_HERE")
BOT_NAME           = os.getenv("BOT_NAME",            "Gemini 3 Pro Legacy Trading Bot")
# ─────────────────────────────────────────────


def send_telegram_message(text: str) -> dict:
    """Send a message to the configured Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=10)
    return response.json()


def format_signal(data: dict) -> str:
    """
    Format a TradingView alert payload into a Telegram signal message.

    Expected TradingView alert JSON fields:
        symbol   — e.g. "BTCUSDT"
        side     — "Long" | "Short"
        entry    — entry price
        tp       — take profit price (or tp1/tp2/tp3)
        sl       — stop loss price
        timeframe (optional)
        note     (optional)
    """
    symbol    = data.get("symbol", "UNKNOWN").upper()
    side      = data.get("side", "Long").capitalize()
    entry     = data.get("entry", "—")
    sl        = data.get("sl", "—")
    timeframe = data.get("timeframe", "")
    note      = data.get("note", "")

    # Support single TP or multiple TPs
    tp1 = data.get("tp1") or data.get("tp", "—")
    tp2 = data.get("tp2")
    tp3 = data.get("tp3")

    side_emoji = "🟢" if side.lower() == "long" else "🔴"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"<b>🤖 {BOT_NAME}</b>",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"{side_emoji} <b>NEW SIGNAL — {symbol}</b>",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"📌 <b>Direction:</b> {side}",
        f"💰 <b>Entry:</b> ${entry}",
    ]

    if timeframe:
        lines.append(f"⏱ <b>Timeframe:</b> {timeframe}")

    lines.append("")
    lines.append(f"🎯 <b>Take Profit 1:</b> ${tp1}")
    if tp2:
        lines.append(f"🎯 <b>Take Profit 2:</b> ${tp2}")
    if tp3:
        lines.append(f"🎯 <b>Take Profit 3:</b> ${tp3}")

    lines += [
        f"🛑 <b>Stop Loss:</b> ${sl}",
        f"━━━━━━━━━━━━━━━━━━━━",
    ]

    if note:
        lines.append(f"📝 {note}")

    lines.append(f"🕐 {now}")
    lines.append("")
    lines.append("⚠️ <i>Trade at your own risk. DYOR.</i>")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook endpoint — TradingView posts here."""

    # Optional secret key check
    secret = request.args.get("secret") or request.headers.get("X-Secret")
    if WEBHOOK_SECRET and WEBHOOK_SECRET != "YOUR_SECRET_KEY_HERE":
        if secret != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401

    # Parse body
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Empty payload"}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    print(f"[WEBHOOK] Received: {json.dumps(data, indent=2)}")

    # Format and send
    message = format_signal(data)
    result  = send_telegram_message(message)

    if result.get("ok"):
        return jsonify({"status": "sent"}), 200
    else:
        print(f"[ERROR] Telegram error: {result}")
        return jsonify({"status": "error", "detail": result}), 500


@app.route("/test", methods=["GET"])
def test():
    """Quick test endpoint — sends a sample signal to Telegram."""
    sample = {
        "symbol":    "BTCUSDT",
        "side":      "Long",
        "entry":     "74060",
        "tp1":       "78925",
        "tp2":       "83418",
        "tp3":       "84636",
        "sl":        "68873",
        "timeframe": "4H",
        "note":      "0.382 Fib breakout confirmed ✅",
    }
    message = format_signal(sample)
    result  = send_telegram_message(message)
    return jsonify({"status": "ok" if result.get("ok") else "error", "telegram": result})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running", "bot": BOT_NAME}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🤖 {BOT_NAME} starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
