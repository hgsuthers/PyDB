import unittest
import app.table

class TableTestCase(unittest.TestCase):
    def setUp(self):
        # Create a sample table for testing
        self.table = app.table.Table(
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

    def test_update_existing_records(self):
        # Update column 0 with value_0_updated where column_1 = 1
        print(self.table.load_data().get('data'))
        self.table.update_row(['column_0'], ['value_updated'], 'column_1', 1)

        self.assertEqual(self.table.load_data().get('data')[0][0], 'value_updated')

    def test_update_nonexistent_record(self):
        # Test updating a nonexistent record, should return 0 since no record was updated
        # The code should not throw an error, just inform the user that no record was updated
        self.assertEqual(self.table.update_row(['column_0'], ['value_updated'], 'column_1', 4), 0)

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
        # Test updating a row with too many columns
        # The code should throw an error since there are too many columns
        with self.assertRaises(ValueError):
            self.table.update_row(['column_0', 'column_1', 'column_2', 'column_3', 'column_4'], ['value_updated', 1], 'column_1', 1)

    def test_update_error_on_too_many_values(self):
        # Test updating a row with too many values
        # The code should throw an error since there are too many values
        with self.assertRaises(ValueError):
            self.table.update_row(['column_0'], ['value_updated', 1], 'column_1', 1)

    def test_dunder(self):
        # Test __str__ and __repr__ methods
        assert 1 == 1

if __name__ == '__main__':
    unittest.main()