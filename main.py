import asyncio
from core.bot import AvitoBot
from config.settings import logger

def main():
    bot = AvitoBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == '__main__':
    main()
