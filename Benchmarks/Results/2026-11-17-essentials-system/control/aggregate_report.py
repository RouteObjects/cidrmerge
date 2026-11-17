#!/usr/bin/env python3
"""Aggregate already-audited benchmark metadata without rerunning or hashing inputs.

Usage:
  python3 control/aggregate_report.py --root EXPERIMENT --output analysis/report-data
  python3 control/aggregate_report.py --root EXPERIMENT --output analysis/partial-01 --allow-partial

The output directory must be new. Primary/follow-up phases, candidate variants,
artifact profiles and platforms are never pooled. Failed attempts are retained in
aggregation.json; original receipts are read-only. This is not a fresh hash audit.
"""

import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path
import statistics
import traceback


PLATFORMS = ("macos", "arm64", "x86_64")
KINDS = ("throughput", "startup", "stdin")
METRICS = {
    "elapsed": ("elapsed_ns", "elapsed_seconds", 1e-9),
    "cpu": ("cpu_seconds", "cpu_seconds", 1),
    "rss": ("peak_rss_bytes", "rss_bytes", 1),
}
IDENTITY = ("platform", "kind", "profile", "comparison", "phase", "case")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def relative_path(root, value):
    path = Path(value)
    require(not path.is_absolute(), "Expected experiment-relative path: " + str(value))
    result = (root / path).resolve()
    require(result.is_relative_to(root), "Path escapes experiment: " + str(value))
    return result


def read_metadata(path):
    before = path.stat()
    require(before.st_size <= 16 * 1024 * 1024, "Unexpectedly large metadata: " + str(path))
    result = json.loads(path.read_text())
    after = path.stat()
    require(
        (before.st_ino, before.st_size, before.st_mtime_ns)
        == (after.st_ino, after.st_size, after.st_mtime_ns),
        "Metadata changed while reading: " + str(path),
    )
    return result


def equivalent(left, right):
    if left is None or right is None:
        return left is None and right is None
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-9)


def finite(value, minimum, label):
    require(type(value) in (float, int) and math.isfinite(value) and value >= minimum, label)


def statistics_for(values):
    return {"median": statistics.median(values), "min": min(values), "max": max(values)}


def aggregate(root, allow_partial):
    dataset = {
        "schema_version": 1,
        "created_at": timestamp(),
        "scope": "Existing audit metadata only; no new hashes, tests, builds or timing. Warmups excluded from values; phases and variants remain separate.",
        "units": {"elapsed_seconds": "seconds", "cpu_seconds": "seconds", "rss_bytes": "bytes", "change_pct": "100 * (C / B - 1)"},
        "absolute_statistics": "Median/min/max of each role's observations, separate from paired percentage medians.",
        "zero_baseline_cpu_policy": "A zero B CPU measurement yields a null percentage delta, excluded from percentage statistics; absolute observations remain included.",
        "allow_partial": allow_partial,
        "expected_platforms": list(PLATFORMS),
        "indices": {},
        "reconciliation": {},
        "summaries": [],
        "pairs": [],
    }
    present = [p for p in PLATFORMS if (root / "analysis" / (p + "-report-index.json")).exists()]
    missing = [p for p in PLATFORMS if p not in present]
    require(present, "No report indices are available")
    require(allow_partial or not missing, "Missing platform indices: " + ", ".join(missing) + "; use --allow-partial explicitly for an interim dataset")
    dataset["platforms"] = present
    dataset["missing_platforms"] = missing
    dataset["complete_platform_set"] = not missing
    for platform in present:
        index_path = "analysis/" + platform + "-report-index.json"
        index = read_metadata(relative_path(root, index_path))
        require(index["platform"] == platform, "Index platform mismatch: " + index_path)
        dataset["indices"][platform] = index_path
        rows = index["audit_rows"]
        require(rows, "Empty audit inventory: " + platform)
        nested = {}
        for kind, profiles in index["passed_audits"].items():
            for profile, comparisons in profiles.items():
                for comparison, phases in comparisons.items():
                    for phase, receipt in phases.items():
                        nested[(kind, profile, comparison, phase)] = receipt
        listed = {}
        for row in rows:
            key = tuple(row[k] for k in ("kind", "profile", "comparison", "phase"))
            require(key not in listed, "Duplicate audit identity: " + repr(key))
            listed[key] = row["receipt"]
        require(listed == nested, "audit_rows and passed_audits disagree: " + platform)
        require(len(set(listed.values())) == len(listed), "Duplicate audit receipt: " + platform)
        totals = {"phases": 0, "measured_samples": 0, "warmups": 0, "case_summaries": 0, "pairs": 0}
        for row in rows:
            kind, profile, comparison, phase = (row[k] for k in ("kind", "profile", "comparison", "phase"))
            require(kind in KINDS, "Unknown benchmark kind: " + kind)
            receipt_path = row["receipt"]
            receipt = read_metadata(relative_path(root, receipt_path))
            result = receipt["result"]
            require(receipt["passed"] is True and result["passed"] is True, "Unpassed audit: " + receipt_path)
            require((result["artifact_profile"], result["comparison"], result["phase"]) == (profile, comparison, phase), "Audit identity mismatch: " + receipt_path)
            require(result["startup"] == (kind == "startup"), "Startup/kind mismatch: " + receipt_path)
            parts = comparison.split("-vs-")
            require(len(parts) == 2 and result["role_mapping"] == dict(zip(("B", "C"), parts)), "Role mapping mismatch: " + receipt_path)
            require(set(result["configs"]) == set(result["recomputed"]) and len(result["configs"]) == len(set(result["configs"])), "Case inventory mismatch: " + receipt_path)
            rounds = result["rounds"]
            require(type(rounds) is int and rounds > 0, "Invalid rounds: " + receipt_path)
            expected_samples = len(result["configs"]) * rounds * 2
            expected_warmups = len(result["configs"]) * 2
            require(row["measured_samples"] == result["measured_samples"] == expected_samples, "Measured count mismatch: " + receipt_path)
            require(row["warmups"] == result["warmups"] == expected_warmups, "Warmup count mismatch: " + receipt_path)
            totals["phases"] += 1
            totals["measured_samples"] += expected_samples
            totals["warmups"] += expected_warmups
            for case in result["configs"]:
                audited = result["recomputed"][case]
                pairs = audited["pairs"]
                require(len(pairs) == rounds and [x["round"] for x in pairs] == list(range(1, rounds + 1)), "Round inventory mismatch: " + case)
                base = dict(zip(IDENTITY, (platform, kind, profile, comparison, phase, case)))
                base.update(B_variant=parts[0], C_variant=parts[1], audit_receipt=receipt_path)
                summary = {**base, "n": rounds}
                for metric, (field, unit_field, scale) in METRICS.items():
                    deltas = []
                    for pair in pairs:
                        for role in ("B", "C"):
                            value = pair[role][field]
                            finite(value, 0 if metric == "cpu" else 1, "Invalid " + field + ": " + case)
                        b, c = pair["B"][field], pair["C"][field]
                        delta = (c / b - 1) * 100 if b else None
                        require(equivalent(delta, pair[metric + "_change_pct"]), "Pair delta mismatch: " + case)
                        if delta is not None:
                            deltas.append(delta)
                    for role in ("B", "C"):
                        absolute = statistics_for([pair[role][field] * scale for pair in pairs])
                        summary.update({role + "_" + unit_field + "_" + stat: value for stat, value in absolute.items()})
                    delta_stats = statistics_for(deltas) if deltas else dict.fromkeys(("median", "min", "max"))
                    summary.update({metric + "_change_pct_" + stat: value for stat, value in delta_stats.items()})
                    summary[metric + "_change_n"] = len(deltas)
                    require(equivalent(delta_stats["median"], audited["paired_change_medians"][metric]), "Median mismatch: " + case)
                    expected_range = audited["paired_change_ranges"][metric]
                    require((expected_range is None and not deltas) or (expected_range is not None and len(expected_range) == 2 and equivalent(delta_stats["min"], expected_range[0]) and equivalent(delta_stats["max"], expected_range[1])), "Range mismatch: " + case)
                dataset["summaries"].append(summary)
                totals["case_summaries"] += 1
                for pair in pairs:
                    output = {**base, "round": pair["round"], "n": 1}
                    for metric, (field, unit_field, scale) in METRICS.items():
                        for role in ("B", "C"):
                            output[role + "_" + unit_field] = pair[role][field] * scale
                        output[metric + "_change_pct"] = pair[metric + "_change_pct"]
                    dataset["pairs"].append(output)
                    totals["pairs"] += 1
        require({k: totals[k] for k in ("phases", "measured_samples", "warmups")} == index["audit_totals"], "Index totals disagree: " + platform)
        require(totals["pairs"] * 2 == totals["measured_samples"], "Pair/sample reconciliation failed: " + platform)
        dataset["reconciliation"][platform] = {"passed": True, **totals}
    for table in ("summaries", "pairs"):
        dataset[table].sort(key=lambda row: tuple(str(row[k]) for k in IDENTITY) + (row.get("round", 0),))
    dataset["totals"] = {k: sum(v[k] for v in dataset["reconciliation"].values()) for k in ("phases", "measured_samples", "warmups", "case_summaries", "pairs")}
    dataset["passed"] = True
    return dataset


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory; relative paths resolve under --root")
    parser.add_argument("--allow-partial", action="store_true", help="Explicitly permit missing platform indices in an interim dataset")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve() if args.output.is_absolute() else relative_path(root, args.output)
    require(output.is_relative_to(root), "Output must remain under experiment root")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"passed": False, "started_at": timestamp(), "allow_partial": args.allow_partial}
    try:
        dataset = aggregate(root, args.allow_partial)
        write_json(output / "dataset.json", dataset)
        for table in ("summaries", "pairs"):
            rows = dataset[table]
            with (output / (table + ".csv")).open("x", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        receipt.update(passed=True, complete_platform_set=dataset["complete_platform_set"], platforms=dataset["platforms"], missing_platforms=dataset["missing_platforms"], totals=dataset["totals"], reconciliation=dataset["reconciliation"])
    except Exception as error:
        receipt.update(error=repr(error), traceback=traceback.format_exc())
    receipt["finished_at"] = timestamp()
    write_json(output / "aggregation.json", receipt)
    print(json.dumps({k: v for k, v in receipt.items() if k != "traceback"}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
