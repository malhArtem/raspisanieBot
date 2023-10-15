from aiogram.utils.callback_data import CallbackData


cb_kurs = CallbackData("kurs", "number")
cb_group = CallbackData("group", "kurs", "groups")
cb_month = CallbackData("month", "number")
cb_day = CallbackData("day", "month", "number")
cb_teacher = CallbackData("teacher", "name")

cb_pag_teacher = CallbackData("pag_teacher", "pag")
