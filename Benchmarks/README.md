# cidrmerge Benchmarks

The benchmark harness builds `cidrmerge` in release mode, generates deterministic
line-oriented corpora, and measures the complete text-input-to-text-output pipeline
for both `ranges` and `cidr` representations. Generated fixtures live only in a
temporary directory.

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

## Range Engine Candidate

Captured 2026-07-12 on the same arm64 macOS 26.5.2 / Swift 6.3.2 system. Each
row processes one million inputs. CIDR output delegates each coalesced interval
to swift-cidr's existing summarizer.

| Corpus | Ranges time | Ranges RSS | CIDR time | CIDR RSS |
|---|---:|---:|---:|---:|
| disjoint | 1.04 s | 82,736 KiB | 1.40 s | 68,112 KiB |
| siblings | 0.79 s | 49,552 KiB | 0.79 s | 49,568 KiB |
| subsumed | 0.79 s | 48,160 KiB | 0.81 s | 48,176 KiB |
| bgp-like | 1.01 s | 52,480 KiB | 1.10 s | 59,792 KiB |
| rpki-like | 0.96 s | 50,960 KiB | 0.97 s | 52,592 KiB |
| mixed | 1.28 s | 144,208 KiB | 1.62 s | 134,496 KiB |
| arbitrary-ranges | 2.40 s | 96,480 KiB | 3.19 s | 113,648 KiB |
| overlapping-ranges | 2.25 s | 63,968 KiB | 2.25 s | 64,032 KiB |

All scenarios remain below 512 MiB. On the six original corpora, CIDR mode is
faster than the recorded Phase 1 baseline; the 15% regression ceiling therefore
passes with margin.
