from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.send_message(message.from_user.id, f"""
    Привет, {message.from_user.full_name}! Я - бот для поиска отелей. 
Что я умею:
1. Выбери команду, и ты сможешь узнать топ отелей по самым разным критериям! 
2. Также я скину тебе ссылку на него, и ты сможешь заказать себе номер прямо сейчас!
3. А еще я умею запоминать историю поиска отелей, и ты всегда найдешь понравившийся тебе отель в истории

Чтобы узнать все мои команды, введи /help
    """)
