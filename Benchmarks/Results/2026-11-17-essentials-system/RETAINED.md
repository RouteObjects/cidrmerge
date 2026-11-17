# Retained prototype: direct baseline comparison

All changes are paired `100 × (R3 / B − 1)`. Negative is lower elapsed time or memory. Brackets show the minimum and maximum paired change, not a confidence interval. Each throughput/stdin row has six pairs; each startup row has twenty. Follow-ups remain separate. Absolute medians are medians of observations, so their ratio can differ from the median paired change.

## macOS ARM64: million-entry file input

| Case | B elapsed (s) | R3 elapsed (s) | Paired elapsed change [min, max] | B peak RSS (MiB) | R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|---:|
| ipv4-canonical / no stats (primary) | 0.1993 | 0.1493 | -24.59% [-25.85%, -24.24%] | 56.16 | 56.12 | -0.08% [-0.14%, +0.48%] |
| ipv4-canonical / stats (primary) | 0.2179 | 0.1713 | -21.65% [-26.01%, -19.19%] | 57.32 | 57.32 | +0.01% [-0.08%, +1.30%] |
| ipv6-canonical / no stats (primary) | 0.3362 | 0.2766 | -18.26% [-19.98%, -16.60%] | 146.77 | 146.68 | -0.06% [-0.16%, -0.04%] |
| ipv6-canonical / stats (primary) | 0.4086 | 0.3484 | -15.61% [-21.55%, -12.96%] | 147.94 | 147.91 | -0.02% [-0.04%, -0.02%] |
| mixed-noncanonical / no stats (primary) | 0.3477 | 0.2633 | -24.09% [-25.01%, -20.33%] | 102.36 | 101.77 | -0.27% [-1.59%, +0.98%] |
| mixed-noncanonical / stats (primary) | 0.3969 | 0.3115 | -21.35% [-22.12%, -19.86%] | 102.98 | 103.22 | -0.01% [-0.90%, +1.08%] |
| mixed-addresses / no stats (primary) | 0.3374 | 0.2563 | -23.94% [-25.56%, -20.17%] | 113.62 | 113.48 | -0.10% [-0.77%, +1.75%] |
| mixed-addresses / stats (primary) | 0.3846 | 0.3063 | -20.10% [-21.58%, -19.65%] | 114.73 | 114.66 | -0.07% [-1.33%, +0.00%] |
| mixed-ranges / no stats (primary) | 2.9361 | 2.7718 | -5.43% [-5.88%, -3.13%] | 115.67 | 114.88 | -0.70% [-1.09%, +0.84%] |
| mixed-ranges / stats (primary) | 3.0597 | 2.9118 | -4.72% [-5.20%, -2.58%] | 116.30 | 116.53 | +0.30% [-0.78%, +0.94%] |
| mixed-overlap / no stats (primary) | 0.3002 | 0.2454 | -18.22% [-18.95%, -17.67%] | 65.71 | 65.58 | -0.19% [-2.46%, +2.07%] |
| mixed-overlap / stats (primary) | 0.3475 | 0.2931 | -15.77% [-17.54%, -15.38%] | 66.84 | 67.14 | +0.51% [-3.39%, +2.66%] |
| searchbot-canonical / no stats (primary) | 1.6554 | 1.6395 | -1.16% [-1.62%, +1.13%] | 268.60 | 268.79 | -0.10% [-0.71%, +1.15%] |
| searchbot-canonical / stats (primary) | 1.6942 | 1.6903 | -0.36% [-2.03%, +0.76%] | 270.34 | 269.88 | -0.16% [-1.06%, +0.38%] |
| searchbot-noncanonical / no stats (primary) | 1.6582 | 1.6514 | -0.44% [-2.10%, +0.01%] | 289.78 | 290.31 | +0.11% [-0.33%, +0.39%] |
| searchbot-noncanonical / stats (primary) | 1.7160 | 1.6968 | -0.80% [-2.04%, +2.77%] | 291.35 | 290.45 | -0.25% [-0.33%, +1.04%] |

### macOS ARM64: large redirected Searchbot stdin

| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|
| searchbot-canonical-no-stats / primary | 1617.980 | 1617.793 | +0.26% [-0.41%, +2.05%] | 268.22 / 271.58 | +1.25% [+0.67%, +1.79%] |
| searchbot-noncanonical-stats / primary | 1683.825 | 1687.131 | -0.11% [-0.68%, +1.09%] | 290.40 / 292.20 | +0.61% [+0.61%, +1.65%] |

### macOS ARM64: shipping-style warm-cache startup

| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 10.088 | 10.311 | +2.70% [-10.60%, +34.41%] | 6.72 / 6.72 | -0.23% [-0.46%, +0.70%] |
| empty-stdin / followup | 10.310 | 10.631 | +2.09% [-22.84%, +28.99%] | 6.73 / 6.73 | +0.23% [-0.46%, +0.93%] |
| mixed-100 / primary | 10.142 | 10.431 | +3.27% [-5.71%, +25.72%] | 6.88 / 6.94 | +0.91% [+0.23%, +1.59%] |
| mixed-100 / followup | 10.339 | 10.542 | +1.65% [-15.10%, +150.51%] | 6.88 / 6.95 | +1.14% [+0.23%, +1.37%] |
| mixed-10000 / primary | 12.894 | 12.559 | -3.35% [-13.53%, +5.76%] | 7.81 / 7.90 | +1.00% [-1.17%, +1.60%] |
| mixed-10000 / followup | 12.790 | 12.789 | -1.54% [-48.33%, +58.51%] | 7.81 / 7.89 | +1.00% [-2.51%, +3.21%] |
| version / primary | 9.837 | 10.249 | +4.19% [-14.72%, +16.22%] | 6.52 / 6.60 | +1.19% [+0.24%, +1.68%] |
| version / followup | 10.074 | 10.381 | +2.90% [-2.51%, +127.03%] | 6.55 / 6.60 | +0.72% [+0.00%, +1.92%] |
## Linux ARM64: million-entry file input

| Case | B elapsed (s) | R3 elapsed (s) | Paired elapsed change [min, max] | B peak RSS (MiB) | R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|---:|
| ipv4-canonical / no stats (primary) | 0.2533 | 0.1992 | -21.37% [-23.42%, -19.89%] | 42.24 | 36.71 | -13.10% [-13.21%, -13.02%] |
| ipv4-canonical / stats (primary) | 0.2878 | 0.2349 | -18.96% [-22.77%, -13.19%] | 45.30 | 36.70 | -18.98% [-19.13%, -18.94%] |
| ipv6-canonical / no stats (primary) | 0.3749 | 0.3128 | -16.46% [-17.25%, -13.81%] | 110.92 | 105.32 | -5.05% [-5.17%, -5.04%] |
| ipv6-canonical / stats (primary) | 0.4682 | 0.3990 | -13.96% [-15.89%, -11.20%] | 110.93 | 105.32 | -5.06% [-5.07%, -5.03%] |
| mixed-noncanonical / no stats (primary) | 0.3928 | 0.3083 | -21.14% [-21.97%, -20.68%] | 76.63 | 71.14 | -7.18% [-7.21%, -7.12%] |
| mixed-noncanonical / stats (primary) | 0.4597 | 0.3775 | -17.97% [-19.18%, -16.72%] | 76.65 | 71.12 | -7.22% [-7.27%, -7.17%] |
| mixed-addresses / no stats (primary) | 0.3803 | 0.3050 | -19.36% [-25.11%, -13.45%] | 76.59 | 71.09 | -7.18% [-7.31%, -7.05%] |
| mixed-addresses / stats (primary) | 0.4488 | 0.3742 | -16.77% [-20.43%, -13.77%] | 79.27 | 71.08 | -10.33% [-10.37%, -10.28%] |
| mixed-ranges / no stats (primary) | 3.2063 | 3.1118 | -3.74% [-4.15%, -0.52%] | 76.58 | 71.09 | -7.16% [-7.22%, -6.81%] |
| mixed-ranges / stats (primary) | 3.4094 | 3.2755 | -4.13% [-4.82%, -1.59%] | 80.53 | 71.09 | -11.73% [-11.76%, -11.63%] |
| mixed-overlap / no stats (primary) | 0.3232 | 0.2695 | -16.25% [-18.77%, -12.21%] | 66.96 | 61.44 | -8.23% [-8.28%, -8.22%] |
| mixed-overlap / stats (primary) | 0.3978 | 0.3314 | -17.01% [-22.17%, -10.42%] | 66.96 | 61.45 | -8.23% [-8.26%, -8.15%] |
| searchbot-canonical / no stats (primary) | 1.8382 | 1.8817 | +1.52% [-2.98%, +3.49%] | 179.62 | 174.09 | -3.08% [-3.09%, -3.06%] |
| searchbot-canonical / stats (primary) | 1.9210 | 1.9765 | +2.82% [+0.11%, +6.70%] | 179.62 | 174.08 | -3.08% [-3.16%, -3.08%] |
| searchbot-canonical / stats (followup-01) | 1.9390 | 1.9634 | +2.17% [-1.02%, +8.25%] | 179.65 | 174.09 | -3.11% [-3.14%, -3.06%] |
| searchbot-noncanonical / no stats (primary) | 1.8699 | 1.8977 | +1.89% [-2.49%, +4.20%] | 190.14 | 184.60 | -2.92% [-2.94%, -2.88%] |
| searchbot-noncanonical / stats (primary) | 1.9293 | 1.9541 | +1.96% [-2.81%, +6.31%] | 190.14 | 184.60 | -2.91% [-2.96%, -2.85%] |
| searchbot-noncanonical / stats (followup-01) | 1.9561 | 1.9595 | -1.00% [-7.00%, +2.29%] | 190.14 | 184.61 | -2.92% [-2.95%, -2.90%] |

### Linux ARM64: large redirected Searchbot stdin

| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|
| searchbot-canonical-no-stats / primary | 1850.566 | 1859.340 | +0.39% [-1.57%, +8.00%] | 179.37 / 173.84 | -3.08% [-3.09%, -3.03%] |
| searchbot-canonical-no-stats / followup-01 | 1858.259 | 1852.598 | +0.15% [-1.07%, +4.48%] | 179.35 / 173.84 | -3.08% [-3.11%, -3.03%] |
| searchbot-noncanonical-stats / primary | 1915.295 | 1967.187 | +2.13% [+0.91%, +8.87%] | 189.89 / 184.34 | -2.91% [-2.98%, -2.91%] |
| searchbot-noncanonical-stats / followup-01 | 1946.895 | 1969.260 | +1.31% [-5.42%, +4.27%] | 189.88 / 184.37 | -2.91% [-2.94%, -2.89%] |

### Linux ARM64: shipping-style warm-cache startup

| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 2.142 | 1.885 | -11.99% [-19.88%, +1.80%] | 17.73 / 17.73 | +0.00% [+0.00%, +0.76%] |
| mixed-100 / primary | 2.358 | 2.070 | -12.37% [-14.89%, +4.21%] | 17.73 / 17.73 | +0.00% [+0.00%, +0.00%] |
| mixed-10000 / primary | 4.714 | 4.019 | -14.75% [-26.12%, +9.55%] | 17.73 / 17.73 | +0.00% [+0.00%, +0.00%] |
| mixed-10000 / followup-01 | 4.669 | 3.974 | -14.89% [-21.28%, -7.26%] | 17.61 / 17.61 | +0.00% [-0.75%, +0.00%] |
| version / primary | 2.153 | 1.875 | -11.61% [-69.40%, -3.78%] | 17.73 / 17.73 | +0.00% [+0.00%, +0.00%] |
## Linux x86-64: million-entry file input

| Case | B elapsed (s) | R3 elapsed (s) | Paired elapsed change [min, max] | B peak RSS (MiB) | R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|---:|
| ipv4-canonical / no stats (primary) | 0.6780 | 0.6097 | -9.64% [-14.37%, -6.10%] | 43.37 | 37.69 | -13.11% [-13.56%, -12.88%] |
| ipv4-canonical / stats (primary) | 0.7909 | 0.6968 | -12.88% [-13.39%, +30.00%] | 46.68 | 37.67 | -19.31% [-19.37%, -18.64%] |
| ipv4-canonical / stats (followup-01) | 0.7904 | 0.6870 | -13.44% [-19.31%, -7.95%] | 46.60 | 37.76 | -19.01% [-19.29%, -18.75%] |
| ipv6-canonical / no stats (primary) | 1.2747 | 1.1657 | -8.24% [-16.91%, -2.48%] | 112.12 | 106.45 | -5.06% [-5.19%, -4.67%] |
| ipv6-canonical / stats (primary) | 1.6176 | 1.5056 | -8.53% [-20.33%, -3.65%] | 112.07 | 106.34 | -5.16% [-5.26%, -4.97%] |
| mixed-noncanonical / no stats (primary) | 1.2132 | 1.1208 | -7.86% [-10.87%, -5.66%] | 77.79 | 72.21 | -7.16% [-7.47%, -7.10%] |
| mixed-noncanonical / stats (primary) | 1.4833 | 1.4125 | -7.45% [-13.25%, -3.61%] | 77.79 | 72.20 | -7.17% [-7.33%, -7.05%] |
| mixed-addresses / no stats (primary) | 1.1346 | 1.0521 | -7.10% [-10.14%, -1.74%] | 77.71 | 72.10 | -7.25% [-7.52%, -7.01%] |
| mixed-addresses / stats (primary) | 1.4109 | 1.2580 | -10.58% [-16.58%, +1.89%] | 80.55 | 72.11 | -10.48% [-10.73%, -10.37%] |
| mixed-ranges / no stats (primary) | 14.1610 | 13.9845 | -2.17% [-31.68%, -0.39%] | 77.87 | 72.25 | -7.20% [-7.37%, -7.15%] |
| mixed-ranges / stats (primary) | 15.4331 | 15.0419 | -1.88% [-6.10%, +2.78%] | 82.04 | 72.30 | -11.84% [-12.02%, -11.75%] |
| mixed-overlap / no stats (primary) | 1.1428 | 1.0768 | -6.35% [-10.84%, -2.51%] | 68.20 | 62.46 | -8.41% [-8.49%, -8.18%] |
| mixed-overlap / stats (primary) | 1.4054 | 1.3187 | -6.70% [-9.54%, -5.05%] | 68.13 | 62.49 | -8.25% [-8.44%, -8.06%] |
| searchbot-canonical / no stats (primary) | 7.4661 | 7.4182 | -1.61% [-3.71%, +67.24%] | 180.87 | 175.26 | -3.11% [-3.19%, -3.04%] |
| searchbot-canonical / no stats (followup-01) | 7.5255 | 7.3645 | -1.69% [-3.19%, +1.91%] | 180.86 | 175.25 | -3.11% [-3.18%, -2.99%] |
| searchbot-canonical / stats (primary) | 7.9225 | 7.9144 | -0.43% [-1.64%, +1.45%] | 180.83 | 175.17 | -3.12% [-3.17%, -3.05%] |
| searchbot-noncanonical / no stats (primary) | 7.7017 | 7.5135 | -2.97% [-46.54%, +1.88%] | 191.36 | 185.78 | -2.91% [-3.00%, -2.82%] |
| searchbot-noncanonical / stats (primary) | 8.0256 | 8.0106 | -1.36% [-1.97%, +32.40%] | 191.33 | 185.73 | -2.94% [-3.02%, -2.82%] |
| searchbot-noncanonical / stats (followup-01) | 8.0627 | 8.0335 | -0.29% [-2.73%, +3.68%] | 191.38 | 185.80 | -2.91% [-3.01%, -2.88%] |

### Linux x86-64: large redirected Searchbot stdin

| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|
| searchbot-canonical-no-stats / primary | 7480.426 | 7434.076 | -0.31% [-1.75%, +3.41%] | 180.67 / 175.06 | -3.11% [-3.15%, -3.07%] |
| searchbot-noncanonical-stats / primary | 8152.415 | 7967.427 | -1.25% [-3.87%, -0.42%] | 191.29 / 185.54 | -2.98% [-3.06%, -2.85%] |

### Linux x86-64: shipping-style warm-cache startup

| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 11.356 | 8.984 | -21.15% [-24.82%, -16.20%] | 18.91 / 18.91 | +0.00% [+0.00%, +0.00%] |
| mixed-100 / primary | 11.851 | 9.578 | -19.10% [-21.88%, -15.73%] | 18.91 / 18.91 | +0.00% [-0.66%, +0.67%] |
| mixed-10000 / primary | 21.790 | 17.786 | -17.83% [-24.92%, -14.29%] | 18.91 / 18.91 | +0.00% [-0.66%, +0.00%] |
| version / primary | 11.299 | 8.835 | -21.21% [-27.08%, -18.46%] | 18.91 / 18.91 | +0.00% [+0.00%, +0.00%] |

CPU time, ordinary startup, all intermediate variants, and individual pairs are retained in the companion CSV files. macOS CPU time is quantized to 0.01 seconds; tiny-call CPU percentages are not useful. The Linux fork/exec measurement harness can impose a peak-RSS floor on tiny calls; equal startup RSS is not evidence of equal application-only memory.
