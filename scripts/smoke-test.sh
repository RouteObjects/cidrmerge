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
[[ "$("$BINARY" --version)" == "0.2.0" ]] \
    || fail "--version did not report 0.2.0"

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
grep -Fq -- '--checksum' "$HELP_STDOUT" \
    || fail "--help did not document detached checksum generation"
grep -Fq 'With --output, write a detached SHA-256 checksum file' "$HELP_STDOUT" \
    || fail "--help did not document the checksum output boundary"
grep -Fq 'for the exact output bytes.' "$HELP_STDOUT" \
    || fail "--help did not document the checksum output boundary"

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

# CHANGE: Verify the exact producer contract independently with system checksum tooling.
CHECKSUM_OUTPUT="$TEMPORARY_DIRECTORY/allow ranges.txt"
CHECKSUM_STDOUT="$TEMPORARY_DIRECTORY/checksum.stdout"
printf '%s\n' '192.0.2.0/25' '192.0.2.128/25' \
    | "$BINARY" --raw --checksum --output "$CHECKSUM_OUTPUT" >"$CHECKSUM_STDOUT"
[[ ! -s "$CHECKSUM_STDOUT" ]] \
    || fail "file output with --checksum produced stdout"
if ! diff -u \
    <(printf '%s\n' '192.0.2.0...192.0.2.255') \
    "$CHECKSUM_OUTPUT"
then
    fail "checksummed raw output did not match"
fi
if ! diff -u \
    <(printf '%s\n' \
        '4fadfa35475984133bb25b33cbb5e793e475888f0c2f1d1347f4df2c7b06f52e  allow ranges.txt') \
    "$CHECKSUM_OUTPUT.sha256"
then
    fail "raw detached checksum bytes did not match"
fi
if command -v sha256sum >/dev/null 2>&1; then
    (cd "$TEMPORARY_DIRECTORY" && sha256sum --check 'allow ranges.txt.sha256')
else
    (cd "$TEMPORARY_DIRECTORY" && shasum -a 256 --check 'allow ranges.txt.sha256')
fi

CHECKSUM_JSON="$TEMPORARY_DIRECTORY/policy.json"
printf '%s\n' '192.0.2.0/24' '2001:db8::/32' \
    | "$BINARY" --json --representation cidr --checksum --output "$CHECKSUM_JSON"
if ! diff -u \
    <(printf '%s\n' \
        '901df054b3fb4eb812693875e0a8b52db5fc112afd76e1402e732cfcd4f2bdac  policy.json') \
    "$CHECKSUM_JSON.sha256"
then
    fail "JSON detached checksum did not cover the exact renderer bytes"
fi

EMPTY_CHECKSUM_OUTPUT="$TEMPORARY_DIRECTORY/empty.txt"
printf '' | "$BINARY" --raw --checksum --output "$EMPTY_CHECKSUM_OUTPUT"
[[ ! -s "$EMPTY_CHECKSUM_OUTPUT" ]] \
    || fail "checksummed empty raw output was not zero bytes"
if ! diff -u \
    <(printf '%s\n' \
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  empty.txt') \
    "$EMPTY_CHECKSUM_OUTPUT.sha256"
then
    fail "empty raw detached checksum did not hash zero bytes"
fi

CHECKSUM_OPTION_STDOUT="$TEMPORARY_DIRECTORY/checksum-option.stdout"
CHECKSUM_OPTION_STDERR="$TEMPORARY_DIRECTORY/checksum-option.stderr"
set +e
"$BINARY" --checksum /definitely/missing/input.txt \
    >"$CHECKSUM_OPTION_STDOUT" 2>"$CHECKSUM_OPTION_STDERR"
CHECKSUM_OPTION_STATUS=$?
set -e
[[ "$CHECKSUM_OPTION_STATUS" -eq 1 ]] \
    || fail "--checksum without --output did not exit with status 1"
[[ ! -s "$CHECKSUM_OPTION_STDOUT" ]] \
    || fail "--checksum without --output produced stdout"
grep -Fq 'cidrmerge: error: --checksum requires --output' "$CHECKSUM_OPTION_STDERR" \
    || fail "--checksum without --output did not fail before reading input"

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

PRESERVED_CHECKSUM_OUTPUT="$TEMPORARY_DIRECTORY/preserved-checksum.txt"
PRESERVED_DETACHED_CHECKSUM="$PRESERVED_CHECKSUM_OUTPUT.sha256"
printf '%s\n' 'existing checksummed policy' >"$PRESERVED_CHECKSUM_OUTPUT"
printf '%s\n' 'existing detached checksum' >"$PRESERVED_DETACHED_CHECKSUM"

set +e
printf '%s\n' '192.0.2.0/24' 'not-a-prefix' \
    | "$BINARY" --checksum --output "$PRESERVED_CHECKSUM_OUTPUT" \
        >"$TEMPORARY_DIRECTORY/preserved-checksum.stdout" \
        2>"$TEMPORARY_DIRECTORY/preserved-checksum.stderr"
PRESERVED_CHECKSUM_STATUS=$?
set -e
[[ "$PRESERVED_CHECKSUM_STATUS" -eq 1 ]] \
    || fail "invalid checksummed input did not exit with status 1"
if ! diff -u \
    <(printf '%s\n' 'existing checksummed policy') \
    "$PRESERVED_CHECKSUM_OUTPUT"
then
    fail "invalid checksummed input replaced the output"
fi
if ! diff -u \
    <(printf '%s\n' 'existing detached checksum') \
    "$PRESERVED_DETACHED_CHECKSUM"
then
    fail "invalid checksummed input replaced the detached checksum"
fi

CHECKSUM_FAILURE_OUTPUT="$TEMPORARY_DIRECTORY/checksum-failure.txt"
printf '%s\n' 'preserved after checksum failure' >"$CHECKSUM_FAILURE_OUTPUT"
mkdir "$CHECKSUM_FAILURE_OUTPUT.sha256"
set +e
printf '%s\n' '192.0.2.0/24' \
    | "$BINARY" --checksum --output "$CHECKSUM_FAILURE_OUTPUT" \
        >"$TEMPORARY_DIRECTORY/checksum-failure.stdout" \
        2>"$TEMPORARY_DIRECTORY/checksum-failure.stderr"
CHECKSUM_FAILURE_STATUS=$?
set -e
[[ "$CHECKSUM_FAILURE_STATUS" -eq 1 ]] \
    || fail "detached checksum replacement failure did not exit with status 1"
if ! diff -u \
    <(printf '%s\n' 'preserved after checksum failure') \
    "$CHECKSUM_FAILURE_OUTPUT"
then
    fail "detached checksum failure replaced the output"
fi

OUTPUT_FAILURE_PATH="$TEMPORARY_DIRECTORY/output-failure"
mkdir "$OUTPUT_FAILURE_PATH"
set +e
printf '%s\n' '192.0.2.0/24' \
    | "$BINARY" --checksum --output "$OUTPUT_FAILURE_PATH" \
        >"$TEMPORARY_DIRECTORY/output-failure.stdout" \
        2>"$TEMPORARY_DIRECTORY/output-failure.stderr"
OUTPUT_FAILURE_STATUS=$?
set -e
[[ "$OUTPUT_FAILURE_STATUS" -eq 1 ]] \
    || fail "output replacement failure did not exit with status 1"
[[ -d "$OUTPUT_FAILURE_PATH" ]] \
    || fail "output replacement failure changed the destination directory"
[[ -s "$OUTPUT_FAILURE_PATH.sha256" ]] \
    || fail "output replacement failure did not leave the new fail-closed checksum"

printf 'cidrmerge smoke test passed\n'
