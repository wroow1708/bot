import os
import telebot
import requests
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Чтение переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверяем наличие токенов
if not TELEGRAM_TOKEN or not OPENAI_KEY:
    raise ValueError("Переменные окружения TELEGRAM_TOKEN и OPENAI_KEY должны быть заданы")

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Обманка портов для поддержания бесплатного тарифа
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

# Запуск dummy-сервера
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

# Обработчик сообщений от пользователя
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # URL для ProxyAPI
        url = "https://api.proxyapi.ru"

        # Заголовки для запроса
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }

        # Данные для запроса
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Ты — Grok. Общайся в ироничном, дружелюбном и живом стиле. Отвечай кратко."},
                {"role": "user", "content": message.text}
            ]
        }

        # Лог отправляемых данных (опционально, для отладки)
        # print(f"Отправляем данные: {data}")

        # Запрос к ProxyAPI
        res = requests.post(url, headers=headers, json=data, timeout=10)

        # Если код ответа НЕ 200, обрабатываем ошибку
        if res.status_code != 200:
            bot.reply_to(message, f"Ошибка ProxyAPI (Код {res.status_code}): {res.text}")
            return

        # Ответ от API ProxyAPI
        response = res.json()
        reply = response['choices'][0]['message']['content']  # Извлекаем текст ответа

        # Отправляем ответ пользователю
        bot.reply_to(message, reply)
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Ошибка: Превышено время ожидания ответа от сервера.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка при запросе к ProxyAPI: {str(e)}")
    except KeyError as e:
        bot.reply_to(message, f"Ошибка обработки ответа от ProxyAPI: ключ {str(e)} не найден.")
    except Exception as e:
        bot.reply_to(message, f"Непредвиденная ошибка: {str(e)}")

# Основной запуск приложения
if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()  # Запуск HTTP-сервера в отдельном потоке
    bot.polling(none_stop=True)  # Запуск бота
