import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# 🔑 Ключи
openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # должен включать токен в конце

# 🔹 Обработка команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я очень умный бот АрмянГПТ. Обращайся ко мне — отвечу!")

# 🔹 Обработка текстов — если обращаются к боту
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    chat_type = message.chat.type
    bot_username = (await context.bot.get_me()).username

    text = message.text or ""

    # Если это личный чат или есть упоминание бота — отвечаем
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

# 🔧 Запуск через Webhook
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Устанавливаем Webhook и запускаем сервер
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL
    )
