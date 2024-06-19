from dataclasses import dataclass, field
from typing import Dict, Any, List

from os import getcwd
from os import path

import json

import sys

filepath = path.join(getcwd(), "db.json") # hardcode this for now

# DB Initialization will take place in the DB Class

with open(filepath, 'w') as f:
    json.dump({}, f, indent=4)

@dataclass
class Table:

    path: str
    table_name: str = ''
    columns: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    data: List[List[Any]] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.build_table()

    def __repr__(self):
        return self.table_name

    def build_table(self):
        # needs error handling for two columns in the same table trying to
        #  form a foreign key relation with the same column in a parent table
        # should also have error handling for when a table will have more than
        #  one PK, this database only allows one PK per table
        '''
        '''
        self.columns = {
            col_name: {
                **col_info,
                'column_name': col_name
            } for col_name, col_info in self.columns.items()
        }

        with open(self.path, 'r+') as f:
            try:
                db_data = json.load(f)
            except json.JSONDecodeError:
                db_data = {}

            # Check for multiple PK here

            for col_info in self.columns.values():
                fk_info = col_info.get('FK')
                if fk_info:
                    if fk_info.get('table') not in db_data:
                        raise ValueError(f"FK Relation does not exist for table {fk_info.get('table')}")
                    else:
                        if not isinstance(
                            db_data.get(fk_info.get('table')).get('columns')[fk_info.get('column')]['type'],
                            type(col_info.get('type'))
                        ):
                            raise ValueError(f"FK Relation type mismatch for column {fk_info.get('column')}")
                        
                        if not db_data.get(fk_info.get('table')).get('columns')[fk_info.get('column')]['PK']:
                            raise ValueError(f"Parent is not a primary key.")

            if self.table_name not in db_data:
                table_base = {
                                "data": self.data,
                                "columns": self.columns
                            }
                db_data[self.table_name] = table_base
                f.seek(0)
                json.dump(db_data, f, indent=4)
            self.data = db_data[self.table_name]["data"]

    def load_data(self) -> Dict[str, Any]:
        if path.exists(self.path):
            # Load all of the db data from db_path then get specific table data
            with open(self.path, 'r') as db_file:
                db_data = json.load(db_file)
                return db_data.get(self.table_name, {})
        else:
            return {}
        
    def save_data(self):
        ''''''
        with open(self.path, 'r') as db_file:
            db_data = json.load(db_file)
            db_data[self.table_name]["data"] = self.data
            db_file.seek(0)
            with open(self.path, 'w') as write_file:
                json.dump(db_data, write_file, indent=4)

    def insert_row(self, row_data: List[Any]):

        if len(row_data) < len(self.columns):

            for index, (col, metadata) in enumerate(self.columns.items()):
                if metadata.get('auto_inc', True):
                    try:
                        row_data.insert(index, self.data[len(self.data)-1][index]+1)
                    except (IndexError) as e:
                        # Handles the first row of the table
                        row_data.insert(index, 0)

            if len(row_data) != len(self.columns):
                raise ValueError(
                    'Attempting to insert {} values. Expected {}.'.format(
                        len(row_data), len(self.columns)
                    )
                )

        elif len(row_data) > len(self.columns):
            raise ValueError(
                '{} values provided. Expected {}.'.format(
                    len(row_data), len(self.columns)
                )
            )

        for index, (col, metadata) in enumerate(self.columns.items()):
            if not isinstance(metadata['type'], type(row_data[index])):
                raise ValueError(
                    'Data type mismatch for column {}.'.format(
                        col
                    )
                )

        self.data.append(row_data)
        self.save_data()

    def update_row(self, column_names: List[str], column_values: List[Any], conditional_column_name: str, conditional_column_value: Any):
        # update <table> set column_1 = value_1, column_2 = value_2, ..., where <condition>
        # this update will only handle one conditional statement
        #  the conditional statement must include the table's primary key
        # this update will handle n number of updates to the table where n is 
        #  the number of columns - 1 as update will not change the value of a primary key

        # so check if primary key
        # check if input data type matches column type
        # check the number of rows being updated

        # Get the indices of the columns to be updated
        row_indices = []
        for col_name in column_names:
            index = [idx for idx, key in enumerate(list(self.columns.items())) if key[0] == col_name]
            row_indices.append(index)

        # Check that row_indices length equals column_names length
        if not len(row_indices) == len(column_names):
            raise ValueError("One or more columns doesn't exist in table.")
        
        # Check if the number of indices exceeds n-m where n=num_columns and m=num_primary_keys
        if len(row_indices) > len(self.columns):
            raise ValueError("Too many columns present in update statement.")
        
        # Check if the conditional column name points to a primary key
        if not self.columns[conditional_column_name]['PK']:
            raise ValueError("Conditional column name is not a primary key.")
        
        # Iterate through column_names, column_values to ensure
        #  data type matching
        # This may be able to be done inside the row_indices for loop
        for col_name in column_names:
            pass
        return None

    def delete_row(self, column_name: str, column_value: Any):
        # DELETE FROM <table> WHERE <column> <operator> <value>
        # 
        # Check if primary key
        # Check if input data type matches what the column type is
        # Grab index of column somehow
        # This method functions correctly but needs to be expanded upon
        #  raise custom errors
        #  should table level check foreign key relations?

        #  currently does not handle > 1 primary keys

        index = [idx for idx, key in enumerate(list(self.columns.items())) if key[0] == column_name]
        if len(index) > 1:
            raise ValueError("Identical column names.")

        if not self.columns[column_name]['PK']:
            raise ValueError("Column not a primary key.")

        if not isinstance(column_value, type(self.columns[column_name]['type'])):
            raise ValueError("There is a type mismatch.")

        for row in self.data:
            if row[index[0]] == column_value:
                self.data.remove(row)
                self.save_data()

# table_naught = Table(
#     filepath,
#     table_name="table_naught",
#     columns={
#         'column_naught': {
#             'type': int(),
#             'auto_inc': False,
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

table_0 = Table(
    filepath,
    table_name='table_0',
    columns={
        'column_0': {
            'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'column_1': {
            'type': int(), 'auto_inc': True, 'nullable': False, 'PK': True, 'FK': None
        },
        'column_2': {
            'type': int(), 'auto_inc': True, 'nullable': False, 'PK': False, 'FK': None
        },
        'column_3': {
            'type': float(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'column_4': {
            'type': float(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'column_5': {
            'type': int(), 'auto_inc': True, 'nullable': False, 'PK': True, 'FK': None
        },
    }
)

table_1 = Table(
    filepath,
    table_name='table_1',
    columns={
        'column_00': {
            'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'column_11': {
            'type': int(),
            'auto_inc': True,
            'nullable': False,
            'PK': True,
            'FK': {
                'table': 'table_0',
                'column': 'column_1',
                'on_update': 'cascade',
                'on_delete': 'do_nothing'
            }
        }
    }
)

table_0.insert_row(['value_1', 1.0, 1.0])
table_0.insert_row(['value_2', 2.0, 2.0])
table_0.insert_row(['value_3', 3.0, 3.0])
table_1.insert_row(['value_11', 1])

table_0.delete_row('column_1', 2)

table_0.update_row(['column_3', 'column_4', 'column_5'], [2.2, 3.3, 9],  'column_1', 3)

print(table_0.load_data())
print(table_1.load_data())
