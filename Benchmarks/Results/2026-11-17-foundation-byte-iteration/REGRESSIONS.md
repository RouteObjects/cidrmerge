# Regression observations and fixed follow-ups

The predeclared trigger is any **primary** paired elapsed-time or peak-RSS increase above 5%, not only a median increase. Each affected configuration receives one separate fixed-size follow-up: six pairs for file/stdin, twenty for startup. Follow-ups do not recursively trigger a third phase. No observation is discarded or pooled; all pairs, including unusually large positive and negative observations, remain in `pairs.csv`.

The repetition labels below describe primary/follow-up medians and are not significance tests. CPU values are retained in the complete measurements and CSVs, but CPU percentage was not the follow-up trigger.

## macOS ARM64

| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| startup | empty-stdin | elapsed | +1.86% [-26.48%, +34.78%] | +0.58% [-16.90%, +14.71%] | Small positive medians; inspect absolute size and spread |
| startup | mixed-100 | elapsed | -1.63% [-24.67%, +11.30%] | -1.09% [-15.24%, +31.01%] | No repeated positive median regression |
| startup | mixed-10000 | elapsed | -2.67% [-33.21%, +17.72%] | -3.90% [-26.68%, +12.34%] | No repeated positive median regression |
| startup | version | elapsed | -3.27% [-17.21%, +16.83%] | +0.80% [-8.31%, +13.51%] | No repeated positive median regression |
| throughput | searchbot-noncanonical-stats | elapsed | +0.28% [-1.42%, +5.38%] | +0.29% [-1.96%, +6.91%] | Small positive medians; inspect absolute size and spread |

### Every observed >5% elapsed/RSS increase

This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.

| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |
|---|---|---:|---|---:|---:|---:|
| startup / followup | empty-stdin | 4 | elapsed | 0.013049 s | 0.014154 s | +8.46% |
| startup / followup | empty-stdin | 9 | elapsed | 0.013762 s | 0.014761 s | +7.25% |
| startup / followup | empty-stdin | 14 | elapsed | 0.012590 s | 0.014442 s | +14.71% |
| startup / followup | empty-stdin | 17 | elapsed | 0.012251 s | 0.013758 s | +12.30% |
| startup / followup | mixed-100 | 3 | elapsed | 0.011882 s | 0.012831 s | +7.99% |
| startup / followup | mixed-100 | 4 | elapsed | 0.012742 s | 0.014326 s | +12.43% |
| startup / followup | mixed-100 | 5 | elapsed | 0.012867 s | 0.013992 s | +8.74% |
| startup / followup | mixed-100 | 7 | elapsed | 0.014743 s | 0.016217 s | +10.00% |
| startup / followup | mixed-100 | 11 | elapsed | 0.012297 s | 0.016109 s | +31.01% |
| startup / followup | mixed-100 | 15 | elapsed | 0.012217 s | 0.013886 s | +13.66% |
| startup / followup | mixed-10000 | 17 | elapsed | 0.014463 s | 0.016248 s | +12.34% |
| startup / followup | version | 3 | elapsed | 0.011851 s | 0.012532 s | +5.75% |
| startup / followup | version | 4 | elapsed | 0.011969 s | 0.012612 s | +5.37% |
| startup / followup | version | 5 | elapsed | 0.013315 s | 0.014493 s | +8.85% |
| startup / followup | version | 7 | elapsed | 0.013103 s | 0.014273 s | +8.93% |
| startup / followup | version | 9 | elapsed | 0.013801 s | 0.014846 s | +7.58% |
| startup / followup | version | 10 | elapsed | 0.013058 s | 0.014454 s | +10.69% |
| startup / followup | version | 18 | elapsed | 0.012534 s | 0.014227 s | +13.51% |
| startup / followup | version | 19 | elapsed | 0.012026 s | 0.013589 s | +13.00% |
| startup / primary | empty-stdin | 1 | elapsed | 0.014664 s | 0.015790 s | +7.68% |
| startup / primary | empty-stdin | 2 | elapsed | 0.012888 s | 0.014865 s | +15.34% |
| startup / primary | empty-stdin | 5 | elapsed | 0.012713 s | 0.014586 s | +14.73% |
| startup / primary | empty-stdin | 9 | elapsed | 0.011872 s | 0.016001 s | +34.78% |
| startup / primary | empty-stdin | 17 | elapsed | 0.012329 s | 0.014263 s | +15.69% |
| startup / primary | empty-stdin | 20 | elapsed | 0.011767 s | 0.013043 s | +10.85% |
| startup / primary | mixed-100 | 12 | elapsed | 0.013037 s | 0.014511 s | +11.30% |
| startup / primary | mixed-100 | 20 | elapsed | 0.012399 s | 0.013760 s | +10.97% |
| startup / primary | mixed-10000 | 9 | elapsed | 0.014881 s | 0.017518 s | +17.72% |
| startup / primary | mixed-10000 | 15 | elapsed | 0.015192 s | 0.016168 s | +6.42% |
| startup / primary | mixed-10000 | 20 | elapsed | 0.015645 s | 0.016503 s | +5.48% |
| startup / primary | version | 11 | elapsed | 0.011956 s | 0.012624 s | +5.59% |
| startup / primary | version | 15 | elapsed | 0.012737 s | 0.014880 s | +16.83% |
| throughput / followup | searchbot-noncanonical-stats | 5 | elapsed | 1.718455 s | 1.837206 s | +6.91% |
| throughput / primary | searchbot-noncanonical-stats | 1 | elapsed | 1.750197 s | 1.844393 s | +5.38% |

## Linux ARM64

| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| startup | empty-stdin | elapsed | -0.54% [-32.31%, +13.56%] | +1.83% [-9.58%, +10.17%] | No repeated positive median regression |
| startup | mixed-100 | elapsed | -2.26% [-14.65%, +22.31%] | -1.23% [-81.32%, +19.40%] | No repeated positive median regression |
| startup | mixed-10000 | elapsed | -6.47% [-16.62%, +305.62%] | -6.99% [-69.75%, +5.43%] | No repeated positive median regression |
| startup | version | elapsed | -4.76% [-54.41%, +54.32%] | +0.91% [-15.48%, +23.75%] | No repeated positive median regression |
| throughput | searchbot-canonical-no-stats | elapsed | +3.82% [-3.98%, +38.33%] | +2.01% [-4.35%, +12.40%] | Small positive medians; inspect absolute size and spread |
| throughput | searchbot-canonical-stats | elapsed | -2.26% [-14.10%, +16.14%] | -0.88% [-5.34%, +22.32%] | No repeated positive median regression |
| throughput | searchbot-noncanonical-no-stats | elapsed | +4.31% [-2.83%, +15.68%] | -1.58% [-7.66%, +8.43%] | No repeated positive median regression |
| throughput | searchbot-noncanonical-stats | elapsed | -1.41% [-10.48%, +9.28%] | +1.46% [-3.62%, +5.88%] | No repeated positive median regression |
| throughput | text-mixed-addresses-no-stats | elapsed | -18.11% [-34.64%, +8.52%] | -18.67% [-26.04%, +4.63%] | No repeated positive median regression |

### Every observed >5% elapsed/RSS increase

This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.

| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |
|---|---|---:|---|---:|---:|---:|
| startup / followup | empty-stdin | 2 | elapsed | 0.005460 s | 0.005943 s | +8.85% |
| startup / followup | empty-stdin | 6 | elapsed | 0.004698 s | 0.004959 s | +5.57% |
| startup / followup | empty-stdin | 9 | elapsed | 0.004727 s | 0.005191 s | +9.81% |
| startup / followup | empty-stdin | 10 | elapsed | 0.004834 s | 0.005295 s | +9.54% |
| startup / followup | empty-stdin | 12 | elapsed | 0.005052 s | 0.005466 s | +8.20% |
| startup / followup | empty-stdin | 13 | elapsed | 0.005625 s | 0.006197 s | +10.17% |
| startup / followup | mixed-100 | 4 | elapsed | 0.005518 s | 0.006230 s | +12.89% |
| startup / followup | mixed-100 | 6 | elapsed | 0.005072 s | 0.005876 s | +15.87% |
| startup / followup | mixed-100 | 9 | elapsed | 0.005874 s | 0.007014 s | +19.40% |
| startup / followup | mixed-100 | 13 | elapsed | 0.005503 s | 0.006179 s | +12.28% |
| startup / followup | mixed-100 | 14 | elapsed | 0.005729 s | 0.006299 s | +9.95% |
| startup / followup | mixed-100 | 19 | elapsed | 0.005431 s | 0.005851 s | +7.73% |
| startup / followup | mixed-10000 | 11 | elapsed | 0.009477 s | 0.009992 s | +5.43% |
| startup / followup | version | 2 | elapsed | 0.005386 s | 0.006193 s | +14.98% |
| startup / followup | version | 4 | elapsed | 0.004854 s | 0.005570 s | +14.73% |
| startup / followup | version | 6 | elapsed | 0.004552 s | 0.005053 s | +11.01% |
| startup / followup | version | 7 | elapsed | 0.005097 s | 0.005761 s | +13.03% |
| startup / followup | version | 15 | elapsed | 0.005259 s | 0.005732 s | +8.99% |
| startup / followup | version | 16 | elapsed | 0.004586 s | 0.005675 s | +23.75% |
| startup / primary | empty-stdin | 6 | elapsed | 0.005327 s | 0.005725 s | +7.45% |
| startup / primary | empty-stdin | 7 | elapsed | 0.004985 s | 0.005661 s | +13.56% |
| startup / primary | empty-stdin | 12 | elapsed | 0.005247 s | 0.005648 s | +7.64% |
| startup / primary | empty-stdin | 14 | elapsed | 0.005177 s | 0.005504 s | +6.31% |
| startup / primary | empty-stdin | 18 | elapsed | 0.005212 s | 0.005699 s | +9.35% |
| startup / primary | mixed-100 | 3 | elapsed | 0.005458 s | 0.006008 s | +10.08% |
| startup / primary | mixed-100 | 8 | elapsed | 0.005230 s | 0.005673 s | +8.47% |
| startup / primary | mixed-100 | 9 | elapsed | 0.005344 s | 0.006536 s | +22.31% |
| startup / primary | mixed-100 | 10 | elapsed | 0.005123 s | 0.005402 s | +5.44% |
| startup / primary | mixed-100 | 11 | elapsed | 0.005593 s | 0.006155 s | +10.05% |
| startup / primary | mixed-100 | 12 | elapsed | 0.005568 s | 0.006111 s | +9.75% |
| startup / primary | mixed-10000 | 15 | elapsed | 0.010025 s | 0.040665 s | +305.62% |
| startup / primary | mixed-10000 | 17 | elapsed | 0.028757 s | 0.040744 s | +41.69% |
| startup / primary | version | 5 | elapsed | 0.004940 s | 0.005210 s | +5.47% |
| startup / primary | version | 8 | elapsed | 0.005132 s | 0.007920 s | +54.32% |
| startup / primary | version | 10 | elapsed | 0.004749 s | 0.005195 s | +9.39% |
| startup / primary | version | 11 | elapsed | 0.005248 s | 0.005529 s | +5.36% |
| throughput / followup | searchbot-canonical-no-stats | 3 | elapsed | 1.937475 s | 2.073616 s | +7.03% |
| throughput / followup | searchbot-canonical-no-stats | 6 | elapsed | 1.929197 s | 2.168399 s | +12.40% |
| throughput / followup | searchbot-canonical-stats | 1 | elapsed | 2.003561 s | 2.450838 s | +22.32% |
| throughput / followup | searchbot-noncanonical-no-stats | 3 | elapsed | 1.912280 s | 2.062585 s | +7.86% |
| throughput / followup | searchbot-noncanonical-no-stats | 4 | elapsed | 1.934311 s | 2.097294 s | +8.43% |
| throughput / followup | searchbot-noncanonical-stats | 6 | elapsed | 1.996680 s | 2.114039 s | +5.88% |
| throughput / primary | searchbot-canonical-no-stats | 1 | elapsed | 2.134779 s | 2.953068 s | +38.33% |
| throughput / primary | searchbot-canonical-no-stats | 6 | elapsed | 1.828188 s | 1.925807 s | +5.34% |
| throughput / primary | searchbot-canonical-stats | 4 | elapsed | 2.071486 s | 2.405812 s | +16.14% |
| throughput / primary | searchbot-noncanonical-no-stats | 3 | elapsed | 1.892468 s | 2.068376 s | +9.30% |
| throughput / primary | searchbot-noncanonical-no-stats | 4 | elapsed | 1.919895 s | 2.220902 s | +15.68% |
| throughput / primary | searchbot-noncanonical-stats | 1 | elapsed | 1.970927 s | 2.071455 s | +5.10% |
| throughput / primary | searchbot-noncanonical-stats | 6 | elapsed | 1.941274 s | 2.121393 s | +9.28% |
| throughput / primary | text-mixed-addresses-no-stats | 1 | elapsed | 0.386433 s | 0.419337 s | +8.52% |

## Linux x86-64

| Workload | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| throughput | searchbot-canonical-stats | elapsed | +0.72% [-0.60%, +17.05%] | -0.54% [-6.58%, +3.36%] | No repeated positive median regression |
| throughput | searchbot-noncanonical-stats | elapsed | +1.74% [-2.72%, +10.33%] | +1.72% [-6.02%, +3.06%] | Small positive medians; inspect absolute size and spread |
| throughput | text-mixed-noncanonical-no-stats | elapsed | -15.33% [-21.85%, +14.24%] | -15.79% [-19.68%, -13.71%] | No repeated positive median regression |
| throughput | text-mixed-ranges-stats | elapsed | -0.56% [-3.69%, +70.82%] | -4.78% [-6.41%, -2.31%] | No repeated positive median regression |

### Every observed >5% elapsed/RSS increase

This register includes both primary and follow-up observations. It does not classify or remove statistical outliers; complete observations of every size and sign remain in the CSV.

| Workload / phase | Case | Pair | Metric | B value | P value | Paired change |
|---|---|---:|---|---:|---:|---:|
| throughput / primary | searchbot-canonical-stats | 1 | elapsed | 7.892500 s | 9.238444 s | +17.05% |
| throughput / primary | searchbot-noncanonical-stats | 1 | elapsed | 8.559660 s | 9.444096 s | +10.33% |
| throughput / primary | text-mixed-noncanonical-no-stats | 2 | elapsed | 1.294579 s | 1.478890 s | +14.24% |
| throughput / primary | text-mixed-ranges-stats | 2 | elapsed | 15.311281 s | 26.155055 s | +70.82% |
