# Upstream macOS qualification

The frozen PR #25 merge tree passed all mandatory library checks on Xcode 27.2 / Swift 6.4.2: 311 Debug tests, 311 Release tests, all four products in both configurations with the macOS 15 floor, all four iOS 18 simulator builds, changed-file formatting, and the default/summarization/Profile benchmark builds. These are deployment-target builds on the current Mac, not execution on macOS 15 or iOS 18 devices.

The complete default threshold check exited 1 with `benchmarkThresholdImprovement`, reporting two formatter p90 improvements (displayed 101→86µs and 114→97µs), and no worse-than-threshold deviations. The original 79 threshold JSON files remain byte-identical. Benchmark 1.35 skips missing static threshold files; the four newly added Span cases were therefore separately observed rather than represented as threshold-gated. No thresholds were created or regenerated.

Raw Span histograms retain every observation: each case has one 1-malloc sample among 962–1019 samples; p50/p75/p90 allocation and ARC counts are zero. All object-allocation/retain/release/retain-release-delta samples are zero. The isolated malloc source is unproven. This does not establish unconditional zero allocations. The default printed table rounds scaled counts, so use the preserved raw histograms for exact count interpretation.

Two optional research targets, CPU and NIO, fail to compile under this toolchain because their `@MainActor benchmarks` variable conflicts with Benchmark 1.35's generated nonisolated registration hook. Their source files are byte-identical on 0.10.1, current main, and this merge tree. No source or dependency workaround was applied. The combined pipeline's false result and each failed log are retained.

One raw-export setup attempt exited 64 before measuring because SwiftPM permission-option ordering was wrong. A distinct corrected attempt succeeded and produced 32 histograms. Both attempts remain preserved.

All 1462 frozen tracked files and all five root dependency pins were reverified unchanged after qualification. Detailed commands, logs, hashes and raw metric summaries are in `qualification-review.json` and its experiment-relative references. No timing remains active.
