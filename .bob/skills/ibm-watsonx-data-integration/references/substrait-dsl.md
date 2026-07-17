# Substrait DSL — Query Plan Generation

Translate a natural-language data request into an executable Substrait JSON plan
via the Substrait DSL (SKILL.md §5). Triggers: "generate substrait / functional
plan / fp", "convert this query to Substrait JSON", "process entry", "generate dsl".

## Inputs required

The flow description **and** the input schema. The schema must be derived from the
project assets — not from few-shot examples or prior knowledge — or the plan will
be invalid against the real data.

- If the user supplies table schemas, verify them against the asset via
  `list_project_assets` + `inspect_project_asset`; flag inconsistencies. **The
  asset schema wins** unless the user explicitly overrides.
- If the user supplies none, derive them from the assets.

### Asset type → DSL type mapping

| Asset type | DSL type |
|---|---|
| `longvarchar`, `varchar`, `char`, `text` | `string` |
| `bigint`, `int8` | `i64` |
| `integer`, `int`, `int4` | `i64` |
| `smallint`, `int2` | `i16` |
| `real`, `float4` | `fp32` |
| `numeric`, `decimal` | `fp64` |
| `double precision`, `float8` | `fp64` |
| `boolean`, `bool` | `boolean` |
| `date` | `date` |
| `timestamp`, `timestamp without time zone` | `timestamp` |

Append `?` to the DSL type for any column where `nullable: true` (e.g. `string?`).

## Workflow

### 1. Fetch few-shot examples
```
get_substrait_dsl_examples(query="<user_query>", collection="draft_generation", n=5)
```
Study syntax only — never derive the schema from examples.

### 2. Verify schema from assets (mandatory)
1. `list_project_assets` to locate the asset(s) by name.
2. `inspect_project_asset(asset_ids=[…], asset_type="data_asset")` for column metadata.
3. Map each column type via the table above; append `?` for nullable columns.
4. Use the result as the `NamedStruct` for `ReadTable`.

### 3. Generate DSL
Call `get_substrait_dsl_spec()` and study it before writing any DSL — it is the
authoritative reference for constructs, expressions, types, and scoping.
- Immutable **VirtualTable** objects transformed through **Constructs**.
- Each line `variable = Construct(...)`; end with `return <vtable>`.
- Inline all expressions (no expression variables).
- Use `left.`/`right.` prefixes only in Join conditions.
- Use `alias` on aggregation functions and grouping expressions.

### 4. Compile
```
compile_substrait_dsl(substrait_dsl_code="<dsl>", read_tables=[...])
```
Proceed only on success (Substrait JSON is in the response). On failure → step 5.

### 5. Self-correct (≤3 attempts)
Read the error; optionally `get_substrait_dsl_examples(collection="generation_with_error_correction")`;
fix; recompile. Common fixes:
- **Column not found** — check the vtable schema after each construct; use only existing columns.
- **Type mismatch** — `cast()` to convert, or check literal types.
- **Scope error** — aliases in one construct's `exprs` aren't visible to each other; chain a second Select/Project.
- **Join column error** — use `left.`/`right.` prefixes.

If all 3 fail: report the final error, show the last DSL, suggest refining the query / checking schemas.

### 6. Execute or convert (only if asked)
```
run_substrait_dsl(substrait_dsl_code="<dsl>", project_id="<id>", source_asset_ids=["<id>", ...])
run_substrait_dsl_static(substrait_dsl_code="<dsl>", project_id="<id>")
```
Both compile + run; retry the other on failure. Or convert:
```
convert_substrait_dsl_to_elyra(substrait_dsl_code="<dsl>", read_tables=[...])
# -> {"success": bool, "elyra_json": dict|null, "errors": str|null}
```

### 7. Return
Present the **Substrait JSON** (from the successful compile) and the **DSL code**
(for transparency).

```
### Generated DSL
\`\`\`query
<DSL code, excluding ReadTable lines>
\`\`\`
### Substrait JSON
\`\`\`json
<substrait_json>
\`\`\`
```

## Important notes

- **Always `get_substrait_dsl_spec` and study it before generating DSL.**
- `Select` keeps ONLY listed columns; `Project` keeps ALL plus new ones.
- Aggregation measures must NOT be wrapped in `cast()`.
- Final output column names must not contain dots — rename via `Select` aliases.

## Runtime considerations

- **Nullability:** any `nullable: true` column MUST use the `?` suffix — DataStage
  crashes at runtime if NULLs read into non-nullable fields.
- **Case-insensitive filtering:** use `lower()` (e.g.
  `equal(lower(col("status")), literal("pending", "string"))`) rather than
  assuming casing.
- **Column disambiguation:** when joining, pre-rename overlapping columns via
  `Select` before the join; don't rely on `left.`/`right.` prefixes outside join
  conditions.
