import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import BOT_TOKEN

# Устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)

# Создаем экземпляр бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    from handlers import *
    import database.models as db
    db.connect()
    executor.start_polling(dp, skip_updates=True)

