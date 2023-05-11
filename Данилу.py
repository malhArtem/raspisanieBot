from aiogram.utils.callback_data import CallbackData


cb_kurs = CallbackData("kurs", "number") """колбэки для выбора курса (kurs - префикс по которому будут фильтроваться колбэки в хендлере (изменять при создании кнопки не надо, 
                                            number - данные которые будут передаваться в колбеке (их и нужно измеенять при создании кнопки"""
cb_group = CallbackData("group", "kurs", "groups") #колбэки для выбора группы в курсе
cb_month = CallbackData("month", "number") #колбэки для выбора месяца
cb_day = CallbackData("day", "month", "number") #колбэки для выбора дня в месяце
cb_teacher = CallbackData("teacher", "name")

#команда в самом начале
@dp.message_handler(commands=['start'])     
async def user_reg_kurs(message: types.Message):
    i_kb_kurs = InlineKeyboardMarkup(row_width=2)
    kurses = get_kurs() #получил список курсов
    for kurs in kurses:
        if kurs[1] != 'users':
            ib = InlineKeyboardButton(kurs[1], callback_data=cb_kurs.new(number=kurs[1])) #создаю кнопки в цикле с данными из списка курсов
            i_kb_kurs.insert(ib) #доабвляем кнопку (именно insert иначе игнорируется ширина клавиатуры или добавляются все в столбик)
    ib = InlineKeyboardButton("Я преподаватель", callback_data='Преподаватель')
    i_kb_kurs.add(ib)
    await message.delete()
    await message.answer("Выберите ваш курс!", reply_markup=i_kb_kurs)
    
   
#команда для перерегистрации  
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


#фильтрация колбэека по классу cb_kurs        
@dp.callback_query_handler(cb_kurs.filter())
async def user_reg_group(callback_query: types.CallbackQuery, callback_data: dict): #передаем в функцию не только query а еще и callback_data
    groups = get_groups(callback_data.get('number'))  #callback_data.get('number') получаем данные из словаря по ключевому полю number и после получеаем список групп из БД в этом курсе
    i_kb_groups = InlineKeyboardMarkup(row_width=3)

    for i in range(len(groups)):
        ib = InlineKeyboardButton(str(groups[i][0]), callback_data=cb_group.new(kurs=str(callback_data.get('number')), # создаем кнопки, но теперь передаем туда курс из прошлой кнопки и группу
                                                                                groups=groups[i][0]))
        i_kb_groups.insert(ib)
    ib = InlineKeyboardButton('<', callback_data='kurs')
    i_kb_groups.add(ib)
    await callback_query.message.delete()
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Выберите группу", reply_markup=i_kb_groups)
    
 #фильтрация колбэека по классу cb_group    
@dp.callback_query_handler(cb_group.filter()) 
async def user_reg(callback_query: types.CallbackQuery, callback_data: dict):
    create_table_users()
    create_profile_student(callback_query, callback_data.get('kurs'), callback_data.get('groups')) #создаю профиль студента в базе данных извлекая курс и группу из переданного словаря callback_data
    user = list(get_user(callback_query.from_user.id))
    user[0] = callback_data.get('kurs')
    user[1] = callback_data.get('groups')
    user[2] = 0
    update_profile(callback_query, user)
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await callback_query.message.answer(f"Успешно\nПоиск по группе ({user[0]}: {user[1]})")
