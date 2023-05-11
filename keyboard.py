from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from attr import ib

kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton(text="/huy")

kb.add(b1)

cb_kurs = CallbackData("kurs", "number")
cb_group = CallbackData("group", "kurs", "groups")
cb_month = CallbackData("month", "number")
cb_day = CallbackData("day", "month", "number")
cb_teacher = CallbackData("teacher", "name")
# i_kb_kurs = InlineKeyboardMarkup(row_width=3)
#
# ib1 = InlineKeyboardButton("1 курс", callback_data= cb_kurs.new(number = "1 курс"))
# ib2 = InlineKeyboardButton("2 курс", callback_data= cb_kurs.new(number = "2 курс"))
# ib3 = InlineKeyboardButton("3 курс", callback_data= cb_kurs.new(number = "3 курс"))
# ib4 = InlineKeyboardButton("4 курс", callback_data= cb_kurs.new(number = "4 курс"))
# ib5 = InlineKeyboardButton("5 курс", callback_data= cb_kurs.new(number = "5 курс"))
# ib6 = InlineKeyboardButton("Магистры 1 курс", callback_data= cb_kurs.new(number = "Магистры 1 курс"))
# ib7 = InlineKeyboardButton("Магистры 2 курс", callback_data= cb_kurs.new(number = "Магистры 2 курс"))
# i_kb_kurs.add(ib1, ib2)
# i_kb_kurs.add(ib3, ib4, ib5)
# i_kb_kurs.add(ib6, ib7)


# def make_keyboard_groups(kurs):
#     groups = get_groups(kurs)
#     i_kb_groups = InlineKeyboardMarkup()
#     i = 0
#     for group in groups:
#             ib = InlineKeyboardButton(text=group[0])
#             i_kb_groups.row(ib)
#             i += 1
#             if i % 3 == 0:
#                 i_kb_groups.add()


# groups = get_groups(kurs)
# i_kb_groups = InlineKeyboardMarkup()
# i = 0
# for group in groups:
#     ib = InlineKeyboardButton(text=group[0])
#     i_kb_groups.row(ib)
#     i += 1
#     if i % 3 == 0:
#         i_kb_groups.add()

