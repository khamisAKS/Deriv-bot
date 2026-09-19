hereimport os
import asyncio
import websockets
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

DERIV_TOKEN = os.getenv("DERIV_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running! Use /balance to check Deriv balance, /trade to trade.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089") as ws:
            await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
            auth = json.loads(await ws.recv())
            if "error" in auth:
                await update.message.reply_text(f"❌ Auth failed: {auth['error']['message']}")
                return
            await ws.send(json.dumps({"balance": 1}))
            res = json.loads(await ws.recv())
            bal = res.get("balance", {})
            await update.message.reply_text(f"💰 Balance: {bal.get('balance')} {bal.get('currency')}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
