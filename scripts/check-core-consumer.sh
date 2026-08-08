#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CONSUMER_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cidrmerge-core-consumer.XXXXXX")"

cleanup() {
    rm -rf -- "${CONSUMER_ROOT}"
}
trap cleanup EXIT

fail() {
    printf 'CIDRMergeCore consumer check: %s\n' "$*" >&2
    exit 1
}

mkdir -p "${CONSUMER_ROOT}/Sources/CoreConsumer"

cat >"${CONSUMER_ROOT}/Package.swift" <<EOF
// swift-tools-version: 6.1

import PackageDescription

let package = Package(
    name: "CoreConsumer",
    platforms: [.macOS(.v15)],
    dependencies: [
        // CHANGE: Give the local dependency a stable identity even when a release
        // snapshot or consumer checks out the package under another directory name.
        .package(name: "cidrmerge", path: "${PACKAGE_ROOT}"),
        .package(
            url: "https://github.com/RouteObjects/swift-cidr.git",
            .upToNextMinor(from: "0.5.0")
        ),
    ],
    targets: [
        .executableTarget(
            name: "CoreConsumer",
            dependencies: [
                .product(name: "CIDRMergeCore", package: "cidrmerge"),
                .product(name: "CIDR", package: "swift-cidr"),
            ]
        )
    ],
    swiftLanguageModes: [.v6]
)
EOF

cat >"${CONSUMER_ROOT}/Sources/CoreConsumer/main.swift" <<'EOF'
import CIDR
import CIDRMergeCore

enum ConsumerError: Error {
    case invalidRange(String)
}

func parseRange(_ text: String) throws -> AnyIPAddressRange {
    guard let range = AnyIPAddressRange(text) else {
        throw ConsumerError.invalidRange(text)
    }
    return range
}

let coverage = CIDRMergeCoverage(
    ranges: try [
        "2001:db8::...2001:db8::ffff",
        "192.0.2.0...192.0.2.191",
    ].map(parseRange)
)

for range in coverage.ranges {
    print(range)
}
EOF

cd "${CONSUMER_ROOT}"
swift package resolve
swift build --product CoreConsumer

if find .build -name 'Crypto.swiftmodule' -print -quit | grep -q .; then
    fail "a Core-only consumer compiled the CLI-only Crypto module"
fi

consumer_binary="$(swift build --show-bin-path)/CoreConsumer"
actual_output="${CONSUMER_ROOT}/actual.txt"
expected_output="${CONSUMER_ROOT}/expected.txt"
"${consumer_binary}" >"${actual_output}"
printf '%s\n' \
    '192.0.2.0...192.0.2.191' \
    '2001:db8::...2001:db8::ffff' \
    >"${expected_output}"
cmp "${expected_output}" "${actual_output}" ||
    fail "the external consumer did not preserve deterministic exact coverage"

printf 'CIDRMergeCore external consumer check passed.\n'
