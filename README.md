# Avito Parser Bot

A Telegram bot for tracking new advertisements on Avito.ru. The bot monitors specified search URLs and notifies users about new listings in real-time.

## Features

- 🔍 Track multiple Avito search URLs
- ⚡ Real-time notifications about new listings
- 🖼️ Image preview support
- 🔄 Automatic updates with configurable intervals
- 🛡️ Anti-detection mechanisms
- 💬 User-friendly interface with keyboard controls

## Setup

1. Clone the repository:
\\\ash
git clone https://github.com/typewriter9000/avito_parser.git
cd avito_parser
\\\

2. Create and activate virtual environment:
\\\ash
python -m venv venv
# On Windows:
venv\\Scripts\\activate
# On Linux/Mac:
source venv/bin/activate
\\\

3. Install required packages:
\\\ash
pip install aiogram==3.2.0
pip install beautifulsoup4==4.12.2
pip install playwright==1.40.0
\\\

4. Install Playwright browsers:
\\\ash
playwright install chromium
\\\

5. Configure the bot:
   - Open \config/settings.py\
   - Replace \BOT_TOKEN\ with your Telegram bot token (get it from @BotFather)
   - Adjust \CHECK_INTERVAL\ if needed (default is 60-90 seconds)
   - Configure browser arguments in \BROWSER_ARGS\ if needed

6. Create project structure:
\\\
avito_parser/
├── config/
│   └── settings.py
├── core/
│   └── browser.py
├── models/
│   └── ad.py
├── services/
│   ├── parser.py
│   └── tracker.py
├── utils/
│   └── keyboards.py
└── main.py
\\\

## Usage

1. Start the bot:
\\\ash
python main.py
\\\

2. In Telegram:
   - Start a chat with your bot
   - Click "🟢 Запустить отслеживание"
   - Send an Avito search URL (e.g., https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyj_srok)
   - The bot will start tracking new listings and notify you about new ads

## Commands

- \/start\ - Initialize the bot and show main menu
- \/stop\ - Stop tracking current URL
- "🟢 Запустить отслеживание" - Start tracking new URL
- "🔴 Остановить отслеживание" - Stop tracking current URL

## Dependencies

- Python 3.9+
- aiogram 3.2.0 - Telegram Bot framework
- beautifulsoup4 4.12.2 - HTML parsing
- playwright 1.40.0 - Browser automation
- asyncio - Asynchronous I/O

## Error Handling

The bot includes several error handling mechanisms:
- Automatic retries for failed requests
- Anti-blocking measures
- Connection error recovery
- Graceful shutdown

## Notes

- The bot uses Playwright for browser automation to bypass Avito's anti-bot measures
- Multiple users can track different URLs simultaneously
- Images are automatically downloaded and sent with notifications
- The bot maintains a list of seen ads to avoid duplicate notifications

## License

MIT License

## Author

typewriter9000

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
