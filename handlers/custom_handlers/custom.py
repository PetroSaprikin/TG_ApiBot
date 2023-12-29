from telebot import types
import datetime

from telebot.types import CallbackQuery

from config_data.config import DEFAULT_COMMANDS
from keyboards.inline.count_hotel import get_count_hotel
from site_api.hotels_request import region_id_finder, request_hotels
from states.custom_state import CustomPriceState
from keyboards.inline.cities_list import cities_keyboard
from loader import bot, calendar, calendar_1_callback
from keyboards.inline.calendar import create_calendar


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message: types.Message):
    bot.send_message(message.chat.id, "Выполнение команды отменено!")
    bot.delete_state(message.from_user.id, message.chat.id)
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, "\n".join(text))


@bot.message_handler(commands=["custom"])
def take_city(message: types.Message):
    bot.set_state(message.from_user.id, CustomPriceState.city, message.chat.id)
    bot.send_message(message.from_user.id, "Вы решили в ручную задать диапазон цены и дистанцию до центра города.\n"
                                           "Прошу, введите в каком городе будет производится поиск.")


@bot.message_handler(state=CustomPriceState.city)
def choose_city(message):
    city_name = message.text
    if city_name.replace(" ", "").replace("-", "").isalpha():
        cities = region_id_finder(city_name)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            hotels_data["city_name"] = city_name
            hotels_data["cities_lst"] = cities
        keyboard = cities_keyboard(cities)
        bot.set_state(message.from_user.id, CustomPriceState.check_city, message.chat.id)
        bot.send_message(message.from_user.id, f"Уточните, пожалуйста, место назначения.", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Введите настоящее название города.\n"
                                               "Попробуйте еще раз.")


@bot.message_handler(state=CustomPriceState.check_city)
def city_check(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
        for destination in hotels_data["cities_lst"]:
            if destination["city_name"] == message.text:
                hotels_data["city_id"] = destination["destination_id"]
    bot.send_message(message.from_user.id, "Отлично, теперь введите дату заселения!")
    create_calendar(message)
    bot.set_state(message.from_user.id, CustomPriceState.check_in, message.chat.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=CustomPriceState.check_in
)
def callback_inline(call: types.CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    my_date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Ты выбрал эту дату: {my_date.strftime('%d.%m.%Y')}"
        )
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
            if datetime.date(int(year), int(month), int(day)) >= datetime.date.today():
                hotels_data['check_in'] = datetime.date(my_date.year, my_date.month, my_date.day)
                bot.send_message(call.message.chat.id, 'Теперь выбери дату выезда')
                create_calendar(call.message, hotels_data['check_in'])
                bot.set_state(call.message.chat.id, CustomPriceState.check_out)
            else:
                bot.send_message(call.message.chat.id, 'Некорректная дата! Попробуй еще раз')
                create_calendar(call.message)
    elif action == 'CANCEL':
        bot.send_message(call.message.chat.id, 'Выбери дату из календаря')
        create_calendar(call.message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=CustomPriceState.check_out
)
def callback_inline(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    my_date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Ты выбрал эту дату: {my_date.strftime('%d.%m.%Y')}"
        )
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
            if datetime.date(int(year), int(month), int(day)) >= hotels_data['check_in']:
                end_date = datetime.date(my_date.year, my_date.month, my_date.day)
                hotels_data['check_out'] = end_date
                hotels_data['total_days'] = end_date - hotels_data['check_in']
                bot.send_message(call.message.chat.id, 'Хорошо, теперь введите нижний порог цены за ночь в долларах.')
                bot.set_state(call.message.chat.id, CustomPriceState.price_min)
            else:
                bot.send_message(call.message.chat.id, 'Ты выезжаешь из отеля раньше, чем приезжаешь туда!')
                create_calendar(call.message, hotels_data['check_in'])

    elif action == 'CANCEL':
        bot.send_message(call.message.chat.id, 'Выбери дату из календаря')
        create_calendar(call.message)


@bot.message_handler(state=CustomPriceState.price_min)
def min_price(message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            hotels_data["price_min"] = int(message.text)
            bot.set_state(message.from_user.id, CustomPriceState.price_max, message.chat.id)
            bot.send_message(message.from_user.id, "Отлично, а теперь введи максимальную цену.")
    else:
        bot.send_message(message.from_user.id, "Цена должна быть целым числом!")


@bot.message_handler(state=CustomPriceState.price_max)
def max_price(message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            if hotels_data["price_min"] >= int(message.text):
                bot.send_message(message.from_user.id, "Максимальная цена должна быть больше минимальной!")
            else:
                hotels_data["price_max"] = int(message.text)
                bot.send_message(message.from_user.id,
                                 "А теперь введите максимально допустимую дистанцию от центра города. (в метрах)")
                bot.set_state(message.from_user.id, CustomPriceState.distance, message.chat.id)
    else:
        bot.send_message(message.from_user.id, "Цена должна быть целым числом!")


@bot.message_handler(state=CustomPriceState.distance)
def set_distance(message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as hotels_data:
            hotels_data["user_distance"] = int(message.text)
            bot.set_state(message.from_user.id, CustomPriceState.count_hotel, message.chat.id)
            bot.send_message(message.from_user.id, "Отлично, сколько результатов вывести?",
                             reply_markup=get_count_hotel())
    else:
        bot.send_message(message.from_user.id, "Дистанция должна быть целым числом в метрах!")


@bot.callback_query_handler(func=None, state=CustomPriceState.count_hotel)
def find_all_deals(call):
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data["hotels_count"] = int(call.data)
    data = request_hotels(call.message.chat.id, call.message.chat.id, is_reverse=False)
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        hotels_data["data_to_show"] = data
    bot.set_state(call.message.chat.id, CustomPriceState.info)
    show_info(call)


def show_info(call):
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as hotels_data:
        bot.send_message(call.message.chat.id, "Отлично, вот список отелей по возрастанию цены!")
        for hotel, hotel_info in hotels_data["data_to_show"].items():
            if hotels_data["user_distance"] > hotel_info["distance"]:
                bot.send_message(call.message.chat.id, f'Название отеля: {hotel}\n'
                                                       f'Примерная цена за период проживания:'
                                                       f' ${hotel_info["total_price"]}\n'
                                                       f'Рейтинг отеля: {hotel_info["rating"]}\n'
                                                       f'Расстояние до отеля: {hotel_info["distance"]}м\n'
                                                       f'Ссылка на отель: {hotel_info["linc"]}',
                                 disable_web_page_preview=True)
    bot.set_state(call.message.chat.id, None)
