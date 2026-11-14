import os
import html
import asyncio
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
PROFILE = os.getenv("PROFILE", "")

if not TOKEN or not OWNER_ID or not PROFILE:
    raise RuntimeError("Не заданы BOT_TOKEN, OWNER_ID или PROFILE")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Бот работает!\n\n"
        "Команда для оффера:\n"
        "/price ССЫЛКА @username ЦЕНА"
    )


@dp.message(Command("id"))
async def get_id(message: Message):
    await message.answer(
        f"Твой Telegram ID: <code>{message.from_user.id}</code>"
    )


@dp.message(Command("price"))
async def price(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("У тебя нет доступа.")
        return

    args = (message.text or "").split(maxsplit=3)

    if len(args) != 4:
        await message.answer(
            "Формат команды:\n"
            "/price ССЫЛКА_НА_ПОДАРОК @username ЦЕНА"
        )
        return

    _, gift_url, username, stars = args

    try:
        stars = int(stars)
        if stars <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Цена должна быть положительным числом.")
        return

    parsed = urlparse(gift_url)
    if parsed.scheme != "https" or not parsed.netloc:
        await message.answer("Укажи корректную HTTPS-ссылку на подарок.")
        return

    if not username.startswith("@") or len(username) < 2:
        await message.answer("Укажи username в формате @username.")
        return

    text = (
        f"Пользователь {html.escape(username)}\n\n"
        f"предложил вам\n\n"
        f"<b>{stars} ⭐</b>\n\n"
        f"за ваш <a href=\"{html.escape(gift_url, quote=True)}\">подарок</a>.\n\n"
        f"⚠️ Будьте осторожны"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Принять",
                    url=PROFILE
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отклонить",
                    callback_data="decline"
                )
            ]
        ]
    )

    try:
        await message.answer(
            text,
            reply_markup=keyboard
        )
    except Exception:
        await message.answer("Не удалось отправить оффер. Проверь настройки.")


@dp.callback_query(F.data == "decline")
async def decline(callback: CallbackQuery):
    await callback.answer("Предложение отклонено!")
    await callback.message.edit_reply_markup(reply_markup=None)


async def main():
    print("OfferBot запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
