# cidrmerge Benchmarks

The benchmark harness builds `cidrmerge` in release mode, generates deterministic
line-oriented corpora, and measures the complete text-input-to-text-output pipeline.
Generated fixtures live only in a temporary directory.

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
distributions. They contain no operational routing or authorization data.

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
