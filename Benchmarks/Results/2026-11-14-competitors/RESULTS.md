# cidrmerge 0.4.0 competitor comparison

Measured 2026-11-14 on an Apple M1 Max, comparing exact CIDR aggregation with
rs-aggregate 0.3.2, iprange 2.1.1, and mapCIDR 1.1.97. All **41 tool/corpus/suite
combinations** produced equivalent minimal coverage. All **337 measured samples**
(**497 CLI process invocations**) passed exit-status, stderr, and output-hash
checks. No measured samples were retried, replaced, or excluded.

## Findings

rs-aggregate had the lowest median elapsed time in all eight split-family
workloads and all three native mixed workloads. iprange had the lowest median
peak RSS in every split-family workload. cidrmerge was faster than mapCIDR in
every measured workload, and faster than iprange on IPv6-disjoint input; iprange
was faster on the other seven split-family workloads.

For a single file of one million mixed, disjoint entries, cidrmerge took a median
**1.008 s at 118.8 MiB**, rs-aggregate **0.215 s at 63.9 MiB**, and mapCIDR
**12.549 s at 1263.5 MiB**. In the median paired elapsed comparison, cidrmerge took
**4.72 times as long as rs-aggregate**, and mapCIDR took **12.53 times as long as
cidrmerge** on this input. These are within-round elapsed ratios, not ratios
computed from the rounded table values.

Input order matters. Permuting those same mixed entries raised cidrmerge's native
median from 1.008 s to 2.300 s; rs-aggregate rose from 0.215 s to 0.245 s, and
mapCIDR from 12.549 s to 16.951 s. Equivalent coverage does not imply equal work
for every input order. The large gap on the synthetic BGP-like and overlapping
inputs is also worth investigating in a future profiling task; these measurements
alone do not identify its cause.

The practical conclusion is specific: cidrmerge completes this million-entry
mixed workload in about one second, while rs-aggregate is substantially faster
and uses less resident memory in the tested native mixed cases. iprange offers
particularly low resident memory when families are handled separately. This is
not an industry-wide ranking or a claim about all input distributions.

## Environment and tested builds

The host was a MacBookPro18,2 with Apple M1 Max, 10 logical CPUs, 64 GiB RAM,
macOS 27.2.1 (26B131), on AC power. CPython 3.12.6 ran the harness. This was an
active workstation: pre-run load averages were 6.77/6.32/6.54, the intermediate
snapshot reported 8.04/7.50/7.19, and the permitted post-run snapshot reported
5.67/5.89/6.33. Power snapshots stayed on AC. `pmset` reported no recorded thermal
or performance warnings; that is not evidence of fixed clocks or an idle host.

All four executables are native ARM64 and were hash-pinned before measurement.
The tested cidrmerge executable is the published 0.4.0 release built with
**Xcode 26.3 / Swift 6.2**, not the earlier local Swift 6.4.2 qualification build.
rs-aggregate was built from its unmodified tag with Rust 1.100.0, the locked
dependencies, and the default release profile/Rayon feature. iprange used Apple
Clang 21 and upstream `-O3 -flto` defaults. mapCIDR is the official ARM64 release
built with Go 1.24.0. Exact pins, binary hashes, commands, and reproduction steps
are in [REPRODUCING.md](REPRODUCING.md).

## Suites

The **split** suite measures all four tools on the same prepartitioned family
files: eight rounds per combination. For a mixed case, elapsed time sums the two
sequential family processes, while peak RSS is their maximum. Partitioning is
outside timing. This is not a measurement of an arbitrary mixed-file wrapper.

The **native** suite measures one unsplit mixed file per process: nine rounds per
combination. It excludes iprange because its IPv4 mode drops native IPv6, while
its IPv6 mode maps IPv4 into IPv6. Neither is equivalent to retaining both address
families. The native suite also preserves the opportunity for tools to process
the two families concurrently. Keep these suites separate.

## Split-family results

Each cell is **median elapsed seconds / median peak RSS MiB**; lower is better.

| Corpus | cidrmerge | rs-aggregate | iprange | mapCIDR |
|---|---:|---:|---:|---:|
| ipv4-disjoint | 0.833 / 69.2 | 0.172 / 31.1 | 0.307 / 11.5 | 11.464 / 1130.5 |
| ipv6-disjoint | 1.171 / 166.8 | 0.256 / 99.6 | 1.612 / 34.4 | 14.431 / 1341.3 |
| mixed-disjoint | 1.020 / 86.7 | 0.226 / 52.8 | 0.698 / 19.1 | 12.815 / 684.3 |
| mixed-permuted | 2.294 / 86.9 | 0.269 / 51.7 | 0.810 / 34.4 | 17.182 / 694.2 |
| mixed-overlap | 1.809 / 71.2 | 0.152 / 35.0 | 0.213 / 19.1 | 10.469 / 585.2 |
| mixed-adjacent | 0.843 / 71.1 | 0.120 / 27.3 | 0.129 / 1.8 | 6.380 / 669.4 |
| bgp-like-ipv4 | 2.029 / 56.6 | 0.148 / 25.8 | 0.267 / 13.0 | 25.344 / 1045.3 |
| range-derived-mixed | 1.040 / 95.0 | 0.225 / 44.1 | 0.696 / 11.5 | 24.748 / 693.7 |

Paired elapsed ratios are the median of `tool elapsed / cidrmerge elapsed` within each round.
Below 1 means that tool was faster; above 1 means cidrmerge was faster.

| Corpus | rs-aggregate | iprange | mapCIDR |
|---|---:|---:|---:|
| ipv4-disjoint | 0.209 | 0.371 | 13.860 |
| ipv6-disjoint | 0.218 | 1.383 | 12.112 |
| mixed-disjoint | 0.223 | 0.683 | 12.555 |
| mixed-permuted | 0.116 | 0.353 | 7.555 |
| mixed-overlap | 0.084 | 0.116 | 5.655 |
| mixed-adjacent | 0.142 | 0.155 | 7.572 |
| bgp-like-ipv4 | 0.073 | 0.132 | 12.254 |
| range-derived-mixed | 0.217 | 0.670 | 23.571 |

## Native results

Each cell is **median elapsed seconds / median peak RSS MiB**; lower is better.

| Corpus | cidrmerge | rs-aggregate | mapCIDR |
|---|---:|---:|---:|
| mixed-disjoint | 1.008 / 118.8 | 0.215 / 63.9 | 12.549 / 1263.5 |
| mixed-permuted | 2.300 / 118.9 | 0.245 / 67.5 | 16.951 / 1178.1 |
| mixed-overlap | 1.812 / 83.4 | 0.137 / 46.9 | 10.397 / 977.7 |

Paired elapsed ratios are the median of `tool elapsed / cidrmerge elapsed` within each round.
Below 1 means that tool was faster; above 1 means cidrmerge was faster.

| Corpus | rs-aggregate | mapCIDR |
|---|---:|---:|
| mixed-disjoint | 0.212 | 12.531 |
| mixed-permuted | 0.106 | 7.353 |
| mixed-overlap | 0.076 | 5.739 |


## Corpora

Every row has 1,000,000 input records. The generator and complete file/coverage
hashes are retained with the machine-readable results.

| Corpus | IPv4 / IPv6 records | Minimal output CIDRs |
|---|---:|---:|
| ipv4-disjoint | 1,000,000 / 0 | 1,000,000 |
| ipv6-disjoint | 0 / 1,000,000 | 1,000,000 |
| mixed-disjoint | 500,000 / 500,000 | 1,000,000 |
| mixed-permuted | 500,000 / 500,000 | 1,000,000 |
| mixed-overlap | 500,000 / 500,000 | 2 |
| mixed-adjacent | 500,000 / 500,000 | 14 |
| bgp-like-ipv4 | 1,000,000 / 0 | 233,532 |
| range-derived-mixed | 500,000 / 500,000 | 1,000,000 |

## Method and interpretation

Every corpus contains exactly 1,000,000 canonical CIDR records. Fixtures and
executable bytes were hashed before the excluded verification runs and measured
rounds. Builds, downloads, fixture generation, partitioning, and independent
coverage verification are outside the timed region. Each CLI invocation reads a
file and writes ordinary formatted output to a file; startup, parsing, aggregation,
formatting, and buffered file writes are included. No fsync durability is claimed.

The four-tool split suite gives each tool the same IPv4 and IPv6 files in the
same within-family order. Nonempty families run sequentially. Elapsed time is the
sum of their process durations; peak RSS is the larger process peak, not their
sum. Input partitioning and concatenation are not timed. This mode is required
for equivalent iprange semantics and changes the opportunity for simultaneous
family processing. The native mixed suite therefore measures the same unsplit
mixed files with cidrmerge, rs-aggregate, and mapCIDR separately. Do not combine
these suites into one ranking.

The split suite has eight rounds per combination; the native suite has nine.
Tool positions are balanced through rotated forward/reverse orders, and case
order rotates. The schedule is not fully balanced for predecessor/carryover
effects. One independently verified run per combination is excluded as warmup.
Processes are fresh; this is an intended warm-cache workload. Every measured
sample is retained, with no automatic retries or outlier removal.

Elapsed time uses Python perf_counter_ns around blocking process launch/wait,
including the BSD time launcher overhead. The runner avoids timeout polling and
uses a signal deadline instead. Raw /usr/bin/time -p -l observations retain
real, user, sys, and maximum resident set size. On macOS the recorded RSS value
is bytes; MiB divides by 1,048,576. RSS is process resident memory, not allocated
bytes, total system memory, or Apple peak memory footprint. Reported quartiles
and ranges describe these small samples; they are not confidence intervals.

Each tool uses its default thread behavior. The fresh child environment omits
inherited thread overrides, credentials, and HOME; it does not modify the user's
global configuration. rs-aggregate retains its default Rayon feature; mapCIDR
retains its default Go runtime and temporary storage behavior. Normal tool output
formats are preserved: iprange prints singleton addresses without /32 or /128.
Coverage is equivalent, but output byte counts can differ across tools.

All runs use native ARM64 executables on one active workstation, with no CPU
pinning, clock lock, cache flush, or dedicated-host isolation. The products use
different release/build toolchains. These results compare these versions and
builds on these inputs; they do not rank programming languages, establish Linux
or Intel performance, or measure arbitrary-range input parsing.

## Coverage verification

An independent Python standard-library parser reads the actual fixture and
output bytes. Numeric intervals are sorted and coalesced separately per family.
The verifier compares a SHA-256 digest of the complete union and requires the
minimal CIDR count calculated by independent integer decomposition. Singleton
addresses are accepted as /32 or /128; malformed records, scoped addresses, and
noncanonical CIDRs with host bits are rejected.

The count algorithm was checked against Python summarize_address_range on 406
boundary and random intervals. Separate negative controls reject wrong coverage,
nonminimal output, and host bits; a bare-host positive control passes. Every
measured output must be byte-identical to that tool's independently verified
warmup output. Hashing happens outside timing. Nonzero exit status, unexpected
stderr, or output drift stops measurement and preserves the failure.

The range-derived corpus begins as 500,000 disjoint six-address intervals,
expanded before timing into 1,000,000 CIDRs for all tools. It tests equivalent
coverage aggregation through a common CIDR grammar, not native range parsing.
The BGP-like corpus is synthetic and carries no route attributes or operational
routing data.

## Evidence and preservation

[summary.json](summary.json) contains all 337 observations, aggregate medians,
quartiles, ranges, paired ratios, CPU times, peak RSS, output sizes/hashes, and
fixture recipes/hashes. [DISTRIBUTIONS.md](DISTRIBUTIONS.md) shows quartiles and
full observed ranges for every combination. The [verification matrix](verification-matrix.json)
records all 41 independent coverage preflights. The frozen runner, generator,
verifier, analyzer, protocol and reference manifests are in [control/](control/).
`render_tables.py` is the subsequent presentation script; it does not participate
in measurement.

Separate [metrics](independent-metrics-audit.json) and
[coverage](independent-coverage-audit.json) audits passed after measurement. They
checked every raw timing receipt and exported statistic, rehashed all 61 retained
warmup outputs, matched all 497 measured output-hash receipts, and verified the
frozen inputs and analysis script. Removed duplicate output bytes cannot be
re-read; their stored hashes are checked against the retained verified originals.

The complete local run is retained under Downloads as
`cidrmerge-competitors-20261114T210745Z`, including raw BSD timing files, stderr,
verified warmup outputs, commands, source/build provenance, temporary storage,
and all failed preparation observations. Only byte-identical duplicate measured
output files were removed, after their hashes were checked outside timing.
No measured invocation failed. A restricted post-run hardware snapshot could not
read several sysctl values; its failure receipt is retained alongside the
successful permitted snapshot. No benchmark was repeated for that metadata check.

The earlier summarization qualification results remain unchanged as the prefix
of their historical report; only a dated link to this separate comparison was
appended. Its original bytes, the prior benchmark overview, and corpus generator
were copied before this work. Historical threshold JSON, production Swift source,
and previous release-validation evidence are untouched. No cross-tool performance
threshold is inferred from the earlier same-tool regression gates.
