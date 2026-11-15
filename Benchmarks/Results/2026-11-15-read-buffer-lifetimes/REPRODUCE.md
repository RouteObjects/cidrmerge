# Reproducing the bounded read-buffer experiment

The retained bundle is `$HOME/Downloads/cidrmerge-read-buffer-20261115T182833Z`; swift-dev keeps its original evidence at the same Downloads-relative location. Do not run into an existing measurements or follow-up directory. Copy controls into a fresh experiment, choose fresh output paths, and regenerate all hash freezes after configuring those paths.

## Source and dependencies

B is main `675d534a29fd3c2231d58bb58bf395b6343e233b`. C is B plus `production.patch` and `ReadBufferLifetimeTests.swift` from this report. The complete B/C source inventory is in `evidence/source-freeze.json`; eight identical locked pins are in `evidence/dependencies.json`. Use canonical remote packages at those revisions, with no local swift-cidr override. Preserve ordinary `swift build -c release --product cidrmerge` binaries before `swift test` builds.

## Functional checks

Run both `swift test` and `swift test -c release` for each source snapshot on all three Swift 6.4.2 hosts. Expect 69 tests for B and 72 for C. Also run candidate Debug/Release with native ARM64 Swift 6.2.4. Use separate scratch and module-cache directories per toolchain.

```sh
swift format lint --configuration .swift-format.json --recursive --strict Package.swift Sources Tests Benchmarks
./scripts/audit-release-content.sh tree
./scripts/smoke-test.sh
./scripts/check-documentation.sh
./scripts/check-core-consumer.sh
git diff --check
python3 differential.py --baseline "$BASELINE_BINARY" --candidate "$CANDIDATE_BINARY" --output "$NEW_DIFFERENTIAL_DIRECTORY"
```

The differential helper and native platform build/measurement helpers are preserved under `evidence/harness/`. Their example JSON uses symbolic host-path placeholders; resolve those and make new freezes. Do not execute timing scripts directly from the report directory.

## Timing and output validation

Reuse the fixture byte hashes and independent output references listed in the retained controls and portable Linux reference manifest. The eight split-family cases and three native mixed cases are fixed by `matched-protocol.json`. Allow the complete output budget in addition to the 3-GiB free-space guard, and keep all outputs, failures and warmups.

On macOS, configure `control/context.json`, the selected Xcode developer directory, source/reference freezes, runtime UUIDs and a passed correctness gate. Then:

```sh
python3 control/run_matched.py --validate-only
python3 control/run_matched.py > control/benchmark.log 2>&1
```

On Linux, populate fresh `sources/`, `fixtures/`, `bin/` and `control/` directories. `prepare_benchmark.py` records the correctness/runtime gates and frozen inputs; `run_matched.py --validate-only` verifies them before `run_matched.py` records a new run. Use the recorded native Swift 6.4.2 toolchain. The ARM64 run uses an existing OrbStack image with `--pull=never`; no registry authentication is required. The Linux sequence is `build_tests.py`, `run_correctness.py`, `freeze_runtime_libraries.py`, `prepare_benchmark.py`, then `run_matched.py --validate-only` and `run_matched.py`; the first four take their configuration from `control/config.json`. Refer to the retained phase receipts for exact commands.

Run one excluded warmup followed by six measured pairs, alternating BC/CB and rotating case order. Keep macOS and OrbStack timings separate, and stop task-owned builds/tests/profiling before measurement. The macOS helper captures BSD time CPU/RSS; Linux captures exact-child `wait4` CPU/RSS. Output verification runs outside each child timer. Never pool follow-up results with the first run.

## Heap checkpoints

The retained `control/profile_heap.py` and `control/profile_heap_postrender.py` launch only owned children. They use separate profiling copies with a debugging entitlement, verify unchanged executable instruction sections, pause with SIGSTOP, collect `sample`, `heap --noContent --addresses=all` and `vmmap`, resume, and check complete output. Post-render captures wait for the first stdout byte before pausing a process whose remaining output is pipe-blocked. Parsing snapshots require stack verification; a fixed delay alone does not identify a phase.

These snapshots explain live input-storage behavior. They are separate from elapsed/RSS timing and do not measure allocation counts.
