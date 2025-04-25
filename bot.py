import os
import logging
import openai
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler, MessageHandler,
    ContextTypes, RequestHandler, filters
)

# 🔐 Токены
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔧 Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📥 /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я готов отвечать, просто напиши!")

# 📥 Ответ на обычные сообщения
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
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Ошибка: {e}"

        await message.reply_text(reply)

# 🌐 aiohttp веб-приложение
async def main():
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)

    # 💡 Используем PTB RequestHandler
    async def handler(request):
        return await RequestHandler(application=app).handle(request)

    web_app = web.Application()
    web_app.router.add_post(f"/{BOT_TOKEN}", handler)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    logger.info("✅ Webhook-сервер запущен и слушает порт 10000")
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
