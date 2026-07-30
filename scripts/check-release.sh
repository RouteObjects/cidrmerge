#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

VERSION="${1:-}"
[[ "${VERSION}" =~ ^[0-9]+[.][0-9]+[.][0-9]+$ ]] ||
    fail "Usage: scripts/check-release.sh MAJOR.MINOR.PATCH"

cd "${PACKAGE_ROOT}"

[[ -z "$(git status --short)" ]] ||
    fail "Commit or stash package changes before running the release check."

release_temporary_directory="$(mktemp -d "${TMPDIR:-/tmp}/cidrmerge-release-check.XXXXXX")"
cleanup() {
    rm -rf -- "${release_temporary_directory}"
}
trap cleanup EXIT

for required in \
    LICENSE \
    THIRD_PARTY_NOTICES.txt \
    SECURITY.md \
    .spi.yml \
    .swift-format.json \
    .github/workflows/ci.yml \
    .github/workflows/release.yml; do
    [[ -e "${required}" ]] || fail "Required release file is missing: ${required}"
done

while IFS= read -r swift_file; do
    grep -q 'SPDX-License-Identifier: Apache-2.0' "${swift_file}" ||
        fail "Apache license header is missing: ${swift_file}"
done < <(find Package.swift Sources Tests Benchmarks -name '*.swift' -type f -print)

# CHANGE: Keep the reviewed notice synchronized with every pin in the complete
# resolved graph, including packages resolved for products cidrmerge does not link.
resolved_pin_count=0
while IFS='|' read -r identity version revision; do
    [[ -n "${identity}" && -n "${version}" && -n "${revision}" ]] ||
        fail "Unable to parse a dependency pin from Package.resolved."
    grep -Fq "${identity} ${version}" THIRD_PARTY_NOTICES.txt ||
        fail "THIRD_PARTY_NOTICES.txt is missing ${identity} ${version}."
    grep -Fq "Revision: ${revision}" THIRD_PARTY_NOTICES.txt ||
        fail "THIRD_PARTY_NOTICES.txt is missing revision ${revision}."
    ((resolved_pin_count += 1))
done < <(
    awk -F '"' '
        /"identity"/ { identity = $4 }
        /"revision"/ { revision = $4 }
        /"version"/ && $4 != "" { print identity "|" $4 "|" revision }
    ' Package.resolved
)
((resolved_pin_count > 0)) || fail "Package.resolved does not contain dependency pins."

"${SCRIPT_DIR}/audit-release-content.sh" tree

git diff --check
swift package resolve
git diff --exit-code -- Package.resolved
swift format lint \
    --configuration .swift-format.json \
    --recursive \
    --strict \
    Package.swift Sources Tests Benchmarks
swift build --product cidrmerge
"${SCRIPT_DIR}/test.sh"

# CHANGE: Exercise process-level contracts before benchmarking the same complete
# offline compiler pipeline with the release-candidate million-record corpus.
"${SCRIPT_DIR}/smoke-test.sh"
benchmark_log="${release_temporary_directory}/benchmark.log"
CIDRMERGE_BENCHMARK_COUNT=1000000 "${SCRIPT_DIR}/benchmark.sh" | tee "${benchmark_log}"
benchmark_record_count="$(
    awk '
        /^.+\/(ranges|cidr): 1000000 records, [0-9.]+s, ([0-9]+|n\/a) records\/s, [0-9]+ KiB peak RSS$/ {
            count += 1
        }
        END { print count + 0 }
    ' "${benchmark_log}"
)"
[[ "${benchmark_record_count}" -eq 16 ]] ||
    fail "The million-record benchmark did not report numeric metrics for all 16 runs."

# CHANGE: Lock the benchmark corpus cardinalities and prove that CIDR and range
# output independently normalize back to the same exact deterministic cover.
benchmark_generator="${release_temporary_directory}/corpus-generator"
swiftc -parse-as-library -O Benchmarks/CorpusGenerator.swift -o "${benchmark_generator}"
benchmark_binary="$(swift build -c release --show-bin-path)/cidrmerge"
benchmark_scenarios=(
    disjoint
    siblings
    subsumed
    bgp-like
    rpki-like
    mixed
    arbitrary-ranges
    overlapping-ranges
)
expected_range_counts=(1000000 1 1 193255 49483 1000000 1000000 1)
expected_cidr_counts=(1000000 7 1 233532 61444 1000000 2000000 8)

for benchmark_index in "${!benchmark_scenarios[@]}"; do
    scenario="${benchmark_scenarios[benchmark_index]}"
    fixture="${release_temporary_directory}/fixture.txt"
    range_output="${release_temporary_directory}/ranges.txt"
    cidr_output="${release_temporary_directory}/cidr.txt"
    cidr_as_ranges="${release_temporary_directory}/cidr-as-ranges.txt"

    "${benchmark_generator}" "${scenario}" 1000000 >"${fixture}"
    "${benchmark_binary}" --raw --representation ranges "${fixture}" >"${range_output}"
    "${benchmark_binary}" --raw --representation cidr "${fixture}" >"${cidr_output}"
    "${benchmark_binary}" --raw --representation ranges "${cidr_output}" >"${cidr_as_ranges}"
    cmp "${range_output}" "${cidr_as_ranges}" ||
        fail "Benchmark representations disagree on exact coverage for ${scenario}."

    range_count="$(wc -l <"${range_output}" | tr -d '[:space:]')"
    cidr_count="$(wc -l <"${cidr_output}" | tr -d '[:space:]')"
    [[ "${range_count}" -eq "${expected_range_counts[benchmark_index]}" ]] ||
        fail "Unexpected range cardinality for ${scenario}: ${range_count}."
    [[ "${cidr_count}" -eq "${expected_cidr_counts[benchmark_index]}" ]] ||
        fail "Unexpected CIDR cardinality for ${scenario}: ${cidr_count}."
done

# Verify that the reusable public surface can emit a symbol graph independently
# of the command-line and executable modules.
symbol_graph_directory="$(
    mktemp -d "${release_temporary_directory}/cidrmerge-symbol-graphs.XXXXXX"
)"
swift build \
    --target CIDRMergeCore \
    -Xswiftc -emit-symbol-graph \
    -Xswiftc -emit-symbol-graph-dir \
    -Xswiftc "${symbol_graph_directory}"
test -s "${symbol_graph_directory}/CIDRMergeCore.symbols.json" ||
    fail "CIDRMergeCore did not emit a public symbol graph."

if [[ "$(uname -s)" == "Darwin" ]]; then
    sdk_path="$(xcrun --sdk iphonesimulator --show-sdk-path)"
    swift build \
        --target CIDRMergeCore \
        --triple arm64-apple-ios18.0-simulator \
        --sdk "${sdk_path}"
fi

if [[ "$(uname -s)" == "Linux" ]]; then
    swift build \
        -c release \
        --static-swift-stdlib \
        --product cidrmerge \
        -Xswiftc -debug-prefix-map \
        -Xswiftc "${PACKAGE_ROOT}=Source" \
        -Xcc "-ffile-prefix-map=${PACKAGE_ROOT}/.build=SwiftPMBuild"
else
    # Match the GitHub Actions Darwin build so the local release gate audits
    # the same remapped and stripped binary that will enter public archives.
    swift build \
        -c release \
        --product cidrmerge \
        -Xswiftc -file-prefix-map \
        -Xswiftc "${PACKAGE_ROOT}/.build=SwiftPMBuild" \
        -Xswiftc -file-prefix-map \
        -Xswiftc "${PACKAGE_ROOT}=Source" \
        -Xcc "-ffile-prefix-map=${PACKAGE_ROOT}/.build=SwiftPMBuild" \
        -Xcc "-ffile-prefix-map=${PACKAGE_ROOT}=Source"
fi

binary="$(swift build -c release --show-bin-path)/cidrmerge"
if [[ "$(uname -s)" == "Linux" ]]; then
    strip --strip-unneeded "${binary}"
elif [[ "$(uname -s)" == "Darwin" ]]; then
    strip -S -x "${binary}"
fi

[[ "$("${binary}" --version)" == "${VERSION}" ]] ||
    fail "The executable version does not match ${VERSION}."
"${binary}" --help >/dev/null
"${SCRIPT_DIR}/audit-release-content.sh" binary "${binary}"

if [[ "$(uname -s)" == "Linux" ]]; then
    readelf -d "${binary}" >.build/release-elf-dynamic-section.txt
    if grep -E 'NEEDED.*(libswift|libFoundation|libdispatch|libBlocksRuntime)' \
        .build/release-elf-dynamic-section.txt; then
        fail "The executable still requires a Swift runtime shared library."
    fi
fi

[[ -z "$(git status --short)" ]] ||
    fail "Release checks changed the working tree."

printf 'cidrmerge %s release checks passed.\n' "${VERSION}"
