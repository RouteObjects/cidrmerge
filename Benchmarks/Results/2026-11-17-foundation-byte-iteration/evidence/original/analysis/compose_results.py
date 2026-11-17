from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/report-narrative-01'
PLATFORMS = [('macos', 'macOS ARM64'), ('arm64', 'Linux ARM64'), ('x86_64', 'Linux x86-64')]
reviews = {key: json.loads((ROOT / f'analysis/{key}-measurement-review.json').read_text()) for key, _ in PLATFORMS}
artifacts = json.loads((ROOT / 'analysis/artifacts-summary.json').read_text())
assert all(review['passed'] for review in reviews.values())
OUT.mkdir(exist_ok=False)

def percent(value):
    return f'{value:+.2f}%'

def spread(values):
    return f'{percent(values[0])} to {percent(values[1])}'

target_rows = []
range_rows = []
count_rows = []
artifact_rows = []
environment_rows = []
repeat_regressions = []
total_measured = total_warmups = 0
for key, label in PLATFORMS:
    review = reviews[key]
    target = next(row for row in review['rows'] if row['kind'] == 'throughput' and row['phase'] == 'primary' and row['case'] == 'text-ipv4-canonical-no-stats')
    b = target['absolute_medians']['B']['elapsed_seconds'] * 1000
    p = target['absolute_medians']['P']['elapsed_seconds'] * 1000
    target_rows.append(f"| {label} | {b:.3f} ms | {p:.3f} ms | {percent(target['paired_change_medians']['elapsed'])} | {spread(target['paired_change_ranges']['elapsed'])} |")
    range_rows.append(f"| {label} | {spread(review['text_primary_elapsed_median_range_percent'])} | {spread(review['text_primary_rss_median_range_percent'])} |")
    totals = review['totals']
    assert totals['primary'] == {'measured_samples': 376, 'warmups': 44}
    count_rows.append(f"| {label} | 376 / 44 | {totals['followup']['measured_samples']} / {totals['followup']['warmups']} | {review['measured_samples']} / {review['warmups']} |")
    total_measured += review['measured_samples']
    total_warmups += review['warmups']
    artifact = artifacts[key]
    assert artifact['same_linkage']
    environment_rows.append(f"| {label} | {artifact['environment']['machine']} | {artifact['environment']['toolchain']} |")
    artifact_rows.append(f"| {label} | {artifact['B']['ordinary_bytes']:,} / {artifact['P']['ordinary_bytes']:,} | {artifact['B']['stripped_bytes']:,} / {artifact['P']['stripped_bytes']:,} | Unchanged |")
    repeat_regressions.extend((label, item) for item in review['repeated_primary_followup_median_regressions_over5_percent'])

regression_statement = (
    'No configuration shows an elapsed-time or peak-RSS median regression above 5% in both its primary and prescribed follow-up phase. Individual regressions and wide spreads remain visible in the detailed tables and pair records.'
    if not repeat_regressions else
    'Repeated median regressions above 5% remain and must be considered before adoption: ' + json.dumps(repeat_regressions) + '.'
)

body = '''# Foundation-only byte-iteration experiment

Baseline: `9fe30dde3fd5ad50944064f912fad8c19cfcec62`. Prototype branch: `perf/foundation-byte-iteration`.
Experiment: `cidrmerge-foundation-byte-iteration-20261117T154127Z`, preserved under `~/Downloads` on the Mac and swift-dev.

This completed, uncommitted prototype changes one loop in `TextInputLoader.consumeChunk`. It retains Foundation's reads and error handling. The eight locked dependency revisions, Swift 6.2 compiler floor, public interfaces, parser, normalization statistics, pending-line storage, Searchbot path, and output contracts are unchanged.

## What this isolates

After the existing `FileHandle.read(upToCount:)` returns a nonempty `Data`, P borrows its bytes with `try data.withUnsafeBytes { (bytes: UnsafeRawBufferPointer) in ... }` and executes the original byte-processing loop. The pointer never escapes the synchronous closure. FileHandle ownership, EOF behavior, read errors, and the enclosing autorelease boundary are unchanged.

Foundation still creates a `Data` for each read. This is a byte-iteration control, not reusable read storage or a FoundationEssentials migration. It adds no POSIX reads, SystemPackage imports, or error adapters. The existing in-memory Data loader remains unchanged.

## The quoted million-entry workload

This case contains one million ordered disjoint IPv4 /32 networks, raw CIDR output, and statistics disabled. Values below are from fresh matched B/P runs with Swift 6.4.2. Lower is better; percentages are medians of paired percentage changes, not percentages calculated from the two absolute medians.

| Platform | Baseline elapsed median | Candidate elapsed median | Paired median change | Six-pair observed spread |
|---|---:|---:|---:|---:|
''' + '\n'.join(target_rows) + '''

The earlier [archived R3 experiment](https://github.com/RouteObjects/cidrmerge/blob/eeca600fa34c5c88e281d19a92d694c3142cbdb7/Benchmarks/Results/2026-11-17-essentials-system/RESULTS.md) reported 199.269 to 149.297 ms on the Mac, with a paired median change of -24.594%. That is historical context, not a matched P-versus-R3 comparison. The current experiment demonstrates a substantial iteration-path gain while retaining per-read Data creation. It does not measure allocation counts or isolate the residual contribution of reusable storage.

## Broader results

These ranges span the paired medians of the twelve text-file configurations; they are not individual-sample ranges.

| Platform | Text elapsed median changes | Text peak-RSS median changes |
|---|---:|---:|
''' + '\n'.join(range_rows) + '''

![Primary text elapsed changes](text-elapsed.png)

![Primary text peak-RSS changes](text-rss.png)

Ordered address/prefix workloads provide the clearest throughput evidence. Small or noisy changes, including some range-derived workloads, remain inconclusive. The four Searchbot file configurations are controls: they bypass the changed reader, and small observed changes do not establish a JSON speedup. Startup observations use warm caches, have wide spreads, and do not establish a general launch-speed improvement.

''' + regression_statement + '''

See [MEASUREMENTS.md](MEASUREMENTS.md) for every configuration and phase's elapsed, CPU, and peak-RSS medians and spreads; [REGRESSIONS.md](REGRESSIONS.md) for triggered follow-ups; and [summaries.csv](summaries.csv) / [pairs.csv](pairs.csv) for machine-readable records. Primary and follow-up phases are never pooled, and no outliers are discarded.

## Correctness and qualification

| Platform / compiler | Baseline Debug / Release | Candidate Debug / Release | CLI differential | Expanded I/O |
|---|---:|---:|---:|---:|
| macOS ARM64 / Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 84 |
| Linux ARM64 / Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 86 |
| Linux x86-64 / Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 86 |
| Linux ARM64 / Swift 6.2.4 floor | Not repeated | 85 / 85 | Not repeated | Not repeated |

Every listed suite and differential case passed. Each full suite comprises 7 Core and 78 CLI tests. No implementation-mirroring tests were added. The existing tests and external differential harness cover raw/JSON output, exact diagnostics and exit status, statistics, checksums, fail-atomic output, empty/repeated sources, BOM/CRLF, split Unicode and malformed UTF-8, long lines, chunk boundaries, EOF, fragmented input, and real read failures.

Candidate formatting, content audit, documentation, external Core consumer, and CLI smoke checks passed on all three platforms. Core symbol graphs were validated on Linux, and the DocC archive was also built on macOS. Ordinary Release executables were frozen before test builds. Source and binary identities were independently rechecked after qualification and timing.

## Binary and runtime scope

| Platform | Ordinary bytes, B / P | Stripped ordinary bytes, B / P | Direct dependencies |
|---|---:|---:|---|
''' + '\n'.join(artifact_rows) + '''

These are ordinary Release artifacts and separately stripped copies, not a static Linux shipping-build comparison. Full Foundation remains in the CLI runtime closure. The earlier FoundationEssentials prototype's Linux binary-size and runtime-library reductions do not apply here. Library-file sizes are not resident-memory measurements.

## Measurement protocol

| Platform | Machine and OS | Toolchain |
|---|---|---|
''' + '\n'.join(environment_rows) + '''

| Group per platform | Configurations | Pairs each | Measured executions | Excluded warmups |
|---|---:|---:|---:|---:|
| Six text and two Searchbot file corpora, statistics off/on | 16 | 6 | 192 | 32 |
| Text stdin: canonical IPv4/no statistics; noncanonical mixed/with statistics | 2 | 6 | 24 | 4 |
| Version, empty stdin, 100 mixed entries, 10,000 mixed entries | 4 | 20 | 160 | 8 |
| Primary total | 22 | — | 376 | 44 |

| Platform | Primary measured / warmups | Follow-up measured / warmups | Total measured / warmups |
|---|---:|---:|---:|
''' + '\n'.join(count_rows) + f'''

Overall: **{total_measured:,} measured executions and {total_warmups:,} excluded warmups**. Each primary configuration has one excluded warmup per variant, alternating baseline/candidate pairs, and rotating case order. An individual primary paired elapsed-time or RSS increase above 5% triggers one separate fixed-size follow-up of that configuration. Follow-ups retain the same pair count and receive their own warmups. A new outlier in a follow-up remains reported without recursively scheduling further phases.

Every timed observation verifies complete stdout and stderr against hash-verified independent coverage/statistics references. macOS uses native `/usr/bin/time -p -l` CPU/RSS accounting and wall-clock elapsed time. Linux uses wall-clock elapsed time and wait4 resource accounting. Throughput and stdin use frozen ordinary binaries; startup uses their separately stripped copies.

macOS and native ARM64 OrbStack timing ran separately, with builds, tests, profiling, bulk transfers, and independent audits outside their timing windows. swift-dev ran independently on its existing guest allocation. Disk remained above the 3-GiB measurement minimum. Historical experiments were not deleted; only the new swift-dev memory-backed build scratch was removed after its required artifacts were preserved and hash-verified.

## Limits and preserved failures

These are warm-cache, within-platform comparisons on the recorded machines, not cross-hardware rankings or cold-launch deployment measurements. macOS CPU accounting has 0.01-second resolution, so tiny-call CPU percentages are not interpreted. Linux fork/exec resource accounting can inherit a parent-process peak-RSS floor for small commands; startup RSS therefore does not isolate application-only memory. The million-entry cases' reported peaks exceed the tiny-command controls, but this does not isolate application-only RSS. No floor is subtracted from the observations.

The Mac build driver initially expected one 85-test summary instead of the separate 7-test and 78-test summaries. Its failure is retained; the successful baseline Debug process was independently verified, and only the remaining suites ran afterward. Initial Mac environment/harness controls lacked sandbox access to native counters; those failures remain preserved, with fresh successful attempts before timing. A metadata aggregation assertion was corrected before its authoritative receipt was written. ARM preserved an unsupported process-inventory column probe and its successful replacement. swift-dev preserved a dependency-seed setup failure, then relocated only copied Git alternate-object metadata and reverified all eight clean pinned checkouts before building. Post-timing transfer setup failures were also preserved and corrected before final receipt verification. None of these setup, qualification, or transfer recoveries changes a product timing observation or the candidate source.

The pointer's lifetime is bounded by the closure. The pending line, parsed ranges, Searchbot document, summarized networks, and whole-output Data may still grow with input/output size. This experiment does not claim zero allocation, bounded total memory, or a general Unicode/JSON speedup.

## Reproduction and preservation

See [REPRODUCING.md](REPRODUCING.md) and [evidence-export.json](evidence-export.json). The frozen patch is `control/P.patch` under the experiment root. Original sources, binary/runtime snapshots, fixtures, harnesses, logs, raw output, and every failed control remain under the new Downloads experiment. Public evidence copies redact local paths without altering measurement values; the export manifest records both original and exported hashes.

The archived `perf/essentials-system-io` branch and unrelated working files remain preserved. This prototype is left uncommitted for review; no push, PR, merge, tag, or release is included.
'''
(OUT / 'RESULTS.md').write_text(body)
print(OUT / 'RESULTS.md')
