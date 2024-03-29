import sqlite3
import aiosqlite
import datetime
import contextlib


async def create_main_tables(path_to_db, db_customers):
    """
    Создание основных таблиц
    """
    create_main_table = (f'CREATE TABLE IF NOT EXISTS main_customers ("phone" TEXT UNIQUE, "user_id" TEXT '
                         f'UNIQUE, "register_date" TEXT)')

    create_qr_table = (
        f'CREATE TABLE IF NOT EXISTS qr_table ("phone" TEXT, "user_id" TEXT, "date_of_purchase" TEXT, "summa" TEXT, '
        f'"fn" TEXT, "qr_index" TEXT, "status" TEXT)')

    create_bonus_table = (f'CREATE TABLE IF NOT EXISTS bonus_table ("phone" '
                          f'TEXT, "user_id" TEXT, "volume" TEXT, "bonus_date" TEXT)')

    try:
        async with aiosqlite.connect(f'{path_to_db}\\{db_customers}') as db:
            async with db.cursor() as cur:
                await cur.execute(create_main_table)
                await cur.execute(create_qr_table)
                await cur.execute(create_bonus_table)
            await db.commit()
    except Exception as e:
        print('Error:', e)


def add_to_qr(user_id, date_of_purchase, summa, fn, index, path_to_db, db_customers) -> int:
    """
    Добавляет чек пользоваетля в базу данных (в таблицу qr_table) и возвращает в конце количество записей
    пользователя в этой таблице, чтобы сообщить пользователю в случае достаточного количества чеков, что он может
    забрать свой бонус
    """
    phone = find_phone(user_id, path_to_db, db_customers)
    values = (phone, user_id, date_of_purchase, summa, fn, index, "True")
    request = (f"INSERT INTO qr_table (phone, user_id, date_of_purchase, summa, fn, qr_index, status) VALUES (?, ?, "
               f"?, ?, ?, ?, ?)")

    try:
        with contextlib.closing(sqlite3.connect(rf'{path_to_db}\\{db_customers}')) as db:
            with db as cur:
                cur.execute(request, values)
            db.commit()
        return check_bonus_coffee(phone, path_to_db, db_customers)
    except Exception as e:
        print('Error:', e)
        return -1


def find_phone(user_id, path_to_db, db_customers) -> str:
    values = (user_id, )
    query = f"SELECT phone FROM main_customers WHERE user_id = ?"

    conn = sqlite3.connect(rf"{path_to_db}\\{db_customers}")
    cursor = conn.cursor()

    cursor.execute(query, values)
    res = cursor.fetchone()

    conn.close()

    return res[0]


def check_bonus_coffee(phone, path_to_db, db_customers):
    conn = sqlite3.connect(rf"{path_to_db}\\{db_customers}")
    cursor = conn.cursor()

    values = (phone, )
    query = f"SELECT COUNT(*) FROM qr_table WHERE phone = ?"

    cursor.execute(query, values)
    res = cursor.fetchall()

    conn.close()

    return res[0][0]


def check_bonus_coffee_by_user(user_id, path_to_db, db_customers):
    """
    Функция для пользователя, когда он хочет узнать свой статус до бонуса
    """
    conn = sqlite3.connect(rf"{path_to_db}\\{db_customers}")
    cursor = conn.cursor()

    values = (user_id, "True")
    query = f"SELECT COUNT(*) FROM qr_table WHERE user_id = ? and status = ?"

    cursor.execute(query, values)
    res = cursor.fetchall()

    conn.close()

    return res[0][0]


def fill_customers(path_to_db, db_customers, phone_number, user_id) -> bool:
    """
    Заполняет таблицу main_customers - в нее записываются впервые зарегестрированные в бонусной программе
    пользователи
    """
    today = str(datetime.datetime.today()).replace('-', '.')

    values = (phone_number, user_id, today)
    request = f'INSERT INTO main_customers (phone, user_id, register_date) VALUES (?, ?, ?)'

    try:
        with contextlib.closing(sqlite3.connect(rf'{path_to_db}\\{db_customers}')) as db:
            with db as cur:
                cur.execute(request, values)
            db.commit()
        return True
    except Exception as e:
        print('Error:', e)
        return False


def find_client(phone_number, path_to_db, db_customers) -> int:
    conn = sqlite3.connect(rf"{path_to_db}\\{db_customers}")
    cursor = conn.cursor()

    query = f"SELECT COUNT(*) FROM qr_table WHERE phone = ?"
    value = (phone_number,)

    cursor.execute(query, value)
    res = cursor.fetchall()

    conn.close()
    return res[0][0]
