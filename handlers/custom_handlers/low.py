from telebot.types import Message
import requests

from states.low_prices_states import LowPricesState
from site_api.core import url1, url2, headers1, headers2, payload, querystring
from config_data.config import DEFAULT_COMMANDS
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
        bot.set_state(message.from_user.id, LowPricesState.checkin_date, message.chat.id)
        bot.send_message(message.chat.id, "Введите дату заселения (в формате гггг-мм-дд)")
        querystring["q"] = message.text
        response = requests.get(url2, headers=headers2, params=querystring)
        r_id = response.json()["sr"][0]["gaiaId"]
        payload["destination"]["regionId"] = r_id
    else:
        bot.send_message(message.from_user.id, "Попробуйте еще раз")


@bot.message_handler(state=LowPricesState.checkin_date)
def checkin_date(message: Message):
    check = message.text.split("-")
    if len(check) == 3 and len(check[0]) == 4 and len(check[1]) == 2 and len(check[2]) == 2:
        if 1 < int(check[1]) < 12 and 1 <= int(check[2]) <= 31:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data["checkin_date"] = message.text
            bot.set_state(message.from_user.id, LowPricesState.checkout_date, message.chat.id)
            bot.send_message(message.chat.id, "Введите дату выселения (в формате гггг-мм-дд)")
            payload["checkInDate"]["day"] = int(check[2])
            payload["checkInDate"]["month"] = int(check[1])
            payload["checkInDate"]["year"] = int(check[0])
    else:
        bot.send_message(message.chat.id, "Введите дату заселения еще раз (в формате гггг-мм-дд)")


@bot.message_handler(state=LowPricesState.checkout_date)
def checkout_date(message: Message):
    check = message.text.split("-")
    if len(check) == 3 and len(check[0]) == 4 and len(check[1]) == 2 and len(check[2]) == 2:
        if 1 < int(check[1]) < 12 and 1 <= int(check[2]) <= 31:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data["checkout_date"] = message.text
            bot.set_state(message.from_user.id, LowPricesState.results_amount, message.chat.id)
            bot.send_message(message.chat.id, "Теперь введите искомое кол-во результатов от 1 до 10ти")
            payload["checkOutDate"]["day"] = int(check[2])
            payload["checkOutDate"]["month"] = int(check[1])
            payload["checkOutDate"]["year"] = int(check[0])
    else:
        bot.send_message(message.chat.id, "Введите дату выселения еще раз (в формате гггг-мм-дд)")


@bot.message_handler(state=LowPricesState.results_amount)
def results(message: Message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            msg = (
                f"Город: {data['city']}\n"
                f"Дата заселения: {data['checkin_date']}\n"
                f"Дата выселения: {data['checkout_date']}"
            )
        bot.send_message(message.chat.id, msg)
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
