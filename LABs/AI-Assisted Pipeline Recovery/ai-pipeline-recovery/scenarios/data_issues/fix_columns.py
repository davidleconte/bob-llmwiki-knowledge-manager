#!/usr/bin/env python3
"""
fix_columns.py - Transform CSV column names to match expected schema

This script is an example of what the AI might generate to fix column mismatches.
It can be used as a reference or called directly.

Usage:
    python fix_columns.py input.csv output.csv
    python fix_columns.py input.csv  # modifies in place
"""

import argparse
import csv
import sys
from pathlib import Path

# Mapping from common variations to expected column names
COLUMN_MAPPINGS = {
    "id": "user_id",
    "userid": "user_id",
    "user": "user_id",
    "uid": "user_id",
    "fullname": "name",
    "full_name": "name",
    "username": "name",
    "mail": "email",
    "email_address": "email",
    "e-mail": "email",
    "years": "age",
    "date": "signup_date",
    "created": "signup_date",
    "created_at": "signup_date",
    "registration_date": "signup_date",
}


def normalize_column_name(col: str) -> str:
    """Normalize a column name to expected format."""
    col_lower = col.lower().strip()
    return COLUMN_MAPPINGS.get(col_lower, col)


def transform_csv(input_path: Path, output_path: Path) -> dict:
    """
    Transform CSV column names to match expected schema.
    Returns dict with transformation details.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        original_columns = reader.fieldnames
        rows = list(reader)

    # Build column mapping
    mapping = {}
    for col in original_columns:
        new_col = normalize_column_name(col)
        if new_col != col:
            mapping[col] = new_col

    # Transform column names in rows
    new_columns = [normalize_column_name(col) for col in original_columns]
    transformed_rows = []
    for row in rows:
        new_row = {normalize_column_name(k): v for k, v in row.items()}
        transformed_rows.append(new_row)

    # Write output
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_columns)
        writer.writeheader()
        writer.writerows(transformed_rows)

    return {
        "original_columns": original_columns,
        "new_columns": new_columns,
        "mappings_applied": mapping,
        "rows_processed": len(transformed_rows),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Transform CSV column names to match expected schema"
    )
    parser.add_argument("input_file", type=Path, help="Input CSV file")
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        default=None,
        help="Output CSV file (default: modify input in place)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying"
    )

    args = parser.parse_args()

    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        return 1

    output_file = args.output_file or args.input_file

    if args.dry_run:
        # Just show the mapping
        with open(args.input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            original_columns = reader.fieldnames

        print("Column transformation preview:")
        for col in original_columns:
            new_col = normalize_column_name(col)
            if new_col != col:
                print(f"  {col} -> {new_col}")
            else:
                print(f"  {col} (unchanged)")
        return 0

    result = transform_csv(args.input_file, output_file)

    print(f"Transformed {result['rows_processed']} rows")
    print(f"Output written to: {output_file}")

    if result["mappings_applied"]:
        print("Column mappings applied:")
        for old, new in result["mappings_applied"].items():
            print(f"  {old} -> {new}")
    else:
        print("No column mappings needed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
