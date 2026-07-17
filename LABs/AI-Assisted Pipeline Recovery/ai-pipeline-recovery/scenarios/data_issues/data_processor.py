#!/usr/bin/env python3
"""
data_processor.py - Process CSV/JSON data files with schema validation

This script demonstrates a data processing pipeline that can fail
when the input schema doesn't match expectations. It's designed
to be recovered by AI-assisted pipeline recovery.

Expected schema:
    - user_id: integer
    - name: string
    - email: string
    - age: integer
    - signup_date: date string (YYYY-MM-DD)
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Expected schema definition
EXPECTED_SCHEMA = {
    "user_id": int,
    "name": str,
    "email": str,
    "age": int,
    "signup_date": str,
}

# Column name mappings for common variations
COLUMN_MAPPINGS = {
    # Common variations -> expected name
    "id": "user_id",
    "userid": "user_id",
    "user": "user_id",
    "uid": "user_id",
    "username": "name",
    "full_name": "name",
    "fullname": "name",
    "mail": "email",
    "email_address": "email",
    "e-mail": "email",
    "years": "age",
    "date": "signup_date",
    "created": "signup_date",
    "created_at": "signup_date",
    "registration_date": "signup_date",
}


class SchemaError(Exception):
    """Raised when data doesn't match expected schema."""
    pass


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


def detect_file_type(filepath: Path) -> str:
    """Detect file type from extension."""
    suffix = filepath.suffix.lower()
    if suffix == ".csv":
        return "csv"
    elif suffix == ".json":
        return "json"
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def load_csv(filepath: Path) -> list[dict]:
    """Load data from CSV file."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_json(filepath: Path) -> list[dict]:
    """Load data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        else:
            raise ValueError("JSON must be an array or object with 'data' key")


def validate_schema(data: list[dict]) -> None:
    """
    Validate that data matches expected schema.
    Raises SchemaError with details if validation fails.
    """
    if not data:
        raise SchemaError("Empty dataset")

    # Check first record for schema
    first_record = data[0]
    actual_columns = set(first_record.keys())
    expected_columns = set(EXPECTED_SCHEMA.keys())

    # Find missing columns
    missing = expected_columns - actual_columns
    if missing:
        # Check if any mapped columns exist
        mapped_missing = []
        for col in missing:
            found_mapping = False
            for actual_col in actual_columns:
                if actual_col.lower() in COLUMN_MAPPINGS:
                    if COLUMN_MAPPINGS[actual_col.lower()] == col:
                        found_mapping = True
                        break
            if not found_mapping:
                mapped_missing.append(col)

        if mapped_missing:
            raise SchemaError(
                f"Missing required columns: {mapped_missing}\n"
                f"Available columns: {list(actual_columns)}\n"
                f"Expected columns: {list(expected_columns)}"
            )

    # Find extra columns (warning only)
    extra = actual_columns - expected_columns
    if extra:
        print(f"Warning: Extra columns found (will be ignored): {extra}", file=sys.stderr)


def validate_data(data: list[dict]) -> list[dict]:
    """
    Validate data values and convert types.
    Returns cleaned data or raises ValidationError.
    """
    cleaned = []
    errors = []

    for i, record in enumerate(data, 1):
        try:
            cleaned_record = {}

            # user_id
            user_id = record.get("user_id")
            if user_id is None:
                raise ValidationError(f"Row {i}: missing user_id")
            cleaned_record["user_id"] = int(user_id)

            # name
            name = record.get("name", "").strip()
            if not name:
                raise ValidationError(f"Row {i}: missing or empty name")
            cleaned_record["name"] = name

            # email
            email = record.get("email", "").strip()
            if not email or "@" not in email:
                raise ValidationError(f"Row {i}: invalid email '{email}'")
            cleaned_record["email"] = email

            # age
            age = record.get("age")
            if age is None:
                raise ValidationError(f"Row {i}: missing age")
            age = int(age)
            if age < 0 or age > 150:
                raise ValidationError(f"Row {i}: age out of range: {age}")
            cleaned_record["age"] = age

            # signup_date
            signup_date = record.get("signup_date", "").strip()
            if signup_date:
                try:
                    datetime.strptime(signup_date, "%Y-%m-%d")
                except ValueError:
                    raise ValidationError(
                        f"Row {i}: invalid date format '{signup_date}', expected YYYY-MM-DD"
                    )
            cleaned_record["signup_date"] = signup_date

            cleaned.append(cleaned_record)

        except (ValueError, TypeError) as e:
            errors.append(f"Row {i}: {e}")

    if errors:
        raise ValidationError(
            f"Validation failed with {len(errors)} errors:\n" + "\n".join(errors[:10])
        )

    return cleaned


def process_data(data: list[dict]) -> dict:
    """
    Process the validated data and compute statistics.
    """
    total_users = len(data)
    avg_age = sum(r["age"] for r in data) / total_users if total_users else 0

    # Group by signup year
    signups_by_year = {}
    for record in data:
        if record["signup_date"]:
            year = record["signup_date"][:4]
            signups_by_year[year] = signups_by_year.get(year, 0) + 1

    return {
        "total_users": total_users,
        "average_age": round(avg_age, 2),
        "signups_by_year": signups_by_year,
        "email_domains": list(set(r["email"].split("@")[1] for r in data)),
    }


def save_output(results: dict, output_path: Path) -> None:
    """Save processing results to JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Process CSV/JSON data files with schema validation"
    )
    parser.add_argument("input_file", type=Path, help="Input data file (CSV or JSON)")
    parser.add_argument(
        "-o", "--output", type=Path, default=None, help="Output JSON file for results"
    )
    parser.add_argument(
        "--schema-only", action="store_true", help="Only validate schema, don't process"
    )
    parser.add_argument(
        "--show-schema", action="store_true", help="Show expected schema and exit"
    )

    args = parser.parse_args()

    if args.show_schema:
        print("Expected schema:")
        for col, col_type in EXPECTED_SCHEMA.items():
            print(f"  {col}: {col_type.__name__}")
        print("\nAccepted column name variations:")
        for alt, canonical in sorted(COLUMN_MAPPINGS.items()):
            print(f"  {alt} -> {canonical}")
        return 0

    # Check input file exists
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        return 1

    try:
        # Detect and load file
        file_type = detect_file_type(args.input_file)
        print(f"Loading {file_type.upper()} file: {args.input_file}")

        if file_type == "csv":
            data = load_csv(args.input_file)
        else:
            data = load_json(args.input_file)

        print(f"Loaded {len(data)} records")

        # Validate schema
        print("Validating schema...")
        validate_schema(data)
        print("Schema validation passed")

        if args.schema_only:
            return 0

        # Validate and clean data
        print("Validating data...")
        cleaned_data = validate_data(data)
        print(f"Data validation passed: {len(cleaned_data)} valid records")

        # Process data
        print("Processing data...")
        results = process_data(cleaned_data)

        # Output results
        print("\n=== Processing Results ===")
        print(json.dumps(results, indent=2))

        if args.output:
            save_output(results, args.output)

        return 0

    except SchemaError as e:
        print(f"Schema Error: {e}", file=sys.stderr)
        return 2

    except ValidationError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        return 3

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
