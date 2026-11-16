# Raw UTF-8 writer publication provenance

Publication of `perf/raw-utf8-writers` was authorized on 2026-11-16 after the three-platform experiment completed. This handoff includes the renderer, its six focused tests and the [preserved experiment report](2026-11-16-raw-utf8-writers/RESULTS.md).

The report's statements about an uncommitted prototype, branch positions and review hashes describe the experiment at capture time. They are historical evidence; this companion records the later publication handoff. Original report bytes remain under `$HOME/Downloads/cidrmerge-raw-utf8-20261116T145749Z/report`.

The published renderer differs from frozen candidate C only by removing three `CHANGE:` markers from comments. Its executable Swift text is unchanged. The tests exactly match frozen C. Source hashes:

| Artifact | SHA-256 |
|---|---|
| Frozen renderer | d4103ef6b1edca08979940d2e1897b3f55e292a3a233461cfa0bab175b67573e |
| Publication renderer | cd24517b0916d5a644053d4267c3e7ba4f750ff8a0a938234652587a1bb91503 |
| Focused tests | a62087487cc7a16b77adc97bf6757dc5e5b34837d5bf9267191b755f6cdfb63d |

Three platform export manifests reword only their `path_redaction` description to avoid a false positive in the existing release-content audit. Their artifact hashes, numeric observations and other fields are unchanged. `FINAL_MANIFEST.json` refreshes the three affected file bindings; its experiment timestamp and status are retained. All other 719 report files remain byte-for-byte identical to the original. Earlier audit receipts, including the x86 export review, continue to identify their original snapshots; the table below maps those original hashes to the publication copies.

| Metadata file | Original SHA-256 | Publication SHA-256 |
|---|---|---|
| `macos/EXPORT_MANIFEST.json` | `a0da8e8526df1fe246499462f3c73001deacddc955e581736df719c78275a0df` | `17c041951785f5deb7643f9e1704c5d2f4a76797c76a5eaba62eb3ba8f32ea0e` |
| `arm64/EXPORT_MANIFEST.json` | `d95a7455afb8541e3d914cb545f7206cd4861214cfd80d414b0c6e39d7da8e0b` | `46529e6b86499655cfc75dda3daabf776950d803d24df4bbc96704af04030bd2` |
| `x86_64/EXPORT_MANIFEST.json` | `1eb8690595464afac201ef9cc89f57c9550ea9608e4072225329cb6112d1da8b` | `b37aae6595a066e259fc458e45c95904b00d822464c164d72705b59568bfc180` |
| `FINAL_MANIFEST.json` | `b0670c4759a028b55cdc85f449a2b7ffc694876e2cf96af61b31617646558c84` | `a55d2849de3a2029c429f3a8e773998cc25b8aec43cc8a4390978ca51e79dda8` |

The branch is based on the merged coalescing-report tree. No coalescing implementation or dependency update is included. The complete-output Data contract, MergeResult and OutputCommitter are retained. The original 1,062 test executions, 231 CLI differential comparisons, 504 measured samples and 84 warmups remain preserved; the reported large-output gains and roughly 2% x86 small-output cost are unchanged. Publication formatting, content audit and hosted CI are checked separately from the historical benchmark evidence.
