from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def create_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🟢 Запустить отслеживание"),
                KeyboardButton(text="🔴 Остановить отслеживание")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    ) 