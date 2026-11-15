# Public benchmark evidence

This directory contains **transformed exports**, not byte-for-byte raw measurements. Original JSON files, raw stdout/stderr, binaries, fixtures and profiler artifacts remain in the retained experiment. manifest.json binds every original JSON/script read by this exporter to its byte count and SHA-256; it also hashes each exported artifact.

Each platform contains all 132 measured samples and 22 excluded warmups, per-child elapsed/CPU/RSS/output hashes, 11 case tables with B/C medians and full paired median/min/max spreads, every one of the 66 pairs, and a >+5% individual-pair elapsed/RSS regression screen. Validation receipts are path-redacted copies. Raw scalar values are unrounded in JSON; Markdown tables are display-rounded. No sample is removed or retried by this exporter.

macOS CPU readings retain the resolution reported by /usr/bin/time -p; decimal display does not imply finer measurement precision. dependencies.json records all eight identical frozen B/C pins, including canonical URLs, versions and revisions.

The original independent audit receipts establish raw-output verification. This exporter reads only small JSON/control/script artifacts and checks their scalar consistency; it does not re-read large outputs or claim a second raw-output audit. Host-specific paths use $EXPERIMENT, $EXPERIMENT_REMOTE, $PLATFORM_ROOT, $BASELINE_REFERENCES, $PREVIOUS_PROFILE, $DOWNLOADS, $HOME, $TEMP or $TMP placeholders. Hardware serial numbers and hardware UUIDs are omitted.

Results apply to the fixed ASCII million-entry corpora and stated host/toolchain; the separate differential corpus covers fallback/error semantics, not their throughput. Peak RSS is not an allocation-count measurement. Paired min/max is the complete observed spread, not a confidence interval.
