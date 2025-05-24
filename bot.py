import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.main_handlers import router
from handlers.main_handlers import check_personal_broadcasts
from config import BOT_TOKEN


bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)


async def main():
    try:
        print("Бот включен!")
        # Инициализация планировщика
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            check_personal_broadcasts,
            'cron',
            hour=10,
            minute=0,
            args=[bot]  # Передаем объект бота как аргумент
        )
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен!')