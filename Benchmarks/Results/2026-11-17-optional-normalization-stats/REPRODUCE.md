# Reproduction

Use the preserved experiment bundle; never overwrite an existing measurement directory. Compiler and OS identities are captured in each platform's control receipts. All binaries are ordinary Release builds captured before test builds.

```sh
R="$HOME/Downloads/cidrmerge-normalization-c2-20261117T020633Z"
python3 "$R/control/differential.py" --baseline "$R/macos/bin/B" --candidate "$R/macos/bin/C" --output "$R/macos/differential-rerun-$(date -u +%Y%m%dT%H%M%SZ)"
python3 "$R/control/run_matched.py" --platform macos --fixtures-root "$R" --cases "$R/control/cases.json" --baseline "$R/macos/bin/B" --candidate "$R/macos/bin/C" --output "$R/macos/rerun-$(date -u +%Y%m%dT%H%M%SZ)" --deduplicate
```

For Linux, use `--platform linux` with that platform's preserved binaries and recorded runtime-library path. Use native ARM64 OrbStack or native x86-64 swift-dev, not emulation. The archived platform control drivers record their exact build/test/runtime setup. Keep Mac and OrbStack timing separate and finish builds/tests first. Six paired rounds and one excluded warmup per variant/configuration are encoded in the runner. Run any flagged cases with `--only` into a new follow-up directory; retain original observations.

Source snapshots are `sources/B` and `sources/C`; `control/source-freeze.json` binds every file. `control/full.patch` applies to the stated baseline; no dependency replacement is needed. `control/prepare_fixtures.py` can regenerate inputs in a new root, using `--prior` to point at the earlier preserved raw-writer fixtures. Fixture, harness, binary and runtime receipts bind the measured artifacts. `control/audit_results.py --help` documents the independent audit; `control/summarize_results.py` regenerates derived tables from completed raw JSON.

To compare with the baseline in an isolated checkout of the measured candidate, review and apply `full.patch` in reverse from that checkout's root. The patch covers only source and tests; it does not include historical or competitor reports. Preserve the original experiment bundle.
