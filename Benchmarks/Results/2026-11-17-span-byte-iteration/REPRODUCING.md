# Reproducing the Data.span byte-iteration experiment

The preserved experiment is `$HOME/Downloads/cidrmerge-span-byte-iteration-20261117T172402Z`. Use a new root and fresh output directories for every rerun. Preserve original sources, binaries, logs, failed controls and every observation. This experiment contains **eight file configurations and two text-stdin configurations**; it does not time startup, Searchbot or stripped executables, or compare shipping builds.

## Source, input and harness identity

B is main commit `b570de5ce1b0ba2dce5a5bba70c9dccd5f3dc3b9`. P is B plus the exact `control/P.patch`: replace the `Data.withUnsafeBytes` closure in `TextInputLoader.consumeChunk` with `let bytes = data.span` and indexed byte iteration. FileHandle reads, per-read Data creation, pending-line ownership, parsing, normalization statistics and error handling remain unchanged. Both `control/{B,P}-freeze.json` manifests contain 1,945 files; only `Sources/CIDRMergeCLI/TextInput.swift` differs. Both package manifests and all eight dependency revisions are identical. There is no FoundationEssentials, Swift System or POSIX reader change.

Prepare a fresh root by copying the two frozen source snapshots or extracting `control/B-source.tar` and `control/P-source-portable.tar`. The latter is the verified GNU-format archive with exactly 1,945 source members; `control/P-source-portable.json` records its SHA-256 (`512318be73b7e025a5dd3b1afdde6da2f2e1cc624f54ede41e7ad6fd690b6bb7`). Alternatively, construct P by applying `control/P.patch` to a clean copy of B; do not apply it again to the already-patched frozen P tree. Copy source manifests, dependency provenance, the files listed in `control/common-harness-freeze.json`, and the selected fixture/reference files listed in `control/fixture-reuse.json`. Verify source/copy hashes. Do not share mutable build or source directories with historical experiments.

The 22 selected fixture/reference files total 204,778,778 bytes. They reuse the historical inputs and independent references byte-for-byte, verified against recorded SHA-256 values. The four corpora are canonical IPv4, canonical IPv6, noncanonical mixed networks and mixed ranges; each file corpus runs with statistics off and on. The two stdin cases are canonical IPv4 without statistics and noncanonical mixed networks with statistics. Exact definitions are in `control/{cases,stdin-cases}.json`; timing policy is `control/measurement-protocol.json`. Never regenerate reference output from either candidate. `analysis/audit_report.py` is included in this experiment's common harness freeze.

## Build and qualification

Use **Swift 6.4.2** explicitly for both variants on macOS ARM64, native ARM64 Linux under OrbStack and x86-64 Linux on swift-dev. Record compiler, target, SDK/Xcode, OS, hardware allocation, disk and runtime identities. Match toolchain/runtime within each platform. Run candidate Debug and Release suites separately with **Swift 6.2.4 on ARM64 Linux** to check the existing compiler floor.

Set `ROOT` to a fresh experiment, `PLATFORM` to its platform directory and `SWIFT` to the exact compiler. The recorded Mac ordinary build command has this shape; use the recorded platform worker count:

```sh
"$SWIFT" --version
"$SWIFT" build --package-path "$ROOT/sources/B" \
  --scratch-path "$PLATFORM/build/B" --cache-path "$PLATFORM/cache" \
  --config-path "$PLATFORM/config" --security-path "$PLATFORM/security" \
  --disable-netrc --disable-sandbox --only-use-versions-from-resolved-file \
  --skip-update -c release -j 6 --product cidrmerge
# Repeat for P with the corresponding source and scratch directory.
```

Seed only the eight locked dependency revisions in isolated scratch; verify each checkout revision and cleanliness. Freeze each ordinary release executable as `PLATFORM/bin/B` or `PLATFORM/bin/P` **before** test builds, preserving hashes, sizes and linkage. Do not strip or rebuild those copies. Record Linux runtime hashes and actual resolved load paths under the measured `LD_LIBRARY_PATH`. If a runtime or fixture alias points at verified historical immutable bytes, record that fact and target identity; do not describe it as a new copied runtime. Verify identities again after qualification and measurement.

Run complete B/P Debug and Release tests with the same isolated flags, replacing `build ... --product cidrmerge` with `test` and the desired configuration. Require exit 0 and **7 Core + 78 CLI = 85 Swift Testing tests** per suite; separate bundle summaries and the zero-test XCTest shim are not failures. Use separate floor scratch/cache for candidate Swift 6.2.4 tests.

Run these fresh-output gates outside timing:

```sh
python3 "$ROOT/control/differential.py" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" \
  --output "$PLATFORM/behavior/differential"
python3 "$ROOT/control/io_differential_v2.py" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" \
  --output "$PLATFORM/behavior/io"
python3 "$ROOT/control/final_validation_v2.py" \
  --source "$ROOT/sources/P" --baseline-source "$ROOT/sources/B" \
  --seed "$PLATFORM/build/P" --binary "$PLATFORM/bin/P" \
  --swift "$SWIFT" --jobs 6 --output "$PLATFORM/final-validation"
python3 "$ROOT/control/negative_control_v2.py" \
  --runner run_matched.py --output "$PLATFORM/controls/negative-files"
python3 "$ROOT/control/negative_control_stdin.py" \
  --runner run_stdin.py --output "$PLATFORM/controls/negative-stdin"
```

The differential gates comprise 254 standard cases and 84 Mac / 86 Linux real-I/O cases. On Linux, pass `--runtime-library-path` to the standard gate and export the recorded `LD_LIBRARY_PATH` for the real-I/O gate. Final validation covers formatting, content/whitespace audit, Core symbol graphs and external consumer, and CLI smoke; full DocC conversion is a Mac check. The negative controls must reject both wrong output and wrong statistics. Mac native `/usr/bin/time -p -l` counters require a context that permits them; preserve any sandbox-denied attempts rather than substituting metrics.

The focused strict-memory-safety probe source and exact Mac compile/run command are preserved as `macos/control/span-probe.swift` and `span-probe.json`; preserve corresponding platform/floor receipts. The Mac command uses `-strict-memory-safety -warnings-as-errors -target arm64-apple-macosx15.0`. `LC_BUILD_VERSION` records deployment target 15.0; compilation/load-command inspection is not execution testing on macOS 15.

## Matched timing and independent auditing

Check disk space before preparation and measurement. Allow additional build/output space beyond the **3-GiB minimum**: the runner requires 3 GiB plus the next expected output size before each observation and 3 GiB afterward. Do not delete older experiments to make room. Preserve any task-owned build artifacts before disposing of new scratch.

Finish builds, tests, profiling, transfers and bulk hashing before the host timing window. Serialize macOS and native ARM64 OrbStack timing on their shared hardware. Freeze CPU/disk allocation and runtime state. The swift-dev host may run independently.

```sh
python3 "$ROOT/control/run_platform.py" \
  --root "$ROOT" --platform-root "$PLATFORM" --platform macos \
  --output-control "$PLATFORM/measurement-control"
```

Use `--platform linux --runtime-library-path PATH` on Linux. `--kind throughput` or `--kind stdin` can schedule groups separately with distinct control outputs. Actual result paths are fixed at `comparisons/ordinary/B-vs-P/{primary,followup}` and `stdin/ordinary/B-vs-P/{primary,followup}`: a different control-output directory alone does not permit overwriting a phase.

Each configuration has one excluded warmup per variant followed by six alternating B/P pairs, with rotating case order: **96 file observations + 24 stdin observations = 120 measured executions and 20 warmups per platform**. Stdin uses regular-file redirection opened before timing, without a timed feeder. Any individual primary paired elapsed-time or peak-RSS increase above 5% triggers one separate fixed six-pair follow-up with fresh warmups. Follow-up outliers do not trigger another phase. Retain all observations and complete output; never pool phases or discard outliers.

After all timing on that host finishes:

```sh
python3 "$ROOT/analysis/audit_report.py" \
  --root "$ROOT" --platform-root "$PLATFORM" --platform macos \
  --output-root "$PLATFORM/audits-01" --timing-finished
```

Use `--platform linux` and `--remote-root` where retrieved paths need translation. This invokes the frozen independent auditors and verifies complete stdout/stderr references, metric units, sample chronology, primary totals 120/20 and exact follow-up selection. Audit reads may change atime; dev/inode/size/mtime/ctime and SHA-256 remain checked. Preserve failed audits and use a fresh destination for any correction.

Report absolute elapsed/CPU/RSS medians and paired percentage medians with full observed minima/maxima. Ratios of absolute medians are not paired medians; spreads are not confidence intervals. Treat small/noisy differences as inconclusive and keep previous experiments separate. Linux wait4 lifetime peak RSS can include inherited parent memory; never subtract a guessed floor. Data.span provides a lifetime-bound byte view here, not zero allocation or bounded total application memory.

## Preserved setup failures

The original `control/P-source.tar`, produced by BSD tar, carried AppleDouble metadata entries. The x86 source-inventory gate detected these extra transport files before compiling. The original archive and diagnostics remain preserved; the new portable archive was checked for exactly 1,945 members and every expected source hash. Extra files in the new x86 task tree were quarantined and the corrected archive verified; candidate source bytes were never changed. Use the portable candidate archive for new reproductions. This was a source-transport setup failure, not a compiler, test or benchmark failure.

The first Mac process inventory was sandbox-denied, as recorded in `macos/control/process-preflight-sandbox-denial.json`. An authorized process preflight passed before timing. Preserve both records; this setup recovery did not alter or discard a product measurement.
