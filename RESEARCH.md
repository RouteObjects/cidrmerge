# FoundationEssentials and Swift System research archive

This branch, `perf/essentials-system-io`, preserves a completed prototype for
study. It is not scheduled for merge or release. The experiment starts from
`9fe30dde3fd5ad50944064f912fad8c19cfcec62` and retains candidate **R3**.

R3 uses FoundationEssentials on Linux, Swift System file descriptors, and a
reusable 64-KiB read buffer. It keeps the pending-line array and the existing
whole-document and whole-output `Data` contracts. The migration-only control
**E4** and rejected borrowed-line candidate **S2** remain documented separately.

Start with these preserved reports:

- [Results and qualification](Benchmarks/Results/2026-11-17-essentials-system/RESULTS.md)
- [Compatibility behavior and maintenance costs](Benchmarks/Results/2026-11-17-essentials-system/COMPATIBILITY.md)
- [Binary size, linkage, and startup limitations](Benchmarks/Results/2026-11-17-essentials-system/ARTIFACTS.md)
- [Regressions and follow-up measurements](Benchmarks/Results/2026-11-17-essentials-system/REGRESSIONS.md)
- [Reproduction commands and evidence layout](Benchmarks/Results/2026-11-17-essentials-system/REPRODUCING.md)

The implementation and report exports are preserved unchanged from the tested
R3 snapshot. Reports and intermediate notes describe their original experiment
phase: references to an uncommitted prototype or pending work are historical,
not the status of this archival commit. The final results report identifies
the completed qualification and the retained candidate. Export hashes remain
recorded in the report directory's `evidence-export.json`.

The measured improvements are specific to the recorded workloads, platforms,
and toolchains. Linux binary-size reductions come with compatibility code to
maintain; macOS retains Foundation and has a larger executable. Small or noisy
timing changes remain inconclusive. This prototype does not establish zero
allocation, bounded total process memory, or a general Unicode/JSON speedup.

Potential lessons for other RouteObjects CLI tools include reusable read
storage, keeping I/O dependencies out of library products, and comparing
compatibility and buffer changes separately. Each tool still needs its own
behavior and performance validation before adopting these techniques.

Raw benchmark outputs, binaries, runtime snapshots, fixtures, failed controls,
and original figures remain outside Git under
`~/Downloads/cidrmerge-essentials-system-20261117T053919Z` on the Mac and
swift-dev. Subsequent archival work does not alter the recorded measurements.
