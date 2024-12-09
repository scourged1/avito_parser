import asyncio
import random
from typing import Dict, Set, List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.ad import AdInfo
from config.settings import CHECK_INTERVAL, MAX_RETRIES, logger

class AvitoTracker:
    def __init__(self, bot, parser):
        self.bot = bot
        self.parser = parser
        self.tracked_links: Dict[int, str] = {}
        self.last_seen_ads: Dict[int, Set[str]] = {}

    async def check_new_ads(self):
        for chat_id, url in self.tracked_links.items():
            if not url:
                continue

            try:
                current_ads, _ = await self._get_ads_with_retry(url)
                if not current_ads:
                    continue

                await self._process_new_ads(chat_id, current_ads)
            except Exception as e:
                logger.error(f"Ошибка при проверке объявлений: {e}")

    async def _get_ads_with_retry(self, url: str) -> tuple[List[AdInfo], str]:
        for attempt in range(MAX_RETRIES):
            try:
                # Clean URL
                base_url = url.split('?')[0]
                params = url.split('?')[1].split('&') if '?' in url else []
                cleaned_params = [p for p in params if not p.startswith('context=')]
                cleaned_url = f"{base_url}?{'&'.join(cleaned_params)}" if cleaned_params else base_url
                
                result = await self.parser.parse_ads(cleaned_url)
                if result and result[0]:  # If we got ads
                    return result
                logger.info(f"Попытка {attempt + 1} из {MAX_RETRIES} не удалась")
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(10)
        return [], "0"

    async def _process_new_ads(self, chat_id: int, current_ads: List[AdInfo]):
        old_urls = self.last_seen_ads.get(chat_id, set())
        new_ads = [ad for ad in current_ads if ad.url not in old_urls]
        
        if new_ads:
            for ad in new_ads:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти к объявлению", url=ad.url)]
                ])
                
                message_text = (
                    f"📌 *{ad.title}*\n\n"
                    f"📅 _{ad.date}_\n"
                    f"💰 {ad.price}"
                )
                
                try:
                    if ad.image_url:
                        await self.bot.send_photo(
                            chat_id,
                            ad.image_url,
                            caption=message_text,
                            reply_markup=keyboard,
                            parse_mode="Markdown"
                        )
                    else:
                        await self.bot.send_message(
                            chat_id,
                            message_text,
                            reply_markup=keyboard,
                            disable_web_page_preview=True,
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"Failed to send ad: {e}")
                    # Fallback to text-only message if image fails
                    await self.bot.send_message(
                        chat_id,
                        message_text,
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                        parse_mode="Markdown"
                    )
                
                await asyncio.sleep(1)
        
        self.last_seen_ads[chat_id] = set(ad.url for ad in current_ads)

    async def scheduler(self):
        while True:
            try:
                if self.tracked_links:
                    await self.check_new_ads()
                await asyncio.sleep(
                    random.uniform(CHECK_INTERVAL[0], CHECK_INTERVAL[1])
                )
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(30)