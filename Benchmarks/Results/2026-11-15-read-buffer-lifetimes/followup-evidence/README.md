# Separate follow-up evidence

These transformed exports preserve all measured and excluded-warmup observations, every paired change, and full original summary scalar values. Follow-ups remain separate from each other and from their hash-bound primary summaries. No samples are pooled, discarded, or retried by this exporter.

Each run includes compact samples, independently recomputed comparisons, the full path-redacted original summary, bound independent-audit/control receipts, and byte-identical Python helpers. manifest.json preserves original small-artifact hashes and exported artifact hashes. Large output files are not reread; their hashes and byte counts are retained from the independently audited summary.

Private host paths use symbolic placeholders. Scripts belong with the main platform harness in a fresh experiment; do not run them in this report directory. Display tables round values; JSON preserves full scalars.
