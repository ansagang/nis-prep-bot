import sqlite3 as sq

from utils import get_project_root

def sql_start():
    global base, cur
    db = get_project_root('nisprepdb.db')
    base = sq.connect(db)
    cur = base.cursor()
    if base:
        print('Database connected!')
    base.execute('CREATE TABLE IF NOT EXISTS tests(file TEXT, name TEXT, subject TEXT, id TEXT PRIMARY KEY)')
    base.execute('CREATE TABLE IF NOT EXISTS materials(photo TEXT, name TEXT, subject TEXT, id TEXT PRIMARY KEY)')
    base.execute('CREATE TABLE IF NOT EXISTS testing(photo TEXT, answer TEXT, subject TEXT, number TEXT, id TEXT)')
    # base.execute("DROP TABLE users")
    base.execute('CREATE TABLE IF NOT EXISTS users(uid INT, current_question INTEGER, questions_passed INTEGER, questions_message INTEGER, in_process INTEGER, testing_id TEXT, result TEXT, username TEXT)')
    base.commit()

async def sql_add_tests(state):
    data = await state.get_data()
    cur.execute('INSERT INTO tests VALUES (?, ?, ?, ?)', tuple(data.values()))
    base.commit()

async def sql_add_materials(state):
    data = await state.get_data()
    cur.execute('INSERT INTO materials VALUES (?, ?, ?, ?)', tuple(data.values()))
    base.commit()

async def sql_add_testing(state):
    data = await state.get_data()
    cur.execute('INSERT INTO testing VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
    base.commit()

async def sql_get_tests(subject):
    if subject:
        tests = cur.execute('SELECT * FROM tests WHERE subject == ? ORDER BY id ASC', (subject, )).fetchall()
    else:
        tests = cur.execute('SELECT * FROM tests').fetchall()
    return tests

async def sql_get_materials(subject):
    if subject:
        materials = cur.execute('SELECT * FROM materials WHERE subject == ? ORDER BY id ASC', (subject, )).fetchall()
    else:
        materials = cur.execute('SELECT * FROM materials').fetchall()
    return materials

async def sql_get_testing_id():
    ids = cur.execute('SELECT DISTINCT id FROM testing').fetchall()
    return ids

async def sql_get_testing(id):
    testing = cur.execute('SELECT * FROM testing WHERE id == ? ORDER BY subject, CAST(number AS INT) ASC', (id, )).fetchall()
    return testing

async def sql_delete_testing(data):
    cur.execute('DELETE FROM testing WHERE id == ?', (data, ))
    base.commit()


async def sql_get_tests_subjects():
    subjects = cur.execute('SELECT DISTINCT subject FROM tests').fetchall()
    return subjects

async def sql_get_materials_subjects():
    subjects = cur.execute('SELECT DISTINCT subject FROM materials').fetchall()
    return subjects

async def sql_get_test(data):
    test = cur.execute('SELECT * FROM tests WHERE id == ?', (data, )).fetchone()
    return test

async def sql_get_material(data):
    material = cur.execute('SELECT * FROM materials WHERE id == ?', (data, )).fetchone()
    return material

async def sql_delete_test(data):
    cur.execute('DELETE FROM tests WHERE id == ?', (data, ))
    base.commit()

async def sql_delete_material(data):
    cur.execute('DELETE FROM materials WHERE id == ?', (data, ))
    base.commit()

async def sql_random_test():
    test = cur.execute('SELECT * FROM tests ORDER BY RANDOM() LIMIT 1').fetchone()
    return test

async def sql_random_material():
    material = cur.execute('SELECT * FROM materials ORDER BY RANDOM() LIMIT 1').fetchone()
    return material



def add(uid: int, testing_id):
    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (uid, 0, 0, 0, 0, testing_id, "", ""))
    base.commit()


def delete(uid: int, testing_id):
    cur.execute("DELETE FROM users WHERE uid=(?) AND testing_id=(?)", (uid, testing_id))
    base.commit()


def is_exists(uid: int, testing_id):
    cur.execute("SELECT * FROM users WHERE uid=(?) AND testing_id=(?)", (uid, testing_id))
    return bool(cur.fetchall())


def set_in_process(uid: int, v: bool, testing_id):
    cur.execute("UPDATE users SET in_process=(?) WHERE uid=(?) AND testing_id=(?)", (1 if v else 0, uid, testing_id))


def is_in_process(uid: int, testing_id):
    cur.execute("SELECT in_process FROM users WHERE uid=(?) AND testing_id=(?)", (uid, testing_id))
    return bool(int(cur.fetchone()[0]))


def get_current_questions(uid: int, testing_id):
    cur.execute("SELECT current_question FROM users WHERE uid=(?) AND testing_id=(?)", (uid, testing_id))
    return int(cur.fetchone()[0])


def change_current_question(uid: int, v: int, testing_id):
    cur.execute("UPDATE users SET current_question=(?) WHERE uid=(?) AND testing_id=(?)", (v, uid, testing_id))
    base.commit()


def change_questions_passed(uid: int, v: int, testing_id):
    cur.execute("UPDATE users SET questions_passed=(?) WHERE uid=(?) AND testing_id=(?)", (v, uid, testing_id))
    base.commit()


def get_questions_passed(uid: int, testing_id):
    cur.execute("SELECT questions_passed FROM users WHERE uid=(?) AND testing_id=(?)", (uid, testing_id))
    return int(cur.fetchone()[0])


def get_questions_message(uid: int, testing_id):
    cur.execute("SELECT questions_message FROM users WHERE uid=(?) AND testing_id=(?)", (uid, testing_id))
    return int(cur.fetchone()[0])


def change_questions_message(uid: int, v: int, testing_id):
    cur.execute("UPDATE users SET questions_message=(?) WHERE uid=(?) AND testing_id=(?)", (v, uid, testing_id))
    base.commit()

def change_user(uid: int, testing_id, result, username):
    cur.execute("UPDATE users SET result=(?), username=(?) WHERE uid=(?) AND testing_id=(?)", (result, username, uid, testing_id))
    base.commit()

def get_user(uid: int):
    user = cur.execute("SELECT * FROM users WHERE uid=(?)", (uid, )).fetchall()
    return user

def get_leaderboard(testing_id):
    users = cur.execute("SELECT * FROM users WHERE testing_id=(?) ORDER BY CAST(result AS int) DESC", (testing_id, )).fetchall()
    return users