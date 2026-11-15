# Bounded read-buffer lifetime prototype

**The prototype meets its memory objective on these macOS workloads.** Paired median peak RSS decreases by 10.82–29.61%, with all 66 individual RSS pairs favoring C. That saves about 9.41–20.24 MiB in paired median peak RSS, depending on the workload. Paired median elapsed changes range from −3.48% to −0.34%, but small or mixed timing differences are inconclusive. Neither Linux platform establishes a performance change; its B/C release `.text` sections are byte-identical.

This experiment compares main `675d534a29fd3c2231d58bb58bf395b6343e233b` (B, including the merged ASCII fast path) with the uncommitted `perf/bounded-read-buffers` candidate (C). Both use the same manifests, compiler settings and eight locked dependencies, including swift-cidr 0.10.1. The Swift 6.2 package floor is unchanged.

## Retention check and implementation

Fresh main was re-profiled before the branch was created. A stack-confirmed rendering snapshot for the ordered IPv6-disjoint fixture still held 326 `NSConcreteData (Bytes Storage)` blocks totaling 21,348,352 bytes. Its complete output matched the independent reference. This satisfied the conditional gate for a prototype; the earlier pre-ASCII profile was not substituted for a fresh baseline.

The candidate extracts one read-and-consume iteration into private `consumeChunk`. On platforms with Objective-C support, `consume` wraps that operation in a throwing `autoreleasepool`. The `Data` and its iteration finish inside the pool; only the owned pending line bytes, parsed values and line counter cross the boundary. Linux calls the helper directly. The final unterminated-line flush and read-error conversion remain outside the loop as before.

No input parser, line preparation, normalization accounting, input classification, public API, output code, dependency or compiler-floor change is included. The Data loader is unchanged. Ordinary release binaries are preserved separately from test builds and profiling copies.

## Live-heap evidence

| Input and checkpoint | B live input-storage blocks | B bytes | C blocks | C bytes |
|---|---:|---:|---:|---:|
| IPv6-disjoint, stack-confirmed parsing snapshot | 149 | 9,764,864 | 1 | 65,536 |
| IPv6-disjoint, post-render output write | 326 | 21,348,352 | 0 | 0 |
| Native mixed-disjoint, post-render output write | 273 | 17,874,944 | 0 | 0 |

For post-render snapshots, the harness waits for the first stdout byte and pauses its owned child while the remaining output is blocked in a pipe. Sampling confirms the output-write stack. It collects `heap --noContent --addresses=all`, `vmmap` and a stack sample, then resumes the child and verifies the complete output. All seven captures, including the earlier baseline rendering gate, matched their references.

The profiling copies have a debugging entitlement. Every executable instruction section was checked against the corresponding ordinary release binary and is unchanged. Timings use the ordinary binaries without profiler attachment. [Heap counts, stack anchors and original artifact hashes](heap-evidence.json) preserve the mechanism evidence.

The class, chunk sizes, phase and disappearance after the intervention support attributing this storage to the file reads; this is an inference from the captures. The parsing snapshots are not synchronized to an identical record count. These are live-storage counts, not total allocations or peak RSS; a zero post-render count does not mean the program allocates nothing. The baseline heap alone does not prove a retaining root. The candidate intervention removes the observed accumulation, and the separate matched measurements below quantify its practical effect.

## Correctness and measurement protocol

Complete Debug and Release suites run for B and C on macOS ARM64, OrbStack ARM64 Linux and swift-dev x86-64 Linux with Swift 6.4.2. B has 69 tests and C has 72. The three focused tests cover multi-chunk lines and split Unicode with final non-newline input, repeated/empty sources with independent BOM handling, and a real FileHandle read error. The existing 77-case differential corpus checks complete stdout, stderr, exit status, output modes, normalization statistics, checksums, Unicode/error precedence and chunk-boundary behavior. Separate baseline characterizations exercise the new cases without changing the frozen B source.

The benchmark reuses all eight original split-family corpora and three native mixed configurations. Each platform retains one excluded warmup per configuration and six alternating BC/CB measured pairs with rotating case order: 132 measured samples and 22 warmups, representing 192 and 32 child processes respectively. Split samples sum elapsed/CPU across families and take the maximum child RSS. Native mixed samples use one process. Every complete output is checked against the preserved independent coverage reference.

Elapsed time uses a monotonic wrapper; macOS CPU/RSS comes from `/usr/bin/time -p -l`, while Linux uses exact-child `wait4` resource usage. B/C binaries, source files, dependency pins, harnesses, fixtures and references are frozen and verified. Linux additionally freezes all resolved linked runtime libraries before timing and rehashes them afterward. macOS records selected toolchain/runtime UUIDs. macOS and OrbStack timed runs are separate, without task-owned builds, tests or profiling during measurement. A 3-GiB free-space guard applies throughout.

Tables show per-variant medians and paired percentage changes; negative changes favor C. Full min/max spreads and all scalar observations remain in the portable evidence. Every individual elapsed/RSS pair above +5% is investigated. Small or mixed changes are inconclusive; no outliers are removed and separate follow-ups are not pooled with the first run.

## Validation results and hosts

| Platform / toolchain | B Debug | B Release | C Debug | C Release | Differential cases |
|---|---:|---:|---:|---:|---:|
| macOS ARM64 / Swift 6.4.2 | 69 | 69 | 72 | 72 | 77 |
| OrbStack ARM64 Linux / Swift 6.4.2 | 69 | 69 | 72 | 72 | 77 |
| swift-dev x86-64 Linux / Swift 6.4.2 | 69 | 69 | 72 | 72 | 77 |
| ARM64 Linux compiler floor / Swift 6.2.4 | — | — | 72 | 72 | — |

All **990 full-suite test executions** and **231 differential comparisons** passed. The Mac supplementary checks passed formatting, release-content audit, documentation, external Core consumer, CLI smoke and whitespace checks. ARM CLI smoke/documentation checks also passed. Three separate baseline characterizations passed in nine CLI processes. The existing focused ASCII tests remain part of both variants' suites.

The Mac is an Apple M1 Max (10 CPUs, 64 GiB) running macOS 27.2.1 build 26B131 and Xcode 27.2 build 27B52, with Apple Swift 6.4.2. Native ARM64 Linux uses the cached OrbStack Swift 6.4.2 image on Ubuntu 24.04.5, kernel `7.2.12-orbstack-00394-gbecdd6130068`, affinity CPUs 0–9 and no cgroup CPU quota. swift-dev reports an Intel Xeon E5520 at 2.27 GHz, Ubuntu 24.04.5, kernel `6.14.8-2-pve`, affinity CPUs 3/8/9/14 and no cgroup CPU quota. Both Linux toolchains, image IDs and runtime identities are in the per-platform metadata and validation receipts. Measurements compare B/C within a platform, not performance between hosts.

## Primary measurements

Each range below spans the eleven **paired case medians**, not the individual-pair spread.

| Platform | Elapsed change range | Peak RSS change range |
|---|---:|---:|
| macOS ARM64 | -3.48% to -0.34% | -29.61% to -10.82% |
| OrbStack ARM64 Linux | -2.12% to +0.53% | -0.01% to +0.10% |
| swift-dev x86-64 Linux | -0.75% to +2.64% | -0.20% to +0.10% |

The primary matrix preserves 396 measured samples and 66 excluded warmups across the three hosts. The following tables display medians; full CPU/RSS spreads and every observation remain linked alongside each table.

### macOS ARM64

| Suite / case | B elapsed (s) | C elapsed (s) | Paired elapsed % [min, max] | B RSS (MiB) | C RSS (MiB) | Paired RSS % |
|---|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.246 | 0.236 | -3.04 [-4.81, -1.35] | 70.19 | 56.15 | -19.99 |
| split / ipv6-disjoint | 0.461 | 0.458 | -0.35 [-1.80, +0.89] | 167.06 | 146.82 | -12.12 |
| split / mixed-disjoint | 0.359 | 0.354 | -0.89 [-3.70, -0.00] | 86.84 | 76.99 | -11.34 |
| split / mixed-permuted | 0.449 | 0.448 | -0.42 [-2.04, +0.86] | 86.86 | 76.99 | -11.36 |
| split / mixed-overlap | 0.356 | 0.353 | -0.34 [-1.68, +0.45] | 71.19 | 61.78 | -13.22 |
| split / mixed-adjacent | 0.281 | 0.275 | -2.48 [-11.62, -0.20] | 71.48 | 61.76 | -13.62 |
| split / bgp-like-ipv4 | 0.362 | 0.357 | -1.44 [-3.37, +0.43] | 50.98 | 35.89 | -29.61 |
| split / range-derived-mixed | 0.396 | 0.369 | -3.48 [-7.65, -0.26] | 94.92 | 84.66 | -10.82 |
| native / mixed-disjoint | 0.359 | 0.354 | -1.39 [-2.75, +0.07] | 118.77 | 101.80 | -14.29 |
| native / mixed-permuted | 0.449 | 0.443 | -1.58 [-2.08, -0.44] | 118.77 | 101.76 | -14.33 |
| native / mixed-overlap | 0.353 | 0.348 | -1.42 [-2.68, +0.46] | 82.11 | 65.66 | -20.03 |

All elapsed/CPU/RSS medians, full spreads and individual pairs: [table](evidence/macos/TABLE.md), [comparisons](evidence/macos/comparisons.json), [samples and warmups](evidence/macos/samples.json), [validation](evidence/macos/validation.json).

### OrbStack ARM64 Linux

| Suite / case | B elapsed (s) | C elapsed (s) | Paired elapsed % [min, max] | B RSS (MiB) | C RSS (MiB) | Paired RSS % |
|---|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.323 | 0.324 | +0.53 [-1.08, +5.34] | 42.21 | 42.23 | +0.04 |
| split / ipv6-disjoint | 0.510 | 0.511 | -0.07 [-1.62, +2.55] | 110.90 | 110.92 | +0.02 |
| split / mixed-disjoint | 0.421 | 0.422 | +0.41 [-2.72, +2.10] | 65.17 | 65.17 | +0.00 |
| split / mixed-permuted | 0.516 | 0.516 | -0.16 [-4.25, +12.76] | 72.54 | 72.55 | +0.02 |
| split / mixed-overlap | 0.379 | 0.380 | +0.28 [-2.58, +2.05] | 57.29 | 57.29 | -0.01 |
| split / mixed-adjacent | 0.307 | 0.306 | -0.55 [-1.75, +1.33] | 49.91 | 49.95 | +0.01 |
| split / bgp-like-ipv4 | 0.403 | 0.406 | +0.01 [-0.58, +2.29] | 39.74 | 39.73 | +0.04 |
| split / range-derived-mixed | 0.426 | 0.426 | +0.45 [-0.85, +3.35] | 65.04 | 65.06 | +0.02 |
| native / mixed-disjoint | 0.424 | 0.425 | -0.40 [-3.92, +2.98] | 76.60 | 76.60 | -0.01 |
| native / mixed-permuted | 0.518 | 0.516 | -0.84 [-1.06, +5.09] | 84.06 | 84.10 | +0.05 |
| native / mixed-overlap | 0.392 | 0.383 | -2.12 [-4.50, +0.13] | 66.92 | 66.98 | +0.10 |

All elapsed/CPU/RSS medians, full spreads and individual pairs: [table](evidence/arm64/TABLE.md), [comparisons](evidence/arm64/comparisons.json), [samples and warmups](evidence/arm64/samples.json), [validation](evidence/arm64/validation.json).

### swift-dev x86-64 Linux

| Suite / case | B elapsed (s) | C elapsed (s) | Paired elapsed % [min, max] | B RSS (MiB) | C RSS (MiB) | Paired RSS % |
|---|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.805 | 0.846 | +2.64 [-0.17, +16.45] | 43.43 | 43.39 | -0.09 |
| split / ipv6-disjoint | 1.672 | 1.705 | +0.47 [-2.65, +3.10] | 112.10 | 112.17 | +0.06 |
| split / mixed-disjoint | 1.253 | 1.258 | +0.80 [-3.26, +4.60] | 66.32 | 66.35 | +0.09 |
| split / mixed-permuted | 1.682 | 1.688 | +0.26 [-1.20, +3.46] | 73.75 | 73.79 | +0.06 |
| split / mixed-overlap | 1.331 | 1.339 | -0.41 [-3.24, +3.50] | 58.55 | 58.44 | -0.20 |
| split / mixed-adjacent | 0.957 | 0.953 | -0.04 [-1.21, +4.11] | 51.08 | 51.13 | +0.10 |
| split / bgp-like-ipv4 | 1.161 | 1.158 | -0.13 [-2.26, +0.68] | 40.97 | 40.94 | -0.13 |
| split / range-derived-mixed | 1.287 | 1.285 | -0.25 [-4.52, +2.08] | 66.29 | 66.23 | -0.13 |
| native / mixed-disjoint | 1.278 | 1.280 | +0.83 [-1.91, +4.63] | 77.83 | 77.85 | -0.03 |
| native / mixed-permuted | 1.698 | 1.704 | +0.92 [-3.87, +4.16] | 85.25 | 85.30 | +0.04 |
| native / mixed-overlap | 1.382 | 1.361 | -0.75 [-5.06, +0.75] | 68.17 | 68.18 | +0.09 |

All elapsed/CPU/RSS medians, full spreads and individual pairs: [table](evidence/x86_64/TABLE.md), [comparisons](evidence/x86_64/comparisons.json), [samples and warmups](evidence/x86_64/samples.json), [validation](evidence/x86_64/validation.json).

## Regression investigations and separate follow-ups

No macOS elapsed/RSS pair exceeded +5%. ARM64 had three primary elapsed triggers across split IPv4-disjoint, split mixed-permuted and native mixed-permuted. x86-64 had two primary elapsed triggers, both split IPv4-disjoint. No primary memory pair exceeded +5%. Each affected case received a fresh six-pair follow-up with one excluded warmup; the results below are never pooled with the primary run.

| Platform / follow-up case | Paired elapsed % [min, max] | Paired RSS % [min, max] |
|---|---:|---:|
| arm64 / native mixed-permuted | -0.67 [-4.18, +4.27] | +0.01 [+0.00, +0.07] |
| arm64 / split ipv4-disjoint | +0.53 [-1.14, +8.33] | -0.03 [-0.08, +0.10] |
| arm64 / split mixed-permuted | +1.20 [-1.99, +4.64] | -0.01 [-0.12, +0.08] |
| x86_64 / split ipv4-disjoint | -2.78 [-13.43, +0.44] | +0.05 [-0.37, +0.49] |

The follow-ups preserve another 48 measured samples and eight warmups. [Separate follow-up manifest, samples, full original scalars, comparisons and audits](followup-evidence/manifest.json).

Two ARM64 IPv4 follow-up pairs remain above +5% (+8.33% and +6.88%, about 26.5 ms and 22.1 ms). CPU time also varies, so these cannot be attributed solely to waiting or scheduling from this evidence. The case median is +0.53%, with changes in both directions. The x86-64 IPv4 median reverses from +2.64% in the primary run to −2.78% in its follow-up. Neither establishes a repeatable Linux gain or slowdown.

A focused code-generation check found the entire B/C `.text` sections byte-identical on both Linux platforms: 1,853,408 bytes on ARM64 and 2,207,093 bytes on x86-64. The loader instruction streams match, and no standalone `consumeChunk` symbol remains. Thus changed loader/`.text` instructions do not explain the observed spread. This does not prove equality of all data/metadata or identify OS, VM or hardware effects; the variation remains unexplained. [Code-generation evidence and artifact bindings](supplemental/codegen.json).

## Preserved failures, artifacts and limitations

The initial ARM64 dependency-cache attempts stopped before compilation because the copied cache lacked its bare repositories; those failed attempts remain under `arm64/attempts/cache-seed-failure-01`. A subsequent Swift 6.2.4 discovered-tests compilation failed with duplicate SwiftShims PCM / missing SwiftOverlayShims before tests executed. A fresh, isolated scratch/cache run passed both suites; the earlier compiler failure remains under `arm64/attempts/floor-swiftshims-failure-02`, and its root cause is not established. Neither failure changed the candidate source.

The first Mac evidence auditor used the prior experiment's progress-log filename and stopped after checking most artifacts. Its failed receipt and original script remain preserved. The corrected auditor reads this run's actual log and passed in a separate receipt. A stale inherited protocol description was corrected before Linux timing; the prior metadata is retained. These are setup/audit corrections, not discarded benchmark observations. [Failure and recovery receipts](supplemental/retained-attempts.json).

Independent native audits checked every primary and follow-up output, raw resource record, schedule and paired aggregate. All seven heap-capture outputs also matched their references. The primary evidence preserves 672 timed child outputs; follow-ups preserve another 70. Original binaries, sources, stdout/stderr, raw metrics, logs, toolchain/runtime identities, heap captures and disassembly remain in `$HOME/Downloads/cidrmerge-read-buffer-20261115T182833Z`, with the original x86-64 evidence retained at the same Downloads-relative path on swift-dev. Only fresh x86 build/cache scratch was removed after validation and after retaining test executables, ordinary binaries, sources, pins, logs and runtime copies; the cleanup has an exact receipt and no cleanup occurred during timing.

Portable [primary evidence](evidence/manifest.json), [follow-up evidence](followup-evidence/manifest.json) and [supplemental artifact bindings](supplemental/manifest.json) distinguish transformed public JSON from unchanged originals. [Reproduction commands](REPRODUCE.md), [production patch](production.patch) and the [focused test](ReadBufferLifetimeTests.swift) accompany the report. Each export retains original byte counts and hashes; it does not replace raw observations.

All 182 pre-existing tracked files other than `TextInput.swift` retain their starting hashes, including historical reports and thresholds. The source and focused test match the frozen build inputs. Older experiment directories were not cleaned or replaced. The prototype remains uncommitted on `perf/bounded-read-buffers`; no dependency update, commit, push, merge or release is included. [Final repository preservation check](supplemental/repository.json).

The measured benefit is bounded Foundation read-buffer lifetime and lower macOS RSS for these fixed million-entry fixtures. Parsed arrays, long pending lines, token Strings, normalization formatting and rendered output still allocate and can grow. No zero-allocation, constant-total-memory, general Unicode throughput or competitor-ranking claim follows. macOS system runtime identity is recorded by OS build and dyld UUIDs, rather than copied out of its shared cache. The Swift 6.2.4 floor checks establish correctness and preserve reported compiler version/core-runtime hash; they do not provide a full pre/post inventory of every floor-toolchain library. No Swift 6.2.4 performance claim is made.
