import os
import openai
import logging
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from aiohttp import web

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены
openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # с токеном в конце

# Обработчики
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я готов к работе.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    bot_username = (await context.bot.get_me()).username
    chat_type = message.chat.type
    text = message.text or ""

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

        await message.reply_text(reply)

# Основной запуск
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)

    # aiohttp вебсервер
    web_app = web.Application()
    web_app.add_routes([web.post(f"/{BOT_TOKEN}", app.webhook_handler())])
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    logger.info("✅ Webhook-сервер запущен на порту 10000")
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
