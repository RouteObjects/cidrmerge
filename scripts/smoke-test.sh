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

# Exercise the packaged release executable so CLI process wiring is covered in addition to
# unit-level parsing, merging, and rendering helpers.
swift build --package-path "$PACKAGE_ROOT" -c release --product cidrmerge
BINARY_DIRECTORY="$(swift build --package-path "$PACKAGE_ROOT" -c release --show-bin-path)"
BINARY="$BINARY_DIRECTORY/cidrmerge"
[[ -x "$BINARY" ]] || fail "release executable was not found at $BINARY"

# Lock the user-visible release identity and basic help wiring before a tag is created.
[[ "$("$BINARY" --version)" == "0.1.0" ]] \
    || fail "--version did not report 0.1.0"

set +e
"$BINARY" -v >"$TEMPORARY_DIRECTORY/short-version.stdout" \
    2>"$TEMPORARY_DIRECTORY/short-version.stderr"
SHORT_VERSION_STATUS=$?
set -e
[[ "$SHORT_VERSION_STATUS" -ne 0 ]] \
    || fail "-v is intentionally unassigned but was accepted"

HELP_STDOUT="$TEMPORARY_DIRECTORY/help.stdout"
"$BINARY" --help >"$HELP_STDOUT"
grep -Fq 'USAGE: cidrmerge' "$HELP_STDOUT" \
    || fail "--help did not contain the command usage"
grep -Fq -- '--raw' "$HELP_STDOUT" \
    || fail "--help did not document raw output"
grep -Fq -- '-j, --json' "$HELP_STDOUT" \
    || fail "--help did not document the short and long JSON flags"
grep -Fq -- '--input-format <input-format>' "$HELP_STDOUT" \
    || fail "--help did not document input format selection"
grep -Fq 'Input grammar for every operand: text or searchbot.' "$HELP_STDOUT" \
    || fail "--help did not document both input grammars"
grep -Fq '(default: text)' "$HELP_STDOUT" \
    || fail "--help did not identify text as the default input grammar"
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

EMPTY_STDOUT="$TEMPORARY_DIRECTORY/empty.stdout"
printf '' | "$BINARY" --raw >"$EMPTY_STDOUT"
[[ ! -s "$EMPTY_STDOUT" ]] \
    || fail "empty raw input did not produce exactly zero output bytes"

JSON_STDOUT="$TEMPORARY_DIRECTORY/json.stdout"
printf '%s\n' \
    '2001:db8::/126' \
    '192.0.2.0/31' \
    | "$BINARY" --json --representation cidr >"$JSON_STDOUT"

if ! diff -u \
    <(printf '%s\n' \
        '{' \
        '  "ipv4" : [' \
        '    "192.0.2.0/31"' \
        '  ],' \
        '  "ipv6" : [' \
        '    "2001:db8::/126"' \
        '  ],' \
        '  "representation" : "cidr"' \
        '}') \
    "$JSON_STDOUT"
then
    fail "JSON output schema or deterministic ordering did not match"
fi

SEARCHBOT_STDOUT="$TEMPORARY_DIRECTORY/searchbot.stdout"
SEARCHBOT_STDERR="$TEMPORARY_DIRECTORY/searchbot.stderr"
printf '%s' \
    '{"creationTime":"fixture","prefixes":[{"ipv6Prefix":"2001:0DB8::1/126"},{"ipv4Prefix":"192.0.2.1/31"},{"ipv4Prefix":"192.0.2.2/31"}]}' \
    | "$BINARY" --input-format searchbot --representation cidr --stats \
        >"$SEARCHBOT_STDOUT" 2>"$SEARCHBOT_STDERR"

if ! diff -u \
    <(printf '%s\n' '192.0.2.0/30' '2001:db8::/126') \
    "$SEARCHBOT_STDOUT"
then
    fail "searchbot stdin did not produce deterministic CIDR output"
fi

if ! diff -u \
    <(printf '%s\n' \
        'input: 3 entries (2 IPv4, 1 IPv6)' \
        'normalized: 2 entries' \
        'output: 2 prefixes (1 IPv4, 1 IPv6)' \
        'reduction: 1 entry (33.3%)') \
    "$SEARCHBOT_STDERR"
then
    fail "searchbot statistics stderr did not match"
fi

INVALID_SEARCHBOT_STDOUT="$TEMPORARY_DIRECTORY/invalid-searchbot.stdout"
INVALID_SEARCHBOT_STDERR="$TEMPORARY_DIRECTORY/invalid-searchbot.stderr"
set +e
printf '%s' '{"prefixes":[{"ipv4Prefix":17}]}' \
    | "$BINARY" --input-format searchbot \
        >"$INVALID_SEARCHBOT_STDOUT" 2>"$INVALID_SEARCHBOT_STDERR"
INVALID_SEARCHBOT_STATUS=$?
set -e

[[ "$INVALID_SEARCHBOT_STATUS" -eq 1 ]] \
    || fail "invalid searchbot input exited with status $INVALID_SEARCHBOT_STATUS instead of 1"
[[ ! -s "$INVALID_SEARCHBOT_STDOUT" ]] \
    || fail "invalid searchbot input produced partial stdout"
grep -Fq \
    'cidrmerge: <stdin>:$.prefixes[0].ipv4Prefix: error: invalid searchbot input: value has the wrong JSON type' \
    "$INVALID_SEARCHBOT_STDERR" \
    || fail "invalid searchbot diagnostic did not identify <stdin> and the prefix path"

DUPLICATE_SEARCHBOT_STDOUT="$TEMPORARY_DIRECTORY/duplicate-searchbot.stdout"
DUPLICATE_SEARCHBOT_STDERR="$TEMPORARY_DIRECTORY/duplicate-searchbot.stderr"
set +e
printf '%s' \
    '{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv4Prefix":"198.51.100.0/24"}]}' \
    | "$BINARY" --input-format searchbot \
        >"$DUPLICATE_SEARCHBOT_STDOUT" 2>"$DUPLICATE_SEARCHBOT_STDERR"
DUPLICATE_SEARCHBOT_STATUS=$?
set -e

[[ "$DUPLICATE_SEARCHBOT_STATUS" -eq 1 ]] \
    || fail "duplicate searchbot member exited with status $DUPLICATE_SEARCHBOT_STATUS instead of 1"
[[ ! -s "$DUPLICATE_SEARCHBOT_STDOUT" ]] \
    || fail "duplicate searchbot member produced partial stdout"
grep -Fq \
    'cidrmerge: <stdin>:$.prefixes[0].ipv4Prefix: error: invalid searchbot input: duplicate JSON member' \
    "$DUPLICATE_SEARCHBOT_STDERR" \
    || fail "duplicate searchbot diagnostic did not identify the semantic member"

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

PRESERVED_OUTPUT="$TEMPORARY_DIRECTORY/preserved-output.txt"
PRESERVED_STDERR="$TEMPORARY_DIRECTORY/preserved-output.stderr"
printf '%s\n' 'existing policy' >"$PRESERVED_OUTPUT"

set +e
printf '%s\n' \
    '192.0.2.0/24' \
    'not-a-prefix' \
    | "$BINARY" --output "$PRESERVED_OUTPUT" 2>"$PRESERVED_STDERR"
PRESERVED_STATUS=$?
set -e

[[ "$PRESERVED_STATUS" -eq 1 ]] \
    || fail "invalid file input exited with status $PRESERVED_STATUS instead of 1"
if ! diff -u \
    <(printf '%s\n' 'existing policy') \
    "$PRESERVED_OUTPUT"
then
    fail "invalid input replaced an existing output file"
fi

VALID_SEARCHBOT_FILE="$TEMPORARY_DIRECTORY/valid-searchbot.json"
INVALID_SEARCHBOT_FILE="$TEMPORARY_DIRECTORY/invalid-searchbot.json"
PRESERVED_SEARCHBOT_OUTPUT="$TEMPORARY_DIRECTORY/preserved-searchbot-output.txt"
printf '%s' '{"prefixes":[{"ipv4Prefix":"192.0.2.0/24"}]}' \
    >"$VALID_SEARCHBOT_FILE"
printf '%s' '{"prefixes":[{"ipv6Prefix":false}]}' \
    >"$INVALID_SEARCHBOT_FILE"
printf '%s\n' 'existing searchbot policy' >"$PRESERVED_SEARCHBOT_OUTPUT"

set +e
"$BINARY" --input-format searchbot --output "$PRESERVED_SEARCHBOT_OUTPUT" \
    "$VALID_SEARCHBOT_FILE" "$INVALID_SEARCHBOT_FILE" \
    >"$TEMPORARY_DIRECTORY/preserved-searchbot.stdout" \
    2>"$TEMPORARY_DIRECTORY/preserved-searchbot.stderr"
PRESERVED_SEARCHBOT_STATUS=$?
set -e

[[ "$PRESERVED_SEARCHBOT_STATUS" -eq 1 ]] \
    || fail "invalid later searchbot document exited with status $PRESERVED_SEARCHBOT_STATUS instead of 1"
if ! diff -u \
    <(printf '%s\n' 'existing searchbot policy') \
    "$PRESERVED_SEARCHBOT_OUTPUT"
then
    fail "invalid later searchbot document replaced an existing output file"
fi

printf 'cidrmerge smoke test passed\n'
