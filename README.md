# cidrmerge

`cidrmerge` compiles IPv4 and IPv6 addresses and networks into the shortest
sorted prefix list that covers exactly the same address space. It uses
[`swift-cidr`](https://github.com/RouteObjects/swift-cidr) for parsing,
canonicalization, containment, and network construction.

The command is intended for admission policies, ACL preparation, and other
offline control-plane pipelines. It never widens coverage to make the output
shorter.

## Example

```bash
printf '%s\n' \
  192.0.2.0/25 \
  192.0.2.128/25 \
  2001:0DB8::1/64 \
  | cidrmerge --stats
```

```text
192.0.2.0/24
2001:db8::/64
```

Statistics are written to stderr, keeping stdout pipeline-safe:

```text
input: 3 prefixes (2 IPv4, 1 IPv6)
normalized: 1 prefix
output: 2 prefixes (1 IPv4, 1 IPv6)
reduction: 1 prefix (33.3%)
```

## Input Semantics

Phase 1 reads line-oriented text from stdin or local files.

- A bare IPv4 address means one `/32`; a bare IPv6 address means one `/128`.
- Slash-qualified input has network semantics. For example,
  `192.0.2.129/24` canonicalizes to `192.0.2.0/24`.
- Blank lines and `#` comments are ignored.
- Additional BGP or RPKI columns are rejected rather than silently discarded.
- Use `-` at most once to combine stdin with local files.

Two canonical CIDR prefixes in one family are either disjoint, identical, or
one contains the other. cidrmerge removes contained prefixes and recursively
combines only aligned siblings. Adjacent prefixes remain separate when one
parent cannot represent their union exactly.

## Usage

```text
USAGE: cidrmerge [--input-format <input-format>] [--output-format <output-format>] [--json] [--stats] [--output <output>] [--version] [<input> ...]
```

- `--output-format text|json` selects output; text is the default.
- `--json` is a short alias for JSON output and cannot be combined with
  `--output-format`.
- JSON uses separate deterministic `ipv4` and `ipv6` arrays.
- `-o, --output` atomically writes a file instead of stdout.
- `-v, --version` prints the version.

URL input, vendor `searchbot` JSON, and admission-policy output are planned
for 0.2.0.

## Phase 0 Vendor Result

A dated 2026-07-10 capture of Google's common-crawlers feed contained 315
prefixes and collapsed to 65 exact prefixes, a 79.4% reduction. Vendor feeds
change, so this metric will be recaptured before release documentation freezes.

## Build and Test

```bash
swift build
./scripts/test.sh
```

The test wrapper adds Swift Testing framework paths only when standalone
Command Line Tools require them.

Run deterministic end-to-end performance corpora with:

```bash
CIDRMERGE_BENCHMARK_COUNT=10000 ./scripts/benchmark.sh siblings bgp-like
```

The release acceptance run uses one million records and a 512 MiB peak-RSS
ceiling.

## Routing and RPKI Data

`cidrmerge` operates on address coverage only. Before using BGP- or
RPKI-derived data, explicitly project it to prefixes. The output is not a route
advertisement or ROA and does not preserve ASN, AS path, `maxLength`, TAL, or
validation state.
