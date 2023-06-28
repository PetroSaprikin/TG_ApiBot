from telebot import types

from config_data.config import DEFAULT_COMMANDS


def help_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for command in DEFAULT_COMMANDS:
        callback_data = command[0]
        button_text = command[1]
        keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
    return keyboard


def command_button(command):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton("/" + command))
    return keyboard
