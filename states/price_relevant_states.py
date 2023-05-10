from telebot.handler_backends import State, StatesGroup


class PriceRelevantState(StatesGroup):
    city = State()
    checkin_date = State()
    checkout_date = State()
    results_amount = State()
    end = State()
