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

    def add_table(self, table_name: str, columns: Dict[str, Dict[str, Any]]):
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists.")
        new_table = Table(path=self.path, table_name=table_name, columns=columns)
        self.tables[table_name] = new_table

    def remove_table(self, table_name: str):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        del self.tables[table_name]

    def get_table(self, table_name: str) -> Table:
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        return self.tables[table_name]

    def list_tables(self) -> List[str]:
        return list(self.tables.keys())
    
    def select(self, table_name: str):
        table = self.get_table(table_name)
        return table.load_data()

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