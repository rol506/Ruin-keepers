import datetime
import logging
import random
import time

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from SETTINGS import telegram_token

from FDataBase import FDataBase
from flsite import connect_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=telegram_token)
dp = Dispatcher()
db: FDataBase = FDataBase(connect_db())

class CreateEvent (StatesGroup):
    name_state = State()
    description_state = State()
    time_state = State()

# region Создание мероприятия

@dp.message(CreateEvent.name_state)
async def get_event_name(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(event_name=message.text)
        await bot.send_message(message.chat.id, 'Введите описание мероприятия.')
        await state.set_state(CreateEvent.description_state)

@dp.message(CreateEvent.description_state)
async def get_event_description(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(event_description=message.text)
        await bot.send_message(message.chat.id, 'Введите дату и время начала мероприятия.')
        await state.set_state(CreateEvent.time_state)

@dp.message(CreateEvent.time_state)
async def get_event_time(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.set_state(None)

# endregion

class RegisterUser (StatesGroup):
    event_state = State()
    name_state = State()
    telegram_state = State()
    phone_state = State()
    birth_state = State()

# region Регистрация пользователя

@dp.message(RegisterUser.name_state)
async def get_user_name(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(user_name=message.text)
        await bot.send_message(message.chat.id, 'Введите ID мероприятия, на которое хотите зарегистрировать этого пользователя.')
        await state.set_state(RegisterUser.event_state)

@dp.message(RegisterUser.event_state)
async def get_user_event(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            await state.update_data(user_event=int(message.text))
            await bot.send_message(message.chat.id, 'Введите телеграм этого пользователя.')
            await state.set_state(RegisterUser.telegram_state)
        else:
            await bot.send_message(message.chat.id, 'ID должен состоять только из цифр, попробуйте ещё раз.')

@dp.message(RegisterUser.telegram_state)
async def get_user_telegram(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(user_telegram=message.text)
        await bot.send_message(message.chat.id, 'Введите номер телефона этого пользователя.')
        await state.set_state(RegisterUser.phone_state)

@dp.message(RegisterUser.phone_state)
async def get_user_phone(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(user_phone=message.text)
        await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг".')
        await state.set_state(RegisterUser.birth_state)

@dp.message(RegisterUser.birth_state)
async def get_user_birth(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        birth = await parse_date(message.text)
        if birth is not None:
            data = await state.get_data()

            await bot.send_message(message.chat.id, f'{data['user_name']} успешно зарегистрирован(а) на мероприятие с ID {data['user_event']}.')
            await db.addUser(data['user_event'], data['user_name'], data['user_telegram'], data['user_phone'], birth)
            await state.set_state(None)
        else:
            await bot.send_message(message.chat.id, 'С вашей датой что-то не так.')

# endregion

async def verify_admin(token):
    with open('admin_token.txt', 'r+') as file:
        file_token = file.read()
        if file_token == token:
            file.seek(0)
            file.write('')
            file.truncate()
            return True
        return False

async def generate_token(username):
    token = ''
    for i in range(10):
        token += chr(ord('a') + random.randint(0, 25))
    time_token = str(hash(time.time())) + str(hash(username))
    return token + time_token

async def parse_date(date):
    try:
        date = date.split('.')
        day, month, year = map(int, date)
        return datetime.date(year, month, day)
    except:
        return None

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if db.getAdminByLogin(message.from_user.username):
        await state.set_state(None)
        await show_menu(message)
    else:
        await bot.send_message(message.chat.id, 'Используйте команду /admin, чтобы войти как администратор.')

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    args = message.text.split()
    if not db.getAdminByLogin(message.from_user.username):
        if len(args) > 1:
            token = args[1]
            if await verify_admin(token):
                await bot.send_message(message.chat.id, 'Вы успешно стали администратором.')
                db.addAdmin(message.from_user.username, False)
                await show_menu(message)
            else:
                await bot.send_message(message.chat.id, 'Токен недействителен.')
        else:
            await bot.send_message(message.chat.id, 'Введите ваш пригласительный токен после /admin.')
    else:
        await bot.send_message(message.chat.id, 'Вы уже администратор.')

async def show_menu(message: Message):
    message_text = 'Выберите действие через кнопки внизу.'
    buttons = [
        [KeyboardButton(text='Взаимодействие со списком участников')],
        [KeyboardButton(text='Взаимодействие со списком мероприятий')]
    ]
    if db.getAdminByLogin(message.from_user.username) == 'GreatAdmin':
        buttons += [[KeyboardButton(text='Добавление администратора')]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons)

    await bot.send_message(message.chat.id, message_text, reply_markup=keyboard)

@dp.message(StateFilter(None))
async def receive_message(message: Message, state: FSMContext):
    if db.getAdminByLogin(message.from_user.username):
        message_text = None
        buttons = None
        match message.text:
            case 'Назад':
                await show_menu(message)
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
                message_text = 'Введите ФИО пользователя, которого хотите записать на мероприятие.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(RegisterUser.name_state)
            case 'Выписать участника с мероприятия':
                pass
            case 'Добавить мероприятие':
                message_text = 'Введите название мероприятия.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(CreateEvent.name_state)
            case 'Удалить мероприятие':
                pass
            case 'Изменить мероприятие':
                pass
            case 'Добавление администратора':
                if db.getAdminByLogin(message.from_user.username) == 'GreatAdmin':
                    token = await generate_token(message.from_user.username)
                    with open('admin_token.txt', 'w') as file:
                        file.write(token)
                    message_text = (f'Ваш токен:\n{token}\nПередайте его тому, кого хотите сделать администратором. '
                                    'Он должен использовать команду /admin с вашим токеном. Токен действует только один раз. '
                                    'Одновременно действителен только один токен.')
                    buttons = [[KeyboardButton(text='Назад')]]

        if message_text is not None:
            if buttons is not None:
                await bot.send_message(message.chat.id, message_text, reply_markup=ReplyKeyboardMarkup(keyboard=buttons))
            else:
                await bot.send_message(message.chat.id, message_text, reply_markup=None)
