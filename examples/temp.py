from app.pydb.database import Database
from app.pydb.table import Table
import sys
import os

# delete the db.json file if it exists
filepath = 'db.json'
if os.path.exists(filepath):
    os.remove(filepath)

db = Database(filepath)
db.add_table(
    table_name='seed_companies',
    columns={
        'seed_company_name': {
            'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'seed_company_id': {
            'type': int(), 'auto_inc': True, 'nullable': False, 'PK': True, 'FK': None
        }
    }
)
db.add_table(
    table_name='contacts',
    columns={
        'contact_name': {
            'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'contact_id': {
            'type': int(), 'auto_inc': True, 'nullable': False, 'PK': True, 'FK': None
        },
        'seed_company_id': {
            'type': int(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': {
                'table': 'seed_companies',
                'column': 'seed_company_id',
                'on_update': 'cascade',
                'on_delete': 'cascade'
            }
        }
    }
)

db.insert_into_table('seed_companies', ['Bayer', 2])
db.insert_into_table('seed_companies', ['Syngenta', 3])
db.insert_into_table('seed_companies', ['Dow AgroSciences', 4])
db.insert_into_table('seed_companies', ['DuPont Pioneer', 5])
db.insert_into_table('seed_companies', ['Limagrain', 6])
db.insert_into_table('seed_companies', ['KWS Saat', 7])
db.insert_into_table('seed_companies', ['Sakata', 8])
db.insert_into_table('seed_companies', ['Rijk Zwaan', 9])
db.insert_into_table('seed_companies', ['Takii', 10])

# Insert statements for contacts
db.insert_into_table('contacts', ['John Doe', 1, 1])
db.insert_into_table('contacts', ['John Doe', 50, 15])
db.insert_into_table('contacts', ['Jane Smith', 2, 1])
db.insert_into_table('contacts', ['Alice Johnson', 3, 2])
db.insert_into_table('contacts', ['Bob Brown', 4, 2])
db.insert_into_table('contacts', ['Charlie Davis', 5, 3])
db.insert_into_table('contacts', ['Diana Evans', 6, 3])
db.insert_into_table('contacts', ['Eve Foster', 7, 4])
db.insert_into_table('contacts', ['Frank Green', 8, 4])
db.insert_into_table('contacts', ['Grace Harris', 9, 5])
db.insert_into_table('contacts', ['Hank Irving', 10, 5])
db.insert_into_table('contacts', ['Ivy Johnson', 11, 6])
db.insert_into_table('contacts', ['Jack King', 12, 6])
db.insert_into_table('contacts', ['Kara Lee', 13, 7])
db.insert_into_table('contacts', ['Leo Martin', 14, 7])
db.insert_into_table('contacts', ['Mona Nelson', 15, 8])
db.insert_into_table('contacts', ['Nina Owens', 16, 8])
db.insert_into_table('contacts', ['Oscar Perry', 17, 9])
db.insert_into_table('contacts', ['Pam Quinn', 18, 9])
db.insert_into_table('contacts', ['Quincy Roberts', 19, 10])
db.insert_into_table('contacts', ['Rachel Scott', 20, 10])
db.insert_into_table('contacts', ['Sam Taylor', 21, 1])
db.insert_into_table('contacts', ['Tina Underwood', 22, 2])
db.insert_into_table('contacts', ['Uma Vance', 23, 3])
db.insert_into_table('contacts', ['Victor White', 24, 4])
db.insert_into_table('contacts', ['Wendy Xander', 25, 5])
db.insert_into_table('contacts', ['Xander Young', 26, 6])
db.insert_into_table('contacts', ['Yara Zane', 27, 7])
db.insert_into_table('contacts', ['Zack Allen', 28, 8])
db.insert_into_table('contacts', ['Amy Baker', 29, 9])
db.insert_into_table('contacts', ['Brian Clark', 30, 10])

db.update_table('seed_companies', ['seed_company_id'], [11], 'seed_company_id', 2)

# Insert a row into the 'users' table
# db.insert_into_table('users', ['John', 25, 7])


# table_0 = Table(
#     filepath,
#     table_name='table_0',
#     columns={
#         'column_0': {
#             'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
#         },
#         'column_1': {
#             'type': int(), 'auto_inc': False, 'nullable': False, 'PK': True, 'FK': None
#         },
#         'column_2': {
#             'type': int(), 'auto_inc': True, 'nullable': False, 'PK': False, 'FK': None
#         },
#         'column_3': {
#             'type': float(), 'auto_inc': False, 'nullable': True, 'PK': False, 'FK': None
#         },
#         'column_4': {
#             'type': float(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
#         },
#         'column_5': {
#             'type': int(), 'auto_inc': True, 'nullable': False, 'PK': False, 'FK': None
#         }
#     }
# )

# table_1 = Table(
#     filepath,
#     table_name='table_1',
#     columns={
#         'column_00': {
#             'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
#         },
#         'column_11': {
#             'type': int(),
#             'auto_inc': True,
#             'nullable': False,
#             'PK': True,
#             'FK': {
#                 'table': 'table_0',
#                 'column': 'column_1',
#                 'on_update': 'cascade',
#                 'on_delete': 'do_nothing'
#             }
#         }
#     }
# )

# table_2 = Table(
#     filepath,
#     table_name='table_1',
#     columns={
#         'column_000': {
#             'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
#         },
#         'column_111': {
#             'type': int(),
#             'auto_inc': True,
#             'nullable': False,
#             'PK': True,
#             'FK': {
#                 'table': 'table_0',
#                 'column': 'column_1',
#                 'on_update': 'cascade',
#                 'on_delete': 'do_nothing'
#             }
#         }
#     }
# )