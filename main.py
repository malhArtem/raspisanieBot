from _cffi_backend import callback
import logging
from keyboard import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from func import *
from aiogram import Bot, Dispatcher, types, executor

import calendar
from aiogram.utils.exceptions import BadRequest, MessageCantBeDeleted, MessageCantBeEdited

bot = Bot('6175627267:AAFpTEFRGuGwBf41cs5xT19KdcEEbLJucSQ', parse_mode="html")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logger = logging.getLogger(__name__)


async def on_startup(_):
    db_start()


@dp.message_handler(commands=['start'])
async def user_reg_kurs(message: types.Message):
    i_kb_kurs = InlineKeyboardMarkup(row_width=2)
    kurses = get_kurs()
    for kurs in kurses:
        if kurs[1] != 'users':
            ib = InlineKeyboardButton(kurs[1], callback_data=cb_kurs.new(number=kurs[1]))
            i_kb_kurs.insert(ib)
    ib = InlineKeyboardButton("Я преподаватель", callback_data='Преподаватель')
    i_kb_kurs.add(ib)
    await message.delete()
    await message.answer("Выберите ваш курс!", reply_markup=i_kb_kurs)


@dp.callback_query_handler(text="kurs")
async def user_reg_kurs(callback_query: types.CallbackQuery):
    i_kb_kurs = InlineKeyboardMarkup(row_width=2)
    kurses = get_kurs()
    for kurs in kurses:
        if kurs[1] != 'users':
            ib = InlineKeyboardButton(kurs[1], callback_data=cb_kurs.new(number=kurs[1]))
            i_kb_kurs.insert(ib)
    ib = InlineKeyboardButton("Я преподаватель", callback_data='Преподаватель')
    i_kb_kurs.add(ib)
    await callback_query.message.delete()
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Выберите ваш курс!", reply_markup=i_kb_kurs)

@dp.callback_query_handler(text = "register")
@dp.message_handler(commands=['register'])
async def user_reg_kurs(message):
    i_kb_kurs = InlineKeyboardMarkup(row_width=2)
    kurses = get_kurs()
    for kurs in kurses:
        if kurs[1] != 'users':
            ib = InlineKeyboardButton(kurs[1], callback_data=cb_kurs.new(number=kurs[1]))
            i_kb_kurs.insert(ib)
    ib = InlineKeyboardButton("Я преподаватель", callback_data='Преподаватель')
    i_kb_kurs.add(ib)
    if isinstance(message, types.Message):
        await message.delete()
        await message.answer("Выберите ваш курс!", reply_markup=i_kb_kurs)
    else:
        await message.message.delete()
        await bot.answer_callback_query(message.id)
        await message.message.answer("Выберите ваш курс!", reply_markup=i_kb_kurs)


@dp.callback_query_handler(cb_kurs.filter())
async def user_reg_group(callback_query: types.CallbackQuery, callback_data: dict):
    groups = get_groups(callback_data.get('number'))
    i_kb_groups = InlineKeyboardMarkup(row_width=3)

    for i in range(len(groups)):
        ib = InlineKeyboardButton(str(groups[i][0]), callback_data=cb_group.new(kurs=str(callback_data.get('number')),
                                                                                groups=groups[i][0]))
        i_kb_groups.insert(ib)
    ib = InlineKeyboardButton('<', callback_data='kurs')
    i_kb_groups.add(ib)
    await callback_query.message.delete()
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Выберите группу", reply_markup=i_kb_groups)


@dp.callback_query_handler(text="Преподаватель")
async def user_reg_teach(callback_query: types.CallbackQuery):
    i_kb = InlineKeyboardMarkup(row_width=2)
    teachers = get_teachers()
    teachers.sort()
    for teacher in teachers:
        ib = InlineKeyboardButton(str(teacher[0]), callback_data=cb_teacher.new(name=str(teacher[0])))
        i_kb.insert(ib)
    ib = InlineKeyboardButton("<", callback_data='kurs')
    i_kb.add(ib)
    create_table_users()
    create_profile_teacher(callback_query, '')
    user = list(get_user(callback_query.from_user.id))
    user[2] = 1
    user[3] = ''
    update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer("""Выберите""", reply_markup=i_kb)


@dp.callback_query_handler(cb_teacher.filter())
async def reg_teacher(callback_query: types.CallbackQuery, callback_data: dict):
    user = list(get_user(callback_query.from_user.id))
    user[3] = callback_data.get("name")
    update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer(f"""Успешно\nПоиск по преподавателю ({user[3]})""")


@dp.callback_query_handler(cb_group.filter())
async def user_reg(callback_query: types.CallbackQuery, callback_data: dict):
    create_table_users()
    create_profile_student(callback_query, callback_data.get('kurs'), callback_data.get('groups'))
    user = list(get_user(callback_query.from_user.id))
    user[0] = callback_data.get('kurs')
    user[1] = callback_data.get('groups')
    user[2] = 0
    update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer(f"Успешно\nПоиск по группе ({user[0]}: {user[1]})")


@dp.callback_query_handler(text="Нет")
async def callback_no(callback_query: types.CallbackQuery):
    user = list(get_user(callback_query.from_user.id))
    if user[2] == 0:
        user[2] = 1
        text = f"Успешно \nПоиск по преподавателю ({user[3]})"
    else:
        user[2] = 0
        text = f"Успешно \nПоиск по группе ({user[0]}: {user[1]})"
    update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer(text)


@dp.message_handler(commands=["today"])
async def today_rasp(message: types.Message):
    user = get_user(message.from_user.id)
    today = datetime.datetime.now()
    if user[2] == 0:
        text = await day_rasp(message, today)
    else:
        text = get_teach_rasp(today, message)

    await message.answer(text, parse_mode='html')


@dp.message_handler(commands=["next_day"])
async def next_day_rasp(message: types.Message):
    user = get_user(message.from_user.id)
    day = datetime.datetime.now() + datetime.timedelta(days=1)
    if day.weekday() == 6:
        day = day + datetime.timedelta(days=1)
    if user[2] == 0:
        text = await day_rasp(message, day)
    else:
        text = get_teach_rasp(day, message)

    await message.answer(text, parse_mode='html')


@dp.message_handler(commands=["week"])
async def week_rasp(message: types.Message):
    user = get_user(message.from_user.id)
    day = datetime.datetime.now()
    week_day = day.weekday()

    day = day - datetime.timedelta(days=week_day)

    if user[2] == 0:
        text = await day_rasp(message, day)
    else:
        text = get_teach_rasp(day, message)

    await message.answer(text, parse_mode='html')

    for i in range(1, 6):
        day = day + datetime.timedelta(days=1)
        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = get_teach_rasp(day, message)

        await message.answer(text, parse_mode='html')


@dp.message_handler(commands=["next_week"])
async def week_rasp(message: types.Message):
    user = get_user(message.from_user.id)
    day = datetime.datetime.now()
    week_day = day.weekday()

    day = day - datetime.timedelta(days=week_day) + datetime.timedelta(days=7)
    if user[2] == 0:
        text = await day_rasp(message, day)
    else:
        text = get_teach_rasp(day, message)
    await message.answer(text, parse_mode='html')
    for i in range(1, 6):
        day = day + datetime.timedelta(days=1)
        if user[2] == 0:
            text = await day_rasp(message, day)
        else:
            text = get_teach_rasp(day, message)

        await message.answer(text, parse_mode='html')


@dp.message_handler(commands=["teacher_or_student"])
async def teach_or_stud(message: types.Message):
    create_table_users()
    text = ''
    i_kb = InlineKeyboardMarkup()
    create_profile_teacher(message, '')
    user = list(get_user(message.from_user.id))
    if user[2] == 0:
        user[2] = 1
        if user[3] == '':
            await user_reg_teach(message)
        else:
            text = f"Изменить преподавателя?\n<i>{user[3]}</i>"
            ib = InlineKeyboardButton("Нет", callback_data='Нет')
            ib1 = InlineKeyboardButton("Да", callback_data='Преподаватель')
            i_kb.add(ib, ib1)

    else:
        if user[0] is None:
            await user_reg_kurs(message)
        else:
            text = f"Сменить группу/курс?\n<i>{user[0]}: {user[1]}</i>"
            ib = InlineKeyboardButton("Нет", callback_data='Нет')
            ib1 = InlineKeyboardButton("Да", callback_data='register')
            i_kb.add(ib, ib1)
    await message.delete()
    await message.answer(text, reply_markup=i_kb)

@dp.message_handler(commands=['day'])
async def choose_month(message: types.Message):
    today = datetime.datetime.now()
    str_month = today.strftime("%Y-%m-%d").split('-')[1]

    i_kb = InlineKeyboardMarkup(row_width=3)
    if int(str_month) < 9:
        for i in range(int(str_month), 9):
            ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
            i_kb.insert(ib)
    else:
        for i in range(int(str_month), 12):
            ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
            i_kb.insert(ib)
    # i_kb = InlineKeyboardMarkup(row_width=7)
    # for i in range(30):
    #     ib = InlineKeyboardButton(text = str(i), callback_data=str(i))
    #     i_kb.insert(ib)

    await message.answer("Выберите месяц:", reply_markup=i_kb)


@dp.callback_query_handler(text="choose_month")
async def choose_month(callback_query: types.CallbackQuery):
    today = datetime.datetime.now()
    str_month = today.strftime("%Y-%m-%d").split('-')[1]

    i_kb = InlineKeyboardMarkup(row_width=3)
    if int(str_month) < 9:
        for i in range(int(str_month), 9):
            ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
            i_kb.insert(ib)
    else:
        for i in range(int(str_month), 12):
            ib = InlineKeyboardButton(str(i), callback_data=cb_month.new(number=str(i)))
            i_kb.insert(ib)
    # i_kb = InlineKeyboardMarkup(row_width=7)
    # for i in range(30):
    #     ib = InlineKeyboardButton(text = str(i), callback_data=str(i))
    #     i_kb.insert(ib)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer("Выберите месяц:", reply_markup=i_kb)


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
    await callback_query.message.delete()
    await callback_query.message.answer("Выберите день:", reply_markup=i_kb)


@dp.callback_query_handler(cb_day.filter())
async def date_rasp(callback_query: types.CallbackQuery, callback_data: dict):
    today = datetime.datetime.now()
    user = get_user(callback_query.from_user.id)
    str_year = today.strftime("%Y-%m-%d").split('-')[0]
    str_date = str_year + '-' + callback_data.get('month') + '-' + callback_data.get('number')
    date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
    if user[2] == 0:
        text = await day_rasp(callback_query, date)
    else:
        text = get_teach_rasp(date, callback_query)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer(text, parse_mode='html')


# @dp.message_handler(content_types='text')
# async def reg_teacher(message: types.Message):
#     if get_user(message.from_user.id) is not None:
#         user = list(get_user(message.from_user.id))
#         if user[2] == 1 and user[3] == '':
#             user[3] = message.text
#             update_profile(message, user)
#             await message.answer("Успешно: Теперь вы преподаватель")



@dp.errors_handler()
async def error_bot_blocked_handler(update: types.Update, exception) -> bool:
    logger.error(f"{exception} : {update}")

    return True




if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
