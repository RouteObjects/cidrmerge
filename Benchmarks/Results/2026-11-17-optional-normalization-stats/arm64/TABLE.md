# ARM64 Linux (OrbStack): optional normalization accounting

B is the frozen baseline; C is candidate C2. Negative percentage changes favor C.
Elapsed time covers the complete invocation; CPU is user plus system time. RSS is reported in MiB (2^20 bytes).
Each change is the median of six paired percentage changes. Brackets show the observed minimum and maximum, not a confidence interval.
Primary runs and follow-ups remain separate; no observations are pooled or discarded.

## Primary

192 measured samples; 32 excluded warmups; 16 configurations.
Evidence: `arm64/primary/summary.json` and corresponding sample JSON files.

### Elapsed time

| Configuration | B median (ms) | C median (ms) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 286.319 | 248.075 | -12.64% | [-48.14%, -10.91%] |
| text-ipv4-canonical (--stats) | 286.528 | 286.576 | +0.29% | [-2.10%, +1.77%] |
| text-ipv6-canonical (no stats) | 460.468 | 370.024 | -18.70% | [-20.70%, -17.50%] |
| text-ipv6-canonical (--stats) | 461.423 | 457.698 | -0.18% | [-39.19%, +2.32%] |
| text-mixed-noncanonical (no stats) | 467.337 | 386.997 | -16.53% | [-24.91%, -12.99%] |
| text-mixed-noncanonical (--stats) | 462.950 | 451.490 | -1.98% | [-2.61%, +0.06%] |
| text-mixed-addresses (no stats) | 442.112 | 374.649 | -14.98% | [-17.96%, -13.21%] |
| text-mixed-addresses (--stats) | 442.636 | 444.147 | +1.54% | [-2.84%, +5.98%] |
| text-mixed-ranges (no stats) | 3386.841 | 3203.895 | -5.74% | [-6.48%, +3.88%] |
| text-mixed-ranges (--stats) | 3389.030 | 3388.617 | -0.44% | [-1.42%, +1.59%] |
| text-mixed-overlap (no stats) | 386.770 | 321.455 | -16.93% | [-18.87%, -12.16%] |
| text-mixed-overlap (--stats) | 389.101 | 391.588 | -0.23% | [-3.10%, +8.07%] |
| searchbot-canonical (no stats) | 1910.615 | 1854.146 | -1.32% | [-6.34%, +4.18%] |
| searchbot-canonical (--stats) | 1879.094 | 1889.781 | -0.07% | [-4.02%, +7.94%] |
| searchbot-noncanonical (no stats) | 1875.819 | 1869.543 | +0.70% | [-4.43%, +1.89%] |
| searchbot-noncanonical (--stats) | 1905.330 | 1930.077 | +0.02% | [-2.00%, +9.96%] |

### CPU time

| Configuration | B median (s) | C median (s) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 0.2861 | 0.2478 | -12.70% | [-48.14%, -10.93%] |
| text-ipv4-canonical (--stats) | 0.2863 | 0.2864 | +0.31% | [-2.10%, +1.78%] |
| text-ipv6-canonical (no stats) | 0.4602 | 0.3699 | -18.71% | [-20.68%, -17.49%] |
| text-ipv6-canonical (--stats) | 0.4612 | 0.4575 | -0.19% | [-39.19%, +2.33%] |
| text-mixed-noncanonical (no stats) | 0.4671 | 0.3868 | -16.54% | [-24.92%, -13.34%] |
| text-mixed-noncanonical (--stats) | 0.4627 | 0.4513 | -2.17% | [-2.60%, +0.07%] |
| text-mixed-addresses (no stats) | 0.4419 | 0.3744 | -14.99% | [-17.96%, -13.24%] |
| text-mixed-addresses (--stats) | 0.4418 | 0.4440 | +1.56% | [-1.98%, +5.44%] |
| text-mixed-ranges (no stats) | 3.3864 | 3.2011 | -5.70% | [-6.48%, +3.87%] |
| text-mixed-ranges (--stats) | 3.3837 | 3.3881 | -0.45% | [-1.43%, +1.67%] |
| text-mixed-overlap (no stats) | 0.3866 | 0.3212 | -16.94% | [-18.89%, -12.17%] |
| text-mixed-overlap (--stats) | 0.3889 | 0.3905 | -0.23% | [-3.55%, +8.07%] |
| searchbot-canonical (no stats) | 1.9091 | 1.8533 | -1.32% | [-6.35%, +4.31%] |
| searchbot-canonical (--stats) | 1.8789 | 1.8891 | -0.09% | [-4.01%, +7.94%] |
| searchbot-noncanonical (no stats) | 1.8754 | 1.8693 | +0.70% | [-4.39%, +1.89%] |
| searchbot-noncanonical (--stats) | 1.9041 | 1.9291 | +0.04% | [-1.92%, +10.08%] |

### Peak resident memory

| Configuration | B median (MiB) | C median (MiB) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 43.496 | 43.359 | -0.30% | [-0.71%, +0.48%] |
| text-ipv4-canonical (--stats) | 48.301 | 48.436 | +0.39% | [-0.67%, +0.66%] |
| text-ipv6-canonical (no stats) | 112.195 | 112.184 | -0.00% | [-0.07%, +0.10%] |
| text-ipv6-canonical (--stats) | 112.156 | 112.033 | -0.16% | [-0.33%, +0.36%] |
| text-mixed-noncanonical (no stats) | 77.914 | 77.768 | -0.12% | [-0.48%, +0.14%] |
| text-mixed-noncanonical (--stats) | 78.016 | 77.861 | -0.19% | [-0.31%, -0.07%] |
| text-mixed-addresses (no stats) | 77.830 | 77.871 | +0.09% | [-0.39%, +0.64%] |
| text-mixed-addresses (--stats) | 82.256 | 82.340 | +0.07% | [-0.34%, +0.18%] |
| text-mixed-ranges (no stats) | 78.057 | 78.014 | -0.03% | [-0.42%, +0.15%] |
| text-mixed-ranges (--stats) | 83.592 | 83.602 | +0.04% | [-0.27%, +0.56%] |
| text-mixed-overlap (no stats) | 68.199 | 68.229 | +0.00% | [-0.45%, +0.72%] |
| text-mixed-overlap (--stats) | 68.248 | 68.223 | -0.03% | [-0.22%, +0.45%] |
| searchbot-canonical (no stats) | 180.986 | 181.115 | +0.06% | [-0.03%, +0.18%] |
| searchbot-canonical (--stats) | 181.135 | 181.148 | +0.01% | [-0.28%, +0.08%] |
| searchbot-noncanonical (no stats) | 191.627 | 191.469 | -0.03% | [-0.23%, +0.12%] |
| searchbot-noncanonical (--stats) | 191.701 | 191.697 | +0.02% | [-0.24%, +0.13%] |

Configurations with at least one elapsed/RSS pair above +5% in this run: `text-mixed-addresses-stats`, `text-mixed-overlap-stats`, `searchbot-canonical-stats`, `searchbot-noncanonical-stats`.

## Separate follow-up

48 measured samples; 8 excluded warmups; 4 configurations.
Evidence: `arm64/followup-01/summary.json` and corresponding sample JSON files.

### Elapsed time

| Configuration | B median (ms) | C median (ms) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-mixed-addresses (--stats) | 439.593 | 446.465 | +2.17% | [-0.66%, +4.24%] |
| text-mixed-overlap (--stats) | 382.111 | 386.604 | +2.53% | [-1.62%, +5.97%] |
| searchbot-canonical (--stats) | 1888.946 | 1896.820 | +0.31% | [-1.68%, +6.08%] |
| searchbot-noncanonical (--stats) | 1886.910 | 1907.409 | +1.68% | [-1.30%, +10.49%] |

### CPU time

| Configuration | B median (s) | C median (s) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-mixed-addresses (--stats) | 0.4394 | 0.4463 | +2.16% | [-0.67%, +4.24%] |
| text-mixed-overlap (--stats) | 0.3819 | 0.3863 | +2.23% | [-1.60%, +5.97%] |
| searchbot-canonical (--stats) | 1.8887 | 1.8966 | +0.30% | [-1.67%, +6.09%] |
| searchbot-noncanonical (--stats) | 1.8867 | 1.9072 | +1.65% | [-1.09%, +10.49%] |

### Peak resident memory

| Configuration | B median (MiB) | C median (MiB) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-mixed-addresses (--stats) | 82.439 | 82.297 | +0.06% | [-0.40%, +0.33%] |
| text-mixed-overlap (--stats) | 68.156 | 68.260 | +0.23% | [-0.13%, +0.58%] |
| searchbot-canonical (--stats) | 181.049 | 181.164 | +0.05% | [-0.12%, +0.16%] |
| searchbot-noncanonical (--stats) | 191.613 | 191.754 | +0.02% | [-0.17%, +0.21%] |

Configurations with at least one elapsed/RSS pair above +5% in this run: `text-mixed-overlap-stats`, `searchbot-canonical-stats`, `searchbot-noncanonical-stats`.

Only JSON measurement records were read to produce these tables. This summary is not a replacement for the independent source, binary, fixture and complete-output audit.
