# Optional normalization accounting in cidrmerge

## Change and scope

The measured candidate on `perf/optional-normalization-stats` skips canonical-formatting comparisons used only for normalization statistics when `--stats` is absent. It applies to text and Searchbot input. Parsing still canonicalizes addresses/networks and validates complete input. Cheap input/family/output counters, output bytes, JSON, checksums, errors, atomic output, Foundation usage, dependency versions, and the Swift 6.2 compiler floor are unchanged. Direct internal loader callers retain counting by default; explicitly uncounted loaders leave the internal normalized count at zero.

Baseline: cidrmerge `f362fc902a8e46291fece4f597fc7a910250a1c5` (main, CLI version 0.4.1). Both variants retain all eight locked revisions, including swift-cidr 0.10.1. [Production patch](production.patch), [complete source/test patch](full.patch), [frozen source identities](SOURCE.json).

Text loading threads a Bool through existing readers and short-circuits before `.description`. Searchbot chooses a concrete counting or non-counting `Decodable` wrapper once per document, then uses ordinary synthesized document/array decoding and the same prefix-validation helper. The whole document must decode successfully before its prefixes are appended. No new public API, dependency, compiler attribute or filesystem implementation is introduced.

## Performance reading

Text input without `--stats` has lower paired medians across the measured workloads: macOS: 3.84–16.99% lower elapsed time; ARM64 Linux (OrbStack): 5.74–18.70% lower elapsed time; x86-64 Linux (swift-dev): 7.88–18.46% lower elapsed time. These ranges describe the primary within-host comparisons, not a combined-platform statistic. Searchbot gains are smaller and platform-dependent; ARM64's primary noncanonical case is slightly slower and the small/mixed changes are inconclusive. Statistics-enabled costs remain visible in the control and follow-up tables. Peak RSS is essentially unchanged.

## Correctness

Baseline Debug and Release each pass 78 tests on macOS, ARM64 Linux and swift-dev. Candidate C2 Debug and Release each pass 85 on those three Swift 6.4.2 platforms; C2 also passes 85 in each configuration with Swift 6.2.4 on ARM64 Linux. Unchanged baseline source, ordinary binaries and test evidence are reused from the first candidate's qualification; C2's candidate binaries/tests and all C2 timing are fresh. No C1/C2 measurements are pooled.

Seven added tests cover optional accounting, exact enabled counts, unchanged cheap counters, raw/JSON/checksum parity, file/stdin/Data propagation, split Unicode reads, diagnostics, Searchbot schema/duplicate-key handling, and application statistics gating. All **254 CLI differential cases per platform** pass: exact exit status, stdout, stderr, statistics, both output representations, JSON and checksum bytes. Formatting, content audit and patch checks pass. Upstream package source is unchanged; its suites were not rerun.

## Platforms

macOS measurements use macOS 27.2.1 (26B131), Xcode 27.2 (27B52), Apple Swift 6.4.2, and a MacBookPro18,2 with 10 CPUs and 64 GiB RAM. Native ARM64 Linux uses OrbStack, Ubuntu 24.04.5, Swift 6.4.2, 10 visible CPUs, and no cgroup CPU quota; its compiler-floor checks use Swift 6.2.4. Native x86-64 Linux uses swift-dev, Ubuntu 24.04.5, kernel 6.14.8-2-pve, four allocated CPUs, and Swift 6.4.2; complete CPU, OS, resource, runtime and binary identities are preserved in its platform receipts. Hardware differs across platforms, so conclusions use matched comparisons within each host.

## Matched protocol

Eight deterministic million-entry inputs each run with statistics off and on: 16 configurations. Canonical IPv4/IPv6 and heavy-overlap inputs reuse preserved corpora; additional cases exercise noncanonical mixed networks, bare addresses, explicit ranges, and canonical/noncanonical Searchbot JSON. All new fixtures have independent Python parsing, numeric interval union, canonical output and statistics references. The two Searchbot corpora and noncanonical text-network corpus have identical coverage. Existing behavior counts every bare address as normalized because `IPAddress.description` includes /32 or /128; that behavior is preserved when statistics are enabled.

Each platform has one excluded warmup per configuration/variant followed by six alternating B/C and C/B pairs, with rotating case order: **192 measured samples and 32 warmups per platform**. Complete stdout and stderr bytes are verified after every invocation. The filesystem retains at least 3 GiB free during measurement. Sources, ordinary Release binaries, toolchain/runtime identities, harnesses, input bytes and references are frozen. Mac and OrbStack timing are separated; builds/tests and bulk local work stay outside their timed windows. swift-dev uses separate native x86-64 hardware.

macOS records BSD time CPU/RSS (RSS bytes) and monotonic elapsed time including its launcher. Linux records direct-child wait4 CPU/RSS (KiB converted to bytes) and monotonic elapsed time. Mac CPU figures inherit BSD time's hundredth-second reporting granularity. Absolute cross-platform times are not hardware-normalized. Identical stdout files are hardlinked only after timing and full byte verification. Counts, order, output hashes, metrics and aggregates are independently audited.

Percentages below are medians of six paired changes, `(candidate / baseline - 1) × 100`; negative values favor C2. Ranges in the detailed tables are observed min/max, not confidence intervals. Every elapsed or RSS pair above +5% triggers one separate fixed six-pair follow-up; no outliers are removed and no recursive rerun is used. Including follow-ups, C2 retains **684 measurements and 114 warmups**.

## Elapsed time without statistics

| Input | macOS | ARM64 Linux | x86-64 Linux |
|---|---:|---:|---:|
| Canonical IPv4 networks | -9.34% | -12.64% | -16.14% |
| Canonical IPv6 networks | -16.99% | -18.70% | -18.46% |
| Noncanonical mixed networks | -11.88% | -16.53% | -16.05% |
| Mixed addresses | -11.63% | -14.98% | -16.63% |
| Mixed explicit ranges | -3.84% | -5.74% | -7.88% |
| Mixed overlapping networks | -13.92% | -16.93% | -17.08% |
| Canonical Searchbot JSON | -2.20% | -1.32% | -3.98% |
| Noncanonical Searchbot JSON | -1.50% | +0.70% | -5.33% |

## Statistics-enabled controls

| Input | macOS | ARM64 Linux | x86-64 Linux |
|---|---:|---:|---:|
| Canonical IPv4 networks | -0.27% | +0.29% | +4.66% |
| Canonical IPv6 networks | +0.51% | -0.18% | +3.59% |
| Noncanonical mixed networks | +0.54% | -1.98% | -0.12% |
| Mixed addresses | +0.15% | +1.54% | +1.39% |
| Mixed explicit ranges | +0.90% | -0.44% | +0.18% |
| Mixed overlapping networks | -0.03% | -0.23% | +2.52% |
| Canonical Searchbot JSON | +0.42% | -0.07% | +2.52% |
| Noncanonical Searchbot JSON | +0.99% | +0.02% | +1.07% |

## Peak RSS without statistics

| Input | macOS | ARM64 Linux | x86-64 Linux |
|---|---:|---:|---:|
| Canonical IPv4 networks | -0.01% | -0.30% | -0.03% |
| Canonical IPv6 networks | -0.01% | -0.00% | -0.02% |
| Noncanonical mixed networks | -0.37% | -0.12% | -0.02% |
| Mixed addresses | +0.21% | +0.09% | -0.02% |
| Mixed explicit ranges | +0.44% | -0.03% | +0.02% |
| Mixed overlapping networks | -0.43% | +0.00% | -0.05% |
| Canonical Searchbot JSON | +0.01% | +0.06% | +0.02% |
| Noncanonical Searchbot JSON | +0.00% | -0.03% | -0.01% |

Full native elapsed/CPU/RSS medians, individual paired observations, and spread: [macOS](macos/TABLE.md), [ARM64 Linux](arm64/TABLE.md), [swift-dev](x86_64/TABLE.md), [numeric results](numericresults.json).

## Follow-ups

- macOS: no individual elapsed or RSS pair exceeded +5%; no follow-up required.
- ARM64 Linux (OrbStack): 48 separate measurements and 8 warmups.
  - `text-mixed-addresses-stats`: elapsed median +2.17% [-0.66%, +4.24%]; RSS median +0.06%.
  - `text-mixed-overlap-stats`: elapsed median +2.53% [-1.62%, +5.97%]; RSS median +0.23%.
  - `searchbot-canonical-stats`: elapsed median +0.31% [-1.68%, +6.08%]; RSS median +0.05%.
  - `searchbot-noncanonical-stats`: elapsed median +1.68% [-1.30%, +10.49%]; RSS median +0.02%.
- x86-64 Linux (swift-dev): 60 separate measurements and 10 warmups.
  - `text-ipv4-canonical-stats`: elapsed median -5.08% [-12.16%, +6.76%]; RSS median +0.21%.
  - `text-ipv6-canonical-stats`: elapsed median +2.94% [-8.77%, +6.52%]; RSS median +0.02%.
  - `text-mixed-ranges-stats`: elapsed median -0.47% [-4.29%, +1.56%]; RSS median -0.10%.
  - `text-mixed-overlap-stats`: elapsed median +1.67% [-2.80%, +6.21%]; RSS median +0.05%.
  - `searchbot-canonical-stats`: elapsed median +2.14% [-0.91%, +4.77%]; RSS median +0.02%.

Small or mixed changes are inconclusive. Searchbot's formatting work is a smaller part of complete JSON ingestion; skipping it is not a general JSON speedup claim. Stats-enabled costs and noisy observations remain part of the result. Peak RSS still includes input collections, decoded JSON, merged networks and whole-output Data. This is not a dynamic allocation count, zero-allocation claim, or carrier deployment qualification.

## Earlier candidate and preserved attempts

C1 carried the preference in JSONDecoder.userInfo. Text improved, but the per-prefix lookup was accompanied by repeatable Searchbot costs on macOS: follow-up elapsed medians +3.15% for canonical input without statistics, +3.11% for canonical input with statistics, and +3.85% for noncanonical input with statistics. C1 remains preserved with its full correctness evidence and Mac primary/follow-up (228 measurements, 38 warmups); Linux timing was intentionally held. C2 replaced the context lookup with document-level concrete decoder selection. A separate independent audit verifies C1's Mac observations.

Preserved setup failures include the initial address-statistics oracle assumption, a too-strict differential expectation for an invalid escape inside ignored JSON metadata, sandbox-denied native timing metadata, Swift 6.2.4 module-cache discovery failure, relocated precompiled-module caches, and an initially omitted inherited negative-control script in C2's evidence layout. These were corrected without changing the frozen C2 production candidate; failed logs/receipts and fresh attempts remain. The invalid-escape case checks existing platform-local baseline behavior rather than imposing a new JSON acceptance rule.

The user approved deletion of exactly one older swift-dev build cache after executable/resource preservation and hash verification, reclaiming about 2.25 GiB. Its sources, measurements, logs, reports and frozen benchmark artifacts remain. Other historical results and thresholds are unchanged.

## Evidence and reproduction

C2 evidence: `$HOME/Downloads/cidrmerge-normalization-c2-20261117T020633Z`. C1: `$HOME/Downloads/cidrmerge-normalization-20261117T014017Z`. Corresponding swift-dev evidence is retained under that host's Downloads. [Reproduction commands](REPRODUCE.md), [evidence receipt](EVIDENCE.json).

The measurements and frozen evidence predate publication. Earlier competitor reports and `common-crawlers.json` are outside this change and remain unchanged.
