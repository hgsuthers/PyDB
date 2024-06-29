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
        '''
        Builds the table in the database file.
        '''
        self.columns = {
            col_name: {
                **col_info,
                'column_name': col_name
            } for col_name, col_info in self.columns.items()
        }

        # Check if the table exists in the db
        with open(self.path, 'r+') as f:
            try:
                db_data = json.load(f)
            except json.JSONDecodeError:
                db_data = {}

            # Check for multiple PK here
            if len([col_info for col_info in self.columns.values() if col_info.get('PK')]) > 1:
                raise ValueError("Multiple primary keys found in table.")

            # Check our FK relations
            for col_info in self.columns.values():
                fk_info = col_info.get('FK')
                print(fk_info)
                if fk_info:
                    if fk_info.get('table') not in db_data:
                        raise ValueError(f"FK Relation does not exist for table {fk_info.get('table')}")
                    else:
                        # Check that the column exists in the parent table
                        if not db_data.get(fk_info.get('table')).get('columns').get(fk_info.get('column')):
                            raise ValueError(f"FK Relation column {fk_info.get('column')} does not exist in parent table.")
                        
                        # Check that the fk type matches the parent type
                        if not isinstance(
                            db_data.get(fk_info.get('table')).get('columns')[fk_info.get('column')]['type'],
                            type(col_info.get('type'))
                        ):
                            raise ValueError(f"FK Relation type mismatch for column {fk_info.get('column')}")
                        
                        # Check that the parent is a primary key
                        if not db_data.get(fk_info.get('table')).get('columns')[fk_info.get('column')]['PK']:
                            raise ValueError(f"Parent is not a primary key.")
                        
                        # Check that the on_update and on_delete are valid
                        if fk_info.get('on_update') not in ['cascade', 'set_null', 'do_nothing']:
                            raise ValueError(f"Invalid on_update action for FK relation.")
                        
                        if fk_info.get('on_delete') not in ['cascade', 'set_null', 'do_nothing']:
                            raise ValueError(f"Invalid on_delete action for FK relation.")

            # Check if the table exists in the db
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
        '''
        Saves the data of the table to the database file.

        Use this method to write any changes to the table data to the database file.

        Parameters:
            None

        Returns:
            None
        '''
        with open(self.path, 'r') as db_file:
            db_data = json.load(db_file)
            db_data[self.table_name]["data"] = self.data
            db_file.seek(0)
            with open(self.path, 'w') as write_file:
                json.dump(db_data, write_file, indent=4)

    def insert_row(self, row_data: List[Any]):
        """
        Insert a new row into the table.

        This method takes into account that some columns may be auto-incrementing.
        """
        if len(row_data) < len(self.columns):
            for index, (col, metadata) in enumerate(self.columns.items()):
                # Check if the column is auto-incrementing
                if metadata.get('auto_inc', True):
                    try:
                        # Get the last value of the column and increment by 1
                        row_data.insert(index, self.data[len(self.data)-1][index]+1)
                    except (IndexError) as e:
                        # Handles the first row of the table
                        row_data.insert(index, 0)

            # Check that the number of values matches the number of columns
            #  after accounting for auto-incrementing columns
            if len(row_data) != len(self.columns):
                raise ValueError(
                    'Attempting to insert {} values. Expected {}.'.format(
                        len(row_data), len(self.columns)
                    )
                )

        # Check that user isn't attempting to insert too many values
        elif len(row_data) > len(self.columns):
            raise ValueError(
                '{} values provided. Expected {}.'.format(
                    len(row_data), len(self.columns)
                )
            )

        # Check that the data types match the schema
        for index, (col, metadata) in enumerate(self.columns.items()):
            if not isinstance(metadata['type'], type(row_data[index])):
                raise ValueError(
                    'Data type mismatch for column {}.'.format(
                        col
                    )
                )

        # Append the row to the table and save the data
        self.data.append(row_data)
        self.save_data()

    def update_row(self, column_names: List[str], column_values: List[Any], conditional_column_name: str, conditional_column_value: Any):
        """
        Updates rows in the table based on a conditional statement.

        Args:
            column_names (List[str]): A list of column names to be updated.
            column_values (List[Any]): A list of values to update the corresponding columns with.
            conditional_column_name (str): The name of the column used in the conditional statement.
            conditional_column_value (Any): The value to match in the conditional statement.

        Raises:
            ValueError: If one or more columns doesn't exist in the table.
            ValueError: If too many columns are present in the update statement.
            ValueError: If the conditional column name is not a primary key.
            ValueError: If there is a data type mismatch between the column values and the table schema.

        Notes:
            - This method updates rows in the table based on a conditional statement.
            - The conditional statement must include the table's primary key.
            - This method can handle multiple updates to the table, where the number of updates is equal to the number of columns - 1.
            - The primary key is used to find the row to update.
            - The method checks for the existence of columns, the number of columns, and the data type matching before performing the update.
            - After updating the table, the changes are saved.

        """
        # Get the indices of the columns to be updated
        row_indices = []
        for col_name in column_names:
            index = [idx for idx, key in enumerate(list(self.columns.items())) if key[0] == col_name]
            row_indices.append(index)

        # Get the index of the conditional column
        conditional_column_index = [idx for idx, key in enumerate(list(self.columns.items())) if key[0] == conditional_column_name]

        # Check that row_indices length equals column_names length
        if not len(row_indices) == len(column_names):
            raise ValueError("One or more columns doesn't exist in table.")
        
        # Check if the number of indices exceeds n-m where n=num_columns and m=num_primary_keys
        if len(row_indices) > len(self.columns):
            raise ValueError("Too many columns present in update statement.")
        
        # Check if the conditional column name points to a primary key
        # if not self.columns[conditional_column_name]['PK']:
        #     raise ValueError("Conditional column name is not a primary key.")
        if not self.columns.get(conditional_column_name, {}).get('PK', False):
            raise ValueError("Conditional column name is not a primary key.")
        
        # Iterate through column_names, column_values to ensure
        #  data type matching
        # This may be able to be done inside the row_indices for loop
        mismatches = []
        for col_name in column_names:
            if not isinstance(column_values[column_names.index(col_name)], type(self.columns[col_name]['type'])):
                mismatches.append(col_name)
        if mismatches:
            raise ValueError("Data type mismatch at {}.".format(mismatches))
        
        # Update the table after all checks have passed
        for row in self.data:
            if row[conditional_column_index[0]] == conditional_column_value:
                for idx, col in enumerate(row_indices):
                    row[col[0]] = column_values[idx]

        # Save the updated table
        self.save_data()

    def delete_row(self, column_name: str, column_value: Any):
        """
        Deletes rows in the table when given a column and value.
        """

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
            'type': int(), 'auto_inc': True, 'nullable': False, 'PK': False, 'FK': None
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

table_2 = Table(
    filepath,
    table_name='table_1',
    columns={
        'column_000': {
            'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
        },
        'column_111': {
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

#table_0.delete_row('column_1', 2)

table_0.update_row(['column_3', 'column_4', 'column_5'], [9.9, 3.9, 9],  'column_1', 1)
# not updating at all

print('0000000')
print(table_0.load_data())
print('0000000')
print(table_1.load_data())
