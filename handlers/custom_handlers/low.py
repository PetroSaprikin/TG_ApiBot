from telebot.types import Message
import requests
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from keyboards.reply.next import next_button
from states.low_prices_states import LowPricesState
from config_data.config import headers1, headers2
from site_api.core import url1, url2, payload, querystring
from config_data.config import DEFAULT_COMMANDS, times_check
from loader import bot


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    bot.send_message(message.chat.id, "Выполнение команды отменено!")
    bot.delete_state(message.from_user.id, message.chat.id)
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, "\n".join(text))


@bot.message_handler(commands=["low"])
def bot_low(message: Message) -> None:
    bot.set_state(message.from_user.id, LowPricesState.city, message.chat.id)
    bot.send_message(message.from_user.id, "Введите нужный город")


@bot.message_handler(state=LowPricesState.city)
def city(message: Message) -> None:
    if message.text.isalpha():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
        bot.set_state(message.from_user.id, LowPricesState.checkout_date, message.chat.id)
        querystring["q"] = message.text
        response = requests.get(url2, headers=headers2, params=querystring)
        r_id = response.json()["sr"][0]["gaiaId"]
        payload["destination"]["regionId"] = r_id
        bot.send_message(message.from_user.id, "Введите дату заселения")
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id,
                         f"Select {LSTEP[step]}",
                         reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, "Попробуйте еще раз")


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        times_check["day"] = int(result.strftime("%d"))
        times_check["month"] = int(result.strftime("%m"))
        times_check["year"] = int(result.strftime("%Y"))
        bot.edit_message_text(f"Выбранная дата: {result}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)


@bot.message_handler(state=LowPricesState.checkout_date)
def checkout_date(message: Message):
    payload["checkInDate"]["day"] = times_check["day"]
    payload["checkInDate"]["month"] = times_check["month"]
    payload["checkInDate"]["year"] = times_check["year"]
    bot.set_state(message.from_user.id, LowPricesState.results_amount, message.chat.id)
    bot.send_message(message.from_user.id, "Введите дату выселения")
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


@bot.message_handler(state=LowPricesState.results_amount)
def results(message: Message):
    payload["checkOutDate"]["day"] = times_check["day"]
    payload["checkOutDate"]["month"] = times_check["month"]
    payload["checkOutDate"]["year"] = times_check["year"]
    if message.text.isdigit():
        response = requests.post(url1, json=payload, headers=headers1)
        if 0 < int(message.text) <= 10:
            for _ in range(int(message.text)):
                try:
                    result = response.json()
                    hotel = result["data"]["propertySearch"]["properties"][_]['name']
                    price = result["data"]["propertySearch"]["properties"][_]['mapMarker']['label']
                    h_id = result["data"]["propertySearch"]["properties"][_]['id']
                    bot.send_message(message.chat.id, f"Название отеля: {hotel}\n"
                                                      f"Средняя цена: {price}\n"
                                                      f"Ссылка на отель: "
                                                      f"https://www.hotels.com/h{h_id}.Hotel-Information",
                                     disable_web_page_preview=True)
                    bot.set_state(message.chat.id, LowPricesState.end, message.chat.id)
                except:
                    bot.send_message(message.chat.id, f"Выведено {_} результатов")
                    break
        else:
            bot.send_message(message.chat.id, "Вывожу 10 результатов")
            for _ in range(10):
                try:
                    result = response.json()["data"]["propertySearch"]["properties"][_]
                    bot.send_message(message.chat.id, f"Название отеля: {result['name']}\n"
                                                      f"Средняя цена: {result['mapMarker']['label']}\n"
                                                      f"Ссылка на отель: "
                                                      f"https://www.hotels.com/h{result['id']}.Hotel-Information",
                                     disable_web_page_preview=True)
                    bot.set_state(message.chat.id, LowPricesState.end, message.chat.id)
                except:
                    bot.send_message(message.chat.id, f"Выведено {_} результатов")
                    break
    else:
        bot.send_message(message.chat.id, "Нужно ввести число от 1 до 10ти")
