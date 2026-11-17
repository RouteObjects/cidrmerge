# x86-64 Linux (swift-dev): optional normalization accounting

B is the frozen baseline; C is candidate C2. Negative percentage changes favor C.
Elapsed time covers the complete invocation; CPU is user plus system time. RSS is reported in MiB (2^20 bytes).
Each change is the median of six paired percentage changes. Brackets show the observed minimum and maximum, not a confidence interval.
Primary runs and follow-ups remain separate; no observations are pooled or discarded.

## Primary

192 measured samples; 32 excluded warmups; 16 configurations.
Evidence: `x86_64/measurements/summary.json` and corresponding sample JSON files.

### Elapsed time

| Configuration | B median (ms) | C median (ms) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 805.019 | 668.632 | -16.14% | [-25.65%, -9.05%] |
| text-ipv4-canonical (--stats) | 749.123 | 787.289 | +4.66% | [-11.81%, +7.55%] |
| text-ipv6-canonical (no stats) | 1530.634 | 1239.132 | -18.46% | [-23.54%, -15.06%] |
| text-ipv6-canonical (--stats) | 1537.795 | 1593.070 | +3.59% | [-7.65%, +6.92%] |
| text-mixed-noncanonical (no stats) | 1497.737 | 1231.300 | -16.05% | [-18.67%, -13.16%] |
| text-mixed-noncanonical (--stats) | 1480.090 | 1471.026 | -0.12% | [-2.56%, +4.41%] |
| text-mixed-addresses (no stats) | 1390.737 | 1153.545 | -16.63% | [-19.52%, -11.47%] |
| text-mixed-addresses (--stats) | 1392.647 | 1401.095 | +1.39% | [-4.23%, +3.98%] |
| text-mixed-ranges (no stats) | 15399.590 | 14178.574 | -7.88% | [-13.15%, -5.50%] |
| text-mixed-ranges (--stats) | 15279.207 | 15264.811 | +0.18% | [-0.50%, +6.44%] |
| text-mixed-overlap (no stats) | 1378.663 | 1138.569 | -17.08% | [-20.13%, -15.87%] |
| text-mixed-overlap (--stats) | 1386.280 | 1413.984 | +2.52% | [-1.92%, +5.46%] |
| searchbot-canonical (no stats) | 7787.313 | 7444.792 | -3.98% | [-6.30%, +0.73%] |
| searchbot-canonical (--stats) | 7787.059 | 7985.077 | +2.52% | [+1.10%, +6.94%] |
| searchbot-noncanonical (no stats) | 8056.024 | 7578.599 | -5.33% | [-8.01%, -1.30%] |
| searchbot-noncanonical (--stats) | 8083.169 | 8132.309 | +1.07% | [-2.27%, +3.76%] |

### CPU time

| Configuration | B median (s) | C median (s) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 0.8018 | 0.6655 | -16.19% | [-25.78%, -9.05%] |
| text-ipv4-canonical (--stats) | 0.7460 | 0.7843 | +4.70% | [-11.89%, +7.58%] |
| text-ipv6-canonical (no stats) | 1.5276 | 1.2361 | -18.47% | [-23.54%, -15.08%] |
| text-ipv6-canonical (--stats) | 1.5344 | 1.5895 | +3.59% | [-7.68%, +6.93%] |
| text-mixed-noncanonical (no stats) | 1.4943 | 1.2280 | -16.09% | [-18.72%, -13.18%] |
| text-mixed-noncanonical (--stats) | 1.4768 | 1.4676 | -0.13% | [-2.58%, +4.42%] |
| text-mixed-addresses (no stats) | 1.3875 | 1.1504 | -16.63% | [-19.57%, -11.49%] |
| text-mixed-addresses (--stats) | 1.3893 | 1.3981 | +1.40% | [-4.24%, +4.01%] |
| text-mixed-ranges (no stats) | 15.3899 | 14.1692 | -7.89% | [-13.15%, -5.50%] |
| text-mixed-ranges (--stats) | 15.2701 | 15.2549 | +0.18% | [-0.51%, +6.44%] |
| text-mixed-overlap (no stats) | 1.3755 | 1.1356 | -17.09% | [-20.18%, -15.90%] |
| text-mixed-overlap (--stats) | 1.3835 | 1.4108 | +2.39% | [-1.89%, +5.44%] |
| searchbot-canonical (no stats) | 7.7815 | 7.4391 | -3.98% | [-6.30%, +0.73%] |
| searchbot-canonical (--stats) | 7.7810 | 7.9789 | +2.53% | [+1.10%, +6.95%] |
| searchbot-noncanonical (no stats) | 8.0496 | 7.5732 | -5.33% | [-8.02%, -1.30%] |
| searchbot-noncanonical (--stats) | 8.0771 | 8.1262 | +1.07% | [-2.27%, +3.76%] |

### Peak resident memory

| Configuration | B median (MiB) | C median (MiB) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 43.400 | 43.355 | -0.03% | [-0.26%, +0.30%] |
| text-ipv4-canonical (--stats) | 46.668 | 46.678 | -0.01% | [-0.15%, +0.31%] |
| text-ipv6-canonical (no stats) | 112.176 | 112.121 | -0.02% | [-0.16%, +0.09%] |
| text-ipv6-canonical (--stats) | 112.104 | 112.135 | +0.02% | [-0.09%, +0.18%] |
| text-mixed-noncanonical (no stats) | 77.809 | 77.799 | -0.02% | [-0.29%, +0.27%] |
| text-mixed-noncanonical (--stats) | 77.809 | 77.807 | -0.11% | [-0.21%, +0.23%] |
| text-mixed-addresses (no stats) | 77.754 | 77.697 | -0.02% | [-0.21%, +0.04%] |
| text-mixed-addresses (--stats) | 80.590 | 80.629 | +0.08% | [-0.16%, +0.27%] |
| text-mixed-ranges (no stats) | 77.844 | 77.871 | +0.02% | [-0.09%, +0.20%] |
| text-mixed-ranges (--stats) | 81.949 | 82.066 | +0.18% | [-0.36%, +0.26%] |
| text-mixed-overlap (no stats) | 68.121 | 68.131 | -0.05% | [-0.16%, +0.17%] |
| text-mixed-overlap (--stats) | 68.150 | 68.143 | +0.03% | [-0.26%, +0.19%] |
| searchbot-canonical (no stats) | 180.824 | 180.852 | +0.02% | [-0.14%, +0.16%] |
| searchbot-canonical (--stats) | 180.848 | 180.895 | +0.01% | [-0.04%, +0.14%] |
| searchbot-noncanonical (no stats) | 191.379 | 191.371 | -0.01% | [-0.10%, +0.06%] |
| searchbot-noncanonical (--stats) | 191.320 | 191.422 | +0.05% | [-0.00%, +0.08%] |

Configurations with at least one elapsed/RSS pair above +5% in this run: `text-ipv4-canonical-stats`, `text-ipv6-canonical-stats`, `text-mixed-ranges-stats`, `text-mixed-overlap-stats`, `searchbot-canonical-stats`.

## Separate follow-up

60 measured samples; 10 excluded warmups; 5 configurations.
Evidence: `x86_64/followup-measurements/summary.json` and corresponding sample JSON files.

### Elapsed time

| Configuration | B median (ms) | C median (ms) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (--stats) | 830.312 | 785.268 | -5.08% | [-12.16%, +6.76%] |
| text-ipv6-canonical (--stats) | 1596.955 | 1602.655 | +2.94% | [-8.77%, +6.52%] |
| text-mixed-ranges (--stats) | 15325.776 | 15271.935 | -0.47% | [-4.29%, +1.56%] |
| text-mixed-overlap (--stats) | 1412.544 | 1453.042 | +1.67% | [-2.80%, +6.21%] |
| searchbot-canonical (--stats) | 8010.593 | 8087.516 | +2.14% | [-0.91%, +4.77%] |

### CPU time

| Configuration | B median (s) | C median (s) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (--stats) | 0.8271 | 0.7823 | -5.06% | [-12.15%, +6.74%] |
| text-ipv6-canonical (--stats) | 1.5936 | 1.5992 | +2.96% | [-8.79%, +6.52%] |
| text-mixed-ranges (--stats) | 15.3162 | 15.2628 | -0.47% | [-4.30%, +1.57%] |
| text-mixed-overlap (--stats) | 1.4096 | 1.4496 | +1.62% | [-2.82%, +6.25%] |
| searchbot-canonical (--stats) | 8.0041 | 8.0813 | +2.14% | [-0.90%, +4.77%] |

### Peak resident memory

| Configuration | B median (MiB) | C median (MiB) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (--stats) | 46.586 | 46.715 | +0.21% | [-0.04%, +0.61%] |
| text-ipv6-canonical (--stats) | 112.037 | 112.059 | +0.02% | [-0.05%, +0.17%] |
| text-mixed-ranges (--stats) | 82.080 | 81.988 | -0.10% | [-0.45%, -0.02%] |
| text-mixed-overlap (--stats) | 68.080 | 68.123 | +0.05% | [-0.14%, +0.14%] |
| searchbot-canonical (--stats) | 180.852 | 180.889 | +0.02% | [-0.04%, +0.07%] |

Configurations with at least one elapsed/RSS pair above +5% in this run: `text-ipv4-canonical-stats`, `text-ipv6-canonical-stats`, `text-mixed-overlap-stats`.

Only JSON measurement records were read to produce these tables. This summary is not a replacement for the independent source, binary, fixture and complete-output audit.
