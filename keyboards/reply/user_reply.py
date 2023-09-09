from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


# Главное меню
buy = KeyboardButton("☎️Купить")
account = KeyboardButton("👤Профиль")
info = KeyboardButton("ℹ️Инфо")

main_reply_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(buy, account, info)
