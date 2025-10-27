import asyncio
import logging
from datetime import datetime
import logging

import aioschedule as aa
from time_mes import send_message_cron

from aiogram import Bot, Dispatcher

from config_data.config import Config, load_config
from handlers import other_handlers, admin_handlers
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Инициализируем логгер
from keyboards.set_menu import set_main_menu

logging.basicConfig(
    level=logging.DEBUG,
    filename="bot.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main() -> None:
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s'
    )
    # Выводим в консоль информацию о начале запуска
    logger.info('Starting BOTV')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()
    # Сообщения по расписанию
    aa.default_scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    aa.default_scheduler.add_job(send_message_cron, trigger='cron', hour=15,
                      minute=33, start_date=datetime.now(), kwargs={'bot': bot})
    aa.default_scheduler.start()
    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())