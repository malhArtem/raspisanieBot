from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot_func import *
from aiogram import Bot, Dispatcher, types, executor
from config2 import *


bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    await db_start()
    print('Бот запущен')



@dp.message_handler(content_types=['new_chat_members'])
async def send_welcome(message: types.Message):
    await send_welcome_func(message)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await start_command_func(message)


@dp.message_handler(text=['Добавить в чат'])
async def add_chat(message: types.Message):
    await add_chat_func(message)


@dp.message_handler(commands=['huy'])
async def huy_command(message: types.Message):
    await huy_command_func(message)


@dp.message_handler(commands=['battle'])
async def battle_command(message: types.Message):
    await battle_command_func(message)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await help_command_func(message)


@dp.message_handler(commands=['profile'])
async def profile_command(message: types.Message):
    await profile_command_func(message)


@dp.message_handler(commands=['top'])
async def command_top(message: types.Message):
    await command_top_func(message)


@dp.message_handler(commands=['global_top'])
async def command_global_top(message: types.Message):
    await command_global_top_func(message)


@dp.callback_query_handler(text='huy')
async def callback_huy(callback_query: types.CallbackQuery):
    await callback_huy_func(callback_query)


@dp.callback_query_handler(cb_attack.filter())
async def callback_battle(callback_query: types.CallbackQuery, callback_data: dict):
    await callback_battle_func(callback_query, callback_data)






if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)