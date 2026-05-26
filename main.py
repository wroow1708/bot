import os
import telebot
import requests
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Читаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверяем наличие необходимых переменных окружения
if not TELEGRAM_TOKEN or not OPENAI_KEY:
    raise ValueError("Переменные окружения TELEGRAM_TOKEN и OPENAI_KEY должны быть заданы")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Обманка портов для удержания бесплатного тарифа Render
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

# Обработчик входящих сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # URL и заголовки для Proxy API
        url = "https://api.proxyapi.ru/openai/v1/completions"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",  # Добавляем корректный Bearer Token
            "Content-Type": "application/json"
        }
        
        # Формируем данные для отправки
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Ты — Grok. Общайся в ироничном, дружелюбном и живом стиле. Отвечай кратко."},
                {"role": "user", "content": message.text}
            ]
        }
        
        # Делаем POST-запрос с тайм-аутом в 10 секунд
        res = requests.post(url, headers=headers, json=data, timeout=10)
        
        # Если статус-код НЕ 200, обрабатываем ошибку
        if res.status_code != 200:
            bot.reply_to(message, f"Ошибка ProxyAPI (Код {res.status_code}): {res.text}")
            return
        
        # Распаковываем JSON и забираем ответ модели
        response = res.json()
        reply = response['choices'][0]['message']['content']  # Забираем первый ответ
        
        # Отправляем ответ пользователю
        bot.reply_to(message, reply)
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Ошибка: Превышено время ожидания ответа от сервера.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка при запросе к ProxyAPI: {str(e)}")
    except KeyError as e:
        bot.reply_to(message, f"Ошибка обработки ответа от ProxyAPI: ключ {str(e)} не найден")
    except Exception as e:
        bot.reply_to(message, f"Непредвиденная ошибка: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()  # Запуск HTTP-сервера в отдельном потоке
    bot.polling(none_stop=True)  # Запуск бота
