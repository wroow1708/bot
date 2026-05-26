import os
import telebot
import requests
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Микро-сервер для обмана Render
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    # Render автоматически передает порт в переменную окружения PORT, по умолчанию 10000
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

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
    # Запускаем обманку в отдельном потоке
    Thread(target=run_server, daemon=True).start()
    # Запускаем самого бота
    bot.polling(none_stop=True)
