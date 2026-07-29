#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TEMPORARY_DIRECTORY="$(mktemp -d "${TMPDIR:-/tmp}/cidrmerge-smoke.XXXXXX")"

cleanup() {
    rm -rf -- "$TEMPORARY_DIRECTORY"
}
trap cleanup EXIT

fail() {
    printf 'cidrmerge smoke test: %s\n' "$1" >&2
    exit 1
}

export CLANG_MODULE_CACHE_PATH="${CLANG_MODULE_CACHE_PATH:-$PACKAGE_ROOT/.build/clang-module-cache}"
mkdir -p "$CLANG_MODULE_CACHE_PATH"

# CHANGE: Exercise the packaged release executable so CLI process wiring is covered in addition to
# unit-level parsing, merging, and rendering helpers.
swift build --package-path "$PACKAGE_ROOT" -c release --product cidrmerge
BINARY_DIRECTORY="$(swift build --package-path "$PACKAGE_ROOT" -c release --show-bin-path)"
BINARY="$BINARY_DIRECTORY/cidrmerge"
[[ -x "$BINARY" ]] || fail "release executable was not found at $BINARY"

# CHANGE: Lock the user-visible release identity and basic help wiring before a tag is created.
[[ "$("$BINARY" --version)" == "0.1.0" ]] \
    || fail "--version did not report 0.1.0"
[[ "$("$BINARY" -v)" == "0.1.0" ]] \
    || fail "-v did not report 0.1.0"

HELP_STDOUT="$TEMPORARY_DIRECTORY/help.stdout"
"$BINARY" --help >"$HELP_STDOUT"
grep -Fq 'USAGE: cidrmerge' "$HELP_STDOUT" \
    || fail "--help did not contain the command usage"
grep -Fq 'Semantic representation: ranges or cidr.' "$HELP_STDOUT" \
    || fail "--help did not document both representations"
grep -Fq '(default: ranges)' "$HELP_STDOUT" \
    || fail "--help did not identify ranges as the default representation"

VALID_STDOUT="$TEMPORARY_DIRECTORY/valid.stdout"
VALID_STDERR="$TEMPORARY_DIRECTORY/valid.stderr"

printf '%s\n' \
    '192.0.2.0/25' \
    '192.0.2.128/25' \
    | "$BINARY" --stats >"$VALID_STDOUT" 2>"$VALID_STDERR"

if ! diff -u \
    <(printf '%s\n' '192.0.2.0...192.0.2.255') \
    "$VALID_STDOUT"
then
    fail "default range stdout did not match"
fi

if ! diff -u \
    <(printf '%s\n' \
        'input: 2 entries (2 IPv4, 0 IPv6)' \
        'normalized: 0 entries' \
        'output: 1 range (1 IPv4, 0 IPv6)' \
        'reduction: 1 entry (50.0%)') \
    "$VALID_STDERR"
then
    fail "statistics stderr did not match"
fi

INVALID_STDOUT="$TEMPORARY_DIRECTORY/invalid.stdout"
INVALID_STDERR="$TEMPORARY_DIRECTORY/invalid.stderr"

set +e
printf '%s\n' \
    '192.0.2.0/24' \
    'not-a-prefix' \
    | "$BINARY" >"$INVALID_STDOUT" 2>"$INVALID_STDERR"
INVALID_STATUS=$?
set -e

[[ "$INVALID_STATUS" -eq 1 ]] \
    || fail "invalid input exited with status $INVALID_STATUS instead of 1"
[[ ! -s "$INVALID_STDOUT" ]] \
    || fail "invalid input produced partial stdout"
grep -Fq \
    'cidrmerge: <stdin>:2: error: invalid IP address, network, or range "not-a-prefix"' \
    "$INVALID_STDERR" \
    || fail "invalid input diagnostic did not identify <stdin>:2"

printf 'cidrmerge smoke test passed\n'
