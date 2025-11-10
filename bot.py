import os
import pytz
from flask import Flask
from threading import Thread
from telegram.ext import Application
import asyncio
import logging
import random
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

#порти
app = Flask(__name__)

@app.route('/')
def home():
    return "bot is running"

def run_web():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
    
# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримання токена з змінних оточення
TOKEN = os.getenv("BOT_TOKEN", "8548946097:AAGIVqUh9GiQiytB5osyt3uMAaqCTPVF3lI")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "-1002927904845"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Зберігаємо ID всіх користувачів для привітань
user_ids = set()

# Міста Польщі для погоди
POLISH_CITIES = {
    "Варшава": {"temp": "15°C", "weather": "⛅ Хмарно"},
    "Краків": {"temp": "14°C", "weather": "🌦️ Невеликий дощ"},
    "Вроцлав": {"temp": "13°C", "weather": "☁️ Хмари"},
    "Гданськ": {"temp": "12°C", "weather": "🌧️ Дощ"},
    "Познань": {"temp": "14°C", "weather": "⛅ Хмарно"},
    "Лодзь": {"temp": "14°C", "weather": "☁️ Хмари"},
    "Щецин": {"temp": "11°C", "weather": "🌦️ Невеликий дощ"},
    "Битом": {"temp": "13°C", "weather": "⛅ Хмарно"},
    "Люблін": {"temp": "15°C", "weather": "☀️ Сонячно"},
    "Катовіце": {"temp": "13°C", "weather": "🌦️ Невеликий дощ"}
}

# 🔹 КОМАНДА /start
@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_ids.add(user_id)  # Зберігаємо ID користувача
    
    await message.answer(
        "👋 Привіт! Я багатофункціональний бот.Я був створений на двіжку kilnir.Та за допомогою Групіровки DDoM.\n\n"
        "📝 Щоб подати заявку - /apply\n"
        "🌤️ Щоб дізнатись погоду в Польщі - /tur\n"
        "🆘 SOS команда - /sos\n"
        "ℹ️ Довідка - /help"
    )

# 🔹 КОМАНДА /apply
@dp.message(Command("apply"))
async def apply_command(message: Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer(
        "📋 Надішли заявку в такому форматі:\n\n"
        "• Ім'я: ім'я\n"
        "• Номер телефону: має начинатись з + \n" 
        "• Юзернейм: @username\n"
        "• Соцмережа: посилання\n"
        "• Опис ситуації: детальний опис\n\n"
        "💡 Надішли все одним повідомленням!",
        reply_markup=remove_keyboard
    )

# 🔹 КОМАНДА /tur - погода
@dp.message(Command("tur"))
async def weather_command(message: Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=city) for city in list(POLISH_CITIES.keys())[i:i+3]]
            for i in range(0, len(POLISH_CITIES), 3)
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🌤️ Обери місто Польщі:", reply_markup=keyboard)

# 🔹 КОМАНДА /sos - спам в адмін-чат
@dp.message(Command("sos"))
async def sos_command(message: Message):
    user = message.from_user
    await message.answer("🆘 SOS сигнал надіслано адміністраторам групіровки DDoM!")
    
    # Спамимо в адмін-чат протягом 2 секунд
    end_time = asyncio.get_event_loop().time() + 2
    spam_count = 0
    
    while asyncio.get_event_loop().time() < end_time:
        try:
            sos_message = f"🚨 SOS від @{user.username or 'користувача'} (ID: {user.id}) - сос"
            await bot.send_message(ADMIN_CHAT_ID, sos_message)
            spam_count += 1
            await asyncio.sleep(0.1)  # Невелика затримка між повідомленнями
        except Exception as e:
            logger.error(f"Помилка під час спаму: {e}")
            break
    
    # Повідомляємо користувача про результат
    await message.answer(f"✅ SOS завершено! Відправлено {spam_count} повідомлень адміністраторам.")

# 🔹 ОБРОБКА ЗАЯВОК
@dp.message(F.text & ~F.text.startswith('/'))
async def handle_message(message: Message):
    text = message.text
    
    if len(text) > 30 or '\n' in text or any(word in text.lower() for word in ['ім\'я', 'телефон', 'номер']):
        # Це заявка
        user = message.from_user
        admin_message = f"📨 Заявка від @{user.username or 'користувача'}\n\n{text}"
        
        try:
            await bot.send_message(ADMIN_CHAT_ID, admin_message)
            await message.answer("✅ Заявка прийнята!Ми зв'яжемося з тобою.")
            logger.info(f"Нова заявка від @{user.username}")
        except Exception as e:
            await message.answer("❌ Помилка. Спробуй пізніше.")
    elif text in POLISH_CITIES:
        # Це погода
        weather_data = POLISH_CITIES[text]
        temp_variation = random.randint(-2, 2)
        base_temp = int(weather_data["temp"].replace("°C", ""))
        actual_temp = base_temp + temp_variation
        
        weather_info = (
            f"🌤️ Погода в {text}\n\n"
            f"🌡️ Температура: {actual_temp}°C\n"
            f"☁️ Умови: {weather_data['weather']}\n"
            f"💧 Вологість: {random.randint(60, 85)}%\n"
            f"🌬️ Вітер: {random.randint(2, 8)} м/с\n"
            f"🇵🇱 Місто в Польщі"
        )
        await message.answer(weather_info)

# 🔹 КОМАНДА /help
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "ℹ️ Доступні команди:\n\n"
        "/start - Початок роботи\n"
        "/apply - Подати заявку\n"
        "/tur - Погода в Польщі\n"
        "/sos - Екстрений виклик\n"
        "/help - Довідка"
    )

# 🔹 ЩОДЕННЕ ПРИВІТАННЯ О 6:00
async def send_morning_greetings():
    greeting_text = (
        "🌅 Доброго ранку.\n\n"
        "💖 Я радий що з вами все харашо.\n\n"
        "🌟 Харошого вам дня та приємних моментів🫂."
    )
    
    for user_id in list(user_ids):
        try:
            await bot.send_message(user_id, greeting_text)
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Не вдалося відправити привітання {user_id}")

async def schedule_greetings():
    while True:
        now = datetime.now(pytz.timezone('Europe/Kiev'))
        if now.hour == 6 and now.minute == 00:
            logger.info("Відправляю привітання...")
            await send_morning_greetings()
            await asyncio.sleep(60)
        await asyncio.sleep(30)

# 🔹 ЗАПУСК БОТА
async def main():
    logger.info("🟢 Бот запускається...")
    asyncio.create_task(schedule_greetings())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
