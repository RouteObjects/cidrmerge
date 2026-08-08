#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CATALOG_PATH="${PACKAGE_ROOT}/Sources/CIDRMergeCore/CIDRMergeCore.docc"

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

documentation_temporary_directory="$(
    mktemp -d "${TMPDIR:-/tmp}/cidrmerge-documentation-check.XXXXXX"
)"
cleanup() {
    rm -rf -- "${documentation_temporary_directory}"
}
trap cleanup EXIT

cd "${PACKAGE_ROOT}"

[[ -f "${CATALOG_PATH}/CIDRMergeCore.md" ]] ||
    fail "CIDRMergeCore documentation landing page is missing."
[[ -f "${CATALOG_PATH}/CompilingSearchbotPrefixLists.md" ]] ||
    fail "Searchbot workflow article is missing."

symbol_graph_directory="${documentation_temporary_directory}/symbol-graphs"
mkdir -p "${symbol_graph_directory}"

# CHANGE: Use the same public symbol graph as hosted CIDRMergeCore documentation on every host.
swift build \
    --target CIDRMergeCore \
    -Xswiftc -emit-symbol-graph \
    -Xswiftc -emit-symbol-graph-dir \
    -Xswiftc "${symbol_graph_directory}" \
    -Xswiftc -symbol-graph-minimum-access-level \
    -Xswiftc public

symbol_graph="${symbol_graph_directory}/CIDRMergeCore.symbols.json"
[[ -s "${symbol_graph}" ]] ||
    fail "CIDRMergeCore did not emit a public symbol graph."
grep -Eq '"name"[[:space:]]*:[[:space:]]*"CIDRMergeCore"' "${symbol_graph}" ||
    fail "CIDRMergeCore symbol graph does not identify its module."
grep -Eq '"title"[[:space:]]*:[[:space:]]*"CIDRMergeCoverage"' "${symbol_graph}" ||
    fail "CIDRMergeCore symbol graph does not contain CIDRMergeCoverage."

case "$(uname -s)" in
Darwin)
    documentation_archive="${documentation_temporary_directory}/CIDRMergeCore.doccarchive"
    docc_symbol_graph_directory="${documentation_temporary_directory}/docc-symbol-graphs"
    mkdir -p "${docc_symbol_graph_directory}"
    cp "${symbol_graph}" "${docc_symbol_graph_directory}/"

    # CHANGE: Convert directly with the installed Xcode DocC so documentation validation adds
    # no package dependency. Isolating the Core graph prevents dependency modules from becoming
    # accidental documentation roots, and warnings are release failures.
    xcrun docc convert "${CATALOG_PATH}" \
        --additional-symbol-graph-dir "${docc_symbol_graph_directory}" \
        --output-path "${documentation_archive}" \
        --fallback-display-name CIDRMergeCore \
        --fallback-bundle-identifier org.routeobjects.cidrmerge.core \
        --fallback-default-module-kind Library \
        --warnings-as-errors

    [[ -d "${documentation_archive}" ]] ||
        fail "DocC did not create CIDRMergeCore.doccarchive."
    [[ -s "${documentation_archive}/metadata.json" ]] ||
        fail "CIDRMergeCore documentation archive metadata is missing."

    module_page="$(
        find "${documentation_archive}/data/documentation" \
            -type f -name 'cidrmergecore.json' -print -quit
    )"
    [[ -n "${module_page}" && -s "${module_page}" ]] ||
        fail "CIDRMergeCore documentation archive does not contain the module page."

    searchbot_article="$(
        find "${documentation_archive}/data/documentation" \
            -type f -name 'compilingsearchbotprefixlists.json' -print -quit
    )"
    [[ -n "${searchbot_article}" && -s "${searchbot_article}" ]] ||
        fail "CIDRMergeCore documentation archive does not contain the searchbot article."
    ;;
Linux)
    ;;
*)
    fail "Unsupported documentation-check host: $(uname -s)"
    ;;
esac

printf 'CIDRMergeCore documentation checks passed.\n'
