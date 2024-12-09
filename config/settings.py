import logging

# Logging configuration
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "7963550037:AAG92rkQ3fTU9bxYbpI_1X4rSEMASo-CoxE"
CHECK_INTERVAL = (60, 90)  # Check interval in seconds (min, max)
MAX_RETRIES = 3
USE_PROXY = False

# Browser configuration
BROWSER_ARGS = [
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-setuid-sandbox',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process',
    '--disable-blink-features=AutomationControlled',
    '--start-maximized'
] 