from app.pydb.database import Database
import time
import os

# Setup a temporary database file
db_path = 'test_db.json'
if os.path.exists(db_path):
    os.remove(db_path)
db = Database(db_path)

# Add tables with complex relationships
db.add_table(
    table_name='users',
    columns={
        'user_id': {'type': int(), 'auto_inc': True, 'PK': True},
        'username': {'type': str()}
    }
)

db.add_table(
    table_name='posts',
    columns={
        'post_id': {'type': int(), 'auto_inc': True, 'PK': True},
        'user_id': {
            'type': int(), 'FK': {
                'table': 'users',
                'column': 'user_id',
                'on_update': 'cascade',
                'on_delete': 'cascade'
            }
        },
        'content': {'type': str()}
    }
)

db.add_table(
    table_name='comments',
    columns={
        'comment_id': {'type': int(), 'auto_inc': True, 'PK': True},
        'post_id': {
            'type': int(), 'FK': {
                'table': 'posts',
                'column': 'post_id',
                'on_update': 'cascade',
                'on_delete': 'cascade'
            }
        },
        'user_id': {
            'type': int(), 'FK': {
                'table': 'users',
                'column': 'user_id',
                'on_update': 'cascade',
                'on_delete': 'cascade'
            }
        },
        'comment': {'type': str()}
    }
)

# Insert initial data
db.insert_into_table('users', [1, 'user1'])
db.insert_into_table('users', [2, 'user2'])
db.insert_into_table('posts', [1, 1, 'First post'])
db.insert_into_table('posts', [1, 'asdf'])
db.insert_into_table('posts', [1, 'aasdf43'])
#db.insert_into_table('posts', [2, 2, 'Second post'])

# Insert a comment with valid foreign keys
db.insert_into_table('comments', [1, 1, 2, 'Nice post!'])
comments = db.select('comments', [], {'comment_id': 1})
print("Comments after valid insert:", comments)
# print("Comments after valid insert:", comments)

# Attempt to insert a comment with an invalid post_id
db.insert_into_table('comments', [2, 3, 1, 'Invalid post'])
#comments = db.select('comments')
# print("Comments after invalid post_id insert:", comments)

# Attempt to insert a comment with an invalid user_id
db.insert_into_table('comments', [3, 1, 3, 'Invalid user'])
#comments = db.select('comments')
# print("Comments after invalid user_id insert:", comments)

# Delete a user and check cascading delete
# db.delete_from_table('users', 'user_id', 1)
users = db.select('users', [], {'user_id': 2})
print("Users after delete:", users)
posts = db.select('posts', [], {'user_id': 1})
print("Posts after delete:", posts)
# comments = db.select('comments')

# join the users and posts tables on the user_id column where the user_id is 1
db.join_tables('users', 'posts', {'user_id': 1})

# try to join joined_table with comments table on the post_id column where the post_id is 1
db.join_tables('temp_users_posts', 'comments', {'post_id': 1})
# print(db.join_tables('users', 'posts', {'user_id': 1}))
# db.tables.pop('temp_users_posts')

db.reset()
print(db.tables)

# Clean up the temporary database file
#if os.path.exists(db_path):
#    os.remove(db_path)