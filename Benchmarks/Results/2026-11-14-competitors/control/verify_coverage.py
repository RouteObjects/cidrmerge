#!/usr/bin/env python3
"""Independently verify exact coverage and minimal CIDR cardinality.

Usage: verify_coverage.py FIXTURE_DIR OUTPUT_PATH [OUTPUT_PATH ...] --receipt PATH
Python's standard-library ipaddress parser supplies numeric intervals. Sorting,
coalescing, interval hashing, and minimal-cover counting are independent of every
program being benchmarked. No benchmark executable is imported or invoked.
"""

import argparse
import datetime
import hashlib
import ipaddress
import json
from pathlib import Path


FAMILY_LABELS = {4: "ipv4", 6: "ipv6"}
SERIALIZATION = "concatenated records: family uint8 (4 or 6), start uint128 big-endian, end uint128 big-endian; IPv4 records first, sorted/coalesced per family"


def sha256_file(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def parse_network_files(paths, require_slash=False):
    """Reject malformed nonempty lines and CIDRs with host bits set."""
    intervals = {4: [], 6: []}
    counts = {"ipv4": 0, "ipv6": 0}
    files = []
    for supplied_path in paths:
        path = Path(supplied_path)
        record = {"path": str(path), "bytes": path.stat().st_size, "line_count": 0, "blank_lines": 0}
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for line_number, raw in enumerate(source, 1):
                digest.update(raw)
                try:
                    text = raw.decode("ascii").strip()
                    if not text:
                        record["blank_lines"] += 1
                        continue
                    if "%" in text or (require_slash and "/" not in text):
                        raise ValueError("expected an unscoped canonical CIDR")
                    network = ipaddress.ip_network(text, strict=True)
                except (UnicodeError, ValueError) as error:
                    raise ValueError(f"{path}:{line_number}: invalid network record: {error}") from error
                family = network.version
                intervals[family].append((int(network.network_address), int(network.broadcast_address)))
                counts[FAMILY_LABELS[family]] += 1
                record["line_count"] += 1
        record["sha256"] = digest.hexdigest()
        files.append(record)
    return intervals, counts, files


def coalesce(intervals):
    intervals.sort()
    merged = []
    for lower, upper in intervals:
        if merged and lower <= merged[-1][1] + 1:
            if upper > merged[-1][1]:
                merged[-1] = (merged[-1][0], upper)
        else:
            merged.append((lower, upper))
    return merged


def minimal_cidr_count(lower, upper, bit_width):
    """Greedy power-of-two decomposition using Python unbounded integers."""
    blocks = 0
    while lower <= upper:
        alignment = bit_width if lower == 0 else (lower & -lower).bit_length() - 1
        remaining_shift = (upper - lower + 1).bit_length() - 1
        lower += 1 << min(alignment, remaining_shift)
        blocks += 1
    return blocks


def coverage_summary(intervals, counts):
    digest = hashlib.sha256()
    ranges = {}
    blocks = {}
    addresses = {}
    for family in (4, 6):
        label = FAMILY_LABELS[family]
        merged = coalesce(intervals[family])
        ranges[label] = len(merged)
        blocks[label] = 0
        covered = 0
        for lower, upper in merged:
            digest.update(bytes([family]))
            digest.update(lower.to_bytes(16, "big"))
            digest.update(upper.to_bytes(16, "big"))
            covered += upper - lower + 1
            blocks[label] += minimal_cidr_count(lower, upper, 32 if family == 4 else 128)
        addresses[label] = str(covered)
    return {
        "input_count": sum(counts.values()),
        "family_counts": counts,
        "coverage_sha256": digest.hexdigest(),
        "coverage_serialization": SERIALIZATION,
        "range_count": sum(ranges.values()),
        "range_count_by_family": ranges,
        "minimal_cidr_count": sum(blocks.values()),
        "minimal_cidr_count_by_family": blocks,
        "addresses_covered": addresses,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("outputs", type=Path, nargs="+")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.receipt.exists():
        raise SystemExit(f"Refusing to overwrite receipt: {args.receipt}")
    receipt = {"passed": False, "fixture": str(args.fixture), "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        expected_path = args.fixture / "expected.json"
        expected = json.loads(expected_path.read_text())
        manifest = json.loads((args.fixture / "manifest.json").read_text())
        receipt["expected_sha256"] = sha256_file(expected_path)
        actual_input_hash = sha256_file(args.fixture / "input.txt")
        if actual_input_hash != expected["input_file_sha256"] or actual_input_hash != manifest["files"]["input.txt"]["sha256"]:
            raise ValueError("Fixture input bytes changed after oracle generation")
        intervals, counts, output_files = parse_network_files(args.outputs)
        actual = coverage_summary(intervals, counts)
        receipt["output_files"] = output_files
        receipt["actual"] = actual
        receipt["expected_coverage_sha256"] = expected["coverage_sha256"]
        receipt["expected_minimal_cidr_count"] = expected["minimal_cidr_count"]
        if actual["coverage_sha256"] != expected["coverage_sha256"]:
            raise ValueError("Output coverage differs from independently parsed fixture")
        if actual["input_count"] != expected["minimal_cidr_count"]:
            raise ValueError("Output is not a minimum-cardinality CIDR cover")
        for field in ("range_count", "minimal_cidr_count", "addresses_covered"):
            if actual[field] != expected[field]:
                raise ValueError(f"Output oracle field differs: {field}")
        receipt["passed"] = True
    except Exception as error:
        receipt["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        receipt["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with args.receipt.open("x") as destination:
            json.dump(receipt, destination, indent=2)
            destination.write("\n")
    print(json.dumps({"passed": True, "fixture": args.fixture.name, "output_count": actual["input_count"], "coverage_sha256": actual["coverage_sha256"], "receipt": str(args.receipt)}))


if __name__ == "__main__":
    main()
