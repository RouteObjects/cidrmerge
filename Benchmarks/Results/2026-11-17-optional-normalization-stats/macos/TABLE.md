# macOS: optional normalization accounting

B is the frozen baseline; C is candidate C2. Negative percentage changes favor C.
Elapsed time covers the complete invocation; CPU is user plus system time. RSS is reported in MiB (2^20 bytes).
Each change is the median of six paired percentage changes. Brackets show the observed minimum and maximum, not a confidence interval.
Primary runs and follow-ups remain separate; no observations are pooled or discarded.

## Primary

192 measured samples; 32 excluded warmups; 16 configurations.
Evidence: `macos/primary/summary.json` and corresponding sample JSON files.

### Elapsed time

| Configuration | B median (ms) | C median (ms) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 219.638 | 198.701 | -9.34% | [-11.34%, -7.90%] |
| text-ipv4-canonical (--stats) | 219.973 | 220.202 | -0.27% | [-1.07%, +1.26%] |
| text-ipv6-canonical (no stats) | 404.920 | 336.527 | -16.99% | [-24.21%, -16.17%] |
| text-ipv6-canonical (--stats) | 409.511 | 408.679 | +0.51% | [-0.83%, +1.23%] |
| text-mixed-noncanonical (no stats) | 396.468 | 350.631 | -11.88% | [-15.73%, -10.84%] |
| text-mixed-noncanonical (--stats) | 396.973 | 399.071 | +0.54% | [-5.78%, +2.07%] |
| text-mixed-addresses (no stats) | 384.066 | 339.169 | -11.63% | [-12.38%, -9.94%] |
| text-mixed-addresses (--stats) | 388.085 | 386.418 | +0.15% | [-3.62%, +4.27%] |
| text-mixed-ranges (no stats) | 3053.542 | 2929.611 | -3.84% | [-4.54%, -2.57%] |
| text-mixed-ranges (--stats) | 3044.791 | 3077.173 | +0.90% | [-0.55%, +1.24%] |
| text-mixed-overlap (no stats) | 349.728 | 300.063 | -13.92% | [-14.73%, -13.66%] |
| text-mixed-overlap (--stats) | 350.582 | 350.587 | -0.03% | [-4.37%, +0.63%] |
| searchbot-canonical (no stats) | 1675.200 | 1632.516 | -2.20% | [-5.80%, +1.09%] |
| searchbot-canonical (--stats) | 1665.762 | 1680.098 | +0.42% | [-2.54%, +1.61%] |
| searchbot-noncanonical (no stats) | 1680.374 | 1654.938 | -1.50% | [-3.34%, -0.79%] |
| searchbot-noncanonical (--stats) | 1686.557 | 1697.890 | +0.99% | [-0.15%, +1.99%] |

### CPU time

| Configuration | B median (s) | C median (s) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 0.2000 | 0.1800 | -9.76% | [-15.00%, -5.00%] |
| text-ipv4-canonical (--stats) | 0.2050 | 0.2050 | +0.00% | [-5.00%, +0.00%] |
| text-ipv6-canonical (no stats) | 0.3800 | 0.3150 | -18.42% | [-20.51%, -15.79%] |
| text-ipv6-canonical (--stats) | 0.3900 | 0.3900 | +0.00% | [-2.50%, +2.56%] |
| text-mixed-noncanonical (no stats) | 0.3750 | 0.3300 | -11.98% | [-13.16%, -10.81%] |
| text-mixed-noncanonical (--stats) | 0.3800 | 0.3800 | +0.00% | [-2.63%, +2.70%] |
| text-mixed-addresses (no stats) | 0.3600 | 0.3200 | -11.11% | [-11.11%, -11.11%] |
| text-mixed-addresses (--stats) | 0.3650 | 0.3600 | +0.00% | [-2.70%, +2.70%] |
| text-mixed-ranges (no stats) | 3.0250 | 2.9050 | -3.84% | [-4.62%, -3.32%] |
| text-mixed-ranges (--stats) | 3.0200 | 3.0400 | +0.33% | [+0.00%, +0.99%] |
| text-mixed-overlap (no stats) | 0.3350 | 0.2800 | -15.39% | [-17.65%, -12.50%] |
| text-mixed-overlap (--stats) | 0.3400 | 0.3350 | +0.00% | [-3.03%, +0.00%] |
| searchbot-canonical (no stats) | 1.6400 | 1.6100 | -1.83% | [-4.24%, -0.61%] |
| searchbot-canonical (--stats) | 1.6400 | 1.6500 | +0.30% | [-1.20%, +1.22%] |
| searchbot-noncanonical (no stats) | 1.6650 | 1.6250 | -1.82% | [-3.55%, -1.20%] |
| searchbot-noncanonical (--stats) | 1.6600 | 1.6750 | +0.90% | [+0.00%, +1.81%] |

### Peak resident memory

| Configuration | B median (MiB) | C median (MiB) | Paired median change | Paired change range |
|---|---:|---:|---:|---:|
| text-ipv4-canonical (no stats) | 56.172 | 56.156 | -0.01% | [-0.14%, +1.27%] |
| text-ipv4-canonical (--stats) | 57.305 | 57.273 | -0.05% | [-0.57%, +0.14%] |
| text-ipv6-canonical (no stats) | 146.781 | 146.766 | -0.01% | [-0.07%, +0.01%] |
| text-ipv6-canonical (--stats) | 147.930 | 147.922 | -0.01% | [-0.02%, +0.01%] |
| text-mixed-noncanonical (no stats) | 102.859 | 103.047 | -0.37% | [-0.87%, +0.46%] |
| text-mixed-noncanonical (--stats) | 103.578 | 103.688 | +0.11% | [-1.17%, +0.74%] |
| text-mixed-addresses (no stats) | 114.805 | 114.938 | +0.21% | [-0.65%, +1.05%] |
| text-mixed-addresses (--stats) | 115.219 | 115.141 | +0.01% | [-0.92%, +1.04%] |
| text-mixed-ranges (no stats) | 115.656 | 116.008 | +0.44% | [-0.32%, +0.99%] |
| text-mixed-ranges (--stats) | 117.016 | 117.578 | +0.58% | [-0.48%, +1.28%] |
| text-mixed-overlap (no stats) | 66.844 | 66.656 | -0.43% | [-1.71%, +1.12%] |
| text-mixed-overlap (--stats) | 68.203 | 68.156 | -0.16% | [-1.91%, +3.37%] |
| searchbot-canonical (no stats) | 268.281 | 268.773 | +0.01% | [-0.76%, +0.38%] |
| searchbot-canonical (--stats) | 269.875 | 269.406 | +0.10% | [-0.36%, +0.72%] |
| searchbot-noncanonical (no stats) | 289.320 | 289.797 | +0.00% | [-0.86%, +1.03%] |
| searchbot-noncanonical (--stats) | 290.414 | 290.438 | +0.01% | [-1.01%, +0.35%] |

Only JSON measurement records were read to produce these tables. This summary is not a replacement for the independent source, binary, fixture and complete-output audit.
