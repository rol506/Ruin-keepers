import datetime
import logging
import random
import time

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, PhotoSize
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from SETTINGS import telegram_token

from FDataBase import FDataBase
from FDataExport import FDataExport
from flsite import connect_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=telegram_token)
dp = Dispatcher()
db: FDataBase = FDataBase(connect_db())

class CreateEvent (StatesGroup):
    name_state = State()
    description_state = State()
    time_state = State()
    photo_state = State()
    place_state = State()
    cost_state = State()

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
        await bot.send_message(message.chat.id, 'Введите дату и время начала мероприятия в формате дд.мм.гггг чч:мм.')
        await state.set_state(CreateEvent.time_state)

@dp.message(CreateEvent.time_state)
async def get_event_time(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        datestr = message.text.split()
        if len(datestr) != 2:
            await bot.send_message(message.chat.id, 'Что-то не так с вашей датой.')
        else:
            date = await parse_date(datestr[0])
            time = await parse_time(datestr[1])
            if date is None or time is None:
                await bot.send_message(message.chat.id, 'Что-то не так с вашей датой.')
            else:
                await state.update_data(event_date=str(date), event_time=str(time))
                await state.set_state(CreateEvent.place_state)
                await bot.send_message(message.chat.id, 'Введите место проведения мероприятия.')

@dp.message(CreateEvent.place_state)
async def get_event_place(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(event_place=message.text)
        await bot.send_message(message.chat.id, 'Введите стоимость мероприятия в рублях.')
        await state.set_state(CreateEvent.cost_state)

@dp.message(CreateEvent.cost_state)
async def get_event_cost(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            await state.update_data(event_cost=int(float(message.text) * 100))
            await bot.send_message(message.chat.id, 'Пришлите фото, чтобы прикрепить его к мероприятию.')
            await state.set_state(CreateEvent.photo_state)
        else:
            await bot.send_message(message.chat.id, 'Можно вводить только цифры.')

@dp.message(CreateEvent.photo_state)
async def get_event_photo(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.photo is None:
            await bot.send_message(message.chat.id, 'В вашем сообщении нет фотографии.')
        else:

            data = await state.get_data()

            path = await create_photo()
            await bot.download(message.photo[0].file_id, 'static/images/custom/' +  path)
            db.addEvent(data['event_name'], data['event_description'], data['event_date'], data['event_time'],
                        path, data['event_place'], data['event_cost'])
            await bot.send_message(message.chat.id, 'Мероприятие успешно создано.')
            await state.set_state(None)

# endregion

class DeleteEvent (StatesGroup):
    id_state = State()

# region Удаление мероприятия

@dp.message(DeleteEvent.id_state)
async def get_event_id_delete(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            if db.getEventByID(message.text):
                db.removeEventByID(message.text)
                await state.set_state(None)
                await bot.send_message(message.chat.id, 'Мероприятие успешно удалено.')
                await show_menu(message)
            else:
                await bot.send_message(message.chat.id, 'Такого мероприятия не существует.')
        else:
            await bot.send_message(message.chat.id, 'ID должен состоять только из цифр, попробуйте ещё раз.')

# endregion

class ChangeEvent (StatesGroup):
    id_state = State()
    name_state = State()
    description_state = State()
    time_state = State()
    photo_state = State()
    place_state = State()
    cost_state = State()

# region Изменение мероприятия

@dp.message(ChangeEvent.id_state)
async def get_event_id_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            if db.getEventByID(message.text):
                await state.set_state(ChangeEvent.name_state)
                await state.update_data(event_id=message.text)
                await bot.send_message(message.chat.id, 'Введите название мероприятия. (Введите точку, чтобы оставить прежним)')
            else:
                await bot.send_message(message.chat.id, 'Такого мероприятия не существует.')
        else:
            await bot.send_message(message.chat.id, 'ID должен состоять только из цифр, попробуйте ещё раз.')

@dp.message(ChangeEvent.name_state)
async def get_event_name_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(event_name=message.text if message.text != '.' else None)
        await bot.send_message(message.chat.id, 'Введите описание мероприятия. (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeEvent.description_state)

@dp.message(ChangeEvent.description_state)
async def get_event_description_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(event_description=message.text if message.text != '.' else None)
        await bot.send_message(message.chat.id, 'Введите дату и время начала мероприятия в формате дд.мм.гггг чч:мм. (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeEvent.time_state)

@dp.message(ChangeEvent.time_state)
async def get_event_time_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text == '.':
            await state.update_data(event_date=None, event_time=None)
            await state.set_state(ChangeEvent.place_state)
            await bot.send_message(message.chat.id,
                                   'Введите место проведения мероприятия. (Введите точку, чтобы оставить прежним)')
        datestr = message.text.split()
        if len(datestr) != 2:
            await bot.send_message(message.chat.id, 'Что-то не так с вашей датой.')
        else:
            date = await parse_date(datestr[0])
            time = await parse_time(datestr[1])
            if date is None or time is None:
                await bot.send_message(message.chat.id, 'Что-то не так с вашей датой.')
            else:
                await state.update_data(event_date=str(date), event_time=str(time))
                await state.set_state(ChangeEvent.place_state)
                await bot.send_message(message.chat.id, 'Введите место проведения мероприятия. (Введите точку, чтобы оставить прежним)')

@dp.message(ChangeEvent.place_state)
async def get_event_place_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(event_place=message.text if message.text != '.' else None)
        await bot.send_message(message.chat.id, 'Введите стоимость мероприятия в рублях. (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeEvent.cost_state)

@dp.message(ChangeEvent.cost_state)
async def get_event_cost_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric() or message.text == '.':
            await state.update_data(event_cost=int(float(message.text) * 100) if message.text != '.' else None)
            await bot.send_message(message.chat.id, 'Пришлите фото, чтобы прикрепить его к мероприятию. (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeEvent.photo_state)
        else:
            await bot.send_message(message.chat.id, 'Можно вводить только цифры.')

@dp.message(ChangeEvent.photo_state)
async def get_event_photo_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.photo is None and message.text != '.':
            await bot.send_message(message.chat.id, 'В вашем сообщении нет фотографии.')
            return

        data = await state.get_data()
        path = None

        if message.photo is not None:
            path = await create_photo()
            await bot.download(message.photo[0].file_id, 'static/images/custom/' +  path)

        db.updateEvent(data["event_id"], data['event_name'], data['event_description'], data['event_date'], data['event_time'],
                    path, data['event_place'], data['event_cost'])
        await bot.send_message(message.chat.id, 'Мероприятие успешно изменено.')
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
            if db.getEventByID(message.text):
                await state.update_data(user_event=int(message.text))
                await bot.send_message(message.chat.id, 'Введите телеграм этого пользователя.')
                await state.set_state(RegisterUser.telegram_state)
            else:
                await bot.send_message(message.chat.id, 'Такого мероприятия не существует.')
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
            db.addUser(data['user_event'], data['user_name'], data['user_telegram'], data['user_phone'], birth)
            await state.set_state(None)
            await show_menu(message)
        else:
            await bot.send_message(message.chat.id, 'С вашей датой что-то не так.')

# endregion

class DeleteRegistration (StatesGroup):
    id_state = State()

# region Удаление регистрации

@dp.message(DeleteRegistration.id_state)
async def get_user_id_delete(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            if db.getUserByID(message.text):
                db.removeUserByID(message.text)
                await state.set_state(None)
                await bot.send_message(message.chat.id, 'Запись успешно удалена.')
                await show_menu(message)
            else:
                await bot.send_message(message.chat.id, 'Такой записи не существует.')
        else:
            await bot.send_message(message.chat.id, 'ID должен состоять только из цифр, попробуйте ещё раз.')


# endregion

class ChangeRegistration (StatesGroup):
    id_state = State()
    name_state = State()
    telegram_state = State()
    phone_state = State()
    birth_state = State()

# region Изменение регистрации

@dp.message(ChangeRegistration.id_state)
async def get_user_id_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            if db.getUserByID(int(message.text)):
                await state.update_data(user_id=int(message.text))
                await bot.send_message(message.chat.id,
                                       'Введите ID мероприятия, на которое хотите зарегистрировать этого пользователя. '
                                       '(Введите точку, чтобы оставить прежним)')
                await state.set_state(ChangeRegistration.name_state)
            else:
                await bot.send_message(message.chat.id, 'Такой записи не существует.')
        else:
            await bot.send_message(message.chat.id, 'В ID могут быть только цифры.')

@dp.message(ChangeRegistration.name_state)
async def get_user_name_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(user_name=message.text if message.text != '.' else None)
        await bot.send_message(message.chat.id, 'Введите телеграм этого пользователя. (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeRegistration.telegram_state)

@dp.message(ChangeRegistration.telegram_state)
async def get_user_telegram_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(user_telegram=message.text if message.text != '.' else None)
        await bot.send_message(message.chat.id, 'Введите номер телефона этого пользователя. (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeRegistration.phone_state)

@dp.message(ChangeRegistration.phone_state)
async def get_user_phone_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        await state.update_data(user_phone=message.text if message.text != '.' else None)
        await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг". (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeRegistration.birth_state)

@dp.message(ChangeRegistration.birth_state)
async def get_user_birth_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text == '.':
            birth = None
        else:
            birth = await parse_date(message.text)
            if birth is None:
                await bot.send_message(message.chat.id, 'С вашей датой что-то не так.')
                return
        data = await state.get_data()

        await bot.send_message(message.chat.id, f'Запись успешно изменена.')
        db.updateUser(data['user_id'], data['user_name'], data['user_telegram'], data['user_phone'], birth)
        await state.set_state(None)
        await show_menu(message)

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

async def create_photo():
    id = 0
    with open('last_photo_id', 'r+') as file:
        id = int(file.read())
        file.seek(0)
        file.write(str(id + 1))
    return 'image' + str(id) + '.jpg'


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
        return str(datetime.date(year, month, day))
    except:
        return None

async def parse_time(time):
    try:
        time = time.split(':')
        h, m = map(int, time)
        return datetime.time(h, m)
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
        [KeyboardButton(text='Взаимодействие со списком мероприятий')],
        [KeyboardButton(text='Экспортировать базу данных в google sheets')]
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
                     KeyboardButton(text='Выписать участника с мероприятия'),
                     KeyboardButton(text='Изменить запись')],
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
                message_text = 'Введите ID записи.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(DeleteRegistration.id_state)
            case 'Изменить запись':
                message_text = 'Введите ID записи.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(ChangeRegistration.id_state)
            case 'Добавить мероприятие':
                message_text = 'Введите название мероприятия.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(CreateEvent.name_state)
            case 'Удалить мероприятие':
                message_text = 'Введите ID мероприятия.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(DeleteEvent.id_state)
            case 'Изменить мероприятие':
                message_text = 'Введите ID мероприятия.'
                buttons = [[KeyboardButton(text='Назад')]]
                await state.set_state(ChangeEvent.id_state)
            case 'Добавление администратора':
                if db.getAdminByLogin(message.from_user.username) == 'GreatAdmin':
                    token = await generate_token(message.from_user.username)
                    with open('admin_token.txt', 'w') as file:
                        file.write(token)
                    message_text = (f'Ваш токен:\n{token}\nПередайте его тому, кого хотите сделать администратором. '
                                    'Он должен использовать команду /admin с вашим токеном. Токен действует только один раз. '
                                    'Одновременно действителен только один токен.')
                    buttons = [[KeyboardButton(text='Назад')]]
            case 'Экспортировать базу данных в google sheets':
                await bot.send_message(message.chat.id, 'Экспортируем...')
                await FDataExport()
                await bot.send_message(message.chat.id, 'Готово!')

        if message_text is not None:
            if buttons is not None:
                await bot.send_message(message.chat.id, message_text, reply_markup=ReplyKeyboardMarkup(keyboard=buttons))
            else:
                await bot.send_message(message.chat.id, message_text, reply_markup=None)
