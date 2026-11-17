# Reproducing the retained R3 prototype

This appendix documents the preserved experiment, not a release. Paths below are relative to the experiment root unless shown as shell variables or container mount points. No measurements were run while writing this appendix.

```sh
EXPERIMENT="$HOME/Downloads/cidrmerge-essentials-system-20261117T053919Z"
cd "$EXPERIMENT"
```

The source baseline is `9fe30dde3fd5ad50944064f912fad8c19cfcec62`. `B` is that source snapshot; `E4` adds FoundationEssentials/Swift System compatibility; `R3` additionally reuses the read scratch buffer; `S2` additionally borrows complete line slices. R3 is retained. S2 and all earlier attempts remain preserved. `control/retained-candidate.json` records the selection; no performance result is summarized here.

## Source, dependency and harness identity

| Evidence | Path |
| --- | --- |
| Baseline source inventory and archive identity | `control/baseline-freeze.json` |
| Retained candidate source inventory and patch identity | `control/R3-freeze.json` |
| Frozen source trees | `sources/B`, `sources/R3` |
| All eight locked dependency revisions | `control/dependency-freeze.json`; each source tree's `Package.resolved` |
| Changes isolated between E4, R3 and S2 | `control/final-variant-isolation.json` |
| Original final protocol | `control/comparison-protocol-final.json` |
| Direct retained-R3 comparisons | `control/retained-R3-protocol-addendum.json` |
| Shipping artifact protocol | `control/release-style-protocol-addendum.json` |
| Redirected-stdin protocol | `control/stdin-protocol-addendum.json` |
| Frozen runners and fixtures | `control/harness-final-freeze.json`, `control/retained-stdin-harness-freeze.json` |
| Mac wrapper/runner identity | `control/macos-measurement-harness-freeze.json` |
| ARM postprocessing wrapper changes | `control/arm-postprocessing-harness-freeze.json` |
| Case definitions and independent output/statistics references | `control/cases.json`, `control/startup-cases.json`, `control/stdin-cases.json` |
| Fixture preparation and reuse provenance | `control/prepare_fixtures.py`, `control/harness-fixture-reuse.json` |

The locked versions are swift-argument-parser 1.8.2, swift-asn1 1.7.1, swift-atomics 1.3.1, swift-cidr 0.10.1, swift-collections 1.6.0, swift-crypto 5.1.1, swift-nio 2.101.2 and swift-system 1.7.4. Swift System becomes a direct CLI dependency without changing its locked revision. No local upstream source substitution is used. Core continues to depend only on CIDR.

Read the source and dependency freezes before rebuilding. Use the locked revisions, matching toolchain and recorded runtime. Compiler version alone is insufficient: architecture, OS, release flags, runtime libraries and artifact profile also matter.

## Rebuild and qualify in a fresh experiment

The preserved build and qualification scripts use exclusive receipt/output creation. Do not rerun them over the original experiment, remove an old phase, or reuse a test-built binary for timing. A fresh reproduction must retain the same source/fixture layout, seed only verified locked dependency checkouts/repositories/workspace metadata, and use new scratch and output paths. Host-specific compiler paths and container mounts are recorded in the scripts and receipts; preserve any relocation as a new harness revision.

The actual Mac build/test entry point accepts variant, action and configuration:

```sh
python3 control/build_macos_final.py B build release
python3 control/build_macos_final.py B test debug
python3 control/build_macos_final.py B test release
python3 control/build_macos_final.py R3 build release
python3 control/build_macos_final.py R3 test debug
python3 control/build_macos_final.py R3 test release
```

These are fresh-root commands, not commands to run against the preserved receipts. The build step copies the ordinary release executable into `macos/bin/<variant>` before tests. Exact invocations, test counts and logs are recorded in `macos/control/{B,R3}-{build|test}-{debug|release}.json` and `macos/logs/`. The selected Xcode/Swift and hardware are recorded in `macos/control/environment.json` and `macos/control/hardware-verified.json`.

On ARM64 Linux the frozen `arm64/control/build_variant_v3.py` is staged as `/validation/control/build_variant_v3.py`, with sources mounted at `/experiment`. Its retained-candidate command, executed in the Swift 6.4.2 container, is:

```sh
python3 /validation/control/build_variant_v3.py --variant R3 --expected-tests 95
```

The same script accepts `--floor` for the separately configured Swift 6.2.4 environment and `--release-style-only` for the shipping-style build. Use the actual container and mounts from `arm64/control/final-642-plan.json`, `arm64/control/R3-floor-plan.json` and `arm64/control/R3-final-build-plan.json`; `--floor` does not install or switch the compiler. The baseline's successful build is under `arm64/control/qualification-B-attempt03/`; R3 qualification is under `arm64/control/qualification-R3/`. Retain the preceding attempts.

On swift-dev, the staged root is also under `$HOME/Downloads`, but the Mac archive's `x86_64/control` directory is staged as that remote root's `control`. The ordinary retained build/test entry point is:

```sh
python3 control/build_variant_v3.py --variant R3 --expected-tests 95
```

It uses the recorded swiftly 6.4.2 compiler and separate scratch, preserves the ordinary release executable before Debug/Release tests, checks actual checkout revisions against the lockfile, and captures runtime libraries. The orchestration scripts are host-specific; `x86_64/control/retained_r3_v2.py` records the exact final qualification and shipping sequence. Do not invoke a driver merely to reproduce one measurement: it can build or clean its explicitly designated scratch.

For exact B/R3 process behavior, the existing differential scripts accept new output directories:

```sh
python3 control/differential.py \
  --baseline "$EXPERIMENT/macos/bin/B" \
  --candidate "$EXPERIMENT/macos/bin/R3" \
  --output "$EXPERIMENT/macos/differential-R3-reproduce-01"

python3 control/io_differential_v2.py \
  --baseline "$EXPERIMENT/macos/bin/B" \
  --candidate "$EXPERIMENT/macos/bin/R3" \
  --output "$EXPERIMENT/macos/io-v2-R3-reproduce-01" --timeout 30
```

On Linux select its preserved binaries and use the frozen runtime. `differential.py` accepts `--runtime-library-path`; the I/O gate inherits `LD_LIBRARY_PATH`. Run qualification outside measurement windows. The common final-validation script is `control/final_validation_v2.py`; its required arguments are `--source`, `--seed`, `--output` and `--binary`, with `--baseline-source`, `--release-style-binary`, `--swift` and `--jobs` supported. Complete actual arguments and individual checks are retained in each platform's final-validation receipts. The Mac retained receipt is `macos/final-validation-R3/summary.json`, including formatting, delta whitespace, content audit, documentation, Core-only consumer and CLI smoke.

## Artifact profiles

Ordinary throughput uses the preserved, unstripped release executables. Ordinary startup uses separately stripped copies. Shipping startup uses independently built workflow-style artifacts; do not substitute an ordinary stripped binary for a shipping build.

- Mac ordinary/stripped identities: `macos/ordinary-artifacts/receipts.json`; startup aliases: `macos/control/ordinary-stripped-hardlinks.json`.
- Mac shipping B/R3 metadata: `macos/release-style/control/artifacts.json` and `artifacts-R3.json`. Build scripts are `control/build_macos_release_style.py` and `control/build_macos_release_style_R3.py`; the first preserves B/S2, the second adds R3. They use source/scratch prefix remapping, `strip -S -x`, and signature, version, loader and content checks. The original ordinary binaries remain unchanged.
- ARM shipping uses `build_variant_v3.py --release-style-only` in its prepared environment; swift-dev uses staged `control/build_release_style_v3.py --variant R3`. Linux shipping builds use `--static-swift-stdlib` and `strip --strip-unneeded`; dynamic ordinary binaries and their runtime libraries remain separately preserved.
- macOS directly loads system Foundation even in the candidate. Consult loader receipts when interpreting size/startup. Do not infer a dependency was removed merely from a changed import.

## Rerun matched measurements using frozen binaries

Check available disk first. The runners require a 3-GiB free-space floor plus room for the next captured output; builds and preservation need additional space. Finish builds, qualification and profiling before timing. macOS and OrbStack share the host and must run in separate windows. Avoid corpus hashing or independent audit work while any same-host measurement runs.

These Mac commands use a new phase name and preserve every original phase:

```sh
python3 control/run_comparison.py \
  --root "$EXPERIMENT" --platform-root "$EXPERIMENT/macos" \
  --platform macos --comparison B-vs-R3 --phase reproduce-01

python3 control/run_comparison.py \
  --root "$EXPERIMENT" --platform-root "$EXPERIMENT/macos" \
  --platform macos --comparison B-vs-R3 --phase reproduce-01 --startup

python3 control/run_comparison.py \
  --root "$EXPERIMENT" --platform-root "$EXPERIMENT/macos" \
  --platform macos --comparison B-vs-R3 --phase reproduce-01 \
  --startup --artifact-profile release-style

python3 control/run_stdin_comparison.py \
  --root "$EXPERIMENT" --platform-root "$EXPERIMENT/macos" \
  --platform macos --comparison B-vs-R3 --phase reproduce-01
```

The ARM wrapper intentionally omits optional cross-comparison relinking on OrbStack; the timed runner is unchanged. Run inside the already-qualified container with its recorded mounts:

```sh
python3 /experiment/control/run_comparison_arm_v2.py \
  --root /experiment --platform-root /validation \
  --platform linux --comparison B-vs-R3 --phase reproduce-01 \
  --runtime-library-path /validation/runtime/lib
```

For startup add `--startup`; for shipping startup also add `--artifact-profile release-style`. For redirected stdin use `/experiment/control/run_stdin_comparison_arm_v2.py` with the same root/runtime arguments, without startup flags. The platform driver and continuation are preserved in `arm64/control/measure_retained_r3.py` and `measure_retained_r3_continuation01.py`; these are records of the executed phase sequence, not instructions to overwrite completed phases.

On swift-dev, run the standard wrapper in its staged experiment root:

```sh
EXPERIMENT="$HOME/Downloads/cidrmerge-essentials-system-20261117T053919Z"
python3 "$EXPERIMENT/control/run_comparison.py" \
  --root "$EXPERIMENT" --platform-root "$EXPERIMENT" \
  --platform linux --comparison B-vs-R3 --phase reproduce-01 \
  --runtime-library-path "$EXPERIMENT/runtime/lib"
```

Use the same startup/profile options or `run_stdin_comparison.py` for the other modes. Remote result paths are translated to preserved experiment-relative paths by the final report index after retrieval.

Each file-throughput phase contains 16 configurations, six alternating pairs, and one excluded warmup per role/configuration: 192 measured processes and 32 warmups. Startup has four configurations and 20 pairs: 160 measured processes and eight warmups. Redirected stdin has two Searchbot configurations and six pairs: 24 measured processes and four warmups. Cases rotate each round. Redirected stdin is a regular file opened before timing; it is separate from the fragmented/slow pipe correctness controls.

Each wrapper writes invocation, completion and driver-log receipts. Each result directory retains the source/harness/fixture/runtime freeze, per-process stdout/stderr and measurements, and a summary. `B`/`C` in the runner mean the left/right named variant for that comparison, not necessarily the experiment's baseline variant. Keep E4-to-R3, R3-to-S2 and direct B-to-R3 evidence separate.

If `summary.json` lists `followup_required`, run a new phase with `--only` followed by exactly those case IDs. File/stdin follow-ups use another six pairs; startup follow-ups use another 20. The trigger is any measured pair above 5% elapsed or RSS, not only a median regression. Retain the original and follow-up observations separately. Never remove an outlier or pool phases to improve a result.

## Audit and aggregate after timing

The ordinary Mac file comparison can be independently audited after all same-host timing has ended:

```sh
python3 control/audit_comparison.py \
  --root "$EXPERIMENT" --platform-root "$EXPERIMENT/macos" \
  --directory "$EXPERIMENT/macos/comparisons/ordinary/B-vs-R3/reproduce-01" \
  --platform macos --output "$EXPERIMENT/macos/audits/B-vs-R3/reproduce-01" \
  --timing-finished
```

Use the startup result directory with the same auditor; use `audit_stdin_comparison.py` for stdin. ARM's final host audits use the preserved `audit_comparison_arm_v3.py` / `audit_stdin_comparison_arm_v3.py` to validate its wrapper/postprocessing records. Do not run hash audits during timing. Each audit must write to a new directory and retain failures.

The final platform indices are `analysis/{macos,arm64,x86_64}-report-index.json`. They identify the precise accepted audit receipts, qualification, environment, artifacts and limitations. Then aggregate only their small metadata:

```sh
python3 control/aggregate_report.py \
  --root "$EXPERIMENT" --output analysis/report-data-final-01
```

The aggregator requires all three indices and passed audits, reconciles phase/sample/warmup counts, and recomputes paired medians and ranges. It emits `dataset.json`, `summaries.csv`, `pairs.csv` and `aggregation.json`. `--allow-partial` is available only for an explicitly interim dataset in a different new directory. Absolute-role medians and paired percentage medians are distinct. A zero baseline CPU sample retains its absolute value but has a null percentage delta. No phase, platform, profile or candidate is pooled.

The Mac startup preflight failure is preserved separately: `macos/measurement-control/startup-preflight-failure.json`. Missing stripped aliases stopped the wrapper before any timed process. Its replacement phase is `startup/ordinary/B-vs-E4/primary-02`; it is not a discarded performance sample. Other failed or superseded attempts are indexed in the compatibility appendix and platform ledgers.
