import random
import sqlite3
from pathlib import Path

conn = sqlite3.connect('database2.db')
cursor = conn.cursor()

INSTRUMENT_PATH = 'values/instuments.txt'
MODELS_PATH = 'values/models.txt'
NAMES_PATH = 'values/names.txt'
SURNAME_PATH = 'values/surnames.txt'
DATE_PATH = 'values/date.txt'
MOUNTH_PATH = 'values/mounth.txt'
TIME_PATH = 'values/time.txt'

INSTRUMENT_ARRAY = [w for w in Path(INSTRUMENT_PATH).read_text(encoding="utf-8").split('\n')]
MODELS_ARRAY = [w for w in Path(MODELS_PATH).read_text(encoding="utf-8").split('\n')]
NAMES_ARRAY = [w for w in Path(NAMES_PATH).read_text(encoding="utf-8").split('\n')]
SURNAME_ARRAY = [w for w in Path(SURNAME_PATH).read_text(encoding="utf-8").split('\n')]
DATE_ARRAY = [w for w in Path(DATE_PATH).read_text(encoding="utf-8").split('\n')]
MOUNTH_ARAY = [w for w in Path(MOUNTH_PATH).read_text(encoding="utf-8").split('\n')]
TIME_ARRAY = [w for w in Path(TIME_PATH).read_text(encoding="utf-8").split('\n')]


def get_inst_combo(m_arr, i_arr):
    result_arr = []
    for i in range(0, (len(m_arr) * len(m_arr))):
        result_arr.append([i, i_arr[random.randint(0, len(m_arr) - 1)], m_arr[random.randint(0, len(m_arr) - 1)]])
    return result_arr


def get_name_surname_combo(n_arr, s_arr):
    result_arr = []
    for i in range(0, (len(n_arr) * len(n_arr))):
        result_arr.append([i, s_arr[random.randint(0, len(n_arr) - 1)], n_arr[random.randint(0, len(n_arr) - 1)]])
    return result_arr


def get_order_item():
    res_arr = []
    for i in range(0, len(NAMES_ARRAY) * len(NAMES_ARRAY)):
        res_arr.append([i, random.randint(0, (len(NAMES_ARRAY) * len(NAMES_ARRAY))), random.randint(1, 500)])

    return res_arr


def get_order_list(d_arr, m_arr, t_arr):
    res_arr = []
    for i in range(0, len(NAMES_ARRAY) * len(NAMES_ARRAY)):
        date = d_arr[random.randint(0, len(d_arr) - 1)] + m_arr[random.randint(0, len(m_arr) - 1)] + t_arr[
            random.randint(0, len(t_arr) - 1)]
        flag = random.randint(0, 2)
        if flag == 0:
            res_arr.append([i, random.randint(0, 1000), random.randint(0, 1000), date, 'waiting for loading'])
        if flag == 1:
            res_arr.append([i, random.randint(0, 1000), random.randint(0, 1000), date, 'on the way'])
        if flag == 2:
            res_arr.append([i, random.randint(0, 1000), random.randint(0, 1000), date, 'handed to the customer'])

    return res_arr


def create_base():
    cursor.execute("""CREATE TABLE IF NOT EXISTS item 
                            (item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_name TEXT,
                            item_model TEXT
                            )""")
    cursor.execute("delete from item")

    cursor.execute("""CREATE TABLE IF NOT EXISTS order_item
                            (
                            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_id INT,
                            amount_of_items_at_order INT,
                            FOREIGN KEY(item_id) REFERENCES item(item_id)
                            )""")

    cursor.execute("delete from order_item")

    cursor.execute("""CREATE TABLE IF NOT EXISTS order_list
                            (
                            order_list_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            order_id INT,
                            manager_id INT,
                            order_date TEXT,
                            status TEXT,
                            FOREIGN KEY(order_id) REFERENCES order_item(order_id),
                            FOREIGN KEY(manager_id) REFERENCES manager(manager_id)
                            )""")
    cursor.execute("delete from order_list")

    cursor.execute("""CREATE TABLE IF NOT EXISTS manager
                            (
                            manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            surname TEXT,
                            name TEXT
                            )""")
    cursor.execute("delete from manager")

    Instr_and_models = get_inst_combo(MODELS_ARRAY, INSTRUMENT_ARRAY)
    for i in range(0, (len(MODELS_ARRAY) * len(MODELS_ARRAY))):
        cursor.execute("insert into item values (?, ?, ?);", Instr_and_models[i])

    names_and_surnames = get_name_surname_combo(NAMES_ARRAY, SURNAME_ARRAY)
    for i in range(0, (len(MODELS_ARRAY) * len(MODELS_ARRAY))):
        cursor.execute("insert into manager values (?, ?, ?);", names_and_surnames[i])

    for_order_item = get_order_item()
    for i in range(0, len(MODELS_ARRAY) * len(MODELS_ARRAY)):
        cursor.execute("insert into order_item values (?, ?, ?);", for_order_item[i])

    for_oder_list_arr = get_order_list(DATE_ARRAY, MOUNTH_ARAY, TIME_ARRAY)
    for i in range(0, len(MODELS_ARRAY) * len(MODELS_ARRAY)):
        cursor.execute("insert into order_list values (?, ?, ?, ?, ?);", for_oder_list_arr[i])

    conn.commit()


if __name__ == '__main__':
    create_base()
