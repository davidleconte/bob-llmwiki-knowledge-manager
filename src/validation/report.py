"""Assemble and serialize the validation report.

The report keeps the three savings mechanisms in **separate, labelled** sections
and elevates only optimizer compression to the headline. It embeds the
reproducibility manifest and refuses to print "VALIDATED" -- it prints measured
numbers with their provenance and lets the reader judge.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

SCHEMA_VERSION = "bob-validation/v1"


def build_report(
    manifest: Dict[str, Any],
    optimizer: Dict[str, Any],
    cache: Dict[str, Any],
    truncation: Dict[str, Any],
    null_test: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble the machine-readable report with a single, honest headline."""
    return {
        "schema": SCHEMA_VERSION,
        "manifest": manifest,
        "headline": {
            "metric": "optimizer_compression_mean_savings_pct",
            "value": optimizer["mean_savings_pct"],
            "ci95": optimizer["ci95_savings_pct"],
            "n": optimizer["n"],
            "tiktoken_active": optimizer["tiktoken_active"],
            "caveat": (
                "lossless-ish prompt compression on real prose; cache "
                "recompute-avoidance and lossy truncation are reported "
                "separately and are NOT part of this headline"
            ),
        },
        "optimizer_compression": optimizer,
        "cache_recompute_avoidance": cache,
        "truncation_budget_fit": truncation,
        "null_test": null_test,
    }


def write_report(
    out_dir: Path, report: Dict[str, Any], manifest: Dict[str, Any]
) -> Tuple[Path, Path]:
    """Write ``report.json`` and a sibling ``manifest.json``; return both paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    manifest_path = out_dir / "manifest.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return report_path, manifest_path


def human_summary(report: Dict[str, Any]) -> str:
    """Render a plain-text summary that leads with N and provenance."""
    manifest = report["manifest"]
    headline = report["headline"]
    optimizer = report["optimizer_compression"]
    cache = report["cache_recompute_avoidance"]
    truncation = report["truncation_budget_fit"]
    null_test = report["null_test"]

    ci = headline["ci95"]
    lines = [
        "Token-optimization validation (measured, manifest-backed)",
        "=" * 58,
        f"corpus documents (N):     {headline['n']}",
        f"tiktoken active:          {headline['tiktoken_active']}",
        f"code SHA:                 {manifest['code_sha']}  (dirty={manifest['git_dirty']})",
        f"data hash:                {manifest['data_hash'][:16]}...",
        f"seed:                     {manifest['seed']}",
        "",
        "HEADLINE -- optimizer compression (lossless-ish, real prose):",
        f"  mean savings:           {headline['value']:.2f}%  "
        f"(95% CI [{ci[0]:.2f}%, {ci[1]:.2f}%], bootstrap)",
        f"  median / std:           {optimizer['median_savings_pct']:.2f}% / "
        f"{optimizer['std_savings_pct']:.2f}%",
        f"  aggregate (token-wtd):  {optimizer['aggregate_savings_pct']:.2f}%",
        f"  mean quality score:     {optimizer['mean_quality_score']:.3f}  "
        f"({optimizer['quality_note']})",
        f"  latency mean / p95:     {optimizer['mean_latency_ms']:.2f}ms / "
        f"{optimizer['p95_latency_ms']:.2f}ms",
        "",
        "SEPARATE -- cache recompute-avoidance (workload-dependent):",
        f"  repeat fraction (real): {cache['actual_repeat_fraction']:.2f}  "
        f"(requested {cache['requested_repeat_rate']:.2f})",
        f"  hit rate:               {cache['hit_rate_pct']:.2f}%  "
        f"(tracks the repeat fraction; NOT part of the headline)",
        "",
        "SEPARATE -- truncation budget-fit (LOSSY, excluded from savings):",
        f"  budget:                 {truncation['budget_tokens']} tokens",
        f"  docs truncated:         {truncation['documents_truncated']}/{truncation['documents']}",
        f"  mean removal when cut:  {truncation['mean_removal_pct_when_truncated']:.2f}%  "
        f"(deletion, no fidelity guarantee)",
        "",
        "NULL TEST -- optimizer on shuffled/high-entropy corpus:",
        f"  mean savings:           {null_test['mean_savings_pct']:.2f}%  "
        f"(threshold < {null_test['threshold_pct']:.1f}%)",
        f"  result:                 {'PASS' if null_test['passed'] else 'FAIL'}",
        "",
        "This report publishes measured numbers with provenance, not a verdict.",
    ]
    return "\n".join(lines)
