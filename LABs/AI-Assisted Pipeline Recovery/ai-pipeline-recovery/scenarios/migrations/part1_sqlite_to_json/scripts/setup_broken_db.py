#!/usr/bin/env python3
"""
setup_broken_db.py - Create a "broken" source database for AI recovery demo

This creates a database with intentional issues:
- Renamed columns (user_id → id, full_name → name)
- Missing table (products renamed to inventory)
- Different date format (MM/DD/YYYY instead of YYYY-MM-DD)

The AI should be able to:
1. Detect the schema mismatches
2. Suggest SQL to create views or rename columns
3. Or suggest migration script modifications
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'source_ecommerce_broken.db')

# Sample data with DIFFERENT column names and formats
USERS = [
    (1, 'alice_j', 'Alice Johnson', 'alice@example.com', '03/15/1995', 'premium'),  # MM/DD/YYYY format
    (2, 'bob_smith', 'Bob Smith', 'bob.smith@company.org', '07/22/1988', 'standard'),
    (3, 'carol_w', 'Carol Williams', 'carol.w@email.net', '11/08/1992', 'premium'),
    (4, 'david_b', 'David Brown', 'david.brown@work.com', '01/30/1985', 'standard'),
    (5, 'eva_m', 'Eva Martinez', 'eva.m@startup.io', '06/12/1990', 'premium'),
]

PRODUCTS = [
    (101, 'Laptop Pro 15', 'Electronics', 1299.99, 50, 1),
    (102, 'Wireless Mouse', 'Electronics', 29.99, 200, 1),
    (103, 'USB-C Hub', 'Electronics', 49.99, 150, 1),
    (104, 'Standing Desk', 'Furniture', 599.99, 25, 1),
    (105, 'Ergonomic Chair', 'Furniture', 399.99, 40, 1),
    (106, 'Monitor 27"', 'Electronics', 349.99, 0, 0),
    (107, 'Keyboard Mechanical', 'Electronics', 89.99, 75, 1),
    (108, 'Webcam HD', 'Electronics', 79.99, 100, 1),
]


def generate_orders():
    """Generate sample orders."""
    orders = []
    order_id = 1000
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    base_date = datetime(2024, 1, 1)

    for uid in range(1, 6):
        num_orders = random.randint(2, 5)
        for _ in range(num_orders):
            product = random.choice(PRODUCTS)
            pid = product[0]
            qty = random.randint(1, 3)
            price = product[3]
            total = round(price * qty, 2)

            order_date = base_date + timedelta(days=random.randint(0, 365))
            status = random.choice(statuses)
            ship_date = None
            if status in ['shipped', 'delivered']:
                ship_date = (order_date + timedelta(days=random.randint(1, 5))).strftime('%m/%d/%Y')

            orders.append((
                order_id,
                uid,
                pid,
                qty,
                price,
                total,
                order_date.strftime('%m/%d/%Y'),  # Wrong format!
                ship_date,
                status
            ))
            order_id += 1

    return orders


def create_broken_database():
    """Create a database with schema issues."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table with RENAMED columns (id instead of user_id, name instead of full_name)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            dob TEXT,
            tier TEXT DEFAULT 'standard'
        )
    ''')

    # Products table RENAMED to 'inventory' with different columns
    cursor.execute('''
        CREATE TABLE inventory (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            department TEXT NOT NULL,
            unit_price REAL NOT NULL,
            qty_on_hand INTEGER DEFAULT 0,
            available INTEGER DEFAULT 1
        )
    ''')

    # Orders table with some renamed columns
    cursor.execute('''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            order_total REAL NOT NULL,
            order_dt TEXT NOT NULL,
            ship_dt TEXT,
            order_status TEXT DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES users(id),
            FOREIGN KEY (item_id) REFERENCES inventory(item_id)
        )
    ''')

    # Insert users with renamed columns
    cursor.executemany(
        'INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)',
        USERS
    )

    # Insert products into 'inventory' table
    cursor.executemany(
        'INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)',
        PRODUCTS
    )

    # Insert orders
    random.seed(42)
    orders = generate_orders()
    cursor.executemany(
        'INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        orders
    )

    conn.commit()

    print(f"Broken database created: {DB_PATH}")
    print(f"  Users: {cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
    print(f"  Inventory: {cursor.execute('SELECT COUNT(*) FROM inventory').fetchone()[0]}")
    print(f"  Orders: {cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]}")
    print()
    print("Schema differences from expected:")
    print("  - 'products' table renamed to 'inventory'")
    print("  - users.user_id → users.id")
    print("  - users.full_name → users.name")
    print("  - users.birth_date → users.dob")
    print("  - users.account_type → users.tier")
    print("  - products columns renamed (product_id→item_id, name→item_name, etc)")
    print("  - orders.user_id → orders.customer_id")
    print("  - Date format: MM/DD/YYYY instead of YYYY-MM-DD")

    conn.close()
    return DB_PATH


if __name__ == '__main__':
    create_broken_database()
