import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Загружаем токены из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # <-- это твой URL на Render

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Ошибка: {e}"

    await update.message.reply_text(reply)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Устанавливаем Webhook
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Запускаем веб-сервер
    await app.start()
    await app.updater.start_polling()  # Можно удалить эту строку если захочешь

    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
