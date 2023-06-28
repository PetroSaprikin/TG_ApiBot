from loader import bot
from keyboards.inline.commands_list import help_keyboard, command_button
from config_data.config import DEFAULT_COMMANDS


def get_command_by_description(description):
    for command in DEFAULT_COMMANDS:
        if command[1] == description:
            return command[0]
    return None


@bot.message_handler(commands=['help'])
def help_handler(message):
    keyboard = help_keyboard()
    bot.send_message(message.chat.id, "Выберите команду:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(callback_query):
    command = callback_query.data
    keyboard = command_button(command)
    bot.send_message(callback_query.message.chat.id, f"Нажмите кнопку, а за тем можешь ее спрятать",
                     reply_markup=keyboard)
