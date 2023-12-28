from telebot import types


def custom_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    criteria_lst = ["По рейтингу", "По дистанции до центра города", "По диапазону цены"]
    for _ in criteria_lst:
        keyboard.add(types.KeyboardButton(text=_))
    return keyboard
