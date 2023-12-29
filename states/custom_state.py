from telebot.handler_backends import State, StatesGroup


class CustomPriceState(StatesGroup):
    city = State()
    check_city = State()
    check_in = State()
    check_out = State()
    price_min = State()
    price_max = State()
    distance = State()
    count_hotel = State()
    info = State()
