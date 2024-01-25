import sqlite3 as sq
from utils import get_project_root

def sql_start():
    global base, cur
    db = get_project_root('nisprepdb.db')
    base = sq.connect(db)
    cur = base.cursor()
    if base:
        print('Database connected!')
    base.execute('CREATE TABLE IF NOT EXISTS tests(file TEXT, name TEXT PRIMARY KEY, subject TEXT)')
    base.commit()

async def sql_add_tests(state):
    a = await state.get_data()
    cur.execute('INSERT INTO tests VALUES (?, ?, ?)', tuple(a.values()))
    base.commit()

async def sql_get_tests(subject):
    tests = cur.execute('SELECT * FROM tests WHERE subject == ?', (subject, )).fetchall()
    return tests

async def sql_get_tests_subjects():
    subjects = cur.execute('SELECT DISTINCT subject FROM tests').fetchall()
    return subjects

async def sql_get_test(data):
    test = cur.execute('SELECT * FROM tests WHERE name == ?', (data, )).fetchone()
    return test