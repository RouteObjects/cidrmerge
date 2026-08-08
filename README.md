# cidrmerge

`cidrmerge` is an offline policy compiler and reusable Swift library. It turns
IPv4 and IPv6 addresses, networks, and inclusive ranges into a deterministic,
minimal exact address cover. It uses
[`swift-cidr`](https://github.com/RouteObjects/swift-cidr) as the canonical
source for IP parsing, normalization, containment, network construction, and
range-to-CIDR summarization.

The compiler is intended for admission policies, ACL preparation, and other
control-plane pipelines. It coalesces only duplicate, contained, overlapping,
or adjacent coverage; it never fills an uncovered gap to make output shorter.

## Requirements

- Swift 6.1 or newer when building from source or using the `CIDRMergeCore`
  library through SwiftPM
- macOS 15 or newer, or Ubuntu 22.04 or newer, to run the command-line
  executable
- iOS 18 or newer when using `CIDRMergeCore` in an application

The package is verified against the declared compatibility floors of
`swift-cidr` 0.5.0, Swift Argument Parser 1.7.0, and Swift Crypto 4.5.1.
`Package.resolved` records the exact dependency revisions used for release
verification. Swift Crypto is used only by the CLI artifact boundary;
`CIDRMergeCore` does not import or link it.

## Install a release archive

GitHub Releases provide native archives for macOS and Linux on ARM64 and
x86-64. Select the archive for the current host, download it together with the
published checksum file, and verify it before installation:

```sh
version=0.1.0
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)  platform=darwin-aarch64 ;;
  Darwin-x86_64) platform=darwin-x86_64 ;;
  Linux-aarch64) platform=linux-aarch64 ;;
  Linux-x86_64)  platform=linux-x86_64 ;;
  *) printf 'Unsupported host: %s-%s\n' "$(uname -s)" "$(uname -m)" >&2; exit 1 ;;
esac

asset="cidrmerge-${version}-${platform}.tar.gz"
base_url="https://github.com/RouteObjects/cidrmerge/releases/download/${version}"
curl --fail --location --remote-name "${base_url}/${asset}"
curl --fail --location --remote-name "${base_url}/SHA256SUMS"

awk -v name="${asset}" '$2 == name' SHA256SUMS >"${asset}.sha256"
test -s "${asset}.sha256"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum --check "${asset}.sha256"
else
  shasum -a 256 --check "${asset}.sha256"
fi
```

Extract the verified archive and install the executable in a directory on
`PATH`:

```sh
stage="cidrmerge-${version}"
mkdir "${stage}"
tar -C "${stage}" -xzf "${asset}"
mkdir -p "${HOME}/.local/bin"
install -m 0755 "${stage}/cidrmerge" "${HOME}/.local/bin/cidrmerge"
"${HOME}/.local/bin/cidrmerge" --version
```

Each archive also contains `LICENSE` and `THIRD_PARTY_NOTICES.txt`. Review and
retain those files with redistributed copies of the executable.

## Build from source

Clone the repository and build a release executable:

```sh
git clone https://github.com/RouteObjects/cidrmerge.git
cd cidrmerge
swift build -c release --product cidrmerge
.build/release/cidrmerge --version
```

Run the test suite and executable smoke test with:

```sh
./scripts/test.sh
./scripts/smoke-test.sh
```

The SwiftPM executable product, source-built binary, and command are all named
`cidrmerge`.

## Command-line usage

With no file operands, `cidrmerge` reads the selected input grammar from
standard input. RouteObjects IP List Text v1 is the default. For example:

```sh
printf '%s\n' \
  192.0.2.0/25 \
  192.0.2.128/25 \
  2001:0DB8::1/64 \
  | cidrmerge --stats
```

Standard output contains IPv4 first and IPv6 second:

```text
192.0.2.0...192.0.2.255
2001:db8::...2001:db8::ffff:ffff:ffff:ffff
```

Statistics are written to standard error, keeping standard output safe for a
pipeline:

```text
input: 3 entries (2 IPv4, 1 IPv6)
normalized: 1 entry
output: 2 ranges (1 IPv4, 1 IPv6)
reduction: 1 entry (33.3%)
```

### Input formats and semantics

`--input-format text|searchbot` selects one grammar for every operand in an
invocation. The default `text` grammar accepts:

- A bare IPv4 address means one `/32`; a bare IPv6 address means one `/128`.
- Slash-qualified input has network semantics. For example,
  `192.0.2.129/24` canonicalizes to the coverage of `192.0.2.0/24`.
- An inclusive range uses exactly `lower...upper`, with address-only endpoints
  from the same family. Reversed bounds and CIDR-qualified endpoints are
  rejected.
- Blank lines and `#` comments are ignored.
- Additional BGP or RPKI columns are rejected rather than silently discarded.
- Pass local files as operands. Use `-` at most once to combine standard input
  with files.
- HTTP and HTTPS operands are rejected. Download changing inputs separately
  with `curl`, CI tooling, or another acquisition step.

The `searchbot` grammar accepts the complete UTF-8 Google/Bing/Apple/OpenAI-
compatible crawler-prefix JSON shape. It names a de facto compatible grammar,
not a formal standard, provider identity check, or generic vendor decoder. The
top-level object must contain a `prefixes` array. Each entry must contain exactly
one string-valued `ipv4Prefix` or `ipv6Prefix` matching the declared family.
Unknown top-level and entry metadata are ignored so publishers can add
descriptive fields without changing the address-list contract.

```json
{
  "creationTime": "2026-01-01T00:00:00Z",
  "prefixes": [
    { "ipv4Prefix": "192.0.2.0/24" },
    { "ipv6Prefix": "2001:db8::/32" }
  ]
}
```

`creationTime` and other unknown metadata are ignored. The prefix values above
use addresses reserved for documentation.

Download vendor data explicitly, then compile the saved file offline:

```sh
curl --fail --location \
  --output common-crawlers.json \
  https://developers.google.com/static/crawling/ipranges/common-crawlers.json

cidrmerge --input-format searchbot \
  --raw --representation ranges --stats \
  common-crawlers.json
```

Every searchbot operand is one complete document; NDJSON, concatenated JSON
documents, malformed or trailing JSON, missing/ambiguous/duplicate
policy-bearing members, non-string values, wrong-family prefixes, and invalid
networks fail the whole operation. Diagnostics identify the source and JSON
path such as `$.prefixes[2].ipv6Prefix`. An empty `prefixes` array is valid.
JSON container nesting is limited to 128 levels. Statistics count extracted
prefix values and their canonicalization, not documents or metadata.

Every accepted value becomes an inclusive first-to-last address interval.
Intervals are partitioned by family, numerically sorted, and coalesced. This
retains exact address membership rather than input provenance: original prefix
lengths and fragmentation cannot be reconstructed after union.

### Representations and serialization

The default `ranges` representation emits the fewest disjoint closed intervals
needed to express the exact union. Request canonical CIDR output explicitly:

```sh
printf '%s\n' 192.168.2.2/31 192.168.2.4/30 \
  | cidrmerge --representation cidr
```

```text
192.168.2.2/31
192.168.2.4/30
```

`--representation ranges|cidr` selects coverage representation. This is
orthogonal to serialization:

- Raw line-oriented output is the default; `--raw` selects it explicitly.
- `--json` or `-j` emits structured JSON.
- `--raw` and `--json` are mutually exclusive.
- `--input-format text|searchbot` selects one input grammar for all operands.
- `-o, --output <path>` atomically replaces a file instead of writing stdout.
- `--checksum` requires `--output` and writes a detached SHA-256 checksum file.
- `--stats` reports statistics for the selected representation on stderr.
- `--version` prints the release version. `-v` is intentionally unassigned.

JSON records the selected representation and preserves separate, deterministic
family arrays:

```json
{
  "ipv4" : [
    "192.0.2.0/24"
  ],
  "ipv6" : [
    "2001:db8::/32"
  ],
  "representation" : "cidr"
}
```

### Detached SHA-256 checksums

`--checksum` writes a detached SHA-256 checksum file at
`<output-path>.sha256` for either raw or JSON output. It hashes the exact
rendered bytes, including the final line feed normally emitted by both
serializers. Empty raw output is zero bytes and uses SHA-256's standard
empty-input digest.

```sh
cidrmerge --input-format searchbot --raw \
  --representation ranges --stats --checksum \
  --output allow.ranges.txt common-crawlers.json
```

The companion `allow.ranges.txt.sha256` contains exactly one record:

```text
<64 lowercase hexadecimal characters><two spaces>allow.ranges.txt<LF>
```

Only the output basename is recorded. Basenames containing carriage return or
line feed are rejected, and invalid checksum/output combinations fail before
cidrmerge reads input. Run standard verification from the output file's parent
directory so the recorded basename resolves to the generated file:

```sh
sha256sum --check allow.ranges.txt.sha256      # Linux
shasum -a 256 --check allow.ranges.txt.sha256 # macOS
```

cidrmerge renders and hashes before touching either destination, atomically
replaces the detached checksum file first, and atomically replaces the output
second. The two paths cannot be one filesystem transaction: if the second
replacement fails, the new checksum intentionally does not match the old or
missing output, so a consumer requiring verification fails closed. Deploy
immutable or versioned directories and switch generations outside cidrmerge
when pair-level rollout atomicity is required.

Detached checksum verification detects a mismatch between the recorded digest
and output bytes; it does not authenticate the file's origin, verify a
crawler's identity, or bind independent allow and deny files into one
generation. Raw text remains the direct admission interchange; a checksum does
not make cidrmerge's JSON schema an admission-policy format.

Output is buffered until all input has parsed, merged, and rendered, so a
failure in those stages emits no standard output. File destinations are
atomically replaced where supported, and standard-output write failures are
surfaced even though a stream write cannot be rolled back.

## Library usage

Add `cidrmerge` and `swift-cidr` to another Swift package:

```swift
dependencies: [
    .package(
        url: "https://github.com/RouteObjects/cidrmerge.git",
        .upToNextMinor(from: "0.2.0")
    ),
    .package(
        url: "https://github.com/RouteObjects/swift-cidr.git",
        .upToNextMinor(from: "0.5.0")
    ),
],
targets: [
    .target(
        name: "MyTarget",
        dependencies: [
            .product(name: "CIDRMergeCore", package: "cidrmerge"),
            .product(name: "CIDR", package: "swift-cidr"),
        ]
    ),
]
```

Applications use `swift-cidr` values directly, so declare its package and
`CIDR` product explicitly instead of relying on a transitive dependency.

`swift-cidr` owns `IPAddressRange<Family>`, `AnyIPAddressRange`, and
`IPAddressCoverage<Family>`. The family-bound coverage type normalizes any
sequence of intervals into an immutable exact union and provides logarithmic
containment lookup.

Inside a throwing context, handle textual configuration errors explicitly:

```swift
import CIDR
import CIDRMergeCore

enum PolicyInputError: Error {
    case invalidValue(String)
}

func parseIPv4Network(_ text: String) throws -> IPv4Network {
    guard let network = IPv4Network(text) else {
        throw PolicyInputError.invalidValue(text)
    }
    return network
}

func parseIPv4Address(_ text: String) throws -> IPv4Address {
    guard let address = IPv4Address(text) else {
        throw PolicyInputError.invalidValue(text)
    }
    return address
}

func parseRange(_ text: String) throws -> AnyIPAddressRange {
    guard let range = AnyIPAddressRange(text) else {
        throw PolicyInputError.invalidValue(text)
    }
    return range
}

let prefixes = try ["192.0.2.0/25", "192.0.2.128/26"].map {
    try parseIPv4Network($0)
}
let coverage = IPAddressCoverage(covering: prefixes)

coverage.ranges.map(\.description)
// ["192.0.2.0...192.0.2.191"]

coverage.summarizedNetworks().map(\.description)
// ["192.0.2.0/25", "192.0.2.128/26"]

coverage.contains(try parseIPv4Address("192.0.2.190")) // true
coverage.contains(try parseIPv4Address("192.0.2.192")) // false
```

`IPAddressRange.summarizedNetworks()` and
`IPAddressCoverage.summarizedNetworks()` delegate CIDR decomposition to
`swift-cidr`. They guarantee the same address membership, not the same prefix
lengths as the input. `AnyIPAddressRange` is the family-erased boundary for
parsing or mixed-family collections; keep algorithms family-bound when the
family is known statically.

`CIDRMergeCoverage` is cidrmerge's mixed-family facade. It normalizes each
family independently and always exposes IPv4 before IPv6:

```swift
let mixedRanges = try [
    "2001:db8::...2001:db8::ffff",
    "192.0.2.0...192.0.2.191",
].map { try parseRange($0) }
let mixed = CIDRMergeCoverage(ranges: mixedRanges)

mixed.ranges.map(\.description)
// ["192.0.2.0...192.0.2.191", "2001:db8::...2001:db8::ffff"]

mixed.summarizedNetworks().map(\.description)
// ["192.0.2.0/25", "192.0.2.128/26", "2001:db8::/112"]

mixed.contains(AnyIPAddress(try parseIPv4Address("192.0.2.190"))) // true
```

Beginning with the 0.2 line, `CIDRMergeCore` no longer provides the range and
coverage types that it declared in 0.1. Import `CIDR` and use the canonical
swift-cidr declarations directly. This deliberate pre-1.0 source break keeps
one owner for address, network, range, containment, normalization, and
summarization behavior.

## Routing and RPKI data

`cidrmerge` operates on address coverage only. Range output is optimized for
containment indexes, not route advertisement. Before using BGP- or
RPKI-derived data, explicitly project it to prefixes. The output is not a route
advertisement or ROA and does not preserve ASN, AS path, community,
`maxLength`, TAL, source, or validation state.

The compiler is deliberately offline. `--input-format searchbot` parses saved
local files or standard input but never fetches them. Vendor feed acquisition,
DNS, IRRd/RPKI queries, admission-policy hot reload, named vendor policy
generation, and admission-policy serialization remain outside this package
boundary.

## Performance

Run deterministic end-to-end corpora with:

```sh
CIDRMERGE_BENCHMARK_COUNT=10000 ./scripts/benchmark.sh siblings bgp-like
```

The release acceptance run uses one million inputs per scenario and a 512 MiB
peak-RSS ceiling. [Benchmarks/README.md](Benchmarks/README.md) records timing,
memory, output cardinality, compression, and the dated Google common-crawler
example. That 2026-07-13 snapshot compiled 315 prefixes to 38 ranges or 65 CIDR
prefixes without changing address coverage; live vendor data can change.

## RouteObjects ecosystem

`cidrmerge` is part of the [RouteObjects](https://github.com/RouteObjects)
**Swift for Network Infrastructure** toolkit:

- [swift-cidr](https://github.com/RouteObjects/swift-cidr) — Strongly typed IP
  address, network, and CIDR primitives for Swift.
- [asroutes](https://github.com/RouteObjects/asroutes) — SwiftNIO IRRd client and
  CLI for direct-ASN IPv4 and IPv6 origin-route lookups.
- [cidrmerge](https://github.com/RouteObjects/cidrmerge) — Deterministic exact
  coverage compilation into minimal address-range or CIDR representations.
- [swift-cidr-admission](https://github.com/RouteObjects/swift-cidr-admission) —
  CIDR-based admission policies for Swift services.
- [cidrwalk](https://github.com/RouteObjects/cidrwalk) — Address-range and CIDR
  traversal and inspection utility.

## License

`cidrmerge` is available under the Apache License 2.0. See [LICENSE](LICENSE).
Resolved dependency and binary-runtime attribution information is recorded in
[THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt).
