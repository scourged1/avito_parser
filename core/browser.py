from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from contextlib import asynccontextmanager
from config.settings import BROWSER_ARGS, logger

class BrowserManager:
    def __init__(self):
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    async def init_browser(self):
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    *BROWSER_ARGS,
                    '--disable-notifications',
                    '--disable-extensions',
                    '--no-default-browser-check',
                    '--disable-site-isolation-trials',
                    '--disable-features=site-per-process',
                    '--disable-web-security'
                ]
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                java_script_enabled=True,
                ignore_https_errors=True,
                locale='ru-RU',
                timezone_id='Europe/Moscow',
                geolocation={'latitude': 55.7558, 'longitude': 37.6173},
                permissions=['geolocation'],
                bypass_csp=True
            )
            await self._setup_stealth_mode()

    async def _setup_stealth_mode(self):
        await self.context.add_init_script("""
            const newProto = navigator.__proto__;
            delete newProto.webdriver;
            navigator.__proto__ = newProto;
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            Object.defineProperties(navigator, {
                webdriver: {
                    get: () => undefined,
                    configurable: true
                },
                languages: {
                    get: () => ['ru-RU', 'ru', 'en-US', 'en'],
                    configurable: true
                },
                plugins: {
                    get: () => [
                        { name: 'Chrome PDF Plugin' },
                        { name: 'Chrome PDF Viewer' },
                        { name: 'Native Client' },
                        { name: 'Chromium PDF Viewer' }
                    ],
                    configurable: true
                },
                platform: { get: () => 'Win32' },
                hardwareConcurrency: { get: () => 8 },
                deviceMemory: { get: () => 8 },
                maxTouchPoints: { get: () => 0 }
            });
            
            // Prevent iframe detection
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    return window;
                }
            });
            
            // Override toString methods
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)

    async def _setup_page(self, page: Page):
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        })

    @asynccontextmanager
    async def get_page(self) -> Page:
        if not self.browser:
            await self.init_browser()
        
        page = await self.context.new_page()
        try:
            await self._setup_page(page)
            yield page
        finally:
            await page.close()

    async def shutdown(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    # Add other browser-related methods here... 