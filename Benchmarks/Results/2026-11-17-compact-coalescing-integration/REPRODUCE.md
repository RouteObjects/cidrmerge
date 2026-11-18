# Reproduce the published-dependency comparison

Use a fresh directory under `$HOME/Downloads`; never reuse an existing result directory. The preserved experiment is `coalescing-release-integration-20261118T031137Z`. Original sources, raw outputs, fixtures, ordinary binaries, runtime files and all attempts remain there and on swift-dev. The public export is deliberately small text evidence with path substitutions; it is not a replacement for those binary/raw artifacts.

## Restore and verify the inputs

| Artifact | SHA-256 |
| --- | --- |
| `control/cidrmerge-baseline-portable.tar` | `17b550797da0292f42759b83929b9f6dda1489334ad5f9a9417e23a84efdcf80` |
| `control/cidrmerge-candidate-portable.tar` | `fd04ea7e2e978f06e7852a177897c5cdf1f85cc64cf1a98ec55af28284fa9b3e` |
| `control/downstream-shared-portable.tar.gz` | `e0db4d74b11a78734e6068a2b4de87ece44bf82e4ebbf7fb489cf2ea95fd8626` |
| Exact candidate dependency patch | `44e18183f22c04b29273e10b34964a590b3614eef421c0dab3ee4b9036d76c02` |

The two source archives contain exactly 2,152 regular files each. Verify every file against the corresponding `cidrmerge-*-freeze.json`, not only the outer archive checksum. Alternatively, export cidrmerge commit `5ab794a5a0578c03fd7b52f3b72889de201c09f8` and apply the preserved six-file dependency patch to a second copy. The patch is exported inside a JSON wrapper so its original UTF-8 bytes and hash remain exact without introducing patch-context whitespace into repository checks. Extract the exact patch from the public wrapper (`REPORT` names this report directory):

```sh
python3 - "$REPORT/evidence/original/analysis/public-support/cidrmerge-candidate-patch.json" "$EXPERIMENT/candidate.patch" <<'PYTHON'
import hashlib, json, pathlib, sys
record = json.loads(pathlib.Path(sys.argv[1]).read_text())
raw = record["patch"].encode("utf-8")
assert len(raw) == record["bytes"] == 4163
assert hashlib.sha256(raw).hexdigest() == record["sha256"] == "44e18183f22c04b29273e10b34964a590b3614eef421c0dab3ee4b9036d76c02"
with pathlib.Path(sys.argv[2]).open("xb") as output:
    output.write(raw)
PYTHON
```

The exported `evidence/original/analysis/public-support/reference-aliases.json` records byte-identical metadata aliases for provenance files originally stored under fixture directories.

Both timed copies keep CLI version 0.4.2. B resolves swift-cidr 0.10.1 at `5e4b3d2f881340a6ced05742429f1bd680dfd1e0`; C resolves published 0.11.0 at `ae956313ebbcb5a6f9d20b74626ce5b6e2e69839`. Verify the signed tag and published release receipt. Retain the seven other complete pins exactly; do not introduce a local package path or resolve fresh dependency versions.

Restore the shared bundle into a fresh `downstream/shared` directory and verify all 132 members using its manifest. It contains the exact fixtures/references, cases/protocol, measurement/audit tools and source provenance. Preserved independent generators/reference metadata are also included in the text export. If regenerating data, require every fixture and reference hash in `control/cases.json` to match before running measurements. Regenerated data with different hashes is a different experiment.

## Build and qualify

Use the recorded Swift 6.4.2 compiler/runtime and environment for each platform. macOS uses Xcode 27.2's Swift Build default; Linux uses explicit `--build-system native`. Keep B/C backend, flags, environment and job count matched within the platform. Use separate ordinary and test scratch directories, and copy the ordinary Release executable to `bin/B` or `bin/C` before any tests. Frozen metadata records complete actual commands, compiler hashes and linkage. Exact clean dependency checkouts may be seeded from caches. Ordinary product and test outputs use independent scratch trees; preserve the recorded compiler and module-cache settings.

Run the complete B/C Debug and Release suites (85 tests each), and C's Debug/Release suites with Swift 6.2.4 on ARM64 Linux. Run the copied differential and final-validation tools against the frozen ordinary executables:

```sh
python3 "$SHARED/control/differential.py" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/C" \
  --output "$PLATFORM/differential-new"
python3 "$SHARED/control/io_differential_v2.py" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/C" \
  --output "$PLATFORM/io-differential-new"
python3 "$SHARED/control/final_validation_v2.py" \
  --source "$C_SOURCE" --baseline-source "$B_SOURCE" \
  --seed "$C_ORDINARY_BUILD" --binary "$PLATFORM/bin/C" \
  --swift "$SWIFT" --output "$PLATFORM/final-validation-new"
```

`SHARED`, `PLATFORM`, source and scratch variables name the new experiment's directories. On Linux, export the frozen runtime directory as `LD_LIBRARY_PATH`; preserve the recorded executable/search-path handling and descriptor-permission setup. Run formatting, content audit, documentation/symbol graphs, Core-consumer and CLI smoke checks. Do not reinterpret count-valued I/O results as a boolean: the preserved qualification adapter checks all 84 macOS or 86 Linux cases and zero failures, then binds the original receipt hash.

Freeze bindings with the exact candidate publication identity and both ordinary workspaces:

```sh
python3 "$SHARED/control/freeze_bindings.py" \
  --shared "$SHARED" --baseline-source "$B_SOURCE" --candidate-source "$C_SOURCE" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/C" --swift "$SWIFT" \
  --candidate-version 0.11.0 \
  --candidate-revision ae956313ebbcb5a6f9d20b74626ce5b6e2e69839 \
  --publication-receipt "$EXPERIMENT/control/upstream-publication.json" \
  --baseline-workspace "$B_ORDINARY_BUILD/workspace-state.json" \
  --candidate-workspace "$C_ORDINARY_BUILD/workspace-state.json" \
  --evidence "$PLATFORM/control/qualification-gate.json" \
  --output "$PLATFORM/control/premeasurement-new.json"
```

Supply the actual platform gate paths and the recorded extra source/qualification/toolchain/runtime files/manifests. Linux additionally supplies `--runtime-library-path`. The successful binding receipts preserve the complete expanded invocations and exact files. macOS binds shared-cache/loaded-image UUID evidence rather than claiming to copy OS runtime libraries.

## Measure and audit

Keep at least 3 GiB free plus space for the next output. Wait for an idle task-owned build/test/profile/transfer environment. Serialize macOS and OrbStack measurements; swift-dev may run independently on its own host. Preserve every attempt in a fresh output directory.

```sh
python3 "$SHARED/control/run_platform.py" \
  --shared "$SHARED" --platform-root "$PLATFORM" --platform macos \
  --bindings "$PLATFORM/control/premeasurement-new.json" \
  --output "$PLATFORM/measurements-new"
```

Use `--platform linux --runtime-library-path "$PLATFORM/runtime/lib"` on Linux. The frozen driver runs original, scale and sparse groups sequentially: one excluded B/C warmup per configuration, six alternating pairs and rotating case order. Per platform, primary phases retain 300 observations/50 warmups, representing 360/60 child processes. Each group with a paired-median elapsed/RSS increase above 5% gets one fixed six-pair follow-up for the affected configurations. No recursive retries, outlier removal or pooling.

Every process output is compared in full against the preserved independent reference after timing. Deduplication happens only after successful comparison and uses a new platform-local hardlink store. Keep original raw resource files and all stdout/stderr paths.

After timing finishes, independently audit every phase:

```sh
python3 "$SHARED/control/audit_measurements.py" \
  --run "$PLATFORM/measurements-new/original/primary" \
  --output "$PLATFORM/audits-new/original-primary.json"
```

Repeat for scale/sparse primary and each actual follow-up. Retrieved remote evidence requires explicit `--map /original/prefix=/retrieved/prefix` mappings, including exact frozen source, compiler and runtime copies. The audit recomputes resources, ordering, pair summaries and full output bytes. Do not treat a successful remote audit as a substitute for byte-verifying retrieval and a mapped local audit.

The report table builder consumes only successful audit receipts. The observation-bundle helper retains every parsed process/sample record, original raw SHA and macOS native-time text; explicit prefix mapping affects only path comparisons, not record values. Public export performs literal path substitutions and verifies unchanged JSON numerical/boolean values, recording both original and export hashes. Failed setup/export attempts remain separate.

Small/noisy time changes are inconclusive. macOS CPU fields have 0.01-second resolution. Linux pre-exec parent high-water RSS may mask small application-only memory differences. Do not turn equal small-input RSS into an allocation claim. Reproduce the shipping 0.4.3 checks separately with the committed release source and `scripts/check-release.sh 0.4.3`; these ordinary Swift 6.4.2 binaries are not the remapped/stripped distribution archives.
