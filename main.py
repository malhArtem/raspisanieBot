from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram.utils.executor import start_webhook
from aiogram.utils.exceptions import TelegramAPIError
import logging
import calendar
import json
import requests
import os

from func import *
from keyboard import *
from config import TOKEN

bot = Bot(TOKEN, parse_mode="html")
dp = Dispatcher(bot)

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='register',
            description='регистрация/смена группы'
        ),
        BotCommand(
            command='today',
            description='расписание на сегодня'
        ),
        BotCommand(
            command='next_day',
            description='расписание на следующий день'
        ),
        BotCommand(
            command='week',
            description='расписание на эту неделю'
        ),
        BotCommand(
            command='next_week',
            description='расписание на следующую неделю'
        ),
        # BotCommand(
        #     command='teacher_or_student',
        #     description='смена режима(преподаватель/студент)'
        # ),
        BotCommand(
            command='day',
            description='расписание на любой день'
        ),
        BotCommand(
            command='communication',
            description='связь'
        )
    ]


    await bot.set_my_commands(commands)



def get_ngrok_url():
    url = "http://localhost:4040/api/tunnels/"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    for i in res_json["tunnels"]:
        if i['name'] == 'command_line':
            return i['public_url']


async def on_startup(_):
    # WEBHOOK_HOST = get_ngrok_url()
    # WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
    #
    # await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)  # передаём адрес куда слать апдейты

    await db_start()
    await set_commands(bot)
    await bot.send_message(admins_id, "Бот запущен")


async def on_startup1(_):
    await db_start()
    await create_table_users()


async def on_shutdown(_):
    await bot.send_message(admins_id, "Бот остановлен")
    await bot.delete_webhook()


@dp.message_handler(commands=["связь", "communication"])
async def connection_cmd(message: types.Message):
    text = """ <b>1. Деканат</b> (каб. 333а) | Тел: <code>2-208-460</code>; <code>2-208-553</code>  
<b>2. КАиММГ</b> (каб. 334) | Тел: <code>2-208-641</code>
<b>3. КМА</b> (каб. 332) | Тел: <code>2-208-690</code>  
<b>4. КММ</b> (каб. 322) | Тел: <code>2-208-364</code>
<b>5. КТФ</b> (каб. 324) | Тел: <code>2-208-665</code>  
<b>6. КУЧП</b> (каб. 327, 308) | Тел: <code>2-208-618</code>
<b>7. КФА</b> (каб. 225) | Тел: <code>2-208-771</code>
  
Сообщить об ошибке: @mlhv_artem
"""
    await message.answer(text)


@dp.message_handler(commands=['start'])
@dp.callback_query_handler(text="kurs")
@dp.callback_query_handler(text="register")
@dp.message_handler(commands=['register'])
async def user_reg_kurs(message):
    i_kb_kurs = InlineKeyboardMarkup(row_width=2)   # создание Inline-клавиатуры
    kurses = await get_kurs()
    for kurs in kurses:
        if kurs[1] != 'users' and not('old' in kurs[1]):
            ib = InlineKeyboardButton(kurs[1], callback_data=cb_kurs.new(number=kurs[1]))   # создание Inline-кнопки
            i_kb_kurs.insert(ib)        # добавление кнопки в клавиатуру
    ib = InlineKeyboardButton("Преподаватель", callback_data='Преподаватель')
    i_kb_kurs.add(ib)
    if isinstance(message, types.Message):
        await message.delete()
        await message.answer("Здравствуй, математик!\nПройди небольшую регистрацию и сможешь наблюдать свое расписание.\nВыбери свой курс:",
                             reply_markup=i_kb_kurs)
    else:
        await message.message.edit_text(text="""Здравствуй, математик!\nПройди небольшую регистрацию и сможешь наблюдать свое расписание.\nВыбери свой курс:""",
                                        reply_markup=i_kb_kurs)
        await bot.answer_callback_query(message.id)



@dp.callback_query_handler(cb_kurs.filter())
async def user_reg_group(callback_query: types.CallbackQuery, callback_data: dict):
    groups = await get_groups(callback_data.get('number'))
    groups.sort()
    i_kb_groups = InlineKeyboardMarkup(row_width=3)

    if len(groups) > 1:
        for i in range(len(groups)-1):
            if groups[i][0] == groups[i+1][0] or groups[i][0] == groups[i-1][0]:
                group = f'{groups[i][1]} {groups[i][0]}'
            else:
                group = groups[i][0]

            ib = InlineKeyboardButton(group, callback_data=cb_group.new(kurs=str(callback_data.get('number')),
                                                                                    groups=group))
            i_kb_groups.insert(ib)

        if groups[-1][0] == groups[-2][0]:
            group = f'{groups[-1][1]} {groups[-1][0]}'
        else:
            group = groups[-1][0]

        ib = InlineKeyboardButton(group, callback_data=cb_group.new(kurs=str(callback_data.get('number')),
                                                                    groups=group))
        i_kb_groups.insert(ib)

    elif groups[0] is not None:
        group = groups[-1][0]
        ib = InlineKeyboardButton(group, callback_data=cb_group.new(kurs=str(callback_data.get('number')),
                                                                    groups=group))
        i_kb_groups.insert(ib)

    ib = InlineKeyboardButton('<', callback_data='kurs')
    i_kb_groups.add(ib)
    # await callback_query.message.delete()
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(text = "Замечательно! \nВыбери свою группу:", reply_markup=i_kb_groups)
    # await callback_query.message.answer("Выберите группу", reply_markup=i_kb_groups)


@dp.callback_query_handler(text="Преподаватель")
async def user_reg_teach(callback_query: types.CallbackQuery):
    await create_table_users()

    i_kb = InlineKeyboardMarkup(row_width=2)
    teachers = await get_teachers()
    teachers.sort()
    for teacher in teachers:
        ib = InlineKeyboardButton(str(teacher[0]), callback_data=cb_teacher.new(name=str(teacher[0])))
        i_kb.insert(ib)
    ib = InlineKeyboardButton("<", callback_data='kurs')
    i_kb.add(ib)
    await create_table_users()
    await create_profile_teacher(callback_query, '')
    user = list(await get_user(callback_query.from_user.id))
    user[2] = 1
    user[3] = ''
    await update_profile(callback_query, user)
    text = "Замечательно\nНайдите себя в списке:"
    if isinstance(callback_query, types.CallbackQuery):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.delete()
        await callback_query.message.answer(text, reply_markup=i_kb)
    else:
        await callback_query.answer(text, reply_markup=i_kb)


@dp.callback_query_handler(cb_teacher.filter())
async def reg_teacher(callback_query: types.CallbackQuery, callback_data: dict):
    user = list(await get_user(callback_query.from_user.id))
    user[3] = callback_data.get("name")
    await update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text(f"""Супер! \nРегистрация прошла успешно\n<i>Поиск по преподавателю ({user[3]})</i>""")


@dp.callback_query_handler(cb_group.filter())
async def user_reg(callback_query: types.CallbackQuery, callback_data: dict):
    await create_table_users()
    await create_profile_student(callback_query, callback_data.get('kurs'), callback_data.get('groups'))
    user = list(await get_user(callback_query.from_user.id))
    user[0] = callback_data.get('kurs')
    user[1] = callback_data.get('groups')
    user[2] = 0
    await update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text(f"Супер! \nРегистрация прошла успешно\n<i>Поиск по группе ({user[0]}: {user[1]})</i>")


@dp.callback_query_handler(text="Нет")
async def callback_no(callback_query: types.CallbackQuery):
    user = list(await get_user(callback_query.from_user.id))
    if user[2] == 0:
        user[2] = 1
        text = f"Успешно \nПоиск по преподавателю ({user[3]})"
    else:
        user[2] = 0
        text = f"Успешно \nПоиск по группе ({user[0]}: {user[1]})"
    await update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text(text)


@dp.message_handler(commands=["today"])
async def today_rasp(message: types.Message):
    user = await get_user(message.from_user.id)    # получаем данные пользователя (курс, группу)
    ikb = InlineKeyboardMarkup()
    if user is not None:
        today = datetime.datetime.now()            # получаем дату на момент написания сообщения
        if user[2] == 0:
            text = await day_rasp(message, today)  # формируем сообщение
        else:
            text = await get_teach_rasp(today, message)
    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
    await message.answer(text, parse_mode='html', reply_markup=ikb)    # отправляем сообщение


@dp.message_handler(commands=["next_day"])
async def next_day_rasp(message: types.Message):
    user = await get_user(message.from_user.id)
    ikb = InlineKeyboardMarkup()
    if user is not None:
        day = datetime.datetime.now() + datetime.timedelta(days=1)
        if day.weekday() == 6:
            day = day + datetime.timedelta(days=1)
        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = await get_teach_rasp(day, message)

    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
    await message.answer(text, parse_mode='html', reply_markup=ikb)


@dp.message_handler(commands=["week"])
async def week_rasp(message: types.Message):
    user = await get_user(message.from_user.id)
    ikb = InlineKeyboardMarkup()
    if user is not None:
        day = datetime.datetime.now()
        week_day = day.weekday()

        day = day - datetime.timedelta(days=week_day)

        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = await get_teach_rasp(day, message)

        await message.answer(text, parse_mode='html')

        for i in range(1, 6):
            day = day + datetime.timedelta(days=1)
            if user[2] == 0:
                text = await day_rasp(message, day)
            else:
                text = await get_teach_rasp(day, message)

            await message.answer(text, parse_mode='html')

    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
        await message.answer(text, parse_mode='html', reply_markup=ikb)


@dp.message_handler(commands=["next_week"])
async def week_rasp(message: types.Message):
    ikb = InlineKeyboardMarkup()
    user = await get_user(message.from_user.id)
    if user is not None:
        day = datetime.datetime.now()
        week_day = day.weekday()

        day = day - datetime.timedelta(days=week_day) + datetime.timedelta(days=7)
        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = await get_teach_rasp(day, message)
        await message.answer(text, parse_mode='html')

        for i in range(1, 6):
            day = day + datetime.timedelta(days=1)
            if user[2] == 0:
                text = await day_rasp(message, day)
            else:
                text = await get_teach_rasp(day, message)

            await message.answer(text, parse_mode='html')
    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="зарегистрироваться", callback_data="register")
        ikb.add(ib)
        await message.answer(text, parse_mode='html', reply_markup=ikb)


# @dp.message_handler(commands=["teacher_or_student"])
# async def teach_or_stud(message: types.Message):
#     await create_table_users()
#     text = ''
#     i_kb = InlineKeyboardMarkup()
#     await create_profile_teacher(message, '')
#     user = list(await get_user(message.from_user.id))
#     if user[2] == 0:
#         user[2] = 1
#         if user[3] == '':
#             await user_reg_teach(message)
#         else:
#             text = f"Изменить преподавателя?\n<i>{user[3]}</i>"
#             ib = InlineKeyboardButton("Нет", callback_data='Нет')
#             ib1 = InlineKeyboardButton("Да", callback_data='Преподаватель')
#             i_kb.add(ib, ib1)
#
#     else:
#         if user[0] is None:
#             await user_reg_kurs(message)
#         else:
#             text = f"Сменить группу/курс?\n<i>{user[0]}: {user[1]}</i>"
#             ib = InlineKeyboardButton("Нет", callback_data='Нет')
#             ib1 = InlineKeyboardButton("Да", callback_data='register')
#             i_kb.add(ib, ib1)
#     await message.delete()
#     await message.answer(text, reply_markup=i_kb)


@dp.callback_query_handler(text="choose_month")
@dp.message_handler(commands=['day'])
async def choose_month(message: types.Message):
    user = await get_user(message.from_user.id)
    i_kb = InlineKeyboardMarkup(row_width=3)
    if user is not None:
        today = datetime.datetime.now()
        str_month = today.strftime("%Y-%m-%d").split('-')[1]
        text = "Выберите месяц"
        if int(str_month) < 9:
            for i in range(int(str_month), 9):
                ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
                i_kb.insert(ib)
        else:
            for i in range(int(str_month), 12):
                ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
                i_kb.insert(ib)

    else:
        text = "Вы не зарегистрированы"

        ib = InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")
        i_kb.add(ib)
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=i_kb)
    else:
        await bot.answer_callback_query(message.id)
        await message.message.edit_text(text, reply_markup=i_kb)

# @dp.callback_query_handler(text="choose_month")
# async def choose_month(callback_query: types.CallbackQuery):
#     today = datetime.datetime.now()
#     str_month = today.strftime("%Y-%m-%d").split('-')[1]
#
#     i_kb = InlineKeyboardMarkup(row_width=3)
#     if int(str_month) < 9:
#         for i in range(int(str_month), 9):
#             ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
#             i_kb.insert(ib)
#     else:
#         for i in range(int(str_month), 12):
#             ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
#             i_kb.insert(ib)
#
#     await bot.answer_callback_query(callback_query.id)
#     await callback_query.message.delete()
#     await callback_query.message.answer("Выберите месяц:", reply_markup=i_kb)


@dp.callback_query_handler(cb_month.filter())
async def choose_day(callback_query: types.CallbackQuery, callback_data: dict):
    today = datetime.datetime.now()
    i_kb = InlineKeyboardMarkup(row_width=7)
    str_year = today.strftime("%Y-%m-%d").split('-')[0]
    month = calendar.monthrange(int(str_year), int(callback_data.get('number')))
    for i in range(0, month[1]):
        ib = InlineKeyboardButton(str(i + 1), callback_data=cb_day.new(month=callback_data.get('number'),
                                                                       number=str(i + 1)))
        i_kb.insert(ib)
    ib = InlineKeyboardButton("<", callback_data="choose_month")
    i_kb.insert(ib)
    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text("Выберите день:", reply_markup=i_kb)


@dp.callback_query_handler(cb_day.filter())
async def date_rasp(callback_query: types.CallbackQuery, callback_data: dict):
    today = datetime.datetime.now()
    user = await get_user(callback_query.from_user.id)
    str_year = today.strftime("%Y-%m-%d").split('-')[0]
    str_date = str_year + '-' + callback_data.get('month') + '-' + callback_data.get('number')
    date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
    if user[2] == 0:
        text = await day_rasp(callback_query, date)
    else:
        text = await get_teach_rasp(date, callback_query)
    await bot.answer_callback_query(callback_query.id)
    # await callback_query.message.delete()
    await callback_query.message.edit_text(text = text, parse_mode='html')


@dp.message_handler(content_types=['document'])     # отлавливаем сообщения являющиеся документом
@dp.async_task      # этот декоратор используется для функций которые будут выполняться долго
async def get_file_xl(message: types.Message):
    if str(message.from_user.id) == str(message.chat.id) == admins_id:
        if message.document.file_name.split('.')[-1] == 'xlsx':
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            path_file = file.file_path
            path = 'xl_new.xlsx'
            await bot.download_file(path_file, path)          # скачиваем файл и сохраняем под именем 'xl_new.xlsx'

            if os.path.exists('xl_old.xlsx'):
                os.remove('xl_old.xlsx')

            if os.path.exists('xl.xlsx'):
                os.rename('xl.xlsx', 'xl_old.xlsx')

            os.rename('xl_new.xlsx', 'xl.xlsx')

            await delete_old()
            kurses = await get_kurs()
            for kurs in kurses:
                if kurs[1] != 'users':
                    await rename_tables(kurs)                # переименовывываем уже существующие таблицы с расписанием
            await message.answer('Изменяем раписание')
            await parse_xl()                                 # извлекаем данные из нового excel файла в базу данных
            await message.answer('Расписание изменено')
            print("Готово")
            await get_all_diff()                             # сравниваем старое расписание с новым и отправляем различия пользователям
        else:
            await message.answer('Неправильное разрешение')







@dp.errors_handler(TelegramAPIError)
async def error_bot_handler(update: types.Update, exception) -> bool:
    logger.error(f"{exception} : {update}")
    await bot.send_message(admins_id, f"{exception}")
    return True




if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     skip_updates=True,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

