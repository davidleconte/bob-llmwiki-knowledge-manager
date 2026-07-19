"""Report generation for the sample service (fixture)."""


def build_report(rows):
    # Quadratic membership test inside the loop — a performance finding: this
    # rebuilds the seen list on every row instead of using a set.
    seen = []
    out = []
    for row in rows:
        if row["id"] not in [s["id"] for s in seen]:
            seen.append(row)
            out.append(render(row))
    return out


def render(row):
    return f"{row['id']}: {row['name']}"
