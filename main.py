import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from config import BOT_TOKEN, GROUP_ID, MANAGEMENT_GROUP_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {}

QUESTIONS = [
    ("telegram_username", "📲 What is your Telegram username?"),
    ("store_name", "🏪 What is the store name, including the domain?"),
    ("order_total", "💰 What is the order total?"),
    ("order_date", "📅 What is the order date?"),
    ("delivery_date", "📦 What is the delivery date?"),
    ("order_number", "🧾 What is the order number?"),
    ("items_ordered", "🛍️ What items were ordered?"),
    ("tracking", "🚚 What is the tracking number and courier?"),
    ("name_on_order", "👤 What name was used on the order?"),
    ("email_on_order", "📧 What email was used on the order?"),
    ("store_password", "🔐 What is the store password? (Type N/A if not required)"),
    ("phone_on_order", "📞 What phone number was used on the order?"),
    ("shipping_address", "📍 What is the full shipping address?"),
    ("billing_address", "🧾 What is the full billing address?")
]


def build_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 In Process", callback_data="status:in_process"),
                InlineKeyboardButton(text="⏳ Waiting", callback_data="status:waiting"),
            ],
            [
                InlineKeyboardButton(text="✅ Done", callback_data="status:done"),
                InlineKeyboardButton(text="❌ Failed", callback_data="status:failed"),
            ],
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id

    user_data[user_id] = {
        "step": 0,
        "answers": {}
    }

    intro_text = (
        "✅ Order Submission Form\n\n"
        "Welcome.\n\n"
        "Please complete this form only once your order has been successfully delivered.\n\n"
        "To process your submission correctly, you will be asked all required order details one question at a time.\n\n"
        "Please answer carefully and make sure all information provided is accurate.\n\n"
        "You may now begin.\n"
    )

    await message.answer(intro_text)
    await message.answer(QUESTIONS[0][1])


@dp.message()
async def handle_form(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    current_step = user_data[user_id]["step"]
    answers = user_data[user_id]["answers"]

    field_name, _ = QUESTIONS[current_step]
    answers[field_name] = message.text

    current_step += 1
    user_data[user_id]["step"] = current_step

    if current_step < len(QUESTIONS):
        await message.answer(QUESTIONS[current_step][1])
        return

    summary_text = (
        "📥 New Order Submission\n\n"
        f"📲 Telegram Username: {answers['telegram_username']}\n"
        f"🏪 Store Name: {answers['store_name']}\n"
        f"💰 Order Total: {answers['order_total']}\n"
        f"📅 Order Date: {answers['order_date']}\n"
        f"📦 Delivery Date: {answers['delivery_date']}\n"
        f"🧾 Order Number: {answers['order_number']}\n"
        f"🛍️ Items Ordered: {answers['items_ordered']}\n"
        f"🚚 Tracking / Courier: {answers['tracking']}\n"
        f"👤 Name on Order: {answers['name_on_order']}\n"
        f"📧 Email on Order: {answers['email_on_order']}\n"
        f"🔐 Store Password: {answers['store_password']}\n"
        f"📞 Phone on Order: {answers['phone_on_order']}\n"
        f"📍 Shipping Address: {answers['shipping_address']}\n"
        f"🧾 Billing Address: {answers['billing_address']}\n"
    )

    await bot.send_message(GROUP_ID, summary_text)

    try:
        await bot.send_message(
            MANAGEMENT_GROUP_ID,
            summary_text,
            reply_markup=build_keyboard()
        )
    except Exception as e:
        print(f"Erro ao enviar para grupo de gestão: {e}")

    await message.answer(
        "✅ Thank you for the order submission.\n\n"
        "Joker team will reach you out soon for more details."
    )

    del user_data[user_id]


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
