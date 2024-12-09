from bs4 import BeautifulSoup
from models.ad import AdInfo
from typing import List, Tuple
from config.settings import logger
import asyncio
import random

class AvitoParser:
    def __init__(self, browser):
        self.browser = browser

    @staticmethod
    async def extract_ads(content: str) -> Tuple[List[AdInfo], str]:
        soup = BeautifulSoup(content, 'html.parser')
        ads = []
        
        # Get total count
        total_count = "неизвестное количество"
        total_count_elem = (
            soup.find('span', {'data-marker': 'page-title/count'}) or
            soup.find('span', {'class': 'page-title-count-'}) or
            soup.find('span', {'class': 'page-title-count'})
        )
        if total_count_elem:
            total_count = total_count_elem.text.strip()
        
        # Check for empty results
        empty_result = soup.find('div', {'data-marker': 'empty-search'})
        if empty_result:
            logger.info("Empty search results found")
            return [], "0"

        # Find all ad items with multiple selectors
        items = []
        for selector in [
            {'data-marker': 'item'},
            {'class': 'iva-item-root'},
            {'class': 'items-items'}
        ]:
            items = soup.find_all('div', selector)
            if items:
                break
        
        logger.info(f"Found {len(items)} items on the page")
        
        for item in items:
            try:
                # Get title with multiple selectors
                title_elem = (
                    item.find('h3', {'itemprop': 'name'}) or
                    item.find('a', {'data-marker': 'item-title'}) or
                    item.find('div', {'class': 'title-root'})
                )
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                # Get date
                date_elem = item.find('div', {'data-marker': 'item-date'}) or item.find('p', {'data-marker': 'item-date'})
                date = date_elem.text.strip() if date_elem else "Дата не указана"

                # Get price
                price_elem = item.find('span', {'data-marker': 'item-price'}) or item.find('meta', {'itemprop': 'price'})
                if price_elem:
                    if price_elem.name == 'meta':
                        price = f"{price_elem.get('content', '').strip()} ₽"
                    else:
                        price = price_elem.text.strip()
                else:
                    price = "Цена не указана"

                # Get image URL
                image_url = None
                img_elem = item.find('img', {'itemprop': 'image'}) or item.find('img', {'data-marker': 'item-photo'})
                if img_elem:
                    for attr in ['src', 'data-src']:
                        if img_elem.has_attr(attr):
                            image_url = img_elem[attr]
                            if image_url.startswith('//'):
                                image_url = 'https:' + image_url
                            break

                # Get URL
                url = None
                if title_elem.name == 'a' and title_elem.has_attr('href'):
                    href = title_elem['href']
                    url = f"https://www.avito.ru{href}" if href.startswith('/') else href
                else:
                    link = item.find('a', {'data-marker': 'item-title'})
                    if link and link.has_attr('href'):
                        href = link['href']
                        url = f"https://www.avito.ru{href}" if href.startswith('/') else href

                if url:  # Only add if we have a valid URL
                    ads.append(AdInfo(title, date, price, url, image_url))
                    logger.info(f"Added ad: {title}")

            except Exception as e:
                logger.error(f"Error processing ad: {str(e)}")
                continue
        
        logger.info(f"Successfully extracted {len(ads)} ads")
        return ads, total_count

    async def parse_ads(self, url: str) -> Tuple[List[AdInfo], str]:
        """Parse ads from the given URL"""
        async with self.browser.get_page() as page:
            try:
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
                    url,
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
                    return [], "0"

                content = await page.content()
                return await self.extract_ads(content)
                
            except Exception as e:
                logger.error(f"Parse error: {str(e)}")
                return [], "0"