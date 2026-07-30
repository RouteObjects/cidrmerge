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

The initial release is verified against the declared compatibility floors of
`swift-cidr` 0.4.0 and Swift Argument Parser 1.7.0. `Package.resolved` records
the exact dependency revisions used for release verification.

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

With no file operands, `cidrmerge` reads line-oriented text from standard
input. For example:

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

### Input semantics

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
- `-o, --output <path>` atomically replaces a file instead of writing stdout.
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
        .upToNextMinor(from: "0.1.0")
    ),
    .package(
        url: "https://github.com/RouteObjects/swift-cidr.git",
        .upToNextMinor(from: "0.4.0")
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

`IPAddressRange<Family>` represents one inclusive, family-bound interval.
`IPAddressCoverage<Family>` normalizes any sequence of those intervals into an
immutable exact union and provides logarithmic containment lookup:

```swift
import CIDR
import CIDRMergeCore

let prefixes = [
    IPv4Network("192.0.2.0/25")!,
    IPv4Network("192.0.2.128/26")!,
]
let coverage = IPAddressCoverage(covering: prefixes)

coverage.ranges.map(\.description)
// ["192.0.2.0...192.0.2.191"]

coverage.summarizedNetworks().map(\.description)
// ["192.0.2.0/25", "192.0.2.128/26"]

coverage.contains(IPv4Address("192.0.2.190")!) // true
coverage.contains(IPv4Address("192.0.2.192")!) // false
```

`IPAddressRange.summarizedNetworks()` and
`IPAddressCoverage.summarizedNetworks()` delegate CIDR decomposition to
`swift-cidr`. They guarantee the same address membership, not the same prefix
lengths as the input. `AnyIPAddressRange` is the family-erased boundary for
parsing or mixed-family collections; keep algorithms family-bound when the
family is known statically.

## Routing and RPKI data

`cidrmerge` operates on address coverage only. Range output is optimized for
containment indexes, not route advertisement. Before using BGP- or
RPKI-derived data, explicitly project it to prefixes. The output is not a route
advertisement or ROA and does not preserve ASN, AS path, community,
`maxLength`, TAL, source, or validation state.

The compiler is deliberately offline. Vendor feed acquisition, DNS, IRRd/RPKI
queries, admission-policy hot reload, and named vendor policy generation do not
belong in the 0.1 package boundary. Local-file and stdin parsing for a future
`searchbot` schema and admission-policy output remain 0.2 design work.

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
