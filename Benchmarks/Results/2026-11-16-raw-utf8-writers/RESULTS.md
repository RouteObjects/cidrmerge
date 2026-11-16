# Direct UTF-8 raw output with a complete Data result

## Outcome

The prototype replaces raw-output String construction with swift-cidr’s existing public UTF-8 writers. Whole-output Data accumulation, MergeResult, OutputCommitter, output ordering, JSON, statistics, checksums and atomic file replacement remain unchanged. The experiment is isolated from the separately accepted compact-coalescing change; combined gains have not been measured. Matched measurements show faster complete CLI runs on the large-output fixtures across all three platforms, essentially unchanged peak memory, and a modest repeated roughly 2% cost for the x86-64 two-line overlap cases. It is left uncommitted for review.

## Implementation and baseline

Baseline production source is cidrmerge `8bba7629d7fc9c366ea47680ee6c38badd615092`. Both frozen variants retain all eight original dependency revisions, including released swift-cidr 0.10.1. No local upstream substitution, dependency update, public API or compiler-floor change is included. The working branch `perf/raw-utf8-writers` advanced over report-only commit `ba02b2179b938a816529bf0c04d1a31b7fc6478b` during the earlier experiment’s signed-commit/push handoff; its production baseline remains identical.

The sole production edit is OutputRenderer.swift (53 added / 19 removed lines). Concrete IPv4 and IPv6 helpers reuse temporary buffers sized from public maximum-address constants: 34 and 82 bytes, including two range endpoints, three dots and a newline. CIDR text also fits those buffers. Each line appends only its initialized bytes and newline to the existing Data in one call; the baseline appended text and newline separately. Timing measures this complete rendering change, without separating the contribution of String construction from append overhead. The old reserve policy remains unchanged. Singleton ranges retain both endpoints and the separator.

[Production diff](production.patch) and [complete code/test patch](full.patch). The complete patch applies to the frozen baseline. Ordinary Release generated code confirms the raw-output loops call the matching public family writers and Data append, without the prior description/String-UTF8 conversion calls. This is static code-generation evidence, not a dynamic allocation count. Short IPv6 range text can fit inline String storage; no fixed number of eliminated heap allocations per line is assumed.

## Correctness

Baseline Debug and Release each pass 72 tests on all three Swift 6.4.2 platforms. Candidate Debug and Release each pass 78. Candidate ARM64 Swift 6.2.4 Debug and Release add 156 passing executions; the six new macOS formatting tests also pass AddressSanitizer in a separate build. Total: **1,062 test executions**, counting repeated configurations. Upstream package source is unchanged and its full suites were not rerun for this CLI-only experiment.

The six focused tests cover exact IPv4/IPv6 ranges and CIDRs; maximum widths followed immediately by short lines; empty and single-family results; singleton and mapped addresses; compression ties; every prefix length; seeded random ranges/networks; IPv4-first ordering; final newlines; and ownership of returned Data after subsequent renders. A description-based reference and explicit golden strings check parity independently of the new writer calls.

All **231 CLI differential cases** (77 per platform) pass with exact exit status, stdout/stderr, raw/JSON output, statistics and checksum bytes. The existing atomic-commit tests remain part of the full CLI suites. All eight locked revisions and clean dependency checkouts are verified.

## Matched protocol

Six preserved million-entry fixtures run in native whole-input mode with both `--representation ranges` and `--representation cidr`: IPv4 disjoint, IPv6 disjoint, mixed disjoint, mixed permuted, mixed overlap, and range-derived mixed. The first four produce one million output records; mixed overlap produces two; range-derived mixed produces 500,000 ranges or one million CIDRs. Python independently parses and unions intervals, checks the original coverage/cardinality/address-count oracle, and generates complete canonical range/CIDR byte references. Every timed stdout is compared in full with its reference.

Each of the 12 configurations has one excluded warmup per variant and six measured pairs: **144 measured samples plus 24 warmups per platform**. Pair order alternates B/C and C/B; case order rotates. Sources, ordinary Release binaries, input/reference bytes, harnesses, pins and toolchain/runtime identities are frozen. Ordinary binaries are preserved before test builds. Mac and OrbStack timing run separately, without task builds/tests/profiling or bulk local transfer/hash work. Native x86 work runs on separate hardware.

macOS uses native BSD time CPU/RSS records plus monotonic elapsed time; Linux uses exact-child wait4 CPU/RSS plus monotonic elapsed time. These are complete CLI runs, including parsing, normalization, rendering and output writing. Absolute cross-platform times are not hardware-normalized. x86 stdout files are deduplicated only after timing and full byte verification; all paths and identical bytes remain as hardlinks. The between-sample validation/storage policy applies equally to both variants and is disclosed.

Any configuration with an individual elapsed-time or RSS pair above +5% receives one separate fixed six-pair follow-up. Follow-ups remain separate, including their outliers; no recursive reruns or pooling. Including follow-ups, all three platforms preserve 504 measured samples and 84 excluded warmups (588 complete timed process outputs). Negative changes below favor the candidate. Percentages are medians of paired changes, not ratios of grouped medians.

## Primary elapsed results

| Configuration | macOS | ARM64 Linux | x86-64 Linux |
|---|---:|---:|---:|
| ipv4-disjoint-ranges | -28.87% | -26.89% | -23.56% |
| ipv4-disjoint-cidr | -8.98% | -10.23% | -6.98% |
| ipv6-disjoint-ranges | -24.58% | -22.49% | -21.37% |
| ipv6-disjoint-cidr | -10.61% | -12.05% | -8.01% |
| mixed-disjoint-ranges | -27.10% | -26.51% | -24.00% |
| mixed-disjoint-cidr | -9.51% | -11.31% | -4.55% |
| mixed-permuted-ranges | -22.87% | -23.86% | -18.60% |
| mixed-permuted-cidr | -6.96% | -8.75% | -4.73% |
| mixed-overlap-ranges | -0.39% | -0.36% | +2.08% |
| mixed-overlap-cidr | -0.06% | -1.04% | +2.10% |
| range-derived-mixed-ranges | -13.64% | -18.21% | -7.99% |
| range-derived-mixed-cidr | -10.87% | -16.85% | -3.14% |

Complete native times, paired spreads, CPU and RSS changes: [macOS](macos/TABLE.md), [ARM64 Linux](arm64/TABLE.md), [x86-64 Linux](x86_64/TABLE.md).

## Follow-ups and interpretation

On macOS, the five large-output fixtures improve elapsed paired medians by roughly 14–29% for range output and 7–11% for CIDR output. The two-line mixed-overlap case is effectively flat. Primary RSS paired medians range from −0.57% to +0.09%, consistent with keeping the full Data and network arrays.

Mac mixed-permuted CIDR output improves −6.96% initially and −6.84% in its separate follow-up. Individual slowdowns of +9.51% and +5.14%, respectively, remain in the data; five of six pairs in each run favor the candidate. Those slower Mac elapsed pairs still use less CPU (−4.65% and −2.33%), which is consistent with elapsed-time variability but does not identify its cause. Follow-up RSS paired median is +0.86%. This supports the median throughput improvement while preserving the observed timing variation.

ARM64 Linux large-output range medians improve 18.21–26.89%; CIDR medians improve 8.75–16.85%. Every observed primary/follow-up paired RSS change remains within ±1%. Mixed-disjoint CIDR retains its initial +9.24% elapsed outlier; its separate follow-up improves in all six pairs, with median −8.65% and spread −12.06% to −5.07%. Heavy-overlap follow-ups are inconclusive: range median +1.06% [−14.43%, +13.16%], CIDR median −0.47% [−12.54%, +10.22%]. Range-derived cases retain individual original +0.24% and +1.91% elapsed changes despite favorable medians. Unlike the Mac slow pairs, the ARM outliers also increase CPU time; their cause is not isolated, and the heavy-overlap results remain inconclusive.

On x86-64 Linux, all ten large-output configurations improve their primary elapsed paired medians: 7.99–24.00% for ranges and 3.14–8.01% for CIDRs. IPv4-disjoint CIDR and range-derived CIDR still retain individual +2.24% and +1.12% observations. The two-line heavy-overlap cases show a modest repeated median cost: ranges +2.08% initially and +1.74% in follow-up; CIDR +2.10% and +1.90%. Follow-up CPU medians similarly rise +1.77% and +1.89%. Follow-up elapsed spreads are −1.42% to +5.75% for ranges and −0.77% to +3.74% for CIDR; original +7.46% and +9.49% observations are also retained. The cause is not isolated, and this is not a general throughput-win claim. Primary RSS paired medians range −0.19% to +0.19%, with follow-up medians +0.11% and +0.07%.

The change removes the raw formatter’s String construction path. It does not remove complete network-array storage or full-output Data storage, and it does not promise lower whole-process peak memory. There is no dynamic malloc-count measurement or zero-allocation claim. Results qualify these synthetic fixtures and recorded toolchains, not every workload or carrier deployment.

## Preserved attempts and evidence

The sandbox denied the first macOS hardware-metadata sysctl read; the diagnostic and successful authorized capture remain. The first Mac evidence auditor stopped on its own host-label assumption before raw-sample verification; its receipt/script are retained, and the corrected audit passed. No source candidate was replaced after the freeze and no measured observation was discarded.

The first x86 setup attempt stopped before building because its staged bare Git cache lacked an empty directory Git expects. The setup-only repair and stricter source checks are preserved; source, tests and ordinary measured binaries were not changed by that recovery. All final platform audits passed. No target build, test, or timed invocation failed.

Raw evidence remains under `$HOME/Downloads/cidrmerge-raw-utf8-20261116T145749Z`, with corresponding preserved swift-dev evidence. Earlier experiment directories and the accepted coalescing reports remain intact. The accepted coalescing code/report commits were separately signed and pushed as swift-cidr `f4b673b0834699b713c1a460cc8ad700e7d0278d` and cidrmerge `ba02b2179b938a816529bf0c04d1a31b7fc6478b`; this raw-writer prototype is not included in either commit.

[Reproduction and rollback](REPRODUCE.md). Portable manifests bind selected original evidence to exported files; private paths are replaced with portable variables and JSON numerical values/types are preserved.
