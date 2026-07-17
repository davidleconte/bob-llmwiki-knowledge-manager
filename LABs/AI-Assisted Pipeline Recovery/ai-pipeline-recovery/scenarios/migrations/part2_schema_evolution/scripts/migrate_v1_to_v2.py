#!/usr/bin/env python3
"""
migrate_v1_to_v2.py - Migrate database from schema V1 to V2

This script performs the following transformations:
1. Merge first_name + last_name → full_name
2. Rename 'addresses' → 'customer_addresses'
3. Rename 'transactions' → 'financial_transactions'
4. Transform transaction_type: 'credit'→'CR', 'debit'→'DR'
5. Add new required columns with defaults

Expected failures (for AI recovery demo):
- Source database has old table names
- Column names don't match
- Data type/format transformations needed
"""

import sqlite3
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

SOURCE_DB = os.environ.get('SOURCE_DB', os.path.join(DATA_DIR, 'app_v1.db'))
TARGET_DB = os.environ.get('TARGET_DB', os.path.join(DATA_DIR, 'app_v2.db'))

# Expected V1 schema (what we're migrating FROM)
EXPECTED_V1_TABLES = {
    'customers': ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'created_at'],
    'addresses': ['address_id', 'customer_id', 'street', 'city', 'state', 'zip_code', 'country'],
    'transactions': ['transaction_id', 'customer_id', 'amount', 'transaction_type', 'description', 'transaction_date'],
}


class MigrationError(Exception):
    """Migration failure."""
    pass


class SchemaError(MigrationError):
    """Schema mismatch."""
    pass


def validate_v1_schema(conn: sqlite3.Connection) -> None:
    """Validate source database has V1 schema."""
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    actual_tables = {row[0] for row in cursor.fetchall()}

    missing = set(EXPECTED_V1_TABLES.keys()) - actual_tables
    if missing:
        raise SchemaError(
            f"V1 schema validation failed. Missing tables: {missing}\n"
            f"Available tables: {actual_tables}\n"
            f"Expected V1 tables: {set(EXPECTED_V1_TABLES.keys())}"
        )

    for table, expected_cols in EXPECTED_V1_TABLES.items():
        cursor.execute(f"PRAGMA table_info({table})")
        actual_cols = [row[1] for row in cursor.fetchall()]

        missing_cols = set(expected_cols) - set(actual_cols)
        if missing_cols:
            raise SchemaError(
                f"Table '{table}' missing expected V1 columns: {missing_cols}\n"
                f"Available columns: {actual_cols}\n"
                f"Expected columns: {expected_cols}"
            )

    print("V1 schema validation passed")


def create_v2_schema(conn: sqlite3.Connection) -> None:
    """Create V2 schema in target database."""
    cursor = conn.cursor()

    # Customers table (V2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            updated_at TEXT
        )
    ''')

    # Customer addresses (V2) - renamed from 'addresses'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_addresses (
            address_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            address_type TEXT DEFAULT 'billing',
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT,
            postal_code TEXT,
            country_code TEXT DEFAULT 'US',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')

    # Financial transactions (V2) - renamed from 'transactions'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_transactions (
            transaction_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            transaction_type TEXT NOT NULL,
            category TEXT,
            transaction_date TEXT NOT NULL,
            processed_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')

    conn.commit()
    print("V2 schema created")


def migrate_customers(source: sqlite3.Connection, target: sqlite3.Connection) -> int:
    """Migrate customers: merge first_name + last_name → full_name."""
    source_cursor = source.cursor()
    target_cursor = target.cursor()

    source_cursor.execute('''
        SELECT customer_id, first_name, last_name, email, phone, created_at
        FROM customers
    ''')
    rows = source_cursor.fetchall()

    for row in rows:
        customer_id, first_name, last_name, email, phone, created_at = row
        full_name = f"{first_name} {last_name}"

        target_cursor.execute('''
            INSERT INTO customers (customer_id, full_name, email, phone, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
        ''', (customer_id, full_name, email, phone, created_at, datetime.utcnow().isoformat()))

    target.commit()
    print(f"Migrated {len(rows)} customers")
    return len(rows)


def migrate_addresses(source: sqlite3.Connection, target: sqlite3.Connection) -> int:
    """Migrate addresses → customer_addresses with transformations."""
    source_cursor = source.cursor()
    target_cursor = target.cursor()

    source_cursor.execute('''
        SELECT address_id, customer_id, street, city, state, zip_code, country
        FROM addresses
    ''')
    rows = source_cursor.fetchall()

    country_map = {'USA': 'US', 'United States': 'US', 'Canada': 'CA', 'UK': 'GB'}

    for row in rows:
        address_id, customer_id, street, city, state, zip_code, country = row
        country_code = country_map.get(country, country[:2].upper() if country else 'US')

        target_cursor.execute('''
            INSERT INTO customer_addresses
            (address_id, customer_id, address_type, street, city, state, postal_code, country_code)
            VALUES (?, ?, 'billing', ?, ?, ?, ?, ?)
        ''', (address_id, customer_id, street, city, state, zip_code, country_code))

    target.commit()
    print(f"Migrated {len(rows)} addresses → customer_addresses")
    return len(rows)


def migrate_transactions(source: sqlite3.Connection, target: sqlite3.Connection) -> int:
    """Migrate transactions → financial_transactions with type transformation."""
    source_cursor = source.cursor()
    target_cursor = target.cursor()

    source_cursor.execute('''
        SELECT transaction_id, customer_id, amount, transaction_type, description, transaction_date
        FROM transactions
    ''')
    rows = source_cursor.fetchall()

    type_map = {'credit': 'CR', 'debit': 'DR'}

    for row in rows:
        txn_id, customer_id, amount, txn_type, description, txn_date = row
        new_type = type_map.get(txn_type.lower(), txn_type)

        target_cursor.execute('''
            INSERT INTO financial_transactions
            (transaction_id, customer_id, amount, currency, transaction_type, category, transaction_date, processed_at)
            VALUES (?, ?, ?, 'USD', ?, ?, ?, ?)
        ''', (txn_id, customer_id, amount, new_type, description, txn_date, datetime.utcnow().isoformat()))

    target.commit()
    print(f"Migrated {len(rows)} transactions → financial_transactions")
    return len(rows)


def run_migration():
    """Run the V1 → V2 migration."""
    print("=== Schema Evolution Migration: V1 → V2 ===")
    print(f"Source: {SOURCE_DB}")
    print(f"Target: {TARGET_DB}")
    print()

    if not os.path.exists(SOURCE_DB):
        raise MigrationError(f"Source database not found: {SOURCE_DB}")

    # Remove existing target
    if os.path.exists(TARGET_DB):
        os.remove(TARGET_DB)

    source_conn = sqlite3.connect(SOURCE_DB)
    target_conn = sqlite3.connect(TARGET_DB)

    try:
        # Validate source schema
        validate_v1_schema(source_conn)

        # Create target schema
        create_v2_schema(target_conn)

        # Migrate data
        customers = migrate_customers(source_conn, target_conn)
        addresses = migrate_addresses(source_conn, target_conn)
        transactions = migrate_transactions(source_conn, target_conn)

        print()
        print("=== Migration Complete ===")
        print(f"  Customers: {customers}")
        print(f"  Addresses: {addresses}")
        print(f"  Transactions: {transactions}")
        print(f"  Target database: {TARGET_DB}")

        return 0

    except SchemaError as e:
        print(f"Schema Error: {e}", file=sys.stderr)
        return 2

    except MigrationError as e:
        print(f"Migration Error: {e}", file=sys.stderr)
        return 1

    finally:
        source_conn.close()
        target_conn.close()


if __name__ == '__main__':
    sys.exit(run_migration())
