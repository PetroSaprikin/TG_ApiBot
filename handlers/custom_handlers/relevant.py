from telebot.types import Message
from states.low_prices_states import LowPricesState
from site_api.core import headers, querystring, querystring1, url, url1

from loader import bot
import requests

params = {}
headers = headers
querystring = querystring
querystring1 = querystring1
querystring["sort_order"] = "PRICE_RELEVANT"


@bot.message_handler(commands=["high"])
def bot_low(message: Message) -> None:
    bot.set_state(message.from_user.id, LowPricesState.city, message.chat.id)
    bot.send_message(message.from_user.id, "Введите нужный город")


@bot.message_handler(state=LowPricesState.city)
def city(message: Message) -> None:
    if message.text.isalpha():
        params['city'] = message.text
        bot.set_state(message.from_user.id, LowPricesState.checkin_date, message.chat.id)
        bot.send_message(message.chat.id, "Введите дату заселения (в формате гггг-мм-дд)")
        querystring1["query"] = message.text
        response = requests.get(url1, headers=headers, params=querystring1)
        querystring["region_id"] = response.json()["data"][0]["gaiaId"]
    else:
        bot.send_message(message.from_user.id, "Попробуйте еще раз")


@bot.message_handler(state=LowPricesState.checkin_date)
def checkin_date(message: Message):
    check = message.text.split("-")
    if len(check) == 3 and len(check[0]) == 4 and len(check[1]) == 2 and len(check[2]) == 2:
        if 1 < int(check[1]) < 12 and 1 <= int(check[2]) <= 31:
            params['checkin_date'] = message.text
            bot.set_state(message.from_user.id, LowPricesState.checkout_date, message.chat.id)
            bot.send_message(message.chat.id, "Введите дату выселения (в формате гггг-мм-дд)")
            querystring["checkin_date"] = message.text
    else:
        bot.send_message(message.chat.id, "Введите дату заселения еще раз (в формате гггг-мм-дд)")


@bot.message_handler(state=LowPricesState.checkout_date)
def checkout_date(message: Message):
    check = message.text.split("-")
    if len(check) == 3 and len(check[0]) == 4 and len(check[1]) == 2 and len(check[2]) == 2:
        if 1 < int(check[1]) < 12 and 1 <= int(check[2]) <= 31:
            params['checkout_date'] = message.text
            bot.set_state(message.from_user.id, LowPricesState.results_amount, message.chat.id)
            bot.send_message(message.chat.id, "Теперь введите искомое кол-во результатов от 1 до 10ти")
            querystring["checkout_date"] = message.text
    else:
        bot.send_message(message.chat.id, "Введите дату выселения еще раз (в формате гггг-мм-дд)")


@bot.message_handler(state=LowPricesState.results_amount)
def results(message: Message):
    if message.text.isdigit():
        bot.send_message(message.chat.id, f"Город: {params['city']}\n"
                                          f"Дата заселения: {params['checkin_date']}\n"
                                          f"Дата выселения: {params['checkout_date']}")
        response = requests.get(url, headers=headers, params=querystring)
        if 0 < int(message.text) <= 10:
            for _ in range(int(message.text)):
                try:
                    result = response.json()
                    hotel = result["properties"][_]["name"]
                    price = result["properties"][_]["mapMarker"]["label"]
                    location = result["properties"][_]["neighborhood"]["name"]
                    bot.send_message(message.chat.id, f"Название отеля: {hotel}\n"
                                                      f"Цена номера: {price}\n"
                                                      f"Находится в: {location}")
                    bot.set_state(message.chat.id, LowPricesState.end, message.chat.id)
                except:
                    bot.send_message(message.chat.id, f"Выведено {_} результатов")
                    break
        else:
            bot.send_message(message.chat.id, "Вывожу 10 результатов")
            for _ in range(10):
                try:
                    bot.send_message(message.chat.id, response.json()["properties"][_]["name"])
                    bot.set_state(message.chat.id, LowPricesState.end, message.chat.id)
                except:
                    bot.send_message(message.chat.id, f"Выведено {_} результатов")
                    break
    else:
        bot.send_message(message.chat.id, "Нужно ввести число от 1 до 10ти")
