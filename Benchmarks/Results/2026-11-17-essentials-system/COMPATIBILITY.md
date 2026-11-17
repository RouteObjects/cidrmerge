# Compatibility scope and retained controls

This appendix concerns frozen R3, the retained FoundationEssentials/Swift System prototype with reusable read scratch. It does not summarize performance or claim release qualification. Paths are relative to the experiment root. The earlier `analysis/compatibility-review.md` reviewed frozen S2 and common compatibility code; it remains historical evidence rather than a claim that borrowed-line code is retained.

The reviewer authored `CLICompatibility.swift` and its focused tests, then reviewed the separately authored descriptor and buffer changes. This is not an independent review of every line. Preparation of this appendix used existing source and metadata only: no new builds, tests, probes, profiling or corpus/binary hashes.

## Preserved contracts

| Contract | Implementation and controls |
| --- | --- |
| Address/network/range interpretation | swift-cidr's parsers and the eight locked dependency revisions are unchanged. Text classification, canonical normalization counts when requested, deterministic IPv4-first output and exact coverage retain their existing paths. |
| Whole-line validation | The ASCII scan checks comment bytes too. Any non-ASCII byte takes the existing strict UTF-8 path before Character-based comment splitting. Invalid bytes after `#` still fail instead of disappearing as comments. |
| Unicode and trimming | Darwin keeps Foundation trimming. Linux uses scalar whitespace plus U+200B to match the tested Foundation set, including trimming within grapheme clusters. Comment splitting remains Character-based, including `#` with combining/keycap characters. |
| BOM, CR and source boundaries | First-line BOM removal, later/repeated BOM rejection behavior, CRLF/repeated CR handling, missing final newline, source/line/token diagnostics, repeated sources and empty sources preserve the original order. |
| Read ownership | R3 allocates one 64-KiB scratch buffer per text source and frees it with `defer`. Only the valid returned byte count is consumed. Each byte is copied into the owned pending array; no borrowed line slice is retained. Pending capacity is reused. |
| Fragmented reads | Partial UTF-8 scalars, BOMs, CRLF, invalid bytes and long lines can cross reads. Only EOF finishes a pending final line. Data and file loaders are compared for exact output/statistics or diagnostics. |
| Searchbot input | Named files still use `Data(contentsOf:)`. Stdin uses reusable scratch but accumulates one owned whole-document Data. Strict UTF-8 preflight, duplicate-member validation, decoding diagnostics and optional normalization counting are unchanged. |
| Descriptor ownership | Named text descriptors close in existing `defer` paths; injected/standard descriptors are borrowed and left open. Rejected Darwin directory descriptors close. Captured errors retain the failing operation and errno. |
| Output and checksum | Whole-output Data, atomic named writes, checksum-first ordering, basename validation and fail-atomic parse/merge behavior are unchanged. Standard streams synchronously borrow Data for Swift System `writeAll`. |
| Diagnostic compatibility | Descriptor, Cocoa, POSIX, LocalizedError and ordinary Swift Error branches have explicit controls. Darwin still uses Foundation's localized rendering. Linux reproduces the tested English Cocoa descriptions without importing full Foundation. |
| Percentages | Darwin keeps the POSIX-locale Foundation formatter. Linux rounds decimal digits from the shortest Double representation; this avoids C printf tie differences and integer overflow for count-derived percentages above Int.max. |
| Dependency boundary | SystemPackage is a direct CLI dependency at its already-locked revision. Core remains CIDR-only. External-consumer checks verify neither SystemPackage nor Crypto is compiled for a Core-only consumer. |

Retained source locations are `sources/R3/Sources/CIDRMergeCLI/{DescriptorIO,TextInput,SearchbotInput,CLICompatibility,DetachedSHA256Checksum,CIDRMergeApplication}.swift`. Focused tests are `sources/R3/Tests/CIDRMergeCLITests/{CLICompatibilityTests,DescriptorIOTests,ReadBufferLifetimeTests}.swift`. No S2 borrowed-slice test is counted as an R3 test.

## Personally inspected qualification evidence

The Mac environment receipt records macOS 27.2.1 build 26B131, Xcode 27.2 build 27B52 and Swift 6.4.2. Environment/hardware sources are `macos/control/environment.json` and `hardware-verified.json`.

| Mac gate | Baseline B | Retained R3 | Receipt |
| --- | ---: | ---: | --- |
| Debug suite | 85 passed | 95 passed | `macos/control/{B,R3}-test-debug.json` |
| Release suite | 85 passed | 95 passed | `macos/control/{B,R3}-test-release.json` |
| Standard exact differential | Reference | 254 cases, 508 processes passed | `macos/differential-R3/summary.json` |
| Expanded real-I/O differential | Reference | 84 cases passed | `macos/io-v2-R3-01/summary.json` |
| Expanded I/O self-control | 84 cases passed | — | `macos/io-v2-harness-self-control-01/summary.json` |
| Final source/consumer/documentation/smoke checks | Reference | Passed | `macos/final-validation-R3/summary.json` |

Test counts are Swift Testing totals across Core and CLI runs, not the XCTest compatibility shim's zero-test message. Baseline has 7 Core and 78 CLI tests; R3 has 7 Core and 88 CLI tests. The retained final-validation receipt includes delta whitespace, content audit, formatting, symbol graphs, DocC conversion, external Core consumer, Core dependency boundary and CLI smoke. Its delta whitespace command returns 1 with an empty diagnostic log because the snapshots differ; this is not a whitespace defect.

The standard differential compares identical source labels, exit status, exact stdout/stderr, statistics, raw/JSON output, checksum bytes and checksum validity. The real-I/O gate additionally preserves filesystem contents/modes and covers missing paths, parent-not-directory, directory operands, permission failures, excessive names, empty/dot/Unicode paths, symlink/dotdot and trailing-slash cases, atomic-output/checksum failures, invalid stdin descriptors and closed stdout. Linux-specific `/dev/full` and privileged permission controls are present in the harness but are not Mac test results.

Fragmented writers exercise strict UTF-8 before and after `#`, split Unicode, source-first BOMs, CRLF and lines spanning multiple 64-KiB reads. Child processes have 30-second timeouts, and a surviving writer is a failure. A 16-input/15-output fixture verifies a 6.25% percentage tie through the CLI.

Separate Mac slow-stdout controls used E4 and S2, whose writer is shared with R3. Both matched baseline and an independently generated 1,020,812-byte output for 60,000 disjoint mixed addresses, with 4,093-byte delayed reads and a 30-second timeout. Receipts are `macos/slow-stdout-E4-01/summary.json` and `macos/slow-stdout-S2-01/summary.json`. These are not separately executed R3 slow-stdout runs. Kernel short-write return counts were not instrumented; the actual retry loop is the locked Swift System `writeAll` implementation.

The complete qualification/artifact/audit maps are `analysis/macos-report-index.json`, `analysis/arm64-report-index.json` and `analysis/x86_64-report-index.json`. The retained qualification receipts on all three platforms were inspected for this appendix; one platform's results are not inferred from another.

### Completed native ARM64 Linux qualification

The recorded environment is native `aarch64-unknown-linux-gnu` under OrbStack with Swift 6.4.2. Baseline B passed 85 tests in each Debug/Release suite; R3 passed 95 in each. Retained R3 also passed 95 tests in each Debug/Release suite with Swift 6.2.4.

| ARM64 retained R3 gate | Result | Receipt |
| --- | --- | --- |
| Swift 6.4.2 Debug/Release | 95/95 passed | `arm64/control/qualification-R3/test-{debug,release}.json` |
| Swift 6.2.4 Debug/Release | 95/95 passed | `arm64/floor-6.2.4/control/qualification-R3/test-{debug,release}.json` |
| Standard exact differential | 254 cases / 508 processes passed | `arm64/behavior/differential-R3/summary.json` |
| Expanded real-I/O differential | 86 cases passed, zero failures | `arm64/behavior/io-v2-R3/summary.json` |
| Separate R3 slow-stdout control | 60,000 entries, exact 1,020,812-byte reference passed | `arm64/behavior/slow-stdout-R3/summary.json` |
| Final validation | Passed; source/binary unchanged | `arm64/final-validation-R3/summary.json` |
| Core-only consumer boundary | No compiled Crypto/SystemPackage; all eight pins unchanged | `arm64/final-validation-R3/core-boundary.json` |

Baseline receipts are under `arm64/control/qualification-B-attempt03/`; earlier attempts remain preserved. The ARM final validation covers formatting, source and shipping content audit, delta whitespace, public Core symbol graph, Core consumer and CLI smoke. Linux documentation qualification is symbol-graph emission/verification; full DocC conversion was performed on macOS, not claimed for Linux. Environment receipts are `arm64/control/qualification-R3/runtime.json` and the corresponding `floor-6.2.4` path. Platform failures and postprocessing recovery are recorded in `arm64/control/preserved-failures.json`.

### Completed x86-64 Linux qualification on swift-dev

The recorded environment is native x86-64 Linux with Swift 6.4.2. Baseline B passed 85 tests in each Debug/Release suite; retained R3 passed 95 in each. Swift 6.2.4 floor qualification was performed on ARM64 Linux, not x86-64.

| x86-64 retained R3 gate | Result | Receipt |
| --- | --- | --- |
| Swift 6.4.2 Debug/Release | 95/95 passed | `x86_64/retrieved/final-v2/control/build-tests-R3/R3-test-{debug,release}.json` |
| Standard exact differential | 254 cases / 508 processes passed | `x86_64/retrieved/final-v2/correctness/B-vs-R3/summary.json` |
| Expanded real-I/O differential | 86 cases passed, zero failures | `x86_64/retrieved/final-v2/correctness/io-B-vs-R3/summary.json` |
| Separate R3 slow-stdout control | 60,000 entries, exact 1,020,812-byte reference passed | `x86_64/retrieved/final-v2/correctness/slow-stdout-B-vs-R3/summary.json` |
| Final validation | Passed; source/binary unchanged | `x86_64/retrieved/final-v2/final-validation-R3/summary.json` |
| Core-only consumer boundary | No compiled Crypto/SystemPackage; all eight pins unchanged | `x86_64/retrieved/final-v2/final-validation-R3/core-boundary.json` |

Baseline suite receipts are under `x86_64/retrieved/final-v2/control/build-tests-B/`. Final validation covers formatting, source and shipping content audits, delta whitespace, public Core symbol graph, external Core consumer build/run and CLI smoke. As on ARM64, Linux documentation qualification is symbol-graph emission/verification; full DocC conversion is a macOS result. The environment is recorded in `x86_64/retrieved/final-v2/control/platform-preflight.json`.

The final index records 24 independently passed result audits and preserves separate primary/follow-up phases. The initial strict audit rejected a read-induced atime change; the separately versioned auditor retained content/hash and all other identity/time checks, with positive and negative controls. Retrieval initially stopped at an intentionally unreadable fixture; the failed archive is preserved, and the final archive preserved bytes and restored the twelve affected fixture modes remotely and locally. Neither recovery reran or altered measurements. Exact evidence paths and other transport/build limitations are listed in `analysis/x86_64-report-index.json` under `failure_and_limitation_ledgers`.

## Compatibility feasibility controls

All probe sources, logs and rejected approaches remain under `control/compatibility-probes/`.

- `digit3-mac.log` and `digit3-linux.log` each record 290,397 successful deterministic formatting comparisons, including decimal ties, adjacent Doubles, scientific notation and count ratios.
- `helper-run.log` and `helper624-run.log` each record 190,397 formatting comparisons and zero whitespace mismatches over every valid Unicode scalar, plus Cocoa/LocalizedError/plain/enum/POSIX controls. These are isolated ARM64 Linux helper probes on Swift 6.4.2 and 6.2.4, not whole-CLI platform qualification.
- `DIRECTORY_ERRNO.md`, `errno-dir.log` and `errno-wrapper.log` preserve Darwin's inherited-errno directory behavior. Controlled errno values 0, 1, 2, 9, 13, 21 and 28 produced Cocoa codes 512, 513, 4, 512, 513, 512 and 640. The final helper captures errno before closing; the unit oracle independently sets the same errno before baseline and candidate operations.
- String UTF-8 constructors were retained: they compile with Essentials on the tested Linux toolchains. This prototype does not add the proposed `String(validating:as:)` replacement as another variable.

## Preserved failures and superseded attempts

`analysis/review.json` is the machine-readable ledger; distinctions between an observed failure and a snapshot superseded without its own failure are intentional.

| Attempt | Observation and disposition | Evidence |
| --- | --- | --- |
| C `vsnprintf` percentage formatter | Rejected: differed from Foundation at decimal ties and large values. | `control/compatibility-probes/format.swift`, `format-run.log` |
| Initial Decimal probe | Included `zero.nextDown`, outside the caller's nonnegative domain; exited 133. Later valid-domain probes preserved separately. | `control/compatibility-probes/decimal.swift`, `decimal-mac-rerun.log` |
| `NSDecimalRound` replacement | Behavior matched tested values, but unavailable from FoundationEssentials alone. | `control/compatibility-probes/decimalessentials-build.log` |
| First pure-decimal carry routine | 117 retained mismatches; corrected digit2/digit3 controls passed. | `control/compatibility-probes/digit-mac.log`, `digit3-mac.log` |
| draftE01 | Standard differential and 88-test suites passed; expanded I/O exposed two failures among 74 cases: directory error mapping and relative permission context. | `macos/io-draftE01-01/summary.json`; corresponding build/test logs |
| E | 94-test suites passed. Superseded to inherit directory/path corrections; no separate failed E Mac I/O run is claimed. | `macos/control/E-test-{debug,release}.json`, `control/E2-freeze.json` |
| E2 | Compile failure: Swift System Errno has no `operationNotPermitted` member. Corrected with raw EPERM in E3. | `macos/control/E2-build-release.json`, corresponding log |
| E3 | Standard and 84-case I/O gates passed; controlled relative-directory unit test exposed inherited errno rather than fixed EPERM. | `macos/control/E3-test-debug.json`, `macos/io-v2-E3-01/summary.json` |
| R, R2, S | Superseded to incorporate common path/errno/audit corrections. R2 and S ordinary builds succeeded; S standard differential passed. Do not invent separate failures for these snapshots. | `control/{R,R2,S,R3,S2}-freeze.json`; `macos/control/{R2,S}-build-release.json` |
| S2 | Correctness-qualified borrowed-line candidate rejected after its separate performance experiment; R3 retained without mixing either variant's measurements. | `control/retained-candidate.json`, `analysis/borrowed-line-source-analysis.md` |
| final-validation-01 | Harness treated preserved historical files as new and failed whitespace on old artifacts. Corrected to inspect source delta; no historical files rewritten. | `macos/final-validation-01/summary.json`, `whitespace.log`; final R3 validation |
| Mac startup preflight | Required stripped aliases were absent. Failure occurred before any timed process: zero measured samples and zero product failures. | `macos/measurement-control/startup-preflight-failure.json`; replacement `startup/ordinary/B-vs-E4/primary-02` |

Platform-specific build, runtime, transport and postprocessing failures belong in their own ledgers/index. This table covers the reviewer's controls and does not replace those records.

## Remaining limits and maintenance cost

1. This removes full Foundation from the intended Linux implementation path, not from macOS. Darwin deliberately keeps Foundation for trimming, percentage formatting and diagnostics. Actual loader/static artifact receipts determine what ships; imports alone do not establish binary size or loaded libraries.
2. The compatibility layer adds maintained Unicode, decimal and error behavior. Future Swift/Foundation versions need renewed controls. The tested format domain is finite nonnegative percentages derived from integer counts; it is not a general-purpose Double formatter or a proof over every Double.
3. Generic Linux Error rendering uses underscored `Error._domain` and `Error._code`. Ordinary Swift error cases and LocalizedError are covered; this is an explicit future-compatibility dependency.
4. Essentials cannot introspect a custom-domain Foundation NSError's userInfo localization overrides. Actual CLI descriptor/Cocoa errors take supported branches, but unrestricted injected NSError interoperability is not claimed.
5. Darwin directory diagnostics inherit process errno, an observed baseline defect. Capturing errno and matching controlled/observed cases preserves that behavior without making its text deterministic across arbitrary prior process state.
6. Input scratch is bounded, not the entire application. The pending line grows to the longest line, Searchbot owns the complete document, merged arrays grow with the workload and raw output still returns whole-output Data. No zero-allocation or globally bounded-memory claim follows.
7. Slow-pipe controls establish complete delayed output and termination, not direct observation of every EINTR/short-write branch. Named descriptors are used synchronously, and the current CLI launches no child processes while they are open; descriptor inheritance in a future spawning application is outside this qualification.
8. The reviewer found no must-fix safety/correctness issue in the retained R3 source review. This is limited to the current synchronous CLI and preserved contracts, not a general systems-I/O library audit.

English Cocoa diagnostics and errno mappings were adapted from swift-corelibs-foundation `Sources/Foundation/NSError.swift` and `FoundationErrors.swift`, consulted on 2026-11-17. The original provenance URLs reference upstream main rather than a pinned revision; actual toolchain behavior is preserved in the probes. Copyright, Apache 2.0 and Runtime Library Exception attribution is present in `sources/R3/Sources/CIDRMergeCLI/CLICompatibility.swift` and `sources/R3/THIRD_PARTY_NOTICES.txt`. Percentage/scalar trimming code was independently written against observed behavior.

## Confirmed tiny-process RSS measurement limit

After timing ended on each Linux host, the unchanged `/bin/true` was measured through the same frozen Python Popen/wait4 route with 0, 32 and 96 MiB of additional parent allocation. Three observations per group passed on each host. Median reported child lifetime peak RSS increased with parent allocation despite using the same target executable:

| Linux host | Extra parent: 0 MiB | Extra parent: 32 MiB | Extra parent: 96 MiB |
| --- | ---: | ---: | ---: |
| ARM64 | 18,092,032 bytes (17.254 MiB) | 51,781,632 bytes (49.383 MiB) | 118,882,304 bytes (113.375 MiB) |
| x86-64 / swift-dev | 20,402,176 bytes (19.457 MiB) | 52,670,464 bytes (50.230 MiB) | 119,832,576 bytes (114.281 MiB) |

Evidence is `arm64/harness-controls/rss-fork-floor/summary.json` and `x86_64/retrieved/final-v2/correctness/rss-fork-floor/summary.json`; `arm64/control/rss-fork-floor-host.json` separately records ARM post-timing execution. These independent controls confirm inherited/pre-exec parent-memory influence for this measurement method on both Linux hosts. Tiny-process peak RSS is not isolated application-only memory, and equal startup values cannot establish equal application peaks below that floor. Preserve every original startup value; do not subtract the control, replace observations, or pool corrected values. These are measurement-method controls, not cidrmerge performance results, and do not invalidate elapsed-time observations. `analysis/report-drafts/ARTIFACTS.json` retains all eighteen control values and distinguishes dependent-file sizes from RSS.

The x86 runtime-resolution check also ran after timing under the unchanged measurement `LD_LIBRARY_PATH`. The Swift libraries resolve from preserved copies, while `libstdc++.so.6` and the ELF interpreter resolve through host paths. Every actual resolved file hash matches its premeasurement original and preserved copy. This is verified mixed resolution, not a claim that every runtime file loaded from the frozen directory. See `x86_64/retrieved/final-v2/control/actual-runtime-closure.json`.

## macOS deployment target and the added errno dylib

The frozen B and R3 shipping binaries both declare minimum macOS 15.0. R3 adds a strong `LC_LOAD_DYLIB` reference to `libswift_errno.dylib` with compatibility version 1.0.0; it is not weak-linked. Its undefined Darwin.errno getter binds to that library. The SDK explicitly maps errno accessor symbols to this library for macOS deployment targets from 15.0 up to, but excluding, 26.0, and maps older targets back to `libswiftDarwin`. Apple's linker implementation confirms those inclusive-start/exclusive-end rules. This supports the existing macOS 15 deployment target; no higher floor is indicated by the added dependency. [Apple linker source](https://github.com/apple-oss-distributions/ld64/blob/main/src/ld/parsers/generic_dylib_file.cpp#L249-L296).

Swift System 1.7.4 uses `Darwin.errno` in its normal source-package implementation. The package's macOS 26 platform declarations are conditional on its separate `SYSTEM_ABI_STABLE` build, not the normal SystemPackage dependency used here. Exact load commands, symbol inspection, SDK excerpts, locked source locations and limitations are preserved in `analysis/macos-errno-deployment-review.json`.

This is static SDK/linkage evidence, **not execution on macOS 15**: the test host is macOS 27.2.1. The dependency is strong, so a system missing the library or symbol could not load this executable; the SDK's explicit macOS 15 mapping is the evidence that this is an intended supported route. No weak-link workaround or deployment-floor change was made. [Apple dynamic-library compatibility guidance](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/DynamicLibraryDesignGuidelines.html).

## Retained R3 read-only review

The reviewer re-read the retained descriptor, text reader, Searchbot loader, output commit path, compatibility helper, manifest and focused tests after R3 was selected. Scratch allocation/deallocation is paired on success and error. Valid byte counts bound all raw-buffer reads. Pending bytes and constructed Strings own their storage before another read; R3 contains no borrowed-line generic path. Named descriptors close on scope exit, while standard streams remain borrowed. Darwin's directory decision uses `fstat` on the opened descriptor, avoiding a separate path-based race. Searchbot copies each valid scratch prefix into owned Data. Output bytes remain alive throughout synchronous `writeAll`. No changes were made during this review.
