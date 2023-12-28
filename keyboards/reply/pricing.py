from telebot import types


def pricing():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    pricing_lst = ["До 10ти долларов за ночь", "От 10ти до 20", "От 20ти до 30", "От 30ти и выше"]
    for price in pricing_lst:
        keyboard.add(types.KeyboardButton(text=price))
    return keyboard
