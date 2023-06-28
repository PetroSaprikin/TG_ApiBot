import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("low", "Топ самых дешевых отелей в городе"),
    ("high", "Топ самых дорогих отелей в городе"),
    ("custom", "Поиск отелей по параметрам пользователя"),
    ("history", "История последних запросов"),
    ("cancel", "Отменяет действие команды")
)
