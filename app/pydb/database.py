from app.pydb.table import Table
from typing import Dict, Any, List
import json

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

    def insert_into_table(self, table_name: str, row: List[Any]):
        table = self.get_table(table_name)
        insert_data = table.prep_insert_row(row)
        print(f"Inserting {insert_data} into {table_name} with {list(table.columns.keys())}")

        # check for a parent table
        for column, values in table.columns.items():
            if values['FK']:
                print(f"FK found in {table_name} for {column}")
                parent_table = values['FK']['table']
                print(f"Parent table is {parent_table}")
                # get the index of column in both tables
                parent_table_index = list(self.get_table(parent_table).columns.keys()).index(column)
                table_index = list(table.columns.keys()).index(column)
                print(f"Parent table index is {parent_table_index}")
                print(f"Table index is {table_index}")

                # check if the parent table has the value
                parent_table_data = self.get_table(parent_table).load_data()['data']
                print(f"Parent table data is {parent_table_data}")
                parent_table_values = [row[parent_table_index] for row in parent_table_data]
                print(f"Parent table values are {parent_table_values}")
                print(f"Row value is {row[table_index]}")
                if row[table_index] not in parent_table_values:
                    # ignore and move on
                    print(f"Value {row[table_index]} not found in parent table {parent_table}. Did not insert.")
                    return

        table.insert_row(row)
        print('-----')

    def update_table(self, table_name, column_names: List[str], column_values: List[Any], conditional_column_name: str, conditional_column_value: Any):
        table = self.get_table(table_name)
        prev_cols = list(table.columns.keys())
        counter, prev_vals = table.update_row(column_names, column_values, conditional_column_name, conditional_column_value)
        print(f"Made {counter} updates to {table_name} where {conditional_column_name} = {conditional_column_value} from {prev_vals} to {column_values}")
        self.handle_fk_updates(table_name, column_names, column_values, prev_cols, prev_vals)

    def handle_fk_updates(self, table_name, column_names, column_values, prev_cols, prev_vals):
        print(f"Checking for FK updates in {table_name}")
        print(f"Column names to be altered: {column_names}")
        print(f"Column values to be altered: {column_values}")
        print(f"---")
        prev_table = self.get_table(table_name)
        for potential_child_table in self.tables:
            if potential_child_table == table_name:
                continue
            pct = self.get_table(potential_child_table)
            for column, values in pct.columns.items():
                print(f"Checking {column} in {potential_child_table}")
                if column in column_names:
                    print(f"Column {column} is in column_names")
                    if values['FK'] and values['FK']['table'] == table_name:
                        print(f"FK found in {potential_child_table} linking to {table_name}")
                        fk_column = values['FK']['column']
                        print(f"The FK column is {fk_column}")
                        if not values['FK']['column'] == column:
                            continue
                        fk_column_index = list(pct.columns.keys()).index(column)
                        prev_column_index = list(prev_table.columns.keys()).index(column)
                        if values['FK']['on_update'] == 'cascade':
                            for i, row in enumerate(pct.load_data()['data']):
                                for column, value, prev_val in zip(column_names, column_values, prev_vals):
                                    if row[fk_column_index] == prev_val[prev_column_index]:
                                        print(f"Updating {column} in {potential_child_table} where {fk_column} = {prev_val[prev_column_index]}")
                                        pct.update_row([column], [value], fk_column, row[fk_column_index])

    def delete_from_table(self, table_name: str, column_name: str, column_value: Any):
        table = self.get_table(table_name)
        table.delete_row(column_name, column_value)
        self.handle_fk_deletes(table_name, column_name, column_value)

    def handle_fk_deletes(self, table_name, column_name, column_value):
        print(f"Checking for FK deletes in {table_name}")
        print(f"Column name to be deleted: {column_name}")
        print(f"Column value to be deleted: {column_value}")
        print(f"---")
        table = self.get_table(table_name)
        for potential_child_table in self.tables:
            if potential_child_table == table_name:
                continue
            pct = self.get_table(potential_child_table)
            for column, values in pct.columns.items():
                print(f"Checking {column} in {potential_child_table}")
                if values['FK'] and values['FK']['table'] == table_name:
                    print(f"FK found in {potential_child_table} linking to {table_name}")
                    fk_column = values['FK']['column']
                    print(f"The FK column is {fk_column}")
                    if not fk_column == column_name:
                        continue
                    fk_column_index = list(pct.columns.keys()).index(column)
                    if values['FK']['on_delete'] == 'cascade':
                        for i, row in enumerate(pct.load_data()['data']):
                            if row[fk_column_index] == column_value:
                                print(f"Deleting row in {potential_child_table} where {fk_column} = {column_value}")
                                pct.delete_row(fk_column, column_value, True)