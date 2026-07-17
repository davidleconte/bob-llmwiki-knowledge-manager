# DataFrame Integration — Pandas & PySpark

Wrap a `Validator` to run over DataFrames (SKILL.md §4). Requires extras:
`pip install "data-intelligence-sdk[pandas]"` and/or `"[spark]"` (or `"[dataframes]"`
for both). Import root `wxdi.dq_validator.integrations`.

Build the `Validator` exactly as for array validation (same metadata + rules),
then wrap it.

## PandasValidator

```python
from wxdi.dq_validator.integrations import PandasValidator
pv = PandasValidator(validator, chunk_size=10000, column_prefix="dq_")
```
Methods:
- `get_summary_statistics(df) -> dict` — aggregated metrics (e.g. `pass_rate`) without materializing per-row results.
- `add_validation_column(df) -> df` — adds the `dq_validation_result` struct column.
- `get_invalid_rows(df) -> df` / `get_valid_rows(df) -> df` — filter.
- `expand_validation_column(df) -> df` — explode the struct into `dq_is_valid`, `dq_score`, `dq_pass_rate`, …

Memory-efficient: chunked (default 10k rows), O(chunk_size) memory — handles
DataFrames larger than RAM.

## SparkValidator

```python
from wxdi.dq_validator.integrations import SparkValidator
sv = SparkValidator(validator, column_prefix="dq_")
```
Methods: `get_summary_statistics(df)`, `add_validation_column(df)`,
`get_invalid_rows(df)` / `get_valid_rows(df)`, `expand_validation_column(df)`,
plus:
- `write_validation_report(df, output_path, format="parquet", mode="overwrite")`
- `get_error_sample(df, limit=100) -> List[dict]`

Distributed via Spark UDFs; O(1) driver memory for aggregations; scales to
billions of rows.

## Result struct column

`dq_validation_result` (prefix configurable) contains:
```python
{
  "is_valid": bool,
  "score": str,            # "5/5"
  "pass_rate": float,      # 0–100
  "total_checks": int,
  "passed_checks": int,
  "failed_checks": int,
  "error_count": int,
  "errors": List[str],
}
```

## Notes

- Same `Validator` works for array, Pandas, and Spark — define metadata/rules once.
- CEL checks work unchanged in both integrations.
- The `column_prefix` (`dq_`) avoids collisions with existing columns; change it if
  your data already uses `dq_`.
