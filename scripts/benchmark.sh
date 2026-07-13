#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
COUNT="${CIDRMERGE_BENCHMARK_COUNT:-1000000}"
MAX_RSS_KB="${CIDRMERGE_MAX_RSS_KB:-524288}"
SCENARIOS=("$@")
REPRESENTATIONS=(ranges cidr)

if (("${#SCENARIOS[@]}" == 0)); then
    SCENARIOS=(disjoint siblings subsumed bgp-like rpki-like mixed arbitrary-ranges overlapping-ranges)
fi

case "$COUNT" in
    '' | *[!0-9]* | 0)
        echo "error: CIDRMERGE_BENCHMARK_COUNT must be a positive integer" >&2
        exit 64
        ;;
esac

TEMPORARY_DIRECTORY="$(mktemp -d "${TMPDIR:-/tmp}/cidrmerge-benchmark.XXXXXX")"
trap 'rm -rf "$TEMPORARY_DIRECTORY"' EXIT

swift build -c release --package-path "$PACKAGE_ROOT" --product cidrmerge
swiftc -parse-as-library -O "$PACKAGE_ROOT/Benchmarks/CorpusGenerator.swift" \
    -o "$TEMPORARY_DIRECTORY/corpus-generator"

BINARY="$PACKAGE_ROOT/.build/release/cidrmerge"

for scenario in "${SCENARIOS[@]}"; do
    fixture="$TEMPORARY_DIRECTORY/$scenario.txt"
    "$TEMPORARY_DIRECTORY/corpus-generator" "$scenario" "$COUNT" >"$fixture"

    for representation in "${REPRESENTATIONS[@]}"; do
        metrics="$TEMPORARY_DIRECTORY/$scenario-$representation.time"

        if [[ "$(uname -s)" == "Darwin" ]]; then
            /usr/bin/time -p -l -o "$metrics" "$BINARY" --representation "$representation" "$fixture" >/dev/null
            peak_rss_kb="$(awk '/maximum resident set size/ { printf "%.0f", $1 / 1024 }' "$metrics")"
        else
            /usr/bin/time -p -v -o "$metrics" "$BINARY" --representation "$representation" "$fixture" >/dev/null
            peak_rss_kb="$(awk -F ': ' '/Maximum resident set size/ { print $2 }' "$metrics")"
        fi

        real_seconds="$(awk '/^real / { print $2 }' "$metrics")"
        throughput="$(awk -v count="$COUNT" -v seconds="$real_seconds" \
            'BEGIN { if (seconds > 0) printf "%.0f", count / seconds; else print "n/a" }')"

        echo "$scenario/$representation: $COUNT records, ${real_seconds}s, $throughput records/s, ${peak_rss_kb} KiB peak RSS"

        if [[ -n "$peak_rss_kb" ]] && ((peak_rss_kb > MAX_RSS_KB)); then
            echo "error: $scenario/$representation exceeded ${MAX_RSS_KB} KiB peak RSS" >&2
            exit 1
        fi
    done
done
