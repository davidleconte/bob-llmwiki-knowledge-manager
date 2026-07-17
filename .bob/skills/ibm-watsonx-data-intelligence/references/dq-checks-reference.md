# DQ Validator — Checks, Dimensions & Results

Complete reference for the validation framework (SKILL.md §3). Import root
`wxdi.dq_validator`; checks also under `wxdi.dq_validator.checks`.

## Metadata & data types

```python
from wxdi.dq_validator import AssetMetadata, ColumnMetadata, DataType

metadata = AssetMetadata(table_name="employees", columns=[
    ColumnMetadata("emp_id", DataType.INTEGER),
    ColumnMetadata("name", DataType.STRING, length=100),
    ColumnMetadata("salary", DataType.DECIMAL, precision=10, scale=2),
])
```
`DataType`: `INTEGER`, `FLOAT`, `DECIMAL`, `STRING`, `BOOLEAN`, `DATE`, `TIME`,
`DATETIME`, `TIMESTAMP`. **A record is an array of values in column order** — not a
dict.

## The 9 checks

### 1. LengthCheck — length of any value (stringified first)
```python
LengthCheck(min_length=3, max_length=20)   # 12345 -> "12345" (len 5)
```
`min_length` / `max_length` (inclusive; at least one required). None → error.

### 2. ValidValuesCheck — membership in an allowed list
```python
ValidValuesCheck(["active", "inactive"], case_sensitive=False)  # default False
```
None → error. Non-string types always exact-match (case flag ignored).

### 3. ComparisonCheck — compare to a constant or another column
```python
ComparisonCheck(operator=ComparisonOperator.GREATER_THAN, target_value=18)
ComparisonCheck(operator=">=", target_column="min_salary")   # string operator ok
```
Operators: `>` `<` `>=` `<=` `==` `!=` (or the `ComparisonOperator` enum members
`GREATER_THAN`, `LESS_THAN`, `GREATER_THAN_OR_EQUAL`, `LESS_THAN_OR_EQUAL`,
`EQUAL`, `NOT_EQUAL`). Works on numbers, strings (lexicographic), dates/datetimes,
booleans.

### 4. CaseCheck — character case
```python
from wxdi.dq_validator import CaseCheck, ColumnCaseEnum
CaseCheck(case_type=ColumnCaseEnum.UPPER_CASE)
```
`ColumnCaseEnum`: `ANY_CASE`, `UPPER_CASE`, `LOWER_CASE`, `NAME_CASE` (Title Case),
`SENTENCE_CASE`.

### 5. CompletenessCheck — presence (non-null)
```python
CompletenessCheck(missing_values_allowed=False)   # True to allow null
```

### 6. RangeCheck — within min/max (inclusive)
```python
RangeCheck(min_value=0, max_value=100)
RangeCheck(min_value=date(2020,1,1), max_value=date(2025,12,31))   # dates
RangeCheck(min_value="A", max_value="Z")                          # strings (lexicographic)
```

### 7. RegexCheck — pattern match
```python
RegexCheck(pattern=r"^\d{3}-\d{3}-\d{4}$")
RegexCheck(pattern=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", case_sensitive=False)  # default True
```

### 8. FormatCheck — intelligent format detection (date/time/timestamp)
```python
from wxdi.dq_validator import FormatCheck, FormatConstraintType
FormatCheck(constraint_type=FormatConstraintType.ValidFormats,
            formats={"%Y-%m-%d", "%d/%m/%Y"})
FormatCheck(constraint_type=FormatConstraintType.InvalidFormats, formats={"%Y%m%d"})
```

### 9. DataTypeCheck — intelligent type inference
```python
from wxdi.dq_validator import DataTypeCheck, DataType
DataTypeCheck(expected_type=DataType.INTEGER)
```
Handles US/DE numeric formats and date/time detection.

## Data Quality Dimensions

```python
from wxdi.dq_validator.data_quality_dimension import DataQualityDimension
```
8 dimensions: `ACCURACY`, `COMPLETENESS`, `CONFORMITY`, `CONSISTENCY`, `COVERAGE`,
`TIMELINESS`, `UNIQUENESS`, `VALIDITY`.

Defaults: `CompletenessCheck`→COMPLETENESS; `CaseCheck`→CONSISTENCY; all others
→VALIDITY. Override:
```python
check = LengthCheck(min_length=5)
check.set_dimension(DataQualityDimension.CONFORMITY)
check.get_dimension()
```
Use dimensions for dimension-level reporting, prioritization, and alignment with
governance frameworks.

## Rules & validator

```python
from wxdi.dq_validator import Validator, ValidationRule
v = Validator(metadata)
v.add_rule(ValidationRule("name").add_check(LengthCheck(min_length=2)).add_check(...))
result  = v.validate(record)          # single
results = v.validate_batch(records)   # list
```
Multiple checks per rule chain with `.add_check(...)`. Table-level rules via
`v.add_table_rule(TableValidationRule(name).add_check(TableCELCheck(...)))` (see
`references/cel-expressions.md`).

## Results

`ValidationResult`: `.is_valid` (bool), `.score` ("5/5"), `.pass_rate` (float
0–100), `.total_checks`, `.passed_checks`, `.failed_checks`, `.errors`
(List[`ValidationError`]), `.to_dict()`.

`ValidationError`: `.column_name`, `.check_name`, `.message`, `.value` (the failing
value), `.expected` (constraint), `.to_dict()`.

## Extending

Add a custom check by subclassing `BaseCheck` (in `wxdi.dq_validator.base`).
External rule sources load via `RuleLoader`.
