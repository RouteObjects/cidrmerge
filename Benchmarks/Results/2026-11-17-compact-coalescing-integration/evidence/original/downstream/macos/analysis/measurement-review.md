# Audited macOS integration measurements

All four phases passed independent full-byte, hash, schedule, resource and statistical audits: 336 measured observations and 56 warmups (396 measured and 66 warmup CLI processes). All 28 case-phase summaries retain six pairs. Sources, binaries and every premeasurement-bound file remain unchanged. Postmeasurement OS build, compiler hash, shared-cache identity and all 17 linked image UUIDs match their prematched records.

| Case | Phase | B median ms | C median ms | Paired median delta ms | Paired median % | Paired min…max % | Slower pairs | B/C median RSS MiB |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| mixed-permuted-1000 | primary | 13.388 | 13.958 | +0.978 | +6.97 | -5.62…+9.95 | 5/6 | 7.0469/7.0703 |
| mixed-overlap-1000 | primary | 13.710 | 15.259 | +1.549 | +11.29 | -6.40…+33.79 | 4/6 | 6.9688/6.9688 |
| mixed-adjacent-1000 | primary | 13.428 | 14.242 | +0.698 | +5.82 | -3.12…+48.68 | 4/6 | 6.9688/6.9688 |
| mixed-permuted-1000 | followup | 14.790 | 13.429 | -0.546 | -3.78 | -33.86…+35.68 | 2/6 | 7.0469/7.0703 |
| mixed-overlap-1000 | followup | 12.479 | 13.571 | +1.366 | +9.80 | -13.64…+32.82 | 3/6 | 6.9766/6.9844 |
| mixed-adjacent-1000 | followup | 14.938 | 13.820 | -1.420 | -9.54 | -25.47…+5.72 | 1/6 | 7.0078/6.9766 |

`mixed-overlap-1000` retains repeated above 5% paired-median elapsed regressions: +11.29% and +9.80%, corresponding to paired absolute median increases of 1.549 ms and 1.366 ms. The followup has only three slower pairs out of six and spans −13.64% to +32.82%. This is a repeated measured median regression with a small absolute magnitude and uncertain mechanism, not evidence of a consistently slower operation in every pair. The elapsed interval includes process launch, `/usr/bin/time` and CLI I/O.

The other two primary triggers reverse direction in the fixed followup (permuted −3.78%, adjacent −9.54%); their direction is inconclusive. None of these tiny cases has a repeated peak-RSS increase. Absolute RSS medians are approximately 7 MiB.

Every measured user/system CPU field in these three primary and followup cases prints 0.00 at the native tool’s 0.01-second resolution. Consequently, CPU percentage changes are undefined here; the observations cannot establish zero CPU cost or attribute elapsed changes to coalescing. No extra rerun was added.

For context, the large range-derived mixed case has a −27.10% paired-median RSS change; its elapsed paired median is +0.23%. The million-base-entry sparse case has elapsed +0.46% and RSS −1.53% paired medians. Those retain their six-pair variation and remain distinct from the tiny-case followup evidence.

Exact rows, paired spreads, absolute medians and source receipts are preserved in `measurement-review.json`.
