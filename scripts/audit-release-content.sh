#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

audit_temporary_file=""
audit_filtered_file=""

cleanup() {
    if [[ -n "${audit_temporary_file}" ]]; then
        rm -f -- "${audit_temporary_file}"
    fi
    if [[ -n "${audit_filtered_file}" ]]; then
        rm -f -- "${audit_filtered_file}"
    fi
}

trap cleanup EXIT

# Build expressions from fragments so this audit script never satisfies its
# own searches. Keep matches out of logs because a match may itself be secret.
local_package="[.]package[[:space:]]*[(][[:space:]]*path[[:space:]]*:"
local_resolution='"kind"[[:space:]]*:[[:space:]]*"lo'""'cal'
ssh_dependency="git""@github[.]com"
file_url="file:""///"

mac_home="/""Users/"
linux_home="/""home/[^/]+/"
private_var="/""private/var/"

private_key="-----BE""GIN (OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----"
aws_key="(A""KIA|A""SIA)[0-9A-Z]{16}"
github_token="gh""[pousr]_[A-Za-z0-9]{20,}"
github_pat="github""_pat_[A-Za-z0-9_]{20,}"
slack_token="xo""x[baprs]-[A-Za-z0-9-]{20,}"
api_key="sk""-(live|proj)-[A-Za-z0-9_-]{16,}"

audit_tracked_tree() {
    local actual_direct_dependencies
    local actual_resolved_dependencies
    local expected_direct_dependencies
    local expected_resolved_dependencies
    local status

    # CHANGE: Allowlist the public dependency graph rather than merely rejecting
    # path and SSH forms; an unexpected HTTPS fork must fail the release audit too.
    expected_direct_dependencies=$'https://github.com/RouteObjects/swift-cidr.git\nhttps://github.com/apple/swift-argument-parser'
    actual_direct_dependencies="$(
        sed -nE 's/.*url:[[:space:]]*"([^"]+)".*/\1/p' \
            "${PACKAGE_ROOT}/Package.swift" | LC_ALL=C sort
    )"
    [[ "${actual_direct_dependencies}" == "${expected_direct_dependencies}" ]] ||
        fail "Package.swift contains an unexpected direct dependency URL."

    expected_resolved_dependencies=$'https://github.com/RouteObjects/swift-cidr.git\nhttps://github.com/apple/swift-argument-parser\nhttps://github.com/apple/swift-atomics.git\nhttps://github.com/apple/swift-collections.git\nhttps://github.com/apple/swift-nio.git\nhttps://github.com/apple/swift-system.git'
    actual_resolved_dependencies="$(
        awk -F '"' '/"location"/ { print $4 }' \
            "${PACKAGE_ROOT}/Package.resolved" | LC_ALL=C sort
    )"
    [[ "${actual_resolved_dependencies}" == "${expected_resolved_dependencies}" ]] ||
        fail "Package.resolved contains an unexpected dependency location."

    # CHANGE: Public release manifests must resolve through canonical HTTPS URLs,
    # never a developer-local path, file URL, or SSH credential context.
    if git -C "${PACKAGE_ROOT}" grep --quiet -I -E \
        -e "${local_package}" \
        -e "${local_resolution}" \
        -e "${ssh_dependency}" \
        -e "${file_url}" \
        -- Package.swift Package.resolved; then
        fail "The package dependency graph contains a local or credential-bound source."
    else
        status=$?
        [[ ${status} -eq 1 ]] || fail "Unable to audit package dependency sources."
    fi

    if git -C "${PACKAGE_ROOT}" grep --quiet -I -E \
        -e "${mac_home}" \
        -e "${linux_home}" \
        -e "${private_var}" \
        -e "${file_url}" \
        -- .; then
        fail "Tracked files contain a local absolute path."
    else
        status=$?
        [[ ${status} -eq 1 ]] || fail "Unable to audit tracked local paths."
    fi

    if git -C "${PACKAGE_ROOT}" grep --quiet -I -E \
        -e "${private_key}" \
        -e "${aws_key}" \
        -e "${github_token}" \
        -e "${github_pat}" \
        -e "${slack_token}" \
        -e "${api_key}" \
        -- .; then
        fail "Tracked files contain a credential or private-key marker."
    else
        status=$?
        [[ ${status} -eq 1 ]] || fail "Unable to audit tracked sensitive markers."
    fi
}

audit_binary() {
    local binary="$1"
    local path_pattern
    local raw_path_pattern
    local status
    local upstream_runtime_path
    local upstream_toolchain_path

    [[ -f "${binary}" ]] || fail "Binary not found: ${binary}"
    command -v strings >/dev/null 2>&1 || fail "Required command not found: strings"

    audit_temporary_file="$(mktemp)"
    audit_filtered_file="$(mktemp)"
    # Inspect every data section consistently on Darwin and Linux; the default
    # Apple `strings` selection omits Mach-O sections that GNU `strings` examines.
    LC_ALL=C strings -a "${binary}" >"${audit_temporary_file}"

    # Static Swift runtime archives contain source locations from the official
    # toolchain build. They are public upstream paths rather than runner paths.
    upstream_toolchain_path="^/""home/build-user/swift(-experimental-string-processing)?/"
    # Static Foundation contains this literal system lookup path on Linux; it
    # is runtime behavior, not a path to the source tree or release runner.
    upstream_runtime_path="^/""private/var/automount/$"
    grep -E -v \
        -e "${upstream_toolchain_path}" \
        -e "${upstream_runtime_path}" \
        "${audit_temporary_file}" >"${audit_filtered_file}"

    path_pattern="(${mac_home}|${linux_home}|${private_var}|/workspace(/|$)|/github/workspace(/|$)|/__w/|/builds?(/|$)|/runner/_work/|[.]build/)"
    if grep --quiet -E "${path_pattern}" "${audit_filtered_file}"; then
        fail "Release binary contains a workspace, home, or build path."
    else
        status=$?
        [[ ${status} -eq 1 ]] || fail "Unable to audit release binary paths."
    fi

    # Apple's `strings` does not inspect every Mach-O section that GNU `strings`
    # examines. Keep an unfiltered byte scan for path families without reviewed
    # static-runtime exceptions.
    raw_path_pattern="(${mac_home}|/workspace(/|$)|/github/workspace(/|$)|/__w/|/builds?(/|$)|/runner/_work/|[.]build/)"
    if LC_ALL=C grep -a --quiet -E "${raw_path_pattern}" "${binary}"; then
        fail "Release binary contains a workspace, home, or build path."
    else
        status=$?
        [[ ${status} -eq 1 ]] || fail "Unable to audit raw release binary paths."
    fi

    if grep --quiet -E \
        -e "${private_key}" \
        -e "${aws_key}" \
        -e "${github_token}" \
        -e "${github_pat}" \
        -e "${slack_token}" \
        -e "${api_key}" \
        "${audit_temporary_file}"; then
        fail "Release binary contains a credential or private-key marker."
    else
        status=$?
        [[ ${status} -eq 1 ]] || fail "Unable to audit release binary markers."
    fi

    cleanup
    audit_temporary_file=""
    audit_filtered_file=""
}

case "${1:-}" in
tree)
    [[ $# -eq 1 ]] || fail "Usage: audit-release-content.sh tree"
    audit_tracked_tree
    ;;
binary)
    [[ $# -eq 2 ]] || fail "Usage: audit-release-content.sh binary PATH"
    audit_binary "$2"
    ;;
*)
    fail "Usage: audit-release-content.sh {tree|binary PATH}"
    ;;
esac
