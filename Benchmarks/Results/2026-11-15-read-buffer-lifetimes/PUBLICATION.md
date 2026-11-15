# Publication provenance

The benchmark report and its manifests capture the completed, initially uncommitted experiment. The original report, source snapshots, patches, binaries and raw results remain preserved in the Downloads experiment bundle.

Before publication, one comment in `Sources/CIDRMergeCLI/TextInput.swift` changed from `// CHANGE: Bound Foundation ...` to `// Bound Foundation ...`. No executable Swift code or line count changed. The focused test and all 69 original report artifacts remain byte-identical to the reviewed experiment. The original `production.patch`, source freeze and repository-preservation receipt intentionally retain their captured hashes and historical uncommitted state.

| Source snapshot | SHA-256 |
|---|---|
| Frozen benchmark candidate | `7adf989494c744de0af07de17cdc9dcfc5edaa48f79133952ebf541a0359e314` |
| Source prepared for the signed commit | `b3f27e796f6e1d5a537d3399dff4450aa7df601ef3036afeb3edd0c1d5470ecd` |

The signed commit includes this comment cleanup and this provenance note. The original three-platform tests, matched measurements and separate follow-ups remain applicable to the executable code; no measurements were rerun or replaced for the comment change. The PR checks validate the committed tree separately.
