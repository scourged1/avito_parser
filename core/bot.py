import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.tracker import AvitoTracker
from services.parser import AvitoParser
from core.browser import BrowserManager
from utils.keyboards import create_main_keyboard
from config.settings import BOT_TOKEN, logger
import random

class AvitoBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.browser = BrowserManager()
        self.parser = AvitoParser(self.browser)
        self.tracker = AvitoTracker(self.bot, self.parser)
        self._setup_handlers()

    def _setup_handlers(self):
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.stop_command, Command("stop"))
        self.dp.message.register(
            self.handle_url,
            lambda msg: msg.text and msg.text.startswith('http')
        )
        self.dp.message.register(
            self.handle_buttons,
            lambda msg: msg.text in ["🟢 Запустить отслеживание", "🔴 Остановить отслеживание"]
        )

    async def start_command(self, message: Message):
        chat_id = message.chat.id
        if chat_id not in self.tracker.tracked_links:
            self.tracker.tracked_links[chat_id] = None
            self.tracker.last_seen_ads[chat_id] = set()
        
        await message.reply(
            "Привет! Я бот для отслеживания объявлений на Авито.\n"
            "🔹 Нажмите «Запустить отслеживание» и отправьте мне ссылку на поиск Авито\n"
            "🔹 Используйте «Остановить отслеживание» чтобы прекратить отслеживание",
            reply_markup=create_main_keyboard()
        )

    async def stop_command(self, message: Message):
        chat_id = message.chat.id
        if chat_id not in self.tracker.tracked_links or not self.tracker.tracked_links[chat_id]:
            await message.reply("❌ У вас нет активных отслеживаний.")
            return
        
        url = self.tracker.tracked_links[chat_id]
        self.tracker.tracked_links[chat_id] = None
        if chat_id in self.tracker.last_seen_ads:
            self.tracker.last_seen_ads[chat_id].clear()
        
        await message.reply(
            f"✅ Отслеживание остановлено!\n"
            f"🔍 Ссылка: {url}"
        )

    async def handle_url(self, message: Message):
        chat_id = message.chat.id
        url = message.text.strip()
        
        if 'avito.ru' not in url:
            await message.reply(
                "❌ Пожалуйста, отправьте ссылку с сайта Авито.",
                reply_markup=create_main_keyboard()
            )
            return
        
        # Check if user already tracking something
        if self.tracker.tracked_links.get(chat_id):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Да", callback_data="replace_url"),
                InlineKeyboardButton(text="Нет", callback_data="keep_old_url")
            ]])
            await message.reply(
                "⚠️ У вас уже есть активное отслеживание. Хотите заменить его на новое?",
                reply_markup=keyboard
            )
            return
        
        processing_msg = await message.reply("⏳ Получил ссылку. Начинаю обработку...")
        
        try:
            for attempt in range(3):
                try:
                    # Clean URL
                    base_url = url.split('?')[0]
                    params = url.split('?')[1].split('&') if '?' in url else []
                    cleaned_params = [p for p in params if not p.startswith('context=')]
                    cleaned_url = f"{base_url}?{'&'.join(cleaned_params)}" if cleaned_params else base_url

                    async with self.browser.get_page() as page:
                        # First visit Avito homepage and emulate user behavior
                        await page.goto('https://www.avito.ru', 
                                    wait_until='domcontentloaded',
                                    timeout=15000)
                        await asyncio.sleep(random.uniform(1, 2))
                        
                        # Emulate mouse movements
                        for _ in range(random.randint(2, 4)):
                            await page.mouse.move(
                                random.randint(100, 800),
                                random.randint(100, 600),
                                steps=3
                            )
                            await asyncio.sleep(random.uniform(0.2, 0.5))

                        # Now navigate to the actual URL
                        await page.goto(
                            cleaned_url,
                            wait_until='domcontentloaded',
                            timeout=15000
                        )
                        
                        await asyncio.sleep(2)
                        
                        # Check for blocked/error pages
                        if any(x in page.url for x in ['blocked', 'error', 'captcha']):
                            raise Exception("Blocked or error page detected")
                        
                        try:
                            await page.wait_for_selector('div[data-marker="item"]', timeout=5000)
                        except Exception:
                            logger.error("No items found on page")
                            continue

                        content = await page.content()
                        initial_ads, total_count = await self.parser.extract_ads(content)

                        if initial_ads:
                            self.tracker.tracked_links[chat_id] = cleaned_url
                            self.tracker.last_seen_ads[chat_id] = set(ad.url for ad in initial_ads)
                            
                            await processing_msg.delete()
                            await message.reply(
                                f"✅ Начал отслеживать новые объявления!\n"
                                f"📊 Всего объявлений в категории: {total_count}",
                                reply_markup=create_main_keyboard()
                            )
                            return

                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == 2:
                        raise
            
            await processing_msg.delete()
            await message.reply(
                "❌ Не удалось найти объявления по этой ссылке.\n"
                "Пожалуйста, проверьте ссылку и попробуйте снова позже.",
                reply_markup=create_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Error in handle_url: {str(e)}")
            await processing_msg.delete()
            await message.reply(
                "❌ Произошла ошибка при обработке ссылки.\n"
                "Пожалуйста, попробуйте позже или используйте другую ссылку.",
                reply_markup=create_main_keyboard()
            )

    async def handle_buttons(self, message: Message):
        if message.text == "🟢 Запустить отслеживание":
            await message.reply(
                "Отправьте мне ссылку на поиск Авито, и я начну отслеживать новые объявления.",
                reply_markup=create_main_keyboard()
            )
        elif message.text == "🔴 Остановить отслеживание":
            await self.stop_command(message)

    async def start(self):
        logger.warning("Bot started successfully")
        try:
            await self.browser.init_browser()
            asyncio.create_task(self.tracker.scheduler())
            await self.dp.start_polling(self.bot)
        finally:
            await self.shutdown()

    async def shutdown(self):
        await self.browser.shutdown()
        await self.bot.session.close()
        logger.warning("Bot shutdown completed")