#!/usr/bin/env python3
"""
setup_broken_v1.py - Create a V1 database with schema variations

This simulates a "drift" scenario where the V1 database has slight variations:
- 'transactions' table already renamed to 'txn_history'
- Some columns have different names
- This will cause the migration script to fail
"""

import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'app_v1_broken.db')


def create_broken_v1_database():
    """Create a V1-ish database with schema drift."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Customers - slightly different column names
    cursor.execute('''
        CREATE TABLE customers (
            cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT NOT NULL,
            lname TEXT NOT NULL,
            email_addr TEXT UNIQUE,
            phone_num TEXT,
            date_created TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Addresses renamed to 'addr' with different columns
    cursor.execute('''
        CREATE TABLE addr (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_id INTEGER NOT NULL,
            street_addr TEXT NOT NULL,
            city_name TEXT NOT NULL,
            state_code TEXT,
            zip TEXT,
            country_name TEXT DEFAULT 'USA',
            FOREIGN KEY (cust_id) REFERENCES customers(cust_id)
        )
    ''')

    # Transactions renamed to 'txn_history'
    cursor.execute('''
        CREATE TABLE txn_history (
            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_id INTEGER NOT NULL,
            amt REAL NOT NULL,
            txn_type TEXT NOT NULL,
            notes TEXT,
            txn_date TEXT NOT NULL,
            FOREIGN KEY (cust_id) REFERENCES customers(cust_id)
        )
    ''')

    # Insert sample data
    cursor.executemany(
        'INSERT INTO customers (fname, lname, email_addr, phone_num) VALUES (?, ?, ?, ?)',
        [
            ('John', 'Doe', 'john.doe@email.com', '555-0101'),
            ('Jane', 'Smith', 'jane.smith@email.com', '555-0102'),
            ('Bob', 'Johnson', 'bob.j@email.com', '555-0103'),
        ]
    )

    cursor.executemany(
        'INSERT INTO addr (cust_id, street_addr, city_name, state_code, zip) VALUES (?, ?, ?, ?, ?)',
        [
            (1, '123 Main St', 'New York', 'NY', '10001'),
            (2, '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
            (3, '789 Pine Rd', 'Chicago', 'IL', '60601'),
        ]
    )

    cursor.executemany(
        'INSERT INTO txn_history (cust_id, amt, txn_type, notes, txn_date) VALUES (?, ?, ?, ?, ?)',
        [
            (1, 150.00, 'credit', 'Initial deposit', '2024-01-15'),
            (1, 25.50, 'debit', 'Purchase', '2024-01-20'),
            (2, 500.00, 'credit', 'Transfer in', '2024-01-18'),
            (3, 75.00, 'credit', 'Refund', '2024-02-01'),
        ]
    )

    conn.commit()

    print(f"Broken V1 database created: {DB_PATH}")
    print(f"  Customers: {cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]}")
    print(f"  Addresses (as 'addr'): {cursor.execute('SELECT COUNT(*) FROM addr').fetchone()[0]}")
    print(f"  Transactions (as 'txn_history'): {cursor.execute('SELECT COUNT(*) FROM txn_history').fetchone()[0]}")
    print()
    print("Schema differences from expected V1:")
    print("  - customers: customer_id→cust_id, first_name→fname, last_name→lname, etc")
    print("  - addresses table renamed to 'addr' with different columns")
    print("  - transactions table renamed to 'txn_history'")

    conn.close()
    return DB_PATH


if __name__ == '__main__':
    create_broken_v1_database()
