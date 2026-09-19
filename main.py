import asyncio, json, os, websockets
from collections import deque
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

DERIV_TOKEN = os.environ.get("DERIV_TOKEN", "pat_e0622b96654eaac7105469a93c456a1111f593099e97ba558045d52dceabb177")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SYMBOL = "R_75"
STAKE = 0.35
is_running = False
ticks = deque(maxlen=10)

async def trading_loop(bot_app):
    global is_running, ticks
    uri = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
                await ws.recv()
                await ws.send(json.dumps({"ticks": SYMBOL}))
                while True:
                    msg = json.loads(await ws.recv())
                    if "tick" not in msg: continue
                    price = float(msg["tick"]["quote"])
                    ticks.append(price)
                    if not is_running or len(ticks) < 3: continue
                    if ticks[0] < ticks[1] < ticks[2]: d="CALL"
                    elif ticks[0] > ticks[1] > ticks[2]: d="PUT"
                    else: continue
                    await ws.send(json.dumps({"buy":1,"price":STAKE,"parameters":{"amount":STAKE,"basis":"stake","contract_type":d,"currency":"USD","duration":1,"duration_unit":"t","symbol":SYMBOL}}))
                    await asyncio.sleep(3)
        except Exception as e:
            print(f"Reconnect {e}")
            await asyncio.sleep(5)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    is_running = True
    await update.message.reply_text(f"✅ Bot STARTED on {SYMBOL} | Stake ${STAKE}")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    is_running = False
    await update.message.reply_text("🛑 Bot STOPPED")

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    asyncio.create_task(trading_loop(app))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

asyncio.run(main())
