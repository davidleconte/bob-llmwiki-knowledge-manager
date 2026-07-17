# CEL Expression Validation

CEL (Common Expression Language) defines custom validation logic without Python
code — safe, non-Turing-complete, fast (~10–100µs/record). Needs
`pip install "cel-python>=0.5.0"`. (SKILL.md §3.)

> **Column names are CASE-SENSITIVE.** `birth_date` ≠ `Birth_date` ≠ `birthDate`.
> Use the exact name from `AssetMetadata`.

## Two CEL flavors

| | Column-level `CELCheck` | Table-level `TableCELCheck` |
|---|---|---|
| Validates | one column value | the whole record |
| Has `value` var | **yes** (current column) | **no** |
| Added via | `ValidationRule('col').add_check(...)` | `TableValidationRule('name').add_check(...)` + `validator.add_table_rule(...)` |
| Example | `value > 0` | `salary > min_salary` |

```python
from wxdi.dq_validator import (
    Validator, ValidationRule, TableValidationRule, CELCheck, TableCELCheck,
)
v = Validator(metadata)
v.add_rule(ValidationRule("salary").add_check(CELCheck("value > 0")))
v.add_table_rule(TableValidationRule("salary_check")
                 .add_check(TableCELCheck("salary > min_salary && age >= 18")))
```

## Variables

- `value` — the current column value (column-level only).
- `<column_name>` — direct access to any column by name (e.g. `min_salary`, `age`).
- `record` — explicit access (`record.min_salary`); optional, for clarity.
- `column_name` — name of the column being validated (string).
- `record_index` — 0-based position in the batch.

**Reserved names:** if a column is literally named `value`, `column_name`,
`record_index`, or `record`, access it with the `record.` prefix (`record.value`).

## Operators

- Comparison: `==` `!=` `>` `>=` `<` `<=`
- Logical: `&&` `||` `!`  (e.g. `value > 0 && value < 100`, `!(value == 0)`)
- Arithmetic: `+` `-` `*` `/` `%`  (e.g. `value == record.price * record.quantity`)
- String: `value.startsWith("admin_")`, `value.endsWith("@co.com")`, `"@" in value`
- List: `value in ["Active","Pending"]`, `!(value in ["Deleted"])`

## Conditionals (ternary)

```python
CELCheck("record.age > 40 ? value >= 80000 : value >= 50000")
CELCheck('record.department == "Sales" ? value <= 20000 : value <= 10000')
```

## Constructor

```python
CELCheck(expression: str, error_message=None,
         dimension=DataQualityDimension.VALIDITY, description=None)
```
Methods: `.validate(value, context)`, `.get_expression()`, `.get_description()`.

## Validate references early

```python
check = TableCELCheck("salary > max_salary")
check.validate_column_references([c.name for c in metadata.columns])  # raises ValueError if missing
```
Table-level CEL auto-extracts only the referenced columns into context (efficient
for 100+ column tables).

## Errors

- `CELCompilationError` — raised **at check creation** for bad syntax (expressions
  compile eagerly).
- `CELEvaluationError` / returned `ValidationError` — runtime issues (type
  mismatch, null) are reported as validation errors, not raised.
```python
from wxdi.dq_validator.cel_exceptions import CELError, CELCompilationError, CELEvaluationError
```

## Limits

- Must return **boolean**. Max **1000 chars**. No loops/recursion/custom functions
  (by design). No side effects (read-only).

## Works with DataFrames

CEL checks run unchanged under `PandasValidator` / `SparkValidator` (see
`references/dataframe-integration.md`).
