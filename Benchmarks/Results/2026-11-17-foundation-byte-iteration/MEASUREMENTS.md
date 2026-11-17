# Complete matched measurements

All values compare ordinary Release P with the frozen baseline B. Negative paired change means lower elapsed time, CPU time, or peak RSS. Brackets show the full observed minimum and maximum, not confidence intervals. Absolute medians and paired percentage medians are different statistics; no phase is pooled and no observation is excluded.

Each file/stdin row has six pairs; each startup row has twenty. Warmups are excluded. `Valid change pairs` can be smaller only when a zero baseline CPU observation makes a percentage undefined. All absolute CPU observations remain included. Audit receipt paths in the CSVs are relative to the preserved experiment root.

## macOS ARM64

### Million-entry file input

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.202789 [0.200939, 0.204385] | 0.158789 [0.157633, 0.165031] | -21.72% [-22.81%, -18.58%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.221747 [0.219222, 0.287535] | 0.177002 [0.174484, 0.185235] | -20.22% [-35.58%, -18.40%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.347286 [0.342254, 0.401350] | 0.287627 [0.283385, 0.289274] | -17.21% [-29.39%, -16.14%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.413765 [0.410954, 0.438868] | 0.360687 [0.356427, 0.367397] | -13.03% [-18.05%, -10.95%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.352767 [0.351315, 0.358003] | 0.277657 [0.273802, 0.298957] | -21.34% [-22.51%, -15.48%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.400996 [0.398174, 0.409440] | 0.321822 [0.318363, 0.327014] | -19.62% [-21.55%, -18.76%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 0.367290 [0.341335, 0.576771] | 0.272234 [0.265341, 0.274594] | -26.31% [-52.69%, -20.66%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 0.395191 [0.386206, 0.635399] | 0.320778 [0.316706, 0.555725] | -18.49% [-28.93%, -12.54%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 3.018614 [2.938449, 3.473468] | 2.822889 [2.810313, 2.905430] | -6.68% [-17.21%, -1.12%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 3.094159 [3.066805, 3.155704] | 3.003293 [2.957489, 3.087496] | -3.60% [-4.24%, +0.67%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 0.306248 [0.301634, 0.309586] | 0.255433 [0.249336, 0.292554] | -16.15% [-18.96%, -4.03%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 0.354099 [0.352761, 0.359717] | 0.307581 [0.299352, 0.350910] | -13.67% [-15.52%, -0.96%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 1.715773 [1.657356, 1.754178] | 1.666199 [1.653621, 1.729304] | -1.43% [-5.06%, +1.33%] | 6 |
| searchbot-canonical-stats / primary | 6 | 1.718307 [1.701294, 1.795243] | 1.718660 [1.703891, 1.765448] | +0.05% [-2.73%, +1.89%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 1.694959 [1.662087, 1.753750] | 1.697828 [1.670745, 1.753004] | +0.53% [-4.68%, +2.12%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 1.720381 [1.706622, 1.750197] | 1.721814 [1.710133, 1.844393] | +0.28% [-1.42%, +5.38%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 1.720431 [1.706497, 1.764903] | 1.733482 [1.710714, 1.837206] | +0.29% [-1.96%, +6.91%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.190000 [0.190000, 0.190000] | 0.140000 [0.130000, 0.140000] | -26.32% [-31.58%, -26.32%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.210000 [0.210000, 0.220000] | 0.160000 [0.160000, 0.160000] | -23.81% [-27.27%, -23.81%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.330000 [0.330000, 0.340000] | 0.270000 [0.260000, 0.270000] | -18.18% [-23.53%, -18.18%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.400000 [0.390000, 0.400000] | 0.340000 [0.340000, 0.350000] | -15.00% [-15.00%, -12.50%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.330000 [0.330000, 0.340000] | 0.255000 [0.250000, 0.270000] | -23.89% [-24.24%, -18.18%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.380000 [0.370000, 0.390000] | 0.300000 [0.300000, 0.310000] | -21.05% [-23.08%, -18.42%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 0.330000 [0.320000, 0.350000] | 0.255000 [0.250000, 0.260000] | -23.06% [-26.47%, -18.75%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 0.380000 [0.370000, 0.410000] | 0.305000 [0.290000, 0.330000] | -19.22% [-23.68%, -18.42%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 2.930000 [2.910000, 2.990000] | 2.785000 [2.770000, 2.820000] | -5.13% [-6.02%, -3.09%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 3.050000 [3.030000, 3.070000] | 2.935000 [2.920000, 2.940000] | -3.93% [-4.26%, -3.61%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 0.290000 [0.290000, 0.290000] | 0.240000 [0.230000, 0.240000] | -17.24% [-20.69%, -17.24%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 0.340000 [0.340000, 0.340000] | 0.290000 [0.290000, 0.300000] | -14.71% [-14.71%, -11.76%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 1.640000 [1.630000, 1.680000] | 1.640000 [1.630000, 1.650000] | +0.00% [-2.38%, +1.23%] | 6 |
| searchbot-canonical-stats / primary | 6 | 1.690000 [1.670000, 1.720000] | 1.685000 [1.670000, 1.700000] | -0.30% [-1.74%, +0.59%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 1.660000 [1.640000, 1.680000] | 1.650000 [1.640000, 1.670000] | -0.60% [-1.80%, +1.22%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 1.695000 [1.680000, 1.710000] | 1.690000 [1.680000, 1.720000] | +0.29% [-1.18%, +0.60%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 1.690000 [1.680000, 1.710000] | 1.695000 [1.680000, 1.730000] | +0.30% [-1.17%, +2.37%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 55.977 [55.500, 56.188] | 56.195 [55.531, 56.234] | +0.41% [-1.17%, +1.27%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 57.281 [57.000, 57.438] | 57.359 [57.047, 57.391] | +0.12% [-0.41%, +0.69%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 146.805 [146.781, 146.859] | 146.812 [146.812, 146.828] | +0.01% [-0.03%, +0.03%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 147.938 [147.922, 148.016] | 147.992 [147.969, 148.047] | +0.04% [-0.02%, +0.07%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 102.758 [101.812, 103.016] | 102.453 [102.188, 103.031] | +0.05% [-0.74%, +0.37%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 104.086 [103.531, 104.281] | 104.359 [103.016, 105.281] | +0.48% [-1.04%, +0.96%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 114.797 [114.172, 115.922] | 114.328 [113.609, 115.859] | -0.36% [-1.07%, +0.45%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 116.133 [114.547, 116.938] | 115.344 [114.766, 117.000] | -0.48% [-1.52%, +0.87%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 116.203 [116.125, 116.531] | 115.500 [115.047, 117.375] | -0.70% [-1.01%, +1.04%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 117.023 [116.391, 118.234] | 116.586 [116.234, 117.359] | -0.26% [-1.63%, +0.32%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 66.273 [65.641, 67.266] | 67.383 [66.562, 67.766] | +1.75% [-0.53%, +2.95%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 68.125 [67.156, 68.344] | 68.422 [67.672, 68.469] | +0.39% [-0.89%, +1.95%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 269.312 [268.281, 271.250] | 268.305 [268.297, 269.328] | -0.19% [-1.08%, +0.20%] | 6 |
| searchbot-canonical-stats / primary | 6 | 270.383 [269.891, 271.891] | 270.250 [269.453, 271.484] | -0.13% [-0.23%, +0.03%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 291.359 [289.344, 292.281] | 290.281 [289.297, 292.125] | -0.06% [-0.88%, +0.33%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 291.141 [290.406, 293.359] | 291.297 [290.469, 292.500] | +0.02% [-0.75%, +0.39%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 290.664 [289.953, 291.938] | 292.500 [290.484, 293.438] | +0.54% [-0.32%, +0.86%] | 6 |

### Million-entry redirected text stdin

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.202303 [0.199614, 0.208195] | 0.157428 [0.156112, 0.164004] | -22.09% [-23.18%, -21.21%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.400067 [0.394651, 0.437292] | 0.323333 [0.320459, 0.325831] | -19.44% [-25.65%, -18.34%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.190000 [0.180000, 0.190000] | 0.140000 [0.140000, 0.140000] | -26.32% [-26.32%, -22.22%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.375000 [0.370000, 0.390000] | 0.300000 [0.300000, 0.300000] | -19.99% [-23.08%, -18.92%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 56.172 [55.469, 56.188] | 56.055 [55.891, 56.234] | -0.22% [-0.53%, +1.35%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 103.836 [102.875, 105.000] | 104.445 [104.188, 105.266] | +0.71% [-0.77%, +1.58%] | 6 |

### Warm-cache fresh-process startup

**Elapsed time (ms)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 13.020 [11.767, 17.244] | 13.083 [11.808, 16.001] | +1.86% [-26.48%, +34.78%] | 20 |
| empty-stdin / followup | 20 | 12.743 [11.880, 14.290] | 12.629 [11.461, 14.761] | +0.58% [-16.90%, +14.71%] | 20 |
| version / primary | 20 | 12.837 [11.956, 17.804] | 12.615 [11.089, 14.880] | -3.27% [-17.21%, +16.83%] | 20 |
| version / followup | 20 | 12.830 [11.713, 14.440] | 12.778 [11.512, 14.846] | +0.80% [-8.31%, +13.51%] | 20 |
| mixed-100 / primary | 20 | 12.823 [11.960, 16.678] | 12.521 [11.814, 15.482] | -1.63% [-24.67%, +11.30%] | 20 |
| mixed-100 / followup | 20 | 12.805 [11.882, 17.895] | 12.836 [11.855, 16.217] | -1.09% [-15.24%, +31.01%] | 20 |
| mixed-10000 / primary | 20 | 15.409 [14.453, 42.448] | 14.881 [14.244, 28.350] | -2.67% [-33.21%, +17.72%] | 20 |
| mixed-10000 / followup | 20 | 15.555 [14.463, 37.217] | 15.065 [14.364, 27.288] | -3.90% [-26.68%, +12.34%] | 20 |

**CPU time (ms)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| empty-stdin / followup | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| version / primary | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| version / followup | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| mixed-100 / primary | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| mixed-100 / followup | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| mixed-10000 / primary | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |
| mixed-10000 / followup | 20 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | n/a | 0 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 6.688 [6.656, 6.719] | 6.672 [6.641, 6.703] | -0.23% [-0.93%, +0.70%] | 20 |
| empty-stdin / followup | 20 | 6.688 [6.656, 6.719] | 6.672 [6.656, 6.703] | +0.00% [-0.93%, +0.70%] | 20 |
| version / primary | 20 | 6.547 [6.516, 6.562] | 6.562 [6.531, 6.594] | +0.24% [-0.48%, +0.96%] | 20 |
| version / followup | 20 | 6.547 [6.516, 6.562] | 6.562 [6.531, 6.594] | +0.36% [-0.24%, +0.96%] | 20 |
| mixed-100 / primary | 20 | 6.812 [6.781, 6.844] | 6.859 [6.812, 6.875] | +0.46% [-0.23%, +1.15%] | 20 |
| mixed-100 / followup | 20 | 6.812 [6.797, 6.844] | 6.844 [6.812, 6.875] | +0.34% [-0.23%, +1.15%] | 20 |
| mixed-10000 / primary | 20 | 7.742 [7.688, 7.953] | 7.781 [7.750, 8.047] | +0.61% [-2.36%, +4.25%] | 20 |
| mixed-10000 / followup | 20 | 7.750 [7.719, 7.969] | 7.797 [7.750, 7.969] | +0.40% [-2.36%, +3.24%] | 20 |

## Linux ARM64

### Million-entry file input

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.259992 [0.255206, 0.307744] | 0.208293 [0.203459, 0.238361] | -21.16% [-29.54%, -8.02%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.301605 [0.294486, 0.354692] | 0.248560 [0.241912, 0.289871] | -17.90% [-26.52%, -16.57%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.407639 [0.385137, 0.475724] | 0.324026 [0.318872, 0.363706] | -19.73% [-32.16%, -7.54%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.471868 [0.463527, 0.603033] | 0.415445 [0.407382, 0.488155] | -11.99% [-31.04%, +3.74%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.396376 [0.391851, 0.451966] | 0.317078 [0.315535, 0.328822] | -19.85% [-28.36%, -17.35%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.469623 [0.464088, 0.527146] | 0.388896 [0.383643, 0.400095] | -17.22% [-26.16%, -13.79%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 0.390924 [0.382274, 0.489917] | 0.320389 [0.313217, 0.419337] | -18.11% [-34.64%, +8.52%] | 6 |
| text-mixed-addresses-no-stats / followup | 6 | 0.391321 [0.385566, 0.426600] | 0.315222 [0.314605, 0.408610] | -18.67% [-26.04%, +4.63%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 0.461900 [0.459402, 0.486457] | 0.390037 [0.380417, 0.415097] | -15.71% [-19.41%, -10.78%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 3.283642 [3.264619, 3.309230] | 3.237412 [3.151755, 3.331182] | -1.44% [-3.55%, +0.90%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 3.589992 [3.543927, 3.675827] | 3.425654 [3.376467, 3.528374] | -4.08% [-6.95%, -2.58%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 0.332204 [0.329008, 0.350341] | 0.274209 [0.269305, 0.305853] | -17.65% [-18.39%, -12.70%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 0.399172 [0.392046, 0.400354] | 0.346565 [0.344378, 0.358214] | -13.19% [-13.56%, -8.63%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 1.904335 [1.828188, 2.134779] | 1.939729 [1.833064, 2.953068] | +3.82% [-3.98%, +38.33%] | 6 |
| searchbot-canonical-no-stats / followup | 6 | 1.933336 [1.902587, 1.968696] | 1.977708 [1.836836, 2.168399] | +2.01% [-4.35%, +12.40%] | 6 |
| searchbot-canonical-stats / primary | 6 | 2.054060 [2.010495, 2.333026] | 2.011538 [1.943032, 2.405812] | -2.26% [-14.10%, +16.14%] | 6 |
| searchbot-canonical-stats / followup | 6 | 1.993798 [1.941045, 2.102437] | 1.986936 [1.960260, 2.450838] | -0.88% [-5.34%, +22.32%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 1.906181 [1.859634, 2.034860] | 2.021014 [1.867312, 2.220902] | +4.31% [-2.83%, +15.68%] | 6 |
| searchbot-noncanonical-no-stats / followup | 6 | 1.953193 [1.912280, 2.175967] | 2.031272 [1.811988, 2.097294] | -1.58% [-7.66%, +8.43%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 1.994905 [1.941274, 2.234153] | 2.025452 [1.925722, 2.121393] | -1.41% [-10.48%, +9.28%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 2.002222 [1.946832, 2.040135] | 2.018081 [1.935048, 2.114039] | +1.46% [-3.62%, +5.88%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.259702 [0.255040, 0.307530] | 0.208117 [0.203278, 0.238129] | -21.16% [-30.14%, -8.01%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.301389 [0.294323, 0.354528] | 0.248356 [0.241747, 0.289700] | -17.91% [-26.52%, -16.56%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.407458 [0.384943, 0.475543] | 0.323246 [0.318634, 0.363418] | -19.91% [-32.17%, -7.58%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.471677 [0.463334, 0.602853] | 0.415232 [0.407224, 0.485911] | -11.99% [-31.05%, +3.31%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.396203 [0.391692, 0.451722] | 0.316893 [0.315303, 0.328651] | -19.87% [-28.36%, -17.35%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.469440 [0.463919, 0.526448] | 0.388716 [0.383467, 0.399941] | -17.22% [-26.10%, -13.79%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 0.390665 [0.382069, 0.474152] | 0.320205 [0.313007, 0.418085] | -18.14% [-32.50%, +8.25%] | 6 |
| text-mixed-addresses-no-stats / followup | 6 | 0.391100 [0.385394, 0.426385] | 0.315034 [0.314378, 0.408447] | -18.69% [-26.05%, +4.63%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 0.461682 [0.459226, 0.486203] | 0.389830 [0.380250, 0.414755] | -15.70% [-19.40%, -10.81%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 3.282513 [3.264116, 3.309047] | 3.235050 [3.151478, 3.330693] | -1.45% [-3.54%, +1.08%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 3.589250 [3.543325, 3.675150] | 3.424729 [3.374254, 3.525266] | -4.07% [-6.97%, -2.63%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 0.332043 [0.328806, 0.350139] | 0.274034 [0.269070, 0.305682] | -17.67% [-18.41%, -12.70%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 0.398990 [0.391714, 0.400180] | 0.346388 [0.344185, 0.358039] | -13.19% [-13.56%, -8.60%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 1.903131 [1.827822, 2.134565] | 1.939133 [1.832810, 2.948814] | +3.83% [-3.88%, +38.15%] | 6 |
| searchbot-canonical-no-stats / followup | 6 | 1.933031 [1.902323, 1.968411] | 1.976806 [1.836629, 2.168217] | +1.97% [-4.41%, +12.40%] | 6 |
| searchbot-canonical-stats / primary | 6 | 2.053799 [2.009517, 2.332825] | 2.011309 [1.942793, 2.405635] | -2.24% [-14.11%, +16.24%] | 6 |
| searchbot-canonical-stats / followup | 6 | 1.993495 [1.940810, 2.102266] | 1.986219 [1.959976, 2.450566] | -0.88% [-5.39%, +22.33%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 1.905945 [1.859438, 2.033395] | 2.020084 [1.867130, 2.220711] | +4.33% [-2.77%, +15.68%] | 6 |
| searchbot-noncanonical-no-stats / followup | 6 | 1.952811 [1.911782, 2.175253] | 2.031033 [1.811670, 2.097130] | -1.57% [-7.64%, +8.43%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 1.994648 [1.940983, 2.233826] | 2.025234 [1.925559, 2.120750] | -1.40% [-10.47%, +9.26%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 2.001997 [1.946569, 2.039874] | 2.017498 [1.934885, 2.113694] | +1.46% [-3.62%, +5.88%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 42.219 [42.160, 42.250] | 42.232 [42.215, 42.316] | +0.07% [-0.06%, +0.24%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 45.279 [45.211, 45.297] | 45.293 [45.277, 45.309] | +0.05% [-0.03%, +0.15%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 110.912 [110.906, 110.922] | 110.916 [110.914, 110.930] | +0.00% [-0.01%, +0.02%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 110.912 [110.871, 110.922] | 110.906 [110.895, 110.922] | -0.00% [-0.01%, +0.02%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 76.615 [76.586, 76.652] | 76.648 [76.523, 76.656] | +0.04% [-0.16%, +0.08%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 76.646 [76.586, 76.656] | 76.652 [76.586, 76.664] | +0.00% [-0.08%, +0.10%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 76.521 [76.207, 76.594] | 76.578 [76.566, 76.594] | +0.07% [+0.00%, +0.48%] | 6 |
| text-mixed-addresses-no-stats / followup | 6 | 76.580 [76.527, 76.602] | 76.590 [76.570, 76.609] | +0.01% [-0.01%, +0.08%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 79.270 [79.258, 79.289] | 79.268 [79.254, 79.273] | -0.00% [-0.04%, +0.02%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 76.596 [76.457, 76.645] | 76.594 [76.590, 76.602] | +0.00% [-0.07%, +0.18%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 80.529 [80.520, 80.574] | 80.531 [80.441, 80.543] | -0.02% [-0.11%, +0.01%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 66.947 [66.891, 66.965] | 66.945 [66.934, 66.961] | -0.01% [-0.03%, +0.11%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 66.945 [66.895, 66.957] | 66.947 [66.875, 66.957] | -0.01% [-0.03%, +0.02%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 179.609 [179.598, 179.613] | 179.604 [179.598, 179.625] | +0.00% [-0.01%, +0.01%] | 6 |
| searchbot-canonical-no-stats / followup | 6 | 179.600 [179.527, 179.613] | 179.609 [179.543, 179.684] | +0.02% [-0.03%, +0.05%] | 6 |
| searchbot-canonical-stats / primary | 6 | 179.615 [179.496, 179.617] | 179.613 [179.602, 179.676] | +0.00% [-0.01%, +0.08%] | 6 |
| searchbot-canonical-stats / followup | 6 | 179.607 [179.578, 179.688] | 179.617 [179.590, 179.668] | -0.00% [-0.04%, +0.05%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 190.133 [190.000, 190.141] | 190.135 [190.133, 190.141] | +0.00% [+0.00%, +0.07%] | 6 |
| searchbot-noncanonical-no-stats / followup | 6 | 190.139 [190.129, 190.203] | 190.135 [190.113, 190.188] | -0.01% [-0.01%, +0.01%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 190.141 [190.125, 190.152] | 190.139 [190.129, 190.176] | -0.00% [-0.01%, +0.03%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 190.125 [190.043, 190.191] | 190.139 [190.043, 190.148] | +0.01% [-0.05%, +0.05%] | 6 |

### Million-entry redirected text stdin

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.257444 [0.254245, 0.263389] | 0.208430 [0.203405, 0.243659] | -19.43% [-20.71%, -5.69%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.473949 [0.459061, 0.481296] | 0.391104 [0.384104, 0.403406] | -17.47% [-20.19%, -14.14%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.257200 [0.254078, 0.263198] | 0.208231 [0.203224, 0.243440] | -19.42% [-20.68%, -5.71%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.473747 [0.458883, 0.481142] | 0.390928 [0.383854, 0.401229] | -17.47% [-20.22%, -14.58%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 41.723 [41.672, 41.742] | 41.727 [41.715, 41.738] | +0.02% [-0.06%, +0.16%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 76.135 [76.098, 76.148] | 76.133 [76.070, 76.148] | -0.01% [-0.09%, +0.06%] | 6 |

### Warm-cache fresh-process startup

**Elapsed time (ms)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 5.287 [4.985, 23.576] | 5.348 [4.791, 18.490] | -0.54% [-32.31%, +13.56%] | 20 |
| empty-stdin / followup | 20 | 5.302 [4.698, 5.888] | 5.247 [4.959, 6.197] | +1.83% [-9.58%, +10.17%] | 20 |
| version / primary | 20 | 5.437 [4.749, 15.513] | 5.233 [4.748, 7.920] | -4.76% [-54.41%, +54.32%] | 20 |
| version / followup | 20 | 5.215 [4.552, 5.844] | 5.228 [4.626, 6.193] | +0.91% [-15.48%, +23.75%] | 20 |
| mixed-100 / primary | 20 | 5.875 [5.123, 6.449] | 5.662 [5.124, 6.536] | -2.26% [-14.65%, +22.31%] | 20 |
| mixed-100 / followup | 20 | 5.754 [5.072, 29.015] | 5.805 [4.961, 7.014] | -1.23% [-81.32%, +19.40%] | 20 |
| mixed-10000 / primary | 20 | 9.104 [8.738, 28.757] | 8.449 [7.745, 40.744] | -6.47% [-16.62%, +305.62%] | 20 |
| mixed-10000 / followup | 20 | 9.090 [8.548, 28.459] | 8.579 [7.873, 9.992] | -6.99% [-69.75%, +5.43%] | 20 |

**CPU time (ms)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 5.154 [4.866, 22.244] | 5.134 [4.688, 18.305] | -1.42% [-31.72%, +13.48%] | 20 |
| empty-stdin / followup | 20 | 5.151 [4.586, 5.711] | 5.116 [4.842, 6.031] | +1.77% [-9.23%, +10.28%] | 20 |
| version / primary | 20 | 5.294 [4.629, 15.342] | 5.107 [4.560, 7.750] | -4.70% [-55.05%, +54.81%] | 20 |
| version / followup | 20 | 5.071 [4.451, 5.704] | 5.057 [4.518, 6.046] | +0.80% [-15.84%, +23.41%] | 20 |
| mixed-100 / primary | 20 | 5.730 [5.008, 6.308] | 5.529 [5.008, 6.389] | -2.09% [-14.89%, +21.95%] | 20 |
| mixed-100 / followup | 20 | 5.611 [4.972, 28.871] | 5.663 [4.866, 6.830] | -1.69% [-81.66%, +19.32%] | 20 |
| mixed-10000 / primary | 20 | 8.934 [8.584, 28.526] | 8.261 [7.603, 40.454] | -6.61% [-15.44%, +310.58%] | 20 |
| mixed-10000 / followup | 20 | 8.934 [8.424, 26.244] | 8.376 [7.737, 9.841] | -6.86% [-69.09%, +5.62%] | 20 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 19.195 [19.180, 19.320] | 19.197 [19.176, 19.312] | -0.01% [-0.67%, +0.61%] | 20 |
| empty-stdin / followup | 20 | 19.201 [19.176, 19.324] | 19.199 [19.191, 19.328] | -0.01% [-0.63%, +0.67%] | 20 |
| version / primary | 20 | 18.625 [18.613, 18.641] | 18.629 [18.504, 18.645] | +0.01% [-0.67%, +0.15%] | 20 |
| version / followup | 20 | 18.633 [18.508, 18.645] | 18.629 [18.516, 18.645] | -0.02% [-0.13%, +0.63%] | 20 |
| mixed-100 / primary | 20 | 19.754 [19.633, 19.766] | 19.750 [19.625, 19.770] | +0.00% [-0.65%, +0.68%] | 20 |
| mixed-100 / followup | 20 | 19.754 [19.629, 19.770] | 19.750 [19.629, 19.766] | -0.02% [-0.67%, +0.60%] | 20 |
| mixed-10000 / primary | 20 | 20.312 [20.203, 20.332] | 20.312 [20.188, 20.324] | -0.01% [-0.67%, +0.58%] | 20 |
| mixed-10000 / followup | 20 | 20.312 [20.188, 20.332] | 20.314 [20.188, 20.328] | +0.01% [-0.63%, +0.62%] | 20 |

## Linux x86-64

### Million-entry file input

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.683670 [0.665858, 0.717987] | 0.590540 [0.588997, 0.607177] | -13.54% [-17.76%, -8.81%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.802155 [0.783986, 1.237685] | 0.685247 [0.681045, 0.748150] | -13.77% [-44.66%, -6.87%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 1.294097 [1.210392, 1.848155] | 1.146160 [1.084456, 1.172991] | -13.74% [-38.05%, -3.35%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 1.605850 [1.574835, 1.654179] | 1.457153 [1.410893, 1.506640] | -10.00% [-14.71%, -4.33%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 1.232853 [1.217201, 1.301254] | 1.031521 [1.016890, 1.478890] | -15.33% [-21.85%, +14.24%] | 6 |
| text-mixed-noncanonical-no-stats / followup | 6 | 1.219085 [1.215275, 1.308957] | 1.029026 [1.020670, 1.051348] | -15.79% [-19.68%, -13.71%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.554513 [1.496994, 2.233709] | 1.321519 [1.293628, 1.385660] | -14.21% [-42.09%, -8.40%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 1.150392 [1.121838, 1.216637] | 0.970917 [0.956386, 1.057888] | -14.99% [-20.46%, -5.70%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 1.408552 [1.389654, 1.471555] | 1.240134 [1.226584, 1.300775] | -12.61% [-12.99%, -8.43%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 14.285999 [13.918046, 14.599699] | 13.902192 [13.648062, 14.241040] | -1.83% [-5.09%, -0.45%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 15.317468 [15.174762, 15.481622] | 15.244099 [14.720331, 26.155055] | -0.56% [-3.69%, +70.82%] | 6 |
| text-mixed-ranges-stats / followup | 6 | 15.780407 [15.199077, 16.166480] | 14.949172 [14.801260, 15.129750] | -4.78% [-6.41%, -2.31%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 1.175366 [1.137621, 1.210228] | 1.039179 [1.031423, 1.044618] | -11.45% [-14.77%, -8.18%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 1.426523 [1.393813, 1.489624] | 1.294103 [1.279885, 1.327461] | -9.03% [-13.41%, -5.07%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 7.490287 [7.361159, 10.491270] | 7.389521 [7.332013, 7.586101] | -0.73% [-29.77%, +2.44%] | 6 |
| searchbot-canonical-stats / primary | 6 | 7.887072 [7.843907, 7.951887] | 7.955472 [7.811143, 9.238444] | +0.72% [-0.60%, +17.05%] | 6 |
| searchbot-canonical-stats / followup | 6 | 8.110868 [7.802355, 8.408716] | 7.996941 [7.813201, 8.167805] | -0.54% [-6.58%, +3.36%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 7.641455 [7.503655, 11.827743] | 7.579694 [7.449197, 7.746059] | -1.65% [-34.51%, +2.14%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 8.050593 [7.943759, 8.559660] | 8.165748 [8.047283, 9.444096] | +1.74% [-2.72%, +10.33%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 8.095098 [7.796561, 8.309624] | 8.045249 [7.809666, 8.379833] | +1.72% [-6.02%, +3.06%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.680416 [0.663229, 0.714939] | 0.587638 [0.585949, 0.604089] | -13.57% [-17.80%, -8.92%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.799080 [0.781044, 1.235601] | 0.682785 [0.678091, 0.745660] | -13.83% [-44.71%, -6.81%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 1.291044 [1.206862, 1.846198] | 1.143876 [1.081360, 1.170017] | -13.77% [-38.07%, -3.32%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 1.602667 [1.571556, 1.650880] | 1.454770 [1.407599, 1.503129] | -10.01% [-14.74%, -4.35%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 1.229742 [1.214365, 1.297898] | 1.028647 [1.013704, 1.476881] | -15.36% [-21.90%, +14.22%] | 6 |
| text-mixed-noncanonical-no-stats / followup | 6 | 1.216025 [1.212238, 1.305706] | 1.025894 [1.017259, 1.048433] | -15.83% [-19.70%, -13.76%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.551120 [1.493833, 2.231471] | 1.318396 [1.291854, 1.382213] | -14.26% [-42.11%, -8.39%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 1.147395 [1.118486, 1.213230] | 0.968050 [0.954832, 1.054914] | -15.03% [-20.46%, -5.68%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 1.405183 [1.386565, 1.468489] | 1.237582 [1.223273, 1.297781] | -12.65% [-13.00%, -8.44%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 14.276630 [13.910045, 14.596416] | 13.893759 [13.639165, 14.232590] | -1.83% [-5.09%, -0.45%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 15.309974 [15.165352, 15.472526] | 15.236000 [14.711374, 26.147156] | -0.55% [-3.70%, +70.83%] | 6 |
| text-mixed-ranges-stats / followup | 6 | 15.770394 [15.189614, 16.155927] | 14.940646 [14.791184, 15.119929] | -4.78% [-6.41%, -2.31%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 1.172244 [1.134893, 1.206955] | 1.036176 [1.028423, 1.041573] | -11.45% [-14.79%, -8.22%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 1.423468 [1.390772, 1.483686] | 1.290953 [1.276670, 1.324366] | -9.05% [-13.27%, -5.07%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 7.484618 [7.355131, 10.485383] | 7.383685 [7.326585, 7.581544] | -0.73% [-29.76%, +2.45%] | 6 |
| searchbot-canonical-stats / primary | 6 | 7.882630 [7.838602, 7.945559] | 7.949562 [7.804731, 9.234401] | +0.72% [-0.60%, +17.04%] | 6 |
| searchbot-canonical-stats / followup | 6 | 8.104658 [7.796455, 8.402361] | 7.990669 [7.807169, 8.162031] | -0.54% [-6.59%, +3.36%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 7.635199 [7.497807, 11.823437] | 7.574244 [7.443653, 7.743388] | -1.65% [-34.51%, +2.14%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 8.043847 [7.937874, 8.557098] | 8.159679 [8.041441, 9.440741] | +1.74% [-2.72%, +10.33%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 8.088770 [7.790613, 8.303584] | 8.039320 [7.803411, 8.373418] | +1.73% [-6.02%, +3.06%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 43.408 [43.262, 43.602] | 43.398 [43.105, 43.547] | +0.09% [-1.14%, +0.66%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 46.613 [46.555, 46.723] | 46.658 [46.527, 46.836] | +0.04% [-0.23%, +0.55%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 112.035 [111.953, 112.238] | 112.094 [111.988, 112.254] | +0.07% [-0.19%, +0.27%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 112.021 [111.918, 112.207] | 112.057 [111.922, 112.145] | +0.03% [-0.25%, +0.13%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 77.822 [77.648, 77.965] | 77.834 [77.629, 77.848] | +0.01% [-0.42%, +0.25%] | 6 |
| text-mixed-noncanonical-no-stats / followup | 6 | 77.787 [77.621, 77.926] | 77.848 [77.777, 77.922] | +0.08% [-0.13%, +0.32%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 77.666 [77.605, 77.867] | 77.814 [77.773, 77.965] | +0.18% [-0.11%, +0.42%] | 6 |
| text-mixed-addresses-no-stats / primary | 6 | 77.773 [77.668, 77.875] | 77.738 [77.688, 77.840] | +0.01% [-0.16%, +0.13%] | 6 |
| text-mixed-addresses-stats / primary | 6 | 80.625 [80.434, 80.645] | 80.561 [80.418, 80.660] | -0.08% [-0.13%, +0.17%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 77.840 [77.672, 77.977] | 77.834 [77.699, 77.961] | -0.04% [-0.18%, +0.22%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 82.025 [81.871, 82.098] | 82.041 [81.859, 82.105] | +0.02% [-0.25%, +0.29%] | 6 |
| text-mixed-ranges-stats / followup | 6 | 81.998 [81.859, 82.172] | 81.943 [81.840, 82.062] | -0.11% [-0.24%, +0.11%] | 6 |
| text-mixed-overlap-no-stats / primary | 6 | 68.098 [68.012, 68.211] | 68.092 [67.801, 68.176] | -0.02% [-0.46%, +0.20%] | 6 |
| text-mixed-overlap-stats / primary | 6 | 68.088 [67.922, 68.215] | 68.186 [68.098, 68.332] | +0.17% [-0.05%, +0.29%] | 6 |
| searchbot-canonical-no-stats / primary | 6 | 180.791 [180.738, 180.980] | 180.848 [180.684, 180.969] | +0.00% [-0.09%, +0.10%] | 6 |
| searchbot-canonical-stats / primary | 6 | 180.771 [180.734, 180.875] | 180.889 [180.691, 180.957] | +0.07% [-0.04%, +0.10%] | 6 |
| searchbot-canonical-stats / followup | 6 | 180.871 [180.633, 180.914] | 180.805 [180.730, 180.965] | -0.01% [-0.06%, +0.05%] | 6 |
| searchbot-noncanonical-no-stats / primary | 6 | 191.396 [191.371, 191.508] | 191.377 [191.145, 191.391] | -0.03% [-0.13%, +0.01%] | 6 |
| searchbot-noncanonical-stats / primary | 6 | 191.424 [191.305, 191.531] | 191.398 [191.305, 191.543] | -0.00% [-0.07%, +0.04%] | 6 |
| searchbot-noncanonical-stats / followup | 6 | 191.350 [191.176, 191.477] | 191.328 [191.258, 191.434] | -0.00% [-0.06%, +0.07%] | 6 |

### Million-entry redirected text stdin

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.690883 [0.669490, 0.718692] | 0.597401 [0.587255, 0.614448] | -12.87% [-17.95%, -8.80%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.515799 [1.498515, 1.558541] | 1.321637 [1.302155, 1.394136] | -12.57% [-16.45%, -9.61%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.687813 [0.666890, 0.715833] | 0.594521 [0.584286, 0.611423] | -12.91% [-18.02%, -8.84%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.512516 [1.495687, 1.555231] | 1.318421 [1.298729, 1.390775] | -12.61% [-16.49%, -9.62%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 42.949 [42.855, 43.027] | 42.947 [42.852, 43.023] | +0.03% [-0.23%, +0.15%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 77.270 [77.172, 77.434] | 77.400 [77.266, 77.508] | +0.14% [-0.05%, +0.28%] | 6 |

### Warm-cache fresh-process startup

**Elapsed time (ms)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 19.194 [18.277, 19.775] | 19.057 [18.272, 20.107] | -0.28% [-2.89%, +2.26%] | 20 |
| version / primary | 20 | 18.650 [17.751, 20.098] | 18.488 [18.161, 19.494] | -0.25% [-4.65%, +3.59%] | 20 |
| mixed-100 / primary | 20 | 19.780 [19.119, 20.544] | 19.622 [18.892, 20.564] | +0.00% [-4.19%, +3.87%] | 20 |
| mixed-10000 / primary | 20 | 29.215 [28.441, 30.917] | 28.328 [27.307, 29.837] | -4.14% [-7.41%, +0.81%] | 20 |

**CPU time (ms)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 16.880 [16.296, 17.656] | 16.711 [16.234, 17.660] | -0.56% [-4.53%, +3.02%] | 20 |
| version / primary | 20 | 16.439 [15.938, 17.983] | 16.239 [15.940, 17.194] | -0.01% [-4.71%, +1.58%] | 20 |
| mixed-100 / primary | 20 | 17.439 [16.881, 18.144] | 17.417 [16.830, 18.285] | -0.15% [-2.70%, +5.44%] | 20 |
| mixed-10000 / primary | 20 | 26.882 [26.318, 29.123] | 26.044 [25.109, 27.589] | -4.49% [-8.61%, +2.35%] | 20 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| empty-stdin / primary | 20 | 20.523 [20.262, 20.723] | 20.469 [20.148, 20.641] | -0.20% [-2.26%, +0.84%] | 20 |
| version / primary | 20 | 19.855 [19.566, 20.090] | 19.830 [19.586, 20.012] | +0.10% [-1.84%, +1.15%] | 20 |
| mixed-100 / primary | 20 | 21.062 [20.852, 21.180] | 21.072 [20.723, 21.234] | +0.01% [-1.87%, +1.54%] | 20 |
| mixed-10000 / primary | 20 | 21.518 [21.301, 21.660] | 21.557 [21.375, 21.652] | +0.11% [-0.94%, +1.05%] | 20 |

Mac CPU observations have 0.01-second accounting resolution; tiny-call CPU percentages are not interpreted. Linux lifetime peak RSS can include pre-exec Python memory, so equal tiny-call RSS does not prove equal application memory. Startup uses warm caches; it is not a cold-launch result.
