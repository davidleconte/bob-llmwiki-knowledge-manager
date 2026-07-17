#!/usr/bin/env python3
"""
setup_source_db.py - Create source SQLite database with normalized tables

This creates a typical e-commerce database with:
- users table
- products table
- orders table (references users and products)

Used as the source for SQLite → JSON Data Lake migration.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'source_ecommerce.db')

# Sample data
USERS = [
    (1, 'alice_j', 'Alice Johnson', 'alice@example.com', '1995-03-15', 'premium'),
    (2, 'bob_smith', 'Bob Smith', 'bob.smith@company.org', '1988-07-22', 'standard'),
    (3, 'carol_w', 'Carol Williams', 'carol.w@email.net', '1992-11-08', 'premium'),
    (4, 'david_b', 'David Brown', 'david.brown@work.com', '1985-01-30', 'standard'),
    (5, 'eva_m', 'Eva Martinez', 'eva.m@startup.io', '1990-06-12', 'premium'),
]

PRODUCTS = [
    (101, 'Laptop Pro 15', 'Electronics', 1299.99, 50, True),
    (102, 'Wireless Mouse', 'Electronics', 29.99, 200, True),
    (103, 'USB-C Hub', 'Electronics', 49.99, 150, True),
    (104, 'Standing Desk', 'Furniture', 599.99, 25, True),
    (105, 'Ergonomic Chair', 'Furniture', 399.99, 40, True),
    (106, 'Monitor 27"', 'Electronics', 349.99, 0, False),  # Out of stock
    (107, 'Keyboard Mechanical', 'Electronics', 89.99, 75, True),
    (108, 'Webcam HD', 'Electronics', 79.99, 100, True),
]

def generate_orders():
    """Generate sample orders with various statuses."""
    orders = []
    order_id = 1000
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

    base_date = datetime(2024, 1, 1)

    for user_id in range(1, 6):
        # Each user has 2-5 orders
        num_orders = random.randint(2, 5)
        for _ in range(num_orders):
            product = random.choice(PRODUCTS)
            product_id = product[0]
            quantity = random.randint(1, 3)
            unit_price = product[3]
            total = round(unit_price * quantity, 2)

            order_date = base_date + timedelta(days=random.randint(0, 365))
            status = random.choice(statuses)

            # Shipped/delivered orders have ship date
            ship_date = None
            if status in ['shipped', 'delivered']:
                ship_date = (order_date + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')

            orders.append((
                order_id,
                user_id,
                product_id,
                quantity,
                unit_price,
                total,
                order_date.strftime('%Y-%m-%d'),
                ship_date,
                status
            ))
            order_id += 1

    return orders


def create_database():
    """Create the source SQLite database."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            birth_date TEXT,
            account_type TEXT DEFAULT 'standard'
        )
    ''')

    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            ship_date TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Insert data
    cursor.executemany(
        'INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)',
        USERS
    )

    cursor.executemany(
        'INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
        PRODUCTS
    )

    random.seed(42)  # Reproducible orders
    orders = generate_orders()
    cursor.executemany(
        'INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        orders
    )

    conn.commit()

    # Print summary
    print(f"Database created: {DB_PATH}")
    print(f"  Users: {cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
    print(f"  Products: {cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]}")
    print(f"  Orders: {cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]}")

    conn.close()
    return DB_PATH


if __name__ == '__main__':
    create_database()
