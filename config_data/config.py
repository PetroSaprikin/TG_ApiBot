import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("low", "Результаты поиска по возрастанию цены"),
    ("high", "Результаты поиска по убыванию цены"),
    ("custom", "Настраиваемый поиск номеров"),
    ("history", "История последних запросов"),
    ("cancel", "Отметить выполнение команды")
)
