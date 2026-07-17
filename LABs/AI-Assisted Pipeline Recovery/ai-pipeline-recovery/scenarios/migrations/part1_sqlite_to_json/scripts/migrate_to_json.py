#!/usr/bin/env python3
"""
migrate_to_json.py - Migrate SQLite database to JSON Data Lake format

This script exports normalized SQL tables to denormalized JSON files
suitable for data lake/analytics platforms.

Expected output structure:
- users.json: User records with embedded order history
- products.json: Product catalog with sales stats
- orders_flat.json: Flattened order records with user/product details

Potential failures (for AI recovery demo):
- Missing tables
- Column name mismatches
- Foreign key violations
- Date format issues
- NULL handling
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

# Configuration - can be overridden by environment
SOURCE_DB = os.environ.get('SOURCE_DB', os.path.join(DATA_DIR, 'source_ecommerce.db'))
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.join(DATA_DIR, 'json_export'))

# Expected schema (for validation)
EXPECTED_TABLES = {
    'users': ['user_id', 'username', 'full_name', 'email', 'birth_date', 'account_type'],
    'products': ['product_id', 'name', 'category', 'price', 'stock_quantity', 'is_active'],
    'orders': ['order_id', 'user_id', 'product_id', 'quantity', 'unit_price', 'total_amount', 'order_date', 'ship_date', 'status'],
}


class MigrationError(Exception):
    """Custom exception for migration failures."""
    pass


class SchemaValidationError(MigrationError):
    """Raised when schema doesn't match expectations."""
    pass


class DataIntegrityError(MigrationError):
    """Raised when data integrity checks fail."""
    pass


def connect_db(db_path: str) -> sqlite3.Connection:
    """Connect to SQLite database with row factory."""
    if not os.path.exists(db_path):
        raise MigrationError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def validate_schema(conn: sqlite3.Connection) -> None:
    """Validate that all expected tables and columns exist."""
    cursor = conn.cursor()

    # Get actual tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    actual_tables = {row[0] for row in cursor.fetchall()}

    # Check for missing tables
    missing_tables = set(EXPECTED_TABLES.keys()) - actual_tables
    if missing_tables:
        raise SchemaValidationError(
            f"Missing tables: {missing_tables}\n"
            f"Available tables: {actual_tables}\n"
            f"Expected tables: {set(EXPECTED_TABLES.keys())}"
        )

    # Check columns for each table
    for table, expected_cols in EXPECTED_TABLES.items():
        cursor.execute(f"PRAGMA table_info({table})")
        actual_cols = [row[1] for row in cursor.fetchall()]

        missing_cols = set(expected_cols) - set(actual_cols)
        if missing_cols:
            raise SchemaValidationError(
                f"Table '{table}' missing columns: {missing_cols}\n"
                f"Available columns: {actual_cols}\n"
                f"Expected columns: {expected_cols}"
            )

    print("Schema validation passed")


def convert_value(value: Any, target_type: str = None) -> Any:
    """Convert SQLite values to JSON-compatible format."""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return value


def export_users_with_orders(conn: sqlite3.Connection, output_path: str) -> int:
    """Export users with embedded order history."""
    cursor = conn.cursor()

    # Get all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    result = []
    for user in users:
        user_dict = dict(user)
        user_id = user_dict['user_id']

        # Get orders for this user
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.category as product_category
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.user_id = ?
            ORDER BY o.order_date DESC
        """, (user_id,))
        orders = cursor.fetchall()

        # Convert to JSON-friendly format
        user_export = {
            'id': user_dict['user_id'],
            'username': user_dict['username'],
            'fullName': user_dict['full_name'],  # camelCase for JSON
            'email': user_dict['email'],
            'birthDate': user_dict['birth_date'],
            'accountType': user_dict['account_type'],
            'orderCount': len(orders),
            'totalSpent': sum(o['total_amount'] for o in orders),
            'orders': [
                {
                    'orderId': o['order_id'],
                    'productName': o['product_name'],
                    'productCategory': o['product_category'],
                    'quantity': o['quantity'],
                    'totalAmount': o['total_amount'],
                    'orderDate': o['order_date'],
                    'shipDate': o['ship_date'],
                    'status': o['status'],
                }
                for o in orders
            ],
            'exportedAt': datetime.utcnow().isoformat() + 'Z',
        }
        result.append(user_export)

    # Write JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(result)} users to {output_path}")
    return len(result)


def export_products_with_stats(conn: sqlite3.Connection, output_path: str) -> int:
    """Export products with sales statistics."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.*,
            COALESCE(SUM(o.quantity), 0) as total_sold,
            COALESCE(SUM(o.total_amount), 0) as total_revenue,
            COUNT(DISTINCT o.user_id) as unique_buyers
        FROM products p
        LEFT JOIN orders o ON p.product_id = o.product_id
        GROUP BY p.product_id
    """)
    products = cursor.fetchall()

    result = []
    for product in products:
        product_export = {
            'id': product['product_id'],
            'name': product['name'],
            'category': product['category'],
            'price': product['price'],
            'stockQuantity': product['stock_quantity'],
            'isActive': bool(product['is_active']),
            'salesStats': {
                'totalSold': product['total_sold'],
                'totalRevenue': round(product['total_revenue'], 2),
                'uniqueBuyers': product['unique_buyers'],
            },
            'exportedAt': datetime.utcnow().isoformat() + 'Z',
        }
        result.append(product_export)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(result)} products to {output_path}")
    return len(result)


def export_orders_flat(conn: sqlite3.Connection, output_path: str) -> int:
    """Export flattened order records (denormalized)."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            o.*,
            u.username,
            u.full_name as user_full_name,
            u.email as user_email,
            p.name as product_name,
            p.category as product_category,
            p.price as product_current_price
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN products p ON o.product_id = p.product_id
        ORDER BY o.order_date DESC
    """)
    orders = cursor.fetchall()

    result = []
    for order in orders:
        order_export = {
            'orderId': order['order_id'],
            'orderDate': order['order_date'],
            'shipDate': order['ship_date'],
            'status': order['status'],
            'quantity': order['quantity'],
            'unitPrice': order['unit_price'],
            'totalAmount': order['total_amount'],
            'user': {
                'id': order['user_id'],
                'username': order['username'],
                'fullName': order['user_full_name'],
                'email': order['user_email'],
            },
            'product': {
                'id': order['product_id'],
                'name': order['product_name'],
                'category': order['product_category'],
                'currentPrice': order['product_current_price'],
            },
            'exportedAt': datetime.utcnow().isoformat() + 'Z',
        }
        result.append(order_export)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(result)} orders to {output_path}")
    return len(result)


def run_migration():
    """Run the full migration process."""
    print(f"=== SQLite to JSON Data Lake Migration ===")
    print(f"Source: {SOURCE_DB}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # Connect to database
    conn = connect_db(SOURCE_DB)

    try:
        # Validate schema
        validate_schema(conn)

        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Export each entity
        users_count = export_users_with_orders(
            conn, os.path.join(OUTPUT_DIR, 'users.json')
        )
        products_count = export_products_with_stats(
            conn, os.path.join(OUTPUT_DIR, 'products.json')
        )
        orders_count = export_orders_flat(
            conn, os.path.join(OUTPUT_DIR, 'orders_flat.json')
        )

        # Summary
        print()
        print("=== Migration Complete ===")
        print(f"  Users exported: {users_count}")
        print(f"  Products exported: {products_count}")
        print(f"  Orders exported: {orders_count}")
        print(f"  Output directory: {OUTPUT_DIR}")

        return 0

    except SchemaValidationError as e:
        print(f"Schema Validation Error: {e}", file=sys.stderr)
        return 2

    except DataIntegrityError as e:
        print(f"Data Integrity Error: {e}", file=sys.stderr)
        return 3

    except MigrationError as e:
        print(f"Migration Error: {e}", file=sys.stderr)
        return 1

    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(run_migration())
