# Reproducibility and provenance

This comparison uses native ARM64 executables on an Apple M1 Max (10 logical CPUs, 64 GiB RAM), macOS 27.2.1, on AC power. `BENCHMARK_ROOT` denotes the retained experiment directory under `~/Downloads`. The tested executables are frozen in `bin/`; fixture and harness hashes are in `control/freeze.json`. No system toolchain or package installation was required for this comparison.

## Executables and builds

| Tool | Source pin | Tested build |
| --- | --- | --- |
| [cidrmerge 0.4.0](https://github.com/RouteObjects/cidrmerge/releases/tag/0.4.0) | `e4f1aed90c013cc5b0d75bb0d29d80f0259e19b0` | Published macOS ARM64 release archive, installed through Homebrew and copied into the experiment. The release workflow selects Xcode 26.3 and its Swift 6.2 compatibility toolchain, builds with `swift build -c release --product cidrmerge` plus source-path remapping, and strips debug/local symbols. This is the shipped executable, not a local Swift 6.4.2 rebuild. |
| [rs-aggregate 0.3.2](https://github.com/ktims/rs-aggregate/releases/tag/v0.3.2) | `48ecb8e7931455c28d47ef64a769d985e2350cd3` | Unmodified source built with rustc/cargo 1.100.0 for `aarch64-apple-darwin`: `cargo build --release --locked --bin rs-aggregate --target aarch64-apple-darwin`. Default release profile and default `rayon` feature; no `RUSTFLAGS`. The release's Mac asset is Intel-only, so the benchmark uses a native source build. |
| [iprange 2.1.1](https://github.com/firehol/iprange/releases/tag/v2.1.1) | `8c6183cdffa2b65504a91e7c2f9d11f88f6995e9` | Official source archive, Apple clang 21.0.0 (`clang-2100.4.1.1`), native ARM64. `CC=/usr/bin/clang ./configure --disable-man --prefix="$BENCHMARK_ROOT/iprange/install"`, then `/usr/bin/make -j4`; no install step. Upstream configure selects `-g -O3 -D_THREAD_SAFE -pthread -flto`, with `LDFLAGS=-flto`; native UInt128 is enabled. |
| [mapCIDR 1.1.97](https://github.com/projectdiscovery/mapcidr/releases/tag/v1.1.97) | `3119d589a4868a79308604d3e42d05c47c9fd77b` | Official `mapcidr_1.1.97_macOS_arm64.zip`, checked against the release checksums. Embedded build information: Go 1.24.0, `GOOS=darwin`, `GOARCH=arm64`, `GOARM64=v8.0`, `CGO_ENABLED=0`, stripped with `-s -w`. No local Go rebuild. |

Binary SHA-256 values:

```text
fbeb31fba24a9742115ec080fe82934b8888a64e1722c15aa1ea15e05a55a6c3  bin/cidrmerge
a4b5250d3703b9e15477d995fee23b811f125cc8116760f3fe88857441253992  bin/rs-aggregate
2baa86bbc136db92c2ac15dfff9a4442c68210e68dccb76d2c39257c11f5d023  bin/iprange
de41d3180f37028f34257c8f150ba56a4fc7a432f53710324dc2e40b638eee90  bin/mapcidr
```

Each tool's `metadata.json` retains archive hashes, exact build details, version evidence, and source provenance. This is a comparison of these CLI distributions/builds, not a compiler-controlled language comparison.

## Exact aggregation commands

The frozen runner passes a file argument and closes stdin. These commands show its argument lists; output is redirected to a per-sample file:

```sh
"$BENCHMARK_ROOT/bin/cidrmerge" --raw --representation cidr "$INPUT"
"$BENCHMARK_ROOT/bin/rs-aggregate" "$INPUT"
"$BENCHMARK_ROOT/bin/iprange" -4 "$INPUT_V4"
"$BENCHMARK_ROOT/bin/iprange" -6 "$INPUT_V6"
"$BENCHMARK_ROOT/bin/mapcidr" -aggregate -silent -disable-update-check -auth=false -cidr "$INPUT"
```

All child processes receive a fresh environment containing only `PATH=/usr/bin:/bin`, `LANG=C`, `LC_ALL=C`, and a unique per-process `TMPDIR` under the experiment. mapCIDR additionally receives the non-secret dummy `PDCP_API_KEY=benchmark-no-credentials`. `HOME`, inherited credentials, `RAYON_NUM_THREADS`, `RAYON_RS_NUM_CPUS`, and `GOMAXPROCS` are absent.

The working directory is `BENCHMARK_ROOT`, except for mapCIDR, which runs in `BENCHMARK_ROOT/mapcidr/run`. Its precreated `mapcidr/config.yaml` contains `{}`. Without `HOME`, Go's macOS config-directory lookup falls back to this local config path. The dummy API-key value prevents ambient credential-file reads; `-auth=false` and `-disable-update-check` disable authentication and update checks. No user configuration is changed. Exact `-aggregate` is used; approximate aggregation is disabled. mapCIDR still creates its normal ipranger/LevelDB temporary storage under each process's `TMPDIR`; that work remains inside the measurement.

Default tool threading is retained. rs-aggregate uses its default Rayon pool and a `rayon::join` to aggregate IPv4 and IPv6; input parsing and output are outside that join. mapCIDR uses Go's default runtime settings. cidrmerge uses its normal synchronous CLI path. iprange's DNS-worker support is irrelevant to these numeric CIDR inputs. No single-worker override, CPU affinity, or frequency lock is applied.

## Matched inputs and coverage

The primary suite runs all four tools on identical prepartitioned IPv4 and IPv6 files, sequentially, skipping an empty family file. This accommodates iprange: its default IPv4 mode drops ordinary IPv6, while `-6` converts IPv4 to mapped IPv6. Neither mode alone preserves native mixed-family semantics. The reported primary elapsed time sums the family processes; reported peak RSS is the larger individual process peak, not their sum. Input partitioning occurs before timing.

The separate native suite gives cidrmerge, rs-aggregate, and mapCIDR the same unsplit `mixed-disjoint`, `mixed-permuted`, and `mixed-overlap` files. It measures one process per sample and preserves these tools' native mixed-family behavior. Do not combine native-suite and split-suite results as though their process counts were equal.

`range-derived-mixed` starts from 500,000 six-address intervals, expanded to 1,000,000 CIDRs before timing for every tool. It is not a native inclusive-range parsing benchmark. All benchmark inputs are valid canonical numeric IP/CIDR records; rs-aggregate's default maximum prefix lengths remain 32 and 128.

The independent verifier parses actual fixture bytes with Python's standard library, compares numeric interval unions, and checks the minimum CIDR count. All 41 tool/case/suite coverage preflights passed. iprange writes singleton addresses without `/32` or `/128`; the other tested commands retain those suffixes. Equivalent coverage therefore does not imply identical cross-tool output bytes or write volume. Default formatting is measured without rewriting a tool's output. Each measured output is hashed outside the timed interval against that same tool's independently verified warmup output.

## Timing protocol

One fresh-process warmup per tool/case/suite is verified and excluded. The primary suite has eight measured rounds; the native suite has nine. Tool positions are balanced using rotating forward/reversed orders, and case order rotates. Each invocation is wrapped by `/usr/bin/time -p -l`; Python `perf_counter_ns` measures blocking launch/wait elapsed time, including the timing launcher. Raw BSD `real`, `user`, `sys`, and maximum resident set size are retained; macOS RSS is recorded in bytes. Output writes are included, without an `fsync` durability claim. Hashing and coverage verification are outside timing.

The frozen runner imposes a 180-second limit per process and stops measurements on an unexpected exit, stderr, or output change. It preserves failure evidence and does not replace failed samples automatically. Identical duplicate timed output files are removed after hash verification; warmup outputs, hashes, timing records, stderr, and temporary storage are retained. Task builds and fixture generation stop before measurement. This is a warm-cache comparison on an ordinary active Mac, not an isolated-machine or cold-cache result.

The runnable protocol is `control/run_comparison.py` (`verify`, then `measure`), supported by `control/generate_fixtures.py` and `control/verify_coverage.py`. Use a fresh experiment directory for a rerun: the runner intentionally refuses to overwrite sample directories. Read `control/protocol.json`, `control/freeze.json`, fixture manifests, and per-sample JSON alongside the aggregate report.

## Rerunning in a new directory

The repository contains the measured scripts and compact results. Large fixtures,
verified outputs, binaries, build caches, and original process receipts remain in
the dated run directory under Downloads. Do not rerun measurements in that
directory: the scripts deliberately refuse to overwrite its evidence.

For a fresh run on macOS, create a new `BENCHMARK_ROOT` under `~/Downloads`. Copy
`generate_fixtures.py`, `verify_coverage.py`, `run_comparison.py`, `analyze.py`,
`render_tables.py`, and `protocol.json` into its `control/` directory. Update the
protocol's host/date metadata to describe the new run before freezing it, and
prepare the four native executables described above in its `bin/` directory.
Record the actual compiler versions and binary hashes if rebuilding. Rebuilding
with different toolchains produces a new comparison, not the original binaries.
Python 3.11 or later is required; this run used CPython 3.12.6.

Prepare `mapcidr/run/mapcidr/config.yaml` containing `{}`. Then generate the
fixtures using `python3 "$BENCHMARK_ROOT/control/generate_fixtures.py"`. Freeze
the new inputs before verification; this example runs from the new experiment
root and intentionally creates a new manifest rather than modifying the original:

```sh
cd "$BENCHMARK_ROOT"
python3 - <<'PY'
from pathlib import Path
import hashlib
import json

root = Path.cwd()
paths = list((root / "bin").glob("*"))
paths += list((root / "control").glob("*.py"))
paths += [root / "control/protocol.json",
          root / "mapcidr/run/mapcidr/config.yaml"]
paths += list((root / "fixtures").glob("*/*.txt"))
paths += list((root / "fixtures").glob("*/expected.json"))
paths += list((root / "fixtures").glob("*/manifest.json"))
files = {}
for path in sorted(paths):
    with path.open("rb") as source:
        files[str(path.relative_to(root))] = hashlib.file_digest(source, "sha256").hexdigest()
with (root / "control/freeze.json").open("x") as output:
    json.dump({"files": files}, output, indent=2)
    output.write("\n")
PY
python3 control/run_comparison.py verify
python3 control/run_comparison.py measure
python3 control/analyze.py
python3 control/render_tables.py
```

Keep the host conditions and native timing permissions in the run record. Stop
other preparation work before measurement. Retain failed attempts separately;
do not pool a changed binary, fixture, protocol, or toolchain into this run.
