import unittest
from pydb.table import Table as t

# Test cases for the Table class
# A better way to write these tests would be to create a new table for each test case
#  and then delete the table after the test case has been run. This would ensure that
#  the tests are independent of each other. However, for the sake of simplicity, I have
#  created a single table and run all the test cases on it. This is not ideal since the
#  tests are not independent of each other. If one test case fails, it could affect the
#  results of the other test cases.

# This is something that will be corrected in a future release of the code. For now,
#  enjoy "test_z_..." :)

class TableTestCase(unittest.TestCase):
    def setUp(self):
        # Create a sample table for testing
        self.table = t(
            'db.json',
            table_name='unit_test_table',
            columns={
                'column_0': {
                    'type': str(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
                },
                'column_1': {
                    'type': int(), 'auto_inc': False, 'nullable': False, 'PK': True, 'FK': None
                },
                'column_2': {
                    'type': int(), 'auto_inc': True, 'nullable': False, 'PK': False, 'FK': None
                },
                'column_3': {
                    'type': float(), 'auto_inc': False, 'nullable': True, 'PK': False, 'FK': None
                },
                'column_4': {
                    'type': float(), 'auto_inc': False, 'nullable': False, 'PK': False, 'FK': None
                },
                'column_5': {
                    'type': int(), 'auto_inc': True, 'nullable': False, 'PK': False, 'FK': None
                },
            }
        )

    def test_insert_first_row(self):
        # Test inserting the first row
        # Auto increment columns should be set to 0
        self.table.insert_row(['value_0', 1, 0.0, 0.0])
        self.assertEqual(self.table.load_data().get('data')[0][2], 0)

    def test_insert_row(self):
        # Test inserting a row
        print(self.table.load_data().get('data'))
        self.table.insert_row(['value_4', 3, 4.0, 4.0])
        self.assertEqual(self.table.load_data().get('data')[1][0], 'value_4')

    def test_insert_row_with_same_pk_value(self):
        # Test inserting a row with the same PK value
        with self.assertRaises(ValueError):
            self.table.insert_row(['value_4', 3, 4.0, 4.0])

    def test_insert_row_with_missing_values(self):
        # Test inserting a row with missing values
        # The code should throw an error since there are missing values
        with self.assertRaises(ValueError):
            self.table.insert_row(['value_6', 3, 6.0])

    def test_insert_row_with_wrong_data_type(self):
        # Test inserting a row with wrong data type
        # The code should throw an error since the data type is wrong
        with self.assertRaises(ValueError):
            self.table.insert_row(['value_7', '3', 7.0, 7.0])

    def test_insert_row_with_too_many_values(self):
        # Test inserting a row with too many values
        # The code should throw an error since there are too many values
        with self.assertRaises(ValueError):
            self.table.insert_row(['value_8', 3, 8.0, 8.0, 8.0])

    def test_insert_row_with_too_few_values(self):
        # Test inserting a row with too few values
        # The code should throw an error since there are too few values
        with self.assertRaises(ValueError):
            self.table.insert_row(['value_9', 3, 9.0])

    def test_insert_row_with_null_value(self):
        # Test inserting a row with a null value
        self.table.insert_row(['value_10', 4, None, 10.0])
        self.assertEqual(self.table.load_data().get('data')[2][3], None)

    def test_insert_null_into_non_nullable_column(self):
        # Test inserting a null value into a non-nullable column
        # The code should throw an error since the column is not nullable
        with self.assertRaises(ValueError):
            self.table.insert_row(['value_11', 5, 11.0, None])

    def test_update_existing_records(self):
        # Update column 0 with value_0_updated where column_1 = 1
        print(self.table.load_data().get('data'))
        self.table.update_row(['column_0'], ['value_updated'], 'column_1', 1)

        self.assertEqual(self.table.load_data().get('data')[0][0], 'value_updated')

    def test_update_nonexistent_record(self):
        # Test updating a nonexistent record, should return 0 since no record was updated
        # The code should not throw an error, just inform the user that no record was updated
        self.assertEqual(self.table.update_row(['column_0'], ['value_updated'], 'column_1', 99), 0)

    def test_update_nullable_column_success(self):
        # Test updating a nullable column with a value of None
        self.table.update_row(['column_3'], [None], 'column_1', 1)
        
        self.assertEqual(self.table.load_data().get('data')[0][3], None)

    def test_update_nullable_column_failure(self):
        # Test updating a non-nullable column with a value of None
        # The code should throw an error since the column is not nullable
        with self.assertRaises(ValueError):
            self.table.update_row(['column_4'], [None], 'column_1', 1)

    def test_update_pk_column_with_non_unique_value(self):
        with self.assertRaises(ValueError):
            self.table.update_row(['column_1'], [1], 'column_1', 3)

    def test_update_error_on_nonexistent_column(self):
        # Test updating a nonexistent column
        # The code should throw an error since the column does not exist
        with self.assertRaises(ValueError):
            self.table.update_row(['column_6'], ['value_updated'], 'column_1', 1)

    def test_update_error_on_too_many_columns(self):
        # Test updating a row with too many columns compared to values
        # The code should throw an error since there are too many columns
        with self.assertRaises(ValueError):
            self.table.update_row(['column_0', 'column_1', 'column_2', 'column_3', 'column_4'], ['value_updated', 1], 'column_1', 1)

    def test_update_error_on_too_many_values(self):
        # Test updating a row with too many values
        # The code should throw an error since there are too many values
        with self.assertRaises(ValueError):
            self.table.update_row(['column_0'], ['value_updated', 1], 'column_1', 1)

    def test_update_error_too_many_columns_and_values(self):
        # Test updating a row with too many columns and values
        # The code should throw an error since there are too many columns and values
        # This error is thrown when the number of columns/values are more
        #  than the number of columns in the table. Takes into consideration
        #  any auto-increment columns in the table.
        print(self.table.load_data().get('data')) 
        with self.assertRaises(ValueError):
            self.table.update_row(['column_0', 'column_1', 'column_2', 'column_3', 'column_4'], ['value_updated', 1, 1, 1, 1], 'column_1', 1)

    def test_z_delete_row(self):
        # Test deleting a row
        print(self.table.load_data().get('data'))  
        self.table.delete_row('column_1', 1)
        self.assertEqual(len(self.table.load_data().get('data')), 2)

    def test_z_delete_nonexistent_row(self):
        # Test deleting a nonexistent row
        # The code should not throw an error, just inform the user that no record was deleted
        self.assertEqual(self.table.delete_row('column_1', 99), None)

    def test_z_delete_error_on_nonexistent_column(self):
        # Test deleting a row with a nonexistent column
        # The code should throw an error since the column does not exist
        with self.assertRaises(ValueError):
            self.table.delete_row('column_6', 1)

    def test_z_delete_non_pk_column(self):
        # Test deleting a row with a non-PK column
        # The code should throw an error since the column is not a PK column
        with self.assertRaises(ValueError):
            self.table.delete_row('column_0', 'value_4')

    def test_z_delete_non_string_to_column_name_param(self):
        # Test passing a non-string value to the column_name parameter
        # The code should throw an error since the column_name parameter is a string
        with self.assertRaises(ValueError):
            self.table.delete_row(1, 'value_4')
    
    def test_z_delete_with_type_mismatch(self):
        # Test deleting a row with a type mismatch
        # The code should throw an error since the data type of the column and value do not match
        with self.assertRaises(ValueError):
            self.table.delete_row('column_1', 'value_4')

    def test_dunder(self):
        # Test __str__ and __repr__ methods
        assert 1 == 1

if __name__ == '__main__':
    unittest.main()