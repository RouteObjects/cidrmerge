#!/usr/bin/env python3
"""Generate eight matched million-record CIDR inputs and independent oracles.

All generated files remain beneath ROOT/fixtures. Existing fixture directories
are never replaced. Run from any directory; ROOT defaults to this file's parent
directory's parent. Each expected cover is computed by reparsing input.txt with
Python's ipaddress implementation, never by a benchmarked executable.
"""

import argparse
import datetime
import hashlib
import ipaddress
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from verify_coverage import coverage_summary, minimal_cidr_count, parse_network_files, sha256_file


COUNT = 1_000_000
V6_BASE = int(ipaddress.IPv6Address("2001:db8::"))
V4_PRIVATE = int(ipaddress.IPv4Address("10.0.0.0"))
CASES = (
    "ipv4-disjoint", "ipv6-disjoint", "mixed-disjoint", "mixed-permuted",
    "mixed-overlap", "mixed-adjacent", "bgp-like-ipv4", "range-derived-mixed",
)
RECIPES = {
    "ipv4-disjoint": "index*2 as IPv4 /32 for index 0..<1,000,000; matches the repository disjoint corpus",
    "ipv6-disjoint": "2001:db8:: + index*2 as IPv6 /128 for index 0..<1,000,000",
    "mixed-disjoint": "exact repository mixed corpus: even index -> IPv4 index*2 /32; odd index -> 2001:db8:(index>>16):(index&65535)::/64",
    "mixed-permuted": "same records as mixed-disjoint, emitted in index j=(i*104729+7919)%1,000,000 order; multiplier coprime to count",
    "mixed-overlap": "alternate families; every 64th family ordinal emits parent 10.0.0.0/8 or 2001:db8::/32; other records are canonical contained /16,/24,/32 or /48,/64,/128 networks",
    "mixed-adjacent": "alternate 500,000 consecutive IPv4 /32 hosts beginning at 0.0.0.0 and 500,000 consecutive IPv6 /128 hosts beginning at 2001:db8::",
    "bgp-like-ipv4": "exact repository bgp-like PRNG and prefix-length distribution; synthetic, not a routing-table snapshot",
    "range-derived-mixed": "500,000 disjoint six-address intervals alternate family; lower=ordinal*16 (plus 2001:db8:: for IPv6); decompose each into /30+/31 or /126+/127 before benchmarking, yielding 1,000,000 common CIDR records",
}


def ipv4(value):
    return f"{(value >> 24) & 255}.{(value >> 16) & 255}.{(value >> 8) & 255}.{value & 255}"


def mixed_record(index):
    if index % 2 == 0:
        return 4, f"{ipv4(index * 2)}/32"
    return 6, f"2001:db8:{index >> 16:x}:{index & 65535:x}::/64"


def records(name):
    state = 0xC1D2_4E20_2607_11
    lengths = (24, 24, 24, 24, 23, 22, 21, 20, 19, 18, 16, 25, 26, 27, 32)
    for index in range(COUNT):
        if name == "ipv4-disjoint":
            yield 4, f"{ipv4(index * 2)}/32"
        elif name == "ipv6-disjoint":
            yield 6, f"{ipaddress.IPv6Address(V6_BASE + index * 2)}/128"
        elif name == "mixed-disjoint":
            yield mixed_record(index)
        elif name == "mixed-permuted":
            yield mixed_record((index * 104729 + 7919) % COUNT)
        elif name == "mixed-overlap":
            ordinal = index // 2
            if index % 2 == 0:
                if ordinal % 64 == 0:
                    yield 4, "10.0.0.0/8"
                elif ordinal % 3 == 0:
                    yield 4, f"{ipv4(V4_PRIVATE + ((ordinal & 65535) << 8))}/24"
                elif ordinal % 3 == 1:
                    yield 4, f"{ipv4(V4_PRIVATE + ((ordinal & 255) << 16))}/16"
                else:
                    yield 4, f"{ipv4(V4_PRIVATE + ordinal)}/32"
            else:
                if ordinal % 64 == 0:
                    yield 6, "2001:db8::/32"
                elif ordinal % 3 == 0:
                    yield 6, f"{ipaddress.IPv6Address(V6_BASE + (ordinal << 64))}/64"
                elif ordinal % 3 == 1:
                    yield 6, f"{ipaddress.IPv6Address(V6_BASE + ((ordinal & 65535) << 80))}/48"
                else:
                    yield 6, f"{ipaddress.IPv6Address(V6_BASE + ordinal)}/128"
        elif name == "mixed-adjacent":
            ordinal = index // 2
            if index % 2 == 0:
                yield 4, f"{ipv4(ordinal)}/32"
            else:
                yield 6, f"{ipaddress.IPv6Address(V6_BASE + ordinal)}/128"
        elif name == "bgp-like-ipv4":
            state = (state * 6_364_136_223_846_793_005 + 1_442_695_040_888_963_407) & ((1 << 64) - 1)
            length = lengths[state % len(lengths)]
            state = (state * 6_364_136_223_846_793_005 + 1_442_695_040_888_963_407) & ((1 << 64) - 1)
            address = (state & 0xFFFFFFFF) & (0xFFFFFFFF << (32 - length))
            yield 4, f"{ipv4(address)}/{length}"
        elif name == "range-derived-mixed":
            ordinal = index // 2
            offset = 0 if index % 2 == 0 else 4
            if ordinal % 2 == 0:
                yield 4, f"{ipv4(ordinal * 16 + offset)}/{30 if offset == 0 else 31}"
            else:
                yield 6, f"{ipaddress.IPv6Address(V6_BASE + ordinal * 16 + offset)}/{126 if offset == 0 else 127}"
        else:
            raise ValueError(name)


def oracle_self_test():
    randomizer = random.Random(0xC1D4)
    checks = 0
    for width, address_type in ((32, ipaddress.IPv4Address), (128, ipaddress.IPv6Address)):
        bounds = [(0, 0), (0, (1 << width) - 1), ((1 << width) - 1, (1 << width) - 1)]
        for _ in range(200):
            lower = randomizer.getrandbits(width)
            upper = min((1 << width) - 1, lower + randomizer.randrange(1, 1 << 20))
            bounds.append((lower, upper))
        for lower, upper in bounds:
            wanted = len(list(ipaddress.summarize_address_range(address_type(lower), address_type(upper))))
            assert minimal_cidr_count(lower, upper, width) == wanted
            checks += 1
    return {"passed": True, "minimum_cover_count_cases": checks, "reference": "stdlib ipaddress.summarize_address_range; deterministic random intervals and full-space/max-address boundaries"}


def generate_case(root, name):
    destination = root / name
    destination.mkdir(exist_ok=False)
    paths = {label: destination / label for label in ("input.txt", "ipv4.txt", "ipv6.txt")}
    hashes = {label: hashlib.sha256() for label in paths}
    counts = {label: 0 for label in paths}
    with paths["input.txt"].open("xb", buffering=1024 * 1024) as common, paths["ipv4.txt"].open("xb", buffering=1024 * 1024) as v4, paths["ipv6.txt"].open("xb", buffering=1024 * 1024) as v6:
        handles = {"input.txt": common, "ipv4.txt": v4, "ipv6.txt": v6}
        for family, text in records(name):
            encoded = (text + "\n").encode("ascii")
            for label in ("input.txt", "ipv4.txt" if family == 4 else "ipv6.txt"):
                handles[label].write(encoded)
                hashes[label].update(encoded)
                counts[label] += 1
    assert counts["input.txt"] == COUNT
    assert counts["ipv4.txt"] + counts["ipv6.txt"] == COUNT
    manifest = {
        "name": name, "input_count": COUNT, "recipe": RECIPES[name],
        "generator_sha256": sha256_file(__file__),
        "oracle_sha256": sha256_file(Path(__file__).with_name("verify_coverage.py")),
        "files": {label: {"lines": counts[label], "bytes": path.stat().st_size, "sha256": hashes[label].hexdigest()} for label, path in paths.items()},
        "conversion_scope": "All tools receive identical CIDR records. Native arbitrary-range parsing is outside this comparison; range-derived-mixed expansion occurs before timing.",
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    intervals, family_counts, parsed_files = parse_network_files([paths["input.txt"]], require_slash=True)
    expected = coverage_summary(intervals, family_counts)
    expected.update(fixture=name, input_file_sha256=parsed_files[0]["sha256"], oracle="Python stdlib ipaddress strict parser plus independent numeric interval union and power-of-two cover counting")
    assert expected["input_count"] == COUNT
    if name in ("ipv4-disjoint", "ipv6-disjoint", "mixed-disjoint", "mixed-permuted", "range-derived-mixed"):
        assert expected["minimal_cidr_count"] == COUNT
    if name == "mixed-overlap":
        assert expected["minimal_cidr_count"] == 2 and expected["range_count"] == 2
    if name == "mixed-adjacent":
        assert expected["range_count"] == 2 and expected["addresses_covered"] == {"ipv4": "500000", "ipv6": "500000"}
    if name == "bgp-like-ipv4":
        assert expected["range_count"] == 193255 and expected["minimal_cidr_count"] == 233532
    if name == "range-derived-mixed":
        assert expected["range_count"] == 500000 and expected["addresses_covered"] == {"ipv4": "1500000", "ipv6": "1500000"}
    if name == "mixed-permuted":
        original = json.loads((root / "mixed-disjoint/expected.json").read_text())
        assert expected["coverage_sha256"] == original["coverage_sha256"]
    (destination / "expected.json").write_text(json.dumps(expected, indent=2) + "\n")
    print(json.dumps({"fixture": name, "inputs": COUNT, "family_counts": family_counts, "ranges": expected["range_count"], "minimum_cidrs": expected["minimal_cidr_count"], "coverage_sha256": expected["coverage_sha256"]}), flush=True)
    return {"name": name, "manifest_sha256": sha256_file(destination / "manifest.json"), "expected_sha256": sha256_file(destination / "expected.json")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root / "fixtures"
    root.mkdir(exist_ok=False)
    receipt = {"started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "oracle_self_test": oracle_self_test(), "cases": [], "passed": False}
    try:
        for name in CASES:
            receipt["cases"].append(generate_case(root, name))
        receipt["passed"] = True
    except Exception as error:
        receipt["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        receipt["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (root / "generation-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
