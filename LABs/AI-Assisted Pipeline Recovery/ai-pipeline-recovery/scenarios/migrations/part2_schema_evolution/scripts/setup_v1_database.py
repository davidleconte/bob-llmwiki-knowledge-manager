#!/usr/bin/env python3
"""
setup_v1_database.py - Create V1 schema database with sample data
"""

import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'app_v1.db')
SCHEMA_PATH = os.path.join(DATA_DIR, 'schema_v1.sql')


def create_v1_database():
    """Create V1 database from schema file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()

    # Print summary
    print(f"V1 Database created: {DB_PATH}")
    print(f"  Customers: {cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]}")
    print(f"  Addresses: {cursor.execute('SELECT COUNT(*) FROM addresses').fetchone()[0]}")
    print(f"  Transactions: {cursor.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]}")

    conn.close()
    return DB_PATH


if __name__ == '__main__':
    create_v1_database()
