from app.pydb.database import Database
import sys
import os

filepath = 'db2.json'
if os.path.exists(filepath):
    os.remove(filepath)

db = Database(filepath)

columns = {
    'id': {'type': int(), 'PK': True, 'auto_inc': True},
    'name': {'type': str()},
    'age': {'type': int()}
}
db.add_table('users', columns)

db.insert_into_table('users', [9, 'Alice', 30])
db.insert_into_table('users', [2, 'Bob', 25])

columns = {
    'id': {'type': int(), 'auto_inc': True, 'PK': True},
    'user_id': {'type': int(), 'nullable': True, 'FK': {'table': 'users', 'column': 'id', 'on_update': 'set_null', 'on_delete': 'cascade'}}
}

db.add_table('orders', columns)

db.insert_into_table('orders', [1])
db.insert_into_table('orders', [2])
db.insert_into_table('orders', [2])

db.update_table('users', ['id'], [5], 'id', 1)

db.delete_from_table('users', 'id', 2)

print(db.select('users'))