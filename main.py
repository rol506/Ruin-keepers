import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message

from SETTINGS import telegram_token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=telegram_token)

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if False: # если чел не зареган
        message_text = ('Здравствуйте! Это бот независимой организации "Хранители Руин". Через него менеджеры могут '
                        'взаимодействовать с записями пользователей и добавлять новые события. Введите ваш одноразовый '
                        'персональный код, чтобы получить доступ.')
        await bot.send_message(message.chat.id, message_text)
    else:
        await show_menu(message.chat.id)

async def show_menu(chat_id : int):
    message_text = 'Выберите действие через кнопки внизу.'
    buttons = [
        [KeyboardButton(text='Взаимодействие со списком участников')],
        [KeyboardButton(text='Взаимодействие со списком мероприятий')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons)

    await bot.send_message(chat_id, message_text, reply_markup=keyboard)

@dp.message()
async def receive_message(message: Message):
    if True: # если чел зареган
        message_text = None
        match message.text:
            case 'Назад':
                await show_menu(message.chat.id)
            case 'Взаимодействие со списком участников':
                message_text = 'Выберите действие.'
                buttons = [
                    [KeyboardButton(text='Записать участника на мероприятие'),
                     KeyboardButton(text='Выписать участника с мероприятия')],
                    [KeyboardButton(text='Назад')]
                ]
            case 'Взаимодействие со списком мероприятий':
                message_text = 'Выберите действие.'
                buttons = [
                    [KeyboardButton(text='Добавить мероприятие'),
                     KeyboardButton(text='Удалить мероприятие')],
                    [KeyboardButton(text='Назад')]
                ]
        if message_text is not None:
            await bot.send_message(message.chat.id, message_text, reply_markup=ReplyKeyboardMarkup(keyboard=buttons))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
