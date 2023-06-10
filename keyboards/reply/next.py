from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def next_button() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton("Далее"))
    return keyboard
