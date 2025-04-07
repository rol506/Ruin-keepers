import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from SETTINGS import telegram_token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=telegram_token)

dp = Dispatcher()

class CreateEvent (StatesGroup):
    name_state = State()
    description_state = State()
    time_state = State()

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

@dp.message(StateFilter(None))
async def receive_message(message: Message, state: FSMContext):
    if True: # если чел зареган
        message_text = None
        buttons = None
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
                     KeyboardButton(text='Удалить мероприятие'),
                     KeyboardButton(text='Изменить мероприятие')],
                    [KeyboardButton(text='Назад')]
                ]
            case 'Записать участника на мероприятие':
                pass
            case 'Выписать участника с мероприятия':
                pass
            case 'Добавить мероприятие':
                message_text = 'Введите название мероприятия.'
                await state.set_state(CreateEvent.name_state)
            case 'Удалить мероприятие':
                pass

        if message_text is not None:
            if buttons is not None:
                await bot.send_message(message.chat.id, message_text, reply_markup=ReplyKeyboardMarkup(keyboard=buttons))
            else:
                await bot.send_message(message.chat.id, message_text, reply_markup=None)

@dp.message(CreateEvent.name_state)
async def get_event_name(message: Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    await bot.send_message(message.chat.id, 'Введите описание мероприятия.')
    await state.set_state(CreateEvent.description_state)

@dp.message(CreateEvent.description_state)
async def get_event_description(message: Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    await bot.send_message(message.chat.id, 'Введите дату и время начала мероприятия.')
    await state.set_state(CreateEvent.time_state)

@dp.message(CreateEvent.time_state)
async def get_event_time(message: Message, state: FSMContext):
    await state.set_state(None)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
