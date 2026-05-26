 import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        url = "https://proxyapi.ru"
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Ты — Grok. Общайся в ироничном, дружелюбном и живом стиле. Отвечай кратко и по делу."},
                {"role": "user", "content": message.text}
            ]
        }
        response = requests.post(url, json=data).json()
        reply = response['choices']['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Ошибка связи с ИИ. Проверь баланс.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
