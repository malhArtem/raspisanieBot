import openpyxl
from openpyxl.cell.cell import MergedCell
import sqlite3 as sq

from pymongo import cursor


# book = openpyxl.open("xl.xlsx")
# sheet = book.active
#
#
#
# def cell_value(sheet, raw, col):
#   cell = sheet[raw][col]
#   coord = cell.coordinate
#   if not isinstance(cell, MergedCell):
#     return cell.value
#
#   # "Oh no, the cell is merged!"
#   for range in sheet.merged_cells.ranges:
#     if coord in range:
#       return range.start_cell.value
#
#   raise AssertionError('Merged cell is not in any merge range!')
#
#
# book = openpyxl.open("xl.xlsx")
# sheet = book.active
#
# print(sheet.merged_cells.ranges)
#
# for raw in range(2,21):
#     for col in range(13):
#         cell = sheet[raw][col]
#         print("\t", cell.coordinate, cell_value(sheet, raw, col), end=' ')
#     print()




def db_start():
    global db, cur
    db = sq.connect('rasp.db')
    cur = db.cursor()


def create_table_rasp(kurs):
    cur.execute("""CREATE TABLE IF NOT EXISTS '{}' 
                (day TEXT, time TEXT, groupp TEXT, subj1 TEXT, teach1 TEXT, clas1 TEXT, subj2 TEXT, teach3 TEXT, clas2 TEXT)"""
                .format(kurs))

    # cur.execute("""CREATE TABLE IF NOT EXISTS users
    #     (user_id TEXT, username TEXT, name TEXT, kurs INTEGER, group TEXT)
    #     """)
    db.commit()


def add_rasp(raw_table: list, kurs):
    cur.execute("INSERT INTO '{}' VALUES(?,?,?,?,?,?,?,?,?)".format(kurs),
                (raw_table[0], raw_table[1], raw_table[2], raw_table[3], raw_table[4], raw_table[5], raw_table[6], raw_table[7], raw_table[8]))
    db.commit()


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


number_in_days = {0: 'Понедельник',
                  1: 'Вторник',
                  2: 'Среда',
                  3: 'Четверг',
                  4: 'Пятница',
                  5: 'Суббота'}

days_in_number = {'Понедельник': 0,
                  'Вторник': 1,
                  'Среда': 2,
                  'Четверг': 3,
                  'Пятница': 4,
                  'Суббота': 5}

def cut_teach(s: str):
    split_s = list()
    if s is not None:
        list_s = s.split()
        j = len(list_s)
        for i in range(len(list_s)):
            if len(list_s[i]) == 4:
                if list_s[i][0].isalpha() and list_s[i][1]== '.' and list_s[i][2].isalpha() and list_s[i][3]== '.':
                    j = i
                    break
        if j == len(list_s):
            split_s.append(" ".join(list_s))
            split_s.append(None)
            split_s.append(None)
        else:
            split_s.append(" ".join(list_s[:j - 1]))
            split_s.append(" ".join(list_s[j - 1: j + 1]))
            split_s.append(" ".join(list_s[j+1:]))

        if split_s[1] is None and split_s[0] is not None:
            for i in range(len(split_s[0])-3):
                if (split_s[0][i].isalpha() and split_s[0][i].istitle()) and split_s[0][i+1] == '.' and (split_s[0][i+2].isalpha() and split_s[0][i+2].istitle()) and (split_s[0][i+3] =='.' or split_s[0][i+3].isspace()):
                    j = i

                    spaces = 0
                    while spaces != 2 and j != 0:
                        if split_s[0][j].isspace():
                            j += -1
                            spaces += 1
                        else:
                            j += -1

                    split_s[1] = split_s[0][j+1: i+4].strip()
                    split_s[2] = split_s[0][i+4:].strip()
                    split_s[0] = split_s[0][:j+1].strip()
                    if split_s[1][-1] != '.':
                        split_s[1] = split_s[1] + '.'

                    break
        if split_s[1] is not None:
            for i in range(len(split_s[1])):
                if split_s[1][i:].istitle():
                    split_s[0] = split_s[0] + split_s[1][:i]
                    split_s[1] = split_s[1][i:]
                    break
    else:
        split_s.append(None)
        split_s.append(None)
        split_s.append(None)
    return split_s

def parse_kurs(col_begin):
    book = openpyxl.open("xl.xlsx")
    sheet = book.active

    corr = 0
    if cell_value(sheet, 3, col_begin) == 'Дни недели':
        corr += 1
    if cell_value(sheet, 3, col_begin + 1) == 'Часы звонков':
        corr += 1

    col = corr + col_begin

    while (cell_value(sheet, 4, col)) is not None:
        row = 5
        group_para = list()
        while row != sheet.max_row:
            if cell_value(sheet, row, 1) is not None:
                para = list()
                para.append(cell_value(sheet, row, 0))
                para.append(cell_value(sheet, row, 1))
                para.append(cell_value(sheet, 4, col))
                # para.append(cell_value(sheet, row, col))
                # para.append(cell_value(sheet, row + 1, col))
                para.extend(cut_teach(cell_value(sheet, row, col)))
                para.extend(cut_teach(cell_value(sheet, row + 1, col)))

                para[0] = days_in_number.get(para[0])

                for i in range(1, len(para[2])):
                    if para[2][len(para[2]) - i].isalpha() and para[2][len(para[2]) - i] != '.':
                        para[2] = para[2][len(para[2]) - i + 2:]
                        break

                if para[2] == '':
                    para[2] = cell_value(sheet, 4, col)
                    for i in range(len(para[2])):
                        if para[2].isspace():
                            para[2] = para[2][:i]
                            break

                if len(para[2]) > 10:
                    para[2] = (para[2].split())[0]



                group_para.append(para)

                row += 2
            else:
                row += 1


        create_table_rasp(cell_value(sheet, 2, col))
        for par in group_para:
            add_rasp(par, cell_value(sheet, 2, col))

        col += 1
        if col == sheet.max_column:
            break

def parse_xl():
    book = openpyxl.open("xl.xlsx")
    sheet = book.active
    print(sheet.max_row)
    print(sheet.max_column)
    col_begin = 0
    parse_kurs(col_begin)
    for j in range(sheet.max_column):
        if (cell_value(sheet, 4, j)) is None:
            j += 1
            col_begin = j
            parse_kurs(col_begin)

def all_subj():
    cur.execute("SELECT DISTINCT subj1, subj2 FROM [4 курс]")
    file = open('file.txt', "w")
    subjs = cur.fetchall()
    for subj in subjs:
        if subj[0] is not None:
            file.write(subj[0] + "\n")
        if subj[1] is not None:
            file.write(subj[1] + "\n")






db_start()
parse_xl()
# all_subj()
print(1)

# s = input()
# cut_teach(s)
