# ASCII input fast-path prototype — 2026-11-15

> Publication note: This report describes the frozen prototype before the separately authorized commit and merge; statements below about uncommitted state refer to that experiment stage.

**The repeatable-gains criterion passes on the measured ASCII workloads.** Paired median elapsed reductions are 46.15–58.56% on macOS ARM64, 77.63–85.11% on OrbStack ARM64 Linux, 82.78–89.95% on swift-dev x86-64 Linux. All 198 individual elapsed pairs favor the candidate. No elapsed-time or peak-RSS pair regresses by more than 5%; no regression follow-up was triggered. Small RSS changes are inconclusive as evidence of an allocation reduction.

This prototype adds an ASCII line-preparation path while keeping swift-cidr's existing parsers. The implementation and focused tests remain uncommitted on `perf/ascii-text-input`, based on main `6703901011fd17da2b07c3edd6e0eea52d04ff46`.

## Plan and patch

1. Freeze main and the candidate with identical manifests and all eight locked dependency revisions.
2. Change line preparation in `TextInputLoader.consumeLine`; preserve input reading, classification, parsing, normalization and collection behavior.
3. Gate timing on complete tests and differential checks, then compare the original eleven workload groups separately on three native architectures/platforms.

The [production patch](production.patch) scans raw bytes for non-ASCII data and records the first `#`. An entirely ASCII line uses the prefix before that `#`, trims boundary bytes `0x09...0x0D` and `0x20`, skips an empty token, and constructs one token `String`. The scan continues after `#` until it has checked the whole line or found a non-ASCII byte. Any non-ASCII byte selects the original CR/BOM handling, strict UTF-8 decoding, Character-based comment splitting and Unicode trimming.

The fallback is necessary even for non-ASCII bytes after a comment marker: invalid UTF-8 must still fail, and `#` plus a combining mark/keycap can be a different Character from the ordinary separator. The existing normalization comparison still formats the parsed value; this experiment does not remove it. Both reading loops, the classifier, public APIs, output/statistics, compiler floor and dependency requirements are unchanged. There is no local swift-cidr package substitution: both variants use release 0.10.1, revision `5e4b3d2f881340a6ced05742429f1bd680dfd1e0`.

Source snapshots contain 142 baseline and 143 candidate files. The only production difference is `Sources/CIDRMergeCLI/TextInput.swift`; the candidate adds `Tests/CIDRMergeCLITests/TextInputASCIITests.swift`. SHA-256 of the candidate production file is `1e917f8da0c59b5ca4178be32536bf74a3f02856b9da305b88afa30094d33716`; the test file is `fac34b2a617ff9848eeb135146f067182281a199baa5b5a80d5c075bb89809ad`.

## Tests and compatibility

| Platform/toolchain | B Debug | B Release | C Debug | C Release |
|---|---:|---:|---:|---:|
| macOS ARM64, Apple Swift 6.4.2 | 57 | 57 | 69 | 69 |
| OrbStack native ARM64 Linux, Swift 6.4.2 | 57 | 57 | 69 | 69 |
| swift-dev native x86-64 Linux, Swift 6.4.2 | 57 | 57 | 69 | 69 |
| OrbStack ARM64 Linux, Swift 6.2.4 floor | — | — | 69 | 69 |

All **894 full-suite test executions** passed. The 12 added focused tests also passed in an initial targeted Debug run. They exercise both address families and all three input forms; exact normalization counts; ASCII boundary whitespace; rejected interior/control bytes; Unicode whitespace/comments; combined `#` Characters; invalid UTF-8 before/after comments; BOMs; CRLF/repeated CR; EOF; exact diagnostics; and FileHandle/Data agreement across the 64-KiB read boundary, including split Unicode and invalid bytes.

Tests preserve observed legacy BOM behavior. On the tested Foundation implementations, decoding also consumes a leading BOM, so some later-line/repeated-BOM inputs already succeed. The prototype retains that behavior rather than imposing a stricter rule.

The portable differential gate ran 60 byte fixtures through 77 CLI cases per platform: **231 comparisons / 462 child invocations**, with exact agreement in status, stdout, stderr, statistics, raw/JSON files and checksum sidecars. Each platform had 26 successful-input cases and 51 expected rejections. Both variants receive identical source labels. Gate controls include a passing B/B comparison, a deliberately failing binary caught in all 77 cases, and refusal to overwrite existing results. The gate does not time these cases.

Candidate strict formatting, tracked-content audit, documentation, external Core-consumer and CLI smoke checks passed on macOS; ARM64 Linux smoke/documentation checks also passed. The floor remains Swift 6.2. The initial targeted test attempt was blocked by SwiftPM's manifest sandbox (`sandbox_apply: Operation not permitted`); the authorized rerun and all full suites passed. Original failure logs are retained.

## Verification method

Each platform retains ordinary release CLI binaries copied **before** test builds, complete source inventories, exact pins, compiler/runtime identifiers, fixture and reference hashes, harnesses, native process records, stdout/stderr and every observation. Binary hashes are checked again by the differential and timing gates. macOS system runtime images are identified by dyld shared-cache UUID; Linux execution uses explicit toolchain/runtime paths, with before/after SHA-256 checks of `libswiftCore`. The recorded immutable ARM64 image identifies the rest of that runtime. On swift-dev, a complete linked-library hash inventory and byte snapshot were added after measurement; that broader inventory is labeled postmeasurement and does not claim a premeasurement hash for every library.

| Platform | Recorded environment |
|---|---|
| macOS | Apple M1 Max, 10 CPUs, 64 GiB; macOS 27.2.1 (26B131); Xcode 27.2 (27B52); Apple Swift 6.4.2 (`swiftlang-6.4.2.1.9`) |
| ARM64 Linux | Native aarch64 in OrbStack on the same Mac; 10 allowed CPUs, about 15.7 GiB guest memory; kernel `7.2.12-orbstack-00394-gbecdd6130068`; Swift `6.4.2-RELEASE` |
| x86-64 Linux | swift-dev, Intel Xeon E5520 at 2.27 GHz; four allowed CPUs, 8 GiB guest memory; Ubuntu 24.04.5 LTS, kernel `6.14.8-2-pve`; Swift `6.4.2-RELEASE` |

The eight original split-family corpora and three native mixed cases reuse the original exact bytes and independently verified coverage references. Each original corpus has one million records before family splitting. These performance fixtures contain ASCII CIDR lines; the range-derived fixture is already expanded to CIDRs. Address/range/Unicode/error behavior is covered separately by correctness tests.

One excluded warmup per configuration precedes six alternating BC/CB measured pairs, with rotating case order. Each platform retains **132 measured samples / 192 child processes and 22 warmup samples / 32 children**. Across all platforms this is 396 measurements and 66 warmups. Every complete output's byte count and SHA-256 matches the preserved independent reference. No outliers are removed and no candidates are pooled.

Elapsed time uses the established monotonic process wrapper. macOS CPU/RSS comes from BSD `/usr/bin/time -p -l`; Linux uses `wait4` for the exact child, converting RSS from KiB to bytes. Split-family elapsed and CPU time are sums of sequential processes; peak RSS is their maximum. Native mixed cases use one process. Builds, tests, fixture generation, audit hashing and profiling are outside measurement windows. Mac and OrbStack timings ran separately. Disk checks preceded builds; the 3-GiB minimum was enforced during measurement without cleaning old results.

Percentages below are medians of six per-round `(C/B - 1) × 100` changes, not ratios of the displayed medians. The brackets give the full minimum–maximum range across those six paired changes. Negative values favor C. Elapsed and RSS medians, individual samples, CPU measurements and all paired statistics are preserved in [portable evidence](evidence/manifest.json). These exports explicitly distinguish transformed portable copies from the original raw evidence hashes.

## Measurements

### macOS ARM64

| Suite / case | B elapsed (s) | C elapsed (s) | Paired elapsed change [min, max] | B RSS (MiB) | C RSS (MiB) | Paired RSS change |
|---|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.598 | 0.252 | -57.85% [-59.02, -57.57] | 70.27 | 70.17 | -0.11% |
| split / ipv6-disjoint | 0.926 | 0.460 | -49.97% [-52.31, -48.83] | 167.11 | 167.07 | -0.02% |
| split / mixed-disjoint | 0.770 | 0.366 | -52.38% [-52.95, -50.76] | 86.88 | 86.84 | -0.02% |
| split / mixed-permuted | 0.859 | 0.461 | -46.15% [-46.72, -44.45] | 86.91 | 86.84 | -0.05% |
| split / mixed-overlap | 0.759 | 0.364 | -52.09% [-52.80, -51.39] | 71.27 | 71.16 | -0.12% |
| split / mixed-adjacent | 0.686 | 0.285 | -58.56% [-59.41, -57.08] | 71.51 | 71.45 | -0.05% |
| split / bgp-like-ipv4 | 0.742 | 0.368 | -50.33% [-51.14, -49.54] | 50.88 | 50.98 | +0.84% |
| split / range-derived-mixed | 0.787 | 0.375 | -52.37% [-54.21, -52.11] | 94.98 | 94.91 | -0.07% |
| native / mixed-disjoint | 0.770 | 0.360 | -53.18% [-53.40, -52.20] | 119.42 | 120.02 | +0.15% |
| native / mixed-permuted | 0.870 | 0.461 | -47.31% [-48.24, -45.64] | 119.85 | 120.12 | +0.39% |
| native / mixed-overlap | 0.765 | 0.357 | -53.24% [-55.32, -52.38] | 83.48 | 83.58 | +0.05% |

All 66 elapsed pairs favor C. Median paired CPU reductions across groups range from 48.24% to 62.50%. Full CPU/RSS spreads and all pairs: [comparisons](evidence/macos/comparisons.json); [samples and warmups](evidence/macos/samples.json); [validation](evidence/macos/validation.json).

### OrbStack ARM64 Linux

| Suite / case | B elapsed (s) | C elapsed (s) | Paired elapsed change [min, max] | B RSS (MiB) | C RSS (MiB) | Paired RSS change |
|---|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 1.991 | 0.332 | -83.26% [-83.48, -82.50] | 42.74 | 42.22 | -1.17% |
| split / ipv6-disjoint | 2.620 | 0.552 | -78.86% [-80.77, -68.81] | 111.43 | 110.90 | -0.47% |
| split / mixed-disjoint | 2.308 | 0.436 | -81.17% [-81.46, -80.22] | 65.70 | 65.17 | -0.80% |
| split / mixed-permuted | 2.434 | 0.529 | -78.32% [-79.08, -76.64] | 73.08 | 72.55 | -0.73% |
| split / mixed-overlap | 2.254 | 0.412 | -81.58% [-83.20, -78.20] | 57.83 | 57.29 | -0.93% |
| split / mixed-adjacent | 2.144 | 0.319 | -85.11% [-85.65, -83.88] | 50.44 | 49.92 | -1.03% |
| split / bgp-like-ipv4 | 2.186 | 0.413 | -81.15% [-81.21, -80.41] | 40.27 | 39.73 | -1.26% |
| split / range-derived-mixed | 2.353 | 0.447 | -80.94% [-81.21, -80.26] | 65.58 | 65.05 | -0.80% |
| native / mixed-disjoint | 2.296 | 0.435 | -80.87% [-81.59, -80.49] | 77.13 | 76.62 | -0.68% |
| native / mixed-permuted | 2.385 | 0.529 | -77.63% [-78.70, -77.35] | 84.61 | 84.12 | -0.59% |
| native / mixed-overlap | 2.191 | 0.401 | -81.78% [-83.64, -80.95] | 67.45 | 66.96 | -0.71% |

All 66 elapsed pairs favor C. Median paired CPU reductions across groups range from 77.63% to 85.12%. Full CPU/RSS spreads and all pairs: [comparisons](evidence/arm64/comparisons.json); [samples and warmups](evidence/arm64/samples.json); [validation](evidence/arm64/validation.json).

### swift-dev x86-64 Linux

| Suite / case | B elapsed (s) | C elapsed (s) | Paired elapsed change [min, max] | B RSS (MiB) | C RSS (MiB) | Paired RSS change |
|---|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 8.140 | 0.808 | -89.95% [-90.31, -89.49] | 43.98 | 43.48 | -1.03% |
| split / ipv6-disjoint | 10.502 | 1.693 | -83.82% [-84.43, -83.48] | 112.59 | 112.13 | -0.42% |
| split / mixed-disjoint | 9.260 | 1.254 | -86.45% [-86.77, -86.10] | 66.86 | 66.32 | -0.74% |
| split / mixed-permuted | 9.759 | 1.682 | -82.79% [-83.14, -82.19] | 74.32 | 73.67 | -0.84% |
| split / mixed-overlap | 9.285 | 1.329 | -85.65% [-85.96, -85.18] | 59.07 | 58.53 | -1.02% |
| split / mixed-adjacent | 8.920 | 0.964 | -89.13% [-89.36, -88.89] | 51.59 | 51.09 | -1.07% |
| split / bgp-like-ipv4 | 8.882 | 1.163 | -87.02% [-87.10, -86.38] | 41.43 | 40.87 | -1.38% |
| split / range-derived-mixed | 9.516 | 1.300 | -86.43% [-86.57, -85.53] | 66.73 | 66.19 | -0.95% |
| native / mixed-disjoint | 9.465 | 1.266 | -86.40% [-86.84, -86.25] | 78.35 | 77.77 | -0.72% |
| native / mixed-permuted | 9.821 | 1.689 | -82.78% [-83.14, -82.19] | 85.78 | 85.24 | -0.62% |
| native / mixed-overlap | 9.359 | 1.337 | -85.64% [-86.08, -85.34] | 68.65 | 68.21 | -0.66% |

All 66 elapsed pairs favor C. Median paired CPU reductions across groups range from 82.81% to 89.99%. Full CPU/RSS spreads and all pairs: [comparisons](evidence/x86_64/comparisons.json); [samples and warmups](evidence/x86_64/samples.json); [validation](evidence/x86_64/validation.json).

## CPU profiles and retained failures

Post-timing Time Profiler captures used the exact frozen binaries and the same ordered IPv6-disjoint and native mixed-disjoint fixtures. Instruments attached to an owned CLI waiting on stdin; after capture readiness, the parent supplied the full fixture and captured stdout. All four outputs matched the independent reference hashes. This profiles the stdin reader, which shares `consumeLine`, while the benchmark tables above use file input. It is explanatory sampling evidence, not another timing run.

| Input / variant | Target samples | Samples including comment split | Samples including Foundation trim |
|---|---:|---:|---:|
| ordered IPv6 / B | 948 | 380 (40.08%) | 30 (3.16%) |
| ordered IPv6 / C | 520 | 0 | 0 |
| native mixed-disjoint / B | 783 | 315 (40.23%) | 25 (3.19%) |
| native mixed-disjoint / C | 382 | 0 | 0 |

The source change bypasses the old comment-splitting/trimming path for these ASCII lines, and the sampled stacks are consistent with that change. Categories overlap and must not be summed. Zero sampled stacks is not a zero-allocation claim or proof about every possible call. [Profile counts, anchors and original evidence hashes](profiles.json).

Two earlier profile attempts remain separate: a direct Instruments launch stalled on a macOS Downloads-folder permission prompt and was killed at the capture time limit; the first attach helper waited for a readiness message that was never emitted and captured no workload. The successful helper uses the observed readiness message. Neither failed attempt contributes to timing or profile comparisons. Traces, logs, commands, diagnostic evidence and successful output files remain in the new Downloads bundle.

## Evidence, reproduction and rollback

Full local evidence is under `$HOME/Downloads/cidrmerge-ascii-20261115T170645Z`, with original x86-64 evidence retained at the same Downloads-relative path on swift-dev. Each platform has `sources/` (or the shared top-level snapshots), `bin/`, `control/`, `logs/`, `fixtures/`, and `measurements/`; successful Mac traces are in `macos/profiles-attach-stdin-v2/`. Sources, ordinary binaries, large outputs and traces are retained locally instead of being added to Git.

Independent audits recomputed all group statistics and pairs, checked complete output hashes and native resource records, and verified the balanced sample inventory on all three platforms. Linux carries the frozen reference digest manifest; the original reference output files were also rehashed by the Mac audit. Portable [export manifest](evidence/manifest.json), per-platform validation receipts and [reproduction commands](REPRODUCE.md) bind the concise repository evidence to its original artifacts. The evidence exporter does not replace raw observations.

All 141 other pre-existing cidrmerge tracked files match the starting hashes, including prior reports. The five older untracked swift-cidr result directories retain exactly 3,775 files and their original hashes. Historical reports and threshold JSON files were not changed. The candidate source/test hashes still match the frozen build inputs. No commit, stage, push, merge, dependency update or release is included.

Rollback is limited to reversing `production.patch` and removing the new focused test/report files after review; do not reset unrelated work or delete historical evidence.

## Notes and limits

- The large elapsed reductions are repeatable within this fixed six-pair matrix on each recorded host. They do not establish general Unicode-input gains, a broad workload distribution, tail latency, or performance under concurrent load.
- Mac and Linux runtimes differ; compare B/C within each platform. Do not pool their timings or treat the larger Linux percentage as an isolated compiler effect.
- Peak RSS changes are small relative to retained input and output buffers. RSS is not an allocation count. The token String, existing parser work, normalization formatting and ordinary arrays remain.
- No competitor was rebenchmarked here; historical competitor timings do not form a new matched ranking with this candidate.
- Direct borrowed-byte parsing, avoiding normalization formatting, and other optimization-plan items remain separate experiments. This prototype keeps the Swift 6.2 floor and swift-cidr 0.10.1 dependency.
