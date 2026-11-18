# Published compact-coalescing integration

This is a fresh reuse of the accepted compact-coalescing experiment's fixtures, independent coverage references and six-pair design. It compares the same current cidrmerge source with published swift-cidr 0.10.1 (B) versus the new published upstream release (C). Both ordinary release binaries retain CLI version 0.4.2 until the later release-version change. No local dependency override is permitted. The other seven locked dependencies must remain identical. The candidate must exactly match the published 0.11.0 version and revision in a passed publication receipt.

## Matrix and units

| Group | Configurations | Measured observations | Excluded warmups | Measured CLI processes | Warmup CLI processes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original: eight split-family million-entry corpora and three native mixed cases | 11 | 132 | 22 | 192 | 32 |
| Native scale: disjoint/permuted/overlap/adjacent at 1,000, 10,000 and 100,000 entries | 12 | 144 | 24 | 144 | 24 |
| Native sparse merge: 10,000/1,000,000 base entries plus one duplicate per family | 2 | 24 | 4 | 24 | 4 |
| Total per platform | 25 | 300 | 50 | 360 | 60 |

The two sparse inputs contain **10,002 and 1,000,002 entries**. The historical separate typed IPv6 retention probe used 1,000,001 entries; it is not this mixed CLI fixture.

Each group has one excluded B/C warmup per configuration followed by six B/C, C/B alternating pairs with rotating case order. Split observations sum constituent-process elapsed and CPU time and use the maximum constituent peak RSS. Native configurations have one process per observation. A primary paired-median elapsed or RSS increase above 5% requests one separate fixed six-pair follow-up for that configuration; no recursive reruns, outlier removal or primary/follow-up pooling. Retain all individual outliers and CPU changes even below the trigger threshold, particularly for sparse merges.

The recorded elapsed interval uses `perf_counter_ns` around process launch and completion. macOS obtains child CPU/RSS from `/usr/bin/time -p -l`; native Linux uses `wait4` for the exact child, multiplying RSS KiB by 1,024. Every process has an owned process-group timeout of 180 seconds. A 3-GiB minimum plus the next output's byte size is required before each process. All stdout/stderr and raw resources remain preserved. Complete stdout bytes, byte count and SHA-256 must match a preserved independent reference; stderr must be empty. Hashing, full-byte comparison and content deduplication happen after the timer ends. Identical outputs are hardlinked only within the new platform-local content store; historical files are never hardlinked or modified.

## Pre-measurement qualification

Freeze ordinary release binaries before test builds. Run full B/C Debug and Release suites on each Swift 6.4.2 platform, plus the agreed Swift 6.2.4 floor qualification in its separate scratch tree. Preserve complete logs and exact summed test counts. Verify all eight dependency revisions and the absence of local replacements.

The copied modern `control/differential.py` exercises 254 text/Searchbot raw/JSON/statistics/checksum/diagnostic cases. `control/io_differential_v2.py` exercises 84 macOS or 86 Linux descriptor/path/fragmentation cases. `final_validation_v2.py` retains formatting, content audit, baseline-aware whitespace, documentation/symbol-graph, isolated Core-consumer and CLI smoke gates. For Linux I/O differential execution, export the captured runtime directory as `LD_LIBRARY_PATH`. Linux permission children may drop privileges, so the experiment source/binary/runtime parent directories must be traversable without exposing private unrelated paths.

```sh
python3 "$SHARED/control/differential.py" --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/C" --output "$PLATFORM/differential-01"
python3 "$SHARED/control/io_differential_v2.py" --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/C" --output "$PLATFORM/io-differential-01"
python3 "$SHARED/control/harness_controls.py" --shared "$SHARED" --output "$PLATFORM/harness-controls-01"
```

`freeze_bindings.py` records all files under the two immutable source snapshots, excludes `.git`, enforces the published dependency baseline and identical seven other pins, checks both binary versions, binds the exact Swift 6.4.2 compiler, and requires explicitly passed qualification evidence receipts. On Linux it also binds every resolved `ldd` runtime file. Use repeated `--extra-file` or `--extra-manifest` arguments for additional toolchain/runtime/code-generation receipts. Extra manifests have `files: {absolute_path: sha256}`. The publication receipt must contain `passed:true`, `published:true`, `version:"0.11.0"`, the exact 40-character `revision`, and `release_url:"https://github.com/RouteObjects/swift-cidr/releases/tag/0.11.0"`. Pass both workspace-state files when available; each dependency is then required to be a remote source-control checkout at its locked revision, with a clean checkout. The resulting binding receipt is immutable and portable only after regenerating it for the destination's actual paths and binaries.

```sh
python3 "$SHARED/control/freeze_bindings.py" \
  --shared "$SHARED" --baseline-source "$BASELINE_SOURCE" --candidate-source "$CANDIDATE_SOURCE" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/C" --swift "$SWIFT" \
  --candidate-version 0.11.0 --candidate-revision "$PUBLISHED_UPSTREAM_REVISION" \
  --publication-receipt "$PUBLICATION_RECEIPT" \
  --baseline-workspace "$BASELINE_SCRATCH/workspace-state.json" \
  --candidate-workspace "$CANDIDATE_SCRATCH/workspace-state.json" \
  --evidence "$PLATFORM/qualification-summary.json" \
  --evidence "$PLATFORM/differential-01/summary.json" \
  --evidence "$PLATFORM/io-differential-01/summary.json" \
  --output "$PLATFORM/control/premeasurement.json"
```

## Measurement and audit

Wait for an explicitly clear measurement window. macOS and OrbStack timing must be serialized, with no local build/test/profile/large hash/transfer work during either window. Native swift-dev can run independently. Run each group only once, with any required follow-up in a distinct directory. The driver creates its output directory exclusively, preserves a failed attempt, and never resumes by overwriting measurements.

```sh
python3 "$SHARED/control/run_platform.py" \
  --shared "$SHARED" --platform-root "$PLATFORM" --platform macos \
  --bindings "$PLATFORM/control/premeasurement.json" \
  --output "$PLATFORM/measurements-01"
```

For Linux use `--platform linux --runtime-library-path "$PLATFORM/runtime/lib"` (or the actual frozen toolchain runtime path). The binaries must be `$PLATFORM/bin/B` and `$PLATFORM/bin/C`. Each group writes `primary`, and affected groups also write `followup`; these retain distinct summaries and samples. No audit runs inside the driver's measurement matrix.

After all timing is finished, independently audit each created phase:

```sh
python3 "$SHARED/control/audit_measurements.py" \
  --run "$PLATFORM/measurements-01/original/primary" \
  --output "$PLATFORM/audits-01/original-primary.json"
```

Repeat for scale/sparse primary and each actual follow-up. A retrieved remote result can be verified with repeated `--map /original/prefix=/retrieved/prefix` arguments. The auditor imports no runner, executes no product, verifies all frozen hashes and complete output bytes, checks schedule and process counts, reconstructs raw CPU/RSS and split aggregates, and recalculates every paired delta, median/range and required follow-up. File-stability checks exclude access time, which reading may legitimately update, while retaining device/inode/size/modification/change-time checks.

Every failed attempt and every observation stays separate. A follow-up does not replace a primary regression. Small/noisy changes are inconclusive. The historical accepted sparse CPU tradeoff remains context, not a replacement for the new measured result; no threshold heuristics are introduced by this integration.
