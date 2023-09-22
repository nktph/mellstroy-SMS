from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_services_kb(page: list, number: int = 0, pages_count: int = 36):
    buttons = []
    for item in page:
        for key in item:
            buttons.append(InlineKeyboardButton(text=f"🔷 {item[key]}", callback_data=f"service {key}"))

    keyboard = InlineKeyboardMarkup(row_width=3).add(*buttons)

    left = number - 1 if number != 0 else pages_count-1
    right = number + 1 if number != pages_count-1 else 0

    left_button = InlineKeyboardButton("◀️", callback_data=f"tos {left}")
    page_button = InlineKeyboardButton(f"{number+1}/{pages_count}", callback_data="pagenumber")
    right_button = InlineKeyboardButton("▶️", callback_data=f"tos {right}")
    keyboard.row(left_button, page_button, right_button)
    return keyboard


async def get_operators_kb(operators: list):
    buttons = []
    for operator in operators:
        buttons.append(InlineKeyboardButton(text=f"{operator['name']} | {operator['cost']} RUB | {operator['count']} шт.",
                                            callback_data=f"oper {operator['name']} {operator['cost']}"))

    keyboard = InlineKeyboardMarkup(row_width=1).add(*buttons)

    return keyboard



async def get_countries_kb(page: list, number: int = 0, pages_count: int = 18):
    buttons = []
    for item in page:
        for key in item:
            buttons.append(InlineKeyboardButton(text=f"{item[key]}", callback_data=f"country {key}"))

    keyboard = InlineKeyboardMarkup(row_width=1).add(*buttons)

    left = number - 1 if number != 0 else pages_count - 1
    right = number + 1 if number != pages_count - 1 else 0

    left_button = InlineKeyboardButton("◀️", callback_data=f"toc {left}")
    page_button = InlineKeyboardButton(f"{number + 1}/{pages_count}", callback_data="pagenumber")
    right_button = InlineKeyboardButton("▶️", callback_data=f"toc {right}")
    keyboard.row(left_button, page_button, right_button)

    return keyboard


async def get_order_kb(order_id: str):
    check = InlineKeyboardButton(text="Проверить СМС", callback_data=f"check_order {order_id}")
    cancel = InlineKeyboardButton(text="Отменить заказ", callback_data=f"canc_order {order_id}")
    finish = InlineKeyboardButton(text="Завершить заказ (СМС получено)", callback_data=f"finish_order {order_id}")
    order_markup = InlineKeyboardMarkup(row_width=1).add(check, cancel, finish)
    return order_markup


async def get_cryptobot_currencies():
    currencies = ['BTC', 'ETH', 'BNB', 'USDT', 'BUSD', 'USDC', 'TON', 'TRX']
    buttons = []
    for c in currencies:
        btn = InlineKeyboardButton(text=c, callback_data=c.lower())
        buttons.append(btn)

    return InlineKeyboardMarkup(row_width=2).add(*buttons)


async def get_payok_currencies():
    currencies = ['RUB', 'UAH', 'USD', 'EUR', 'BTC', 'USDT', 'LTC', 'DOGE', 'ETH', 'TRX']
    buttons = []
    for c in currencies:
        btn = InlineKeyboardButton(text=c, callback_data=c)
        buttons.append(btn)

    return InlineKeyboardMarkup(row_width=2).add(*buttons)


async def get_payok_pay_btn(link: str):
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text="Оплатить", url=link))
