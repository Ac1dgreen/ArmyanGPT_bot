import os
import logging
import openai
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# 🔐 Ключи
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔧 Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я жив и готов отвечать :)")

# Обычные сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    bot_username = (await context.bot.get_me()).username
    chat_type = update.message.chat.type

    if chat_type == "private" or f"@{bot_username}" in text:
        prompt = text.replace(f"@{bot_username}", "").strip()
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Ошибка: {e}"
        await update.message.reply_text(reply)

# aiohttp handler
async def main():
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)

    async def handler(request):
        data = await request.json()
        await app._update_queue.put(data)
        return web.Response()

    web_app = web.Application()
    web_app.router.add_post(f"/{BOT_TOKEN}", handler)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    logger.info("✅ Webhook слушает порт 10000")
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
