# Reproducing the ASCII experiment

The full original bundle is `$HOME/Downloads/cidrmerge-ascii-20261115T170645Z`. Retain it. Every new measurement run needs a new timestamped directory, its own freeze, and the complete six-pair matrix. Do not change a fixture, binary, runtime or harness inside a frozen run. Do not rerun into an existing result directory.

## Sources, builds and tests

Baseline is commit `6703901011fd17da2b07c3edd6e0eea52d04ff46`. Candidate is that snapshot plus [production.patch](production.patch) and the new `Tests/CIDRMergeCLITests/TextInputASCIITests.swift`. Manifests and all eight dependency pins must be byte-identical between variants. Source inventories and original build/test commands are retained in the full bundle and portable validation receipts. Do not substitute a local swift-cidr checkout.

For each frozen source snapshot, use a new scratch directory. On macOS select `/Applications/Xcode-27.2.0.app/Contents/Developer` through `DEVELOPER_DIR`; on Linux select the explicit Swift 6.4.2 binary and its runtime library paths from `swift -print-target-info`.

```sh
# Set SOURCE to the frozen B or C package, SCRATCH to a new Downloads path,
# and FROZEN_BINARY to a new B or C file outside that scratch directory.
swift --version
swift build --package-path "$SOURCE" --scratch-path "$SCRATCH" \
  --skip-update --only-use-versions-from-resolved-file --disable-netrc \
  -c release --product cidrmerge -j 4
BIN_DIR=$(swift build --package-path "$SOURCE" --scratch-path "$SCRATCH" \
  --skip-update --only-use-versions-from-resolved-file -c release --show-bin-path)
mkdir -p "$(dirname "$FROZEN_BINARY")"
test ! -e "$FROZEN_BINARY" && cp "$BIN_DIR/cidrmerge" "$FROZEN_BINARY"
# Copy/hash the ordinary binary above before these test builds.
swift test --package-path "$SOURCE" --scratch-path "$SCRATCH" \
  --skip-update --only-use-versions-from-resolved-file --disable-netrc -c debug -j 4
swift test --package-path "$SOURCE" --scratch-path "$SCRATCH" \
  --skip-update --only-use-versions-from-resolved-file --disable-netrc -c release -j 4
```

Expect 57 tests for B and 69 for C in each configuration. Repeat C with Swift 6.2.4 on native ARM64 Linux for the compiler-floor check. The recorded OrbStack runs used existing cached native images with networking disabled; they did not use Docker Desktop or request registry credentials.

From the candidate Git checkout, the supplemental checks are below. The archived source snapshots have no `.git`; run the tracked-content audit and diff checks in the checkout, not in those archives:

```sh
swift format lint --configuration .swift-format.json --recursive --strict \
  Package.swift Sources Tests Benchmarks
./scripts/audit-release-content.sh tree
./scripts/smoke-test.sh
./scripts/check-documentation.sh
./scripts/check-core-consumer.sh
git diff --check
```

## Exact CLI parity

The portable differential helper accepts ordinary frozen binaries. Use a fresh output directory; it refuses an existing one.

```sh
EXPERIMENT="$HOME/Downloads/cidrmerge-ascii-20261115T170645Z"
PARITY="$HOME/Downloads/cidrmerge-ascii-parity-$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$EXPERIMENT/shared/differential.py" \
  --baseline "$EXPERIMENT/macos/bin/B" \
  --candidate "$EXPERIMENT/macos/bin/C" --output "$PARITY"
```

On Linux also supply `--toolchain-bin` and `--runtime-library-path` for the selected Swift installation. Expected result: 60 fixtures, 77 cases, 154 child invocations, all byte/status comparisons passed. File inputs, stdin, statistics, diagnostics, raw/JSON output and checksum files are included.

## Full Linux timing matrix

The shared harness is directly relocatable: its root is the parent of `control/`. On the native Linux host, prepare a new Downloads directory with the original `sources/{B,C}/cidrmerge`, all `fixtures`, and the shared helpers in `control/`. Copy `source-reference.json`, `reference.json` and `matched-protocol.json` unchanged. Create `control/config.json` with the absolute Swift 6.4.2 binary, a positive `jobs` count, a platform label, and `expected_tests: {"B":57,"C":69}`. The full bundle's `shared/README.md` and recorded configs show the exact layout. Dependency caches may be seeded for offline execution, but all eight checkout revisions and clean working trees must pass the pin gate.

```sh
python3 control/build_tests.py
python3 control/run_correctness.py
python3 control/prepare_benchmark.py
python3 control/run_matched.py --validate-only
# Run only after builds/tests/profiling/transfers have stopped on this host.
python3 control/run_matched.py > logs/phase-benchmark.log 2>&1
python3 control/audit_linux.py . --output control/evidence-audit.json --check-runtime-files
```

Expect 132 measured samples / 192 child processes plus 22 excluded warmups / 32 children. The harness enforces the 3-GiB free-space minimum and retains every output and resource record. Supply additional disk space for builds, fixtures and approximately 1.7 GiB of captured stdout per platform. Runtime environment selection belongs to the config/build receipts; merely putting a different compiler on PATH is insufficient.

## macOS timing and profiling

The original macOS harness is retained under `macos/control/{base_runner.py,run_matched.py}`. It uses the original verified fixture/reference directory recorded in `context.json`. The freeze includes that context, the source inventory, ordinary binary hashes, correctness gate, runtime UUIDs and protocol. For a fresh run, recreate those artifacts for the fresh root using the retained build commands; do not edit the old freeze or reuse old timing output. The same `run_matched.py --validate-only` and `run_matched.py` entry points apply. The Mac auditor is retained as `control/audit_mac_evidence.py` in the full bundle.

Keep Mac and OrbStack measurement windows separate. After timing, reproduce successful CPU sampling with `control/profile_ascii_attach_v2.py` adapted to a new profile output directory. It starts an owned CLI blocked on stdin, attaches Time Profiler, feeds the exact fixture after capture readiness, and validates the complete output. Four captures cover B/C and ordered IPv6/native mixed-disjoint. The original direct-launch and first readiness attempts remain preserved as failures; they are excluded from the comparison.

The repository exports are portable analysis evidence, not replacements for the raw bundle. `evidence/manifest.json` records original artifact hashes and transformation rules; per-platform `samples.json` retains all measured/warmup scalar observations, and `comparisons.json` retains every pair and its full spread. Recompute comparisons from those samples without removing outliers. An elapsed or peak-RSS increase greater than 5% in any pair triggers investigation and a separate six-pair follow-up directory for the affected case.
