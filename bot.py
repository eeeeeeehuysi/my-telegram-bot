import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ------------------ ТВОЇ ТОКЕНИ ------------------
BOT_TOKEN = "8658055907:AAHpAd8cDqeiTwWuof2lDtLNn2GSKJcWWTM"
CRYPTO_API_TOKEN = "542753:AAkt1zCJ0Hrz1oBZyhD5vzUNUfV5vf5Uelt"
# -------------------------------------------------

PRODUCT_NAME = "рецепт"
PRODUCT_PRICE = 3  # ціна в USDT
CRYPTO_API_URL = "https://pay.crypt.bot/api/createInvoice"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def create_invoice():
    headers = {"Crypto-Pay-API-Token": CRYPTO_API_TOKEN}
    payload = {"asset": "USDT", "amount": PRODUCT_PRICE}

    async with aiohttp.ClientSession() as session:
        async with session.post(CRYPTO_API_URL, json=payload, headers=headers) as resp:
            data = await resp.json()
            return data["result"]["invoice_id"], data["result"]["pay_url"]

async def check_payment(invoice_id):
    headers = {"Crypto-Pay-API-Token": CRYPTO_API_TOKEN}
    payload = {"invoice_ids": [invoice_id]}

    async with aiohttp.ClientSession() as session:
        async with session.post("https://pay.crypt.bot/api/getInvoices", json=payload, headers=headers) as resp:
            data = await resp.json()
            return data["result"]["items"][0]["status"]

# ------------------ СТАРТ ------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Купить", callback_data="buy")]
    ])
    await message.answer(f"Товар: {PRODUCT_NAME}\nЦена: {PRODUCT_PRICE} USDT", reply_markup=keyboard)

# ------------------ ОБРОБКА КНОПКИ ------------------
@dp.callback_query(lambda c: c.data == "buy")
async def buy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    invoice_id, pay_url = await create_invoice()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=pay_url)]
    ])
    await callback.message.answer("Нажмите кнопку ниже для оплаты:", reply_markup=keyboard)

    # Перевірка оплати кожні 10 секунд
    while True:
        await asyncio.sleep(10)
        status = await check_payment(invoice_id)
        if status == "paid":
            await bot.send_message(user_id, "✅ Оплата получена! Сейчас отправляем ваш файл...")
            await bot.send_document(user_id, open("product.jpg", "rb"))  # ТВОЄ ФОТО
            break

    await callback.answer()

# ------------------ ГОЛОВНА ФУНКЦІЯ ------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())