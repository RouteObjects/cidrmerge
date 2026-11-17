#!/usr/bin/env python3
"""Verify preserved audit arithmetic, then render the complete B/P experiment.

This script never runs the product, builds, tests, or new measurements. A partial
--validate-only check is permitted; rendering always requires all three platforms.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import traceback

PLATFORMS = {"macos": "macOS ARM64", "arm64": "Linux ARM64", "x86_64": "Linux x86-64"}
METRICS = {"elapsed": "elapsed_seconds", "cpu": "cpu_seconds", "rss": "rss_bytes"}
KINDS = {"throughput": "Million-entry file input", "stdin": "Million-entry redirected text stdin"}
CHECKS = 0


def check(condition, detail):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(detail)


def equal(actual, expected, detail):
    if actual is None or expected is None:
        check(actual is expected, (detail, actual, expected))
    elif isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        check(len(actual) == len(expected), (detail, actual, expected))
        for index, (left, right) in enumerate(zip(actual, expected)):
            equal(left, right, (detail, index))
    elif isinstance(actual, (float, int)) and isinstance(expected, (float, int)):
        check(math.isfinite(actual) and math.isfinite(expected)
              and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-10),
              (detail, actual, expected))
    else:
        check(actual == expected, (detail, actual, expected))


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def row_key(row):
    return tuple(row[key] for key in ("platform", "kind", "profile", "comparison", "phase", "case"))


def median(values):
    return statistics.median(values) if values else None


def extremes(values):
    return [min(values), max(values)] if values else None


def load_dataset(root, platforms):
    fingerprints = {}
    audits = {}
    summaries = []
    pair_rows = []
    platform_counts = {}
    phase_rows = []

    def read_json(relative):
        path = root / relative
        data = json.loads(path.read_text())
        fingerprints[relative] = sha(path)
        return data

    case_order = {}
    for kind, filename in [("throughput", "cases.json"), ("stdin", "stdin-cases.json")]:
        case_order[kind] = [case["id"] for case in read_json("control/" + filename)["configs"]]
    check(len(case_order["throughput"]) == 8 and len(case_order["stdin"]) == 2, "focused case inventory")
    seen_rows = set()
    seen_pairs = set()

    for platform in platforms:
        review = read_json(f"analysis/{platform}-measurement-review.json")
        check(review["passed"] is True, (platform, "review did not pass"))
        check(review["row_count"] == len(review["rows"]), (platform, "review row count"))
        platform_summaries = []
        phase_cases = collections.defaultdict(set)
        phase_counts = {}
        review_phase_totals = {phase: {"measured_samples": 0, "warmups": 0} for phase in ("primary", "followup")}
        for row in review["rows"]:
            fields = {key: row[key] for key in ("kind", "profile", "comparison", "phase", "case")}
            fields.update(platform=platform, B_variant="B", P_variant="P", audit_receipt=row["audit_receipt"])
            key = row_key(fields)
            check(key not in seen_rows, ("duplicate summary", key))
            seen_rows.add(key)
            check(row["profile"] == "ordinary" and row["comparison"] == "B-vs-P", ("unexpected profile/variants", key))
            check(row["kind"] in KINDS and row["phase"] in ("primary", "followup"), ("unexpected group", key))
            receipt = row["audit_receipt"]
            if receipt not in audits:
                audit = read_json(receipt)
                check(audit["passed"] is True and audit["result"]["passed"] is True, (receipt, "audit did not pass"))
                audits[receipt] = audit["result"]
            result = audits[receipt]
            check(result["role_mapping"] == {"B": "B", "C": "P"}, (receipt, "variant roles"))
            check(result["comparison"] == row["comparison"] and result["artifact_profile"] == row["profile"] and result["phase"] == row["phase"], (receipt, "phase identity"))
            check(result["startup"] is False, (receipt, "ordinary throughput-only identity"))
            check(row["case"] in result["configs"], (receipt, "unknown case", row["case"]))
            phase_cases[receipt].add(row["case"])
            if receipt not in phase_counts:
                phase_counts[receipt] = {"kind": row["kind"], "profile": row["profile"], "comparison": row["comparison"], "phase": row["phase"], "receipt": receipt, "measured_samples": result["measured_samples"], "warmups": result["warmups"], "case_count": len(result["configs"]), "rounds": result["rounds"]}
                for name in ("measured_samples", "warmups"):
                    review_phase_totals[row["phase"]][name] += result[name]
            source = result["recomputed"][row["case"]]
            pairs = source["pairs"]
            expected_n = 6
            check(len(pairs) == row["n"] == result["rounds"] == expected_n, (key, "pair count"))
            check(sorted(pair["round"] for pair in pairs) == list(range(1, expected_n + 1)), (key, "round inventory"))
            values = {f"{role}_{metric}": [] for role in ("B", "P") for metric in METRICS.values()}
            changes = {metric: [] for metric in METRICS}
            for pair in pairs:
                pair_key = key + (pair["round"],)
                check(pair_key not in seen_pairs, ("duplicate pair", pair_key))
                seen_pairs.add(pair_key)
                output_pair = dict(fields, round=pair["round"])
                for role, source_role in [("B", "B"), ("P", "C")]:
                    observation = pair[source_role]
                    converted = {"elapsed_seconds": observation["elapsed_ns"] / 1e9, "cpu_seconds": observation["cpu_seconds"], "rss_bytes": observation["peak_rss_bytes"]}
                    for metric, value in converted.items():
                        check(math.isfinite(value) and value >= 0, (pair_key, role, metric, "invalid observation"))
                        values[f"{role}_{metric}"].append(value)
                        output_pair[f"{role}_{metric}"] = value
                for metric, source_metric in [("elapsed", "elapsed_ns"), ("cpu", "cpu_seconds"), ("rss", "peak_rss_bytes")]:
                    baseline = pair["B"][source_metric]
                    change = 100 * (pair["C"][source_metric] / baseline - 1) if baseline else None
                    equal(change, pair[f"{metric}_change_pct"], (pair_key, metric, "audit pair change"))
                    output_pair[f"{metric}_change_pct"] = change
                    if change is not None:
                        changes[metric].append(change)
                pair_rows.append(output_pair)
            summary = dict(fields, n=expected_n)
            for name, observations in values.items():
                for statistic, function in [("median", statistics.median), ("min", min), ("max", max)]:
                    summary[f"{name}_{statistic}"] = function(observations)
                role, metric = name.split("_", 1)
                reviewer_metric = "peak_rss_bytes" if metric == "rss_bytes" else metric
                equal(summary[f"{name}_median"], row["absolute_medians"][role][reviewer_metric], (key, role, metric, "reviewer absolute median"))
            for metric, observations in changes.items():
                mid = median(observations)
                limits = extremes(observations)
                equal(mid, row["paired_change_medians"][metric], (key, metric, "reviewer paired median"))
                equal(limits, row["paired_change_ranges"][metric], (key, metric, "reviewer paired range"))
                equal(mid, source["paired_change_medians"][metric], (key, metric, "audit paired median"))
                equal(limits, source["paired_change_ranges"][metric], (key, metric, "audit paired range"))
                summary[f"{metric}_change_pct_median"] = mid
                summary[f"{metric}_change_pct_min"] = limits[0] if limits else None
                summary[f"{metric}_change_pct_max"] = limits[1] if limits else None
                summary[f"{metric}_change_n"] = len(observations)
            equal(all(value < 0 for value in changes["elapsed"]), row["all_elapsed_pairs_improved"], (key, "all-pairs-improved flag"))
            for metric in ("elapsed", "rss"):
                equal(sum(value > 5 for value in changes[metric]), row[f"{metric}_pairs_above_5_percent"], (key, metric, "trigger count"))
            summaries.append(summary)
            platform_summaries.append(summary)

        for receipt, cases in phase_cases.items():
            result = audits[receipt]
            check(cases == set(result["configs"]) == set(result["recomputed"]), (receipt, "complete case inventory"))
            check(result["measured_samples"] == 2 * result["rounds"] * len(cases), (receipt, "measured count"))
            check(result["warmups"] == 2 * len(cases), (receipt, "warmup count"))
        for kind, expected_cases in case_order.items():
            primary = [item for item in platform_summaries if item["kind"] == kind and item["phase"] == "primary"]
            check({item["case"] for item in primary} == set(expected_cases), (platform, kind, "primary case inventory"))
            followups = [item for item in platform_summaries if item["kind"] == kind and item["phase"] == "followup"]
            triggered = {item["case"] for item in primary if item["elapsed_change_pct_max"] > 5 or item["rss_change_pct_max"] > 5}
            check({item["case"] for item in followups} == triggered, (platform, kind, "fixed follow-up inventory"))
        equal(dict(review_phase_totals), review["totals"], (platform, "review phase totals"))
        equal(review_phase_totals["primary"], {"measured_samples": 120, "warmups": 20}, (platform, "focused primary totals"))
        count = {"phases": len(phase_counts), "measured_samples": sum(item["measured_samples"] for item in phase_counts.values()), "warmups": sum(item["warmups"] for item in phase_counts.values()), "case_summaries": len(platform_summaries), "pairs": sum(item["n"] for item in platform_summaries)}
        equal(count["phases"], review["audits"], (platform, "audit count"))
        equal(count["measured_samples"], review["measured_samples"], (platform, "sample count"))
        equal(count["warmups"], review["warmups"], (platform, "warmup count"))
        check(count["measured_samples"] == count["pairs"] * 2, (platform, "pair/sample count"))
        text = [item for item in platform_summaries if item["kind"] == "throughput" and item["phase"] == "primary" and item["case"].startswith("text-")]
        check(len(text) == 8, (platform, "text primary count"))
        for metric in ("elapsed", "rss"):
            equal(extremes([item[f"{metric}_change_pct_median"] for item in text]), review[f"text_primary_{metric}_median_range_percent"], (platform, metric, "review headline range"))
        platform_counts[platform] = count
        phase_rows.extend(dict(item, platform=platform) for item in phase_counts.values())
    summaries.sort(key=row_key)
    pair_rows.sort(key=lambda row: row_key(row) + (row["round"],))
    return {"schema_version": 1, "created_at": now(), "passed": True, "scope": "Existing independently passed audit metadata for indexed Data.span versus withUnsafeBytes; primary and follow-up remain separate. No new product execution, measurements, or observation exclusion.", "platforms": platforms, "complete_platform_set": platforms == list(PLATFORMS), "units": {"elapsed_seconds": "seconds", "cpu_seconds": "seconds", "rss_bytes": "bytes", "change_pct": "100 * (P / B - 1)"}, "statistics": "Absolute medians/minima/maxima use each role's observations. Paired percentage statistics use each matched pair; the ratio of absolute medians can differ.", "zero_baseline_cpu_policy": "Zero baseline CPU gives a null percentage; all absolute observations remain included, and valid change counts are explicit.", "input_sha256": fingerprints, "case_order": case_order, "counts": platform_counts, "audit_rows": phase_rows, "totals": {name: sum(count[name] for count in platform_counts.values()) for name in ["phases", "measured_samples", "warmups", "case_summaries", "pairs"]}, "summaries": summaries, "pairs": pair_rows, "arithmetic_checks": CHECKS}


def percent(value):
    return "n/a" if value is None else f"{value:+.2f}%"


def paired(row, metric):
    if row[f"{metric}_change_pct_median"] is None:
        return "n/a"
    return f"{percent(row[metric+'_change_pct_median'])} [{percent(row[metric+'_change_pct_min'])}, {percent(row[metric+'_change_pct_max'])}]"


def ordered_rows(dataset, platform, kind):
    cases = dataset["case_order"][kind]
    return sorted([row for row in dataset["summaries"] if row["platform"] == platform and row["kind"] == kind], key=lambda row: (cases.index(row["case"]), row["phase"] != "primary"))


def render_tables(dataset, output):
    lines = ["# Complete matched measurements", "", "All values compare ordinary Release P with the frozen baseline B. Negative paired change means lower elapsed time, CPU time, or peak RSS. Brackets show the full observed minimum and maximum, not confidence intervals. Absolute medians and paired percentage medians are different statistics; no phase is pooled and no observation is excluded.", "", "Each file/stdin row has six pairs. Warmups are excluded. `Valid change pairs` can be smaller only when a zero baseline CPU observation makes a percentage undefined. All absolute CPU observations remain included. Audit receipt paths in the CSVs are relative to the preserved experiment root.", ""]
    for platform, title in PLATFORMS.items():
        lines.extend([f"## {title}", ""])
        for kind, heading in KINDS.items():
            rows = ordered_rows(dataset, platform, kind)
            lines.extend([f"### {heading}", ""])
            for metric, absolute in METRICS.items():
                unit = "MiB" if metric == "rss" else "s"
                scale = 1 / 2**20 if metric == "rss" else 1
                places = 3 if unit != "s" else 6
                title_metric = {"elapsed": "Elapsed time", "cpu": "CPU time", "rss": "Peak RSS"}[metric]
                lines.extend([f"**{title_metric} ({unit})**", "", "| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |", "|---|---:|---:|---:|---:|---:|"])
                for row in rows:
                    def absolute_cell(role):
                        values = [row[f"{role}_{absolute}_{stat}"] * scale for stat in ["median", "min", "max"]]
                        return f"{values[0]:.{places}f} [{values[1]:.{places}f}, {values[2]:.{places}f}]"
                    lines.append(f"| {row['case']} / {row['phase']} | {row['n']} | {absolute_cell('B')} | {absolute_cell('P')} | {paired(row,metric)} | {row[metric+'_change_n']} |")
                lines.append("")
    lines.extend(["Mac CPU observations have 0.01-second accounting resolution. Linux lifetime peak RSS uses wait4; it is an end-to-end process measurement, not a heap allocation count. This focused experiment has no startup or cold-cache timing groups.", ""])
    (output / "MEASUREMENTS.md").write_text("\n".join(lines))


def render_regressions(dataset, output):
    summaries = dataset["summaries"]
    index = {row_key(row): row for row in summaries}
    registry = []
    large_observations = []
    lines = ["# Regression observations and fixed follow-ups", "", "The predeclared trigger is any **primary** paired elapsed-time or peak-RSS increase above 5%, not only a median increase. Each affected configuration receives one separate fixed-size follow-up: six pairs for file/stdin. Follow-ups do not recursively trigger a third phase. No observation is discarded or pooled; all pairs, including unusually large positive and negative observations, remain in `pairs.csv`.", "", "The repetition labels below describe primary/follow-up medians and are not significance tests. CPU values are retained in the complete measurements and CSVs, but CPU percentage was not the follow-up trigger.", ""]
    for platform, title in PLATFORMS.items():
        lines.extend([f"## {title}", "", "| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |", "|---|---|---|---:|---:|---|"])
        for primary in [row for row in summaries if row["platform"] == platform and row["phase"] == "primary"]:
            followup = index.get(row_key(dict(primary, phase="followup")))
            for metric in ("elapsed", "rss"):
                primary_trigger = primary[metric + "_change_pct_max"] > 5
                followup_trigger = followup is not None and followup[metric + "_change_pct_max"] > 5
                if not primary_trigger and not followup_trigger:
                    continue
                check(followup is not None, (row_key(primary), metric, "missing follow-up"))
                first = primary[metric + "_change_pct_median"]
                second = followup[metric + "_change_pct_median"]
                if not primary_trigger:
                    interpretation = "First >5% observation in follow-up; no third phase"
                elif first > 5 and second > 5:
                    interpretation = "Both phase medians >5%"
                elif first > 5 or second > 5:
                    interpretation = "Not repeated above 5%; phases differ"
                elif first > 0 and second > 0:
                    interpretation = "Small positive medians; inspect absolute size and spread"
                else:
                    interpretation = "No repeated positive median regression"
                item = {key: primary[key] for key in ["platform", "kind", "profile", "comparison", "case"]}
                item.update(metric=metric, primary_trigger=primary_trigger, primary_median_pct=first, followup_median_pct=second, interpretation=interpretation)
                registry.append(item)
                lines.append(f"| {primary['kind']} | {primary['case']} | {metric} | {paired(primary,metric)} | {paired(followup,metric)} | {interpretation} |")
        lines.extend(["", "### Every observed >5% elapsed/RSS increase", "", "This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.", "", "| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |", "|---|---|---:|---|---:|---:|---:|"])
        for pair in [pair for pair in dataset["pairs"] if pair["platform"] == platform]:
            for metric in ("elapsed", "rss"):
                change = pair[metric + "_change_pct"]
                if change <= 5:
                    continue
                item = {key: pair[key] for key in ["platform", "kind", "profile", "comparison", "phase", "case", "round", "audit_receipt"]}
                field = METRICS[metric]
                item.update(metric=metric, B_value=pair["B_" + field], P_value=pair["P_" + field], change_pct=change, units="bytes" if metric == "rss" else "seconds")
                large_observations.append(item)
                scale = 1 / 2**20 if metric == "rss" else 1
                unit = "MiB" if metric == "rss" else "s"
                lines.append(f"| {pair['kind']} / {pair['phase']} | {pair['case']} | {pair['round']} | {metric} | {pair['B_'+field]*scale:.6f} {unit} | {pair['P_'+field]*scale:.6f} {unit} | {percent(change)} |")
        lines.append("")
    (output / "REGRESSIONS.md").write_text("\n".join(lines))
    save_json(output / "regression-observations.json", {"phase_comparisons": registry, "individual_elapsed_or_rss_increases_over5_percent": large_observations, "all_pairs_retained": True})
    return registry, large_observations


def render_charts(dataset, output, root):
    cache = root / "analysis/plot-cache"
    cache.mkdir(exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(cache)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cases = [case for case in dataset["case_order"]["throughput"] if case.startswith("text-")]
    labels = [case.removeprefix("text-").replace("-no-stats", " / no stats").replace("-stats", " / stats") for case in cases]
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    selected = {(row["platform"], row["case"]): row for row in dataset["summaries"] if row["kind"] == "throughput" and row["phase"] == "primary" and row["case"].startswith("text-")}
    for metric, title in [("elapsed", "Elapsed time"), ("rss", "Peak RSS")]:
        figure, axes = plt.subplots(1, 3, figsize=(18, 7.5), sharey=True)
        limits = [0.0]
        for axis, (platform, platform_title) in zip(axes, PLATFORMS.items()):
            for y, case in enumerate(cases):
                row = selected[platform, case]
                low, middle, high = [row[f"{metric}_change_pct_{stat}"] for stat in ["min", "median", "max"]]
                check(low <= middle <= high, (platform, case, metric, "chart interval"))
                limits.extend([low, high])
                axis.errorbar(middle, y, xerr=[[middle - low], [high - middle]], fmt="o", color="#17638c", markersize=5, linewidth=1.3, capsize=3)
            axis.axvline(0, color="#666666", linewidth=1)
            axis.grid(axis="x", color="#dddddd", linewidth=.6)
            axis.set_title(platform_title, pad=12)
            axis.set_xlabel("Paired change (%) — negative is lower")
            axis.set_yticks(range(len(cases)), labels)
        margin = max(.3, (max(limits) - min(limits)) * .06)
        for axis in axes:
            axis.set_xlim(min(limits) - margin, max(limits) + margin)
        axes[0].invert_yaxis()
        figure.suptitle(f"{title}: Data.span (P) vs withUnsafeBytes (B)", fontsize=18, y=.985)
        figure.text(.5, .025, "Primary text workloads · six alternating pairs per configuration\nDots: paired median; whiskers: full observed min–max, not confidence intervals.\nSeparate follow-ups and every observation remain in the tables and CSVs.", ha="center", fontsize=10)
        figure.tight_layout(rect=(0, .10, 1, .95))
        figure.savefig(output / f"text-{metric}.png", dpi=180)
        plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("analysis/report-data-01"))
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--platform", choices=list(PLATFORMS), action="append")
    args = parser.parse_args()
    root = args.root.resolve()
    selected = args.platform or list(PLATFORMS)
    check(len(set(selected)) == len(selected), "duplicate platform")
    selected = [platform for platform in PLATFORMS if platform in selected]
    if not args.validate_only:
        check(selected == list(PLATFORMS), "Rendering requires all three platforms")
    data = load_dataset(root, selected)
    if args.validate_only:
        print(json.dumps({"passed": True, "mode": "validate-only; no files written", "platforms": selected, "checks": CHECKS, "totals": data["totals"]}, indent=2))
        return
    output = args.output if args.output.is_absolute() else root / args.output
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"passed": False, "started_at": now(), "script_sha256": sha(Path(__file__)), "dataset_directory": str(output.relative_to(root)), "platforms": selected}
    try:
        for filename, rows in [("summaries.csv", data["summaries"]), ("pairs.csv", data["pairs"])]:
            with (output / filename).open("x", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        render_tables(data, output)
        registry, observations = render_regressions(data, output)
        render_charts(data, output, root)
        for relative, digest in data["input_sha256"].items():
            check(sha(root / relative) == digest, (relative, "source metadata changed during render"))
        data["arithmetic_checks"] = CHECKS
        save_json(output / "dataset.json", data)
        receipt.update(passed=True, arithmetic_checks=CHECKS, totals=data["totals"], regression_metric_rows=len(registry), observations_over5_percent=len(observations), input_metadata_unchanged=True, artifacts={path.name: {"bytes": path.stat().st_size, "sha256": sha(path)} for path in sorted(output.iterdir()) if path.is_file()})
    except BaseException as error:
        receipt.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        receipt["finished_at"] = now()
        save_json(output / "render.json", receipt)
        print(json.dumps({"passed": receipt["passed"], "output": str(output), "checks": CHECKS, "totals": data["totals"], "error": receipt.get("error")}, indent=2))


if __name__ == "__main__":
    main()
