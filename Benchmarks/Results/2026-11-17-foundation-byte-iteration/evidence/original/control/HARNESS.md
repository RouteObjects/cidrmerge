# Foundation byte-iteration common harness

Frozen inputs and independent references are reused byte-for-byte from the prior experiment. Source variants are B/P; internal generic runner roles B/C map to B/P only. Original ordinary release binaries remain separate from test builds. Startup uses separately stripped ordinary copies at `PLATFORM/bin/stripped/{B,P}`. There is no shipping-profile matrix.

Set `ROOT` to this experiment root and `PLATFORM` to `ROOT/macos`, `ROOT/arm64`, or the swift-dev platform root. Linux measurement commands add `--runtime-library-path` pointing to frozen runtime libraries. All output directories must be fresh. Every primary/follow-up observation is preserved; never rerun into an existing output directory.

Qualification (outside timing):

```sh
python3 "$ROOT/control/differential.py" --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" --output "$PLATFORM/behavior/differential"
python3 "$ROOT/control/io_differential_v2.py" --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" --output "$PLATFORM/behavior/io"
python3 "$ROOT/control/negative_control_v2.py" --runner run_matched.py --output "$PLATFORM/controls/negative-files"
python3 "$ROOT/control/negative_control_v2.py" --runner run_startup.py --output "$PLATFORM/controls/negative-startup"
python3 "$ROOT/control/negative_control_stdin.py" --runner run_stdin.py --output "$PLATFORM/controls/negative-stdin"
```

The standard differential accepts `--runtime-library-path`; the real-I/O differential inherits `LD_LIBRARY_PATH`. Export the frozen library path in the Linux qualification environment. These gates are 254 standard cases and 84 Mac/86 Linux real-I/O cases. Full test counts are **7 Core + 78 CLI = 85**; do not inspect only the final suite's 78-test summary or the zero-test XCTest shim.

Run the whole approved matrix only after host timing clearance (substitute `linux` for `macos` as needed):

```sh
python3 "$ROOT/control/run_platform.py" --root "$ROOT" --platform-root "$PLATFORM" --platform macos --output-control "$PLATFORM/measurement-control"
```

The driver runs file, text-stdin and warm-cache startup primary groups and their fixed triggered follow-ups. Primary totals are 376 measured samples and 44 excluded warmups. To schedule groups independently, use `--kind throughput`, `--kind stdin`, or `--kind startup` with a unique output-control directory. The driver never recursively follows up a follow-up. A stopped phase requires investigation and a fresh phase/output directory, retaining the failure.

Independent audits after all timing on that host finishes:

```sh
python3 "$ROOT/control/audit_comparison.py" --root "$ROOT" --platform-root "$PLATFORM" --directory "$PLATFORM/comparisons/ordinary/B-vs-P/primary" --platform macos --output "$PLATFORM/audits/files-primary" --timing-finished
python3 "$ROOT/control/audit_comparison.py" --root "$ROOT" --platform-root "$PLATFORM" --directory "$PLATFORM/startup/ordinary/B-vs-P/primary" --platform macos --output "$PLATFORM/audits/startup-primary" --timing-finished
python3 "$ROOT/control/audit_stdin_comparison.py" --root "$ROOT" --platform-root "$PLATFORM" --directory "$PLATFORM/stdin/ordinary/B-vs-P/primary" --platform macos --output "$PLATFORM/audits/stdin-primary" --timing-finished
```

Audit every executed follow-up similarly into a new audit directory. For retrieved remote paths use the auditor's `--remote-root`. Atime is excluded from hash-time identity checks because the audit read can update it; dev/inode/size/mtime/ctime and complete SHA256 remain enforced. No optional crossphase hardlink pass exists. The runner also avoids same-inode rename, so it does not leave redundant `stdout.link` aliases.

The fixtures freeze and adaptation provenance are `control/fixture-reuse.json` and `control/harness-adaptation.json`. Exact runnable files are frozen in `control/common-harness-freeze.json`. Do not edit a frozen runner after platform jobs start; create and separately qualify a new version if required.
