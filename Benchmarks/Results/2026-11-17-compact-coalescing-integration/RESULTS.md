# Published compact-coalescing integration

This experiment validates the accepted compact-storage implementation as a published dependency of cidrmerge. It reproduces the macOS range-derived memory improvement: median peak RSS falls from **84.67 to 61.73 MiB**, a paired median reduction of **27.10%**. Throughput changes are generally small or noisy; this is not a general speedup claim. The measured ARM64 range-derived CPU cost and the noisy macOS tiny-input latency result remain explicit below.

The prior cidrmerge PR #25 preserved experiment reports without adopting the upstream branch. swift-cidr PR #25 now supplies the implementation, and signed swift-cidr **0.11.0** is published. cidrmerge **0.4.3** adopts that release. Existing experiments and thresholds are unchanged.

## Sources and scope

- Baseline B: cidrmerge main `5ab794a5a0578c03fd7b52f3b72889de201c09f8`, with swift-cidr **0.10.1** at `5e4b3d2f881340a6ced05742429f1bd680dfd1e0`.
- Candidate C: the same CLI sources/tests with published swift-cidr **0.11.0** at `ae956313ebbcb5a6f9d20b74626ce5b6e2e69839`. Its signed tag object is `24c6acb229c7cb34ec3fb1f09e0839ff614629c1`.
- C changes the manifest, lockfile, notices, README dependency references, external-consumer constraint and minimum-dependency CI gate. All seven other complete dependency pins remain identical. There is no local dependency override.
- Both timed binaries report CLI version **0.4.2**. Version preparation for 0.4.3 happens afterward; the only subsequent CLI source/test changes are the version constant and its assertion. Release documentation, workflow defaults and smoke expectations change accordingly. The frozen candidate patch and full source hashes preserve exactly what was measured.

Coalescing compacts the sorted buffer in place. If every range survives, it returns that buffer. When ranges merge, it copies the reduced prefix into fresh storage. This deterministic policy retains no shrink threshold. Exact coverage, ordering, endpoint behavior, caller-owned values and the generic Sequence API are preserved.

The dependency update also includes the Span octet initializers already on upstream main. This is a whole published-dependency comparison; not every timing difference can be attributed solely to one loop. Swift tools minimum 6.2, Swift language mode 6, macOS 15 and Core's iOS 18 floor remain unchanged.

## Qualification

The exact upstream merged tree passed 311 Debug and 311 Release tests on macOS, ARM64 Linux and x86-64 Linux with Swift 6.4.2, plus both suites on ARM64 Linux with Swift 6.2.4: **2,488 upstream test executions**. All four products and Apple deployment-floor builds passed. Final upstream CI passed all five jobs, including every benchmark build under Swift 6.3.

The complete macOS default threshold check exited 1 for two improvements, with no regression deviations; all 79 historical threshold files are unchanged. Four new Span cases were observed separately, with zero allocation/ARC percentiles but isolated malloc samples. This does not establish unconditional zero allocation. Optional CPU/NIO research benchmark targets retain pre-existing actor-isolation build errors under Swift 6.4.2; default/summarization/Profile builds passed on that compiler.

| Downstream platform/toolchain | B Debug / Release | C Debug / Release | CLI differential | I/O differential |
| --- | ---: | ---: | ---: | ---: |
| macOS, Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 84 |
| ARM64 Linux, Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 86 |
| x86-64 Linux, Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 86 |
| ARM64 Linux, Swift 6.2.4 | — | 85 / 85 | — | — |

That is **1,190 downstream test executions**, **762 CLI differential cases** and **256 I/O cases**. Exact output, diagnostics, exit status, statistics, JSON, checksums and file-output behavior passed. Formatting, content/whitespace audits, documentation or symbol graphs, isolated Core consumers and CLI smoke checks passed. Sources, clean checkout revisions, ordinary binaries, compiler/runtime identities and qualification receipts were checked before and after measurements.

These benchmark qualification checks are distinct from `scripts/check-release.sh 0.4.3`, shipping-compiler CI and four-platform asset validation. Their completion is recorded by the release workflow and release record; this report freezes the benchmark evidence before release publication. Distributed archives use the established Swift 6.2 compatibility toolchain rather than these Swift 6.4.2 benchmark binaries.

## Platforms and method

| Platform | Recorded environment | B/C build backend |
| --- | --- | --- |
| macOS ARM64 | MacBookPro18,2; 10 CPUs; 64 GiB; macOS 27.2.1 build 26B131; Xcode 27.2; Apple Swift 6.4.2 | Swift Build default, identical commands |
| ARM64 Linux | Native ARM64 cached Swift 6.4.2 container through OrbStack; Ubuntu 24.04.5; kernel 7.2.12-orbstack; 10 visible CPUs | Native SwiftPM, identical flags |
| x86-64 Linux | swift-dev; four Xeon E5520 logical CPUs; 8 GiB; Ubuntu 24.04.5; kernel 6.14.8-2-pve; Swift 6.4.2 | Native SwiftPM, identical flags |

Compare B/C within each platform. Backend, architecture, operating system and runtime differences prevent attributing cross-platform absolute times solely to CPU architecture. macOS shared-cache and all 17 linked-image UUIDs match between variants; they are recorded host identities, not copied runtime files. Linux runtime bytes are preserved and match. The swift-dev filesystem was expanded to 128 GiB before qualification and measurement; no historical cleanup was required.

The matrix reuses eight split-family million-entry corpora, three native mixed cases, twelve scale cases at 1,000/10,000/100,000 entries, and two sparse-merge cases with 10,002 and 1,000,002 entries. The earlier separate typed sparse probe had 1,000,001 entries; it is not the mixed fixture here.

Every configuration has one excluded B/C warmup and six alternating B/C–C/B pairs, with rotating case order. Commands use `--raw --representation cidr`. Complete stdout bytes and SHA-256 match preserved independent coverage references; stderr must be empty. Source archives, eight pins, harnesses, fixtures, references, binaries and runtime/toolchain evidence are frozen. Ordinary release binaries are copied before separate test builds.

Elapsed time spans process launch through completion, including I/O. CPU and peak RSS use native `/usr/bin/time -p -l` on macOS and exact-child `wait4` on Linux, converting RSS KiB to bytes. Split-family observations sum sequential child elapsed/CPU and take the maximum child RSS. They are not simultaneous combined RSS.

macOS and OrbStack timing windows were serial, without task builds/tests/profiling or bulk transfers. swift-dev ran independently after its checks. At least 3 GiB free space was required throughout. Identical stdout files are hardlinked only after timing and complete-byte verification within each new experiment's content store; no historical files are linked or changed.

| Platform | Primary observations / warmups | Follow-up observations / warmups | Total measured CLI processes / warmup processes |
| --- | ---: | ---: | ---: |
| macOS | 300 / 50 | 36 / 6 | 396 / 66 |
| ARM64 Linux | 300 / 50 | 12 / 2 | 372 / 62 |
| x86-64 Linux | 300 / 50 | 0 / 0 | 360 / 60 |

All **948 measured observations**, **158 warmups**, **1,128 measured child processes** and **188 warmup child processes** passed independent audits. Primary and follow-up phases remain separate. Every observation is retained. Percentages below are medians of six paired percentage changes, not ratios of the displayed absolute medians. Brackets show the observed six-pair minimum and maximum, not confidence intervals. Negative changes are lower elapsed time or RSS.

## Results

Across the eleven original million-entry configurations:

| Platform | Original-case elapsed median range | Original-case RSS median range |
| --- | --- | --- |
| macOS ARM64 | -1.49% to +1.72% | -27.10% to +0.29% |
| ARM64 Linux | -1.24% to +3.50% | -4.47% to +0.09% |
| x86-64 Linux | -1.17% to +1.00% | -4.33% to +0.16% |


The range-derived configuration reproduces the targeted macOS memory benefit:

| Platform | B elapsed ms | C elapsed ms | Paired elapsed change [min,max] % | B RSS MiB | C RSS MiB | Paired RSS change [min,max] % |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| macOS ARM64 | 237.12 | 236.03 | +0.23% [-1.99, +1.45] | 84.67 | 61.73 | -27.10% [-27.13, -27.08] |
| ARM64 Linux | 271.21 | 279.94 | +3.50% [-1.26, +6.91] | 65.01 | 65.07 | +0.08% [-0.10, +0.10] |
| x86-64 Linux | 864.32 | 872.01 | +0.97% [-2.23, +5.95] | 66.24 | 66.27 | +0.09% [-0.20, +0.18] |


ARM64 range-derived CPU time increases by a paired median **3.50%**, matching its elapsed direction; its observed elapsed spread crosses zero. x86-64 range-derived CPU change is **+1.01%**. These costs remain reported. Native mixed-permuted peak RSS falls **4.47% on ARM64 Linux** and **4.33% on x86-64 Linux**; other Linux memory changes depend on the workload. There is no claim of a universal RSS reduction.

The nearly-full-copy sparse fixture contains 1,000,002 entries:

| Platform | Paired elapsed change [min,max] % | Paired CPU change | Paired RSS change |
| --- | --- | ---: | ---: |
| macOS ARM64 | +0.46% [-0.84, +4.08] | 0.00% (coarse clock) | -1.53% |
| ARM64 Linux | +0.89% [-9.94, +18.08] | +0.88% | +0.02% |
| x86-64 Linux | +1.20% [-1.38, +3.39] | +1.10% | +0.05% |


These new observations are not pooled with the accepted historical experiment's +2.39%/+3.34% x86 CPU medians. No shrink heuristic or additional candidate was introduced.

### Fixed follow-ups and limits

A primary paired-median elapsed or RSS increase above 5% triggered exactly one separate six-pair follow-up. Four configurations triggered; none of the original million-entry or sparse cases did.

| Platform / case | Primary elapsed median | Follow-up elapsed median [min,max] % | Interpretation |
| --- | ---: | --- | --- |
| macOS ARM64 / mixed-permuted-1000 | +6.97% | -3.78% [-33.86, +35.68] | Initial trigger did not repeat; noisy/inconclusive |
| macOS ARM64 / mixed-overlap-1000 | +11.29% | +9.80% [-13.64, +32.82] | Positive median retained; mixed-sign pairs, about +1.37 ms |
| macOS ARM64 / mixed-adjacent-1000 | +5.82% | -9.54% [-25.47, +5.72] | Initial trigger did not repeat; noisy/inconclusive |
| ARM64 Linux / mixed-disjoint-1000 | +5.72% | +2.12% [-12.39, +10.45] | Initial trigger did not repeat; noisy/inconclusive |


The macOS 1,000-entry overlap case retains positive paired medians in both phases: **+11.29% initially and +9.80% in follow-up**, with paired absolute medians about **+1.55 ms and +1.37 ms**. Only three of six follow-up pairs are slower, and its spread is **−13.64% to +32.82%**. This is retained millisecond-scale latency evidence with uncertain attribution, not clean all-case performance parity. The other initial triggers did not repeat. No additional rerun, outlier deletion or phase pooling was used.

macOS CPU fields have 0.01-second resolution. Both CPU fields print 0.00 for every process in these tiny triggered cases; that cannot establish zero CPU cost. Small-input Linux RSS can include a pre-exec parent high-water floor: ARM64 tiny values are roughly 21.7–23.0 MiB, while x86's 24 tiny B/C pairs match within each pair across four rising floor levels. These values do not establish equal application-only memory or allocations. No new RSS-isolation experiment was performed.

Six pairs support bounded observations, not production capacity qualification or a general Unicode/input speedup. Synthetic million-entry cases are useful scale checkpoints, but representative operational traces and explicit latency/memory budgets remain separate work. The current whole-output Data and network-array lifetimes are unchanged.

## Binary size and linkage

| Ordinary unstripped Swift 6.4.2 binary | B bytes | C bytes |
| --- | ---: | ---: |
| macOS ARM64 | 2,447,416 | 2,448,936 |
| ARM64 Linux | 17,361,272 | 17,366,592 |
| x86-64 Linux | 17,775,960 | 17,781,040 |

These include ordinary-build metadata and are not the distributed archive sizes. ARM64 stripped inspection copies are both 3,322,808 bytes. Linkage/runtime identities remain matched within each platform. Final remapped/stripped shipping binaries receive separate four-platform validation.

## Preservation and reproduction

Raw artifacts remain under `$HOME/Downloads/coalescing-release-integration-20261118T031137Z`, with the corresponding complete swift-dev experiment retained. All previous experiments, reports, thresholds and unrelated working files remain untouched. No historical files were deleted. The verified x86 retrieval archive contains all raw output and resource observations; local mapped audits independently rechecked them.

The compact public observation bundles retain every process/sample JSON value, original relative path and raw hash, plus every macOS native-time text. Raw stdout, fixtures, binaries and runtime files stay in Downloads. Public path-redacted copies have separate export hashes; numerical and boolean values are unchanged. Setup failures are retained: upstream raw-export option ordering, x86 test-artifact layout/guard recovery, strict boolean binding of a count-valued I/O receipt, and observation-bundle path/JSON-metadata preparation attempts. None required repeating successful product tests or measured phases. One successful ARM64 baseline Debug log contains invalid UTF-8; its original bytes remain preserved, while the public export records its hash, size, omission reason and successful structured test receipt rather than transcoding it.

- [All 79 phase-separated summaries](summaries.csv) and [all 474 pairs](pairs.csv).
- [Reproduction commands and artifact identities](REPRODUCE.md).
- [Export manifest](evidence-export.json), including original and exported hashes.
- [Upstream implementation PR](https://github.com/RouteObjects/swift-cidr/pull/25) and [signed 0.11.0 release](https://github.com/RouteObjects/swift-cidr/releases/tag/0.11.0).
- [Historical accepted experiment](../2026-11-16-compact-coalescing/RESULTS.md), preserved as its original completion-state report.
