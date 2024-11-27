from app.pydb.table import Table
from typing import Dict, Any, List
import logging
import json

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the lowest level to capture all messages

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('database_debug.log')

# Set levels for handlers
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class Database:
    '''
    Database class to manage tables and data in a JSON file.

    PyDB is a simple, lightweight, file-based database
        system that uses JSON files to store data.
        It is designed to be easy to use and understand.
        It is not intended for production use, but rather
        for educational purposes. Use in production
        at your own risk.

    A common use case for PyDB is to act as an offline
        storage system for small applications or as a
        simple way to store data for personal projects.

    PyDB supports the following features:
        - Create tables with columns
        - Insert data into tables
        - Update data in tables
        - Delete data from tables
        - Foreign key constraints
        - ON DELETE and ON UPDATE actions
    
    PyDB does NOT support the following features:
        - Joins
        - Indexes
        - Transactions
        - Views
        - Stored procedures
        - Triggers
        - User management
        - Permissions

    To simulate JOINs, you can use the `select` method
        to load data from multiple tables and perform
        the join in Python code using a library like
        Pandas or NumPy.
    
    To simulate transactions, you can wrap multiple
        operations in a try-except block and handle
        exceptions accordingly.

    To simulate indexes, you can create additional
        tables that store indexed data and use them
        to quickly look up values.

    To simulate views, you can create a method that
        generates a view by combining data from
        multiple tables.

    To simulate stored procedures, you can create
        methods that perform specific operations
        on the database.
    
    To simulate triggers, you can create methods
        that are called before or after specific
        operations on the database.

    To simulate user management and permissions,
        you can create a custom authentication and
        authorization system in your application.

    Args:
        path (str): The path to the JSON file that
            will store the database data.
    
    Attributes:
        path (str): The path to the JSON file that
            stores the database data.
        tables (dict): A dictionary of Table objects
            that represent the tables in the database.
    '''
    def __init__(self, path: str):
        self.path = path
        self.tables = {}

        # create the db.json file if it does not exist
        try:
            with open(path, 'r') as f:
                pass
        except FileNotFoundError:
            with open(path, 'w') as f:
                json.dump({}, f)
    
    def __repr__(self):
        return f"Database(path='{self.path}', tables={self.tables})"
    
    def clear_temp_tables(self):
        to_remove = [table_name for table_name in self.tables if table_name.startswith('temp_')]
        for table_name in to_remove:
            logger.info(f"Removing temporary table {table_name}")
            self.remove_table(table_name)

    def add_table(self, table_name: str, columns: Dict[str, Dict[str, Any]]):
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists.")
        new_table = Table(path=self.path, table_name=table_name, columns=columns)
        self.tables[table_name] = new_table

    def remove_table(self, table_name: str):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        
        # get the table
        table = self.get_table(table_name)

        # delete the table using the table's built in delete_table method
        #  this removes the table from the db file
        table.delete_table()

        # remove the table from the database object's tables attribute
        del self.tables[table_name]

    def get_table(self, table_name: str) -> Table:
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        return self.tables[table_name]

    def list_tables(self) -> List[str]:
        return list(self.tables.keys())
    
    def select(self, table_name: str, columns: List[str], condition: Dict[str, Any] = None) -> List[List[Any]]:
        table = self.get_table(table_name)
        loaded = table.load_data()
        data = loaded['data']
        columns = list(loaded['columns'].keys())
    
        cond_index = [columns.index(col) for col in condition.keys()]
        if len(cond_index) == 0:
            return data
        if condition:
            filtered_data = []
            for row in data:
                if all(row[cond_index[i]] == val for i, val in enumerate(condition.values())):
                    if len(columns) > 0:
                        filtered_data.append([row[columns.index(col)] for col in columns])
                    else:
                        filtered_data.append(row)
            return filtered_data

    def join_tables(self, leftmost: str, rightmost: str, condition: Dict[str, Any] = None, *args):
        '''Join two tables together.
        This method can be daisy-chained to join multiple tables together.
        '''
        joined = []

        try:
            # start by getting the table objects
            leftmost = self.get_table(leftmost)
            rightmost = self.get_table(rightmost)

            # dont want to have temp_temp_table
            if not 'temp' in leftmost.table_name and not 'temp' in rightmost.table_name:
                temp_name = f'temp_{leftmost.table_name}_{rightmost.table_name}'
            else:
                temp_name = f'{leftmost.table_name}_{rightmost.table_name}'
        except ValueError as e:
            logger.error(f"Error joining tables: {e}")
            return

        # load the data from the tables
        leftmost_loaded = leftmost.load_data()
        rightmost_loaded = rightmost.load_data()

        # get the data and columns from the loaded data
        leftmost_data = leftmost_loaded['data']
        rightmost_data = rightmost_loaded['data']

        leftmost_columns = list(leftmost_loaded['columns'].keys())
        rightmost_columns = list(rightmost_loaded['columns'].keys())

        # get full column info
        leftmost_columns_info = leftmost.columns
        rightmost_columns_info = rightmost.columns

        # get the column info for the joined columns
        cols = {col: leftmost_columns_info[col] for col in leftmost_columns}
        cols.update({col: rightmost_columns_info[col] for col in rightmost_columns if col not in leftmost_columns})
        
        # rip only the key and type from the columns info,
        #  keeping the nested dict structure
        #  all other columns will default
        cols = {col: {'type': info['type']} for col, info in cols.items()}

        # get the index of the condition columns in both tables
        left_cond_index = [leftmost_columns.index(col) for col in condition.keys()]
        right_cond_index = [rightmost_columns.index(col) for col in condition.keys()]

        # iterate through the leftmost table
        #  and find rows that match the condition
        # then iterate through the rightmost table
        #  and find rows that match the condition, but only keep columns
        #  that are not in the leftmost table
        for row in leftmost_data:
            if all(row[left_cond_index[i]] == val for i, val in enumerate(condition.values())):
                joined_row_starter = [row[leftmost_columns.index(col)] for col in leftmost_columns]
                for r_row in rightmost_data:
                    if all(r_row[right_cond_index[i]] == val for i, val in enumerate(condition.values())):
                        joined_row = joined_row_starter.copy()
                        joined_row.extend([r_row[rightmost_columns.index(col)] for col in rightmost_columns if col not in leftmost_columns])
                        joined.append(joined_row)

        # turn the joined list into a table
        self.add_table(table_name=temp_name, columns=cols)
        for row in joined:
            self.insert_into_table(temp_name, row)


    def insert_into_table(self, table_name: str, row: List[Any]):
        table = self.get_table(table_name)
        insert_data = table.prep_insert_row(row)

        logger.debug(f"Inserting {insert_data} into {table_name} with {list(table.columns.keys())}")

        # check for a parent table
        for column, values in table.columns.items():
            if values['FK']:
                fk_column = values['FK']['column']
                parent_table = values['FK']['table']

                # get the index of column in both tables
                parent_table_index = list(self.get_table(parent_table).columns.keys()).index(fk_column)
                table_index = list(table.columns.keys()).index(column)

                # check if the parent table has the value
                parent_table_data = self.get_table(parent_table).load_data()['data']
                parent_table_values = [row[parent_table_index] for row in parent_table_data]

                if row[table_index] not in parent_table_values:
                    # ignore and move on
                    logger.info(f"Row {row} not inserted into {table_name}.")
                    logger.debug(f"Value {row[table_index]} not found in parent table {parent_table}. Did not insert.")
                    return

        table.insert_row(insert_data)

    def update_table(self, table_name, column_names: List[str], column_values: List[Any], conditional_column_name: str, conditional_column_value: Any):

        table = self.get_table(table_name)
        prev_cols = list(table.columns.keys())
        counter, prev_vals = table.update_row(column_names, column_values, conditional_column_name, conditional_column_value)

        logger.info(f"{counter} updates made to {table_name} where {conditional_column_name} = {conditional_column_value} from {prev_vals} to {column_values}")

        self.handle_fk_updates(table_name, column_names, column_values, prev_cols, prev_vals)

    def handle_fk_updates(self, table_name, column_names, column_values, prev_cols, prev_vals):

        prev_table = self.get_table(table_name)
        for potential_child_table in self.tables:
            if potential_child_table == table_name:
                continue
            pct = self.get_table(potential_child_table)

            for child_column, child_values in pct.columns.items():
                if child_values['FK'] and child_values['FK']['table'] == table_name:
                    parent_column = child_values['FK']['column']

                    for column, value, prev_val in zip(column_names, column_values, prev_vals):
                        if not child_values['FK']['column'] == column:
                            continue

                        fk_column_index = list(pct.columns.keys()).index(child_column)
                        prev_column_index = list(prev_table.columns.keys()).index(parent_column)

                        logger.debug(f"Updating {potential_child_table}.{child_column} where {table_name}.{parent_column} = {prev_val[prev_column_index]}")

                        if child_values['FK']['on_update'] == 'cascade':
                            for i, row in enumerate(pct.load_data()['data']):
                                if row[fk_column_index] == prev_val[prev_column_index]:
                                        pct.update_row([child_column], [value], child_column, row[fk_column_index])
                        elif child_values['FK']['on_update'] == 'set_null':
                            for i, row in enumerate(pct.load_data()['data']):
                                if row[fk_column_index] == prev_val[prev_column_index]:
                                    pct.update_row([child_column], [None], child_column, row[fk_column_index])


    def delete_from_table(self, table_name: str, column_name: str, column_value: Any):
        table = self.get_table(table_name)
        counter = table.delete_row(column_name, column_value)

        logger.info(f"{counter} rows deleted from {table_name} where {column_name} = {column_value}")

        self.handle_fk_deletes(table_name, column_name, column_value)

    def handle_fk_deletes(self, table_name, column_name, column_value):

        table = self.get_table(table_name)
        for potential_child_table in self.tables:
            if potential_child_table == table_name:
                continue
            pct = self.get_table(potential_child_table)
            for child_column, child_values in pct.columns.items():
                if child_values['FK'] and child_values['FK']['table'] == table_name:
                    parent_column = child_values['FK']['column']

                    if not parent_column == column_name:
                        continue

                    fk_column_index = list(pct.columns.keys()).index(child_column)
                    if child_values['FK']['on_delete'] == 'cascade':
                        for i, row in enumerate(pct.load_data()['data']):
                            if row[fk_column_index] == column_value:
                                logger.debug(f"Deleting row in {potential_child_table} where {child_column} = {column_value}")
                                pct.delete_row(child_column, column_value, True)
                    elif child_values['FK']['on_delete'] == 'set_null':
                        for i, row in enumerate(pct.load_data()['data']):
                            if row[fk_column_index] == column_value:
                                logger.debug(f"Setting row in {potential_child_table} where {child_column} = {column_value} to NULL")
                                pct.update_row([child_column], [None], child_column, column_value)

    def save(self):
        for table_name, table in self.tables.items():
            table.save_data()
        logger.info(f'Tables saved to {self.path}.')

    def load(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
        for table_name, table_data in data.items():
            self.add_table(table_name, table_data['columns'])
            table = self.get_table(table_name)
            table.load_data(table_data['data'])

    def reset(self):
        for table_name in self.list_tables():
            self.remove_table(table_name)
        self.tables = {}
        self.save()
        logger.info("Database reset.")
        return self
    
    def close(self):
        # close any temporary tables
        self.clear_temp_tables()
        self.save()
        logger.info("Database closed.")
        return self