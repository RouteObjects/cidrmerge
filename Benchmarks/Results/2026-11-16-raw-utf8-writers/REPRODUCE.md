# Reproducing the direct raw UTF-8 writer experiment

Use a fresh directory under `$HOME/Downloads`; retain this experiment and all earlier results. The original is `cidrmerge-raw-utf8-20261116T145749Z`. Baseline production source is cidrmerge `8bba7629d7fc9c366ea47680ee6c38badd615092`. The canonical experiment branch later advanced over report-only commit `ba02b2179b938a816529bf0c04d1a31b7fc6478b`; production source did not change with that handoff.

Both snapshots retain all eight original `Package.resolved` revisions, including released swift-cidr 0.10.1. The separately accepted compact-coalescing implementation is not substituted into either variant. Apply `full.patch` only to C. The measured production change is confined to `Sources/CIDRMergeCLI/OutputRenderer.swift`; C also adds `RawUTF8OutputTests.swift`.

## Builds and correctness

The preserved `control/build_macos.py` invokes the recorded Xcode 27.2 / Apple Swift 6.4.2 toolchain, uses independent B/C scratch paths and locked dependency resolution, and freezes ordinary Release CLI binaries before any test builds. Reuse verified dependency cache bytes but create fresh build paths. Then run:

```sh
python3 control/build_macos.py B build release
python3 control/build_macos.py C build release
python3 control/build_macos.py B test debug
python3 control/build_macos.py B test release
python3 control/build_macos.py C test debug
python3 control/build_macos.py C test release
python3 control/differential.py --baseline macos/bin/B --candidate macos/bin/C --output macos/differential
```

Do not rerun these commands into existing log/output paths. Baseline suites contain 72 tests per configuration; candidate suites contain 78. Preserve the logs and verify all eight dependency checkout revisions and clean contents. The additional macOS AddressSanitizer run targets the six new formatting tests in a separate scratch directory. ARM64 also checks candidate Debug and Release with Swift 6.2.4. Linux launch commands, runtime-library environment, images and build constraints are recorded in their platform receipts; native Linux builds use the same frozen source and lockfile contents.

## Inputs and matched runs

`control/prepare_references.py` copies six preserved million-entry fixtures: IPv4 disjoint, IPv6 disjoint, mixed disjoint, mixed permuted, mixed overlap and range-derived mixed. Independent Python parsing, interval union and `ipaddress.summarize_address_range` produce complete canonical range and CIDR reference bytes. Coverage hashes, range/CIDR counts and covered-address counts must match the earlier preserved oracle. Freeze the generated `control/cases.json`, input bytes and both output references before timing.

Each of the 12 configurations receives one excluded warmup per variant and six measured B/C pairs. Variant order alternates each round; case order rotates. Primary totals are 144 measurements and 24 warmups per platform. Use ordinary frozen binaries, not test or sanitizer binaries.

```sh
python3 control/run_matched.py \
  --platform macos --fixtures-root . --cases control/cases.json \
  --baseline macos/bin/B --candidate macos/bin/C \
  --output macos/measurements
```

For native Linux, set `--platform linux`, use its preserved B/C paths, and supply `--runtime-library-path` when required by the recorded toolchain. `--fixtures-root` is the experiment root containing the `fixtures` directory. Linux uses exact-child `wait4` resources; macOS uses native `/usr/bin/time` CPU/RSS data and a monotonic elapsed timer. Cross-platform absolute times are not hardware-normalized.

The x86 run uses `--deduplicate` after timing and complete byte verification: identical stdout files share verified immutable content through hardlinks. All original stdout pathnames and bytes remain. This avoids duplicate-output storage exhausting the host; it does not redirect output to `/dev/null` or omit validation. Maintain at least 3 GiB free plus space for the next output. Preserve every sample, including failures and outliers.

If any individual paired elapsed-time or RSS change exceeds +5%, run exactly one separate six-pair follow-up for that configuration, using `--only` with the selected IDs and a new output directory. Keep primary and follow-up results separate. Do not recursively rerun until a desired result appears.

Do not overlap Mac and OrbStack timed runs or run task builds, tests, profiling, bulk transfers or heavy hashing on their shared host during timing. Freeze and verify source, binaries, toolchains/runtime identity, dependency pins, harnesses and inputs before and after measurement.

## Review and rollback

Compare exact bytes, not merely equivalent coverage. Range separators, compressed IPv6 spelling, family order and trailing newlines remain identical. JSON, statistics, checksum behavior and atomic output replacement stay on their existing paths.

The direct writers remove String construction from the raw formatting loops. Whole-output `Data` and complete network arrays remain. Static generated code does not establish dynamic allocation counts or zero allocation.

The prototype is left uncommitted. To return only the production renderer to its branch baseline after reviewing the diff:

```sh
git restore --source=HEAD -- Sources/CIDRMergeCLI/OutputRenderer.swift
```

Retain the focused tests, reports and Downloads evidence for review. No dependency update or upstream code change needs reverting.
