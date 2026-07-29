# cidrmerge Benchmarks

The benchmark harness builds `cidrmerge` in release mode, generates deterministic
line-oriented corpora, and measures the complete text-input-to-text-output pipeline
for both `ranges` and `cidr` representations. Each generated fixture is reused
unchanged for both representation runs. Generated fixtures live only in a temporary
directory.

```bash
./scripts/benchmark.sh
```

The default corpus size is one million records and the default peak-RSS limit is
512 MiB. Override them when doing smaller development runs:

```bash
CIDRMERGE_BENCHMARK_COUNT=10000 ./scripts/benchmark.sh siblings bgp-like
CIDRMERGE_MAX_RSS_KB=262144 ./scripts/benchmark.sh
```

The BGP-like and RPKI-like inputs are deterministic synthetic prefix-length
distributions. `arbitrary-ranges` exercises range-to-CIDR expansion, while
`overlapping-ranges` exercises heavy coalescing. These corpora contain no operational
routing or authorization data.

## Initial Baseline

Captured 2026-07-11 on arm64 macOS 26.5.2 with Swift 6.3.2. Each row is a
complete one-million-record text-input-to-text-output run.

| Corpus | Wall time | Throughput | Peak RSS |
|---|---:|---:|---:|
| disjoint | 2.03 s | 492,611 records/s | 60,256 KiB |
| siblings | 2.42 s | 413,223 records/s | 49,264 KiB |
| subsumed | 1.33 s | 751,880 records/s | 47,504 KiB |
| bgp-like | 1.71 s | 584,795 records/s | 55,040 KiB |
| rpki-like | 1.61 s | 621,118 records/s | 52,144 KiB |
| mixed | 2.29 s | 436,681 records/s | 110,528 KiB |

All corpora remained below the 512 MiB Phase 1 acceptance ceiling.

This table predates the range engine and remains the CIDR-mode regression baseline.

## 0.1.0 Release Candidate

Captured 2026-07-28 on arm64 macOS 26.6 with Swift 6.3.3. Each row processes one
million inputs. CIDR output delegates each coalesced interval to swift-cidr's
existing summarizer.

| Corpus | Ranges time | Ranges RSS | CIDR time | CIDR RSS |
|---|---:|---:|---:|---:|
| disjoint | 1.07 s | 82,000 KiB | 1.40 s | 69,712 KiB |
| siblings | 0.78 s | 49,536 KiB | 0.79 s | 48,832 KiB |
| subsumed | 0.78 s | 47,472 KiB | 0.78 s | 47,872 KiB |
| bgp-like | 1.07 s | 52,176 KiB | 1.13 s | 59,776 KiB |
| rpki-like | 0.97 s | 50,240 KiB | 1.01 s | 52,160 KiB |
| mixed | 1.30 s | 144,512 KiB | 1.64 s | 134,960 KiB |
| arbitrary-ranges | 2.39 s | 96,480 KiB | 3.13 s | 114,848 KiB |
| overlapping-ranges | 2.25 s | 63,968 KiB | 2.27 s | 63,872 KiB |

All scenarios remain below 512 MiB. On the six original corpora, CIDR mode is
faster than the recorded Phase 1 baseline; the 15% regression ceiling therefore
passes with margin.

## Output Cardinality and Compression

Timing and peak RSS measure the cost of compiling an input. Output cardinality
measures the size of the resulting coverage list that a downstream consumer such
as `swift-cidr-admission` must index and search. The following results use the same
one-million-record fixtures as the release-candidate measurements above.

Compression is `input records / output entries`, so a larger value is more compact.
A value below `1x` indicates that an exact CIDR representation expanded the input.
Range reduction is `(CIDR entries - range entries) / CIDR entries` and measures the
additional entry-count reduction obtained by representing the same coverage as
closed address ranges.

| Corpus | Range entries | Range compression | CIDR entries | CIDR compression | Range reduction |
|---|---:|---:|---:|---:|---:|
| disjoint | 1,000,000 | 1.00x | 1,000,000 | 1.00x | 0.0% |
| siblings | 1 | 1,000,000x | 7 | 142,857x | 85.7% |
| subsumed | 1 | 1,000,000x | 1 | 1,000,000x | 0.0% |
| bgp-like | 193,255 | 5.17x | 233,532 | 4.28x | 17.2% |
| rpki-like | 49,483 | 20.21x | 61,444 | 16.27x | 19.5% |
| mixed | 1,000,000 | 1.00x | 1,000,000 | 1.00x | 0.0% |
| arbitrary-ranges | 1,000,000 | 1.00x | 2,000,000 | 0.50x | 50.0% |
| overlapping-ranges | 1 | 1,000,000x | 8 | 125,000x | 87.5% |

Ranges do not reduce cardinality for already disjoint coverage. They are most
effective for dense adjacent prefix walls and intervals whose endpoints do not
align to a single canonical CIDR block. The synthetic BGP-like and RPKI-like
fixtures show a moderate cardinality benefit, but they model address coverage only;
they do not imply that route attributes or authorization semantics can be merged.

## Operational Feed Example

The official [Google common-crawler feed](https://developers.google.com/static/crawling/ipranges/common-crawlers.json)
is a useful example of dense bot/indexer coverage. The feed snapshot created at
`2026-07-13T14:46:17Z` contained 315 prefixes: 169 IPv4 and 146 IPv6.

| Representation | IPv4 entries | IPv6 entries | Total entries | Compression |
|---|---:|---:|---:|---:|
| ranges | 29 | 9 | 38 | 8.29x |
| CIDR | 41 | 24 | 65 | 4.85x |

For this snapshot, ranges represent the same coverage with 41.5% fewer entries.
This is a dated operational example rather than a regression fixture; the live feed
can change independently of `cidrmerge`.
