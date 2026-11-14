# cidrmerge 0.4.0 summarization qualification

Status: **tests and data audits complete; performance acceptance not met, 2026-11-13**.
All 11 functional test configurations passed. Final C2 macOS, native ARM64 Linux,
and native x86-64 Linux CLI and Core measurements have passed independent data
audits. No primary CLI median paired increase exceeded 5% on any measured
platform. Core results differ: x86-64 has 31 full-profile cases and three large
wall-only range cases above 5% at both p50 and p90, despite fewer allocations.
All six pairs of each large x86 range control were slower. The macOS +5.94%
instrumented mixed-range result and its separately reported wall-only follow-up
also remain retained. Data-audit success does not resolve these performance
exceptions. Persistent x86-64 Core regressions prevent performance acceptance
of the current C2 candidate. This report does not qualify or announce a release.

## Change and comparison scope

The candidate raises the swift-cidr requirement to 0.10.0 and pins its published
revision `e268b139e334a0662185d16a3e07b187ab0cbe70`. That dependency supplies the
append-based range summarizer. Four family projections in `CIDRMergeCoverage`
now use `lazy.map` while appending to a reserved result array: two in `ranges`
and two in `summarizedNetworks()`. The public return types and IPv4-first ordering
remain unchanged. The corrected candidate also returns immediately when both
family indexes are empty, before setting up projections or family summaries.

| Arm | cidrmerge source | swift-cidr | Purpose |
|---|---|---|---|
| A | 0.3.0, `af92697968338bdbd5bcff416b0a5edfcdeb16be` | 0.8.1 | Frozen released baseline |
| B | A with only the dependency floor and pin updated | 0.10.0 | Complete dependency-upgrade comparison |
| C | Initial 0.4.0 candidate, including the four lazy projections | 0.10.0 | Original integration and Core projection comparison |
| C2 | C plus an empty-coverage return in each Core projection API | 0.10.0 | Final measured candidate; all platform data audited, performance exceptions unresolved |

A/B includes all intervening swift-cidr changes from 0.8.1 to 0.10.0; it cannot
isolate the new summarizer from those changes. B/C Core measurements isolate the
four lazy projections in the measured library methods; B/C2 also includes the
two empty fast paths. The CLI reads typed IPv4
and IPv6 coverage and calls each family's summarizer directly. It bypasses the
family-erased Core projections, so small CLI B/C differences do not measure the
lazy projection optimization.

All other application pins are identical across A/B/C/C2. Source archives, file
manifests, dependency locks, executables, generator, fixtures, commands, and raw
measurement outputs were retained in the qualification evidence. The external
Core harness adds no dependency to the cidrmerge package.

The review tree has four comment-label edits relative to frozen C2; all
executable code is unchanged. Their before/after hashes are retained separately.

## Functional validation

| Platform and toolchain | Completed checks | Status |
|---|---|---|
| Final C2, native macOS arm64, Xcode 27.2 / Apple Swift 6.4.2 | Debug and Release: 57 tests in 7 suites each; CLI smoke; strict formatting; DocC; external Core consumer; iOS 18 arm64 simulator Core compilation; source and stripped-binary content audits; version/help and linked-library inspection | Passed |
| Final C2, native Linux ARM64 under OrbStack, Swift 6.2.4 | Debug and Release: 57 tests in 7 suites each | Passed |
| Final C2, native Linux ARM64 under OrbStack, Swift 6.3.3 | Debug and Release: 57 tests in 7 suites each | Passed |
| Final C2, native Linux ARM64, Swift 6.2.4 dependency-floor graph | Build and 57 tests in 7 suites, with swift-cidr 0.10.0, ArgumentParser 1.7.0, and Swift Crypto 5.1.1 | Passed |
| Final C2, native Linux x86-64, Swift 6.2.4 and 6.3.3 | Debug and Release: 57 tests in 7 suites each, in all four configurations | Passed |

The 11 test configurations above comprise two macOS, four ARM64 Linux,
one ARM64 dependency-floor, and four x86-64 Linux configurations. Each passed
57 tests in 7 suites.

macOS functional builds explicitly used SwiftPM's native build engine. All three
macOS CLI benchmark arms used the default SwiftBuild engine, identical Release
flags, Xcode 27.2, and Apple Swift 6.4.2. These are separate validation scopes;
functional timings are not benchmark evidence. The iOS check is a compilation
check, not an on-device runtime test.

After adding C2's two empty-coverage guards, macOS Debug and Release each passed
all 57 tests in 7 suites again, including the existing test for both empty
projection APIs. Strict formatting also passed. The dependency lock remained
unchanged. After all measurements on the local Mac/ARM host stopped, C2 also
passed the refreshed smoke, external consumer, DocC, iOS compilation, notices,
and remapped/stripped-binary checks. This timing boundary did not imply that
measurements on the separate x86-64 host had finished.

The GNU `time` reporting correction was checked on native ARM64 Linux with
GNU time 1.9. Combining `-p -v` omitted the parser's required `real/user/sys`
lines. The script now requests those fields and RSS explicitly, preserving
Linux RSS in KiB; the macOS timing format is unchanged.

The complete clean-tree `check-release.sh` gate has not run for this uncommitted
candidate. Its completed functional and content-audit constituents do not imply
that release CI, four-platform archive inspection, tagging, or publication has
completed. The native x86-64 tests, three primary measurement phases, and separate
CLI diagnostic are now complete, with retrieved, independently checked evidence.
The x86-64 Core regressions below remain unresolved; completed measurements and
successful correctness checks do not imply a performance qualification pass.

## macOS CLI methodology

Captured on native arm64 macOS 27.2.1 with Xcode 27.2 and Apple Swift 6.4.2.
Eight deterministic, synthetic one-million-record corpora were each tested in
`ranges` and `cidr` output modes, giving 16 cases. The six round orders were
`ABC`, `BCA`, `CAB`, `CBA`, `ACB`, and `BAC`, balancing every arm position.
Each arm/case had one excluded warmup: 48 warmups and 288 measured invocations.

Before timing, all three arms produced identical raw output bytes and the locked
range/CIDR cardinalities listed in the [benchmark overview](../../README.md#output-cardinality-and-compression).
Every CIDR output normalized back to exactly the same range bytes. The original
runner compared output bytes directly before discarding duplicate B/C and
roundtrip files. The independent audit rechecked their saved hashes and counts,
decompressed all 16 retained shared output archives, and rehashed all eight
fixtures. Thus the second audit verifies the retained bytes and comparison
receipts; it does not claim to reread files that were intentionally discarded.

On every platform, the shared CLI runner redirects timed standard output to
`/dev/null`. Output formatting and emission remain inside the measured process;
downstream consumption and persistent output-file I/O are outside this scope.
Output bytes, cardinalities, and roundtrips are verified separately before timing.

Times below are medians of six whole-process elapsed measurements, including
Python subprocess launch and the `/usr/bin/time` wrapper. Changes are medians
of six per-round C/B, B/A, or C/A ratios as labeled, not ratios of the displayed
medians. Original hundredth-second `real/user/sys` readings are preserved
separately. Peak RSS is a process maximum: Darwin reports bytes, divided by
1,024 for KiB. Every invocation must remain within 524,288 KiB (512 MiB).

## Final C2 macOS CLI results

Negative elapsed changes indicate less time; positive changes indicate more.
The final run uses the original frozen A/B binaries and a rebuilt C2 executable.
It repeats all cases with freshly validated fixtures and output comparisons.

| Corpus / representation | A seconds | B seconds | C2 seconds | A to B | B to C2 | A to C2 |
|---|---:|---:|---:|---:|---:|---:|
| disjoint/ranges | 0.8057 | 0.8122 | 0.8164 | +0.85% | +0.03% | +0.53% |
| disjoint/cidr | 1.5089 | 0.7352 | 0.7432 | -51.46% | +0.46% | -50.86% |
| siblings/ranges | 0.6888 | 0.7012 | 0.6952 | +2.05% | -1.08% | +1.04% |
| siblings/cidr | 0.6882 | 0.6966 | 0.6959 | +1.60% | -0.59% | +1.27% |
| subsumed/ranges | 1.4980 | 1.5529 | 1.5374 | +3.15% | -2.12% | +2.91% |
| subsumed/cidr | 1.5016 | 1.5510 | 1.5413 | +3.52% | -1.47% | +1.23% |
| bgp-like/ranges | 2.1871 | 2.2562 | 2.2647 | +3.19% | +0.50% | +3.75% |
| bgp-like/cidr | 2.3435 | 2.2481 | 2.2402 | -4.01% | -0.56% | -4.34% |
| rpki-like/ranges | 2.1496 | 2.2119 | 2.1658 | +3.01% | -2.56% | +0.53% |
| rpki-like/cidr | 2.1845 | 2.2096 | 2.1968 | +1.06% | -0.70% | +0.62% |
| mixed/ranges | 1.0352 | 1.0500 | 1.0511 | +1.46% | +0.56% | +1.00% |
| mixed/cidr | 1.7396 | 0.9263 | 0.9370 | -46.74% | +0.84% | -46.26% |
| arbitrary-ranges/ranges | 2.4121 | 2.4309 | 2.4319 | +0.68% | -0.31% | +0.54% |
| arbitrary-ranges/cidr | 3.4225 | 2.4179 | 2.3994 | -29.42% | -0.70% | -30.04% |
| overlapping-ranges/ranges | 2.8123 | 2.8285 | 2.8277 | +0.73% | -0.02% | +0.51% |
| overlapping-ranges/cidr | 2.8124 | 2.8430 | 2.8316 | +0.86% | -0.13% | +0.50% |

All measured invocations and warmups passed. Maximum RSS was 150,320 KiB
(146.80 MiB), including warmups. No case's median paired elapsed increase
exceeded 5%. A/B ranged from -51.46% to +3.52%, B/C2 from -2.56% to +0.84%,
and A/C2 from -50.86% to +3.75%.

An independent audit passed 3,913 checks covering inventory, arm order, raw
timing fields, RSS conversion, paired arithmetic, output verification receipts,
archives, and frozen hashes. These six trials are descriptive evidence for this
host, toolchain, and corpus. They do not establish precise tail latency,
statistical confidence intervals, or a general speedup for every input.

The preceding initial C run remains preserved separately: it also completed all
288 measurements and 48 warmups, stayed below 512 MiB, and had no median paired
increase above 5%. Its A/C changes ranged from -51.66% to +2.97%. Those earlier
figures are historical evidence; the table above reports the final C2 rerun.

## Final C2 macOS Core results

C2 was rebuilt and validated against the unchanged frozen B, using identical
fixtures, the complete dependency graph, and the same nine-metric full profile.
Both validation and final executables listed exactly 56 cases. Six alternating
pairs covered the full profile, six pairs covered the six large wall-only cases,
and six pairs verified both empty APIs with wall-clock alone. The fixture,
batching, histogram, and measurement-boundary details are described below.

| Large fragmented fixture / API | B wall-only ms | C2 wall-only ms | Paired change | B allocations/call | C2 allocations/call |
|---|---:|---:|---:|---:|---:|
| IPv4 / ranges | 0.035711 | 0.027111 | -24.07% | 2 | 1 |
| IPv6 / ranges | 0.039247 | 0.034879 | -10.19% | 2 | 1 |
| Mixed / ranges | 0.072959 | 0.062367 | -14.39% | 3 | 1 |
| IPv4 / networks | 2.330623 | 2.212863 | -5.35% | 8 | 7 |
| IPv6 / networks | 15.036415 | 15.134719 | +0.54% | 10 | 9 |
| Mixed / networks | 17.575935 | 17.444863 | -0.66% | 17 | 15 |

Allocation values come from the full profile; wall-only measurements disable
allocation/ARC hooks while keeping the same binaries and loaded interposers.
The retained fresh-result allocations are not a reusable-destination benchmark.

| Empty API, wall-only | B ns/call | C2 ns/call | Paired p50 change | Paired p90 change |
|---|---:|---:|---:|---:|
| ranges | 29.839 | 4.711 | -84.21% | -84.25% |
| networks | 36.095 | 5.335 | -85.22% | -85.35% |

These empty results are 1,000-call batch means. Both APIs record zero mallocs
in the full profile. The fast paths remove the original empty regressions in
this matched comparison; the original outcomes remain documented below.

The only full-profile median paired wall increase above 5% was
`mixed.aligned.ranges1024.ranges`: 3,875 to 4,147 ns, +5.94%, with a median
paired absolute change of +230 ns. Four paired ratios increased and two
decreased. Observed allocations fell from three to one, retains rose from zero
to two, and releases were unchanged. Those observations do not establish the
cause of the timing difference.

That result triggered six additional wall-only pairs for all three mixed
1,024-range projection shapes, using the same frozen binaries:

| Mixed 1,024 ranges, ranges API | Paired p50 change | Paired p90 change |
|---|---:|---:|
| Aligned | -2.08% | -3.41% |
| Fragmented | +0.28% | -1.98% |
| Singleton | +2.21% | -0.53% |

The targeted control did not reproduce a median wall-only increase above 5%.
Individual paired ratios varied, so the original +5.94% instrumented result is
retained rather than dismissed or replaced. The extra control was selected
after observing that result, not part of the original matrix. No other final
full-profile or planned wall-only case had a p50 or p90 paired increase above 5%.

The independent final Core audit passed 32,354 checks across 6,144 exports,
plus a separate audit of the 36 mixed-1,024 diagnostic exports. Full-profile
sample counts ranged from 17 to 1,000 per metric; large wall-only counts from
15 to 1,000; empty and mixed-1,024 controls had 1,000 each. All source, fixture,
pin, binary, and interposer checks passed. These results do not imply individual
call tail latency, confidence intervals, a Core RSS limit, or performance on an
unmeasured platform.

## Initial macOS Core projection comparison

The first external Core packages compiled, but runner initialization did not
pass: Benchmark 1.35 generates its entry point only for targets under a
`Benchmarks` directory, while the initial package used `Sources`. The resulting
executables returned no benchmark inventory; the driver reported `WaitPIDError`
despite exiting successfully. No Core measurements were accepted. Failed setup
evidence is retained. Correcting the package layout preserved fixture and
measured callback bodies. Both rebuilt arms then passed fixture validation and
listed exactly 56 named cases before timing. An exit status of zero alone was
not accepted as proof of validation.

The external B/C harness directly consumes `CIDRMergeCore` with identical
fixtures and dependency pins. The full profile covered 56 cases:
`ranges` and `summarizedNetworks()` over empty, IPv4, IPv6, and mixed coverage;
singleton, aligned, and fragmented shapes; and 1, 1,024, or 16,384 disjoint
ranges per present family. Fixture construction and exact ordered output
validation occur outside measurement.

Six alternating B/C pairs collected wall-clock and eight allocation/ARC metrics.
Six large fragmented cases also ran six pairs with wall-clock alone. The same
binaries and interposer libraries were used; allocation/ARC hooks were disabled
for wall-only runs. The full profile excludes process-stat/RSS sampling.

Each case used three warmups and a 300 ms or 1,000-sample limit. Empty and
one-range fixtures use 1,000 calls per sample; the larger fixtures use one.
Exported observations are quantized histogram values expanded by count, not
chronological raw samples. Dividing a batched percentile by 1,000 describes a
batch mean, not a percentile of individual call latency. Results below use the
median of six same-round C/B ratios. Fresh output allocation and disposal are
inside measurement; fixture construction and validation are outside it.

| Large fragmented fixture / API | B wall-only ms | C wall-only ms | Paired change | B allocations/call | C allocations/call |
|---|---:|---:|---:|---:|---:|
| IPv4 / ranges | 0.036343 | 0.027695 | -23.46% | 2 | 1 |
| IPv6 / ranges | 0.039471 | 0.035823 | -9.28% | 2 | 1 |
| Mixed / ranges | 0.076159 | 0.063615 | -16.65% | 3 | 1 |
| IPv4 / networks | 2.366463 | 2.245631 | -5.19% | 8 | 7 |
| IPv6 / networks | 15.314943 | 15.321087 | +0.49% | 10 | 9 |
| Mixed / networks | 17.932287 | 17.555455 | -1.98% | 17 | 15 |

Each present family has 16,384 disjoint ranges in these fixtures; mixed has
32,768 total. Allocation values are observed medians from the separate full
profile. They show reductions of one allocation for a single present family
and two for mixed coverage in these cases, not elimination of every result
allocation. All 54 nonempty full-profile cases had no median paired elapsed
increase above 5%; the six large wall-only cases likewise stayed below that
level. Core peak RSS was not measured; the CLI's separate 512 MiB guard does not
establish a Core process-memory bound.

### Empty-coverage regression and correction

The initial C candidate regressed on both empty APIs. Six additional wall-only
pairs were selected after observing this result, using the same frozen binaries.
The slowdown persisted with allocation/ARC hooks disabled:

| Empty API | Profile | B ns/call | C ns/call | Paired p50 change | Paired p90 change |
|---|---|---:|---:|---:|---:|
| ranges | Full | 61.511 | 102.783 | +67.31% | +54.61% |
| ranges | Wall-only diagnostic | 29.887 | 52.479 | +75.59% | +73.11% |
| networks | Full | 75.039 | 82.943 | +10.66% | +0.08% |
| networks | Wall-only diagnostic | 36.095 | 44.191 | +22.43% | +23.42% |

Both empty APIs recorded zero mallocs. Empty `ranges` recorded approximately two
additional retains and releases per call; empty `networks` had no corresponding
retain/release increase. Those counters do not establish a common cause for both
slowdowns. The wall-only median paired absolute increases were 22.592 ns/call
for ranges and 8.096 ns/call for networks, averaged over 1,000-call batches.

C2 adds a constant-time check of both typed family indexes before either Core
projection method does further work. Correctness and formatting checks passed;
the matched C2 results above verify the empty-path change. The original C
measurements remain preserved and are not replaced by the retry.

An independent audit passed 32,354 checks across all 6,144 exported histograms:
6,048 full-profile, 72 large wall-only, and 24 empty diagnostic exports. It
recomputed unit conversion, batch scaling, p50/p90 values, paired ratios and
allocation deltas, and verified frozen source, fixture, binary, interposer, and
full dependency-pin evidence. Sample counts ranged from 16 to 1,000 per metric
in the full and large wall-only profiles; empty controls had 1,000 each. These
are descriptive host/toolchain results, including the regressions, not confidence
intervals or precise individual-call tail-latency measurements.

## Final C2 native ARM64 Linux results

These measurements ran with Swift 6.3.3-RELEASE, Ubuntu 24.04, and GNU time 1.9
inside the OrbStack ARM64 Linux virtual machine/container on the Mac host.
Instructions execute natively on ARM64; this is not bare-metal Linux evidence.
The environment differs from macOS and its Apple Swift 6.4.2 compiler, so results
are reported separately without pooling or making cross-host comparisons.

The same frozen A/B/C2 sources and million-record corpus were used. All 16 CLI
cases completed six balanced rounds and one excluded warmup per arm/case:
288 measured invocations and 48 warmups. GNU time reports RSS directly in KiB;
there is no Darwin byte conversion. Primary elapsed time includes subprocess
launch, the time wrapper, and process completion, as in the macOS harness.

| Corpus / representation | A seconds | B seconds | C2 seconds | A to B | B to C2 | A to C2 |
|---|---:|---:|---:|---:|---:|---:|
| disjoint/ranges | 2.5124 | 2.4867 | 2.5266 | -1.26% | +0.44% | -3.41% |
| disjoint/cidr | 3.3712 | 2.4386 | 2.3712 | -28.82% | -0.90% | -30.18% |
| siblings/ranges | 2.2337 | 2.2434 | 2.2125 | -0.74% | -2.94% | -1.93% |
| siblings/cidr | 2.2662 | 2.1964 | 2.2317 | -2.38% | +0.49% | -0.81% |
| subsumed/ranges | 3.3831 | 3.4334 | 3.5016 | +1.47% | -0.08% | +2.65% |
| subsumed/cidr | 3.4087 | 3.3860 | 3.4009 | -0.86% | +0.24% | +1.38% |
| bgp-like/ranges | 4.5058 | 4.5685 | 4.5927 | +1.59% | +0.42% | +1.73% |
| bgp-like/cidr | 4.6799 | 4.5913 | 4.6083 | -2.63% | +1.09% | -2.54% |
| rpki-like/ranges | 4.4333 | 4.4670 | 4.4410 | +0.76% | -0.11% | +0.40% |
| rpki-like/cidr | 4.5208 | 4.4327 | 4.4713 | -1.43% | +0.28% | -1.37% |
| mixed/ranges | 3.0069 | 3.0151 | 2.9201 | +1.40% | -2.65% | -1.90% |
| mixed/cidr | 3.8418 | 2.7976 | 2.8101 | -27.42% | -0.05% | -27.38% |
| arbitrary-ranges/ranges | 5.1879 | 5.1253 | 5.2227 | -1.01% | +2.50% | +0.82% |
| arbitrary-ranges/cidr | 6.7188 | 5.3298 | 5.2858 | -21.51% | -0.96% | -21.14% |
| overlapping-ranges/ranges | 5.7910 | 5.7521 | 5.8325 | -0.64% | +0.67% | +0.09% |
| overlapping-ranges/cidr | 5.8119 | 5.8072 | 5.7972 | -0.70% | -0.00% | +0.03% |

Percentages are medians of six same-round ratios, not ratios of displayed
medians. They can even differ in sign: disjoint/ranges A and C2 displayed
medians rise slightly, while the paired A/C2 change is -3.41%. All six ratios
are retained. No CLI median paired increase exceeded 5%. Maximum observed RSS,
including warmups, was 97,576 KiB (95.29 MiB), below the 512 MiB limit.

The Core matrix also completed all 56 cases with nine metrics over six pairs,
plus six large and two empty wall-only cases over six pairs. Both runtime and
malloc interposer libraries were pinned and hashed for each side across all
profiles. Allocation/ARC hooks were disabled for wall-only controls while those
libraries remained loaded. All 648 nonempty full-profile case/run malloc-count
medians were positive, confirming that the observed reductions were not a
disabled allocation sensor.

| Large fragmented fixture / API | B wall-only ms | C2 wall-only ms | Paired change | B allocations/call | C2 allocations/call |
|---|---:|---:|---:|---:|---:|
| IPv4 / ranges | 0.056031 | 0.028487 | -49.23% | 2 | 1 |
| IPv6 / ranges | 0.056783 | 0.036991 | -34.91% | 2 | 1 |
| Mixed / ranges | 0.112991 | 0.064495 | -43.06% | 3 | 1 |
| IPv4 / networks | 5.251071 | 2.303999 | -56.07% | 8 | 7 |
| IPv6 / networks | 30.908415 | 24.645631 | -19.77% | 10 | 9 |
| Mixed / networks | 36.798463 | 30.150655 | -19.36% | 17 | 15 |

Each present family contains 16,384 ranges. Allocation values are observed
medians from the full profile; wall-only timings are separate. These APIs still
allocate fresh nonempty result arrays.

| Empty API, wall-only | B ns/call | C2 ns/call | Paired p50 change | Paired p90 change |
|---|---:|---:|---:|---:|
| ranges | 63.999 | 6.167 | -90.36% | -90.72% |
| networks | 73.599 | 6.793 | -90.74% | -91.12% |

No Core p50 or p90 median paired increase exceeded 5% in these measurements.
The full and large wall-only profiles had 7 to 1,000 samples per case/metric;
the largest cases therefore provide limited within-run tail evidence. Empty
controls had 1,000 samples each. The same quantized-histogram and 1,000-call
batch-mean limits apply as on macOS. No Core process-RSS bound was measured.

The independent audit passed 25,431 raw-evidence checks plus 8,600 checks of
derived comparisons, preload identity, and baseline reuse. The reused Core B
matched the accepted prior build's 41 source files, package manifest, fixture,
complete dependency pins, all four binary/library artifacts, and validation
receipt. The audit decompressed all 16 shared output archives, rehashed all
eight fixtures, and verified the 72 output/roundtrip receipts. Those eight
fixture and 72 output fingerprints also match the separately audited macOS
run. Native ARM64 VM results support this environment and workload only.

## Final C2 native x86-64 CLI results

The primary CLI comparison ran with Swift 6.3.3-RELEASE and the configured
Swiftly toolchain, using native x86-64 instructions inside LXC on a separate host
reporting an Intel Xeon E5520 at 2.27 GHz and four visible logical CPUs. Compiler
checks and recorded Release build commands establish the toolchain scope. An
approved read-only probe after CLI and before Core identified the CPU and LXC;
it found no active task or identified prior-probe workers at that boundary.
Visible cgroup files showed no local CPU or memory cap and zero recorded
throttling, but ancestor constraints are unknown. These observations establish
neither global host idleness nor uninterrupted isolation or unbounded resources.
No bare-metal or cross-host performance claim is made. GNU time reports RSS
directly in KiB.

All 16 million-record cases completed six balanced rounds and one excluded
warmup per arm/case: 288 measured invocations and 48 warmups. All 80 generation
and correctness commands succeeded. The same stdout, output-verification, and
paired-statistic boundaries described above apply. A/B covers the complete
swift-cidr 0.8.1-to-0.10.0 upgrade; CLI B/C2 does not exercise the erased Core
projection changes.

| Case | A seconds | B seconds | C2 seconds | A→B | B→C2 | A→C2 |
|---|---:|---:|---:|---:|---:|---:|
| disjoint/ranges | 9.088 | 9.105 | 9.134 | +0.864% | +1.393% | +1.711% |
| disjoint/cidr | 11.314 | 8.816 | 8.924 | -22.052% | +1.318% | -21.286% |
| siblings/ranges | 8.094 | 8.066 | 8.078 | +0.874% | +0.193% | -0.273% |
| siblings/cidr | 8.121 | 8.140 | 8.213 | +0.443% | +0.985% | +1.161% |
| subsumed/ranges | 10.653 | 10.568 | 10.653 | -0.672% | +0.238% | -0.434% |
| subsumed/cidr | 10.563 | 10.506 | 10.669 | -0.279% | +1.974% | +1.893% |
| bgp-like/ranges | 13.230 | 13.369 | 13.366 | +1.047% | +0.136% | +1.186% |
| bgp-like/cidr | 13.725 | 13.304 | 13.312 | -2.489% | +0.062% | -2.549% |
| rpki-like/ranges | 13.050 | 13.112 | 13.078 | +0.171% | -0.311% | +0.162% |
| rpki-like/cidr | 13.141 | 12.942 | 13.011 | -1.243% | +0.087% | -0.982% |
| mixed/ranges | 10.625 | 10.784 | 10.810 | +1.040% | -0.240% | +1.204% |
| mixed/cidr | 12.967 | 10.245 | 10.254 | -20.906% | -0.336% | -21.032% |
| arbitrary-ranges/ranges | 20.728 | 20.811 | 21.021 | +0.779% | +1.167% | +1.513% |
| arbitrary-ranges/cidr | 24.703 | 21.249 | 21.331 | -13.823% | +0.332% | -13.677% |
| overlapping-ranges/ranges | 21.954 | 22.024 | 22.155 | -0.443% | +0.731% | +0.783% |
| overlapping-ranges/cidr | 21.983 | 22.001 | 22.118 | -0.077% | +0.870% | +0.260% |

No primary median paired elapsed increase exceeded 5%. Maximum observed RSS,
including warmups, was 98,604 KiB (96.29 MiB), below the 512 MiB limit. These are
medians of six same-round ratios, not ratios of the displayed time medians.

During round 4 of `overlapping-ranges/cidr`, manual process inspection overlapped
B and an agent diagnostic overlapped A. The A interval was checked against saved
command timestamps; the B overlap was reported during the inspection. The primary
six pairs remain intact. The following separate sensitivity calculation excludes
round 4 only for this case, including the whole pair in each comparison:

| overlapping-ranges/cidr comparison | Primary six pairs | Five pairs excluding round 4 |
|---|---:|---:|
| A to B | -0.077% | -0.407% |
| B to C2 | +0.870% | +0.723% |
| A to C2 | +0.260% | +0.128% |

The sensitivity is secondary and does not replace the primary results. The
observed overlap does not establish that diagnostics caused any particular
timing change. A separate diagnostic ran after Core and is reported below; it
does not replace or add a round to the primary matrix.

The complete CLI phase took 90 minutes 39 seconds: 65.67 minutes in measured
processes, 10.91 minutes in excluded warmups, and 14.07 minutes in generation,
verification, and other overhead. Aggregate measured user-plus-system CPU time
was 0.99856 CPU seconds per elapsed second. That evidence supports active
computation; it is not a complete audit of host contention or I/O behavior.

The earlier partial CLI audit passed 9,469 checks and remains preserved. The
final independent audit verified that the original primary inputs and all 288
observations are unchanged. It rehashed all eight fixtures, decompressed all 16
retained shared output archives, and checked 72 output/roundtrip fingerprints.
Those fingerprints match the separately audited macOS and ARM64 runs. Deleted
duplicate files are represented by their original streaming-comparison receipts.

### Separate post-Core CLI diagnostic

One warmup per arm was followed by one measured CBA triplet, using the same
frozen binaries, fixture, and recorded environment fields. Unrecorded inherited
environment fields are not claimed identical. The original six rounds remain
primary; this diagnostic is not an extra primary round.

| Record | Arm | Elapsed seconds | User + system CPU seconds | Peak RSS KiB |
|---|---|---:|---:|---:|
| Warmup | C2 | 22.333 | 22.310 | 41,292 |
| Warmup | B | 21.942 | 21.910 | 41,172 |
| Warmup | A | 22.163 | 22.140 | 41,148 |
| Measured | C2 | 21.861 | 21.840 | 41,244 |
| Measured | B | 22.403 | 22.380 | 41,248 |
| Measured | A | 35.033 | 35.010 | 40,984 |

Measured A took 35.033 seconds versus its 22.163-second warmup and 21.983-second
primary median. Its CPU time likewise rose to 35.010 seconds from a 21.960-second
primary median. The retained evidence does not identify the cause. A single
triplet with this variation does not establish a new speedup or erase the
original result. All six diagnostic processes passed the RSS guard; their
separate terminal receipts record a reaped child and quiescent owned group.

## Final C2 native x86-64 Core results

The corrected harness validated exact ordered results and listed all 56 cases
before timing. Six alternating B/C2 pairs collected the nine-metric full profile;
six pairs covered the six large fragmented wall-only controls. These phases
produced 6,048 and 72 histogram exports respectively. Both empty APIs are covered
by the full profile; no separate x86 empty-only wall control was measured.
The fixtures, batching, fresh result lifetime, and histogram interpretation are
the same as described above. The same frozen binaries and both interposer
libraries were used across profiles, with allocation/ARC hooks disabled in the
wall-only controls. All 648 nonempty full-profile case/run malloc medians were
positive, confirming live allocation sensors.

| Large fragmented fixture / API | B wall-only ms | C2 wall-only ms | Paired change | B allocations/call | C2 allocations/call | Samples per run |
|---|---:|---:|---:|---:|---:|---:|
| IPv4 / ranges | 0.244927 | 0.279679 | +14.19% | 2 | 1 | 1,000 |
| IPv6 / ranges | 0.254591 | 0.278527 | +9.40% | 2 | 1 | 1,000 |
| Mixed / ranges | 0.489279 | 0.567295 | +15.95% | 3 | 1 | 527–611 |
| IPv4 / networks | 39.264255 | 12.431359 | -68.29% | 8 | 7 | 8–25 |
| IPv6 / networks | 258.572287 | 200.867839 | -22.19% | 10 | 9 | 2 |
| Mixed / networks | 307.888127 | 249.069567 | -18.98% | 17 | 15 | 1–2 |

The three large range controls are slower in every one of their six pairs:
IPv4 +14.19%, IPv6 +9.40%, and mixed +15.95% by median paired p50. Their median
paired absolute increases are 34,752, 23,936, and 78,016 ns respectively. These
wall-only results retain the regression with allocation/ARC hooks disabled.
Lower allocation counts did not imply lower elapsed time in this environment.
The three large network controls improve, but the sparse IPv6 and mixed samples
limit what their percentile estimates can establish.

The full profile has 31 of 56 cases above +5% at both p50 and p90, including all
18 range cases at 1,024 and 16,384 ranges. Together with the three wall-only
range cases, this is 68 reported percentile entries across 34 profile/case
combinations. The complete exception list follows; the six individual ratios
and absolute deltas remain in the retained evidence.

| Profile / case | Paired p50 change | Paired p90 change |
|---|---:|---:|
| full-profile / `mixed.aligned.ranges1024.networks` | +15.128% | +15.490% |
| full-profile / `mixed.aligned.ranges1024.ranges` | +26.076% | +26.495% |
| full-profile / `mixed.aligned.ranges16384.networks` | +12.401% | +12.888% |
| full-profile / `mixed.aligned.ranges16384.ranges` | +13.090% | +12.576% |
| full-profile / `mixed.fragmented.ranges1024.ranges` | +26.295% | +28.664% |
| full-profile / `mixed.fragmented.ranges16384.ranges` | +12.654% | +12.343% |
| full-profile / `mixed.singleton.ranges1024.networks` | +16.000% | +15.976% |
| full-profile / `mixed.singleton.ranges1024.ranges` | +26.973% | +27.672% |
| full-profile / `mixed.singleton.ranges16384.networks` | +12.281% | +12.787% |
| full-profile / `mixed.singleton.ranges16384.ranges` | +11.990% | +11.664% |
| full-profile / `v4.aligned.ranges1024.networks` | +17.287% | +17.534% |
| full-profile / `v4.aligned.ranges1024.ranges` | +29.732% | +29.275% |
| full-profile / `v4.aligned.ranges16384.networks` | +15.041% | +14.867% |
| full-profile / `v4.aligned.ranges16384.ranges` | +14.647% | +13.956% |
| full-profile / `v4.fragmented.ranges1024.ranges` | +30.318% | +30.026% |
| full-profile / `v4.fragmented.ranges16384.ranges` | +15.751% | +14.926% |
| full-profile / `v4.singleton.ranges1024.networks` | +17.663% | +17.538% |
| full-profile / `v4.singleton.ranges1024.ranges` | +29.614% | +29.255% |
| full-profile / `v4.singleton.ranges16384.networks` | +14.978% | +14.652% |
| full-profile / `v4.singleton.ranges16384.ranges` | +13.271% | +13.250% |
| full-profile / `v6.aligned.ranges1024.networks` | +16.930% | +16.779% |
| full-profile / `v6.aligned.ranges1024.ranges` | +23.984% | +23.746% |
| full-profile / `v6.aligned.ranges16384.networks` | +11.692% | +11.600% |
| full-profile / `v6.aligned.ranges16384.ranges` | +11.162% | +10.639% |
| full-profile / `v6.fragmented.ranges1.networks` | +12.394% | +13.502% |
| full-profile / `v6.fragmented.ranges1024.ranges` | +24.022% | +23.497% |
| full-profile / `v6.fragmented.ranges16384.ranges` | +10.862% | +10.219% |
| full-profile / `v6.singleton.ranges1024.networks` | +16.872% | +16.730% |
| full-profile / `v6.singleton.ranges1024.ranges` | +27.748% | +27.432% |
| full-profile / `v6.singleton.ranges16384.networks` | +11.815% | +11.713% |
| full-profile / `v6.singleton.ranges16384.ranges` | +11.173% | +10.603% |
| wall-only / `mixed.fragmented.ranges16384.ranges` | +15.947% | +14.802% |
| wall-only / `v4.fragmented.ranges16384.ranges` | +14.189% | +13.842% |
| wall-only / `v6.fragmented.ranges16384.ranges` | +9.402% | +9.130% |

Both empty APIs improve in the full profile: `ranges` falls from 144.511 to
22.055 ns per call (-84.75% by paired p50), and `networks` from 173.951 to
21.471 ns (-87.68%). These are 1,000-call batch means with counters enabled;
no x86 empty-only wall comparison is inferred.

Core histogram counts range from 1 to 1,000 per export. A p90 based on one
observation has no additional tail information, and dividing a batched
percentile by 1,000 does not yield individual-call tail latency. The single-family
and mixed large allocation reductions were one and two per call in every pair,
with fresh result allocations still present. Core process RSS was not measured.
The x86 regressions are unresolved observations for this toolchain and LXC
environment. The evidence does not identify a compiler, processor, ARC, or
container mechanism as their cause, and improvements on other platforms do not
remove them.

The final independent raw audit passed 49,897 checks across the CLI and 6,120
Core exports, rehashing all 7,694 exported regular files and checking the 631
directories. It verified the complete source/pin/binary/preload graph, GNU time
units, output evidence, exact inventories, batch scaling, quantized p50/p90,
paired ratios, and all 68 exceptions. A further 8,018 checks verified the
separate follow-up and correspondence with all 1,020 Core metric/percentile
comparison rows and 48 CLI comparisons. The completed-task status and immutable
export were checked; this is not a global host-process census. Earlier partial
reports and the original diagnostic annotation remain preserved.

## Remaining qualification

- Review the unresolved x86-64 Core regressions and decide the candidate's scope
  before accepting its performance qualification. No cause or remedy is claimed
  from the current measurements.
- Review the final candidate and run the clean committed-tree release gates and
  required release CI before any release action.

The [draft 0.4.0 notes](../../../ReleaseNotes/0.4.0.md) summarize the intended
release changes. They remain unpublished; completed data audits do not authorize
a release or remove the reported performance exceptions.


## Follow-up: Swift 6.3.3 and 6.4.2 on native x86-64 Linux

**Follow-up outcome:** Swift 6.4.2 does not resolve the lazy projection regressions. Explicit append loops improve every selected nonempty case under both compilers, while small empty-case costs remain. The direct variant is a candidate for further qualification, not an accepted release.

This follow-up compares eager `map`, `lazy.map`, and explicit `for`/`append`
loops under both Linux toolchains. Every arm starts from the same C2 source,
retains both empty guards and capacity reservations, and uses the same published
swift-cidr 0.10.0 revision and dependency locks. The eager arm is a new control
with C2's empty guards; it is not the historical B source or binary. Only the
four projection constructions differ across the three source variants.

Before this run, the container's disk was expanded from 40 to 64 GiB. Its visible
allocation remained four CPUs and 8 GiB memory on the same Xeon E5520 host.
Swift 6.4.2 was installed with signature verification alongside 6.2.4, 6.3.3,
and 6.4.0. Swift 6.3.3 remained the default. Both compared compilers report
`x86_64-unknown-linux-gnu`. Previous measurements remain preserved and are not
combined with these new pairs. Visible container settings do not establish
dedicated hardware or exclude limits imposed by an ancestor cgroup.

The six cells are E633/L633/D633 and E642/L642/D642, where E is eager, L is lazy,
and D is direct append. Release builds explicitly select SwiftPM's native build
engine, the same language mode, and the same pins. Each compiler has its own
build staging directory and runtime libraries. Each cell's executables and
interposers are copied and hashed before the next source variant is built.

Each of the six cells passes ordered full-array comparisons for all 28 coverage
fixtures and both APIs: 56 cases per cell, or 336 API comparisons. The validation
define applies only to a separate executable target; the timing target retains
the previous fixture and callback source bytes. These checks do not constitute
a new execution of the complete 57-test application suite.

The instrumented follow-up selects the 31 previously affected cases and both
empty cases, measuring the same nine wall/allocation/ARC metrics. Separate
wall-clock controls select all six large fragmented cases and both empty cases.
Selection was frozen before new measurements. This is a targeted follow-up,
not a new full 56-case performance qualification or CLI benchmark run.

Both profiles use six balanced rounds, interleaving all six cells. Every cell
occupies each position once. Comparisons pair the same round and report the
median of six ratios, not a ratio of the two displayed medians. Zero or negative
baselines have no reported relative percentage; absolute changes remain in the
retained analysis. Each case uses three warmups, a configured 300 ms measurement
budget, and at most 1,000 observations. Small and empty cases measure 1,000-call batches. Exported
values are quantized histogram observations, and per-call small-case values are
batch means. Low observation counts limit interpretation of p90.

The runner binds source, executable, interposer, compiler, and Swift runtime
identities. It checks visible resources before each invocation, records progress
after completed validated invocations, and enforces a 300-second command deadline.
All builds and installation on the benchmark host had stopped before measurement. The cross-version
comparison measures complete toolchains and their runtimes, rather than an
isolated optimizer change.

The first Swift 6.4.2 build attempt compiled all targets but stopped before
validation because a deprecation warning was included in the reported binary
directory. A small harness correction selects the single absolute directory
line. The original builder and failed attempt remain preserved; the correction
does not change Swift source or build flags. Swift 6.4.2's native-engine
deprecation warning remains in the logs.


### Construction comparison after the toolchain upgrade

Swift 6.4.2 did not remove the lazy-map regression in this selected native x86_64 Linux experiment. Under each compiler, lazy mapping was more than 5% slower than eager mapping in 32 of 33 focused cases at both p50 and p90, including all 31 nonempty cases. Direct append was faster than both alternatives in all 31 selected nonempty focused cases and all six large wall-only controls on both toolchains. This is a selected follow-up, not full-suite or cross-platform acceptance.

E means eager map, L lazy map, and D explicit append loops. Each keeps the same swift-cidr 0.10.0 dependency, empty guards, reservations and ordering; E is not the earlier dependency-only B binary. Displayed times are medians of the six run p50 values. Percentages are medians of the six same-round ratios, not ratios of the displayed medians. Negative changes mean less elapsed time.

All large cases below use 16,384 fragmented ranges per active family. The mixed fixture has 16,384 ranges in each family. Times are milliseconds per call; six decimal places preserve the recorded integer-nanosecond medians.

| Swift | Case | E ms | L ms | D ms | E→L | E→D | L→D |
|---|---|---:|---:|---:|---:|---:|---:|
| 6.3.3 | v4 ranges | 0.244991 | 0.279807 | 0.138879 | +14.181% | -43.309% | -50.366% |
| 6.3.3 | v4 networks | 38.936575 | 12.365823 | 8.898559 | -68.178% | -77.165% | -28.167% |
| 6.3.3 | v6 ranges | 0.254655 | 0.278271 | 0.156479 | +9.324% | -38.527% | -43.770% |
| 6.3.3 | v6 networks | 255.623167 | 201.228287 | 184.549375 | -21.231% | -27.747% | -8.175% |
| 6.3.3 | mixed ranges | 0.491263 | 0.567551 | 0.293887 | +15.634% | -40.190% | -48.219% |
| 6.3.3 | mixed networks | 306.315263 | 246.513663 | 225.509375 | -19.677% | -26.190% | -8.004% |
| 6.4.2 | v4 ranges | 0.243263 | 0.271615 | 0.138367 | +11.684% | -43.135% | -49.058% |
| 6.4.2 | v4 networks | 38.666239 | 12.464127 | 8.884223 | -67.853% | -77.044% | -28.574% |
| 6.4.2 | v6 ranges | 0.254527 | 0.277759 | 0.156223 | +9.205% | -38.626% | -43.779% |
| 6.4.2 | v6 networks | 257.589247 | 204.013567 | 190.447615 | -20.950% | -26.291% | -7.116% |
| 6.4.2 | mixed ranges | 0.490751 | 0.555519 | 0.296447 | +13.198% | -39.593% | -46.636% |
| 6.4.2 | mixed networks | 306.708479 | 253.788159 | 233.471999 | -17.575% | -24.118% | -8.005% |

The counts below include the two empty controls. Every direct-append comparison above +5% is an empty case; none of the selected nonempty cases exceeds +5%. These are investigation counts, not statistical significance tests.

| Swift | Comparison | Focused p50 >5% / 33 | Focused p90 >5% / 33 | Wall p50 >5% / 8 | Wall p90 >5% / 8 |
|---|---|---:|---:|---:|---:|
| 6.3.3 | E→L | 32 | 32 | 3 | 3 |
| 6.3.3 | E→D | 1 | 1 | 2 | 2 |
| 6.3.3 | L→D | 0 | 0 | 1 | 1 |
| 6.4.2 | E→L | 32 | 32 | 4 | 4 |
| 6.4.2 | E→D | 2 | 2 | 2 | 2 |
| 6.4.2 | L→D | 0 | 0 | 1 | 1 |

Changing 6.3.3 to 6.4.2 compares the complete compiler/runtime combination. Across all eight wall controls, no variant has a >5% p50 or p90 increase. The focused profile retains the smaller toolchain-specific exceptions below; it does not justify describing 6.4.2 as a general performance fix.

| Variant, 6.3.3→6.4.2 | Focused p50 change range | Focused p50 / p90 >5% of 33 | Wall p50 change range | Wall p50 / p90 >5% of 8 |
|---|---:|---:|---:|---:|
| E | -6.686% to +6.199% | 4 / 5 | -4.290% to +0.674% | 0 / 0 |
| L | -4.062% to +5.682% | 1 / 1 | -2.928% to +2.765% | 0 / 0 |
| D | -2.678% to +7.108% | 5 / 5 | -0.369% to +3.196% | 0 / 0 |

The empty-case costs remain visible even though the source guards are identical. In the wall-only controls, D costs 1.344 ns more than E for empty ranges and 1.432 ns more for empty networks under 6.3.3; under 6.4.2 these differences are 2.224 ns and 2.336 ns. These are median paired absolute deltas. The measured differences are not attributed to a proven cause.

| Swift | Empty operation | E ns | L ns | D ns | E→D | L→D | D−L paired ns |
|---|---|---:|---:|---:|---:|---:|---:|
| 6.3.3 | ranges | 20.511 | 21.399 | 21.855 | +6.553% | +2.093% | +0.448 |
| 6.3.3 | networks | 22.719 | 22.719 | 24.151 | +6.303% | +6.268% | +1.424 |
| 6.4.2 | ranges | 19.631 | 21.855 | 21.855 | +11.329% | +0.037% | +0.008 |
| 6.4.2 | networks | 22.303 | 23.167 | 24.639 | +10.474% | +6.352% | +1.472 |

The focused profile also retains empty-range D-versus-E increases of +6.648% (+1.336 ns) under 6.3.3 and +14.286% (+2.680 ns) under 6.4.2, plus the 6.4.2 empty-network increase of +10.832% (+2.360 ns). All six absolute values and ratios remain in the accompanying comparisons JSON.

D and L have equal median allocation counts in every selected focused case under both compilers. For the selected large range projections, E performs two allocations for a single family and three for mixed coverage, while L and D perform one. The selected large aligned/singleton network projections use three versus two for one family and five versus three for mixed coverage. Empty-call allocation medians are zero. No zero-allocation claim applies to nonempty returned arrays. The live-sensor audit confirmed allocations and releases for all arms; selected E/D retain medians were zero while L retained positive counts.

The focused profile has 48–1,000 histogram observations per export. Wall controls have 1–1,000: eager large mixed-network cases have only one observation per run, all large IPv6-network cases have two, and lazy/direct mixed-network cases have two. Large IPv4-network runs have 8 eager, 24–25 lazy and 33–35 direct observations. Range controls have 522–1,000 and empty controls have 1,000 observations. Empty/single-range observations are 1,000-call batch means. A one-observation p90 provides no independent tail information. Six repeated paired invocations do not remove these within-invocation limits.

The independent audit passed 169,269 checks, binding all 10,980 raw histogram exports, 3,660 cell summaries and 5,490 comparisons to the verified final archive; all six paired values are retained. Audit success establishes evidence consistency, not performance or release acceptance.

The bounded recommendation is to use explicit append loops as the next candidate for the selected nonempty projection paths, retain the empty guards, and keep the observed empty costs documented. Qualify that candidate with the full Core suite, semantic tests and the required platforms before release. Performance outside the selected x86 cases remains unmeasured for the direct variant; the canonical implementation still uses lazy projections.

### Generated-code evidence

Inspection of the six retained ELF executables verifies that the benchmark
closures call the reviewed projection functions. Both lazy binaries retain
four conversion thunks and per-element indirect calls with stack input/output
copies in the actual reserved-capacity copy helpers. Swift 6.4.2 renames those
helpers to `_copySequenceContents`; it does not inline away these conversions.

Both direct variants inline enum construction into the four output loops,
eliminating those transform calls and associated stack copies. Their normalized
entry instructions match across toolchains, while capacity checks and growth
fallbacks remain. Swift 6.4.2 also changes the eager implementation, including
some loop bounds checks. Function sizes or static call-site counts do not
measure elapsed cost. This inspection does not establish a per-call nanosecond
cost, allocator tcache/mmap behavior, or a page-fault explanation.

The empty-path inspection also identifies a concrete layout difference: eager
ranges returns before creating a stack frame, whereas direct ranges saves and
restores six registers before returning. The reviewed empty paths contain no
allocator, summarizer, transform, retain, or release calls. These instruction
differences do not establish the cause or exact nanosecond cost of the measured
empty-case changes.

### Follow-up evidence and retained state

All 72 invocations completed: 36 for the instrumented profile and 36 for wall
controls. Independent verification passed 169,269 checks over 11,722 exported
files, including all 10,980 histogram exports and every paired value. The 578
files from the earlier build snapshot remained unchanged. All six-cell codegen
inputs matched their build receipts. The benchmark host was idle afterward,
Swift 6.3.3 remained selected by default, and about 19.15 GiB remained free.
The task's SSH connection closed cleanly.

The separate raw follow-up archive is `final-evidence-v1.tar.gz`, 59,455,922 bytes,
SHA-256 `1a2857abc6f30b6d39ea757689bc6bdadd456f54616a84257f0b0569bcbee49d`.
The frozen 167-file source bundle manifest is
`6508c8b0dd4e01fb70dc21f83264033e848a2944863e04489907dff0c2492286`.
The follow-up evidence retains the raw profiles, six build receipts, both builder
versions, source variants, generated-code captures, analysis JSON/CSV, and audit
receipts. The original C2 artifacts and every earlier benchmark result remain
preserved separately. No historical threshold or production Swift source was
changed for this comparison.


## Final follow-up: explicit loops and the empty-call fast path

This follow-up supersedes the earlier candidate-selection statements, whose
source reports and raw results remain preserved. The final source is G: explicit append loops with
cross-module empty guards. E is a contemporaneous guarded eager-map control using
the same swift-cidr 0.10.0 dependency. E is not the historical dependency-only B
binary. Earlier lazy-map, plain-loop and rejected F results remain separate.

**Outcome:** The selected G implementation passes the requested functional tests
and has no G/E timing exception above +5% in the full Swift 6.4.2 Core comparisons,
focused Swift 6.3.3 Linux comparisons, separate wall controls, or any of the 16
CLI cases on each platform. All measured empty wall controls improve. The strict
Linux allocation gates pass. The literal Mac all-observations-zero empty gate
remains false, with a separately isolated ARC-instrumentation signature described
below. These results support the explicit-loop implementation with that recorded
limitation; they do not imply that every acceptance gate is unconditionally true
or that cidrmerge 0.4.0 has been released.

### Implementation and Craig's proposed loops

Craig's four loops are correct: they append family-erased values directly into
the reserved result, preserve IPv4-first order, and avoid the temporary arrays
created by eager `map`. The selected implementation retains those loops and the
same exact combined capacity reservations. `summarizedNetworks()` still obtains
the two typed family network arrays. It does not eliminate every allocation in a
nonempty call, and it does not duplicate swift-cidr's range-to-CIDR algorithm.

The plain-loop D variant left a measurable empty-call cost in the earlier x86
experiment. The first follow-up F separated empty guards from private non-inlined
helpers, but its x86-64 empty-ranges preflight still regressed by 11.29%, or
2.216 ns, against E. That failed candidate and its measurements are retained.

G makes the small public guards `@inlinable` and keeps the nonempty loops in
`@usableFromInline`, `@inline(never)` internal helpers. The guards inspect the
public stored ranges directly, avoiding the non-inlinable swift-cidr `isEmpty`
accessor. Rebuilt ordinary callers can perform the empty check without entering
the projection function. Consumers do not need to discover a different API.
Public signatures, ordering, and semantics are unchanged; the helpers are
source-internal but ABI-public because they are usable from inlinable code.
Their names and behavior therefore need care if binary compatibility is offered.

The inspected Mac and x86 benchmark callers inline G's count guards, skip the
nonempty helper for empty coverage, and use shared empty array storage. This is
evidence for these builds, not a promise that every client/compiler will inline.
The inspected batched callers also hoist the first family-count load outside the
1,000-call loop; their per-call values are amortized batch costs, not isolated
single-invocation latency measurements.
No forced `@inline(__always)`, frozen public layout, platform-specific workaround,
or new dependency was added. The package's Swift tools minimum remains 6.2.

### Functional verification

The final G source passed the complete 57-test, seven-suite application suite in
each of these 14 normal configurations. These are repeated executions of the
same suite, not 798 distinct tests.

| Platform | Compiler | Configurations | Result |
|---|---|---|---|
| macOS ARM64 | Apple Swift 6.4.2 / Xcode 27.2 | Debug, Release | 57/57 each |
| ARM64 Linux | Swift 6.2.4 | Debug, Release | 57/57 each |
| ARM64 Linux | Swift 6.3.3 | Debug, Release | 57/57 each |
| ARM64 Linux | Swift 6.4.2 | Debug, Release | 57/57 each |
| x86-64 Linux | Swift 6.2.4 | Debug, Release | 57/57 each |
| x86-64 Linux | Swift 6.3.3 | Debug, Release | 57/57 each |
| x86-64 Linux | Swift 6.4.2 | Debug, Release | 57/57 each |

The separate ARM64 Swift 6.2.4 dependency-floor run also passed 57 tests, using
swift-cidr 0.10.0, ArgumentParser 1.7.0 and Swift Crypto 5.1.1. Only the intended
ArgumentParser pin changed from the regular lock. ARM Linux smoke checks passed
on 6.2.4, 6.3.3 and 6.4.2; external Core consumers passed on 6.2.4 and 6.4.2;
the public symbol graph was validated on 6.4.2. Mac checks passed for the external
Core consumer, DocC conversion, formatting/content, the iOS 18 ARM64 simulator
Core build, and the remapped/stripped production binary. Frozen Core executables separately validated all 56
ordered output arrays against the same fixture expectations.

The branch remains uncommitted and unpublished. The clean committed-tree release
check and hosted release CI have not been run for this final candidate; the
completed local checks do not stand in for those release gates.

### Matched experiment and interpretation

The macOS host reports 27.2.1 (26B131), Xcode 27.2 (27B52), and Apple Swift 6.4.2.
ARM64 Linux uses native aarch64 Swift in OrbStack. swift-dev uses native x86-64
Swift on the Xeon E5520 host, with four allowed CPUs, an 8 GiB allocation, and the
expanded 64 GiB disk. Swift 6.2.4, 6.3.3 and 6.4.2 coexist on swift-dev; its default
remains 6.3.3. Visible resources do not establish dedicated hardware or exclude
ancestor cgroup limits. Mac and OrbStack timing was serialized because they share
physical hardware. Remote x86 timing ran independently.

Source, dependencies, generators, compiler/runtime identities and executable
hashes were frozen before timing and verified afterward. The two final sources
differ only in `CIDRMergeCoverage.swift`. Both use published swift-cidr 0.10.0.
SwiftPM's native engine and Swift 6 language mode were selected explicitly.
The Mac benchmark graph has 13 pins; Linux has the same applicable pins plus the
Linux-only runtime interposer. CLI executables were explicitly verified as
ordinary optimized production builds, without `-enable-testing`. Build paths
and path-derived SwiftPM package identities differ between some CLI snapshots;
normalized option/runtime audits retain this distinction rather than claiming
byte-identical compiler commands. On Mac, system Swift runtime provenance is
bound through OS identity and linkage because it is delivered in the dyld cache.

The E/D/G preflight uses 26 cases and all six balanced three-arm permutations.
Final Swift 6.4.2 Core qualification covers all 56 cases with nine time,
allocation and ARC metrics. Swift 6.3.3 Linux controls cover the 31 previously
affected cases plus both empty calls. Each toolchain also has eight separate
wall-clock-only controls: six large fragmented cases and two empty cases.
Every final Core profile uses six alternating E/G pairs, three warmups, a configured
300 ms measurement budget and at most 1,000 observations. Empty and single-range
cases measure 1,000-call batches; their per-call times are batch means.

Percentages below are medians of six same-round ratios, not ratios of displayed
medians. Positive elapsed changes mean slower. The five-percent exception screen
is an investigation criterion, not a statistical significance test. Raw exports
are quantized histograms, not chronological traces. Expensive x86 network cases
have as few as one observation in a run; a one-observation p90 has no independent
tail information; with two observations, p90 is the larger observation. The
largest x86 mixed/IPv6 cases therefore do not provide well-sampled tail estimates.
Within-invocation sample counts and every pair are retained.
Instrumented and wall-only timings are not interchangeable. No historical
macOS/Xcode/toolchain results are pooled with these new matched runs.

Instrumented Core results compare G with E. The exception column counts p50/p90 contrasts above +5%, not individual raw observations.

| Platform / Swift | Cases | p50 change range | p90 change range | >5% contrasts | Observations/export |
|---|---|---|---|---|---|
| macOS 6.4.2 | 56 | -68.893% to -6.123% | -67.779% to +2.211% | 0 | 14–1000 |
| ARM64 Linux 6.4.2 | 56 | -70.886% to -10.718% | -71.773% to -11.276% | 0 | 8–1000 |
| x86-64 Linux 6.4.2 | 56 | -77.853% to -2.218% | -77.917% to -2.258% | 0 | 1–1000 |
| ARM64 Linux 6.3.3 | 33 | -69.257% to -14.016% | -70.995% to -13.084% | 0 | 158–1000 |
| x86-64 Linux 6.3.3 | 33 | -44.175% to -8.199% | -42.694% to -8.294% | 0 | 56–1000 |

The separate wall-only cases below contain 16,384 fragmented ranges per active family; mixed contains that many in each family. Times are medians of run p50 values in milliseconds per call.

| Platform / Swift | Large case | E ms | G ms | Paired p50 | Paired p90 | Observations/export |
|---|---|---|---|---|---|---|
| macOS 6.4.2 | mixed networks | 18.169855 | 15.970303 | -12.226% | -11.277% | 15–19 |
| macOS 6.4.2 | mixed ranges | 0.075455 | 0.040671 | -46.107% | -48.663% | 1000–1000 |
| macOS 6.4.2 | v4 networks | 2.397183 | 1.943039 | -18.902% | -17.775% | 124–154 |
| macOS 6.4.2 | v4 ranges | 0.036447 | 0.016959 | -53.371% | -55.427% | 1000–1000 |
| macOS 6.4.2 | v6 networks | 15.370239 | 13.787135 | -10.045% | -10.040% | 20–22 |
| macOS 6.4.2 | v6 ranges | 0.039935 | 0.023447 | -41.318% | -42.454% | 1000–1000 |
| ARM64 Linux 6.4.2 | mixed networks | 34.766847 | 28.516351 | -19.013% | -18.202% | 9–11 |
| ARM64 Linux 6.4.2 | mixed ranges | 0.078655 | 0.042111 | -46.449% | -49.223% | 1000–1000 |
| ARM64 Linux 6.4.2 | v4 networks | 4.878335 | 1.935871 | -59.943% | -60.821% | 58–155 |
| ARM64 Linux 6.4.2 | v4 ranges | 0.037023 | 0.017295 | -53.325% | -55.323% | 1000–1000 |
| ARM64 Linux 6.4.2 | v6 networks | 29.401087 | 23.207935 | -20.752% | -22.114% | 9–13 |
| ARM64 Linux 6.4.2 | v6 ranges | 0.041487 | 0.024799 | -40.190% | -42.796% | 1000–1000 |
| x86-64 Linux 6.4.2 | mixed networks | 312.868863 | 237.469695 | -24.236% | -24.079% | 1–2 |
| x86-64 Linux 6.4.2 | mixed ranges | 0.491647 | 0.296575 | -39.651% | -38.219% | 586–999 |
| x86-64 Linux 6.4.2 | v4 networks | 39.370751 | 8.839167 | -77.597% | -77.582% | 8–35 |
| x86-64 Linux 6.4.2 | v4 ranges | 0.243327 | 0.138367 | -43.150% | -41.658% | 1000–1000 |
| x86-64 Linux 6.4.2 | v6 networks | 260.866047 | 192.806911 | -26.089% | -25.967% | 2–2 |
| x86-64 Linux 6.4.2 | v6 ranges | 0.254527 | 0.156287 | -38.607% | -37.307% | 1000–1000 |
| ARM64 Linux 6.3.3 | mixed networks | 41.820159 | 31.797247 | -24.874% | -25.177% | 7–11 |
| ARM64 Linux 6.3.3 | mixed ranges | 0.112927 | 0.042703 | -62.165% | -60.641% | 1000–1000 |
| ARM64 Linux 6.3.3 | v4 networks | 5.898239 | 1.979903 | -66.633% | -69.922% | 47–153 |
| ARM64 Linux 6.3.3 | v4 ranges | 0.056439 | 0.017335 | -69.219% | -70.833% | 1000–1000 |
| ARM64 Linux 6.3.3 | v6 networks | 35.045375 | 25.055231 | -27.929% | -22.587% | 8–13 |
| ARM64 Linux 6.3.3 | v6 ranges | 0.056639 | 0.024719 | -56.239% | -57.269% | 1000–1000 |
| x86-64 Linux 6.3.3 | mixed networks | 313.786367 | 232.095743 | -26.157% | -26.062% | 1–2 |
| x86-64 Linux 6.3.3 | mixed ranges | 0.486783 | 0.293759 | -39.674% | -38.736% | 608–1000 |
| x86-64 Linux 6.3.3 | v4 networks | 39.788543 | 8.902655 | -77.706% | -77.703% | 8–35 |
| x86-64 Linux 6.3.3 | v4 ranges | 0.244991 | 0.138623 | -43.376% | -41.779% | 1000–1000 |
| x86-64 Linux 6.3.3 | v6 networks | 259.948543 | 187.367423 | -28.046% | -28.031% | 2–2 |
| x86-64 Linux 6.3.3 | v6 ranges | 0.254655 | 0.156543 | -38.512% | -37.114% | 1000–1000 |

Empty wall-only controls use 1,000 observations per run, each a 1,000-call batch. Times and absolute deltas below are nanoseconds per call after normalization.

| Platform / Swift | Empty API | E ns | G ns | Paired delta ns | Paired p50 | Paired p90 |
|---|---|---|---|---|---|---|
| macOS 6.4.2 | networks | 5.503 | 4.189 | -1.292 | -23.573% | -24.156% |
| macOS 6.4.2 | ranges | 5.127 | 4.189 | -0.960 | -18.724% | -18.208% |
| ARM64 Linux 6.4.2 | networks | 6.773 | 5.503 | -1.292 | -19.076% | -20.695% |
| ARM64 Linux 6.4.2 | ranges | 6.419 | 5.501 | -0.896 | -14.008% | -14.737% |
| x86-64 Linux 6.4.2 | networks | 22.279 | 18.751 | -3.536 | -15.871% | -15.871% |
| x86-64 Linux 6.4.2 | ranges | 19.631 | 18.759 | -0.872 | -4.442% | -4.442% |
| ARM64 Linux 6.3.3 | networks | 6.815 | 5.523 | -1.292 | -19.074% | -18.623% |
| ARM64 Linux 6.3.3 | ranges | 6.459 | 5.481 | -0.978 | -15.142% | -14.292% |
| x86-64 Linux 6.3.3 | networks | 22.727 | 18.735 | -3.992 | -17.565% | -17.652% |
| x86-64 Linux 6.3.3 | ranges | 20.511 | 18.751 | -1.760 | -8.581% | -8.538% |

### Allocations and the Mac instrumentation boundary

| Platform / Swift | Every raw empty total-allocation observation zero | Nonempty G≤E in each pair, p50/p90 |
|---|---|---|
| macOS 6.4.2 | False; diagnostic below | Pass |
| ARM64 Linux 6.4.2 | Pass | Pass |
| x86-64 Linux 6.4.2 | Pass | Pass |
| ARM64 Linux 6.3.3 | Pass | Pass |
| x86-64 Linux 6.3.3 | Pass | Pass |

For nonempty projections, G's measured total-allocation p50 and p90 do not exceed
E in any paired case. Direct loops remove the arrays used solely to erase the
address family. For example, large range projections use one result allocation
instead of E's two for one active family or three for mixed coverage. Typed
network arrays and the returned array still exist. The strict zero-allocation
result applies to the measured Linux empty paths, not nonempty output or every
platform. The Mac raw gate has the instrumentation exception described next.

The strict Mac all-observations-zero empty-allocation gate remains **false**.
Each of its 24 empty count exports contains 999 zero observations and one
allocation; the corresponding byte export has one 16-byte observation. Both
arms and both APIs show the same pattern. Empty p50/p90 values are zero, and
every empty object-allocation observation is zero. No raw event was discarded,
subtracted or replaced to make a gate pass.

A separate frozen diagnostic has no CIDRMergeCore dependency or symbol. It
passes fixed empty family-erased arrays to `blackHole` in the same scaled loop.
Three fresh runs with all nine metrics reproduce the one-allocation/16-byte
event for both array types. Three runs of the identical executable with ARC
metrics disabled record all 1,000 malloc observations as zero for each type.
All 84 exports are retained and independently checked. This isolates the
signature to enabling ARC measurement, independently of a Core call.

Preserved Benchmark source and codegen support lazy ARC counter initialization
as the explanation: warmups precede hook installation, malloc statistics are
snapshotted before ARC statistics, and lazy `UnsafeAtomic` counters allocate
storage. No allocation backtrace proves the precise runtime site. This bounded
instrumentation diagnosis supports continuing qualification while leaving the
literal primary gate false. It does not establish universal allocation behavior.

### Complete CLI regression comparison

Each platform checks eight deterministic million-record fixtures in both ranges
and CIDR representations. Before timing, 56 commands verify generation,
byte-identical E/G output, fixed cardinalities and exact CIDR-to-range roundtrips.
Each platform then runs 32 excluded warmups and 192 measured invocations: six
alternating pairs across all 16 cases. Shared output archives, full timing data,
verification receipts and error streams are retained. Redundant candidate and
roundtrip files are removed only after equality is checked.

High-resolution elapsed time includes the launcher and native `time` wrapper;
raw BSD/GNU wall/CPU/RSS output is retained separately. Receipt writes occur
outside the interval. The harness uses a stderr pipe to avoid timeout polling
quantization, and it does not subtract estimated overhead. Process deadlines,
progress receipts, a free-disk floor and the 512 MiB RSS cap remain enforced.
There are no automatic retries. The CLI uses the existing typed coverage path;
these results are an end-to-end regression check and do not attribute a CLI
speedup to the family-erasing Core projections that it bypasses.

| Million-input case | macOS E→G | ARM64 Linux E→G | x86-64 Linux E→G |
|---|---|---|---|
| disjoint/ranges | +0.051% | +2.059% | +0.910% |
| disjoint/cidr | -1.857% | -2.287% | +0.025% |
| siblings/ranges | -0.377% | -0.566% | +0.924% |
| siblings/cidr | -1.024% | +1.227% | +1.089% |
| subsumed/ranges | -0.008% | +0.632% | +0.394% |
| subsumed/cidr | -0.374% | -0.821% | -0.196% |
| bgp-like/ranges | -0.445% | -0.423% | -0.101% |
| bgp-like/cidr | +1.222% | -0.559% | +0.448% |
| rpki-like/ranges | -1.205% | +2.739% | -0.657% |
| rpki-like/cidr | +0.300% | -2.288% | -0.524% |
| mixed/ranges | -0.727% | +1.636% | -0.627% |
| mixed/cidr | -1.259% | +1.327% | +2.202% |
| arbitrary-ranges/ranges | -0.558% | +0.649% | -0.270% |
| arbitrary-ranges/cidr | -1.308% | -0.529% | +0.057% |
| overlapping-ranges/ranges | +0.680% | -0.843% | -0.034% |
| overlapping-ranges/cidr | -0.678% | +1.270% | +0.254% |

| Platform / Swift | Peak RSS including warmups | Limit | Elapsed >5% cases |
|---|---|---|---|
| macOS 6.4.2 | 142.781 MiB | 512 MiB | 0 |
| ARM64 Linux 6.4.2 | 85.566 MiB | 512 MiB | 0 |
| x86-64 Linux 6.4.2 | 87.027 MiB | 512 MiB | 0 |

### Preservation, failed attempts and remaining scope

All earlier C2/lazy, compiler-comparison, D and F evidence remains intact. This
section is appended to the previous report without changing its original bytes.
The old report, benchmark overview and release-note drafts were also copied and
hashed before editing. Previous deliverable archives and patches retain their
original names and hashes. The new qualification has separate result directories
and delivery files; historical threshold JSON is not regenerated by this work.

Preparatory failures are retained separately from product results. They include
platform-specific pin validation, generator invocation/SDK fixes, an execution
permission failure in the smoke helper, and a preliminary x86 CLI build that
was replaced by an explicitly matched production build before timing. The
public Swift image pull initially invoked a saved Docker credential helper;
an isolated anonymous configuration and helper-free path resolved it without
user credentials or global OrbStack configuration changes.

Mac CLI attempt v1 passed all 56 verification commands but its first excluded
warmup failed when BSD `time` could not query `kern.clockrate` under restricted
execution. It produced zero measured observations. The successful v2 attempt
repeated the identical source, frozen binaries, configuration and protocol with
the required timing query permitted. The failed attempt was not merged into v2.
Audit-adapter schema fixes, where needed, change offline validation only and
retain their failed audit receipts; they do not alter benchmark observations.

The selected Core source SHA-256 is
`b4931cd59d00b1cef83acc68b62a335c90f966335a2c71d6684aa816c2feb180`.
The v2 source-freeze manifest is
`661a495260cfd5d03d72deadb470817f60e893d3cb42c41f55730712ce8d2465`;
the v2 harness manifest is
`b660373a16b637e05ab47741bd328a85a8cbdddffe1d59f08080866abe0d632d`.

The separate frozen Mac/ARM archive is 187,773,383 bytes, SHA-256
`5c1583aa862d60fe0a63edf482e4cfe7128e52b3670f76717f09400c185c22a0`.
It contains 21,155 payload files plus 11 inventory metadata files, including all
17,436 retained histogram exports from those hosts and the allocation diagnostic.
Its source files and every archived member were independently hashed. Build
caches and exact source-staging duplicates are excluded with explicit inventories
and reconstruction aliases; unique dependency-floor overrides are retained.

The frozen x86 archive is 119,968,639 bytes, SHA-256
`5c96bf49d07c60b2c5fbf3fe715d8f609cc4da5db25c41f4af1849ef972e87c7`.
Its manifest SHA-256 is
`db677a6007d6bcb03d76c697c106d9ebf2992098ab6adefd4a646e762e9c2ee8`;
all 12,748 exported files were verified after extraction. Independent raw-data
reviews are separate from the immutable export and retain the original inventory.

The new delivery bundles these archives, their verification receipts, independent
reviews, final report, frozen reporting inputs, and the repository-root patch.
The patch is verified by applying it to an isolated archive of base commit
`af92697968338bdbd5bcff416b0a5edfcdeb16be` and comparing its resulting files with
the final checkout. The delivery receipt records the final bundle hash. Neither
archive embeds a claim that the Mac strict empty-allocation gate passed.

The measurements qualify these fixtures and toolchains; they do not establish
universal performance, a dedicated-host result, or deployment readiness. Review
the final source and run the clean-tree and hosted release gates before any
cidrmerge 0.4.0 publication. No commit, tag, push, or release was performed for
cidrmerge in this follow-up.
