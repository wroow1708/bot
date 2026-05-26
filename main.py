import telebot
import requests
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# ВСТАВЬТЕ СЮДА ВАШИ КЛЮЧИ ПРЯМО ВНУТРИ КАВЫЧЕК:
TELEGRAM_TOKEN = "8803743449:AAH4GHARlIezZzbZDJlbgyHNwkupDrvouWQ"
OPENAI_KEY = "sk-Rc4g8TixJPPhGeICh1NJ84727EKwPFb8"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Обманка для удержания бесплатного тарифа Render
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    import os
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
                {"role": "system", "content": "Ты — Grok. Общайся в ироничном, дружелюбном и живом стиле. Отвечай кратко."},
                {"role": "user", "content": message.text}
            ]
        }
        res = requests.post(url, json=data)
        
        # Если реселлер недоволен ключом или балансом, вы увидите ЧЕТКИЙ текст причины
        if res.status_code != 200:
            bot.reply_to(message, f"Ошибка ProxyAPI (Код {res.status_code}): {res.text}")
            return
            
        response = res.json()
        reply = response['choices']['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Ошибка в коде: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    bot.polling(none_stop=True)
