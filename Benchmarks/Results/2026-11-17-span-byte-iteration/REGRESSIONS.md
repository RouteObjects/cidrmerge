# Regression observations and fixed follow-ups

The predeclared trigger is any **primary** paired elapsed-time or peak-RSS increase above 5%, not only a median increase. Each affected configuration receives one separate fixed-size follow-up: six pairs for file/stdin. Follow-ups do not recursively trigger a third phase. No observation is discarded or pooled; all pairs, including unusually large positive and negative observations, remain in `pairs.csv`.

The repetition labels below describe primary/follow-up medians and are not significance tests. CPU values are retained in the complete measurements and CSVs, but CPU percentage was not the follow-up trigger.

## macOS ARM64

| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| throughput | text-ipv6-canonical-stats | elapsed | -2.05% [-16.55%, +10.00%] | -3.45% [-12.86%, +3.58%] | No repeated positive median regression |

### Every observed >5% elapsed/RSS increase

This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.

| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |
|---|---|---:|---|---:|---:|---:|
| throughput / primary | text-ipv6-canonical-stats | 5 | elapsed | 0.354256 s | 0.389695 s | +10.00% |

## Linux ARM64

| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| throughput | text-ipv6-canonical-no-stats | elapsed | -0.39% [-5.24%, +14.47%] | -0.77% [-3.01%, +0.80%] | No repeated positive median regression |
| throughput | text-ipv6-canonical-stats | elapsed | -0.52% [-11.15%, +6.83%] | -0.12% [-6.56%, +32.16%] | No repeated positive median regression |
| throughput | text-mixed-noncanonical-stats | elapsed | +0.13% [-5.14%, +9.22%] | +2.22% [-1.72%, +3.60%] | Small positive medians; inspect absolute size and spread |
| throughput | text-mixed-ranges-no-stats | elapsed | +0.04% [-4.75%, +6.59%] | -1.24% [-3.88%, +4.90%] | No repeated positive median regression |

### Every observed >5% elapsed/RSS increase

This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.

| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |
|---|---|---:|---|---:|---:|---:|
| throughput / followup | text-ipv6-canonical-stats | 6 | elapsed | 0.420683 s | 0.555965 s | +32.16% |
| throughput / primary | text-ipv6-canonical-no-stats | 3 | elapsed | 0.321966 s | 0.368554 s | +14.47% |
| throughput / primary | text-ipv6-canonical-stats | 4 | elapsed | 0.416124 s | 0.444533 s | +6.83% |
| throughput / primary | text-mixed-noncanonical-stats | 6 | elapsed | 0.386371 s | 0.421994 s | +9.22% |
| throughput / primary | text-mixed-ranges-no-stats | 4 | elapsed | 3.177316 s | 3.386588 s | +6.59% |

## Linux x86-64

| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| stdin | text-ipv4-canonical-no-stats | elapsed | -5.26% [-8.47%, +8.78%] | -4.04% [-5.17%, -2.79%] | No repeated positive median regression |
| stdin | text-mixed-noncanonical-stats | elapsed | -1.94% [-8.38%, +10.36%] | +0.18% [-5.16%, +9.57%] | No repeated positive median regression |
| throughput | text-ipv6-canonical-no-stats | elapsed | -2.44% [-8.68%, +5.87%] | -4.55% [-8.77%, -0.86%] | No repeated positive median regression |
| throughput | text-ipv6-canonical-stats | elapsed | -2.78% [-8.09%, +5.06%] | -1.14% [-5.51%, +2.63%] | No repeated positive median regression |

### Every observed >5% elapsed/RSS increase

This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.

| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |
|---|---|---:|---|---:|---:|---:|
| stdin / followup | text-mixed-noncanonical-stats | 2 | elapsed | 1.284385 s | 1.407303 s | +9.57% |
| stdin / primary | text-ipv4-canonical-no-stats | 1 | elapsed | 0.595071 s | 0.647311 s | +8.78% |
| stdin / primary | text-mixed-noncanonical-stats | 4 | elapsed | 1.300906 s | 1.435736 s | +10.36% |
| throughput / primary | text-ipv6-canonical-no-stats | 2 | elapsed | 1.098289 s | 1.162749 s | +5.87% |
| throughput / primary | text-ipv6-canonical-stats | 6 | elapsed | 1.434589 s | 1.507135 s | +5.06% |
