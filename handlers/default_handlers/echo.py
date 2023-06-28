from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message):
    bot.reply_to(message, f"Введи любую команду из меню, чтобы я начал работать\n"
                          f"Чтобы узнать все мои команды, введи /help")
