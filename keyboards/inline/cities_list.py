from telebot import types


def cities_keyboard(cities):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for location in cities:
        city_name = location['city_name']
        keyboard.add(types.KeyboardButton(text=city_name))
    return keyboard
