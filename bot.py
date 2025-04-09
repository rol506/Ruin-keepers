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
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery

from SETTINGS import telegram_token

from FDataBase import FDataBase
from FDataExport import FDataExport
from flsite import connect_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=telegram_token)
dp = Dispatcher()
db: FDataBase = FDataBase(connect_db())

# region Создание мероприятия

class CreateEvent (StatesGroup):
    name_state = State()
    description_state = State()
    time_state = State()
    photo_state = State()
    place_state = State()
    cost_state = State()
    lunch_state = State()
    lunch_cost_state = State()

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
        await bot.send_message(message.chat.id, 'Введите дату и время начала мероприятия в формате дд.мм чч:мм.')
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
            await bot.send_message(message.chat.id, 'Будет ли обед на мероприятии? Введите да или нет.')
            await state.set_state(CreateEvent.lunch_state)
        else:
            await bot.send_message(message.chat.id, 'Можно вводить только цифры.')

@dp.message(CreateEvent.lunch_state)
async def get_event_lunch(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.lower() == 'да':
            await bot.send_message(message.chat.id, 'Введите стоимость обеда в рублях.')
            await state.set_state(CreateEvent.lunch_cost_state)
        elif message.text.lower() == 'нет':
            await bot.send_message(message.chat.id, 'Пришлите фото, чтобы прикрепить его к мероприятию.')
            await state.update_data(event_lunch_cost=-1)
            await state.set_state(CreateEvent.photo_state)
        else:
            await bot.send_message(message.chat.id, 'Введите только ДА или НЕТ.')

@dp.message(CreateEvent.lunch_cost_state)
async def get_event_lunch_cost(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            await state.update_data(event_lunch_cost=int(float(message.text) * 100))
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
                        path, data['event_place'], data['event_cost'], data['event_lunch_cost'])
            await bot.send_message(message.chat.id, 'Мероприятие успешно создано.')
            await state.set_state(None)

# endregion

# region Удаление мероприятия

class DeleteEvent (StatesGroup):
    id_state = State()

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

# region Изменение мероприятия

class ChangeEvent (StatesGroup):
    id_state = State()
    name_state = State()
    description_state = State()
    time_state = State()
    photo_state = State()
    place_state = State()
    cost_state = State()
    lunch_state = State()
    lunch_cost_state = State()

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
        await bot.send_message(message.chat.id, 'Введите дату и время начала мероприятия в формате дд.мм чч:мм. (Введите точку, чтобы оставить прежним)')
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
            return

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
            await bot.send_message(message.chat.id, 'Будет ли обед на мероприятии? Введите да или нет. (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeEvent.lunch_state)
        else:
            await bot.send_message(message.chat.id, 'Можно вводить только цифры.')

@dp.message(ChangeEvent.lunch_state)
async def get_event_lunch_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text == '.':
            await state.update_data(event_lunch_cost=None)
            await bot.send_message(message.chat.id, 'Пришлите фото, чтобы прикрепить его к мероприятию. (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeEvent.photo_state)
        elif message.text.lower() == 'да':
            await bot.send_message(message.chat.id, 'Введите стоимость обеда в рублях. (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeEvent.lunch_cost_state)
        elif message.text.lower() == 'нет':
            await bot.send_message(message.chat.id, 'Пришлите фото, чтобы прикрепить его к мероприятию. (Введите точку, чтобы оставить прежним)')
            await state.update_data(event_lunch_cost=-1)
            await state.set_state(ChangeEvent.photo_state)
        else:
            await bot.send_message(message.chat.id, 'Введите только ДА или НЕТ.')

@dp.message(ChangeEvent.lunch_cost_state)
async def get_event_lunch_cost_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.isnumeric():
            await state.update_data(event_lunch_cost=int(float(message.text) * 100))
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

        db.updateEvent(data['event_id'], data['event_name'], data['event_description'], data['event_date'], data['event_time'],
                    path, data['event_place'], data['event_cost'], data['event_lunch_cost'])
        await bot.send_message(message.chat.id, 'Мероприятие успешно изменено.')
        await state.set_state(None)

# endregion

# region Регистрация пользователя

class RegisterUser (StatesGroup):
    event_state = State()
    name_state = State()
    telegram_state = State()
    phone_state = State()
    birth_state = State()
    lunch_state = State()

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
        await bot.send_message(message.chat.id, 'Будет ли участник обедать? Введите да или нет.')
        await state.set_state(RegisterUser.lunch_state)

@dp.message(RegisterUser.lunch_state)
async def get_user_lunch(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text.lower() == 'да':
            await state.update_data(user_lunch=1)
            await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг".')
            await state.set_state(RegisterUser.birth_state)
        elif message.text.lower() == 'нет':
            await state.update_data(user_lunch=0)
            await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг".')
            await state.set_state(RegisterUser.birth_state)
        else:
            await bot.send_message(message.chat.id, 'Введите только ДА или НЕТ.')

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
            db.addUser(data['user_event'], data['user_name'], data['user_telegram'], data['user_phone'], birth, data['user_lunch'])
            await state.set_state(None)
            await show_menu(message)
        else:
            await bot.send_message(message.chat.id, 'С вашей датой что-то не так.')

# endregion

# region Удаление регистрации

class DeleteRegistration (StatesGroup):
    id_state = State()

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

# region Изменение регистрации

class ChangeRegistration (StatesGroup):
    id_state = State()
    name_state = State()
    telegram_state = State()
    phone_state = State()
    birth_state = State()
    lunch_state = State()

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
        await bot.send_message(message.chat.id, 'Будет ли участник обедать? Введите да или нет. (Введите точку, чтобы оставить прежним)')
        await state.set_state(ChangeRegistration.lunch_state)

@dp.message(ChangeRegistration.lunch_state)
async def get_user_lunch_change(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
    else:
        if message.text == '.':
            await state.update_data(user_lunch=None)
            await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг". (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeRegistration.birth_state)
        elif message.text.lower() == 'да':
            await state.update_data(user_lunch=1)
            await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг". (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeRegistration.birth_state)
        elif message.text.lower() == 'нет':
            await state.update_data(user_lunch=0)
            await bot.send_message(message.chat.id, 'Введите дату рождения этого пользователя в формате "дд.мм.гггг". (Введите точку, чтобы оставить прежним)')
            await state.set_state(ChangeRegistration.birth_state)
        else:
            await bot.send_message(message.chat.id, 'Введите только ДА или НЕТ.')

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
        db.updateUser(data['user_id'], data['user_name'], data['user_telegram'], data['user_phone'], birth, data['user_lunch'])
        await state.set_state(None)
        await show_menu(message)

# endregion

# region Вывод списка участников

class ViewUsers(StatesGroup):
    show = State()

@dp.message(ViewUsers.show)
async def user_navigation_quit(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
        return

@dp.callback_query(ViewUsers.show)
async def handle_user_navigation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users = data.get("users", [])
    index = data.get("index", 0)

    if not users:
        await callback.message.edit_text("Список участников пуст.")
        await state.clear()
        return

    if callback.data.startswith("prev_"):
        index = max(0, int(callback.data.split("_")[1]))
    elif callback.data.startswith("next_"):
        index = min((len(users) - 1) // 3, int(callback.data.split("_")[1]))
    else:
        await callback.answer("Некорректная кнопка.")
        return

    await state.update_data(index=index)
    user = users[index * 3]

    text = await get_user_data(user)
    for i in range(index * 3 + 1, min(index * 3 + 3, len(users))):
        text += '\n\n' + await get_user_data(users[i])

    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"prev_{index - 1}"))
    if (index + 1) * 3 < len(users):
        buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"next_{index + 1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else None)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

async def get_user_data(user):
    text = (
        f"🆔 ID: {user['id']}\n"
        f"👤 ФИО: {user['name']}\n"
        f"📞 Телефон: {user['phone']}\n"
        f"🎂 Дата рождения: {user['birth']}\n"
        f"📬 Telegram: {user['telegram'] or '—'}\n"
        f"🗓️ ID мероприятия: {user['eventID']}\n"
        f"🍽️ Обед: {'Оплачен' if user['lunch'] else 'Нет'}\n"
    )
    return text

# endregion

# region Вывод списка мероприятий

class ViewEvents(StatesGroup):
    show = State()

@dp.message(ViewEvents.show)
async def user_navigation_quit(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
        return

@dp.callback_query(ViewEvents.show)
async def handle_events_navigation(callback: CallbackQuery, state: FSMContext, message: Message = None):
    if message is not None and message.text == 'Назад':
        await state.set_state(None)
        await show_menu(message)
        return

    data = await state.get_data()
    events = data.get("events", [])
    index = data.get("index", 0)

    if not events:
        await callback.message.edit_text("Список участников пуст.")
        await state.clear()
        return

    if callback.data.startswith("prev_"):
        index = max(0, int(callback.data.split("_")[1]))
    elif callback.data.startswith("next_"):
        index = min((len(events) - 1) // 3, int(callback.data.split("_")[1]))
    else:
        await callback.answer("Некорректная кнопка.")
        return

    await state.update_data(index=index)
    event = events[index * 3]

    text = await get_event_data(event)
    for i in range(index * 3 + 1, min(index * 3 + 3, len(events))):
        text += '\n\n' + await get_event_data(events[i])

    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"prev_{index - 1}"))
    if (index + 1) * 3 < len(events):
        buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"next_{index + 1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else None)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

async def get_event_data(event):
    text = (
        f"🆔 ID: {event['id']}\n"
        f"🚩 Название: {event['name']}\n"
        f"📃 Описание: {event['description']}\n"
        f"💳 Стоимость: {event['cost']}\n"
        f"🏠 Место: {event['place']}\n"
        f"📆 Дата: {event['date']}\n"
        f"🕒 Время: {event['time']}\n"
        f"🍽️ Обед: {str(event['lunchCost'] // 100) + ' руб.' if event['lunchCost'] >= 0 else 'Не включён'}"
    )
    return text

# endregion

# region Misc

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
        if len(date) == 3:
            day, month, year = map(int, date)
        else:
            day, month = map(int, date)
            now = datetime.datetime.now()
            if month < now.month:
                year = now.year + 1
            else:
                if month == now.month and day < now.day:
                    year = now.year + 1
                else:
                    year = now.year
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

# endregion

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
                    [KeyboardButton(text='Вывести список участников')],
                    [KeyboardButton(text='Назад')]
                ]
            case 'Взаимодействие со списком мероприятий':
                message_text = 'Выберите действие.'
                buttons = [
                    [KeyboardButton(text='Добавить мероприятие'),
                     KeyboardButton(text='Удалить мероприятие'),
                     KeyboardButton(text='Изменить мероприятие')],
                    [KeyboardButton(text='Вывести список мероприятий')],
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
            case 'Вывести список участников':
                buttons = [[KeyboardButton(text='Назад')]]
                await bot.send_message(message.chat.id, 'Список участников:', reply_markup=ReplyKeyboardMarkup(keyboard=buttons))
                users = db.getUsers()
                if not users:
                    await bot.send_message(message.chat.id, "Список участников пуст.")
                    return

                await state.set_state(ViewUsers.show)
                await state.update_data(users=users, index=0)

                user = users[0]
                text = await get_user_data(user)
                for i in range(1, min(3, len(users))):
                    text += '\n\n' + await get_user_data(users[i])

                inline_buttons = []
                if len(users) > 3:
                    inline_buttons.append(InlineKeyboardButton(text="▶️", callback_data="next_1"))
                keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons] if inline_buttons else [])  # Передаем пустой список, если кнопок нет
                
                await bot.send_message(message.chat.id, text, reply_markup=keyboard)
            case 'Вывести список мероприятий':
                buttons = [[KeyboardButton(text='Назад')]]
                await bot.send_message(message.chat.id, 'Список мероприятий:', reply_markup=ReplyKeyboardMarkup(keyboard=buttons))
                events = db.getEvents()
                if not events:
                    await bot.send_message(message.chat.id, "Список мероприятий пуст.")
                    return

                await state.set_state(ViewEvents.show)
                await state.update_data(events=events, index=0)

                event = events[0]
                text = await get_event_data(event)
                for i in range(1, min(3, len(events))):
                    text += '\n\n' + await get_event_data(events[i])

                inline_buttons = []
                if len(events) > 3:
                    inline_buttons.append(InlineKeyboardButton(text="▶️", callback_data="next_1"))
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[inline_buttons] if inline_buttons else [])  # Передаем пустой список, если кнопок нет

                await bot.send_message(message.chat.id, text, reply_markup=keyboard)

        if message_text is not None:
            if buttons is not None:
                await bot.send_message(message.chat.id, message_text, reply_markup=ReplyKeyboardMarkup(keyboard=buttons))
            else:
                await bot.send_message(message.chat.id, message_text, reply_markup=None)
