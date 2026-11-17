# Data.span byte-iteration common harness

B/P use frozen ordinary release binaries at PLATFORM/bin/{B,P}, frozen before test builds. There are no startup or Searchbot timing groups and no stripped/static shipping profile. Four selected text corpora each run with statistics off/on; the two text-stdin cases use regular-file redirection. Primary totals per platform: 120 measured observations and 20 excluded warmups (8 file configurations × 6 pairs + 2 stdin configurations × 6 pairs).

ROOT is the new experiment root; PLATFORM is its macos/arm64 directory or the swift-dev platform root. All output destinations must be fresh. Linux uses the same frozen LD_LIBRARY_PATH for both variants; standard differential accepts --runtime-library-path, while the real-I/O gate inherits the environment.

Qualification outside timing:

```sh
python3 "$ROOT/control/differential.py" --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" --output "$PLATFORM/behavior/differential"
python3 "$ROOT/control/io_differential_v2.py" --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" --output "$PLATFORM/behavior/io"
python3 "$ROOT/control/negative_control_v2.py" --runner run_matched.py --output "$PLATFORM/controls/negative-files"
python3 "$ROOT/control/negative_control_stdin.py" --runner run_stdin.py --output "$PLATFORM/controls/negative-stdin"
```

The reused exact differential has 254 cases; the real-I/O gate has 84 Mac / 86 Linux cases. Full Swift Testing suites contain 7 Core + 78 CLI = 85 tests. On macOS native time counters require an authorized unsandboxed context; retain any failed controls and use a fresh destination for correction. Negative controls must reject wrong stdout and wrong statistics before product timing.

After host timing clearance:

```sh
python3 "$ROOT/control/run_platform.py" --root "$ROOT" --platform-root "$PLATFORM" --platform macos --output-control "$PLATFORM/measurement-control"
```

Use --platform linux --runtime-library-path PATH on Linux. Use --kind throughput or --kind stdin for separate scheduling, with distinct output-control directories. Result directories comparisons/ordinary/B-vs-P/{primary,followup} and stdin/ordinary/B-vs-P/{primary,followup} must be fresh. Changing output-control alone does not permit overwriting a phase.

A primary individual paired elapsed/RSS increase >5% triggers one separate fixed six-pair follow-up of that configuration. Keep all primary/follow-up observations and outliers; no recursive third phase, no pooling, and no optional crossphase hardlink rewriting.

After all timing on that host finishes:

```sh
python3 "$ROOT/analysis/audit_report.py" --root "$ROOT" --platform-root "$PLATFORM" --platform macos --output-root "$PLATFORM/audits-01" --timing-finished
```

Use --platform linux and --remote-root where retrieved remote paths require mapping. The independent helper audits every completed phase, exact output/metrics/order/follow-up selection and primary total 120/20. Atime is excluded from read-time identity checks; dev/inode/size/mtime/ctime and SHA-256 remain enforced. Previous experiments and observations are never modified or pooled. All control files, including the aggregate auditor, are frozen in common-harness-freeze.json; never modify a frozen runner after platform jobs start.
