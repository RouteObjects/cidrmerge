# Reproducing the Foundation byte-iteration experiment

The preserved run is `$HOME/Downloads/cidrmerge-foundation-byte-iteration-20261117T154127Z`. Use a new root for every rerun. Do not overwrite frozen binaries, source snapshots, phase directories, audit receipts or failed attempts. This experiment compares ordinary release artifacts only; it does not build or benchmark the static shipping profile.

## Freeze identity and scope

B is main commit `9fe30dde3fd5ad50944064f912fad8c19cfcec62`. P is exactly B plus `control/P.patch`: iterate the existing Foundation Data chunk inside synchronous `withUnsafeBytes`, keeping the existing FileHandle read and pending-line loop. `control/{B,P}-freeze.json` records all 1,745 files per snapshot; only TextInput differs. Both manifests and all eight Package.resolved revisions are identical. Foundation and the Swift 6.2 compiler floor remain unchanged.

The exact candidate patch is also embedded in [candidate-patch.json](candidate-patch.json). Applying it to a clean copy of B is an alternative to copying the already-patched frozen `sources/P` tree; do not apply it to that frozen candidate again. For this alternative, choose a fresh `ROOT` and create its `control` directory as shown below, then prepare `ROOT/sources/P` as a clean copy of B before the two `git apply` commands. Run the snippet from the report directory:

```sh
ROOT="$HOME/Downloads/cidrmerge-foundation-byte-iteration-rerun-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$ROOT/control"

python3 - "$ROOT/control/P.patch" <<'PY_PATCH'
import hashlib, json, pathlib, sys
record = json.loads(pathlib.Path("candidate-patch.json").read_text())
patch = record["unified_diff"].encode("utf-8")
assert hashlib.sha256(patch).hexdigest() == record["sha256"]
with pathlib.Path(sys.argv[1]).open("xb") as output:
    output.write(patch)
PY_PATCH
git -C "$ROOT/sources/P" apply --check "$ROOT/control/P.patch"
git -C "$ROOT/sources/P" apply "$ROOT/control/P.patch"
```

The 57 fixture/reference files in `control/fixture-reuse.json` are copied from the previous preserved corpus, with both original and copied SHA-256 values verified. The 16 file configurations, two text-stdin configurations and four startup configurations are defined in `control/{cases,stdin-cases,startup-cases}.json`. The helper scripts and protocol are frozen in `control/common-harness-freeze.json`. Independent references are never regenerated from B or P.

To prepare a fresh root, copy the two frozen source trees; the exact control files listed in common-harness-freeze; B/P source manifests and P.patch; and the exact fixtures listed in fixture-reuse. Copy, do not hardlink mutable build/source trees back into the preserved experiment. Verify every copied file against the recorded hash before building or timing. The original `control/{B,P}-source.tar` artifacts provide another source-transfer route. Preserve source/base, patch, fixture and harness manifests in the fresh root. Also copy the separately preserved `analysis/audit_report.py` into the fresh root at that same relative path, verify its source/copy hashes, and record it in the rerun manifest; it is not part of the earlier common-harness freeze. The portable final-validation helper **does exist** at `control/final_validation_v2.py` and is already included in that freeze (SHA-256 `dddee01847d4e4cfc3e2b1bf5119079e45364f443edfb267fea2d8ae2df9d70a`); it is identical to the additional Mac copy at `macos/control/final_validation.py`. The command below intentionally uses the shared frozen control path.

## Platform and dependency preparation

Use **Swift 6.4.2** explicitly for every matched B/P build and test on macOS ARM64, native ARM64 Linux through OrbStack, and native x86-64 Linux on swift-dev. Record `swift --version`, target architecture, SDK/Xcode when applicable, OS/kernel, hardware allocation, free space and relevant runtime paths before work. Confirm the platform is native rather than emulated. Match toolchain and runtime within each platform; do not compare absolute timings across architectures as a hardware ranking.

The original Mac compiler was Xcode 27.2's `XcodeDefault.xctoolchain/usr/bin/swift`; its complete version string and build commands are preserved in `macos/control/{B,P}-build-release.json` and the test receipts. ARM compiler, image identity, dependency seed and commands are under `arm64/control/qualification-{B,P}/`. Use the final x86 index for its exact compiler and runtime provenance.

Seed fresh per-variant scratch directories from the preserved locked dependency repositories/checkouts, copying workspace-state and repairing Git alternates to point at the copied repositories. Verify checkout HEAD equals each of the eight resolved revisions and the checkout is clean. No local swift-cidr substitution or dependency update is part of this control. Source and manifests stay immutable. Do not reuse one candidate's compiled build directory for the other candidate.

Check disk capacity before copying/building. Reserve more than the 3-GiB measurement floor for builds, outputs, runtime copies and follow-ups. The measurement harness requires at least 3 GiB plus the next expected output size before each sample and at least 3 GiB afterward. Keep historical experiments intact. A new task-owned tmpfs may be used for Linux build scratch if memory is sufficient; retain binaries, logs, manifests and qualification evidence outside disposable scratch.

## Build, freeze, then test

Set `ROOT`, `PLATFORM` and `SWIFT` to the fresh experiment, its platform directory and the explicit Swift 6.4.2 executable. For ARM containers the preserved layout is `ROOT=/experiment`, `PLATFORM=/validation`; host-mounted paths correspond to the new experiment. The following uses the same ordinary build flags as the recorded Mac pipeline; choose the recorded platform worker count.

```sh
"$SWIFT" --version

"$SWIFT" build --package-path "$ROOT/sources/B" \
  --scratch-path "$PLATFORM/build/B" --cache-path "$PLATFORM/cache" \
  --config-path "$PLATFORM/config" --security-path "$PLATFORM/security" \
  --disable-netrc --disable-sandbox --only-use-versions-from-resolved-file \
  --skip-update -c release -j 6 --product cidrmerge

# Repeat with sources/P and build/P, using exactly the same flags/toolchain.
```

Before running tests, find the output with the same Swift build options plus `--show-bin-path`, copy each executable into the fresh `PLATFORM/bin/B` or `PLATFORM/bin/P`, and record its SHA-256, size and direct linkage. These ordinary binaries remain unchanged even if test builds reuse or modify their scratch tree. Freeze the Linux runtime closure, copy required libraries into `PLATFORM/runtime/lib`, and record actual loaded paths/hashes. Set the same `LD_LIBRARY_PATH` for B and P when used; system-library/interpreter paths that still resolve on the host must be recorded rather than described as frozen-directory loads.

Run complete Debug and Release suites for B and P with the same isolated path flags:

```sh
"$SWIFT" test --package-path "$ROOT/sources/B" \
  --scratch-path "$PLATFORM/build/B" --cache-path "$PLATFORM/cache" \
  --config-path "$PLATFORM/config" --security-path "$PLATFORM/security" \
  --disable-netrc --disable-sandbox --only-use-versions-from-resolved-file \
  --skip-update -c debug -j 6

# Also B release, P debug, P release with the corresponding source/scratch pair.
```

Require process exit 0 and **7 Core + 78 CLI = 85 Swift Testing tests** for each run. Do not require one final 85-test line: the bundles report separately. Keep the zero-test XCTest shim separate. On ARM64 Linux additionally run P Debug and Release with the explicit **Swift 6.2.4** floor toolchain and separate floor scratch/cache; do not substitute these for the matched 6.4.2 suites.

Final qualification uses the preserved `control/final_validation_v2.py` interface:

```sh
python3 "$ROOT/control/final_validation_v2.py" \
  --source "$ROOT/sources/P" --baseline-source "$ROOT/sources/B" \
  --seed "$PLATFORM/build/P" --binary "$PLATFORM/bin/P" \
  --swift "$SWIFT" --jobs 6 --output "$PLATFORM/final-validation"
```

This creates fresh validation scratch, runs content/format/whitespace checks, Core symbol-graph and consumer checks, and CLI smoke. macOS also runs DocC conversion; Linux does not claim full DocC conversion. Source and frozen ordinary binary hashes must remain unchanged afterward. No `--release-style-binary` is supplied for this experiment.

## Correctness and harness controls

All output directories below must be new:

```sh
python3 "$ROOT/control/differential.py" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" \
  --output "$PLATFORM/behavior/differential"

python3 "$ROOT/control/io_differential_v2.py" \
  --baseline "$PLATFORM/bin/B" --candidate "$PLATFORM/bin/P" \
  --output "$PLATFORM/behavior/io"

python3 "$ROOT/control/negative_control_v2.py" \
  --runner run_matched.py --output "$PLATFORM/controls/negative-files"
python3 "$ROOT/control/negative_control_v2.py" \
  --runner run_startup.py --output "$PLATFORM/controls/negative-startup"
python3 "$ROOT/control/negative_control_stdin.py" \
  --runner run_stdin.py --output "$PLATFORM/controls/negative-stdin"
```

The standard differential has 254 cases/508 processes; real-I/O has 84 Mac or 86 Linux cases. The negative controls run tiny fake children and must reject deliberately wrong output and statistics. They are not product performance samples. On Linux add `--runtime-library-path "$PLATFORM/runtime/lib"` to the standard differential and export that path for the real-I/O process. The latter inherits the environment.

## Startup copies and matched measurements

Create **separate stripped copies**, never strip the ordinary timing binaries in place. On macOS the recorded command is `strip -S -x`; use the recorded Linux strip flags for that platform. The measurement wrappers require the following exact layout:

```text
PLATFORM/bin/B              ordinary frozen B release executable
PLATFORM/bin/P              ordinary frozen P release executable
PLATFORM/bin/stripped/B     separately stripped ordinary B copy/verified alias
PLATFORM/bin/stripped/P     separately stripped ordinary P copy/verified alias
```

After stripping each Mac copy, run `codesign --verify --strict` on that copy. Only if verification fails because stripping invalidated its signature, ad-hoc sign the **stripped copy** with `codesign --force --sign -`, then verify it again and smoke-check `--version`. Complete this before recording final hashes and before timing; never alter the ordinary original. Both stripped copies in the preserved run verified successfully without that fallback.

If using another artifact directory, create byte/hash-verified aliases at these expected startup paths before timing. Preserve the original and stripped sizes, hashes and linkage. No shipping-profile artifacts are substituted here.

On macOS, the native `/usr/bin/time -p -l` resource counters and hardware queries need an execution context that permits them. Run from a normal Terminal or approved execution outside the restricted Codex sandbox, and pass the three negative harness controls before timing. The preserved sandbox-denied attempts are retained; missing resource metrics must fail rather than be replaced with guesses.

Wait until all builds, tests, profiles and source/corpus audit hashing finish. macOS and OrbStack measurements must run in separate windows on the shared Mac. Do not alter CPU/disk allocation, toolchains, fixtures, source or runtime during the experiment. Then run the common driver:

```sh
python3 "$ROOT/control/run_platform.py" \
  --root "$ROOT" --platform-root "$PLATFORM" --platform macos \
  --output-control "$PLATFORM/measurement-control"
```

Linux uses `--platform linux --runtime-library-path "$PLATFORM/runtime/lib"`. The driver accepts `--kind throughput`, `--kind stdin` or `--kind startup` if scheduling groups independently, each with a new output-control directory. The result phase paths are fixed under `comparisons/ordinary/B-vs-P`, `stdin/ordinary/B-vs-P` and `startup/ordinary/B-vs-P`; they must not already exist. A new output-control path alone does not make it safe to rerun an existing phase.

The primary matrix is 16 named-file configurations × six B/P pairs, two text-stdin configurations × six pairs, and four startup configurations × twenty pairs: **376 measured observations and 44 excluded warmups per platform**. Case order rotates and variant order alternates. Text stdin is regular-file redirection opened by the harness before timing, without a timed generator/feeder. Startup is a fresh process with warm caches, not cold-start qualification.

Any individual primary paired elapsed or RSS increase above 5% triggers one separate fixed follow-up for that configuration, with the same pair count and excluded warmups. Follow-up outliers do not trigger a third phase. Keep phases separate and retain every observation, including failures. The runner verifies complete stdout/stderr bytes against independent references and may hardlink verified identical stdout within a phase after timing. It performs no crossphase relinking.

## Independent auditing and reporting

After **all** timing on that host ends, run:

```sh
python3 "$ROOT/analysis/audit_report.py" \
  --root "$ROOT" --platform-root "$PLATFORM" --platform macos \
  --output-root "$PLATFORM/audits-01" --timing-finished
```

Use `--platform linux` for Linux; retrieved remote paths may additionally require `--remote-root`. The helper invokes the frozen file/startup and stdin auditors, checks exact output hashes/bytes, metric units, chronological pair order, complete inventories and fixed follow-up selection, then reconciles primary totals to 376/44. Keep failed audits in place and use fresh destinations for a corrected auditor. Atime is intentionally excluded from read-time identity checks; dev/inode/size/mtime/ctime and SHA-256 remain checked.

Report absolute elapsed/CPU/RSS medians alongside medians and extrema of paired percentage changes. The ratio of absolute medians can differ from the paired median. Extrema are not confidence intervals. Keep primary/follow-up and file/stdin/startup profiles distinct; never pool the old FoundationEssentials experiment with this one. Treat the unchanged Searchbot file path and tiny startup calls as controls and describe small/noisy differences as inconclusive. Linux child lifetime RSS may include inherited pre-exec parent memory; preserve any separately executed `/bin/true` control and never subtract or replace original RSS observations.
