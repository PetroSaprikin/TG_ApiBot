from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_count_hotel():

    dest = InlineKeyboardMarkup(row_width=5)
    buts_list = []
    for num in range(1, 11):
        buts_list.append(InlineKeyboardButton(text=str(num), callback_data=str(num)))
    dest.add(*buts_list)
    return dest
