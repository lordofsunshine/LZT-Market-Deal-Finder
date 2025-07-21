import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from colorama import init, Fore, Style

from utils.config import ConfigManager
from utils.database import Database
from services.lolz_api import LolzAPI
from services.monitoring import MonitoringService
from utils.handlers import router

init(autoreset=True)


class ColorFormatter(logging.Formatter):
    def format(self, record):
        colors = {
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED + Style.BRIGHT
        }
        color = colors.get(record.levelno, Fore.WHITE)
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


async def main():
    config = ConfigManager.get_config()
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    bot = Bot(token=config['bot_token'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    
    db = Database(config['database_path'])
    await db.init_db()
    
    api = LolzAPI(config['lolz_api_token'])
    monitoring = MonitoringService(bot, db, api, config['check_interval_minutes'])
    
    dp['db'] = db
    dp['api'] = api
    dp['monitoring'] = monitoring
    
    print(f"{Fore.CYAN}Lolz Market Deal Finder запущен!")
    print(f"{Fore.BLUE}Интервал: {config['check_interval_minutes']} мин")
    
    await monitoring.start()
    
    try:
        await dp.start_polling(bot)
    finally:
        await monitoring.stop()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
