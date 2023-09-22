import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiopayok import Payok
from data.config import PAYOK_API_ID, PAYOK_SECRET_KEY, PAYOK_API_KEY, PAYOK_SHOP_ID


# Устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)

# Создаем экземпляр бота и диспетчера
bot = Bot(token="6471197281:AAEGdOS6ff92vcdIZ23QLwzSgMu1mbJ_efE")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

payok = Payok(api_id=PAYOK_API_ID,
                  api_key=PAYOK_API_KEY,
                  secret_key=PAYOK_SECRET_KEY,
                  shop=PAYOK_SHOP_ID)

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    from handlers import *
    import database.models as db
    db.connect()
    executor.start_polling(dp, skip_updates=True)

