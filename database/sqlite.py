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
    base.commit()

async def sql_add_tests(state):
    data = await state.get_data()
    cur.execute('INSERT INTO tests VALUES (?, ?, ?, ?)', tuple(data.values()))
    base.commit()

async def sql_add_materials(state):
    data = await state.get_data()
    cur.execute('INSERT INTO materials VALUES (?, ?, ?, ?)', tuple(data.values()))
    base.commit()

async def sql_get_tests(subject):
    if subject:
        tests = cur.execute('SELECT * FROM tests WHERE subject == ?', (subject, )).fetchall()
    else:
        tests = cur.execute('SELECT * FROM tests').fetchall()
    return tests

async def sql_get_materials(subject):
    if subject:
        materials = cur.execute('SELECT * FROM materials WHERE subject == ?', (subject, )).fetchall()
    else:
        materials = cur.execute('SELECT * FROM materials').fetchall()
    return materials

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