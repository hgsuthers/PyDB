Comprehensive Guide to Using PyDB
=================================

PyDB is a lightweight, file-based database system implemented in Python. It allows you to create, manage, and manipulate tables and rows using simple Python code. This guide will walk you through the essential features and usage of PyDB.

Table of Contents
-----------------
- `Getting Started`_
- `Creating a Database`_
- `Adding Tables`_
- `Inserting Data`_
- `Foreign Key Constraints`_
- `Updating Data`_
- `Deleting Data`_
- `Listing Tables`_
- `Example Usage`_

Getting Started
---------------

To get started with PyDB, you need to have Python installed on your machine. You can install PyDB by cloning the repository from GitHub or by downloading the source code.

.. code-block:: bash

    git clone https://github.com/your-repo/pydb.git
    cd pydb

Creating a Database
-------------------

To create a new database, you need to instantiate the `Database` class and provide a path for the database file.

.. code-block:: python

    from pydb.database import Database

    db = Database(path='db.json')

This will create a `db.json` file if it does not already exist.

Adding Tables
-------------

You can add tables to your database using the `add_table` method. Each table requires a name and a dictionary defining its columns.

.. code-block:: python

    columns = {
        'id': {'type': int(), 'PK': True},
        'name': {'type': str()},
        'age': {'type': int()}
    }

    db.add_table('users', columns)

This creates a table named `users` with three columns: `id`, `name`, and `age`.

Inserting Data
--------------

To insert data into a table, use the `insert_into_table` method. You need to provide the table name and a list of values corresponding to the columns.

.. code-block:: python

    db.insert_into_table('users', [1, 'Alice', 30])
    db.insert_into_table('users', [2, 'Bob', 25])

Foreign Key Constraints
-----------------------

PyDB supports foreign key constraints to maintain referential integrity between tables. When defining a column, you can specify a foreign key constraint.

.. code-block:: python

    columns = {
        'id': {'type': int(), 'auto_inc': True, 'PK': True},
        'user_id': {'type': int(), 'nullable': True, 'FK': {'table': 'users', 'column': 'id', 'on_update': 'set_null', 'on_delete': 'cascade'}}
    }
    
    db.add_table('orders', columns)

This creates an `orders` table with a foreign key constraint on the `user_id` column, referencing the `id` column in the `users` table.

Updating Data
-------------

To update data in a table, you can use the `update_row` method. You need to specify the columns to update, their new values, and the condition for selecting the rows to update.

.. code-block:: python

    db.update_table('users', ['name'], ['Alice Smith'], 'id', 1)

This updates the `name` column for the row where `id` is 1.

Deleting Data
-------------

To delete data from a table, use the `delete_row` method. You need to specify the column and value to identify the rows to delete.

.. code-block:: python

    db.delete_from_table('users', 'id', 2)

This deletes the row where `id` is 2.

Listing Tables
--------------

To list all tables in the database, use the `list_tables` method.

.. code-block:: python

    tables = db.list_tables()
    print(tables)

This will print a list of all table names in the database.

Example Usage
-------------

Here is a complete example demonstrating the usage of PyDB:

.. code-block:: python

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

This example demonstrates how to create a database, add tables, insert data, update data, delete data, and select data using PyDB.

Conclusion
----------

PyDB is a simple yet powerful tool for managing data in a file-based database. With support for primary keys, foreign keys, and basic CRUD operations, it provides a lightweight solution for small-scale data management needs. This guide should help you get started with PyDB and utilize its features effectively.
