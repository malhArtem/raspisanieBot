import sqlite3 as sq
from datetime import datetime
import random
import pytz

from aiogram import types
import openpyxl
from openpyxl.cell.cell import MergedCell
from config import *


def db_start():
    global db, cur
    db = sq.connect('rasp.db')
    cur = db.cursor()


def create_table_rasp(kurs):
    cur.execute("""CREATE TABLE IF NOT EXISTS '{}' 
                (day TEXT, time TEXT, group TEXT, subj TEXT, class TEXT)"""
                .format(kurs))
    db.commit()


def create_table_users():
    cur.execute("""CREATE TABLE IF NOT EXISTS users
        (user_id TEXT, username TEXT, name TEXT, kurs INTEGER, groupp TEXT, st_or_teach INTEGER, teacher TEXT)
        """)
    db.commit()


def create_profile_student(message: types.CallbackQuery, kurs, group):
    user = cur.execute("SELECT 1 FROM users WHERE user_id == '{}'"
                       .format(message.from_user.id)).fetchone()
    if not user:
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, message.from_user.full_name, kurs, group, 0, ''))
        db.commit()


def create_profile_teacher(message: types.CallbackQuery, teacher):
    user = cur.execute("SELECT 1 FROM users WHERE user_id == '{}'"
                       .format(message.from_user.id)).fetchone()
    if not user:
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, message.from_user.full_name, 0, 0, 1, teacher))
        db.commit()


def update_profile(callback_query: types.CallbackQuery, user: list):
    cur.execute(
        "UPDATE users SET username = '{}', name = '{}', kurs = '{}', groupp = '{}', st_or_teach = '{}', teacher = '{}' WHERE user_id = '{}'"
        .format(callback_query.from_user.username, callback_query.from_user.full_name, user[0], user[1], user[2],
                user[3], callback_query.from_user.id))
    db.commit()


def delete_profile(user_id):
    cur.execute("DELETE FROM users WHERE user_id = '{}'".format(user_id))
    db.commit()


def add_rasp(raw_table, kurs):
    cur.execute("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(kurs),
                (raw_table[0], raw_table[1], raw_table[2], raw_table[3], raw_table[4]))
    db.commit()


def get_rasp(day, kurs, group):
    cur.execute("SELECT * FROM '{}' WHERE day = '{}' AND groupp = '{}'".format(kurs, day, group))
    day_rasp = cur.fetchall()
    return day_rasp


def get_teachers():
    kurses = get_kurs()
    teachers = list()
    for kurs in kurses:
        if kurs[1] != 'users':
            cur.execute("SELECT DISTINCT teach1 FROM '{}' WHERE teach1 IS NOT NULL".format(kurs[1]))
            teachers.extend(cur.fetchall())
            cur.execute("SELECT DISTINCT teach3 FROM '{}' WHERE teach3 IS NOT NULL".format(kurs[1]))
            teachers.extend(cur.fetchall())
    unic_teach = list(set(teachers))
    return unic_teach


def get_user(user_id):
    cur.execute("SELECT kurs, groupp, st_or_teach, teacher FROM users WHERE user_id = '{}'".format(user_id))
    user = cur.fetchone()
    return user


def chisl_or_znam(now):
    delta = now - day_chisl
    if (delta.days // 7) % 2 == 0:
        return 3
    else:
        return 6


def cell_value(sheet, raw, col):
    cell = sheet[raw][col]
    coord = cell.coordinate
    if not isinstance(cell, MergedCell):
        return cell.value

    # "Oh no, the cell is merged!"
    for range in sheet.merged_cells.ranges:
        if coord in range:
            return range.start_cell.value

    raise AssertionError('Merged cell is not in any merge range!')


def get_kurs():
    cur.execute("SELECT * FROM sqlite_master WHERE type = 'table'")
    return cur.fetchall()


def get_groups(kurs):
    cur.execute("SELECT DISTINCT groupp FROM '{}'".format(kurs))
    groups = cur.fetchall()
    db.commit()
    return groups


def normalize(target_str):
    if target_str is None:
        target_str = ''
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in sokr.items():
        # меняем все target_str на подставляемое
        target_str = target_str.strip()
        target_str = (" ".join(target_str.split())).replace(i, j)
    return target_str


def sort_by_tyme(rasp: list):
    rasp = sorted(rasp, key=lambda para: datetime.strftime(para[1].split('-')[0], '%H.%M'))


def parse_date():
    book = openpyxl.open("xl.xlsx")
    sheet = book.active
    col = 2
    while (cell_value(sheet, 2, col)).value != None:
        col += 1
        row = 5
        while (cell_value(sheet, row, 1)).value != None:
            para: list
            para[0] = (cell_value(sheet, row, 0)).value
            para[1] = (cell_value(sheet, row, 1)).value
            para[2] = (cell_value(sheet, 4, col)).value
            para[3] = (cell_value(sheet, row, col)).value
            for i in range(len(para[3])):
                if para[3][i].isdigit:
                    para[4] = para[3][i:]
                    para[3] = para[3][:i]
                    break
                else:
                    i += 1
            create_table_rasp(cell_value(sheet, 1, col))
            add_rasp(para, cell_value(sheet, 1, col))


def get_teach_rasp(day, message):
    user = get_user(message.from_user.id)
    rasp = list()
    kurses = get_kurs()
    ch_or_zn = chisl_or_znam(day)
    for kurs in kurses:
        if kurs[1] != "users":
            if ch_or_zn == 3:
                cur.execute("SELECT *, '{}' FROM '{}' WHERE day = '{}' AND teach1 = '{}' ".format(kurs[1], kurs[1],
                                                                                                  day.weekday(),
                                                                                                  user[3]))
            else:
                cur.execute("SELECT *, '{}' FROM '{}' WHERE day = '{}' and teach3 = '{}' ".format(kurs[1], kurs[1],
                                                                                                  day.weekday(),
                                                                                                  user[3]))
            rasp1 = list(cur.fetchall())
            rasp.extend(rasp1)
    rasp = sorted(rasp, key=lambda para: datetime.datetime.strptime(para[1].split('-')[0], '%H.%M'))
    text = text = f'<b><u>{number_in_days.get(day.weekday())}</u></b>'
    text = f'<i>{user[3]}   [{day.strftime("%d.%m.%Y")}]</i>\n' + text
    if ch_or_zn == 3:
        text = text + '(числитель):\n\n'
    else:
        text = text + '(знаменатель):\n\n'
    if len(rasp) == 0:
        text = text + "Сегодня нет пар"
        return text
    k = 0

    for i in range(0, len(rasp)):
        if k != 0 and rasp[i][1] != rasp[i - 1][1]:
            text = text + f') [{rasp[i - 1][ch_or_zn + 2]}]\n\n'
            k = 0
        if rasp[i][ch_or_zn] is not None:
            if rasp[i][1] != rasp[i - 1][1] or i == 0:
                text = text + f'> <b><i>{rasp[i][1]}</i>:</b>\n'
                text = text + f'{normalize(rasp[i][ch_or_zn])} ({rasp[i][9]}: {rasp[i][2]}'
                k += 1
            else:
                text = text + f', {rasp[i][2]}'
    if k != 0:
        text = text + f') [{rasp[len(rasp) - 1][ch_or_zn + 2]}]\n\n'
        k = 0
    return text


async def day_rasp(message: types.Message, day):
    user = get_user(message.from_user.id)
    ch_or_zn = chisl_or_znam(day)
    rasp = list(get_rasp(day.weekday(), user[0], user[1]))
    text = f'<b><u>{number_in_days.get(day.weekday())}</u></b>'
    text = f'<i>{user[0]} {user[1]}   [{day.strftime("%d.%m.%Y")}]</i>\n' + text
    if ch_or_zn == 3:
        text = text + '(числитель):\n\n'
    else:
        text = text + '(знаменатель):\n\n'
    j = 1
    # for para in rasp:
    #     if para[chisl_or_znam(day_today)] is not None:
    #         text = text + f'{para[1]}:  {para[chisl_or_znam(day_today)]}\n'
    for l in range(1, len(rasp)):
        if rasp[0] == rasp[l]:
            j += 1

    for m in range(len(rasp) // j):
        for k in range(j):
            i = m + (len(rasp) // j) * k
            if (rasp[i][ch_or_zn] is not None and rasp[i][ch_or_zn] != rasp[m + (len(rasp) // j) * (k - 1)][
                ch_or_zn]) or (rasp[i][ch_or_zn] is not None and k == 0):
                text = text + f'> <b><i>{rasp[i][1]}</i>:</b>\n'

                if len(normalize(rasp[i][ch_or_zn + 1])) + len(normalize(rasp[i][ch_or_zn + 2])) > 0:
                    if len(normalize(rasp[i][ch_or_zn + 1])) + len(normalize(rasp[i][ch_or_zn + 2])) < 31 and len(
                            normalize(rasp[i][ch_or_zn])) \
                            + len(normalize(rasp[i][ch_or_zn + 1])) + len(normalize(rasp[i][ch_or_zn + 2])) > 31:
                        text = text + f'{normalize(rasp[i][ch_or_zn])}\n{normalize(rasp[i][ch_or_zn + 1])} [{normalize(rasp[i][ch_or_zn + 2])}]'

                    elif (len(normalize(rasp[i][ch_or_zn])) + len(normalize(rasp[i][ch_or_zn + 1])) + len(
                            normalize(rasp[i][ch_or_zn + 2])) < 27) \
                            or (
                            len((normalize(rasp[i][ch_or_zn]))) < 20 and len(normalize(rasp[i][ch_or_zn + 1])) + len(
                        normalize(rasp[i][ch_or_zn + 2])) < 19):
                        if len((normalize(rasp[i][ch_or_zn]))) > 13:
                            text = text + f'{normalize(rasp[i][ch_or_zn])[:13]}... {normalize(rasp[i][ch_or_zn + 1])} [{normalize(rasp[i][ch_or_zn + 2])}]'
                        else:
                            text = text + f'{normalize(rasp[i][ch_or_zn])[:13]} {normalize(rasp[i][ch_or_zn + 1])} [{normalize(rasp[i][ch_or_zn + 2])}]'
                    elif len(normalize(rasp[i][ch_or_zn + 2])) and len(normalize(rasp[i][ch_or_zn])) + len(
                            normalize(rasp[i][ch_or_zn + 1])) < 31:
                        text = text + f'{normalize(rasp[i][ch_or_zn])} {normalize(rasp[i][ch_or_zn + 1])}\n[{normalize(rasp[i][ch_or_zn + 2])}]'

                    elif len(normalize(rasp[i][ch_or_zn])) + len(normalize(rasp[i][ch_or_zn + 1])) > 31 and len(
                            normalize(rasp[i][ch_or_zn + 1])) + len(normalize(rasp[i][ch_or_zn + 2])) > 31:
                        text = text + f'{normalize(rasp[i][ch_or_zn])}\n{normalize(rasp[i][ch_or_zn + 1])}\n[{normalize(rasp[i][ch_or_zn + 2])}]'

                    else:
                        text = text + f'{normalize(rasp[i][ch_or_zn])} {normalize(rasp[i][ch_or_zn + 1])} [{normalize(rasp[i][ch_or_zn + 2])}]'
                else:
                    text = text + f'{normalize(rasp[i][ch_or_zn])}'
                if k > 0:
                    text = text + f' ({k + 1})\n\n'
                else:
                    text = text + '\n\n'
        # if rasp[i][ch_or_zn] is not None:
        #     if rasp[i][ch_or_zn + 1] is None and rasp[i][ch_or_zn+2] is None:
        #     text = text + f'> <b><i>{" ".join(rasp[i][1].split())}</i>:\n</b>{normalize(rasp[i][ch_or_zn])}\n\n'
        # else:
        #     for k in range(j):
        #         if rasp[i + (len(rasp)//j)*k][ch_or_zn] is not None:
        #             text = text + f'> <b><i>{rasp[i + (len(rasp)//j)*k][1]}</i>:\n</b>{normalize(rasp[i + (len(rasp)//j)*k][ch_or_zn])} ({k+1})\n\n'
        #             break
    return text

# text = text + f'> <b><i>{" ".join(rasp[i][1].split())}</i>:\n</b>
