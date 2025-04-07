import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from SETTINGS import telegram_token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=telegram_token)

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if True: # если чел зареган
        pass
    else:
        message_text = ('Здравствуйте! Это бот независимой организации "Хранители Руин". Через него менеджеры могут '
                        'взаимодействовать с записями пользователей и добавлять новые события. Введите ваш одноразовый '
                        'персональный код, чтобы получить доступ.')

        await bot.send_message(message.chat.id, message_text)
    await message.answer("Hello from RUIN KEEPERS EPTA")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
