from aiogram.dispatcher.filters.state import State, StatesGroup


class StateWorker(StatesGroup):
    buy = State()
    order_confirmation = State()
    transfer = State()
    transfer_commit = State()
    dialog = State()
    dialog_support_reply = State()
    balance_method = State()
    balance_currency = State()
    balance_commit = State()
