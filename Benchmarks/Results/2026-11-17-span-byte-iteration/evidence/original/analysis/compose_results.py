from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = [('macos', 'macOS ARM64'), ('arm64', 'Linux ARM64'), ('x86_64', 'Linux x86-64 / swift-dev')]
reviews = {key: json.loads((ROOT / f'analysis/{key}-measurement-review.json').read_text()) for key, _ in PLATFORMS}
artifacts = json.loads((ROOT / 'analysis/artifacts-summary.json').read_text())
assert all(value['passed'] for value in reviews.values())
assert all(not value['repeated_primary_followup_median_regressions_over5_percent'] for value in reviews.values()), 'Report acceptance must be revised if a repeatable regression is found'
measured = sum(value['measured_samples'] for value in reviews.values())
warmups = sum(value['warmups'] for value in reviews.values())

million_rows = []
range_rows = []
count_rows = []
artifact_rows = []
for key, label in PLATFORMS:
    review = reviews[key]
    row = next(row for row in review['rows'] if row['kind'] == 'throughput' and row['phase'] == 'primary' and row['case'] == 'text-ipv4-canonical-no-stats')
    absolute = row['absolute_medians']; spread = row['paired_change_ranges']['elapsed']
    million_rows.append(f"| {label} | {absolute['B']['elapsed_seconds']*1000:.3f} ms | {absolute['P']['elapsed_seconds']*1000:.3f} ms | {row['paired_change_medians']['elapsed']:+.3f}% | {spread[0]:+.3f}% to {spread[1]:+.3f}% |")
    elapsed = review['text_primary_elapsed_median_range_percent']; rss = review['text_primary_rss_median_range_percent']
    range_rows.append(f'| {label} | {elapsed[0]:+.3f}% to {elapsed[1]:+.3f}% | {rss[0]:+.3f}% to {rss[1]:+.3f}% |')
    followup = review['totals']['followup']
    count_rows.append(f"| {label} | 120 / 20 | {followup['measured_samples']} / {followup['warmups']} | {review['measured_samples']} / {review['warmups']} |")
    info = artifacts[key]
    assert info['same_direct_linkage']
    artifact_rows.append(f"| {label} | {info['B']['bytes']:,} | {info['P']['bytes']:,} | Unchanged |")

report = f'''# Data.span byte-iteration maintenance experiment

Baseline: `b570de5ce1b0ba2dce5a5bba70c9dccd5f3dc3b9`. Prototype branch: `refactor/span-byte-iteration`.
Preserved experiment: `cidrmerge-span-byte-iteration-20261117T172402Z` under `~/Downloads`, with corresponding evidence on swift-dev.

## Change and acceptance

This completed, uncommitted prototype replaces the `withUnsafeBytes` loop in `TextInputLoader.consumeChunk` with Foundation's public typed byte view:

```swift
let bytes = data.span
for index in bytes.indices {{
    let byte = bytes[index]
    // Existing byte-processing body.
}}
```

The `Span<UInt8>` borrow is tied to the lifetime of its owning Data. The implementation uses no underscored conversion initializer and introduces no pointer escape or new public API. Foundation reads, read errors, the 64-KiB chunk size, autorelease boundaries, pending bytes, parsing, statistics, the separate Data loader, Searchbot and output paths are unchanged. Both variants retain identical manifests, all eight locked dependency revisions, the Swift 6.2 compiler floor and the macOS 15 deployment target.

All required correctness and compatibility checks passed. No configuration has an elapsed-time or peak-RSS paired-median increase above 5% in both its primary and prescribed follow-up phase. The candidate therefore meets the selected performance-parity criterion on these workloads. Small or noisy differences remain inconclusive; the reason to adopt this change is the supported borrowing API and maintainability, not a promised speedup.

Foundation still creates a Data for each read. This experiment does not measure allocation counts, remove read allocations, bound total application memory, or establish identical generated assembly.

## Measurements

The million-entry ordered IPv4 /32 file with raw CIDR output and statistics disabled gives:

| Platform | Baseline elapsed median | Candidate elapsed median | Paired median change | Six-pair observed spread |
|---|---:|---:|---:|---:|
{chr(10).join(million_rows)}

Percentages are medians of paired percentage changes. They are not percentages computed from the two absolute medians; the signs may differ for small, noisy changes.

The following ranges span the paired medians of the eight primary text-file configurations, not all individual observations:

| Platform | Elapsed median changes | Peak-RSS median changes |
|---|---:|---:|
{chr(10).join(range_rows)}

![Primary text elapsed changes](text-elapsed.png)

![Primary text peak-RSS changes](text-rss.png)

[MEASUREMENTS.md](MEASUREMENTS.md) contains all file/stdin and primary/follow-up elapsed, CPU and peak-RSS statistics. [REGRESSIONS.md](REGRESSIONS.md) retains the triggers and follow-up investigations; [summaries.csv](summaries.csv) and [pairs.csv](pairs.csv) contain every reported summary and measured pair. Whiskers and table ranges are observed minima/maxima, not confidence intervals. No outliers are discarded and phases are never pooled.

## Correctness and compatibility

| Platform / compiler | Baseline Debug / Release | Candidate Debug / Release | CLI differential cases | Expanded I/O cases |
|---|---:|---:|---:|---:|
| macOS ARM64 / Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 84 |
| Linux ARM64 / Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 86 |
| Linux x86-64 / Swift 6.4.2 | 85 / 85 | 85 / 85 | 254 | 86 |
| Linux ARM64 / Swift 6.2.4 floor | Not repeated | 85 / 85 | Not repeated | Not repeated |

Every listed suite passed. The existing tests and external gates cover exact raw/JSON bytes, exit status, diagnostics, normalization statistics, checksums, output-file behavior, chunk boundaries, fragmented input, Unicode/BOM/CRLF, malformed UTF-8, long lines, EOF and actual I/O failures. No tests were added merely to mirror the loop implementation.

Formatting, content audit, documentation, external Core consumer and CLI smoke checks passed on all three platforms. Linux documentation qualification validates the public Core symbol graph; macOS additionally builds the DocC archive. The external consumer checks retain the dependency lock and verify that the Core consumer does not compile Crypto or SystemPackage.

Standalone Data.span probes compile and run with `-strict-memory-safety -warnings-as-errors` on Swift 6.4.2 on all three platforms and Swift 6.2.4 on ARM64 Linux. These are isolated probes, not a claim that the entire package has strict-memory-safety coverage. No package-wide flags changed. The Mac probe targets macOS 15, and both ordinary Release binaries record minimum macOS 15.0 in their load commands. Execution was on macOS 27.2.1; an actual macOS 15 host was not tested.

## Protocol and artifacts

All matched measurements use Swift 6.4.2: Xcode 27.2 on the M1 Max Mac, native ARM64 Linux through OrbStack, and native x86-64 Linux on swift-dev. The compiler-floor suites are correctness checks only. Exact machine, compiler, OS, runtime and binary identities are retained in the evidence.

| Platform | Recorded machine / visible resources | OS |
|---|---|---|
| macOS ARM64 | Apple M1 Max; 10 cores; 64 GiB RAM | macOS 27.2.1 (26B131) |
| Linux ARM64 | Native aarch64 on the same Mac through OrbStack; 10 visible CPUs; 15.66 GiB reported MemTotal | Ubuntu 24.04.5 LTS; kernel 7.2.12-orbstack |
| Linux x86-64 | swift-dev, Xeon E5520; 4 visible logical CPUs; 8 GiB reported MemTotal | Ubuntu 24.04.5 LTS; kernel 6.14.8-2-pve |

Linux MemTotal is the reported system view, not an inference about a cgroup memory limit.

Per platform: four preserved text corpora (canonical IPv4, canonical IPv6, noncanonical mixed input and mixed ranges), each with statistics off/on, plus two stdin configurations (canonical IPv4/no statistics and noncanonical mixed/with statistics). Ten configurations each receive one excluded warmup per variant and six alternating B/P pairs with rotating case order: **120 measured executions and 20 excluded warmups** before follow-ups.

| Platform | Primary measured / warmups | Follow-up measured / warmups | Total measured / warmups |
|---|---:|---:|---:|
{chr(10).join(count_rows)}

Overall: **{measured:,} measured executions and {warmups:,} excluded warmups**. Any individual primary paired elapsed/RSS increase above 5% triggers one separate six-pair follow-up for that configuration, with its own excluded warmups. Follow-up outliers remain reported without recursively creating a third phase. Searchbot and startup timing are outside this focused experiment.

Every timed observation verifies full stdout/stderr against the preserved independent references. stdin uses an already-open regular file, without a timed generator. macOS uses wall-clock elapsed time and native `/usr/bin/time -p -l` CPU/RSS accounting; Linux uses wall-clock elapsed time and wait4 accounting. Ordinary Release binaries were copied before test builds and remain frozen. macOS and OrbStack timing ran separately, with builds, tests, bulk transfers and corpus audits outside those timing windows. swift-dev ran independently. Measurement free-space guards retain at least 3 GiB and room for the next output.

| Platform | Ordinary baseline bytes | Ordinary candidate bytes | Direct linkage |
|---|---:|---:|---|
{chr(10).join(artifact_rows)}

These are ordinary Release artifacts, not a static shipping-profile comparison. Foundation remains linked. Linux records the actual runtime files and any verified read-only aliases; copied-directory or library-size claims must not be substituted for actual loading provenance or RSS.

## Limitations and preservation

These are warm-cache within-platform observations, not cross-hardware rankings or general launch-time results. macOS CPU accounting has 0.01-second resolution. Linux wait4 peak RSS can include a pre-exec parent-process floor; no floor is subtracted. The selected corpora do not establish a general Unicode or JSON performance improvement. System desktop activity and scheduling noise are not eliminated by matched order, so all spreads and follow-ups remain visible.

Pre-timing setup failures are retained: a sandbox-denied Mac process inventory was repeated in an authorized context; the original macOS-created P archive carried AppleDouble sidecars, which swift-dev quarantined before verifying its exact source inventory; and an initial remote harness-placement check was corrected without changing the frozen script. The original archive remains preserved. `control/P-source-portable.tar` contains exactly the 1,945 candidate files and is verified against the source freeze. A report-index field-name correction affected metadata only. None of these recoveries changed candidate source or discarded a measured observation.

See [REPRODUCING.md](REPRODUCING.md), [candidate-patch.json](candidate-patch.json), and [evidence-export.json](evidence-export.json). Original source archives, frozen executables/runtime identities, fixtures, harnesses, logs, every observation and failed setup remain in the new Downloads experiments. Public evidence copies redact local paths while retaining numeric/boolean values and recording original/exported hashes.

Historical experiments and unrelated working files remain preserved. This report describes the experiment's completion state: the prototype is uncommitted for review, with no push, PR, merge or release included.
'''

output = ROOT / 'analysis/report-narrative-01'
output.mkdir(exist_ok=False)
(output / 'RESULTS.md').write_text(report)
print(json.dumps({'report': str(output / 'RESULTS.md'), 'measured': measured, 'warmups': warmups}))
