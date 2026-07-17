#!/usr/bin/env python3
"""
etl_pipeline.py - Full ETL Pipeline: CSV → SQLite → JSON

This script demonstrates a complete ETL (Extract, Transform, Load) pipeline:
1. EXTRACT: Read sales data from CSV
2. TRANSFORM: Clean, validate, normalize into SQLite tables
3. LOAD: Export to JSON for data lake/analytics

Expected CSV columns:
- sale_id, date, customer_name, customer_email, product, category
- quantity, unit_price, total, region, sales_rep

Potential failures (for AI recovery demo):
- Column name mismatches
- Date format variations
- Data type issues
- Missing required fields
"""

import csv
import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

# Configuration
CSV_INPUT = os.environ.get('CSV_INPUT', os.path.join(DATA_DIR, 'sales_data.csv'))
SQLITE_DB = os.environ.get('SQLITE_DB', os.path.join(DATA_DIR, 'sales_warehouse.db'))
JSON_OUTPUT = os.environ.get('JSON_OUTPUT', os.path.join(DATA_DIR, 'sales_export.json'))

# Expected CSV schema
EXPECTED_COLUMNS = [
    'sale_id', 'date', 'customer_name', 'customer_email',
    'product', 'category', 'quantity', 'unit_price', 'total',
    'region', 'sales_rep'
]


class ETLError(Exception):
    """Base ETL error."""
    pass


class ExtractError(ETLError):
    """Error during extraction phase."""
    pass


class TransformError(ETLError):
    """Error during transformation phase."""
    pass


class LoadError(ETLError):
    """Error during load phase."""
    pass


def validate_csv_schema(headers: List[str]) -> None:
    """Validate CSV has expected columns."""
    headers_lower = [h.lower().strip() for h in headers]
    expected_lower = [c.lower() for c in EXPECTED_COLUMNS]

    missing = set(expected_lower) - set(headers_lower)
    if missing:
        raise ExtractError(
            f"CSV schema validation failed.\n"
            f"Missing columns: {missing}\n"
            f"Found columns: {headers}\n"
            f"Expected columns: {EXPECTED_COLUMNS}"
        )


def parse_date(date_str: str) -> str:
    """Parse date string to ISO format (YYYY-MM-DD)."""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    raise TransformError(f"Unable to parse date: '{date_str}'. Expected formats: {formats}")


def extract_csv(filepath: str) -> List[Dict[str, Any]]:
    """Extract data from CSV file."""
    print(f"EXTRACT: Reading CSV from {filepath}")

    if not os.path.exists(filepath):
        raise ExtractError(f"CSV file not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        if not headers:
            raise ExtractError("CSV file is empty or has no headers")

        validate_csv_schema(headers)

        rows = list(reader)

    print(f"  Extracted {len(rows)} rows")
    return rows


def transform_to_sqlite(rows: List[Dict[str, Any]], db_path: str) -> sqlite3.Connection:
    """Transform and load data into SQLite (normalized schema)."""
    print(f"TRANSFORM: Loading into SQLite at {db_path}")

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create normalized tables
    cursor.execute('''
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE sales_reps (
            rep_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            region TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE sales (
            sale_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            rep_id INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            region TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (rep_id) REFERENCES sales_reps(rep_id)
        )
    ''')

    # Track unique entities
    customers = {}
    products = {}
    reps = {}

    for row in rows:
        # Parse and validate date
        sale_date = parse_date(row['date'])

        # Get or create customer
        cust_email = row['customer_email'].lower().strip()
        if cust_email not in customers:
            cursor.execute(
                'INSERT INTO customers (name, email) VALUES (?, ?)',
                (row['customer_name'], cust_email)
            )
            customers[cust_email] = cursor.lastrowid

        # Get or create product
        prod_name = row['product'].strip()
        if prod_name not in products:
            cursor.execute(
                'INSERT INTO products (name, category) VALUES (?, ?)',
                (prod_name, row['category'])
            )
            products[prod_name] = cursor.lastrowid

        # Get or create sales rep
        rep_name = row['sales_rep'].strip()
        if rep_name not in reps:
            cursor.execute(
                'INSERT INTO sales_reps (name, region) VALUES (?, ?)',
                (rep_name, row['region'])
            )
            reps[rep_name] = cursor.lastrowid

        # Insert sale record
        cursor.execute('''
            INSERT INTO sales (sale_id, customer_id, product_id, rep_id,
                              sale_date, quantity, unit_price, total_amount, region)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(row['sale_id']),
            customers[cust_email],
            products[prod_name],
            reps[rep_name],
            sale_date,
            int(row['quantity']),
            float(row['unit_price']),
            float(row['total']),
            row['region']
        ))

    conn.commit()

    print(f"  Created {len(customers)} customers")
    print(f"  Created {len(products)} products")
    print(f"  Created {len(reps)} sales reps")
    print(f"  Loaded {len(rows)} sales records")

    return conn


def load_to_json(conn: sqlite3.Connection, output_path: str) -> int:
    """Load data from SQLite to JSON (denormalized for analytics)."""
    print(f"LOAD: Exporting to JSON at {output_path}")

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Export denormalized sales data
    cursor.execute('''
        SELECT
            s.sale_id,
            s.sale_date,
            s.quantity,
            s.unit_price,
            s.total_amount,
            s.region,
            c.name as customer_name,
            c.email as customer_email,
            p.name as product_name,
            p.category as product_category,
            r.name as sales_rep_name
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products p ON s.product_id = p.product_id
        JOIN sales_reps r ON s.rep_id = r.rep_id
        ORDER BY s.sale_date
    ''')

    rows = cursor.fetchall()

    # Convert to JSON-friendly format
    result = {
        'exportedAt': datetime.utcnow().isoformat() + 'Z',
        'recordCount': len(rows),
        'sales': [
            {
                'saleId': row['sale_id'],
                'saleDate': row['sale_date'],
                'quantity': row['quantity'],
                'unitPrice': row['unit_price'],
                'totalAmount': row['total_amount'],
                'region': row['region'],
                'customer': {
                    'name': row['customer_name'],
                    'email': row['customer_email'],
                },
                'product': {
                    'name': row['product_name'],
                    'category': row['product_category'],
                },
                'salesRep': row['sales_rep_name'],
            }
            for row in rows
        ]
    }

    # Add summary statistics
    cursor.execute('SELECT SUM(total_amount) as total, COUNT(*) as count FROM sales')
    stats = cursor.fetchone()
    result['summary'] = {
        'totalSales': round(stats['total'], 2),
        'transactionCount': stats['count'],
    }

    # Write JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  Exported {len(rows)} records to JSON")
    return len(rows)


def run_etl():
    """Run the complete ETL pipeline."""
    print("=" * 50)
    print("Full ETL Pipeline: CSV → SQLite → JSON")
    print("=" * 50)
    print(f"Input CSV:  {CSV_INPUT}")
    print(f"SQLite DB:  {SQLITE_DB}")
    print(f"Output JSON: {JSON_OUTPUT}")
    print()

    try:
        # Phase 1: Extract
        rows = extract_csv(CSV_INPUT)

        # Phase 2: Transform
        conn = transform_to_sqlite(rows, SQLITE_DB)

        # Phase 3: Load
        count = load_to_json(conn, JSON_OUTPUT)

        conn.close()

        print()
        print("=" * 50)
        print("ETL Pipeline Complete!")
        print("=" * 50)
        return 0

    except ExtractError as e:
        print(f"EXTRACT ERROR: {e}", file=sys.stderr)
        return 2

    except TransformError as e:
        print(f"TRANSFORM ERROR: {e}", file=sys.stderr)
        return 3

    except LoadError as e:
        print(f"LOAD ERROR: {e}", file=sys.stderr)
        return 4

    except Exception as e:
        print(f"ETL ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(run_etl())
