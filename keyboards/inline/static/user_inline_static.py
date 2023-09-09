from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

# Покупка
buy = InlineKeyboardButton(text="Купить", callback_data='buy')
cancel = InlineKeyboardButton(text="Отмена", callback_data='cancel')

buy_cancel_markup = InlineKeyboardMarkup(row_width=1).add(buy, cancel)

# Профиль
balance_ = InlineKeyboardButton(text="💸 Пополнить баланс", callback_data='balance')
referal = InlineKeyboardButton(text="🤝 Реферальная система", callback_data='referal')
transfer = InlineKeyboardButton(text="💳 Поделиться балансом", callback_data='transfer')
history = InlineKeyboardButton(text="🛒 История покупок", callback_data='history')

account_inline_menu = InlineKeyboardMarkup(row_width=1).add(balance_, referal, transfer, history)

# Инфо
admin = InlineKeyboardButton(text="⚙️Админ", callback_data='admin', url='https://t.me/eitins')
tech_support = InlineKeyboardButton(text="🆘Тех. поддержка", callback_data='support')
manual = InlineKeyboardButton(text="📖Инструкция", callback_data='manual')
rules = InlineKeyboardButton(text="📜Правила", callback_data='rules')

info_inline_menu = InlineKeyboardMarkup(row_width=2).add(admin, tech_support, manual, rules)

# Оплата
cryptobot = InlineKeyboardButton(text="Cryptobot", callback_data='cryptobot')

pay_options_menu = InlineKeyboardMarkup(row_width=1).add(cryptobot)
# способы

btc = InlineKeyboardButton(text="BTC", callback_data='btc')
eth = InlineKeyboardButton(text="ETH", callback_data='eth')
bnb = InlineKeyboardButton(text="BNB", callback_data='bnb')
usdt = InlineKeyboardButton(text="USDT", callback_data='usdt')
busd = InlineKeyboardButton(text="BUSD", callback_data='busd')
usdc = InlineKeyboardButton(text="USDC", callback_data='usdc')
ton = InlineKeyboardButton(text="TON", callback_data='ton')
trx = InlineKeyboardButton(text="TRX", callback_data='trx')

currencies = InlineKeyboardMarkup(row_width=2).add(btc, eth, bnb, usdt, busd, usdc, ton, trx)
