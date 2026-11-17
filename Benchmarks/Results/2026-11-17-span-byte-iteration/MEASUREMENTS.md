# Complete matched measurements

All values compare ordinary Release P with the frozen baseline B. Negative paired change means lower elapsed time, CPU time, or peak RSS. Brackets show the full observed minimum and maximum, not confidence intervals. Absolute medians and paired percentage medians are different statistics; no phase is pooled and no observation is excluded.

Each file/stdin row has six pairs. Warmups are excluded. `Valid change pairs` can be smaller only when a zero baseline CPU observation makes a percentage undefined. All absolute CPU observations remain included. Audit receipt paths in the CSVs are relative to the preserved experiment root.

## macOS ARM64

### Million-entry file input

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.158532 [0.156094, 0.161552] | 0.154590 [0.150703, 0.160374] | -2.83% [-4.42%, -0.36%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.174749 [0.173993, 0.180365] | 0.170008 [0.168690, 0.174988] | -2.91% [-3.37%, -1.47%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.288502 [0.285883, 0.316779] | 0.284660 [0.278873, 0.288443] | -2.24% [-8.95%, -0.49%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.359302 [0.354256, 0.416101] | 0.350970 [0.347243, 0.389695] | -2.05% [-16.55%, +10.00%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 0.359787 [0.353465, 0.400465] | 0.348039 [0.346710, 0.367211] | -3.45% [-12.86%, +3.58%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.276188 [0.272498, 0.311756] | 0.268935 [0.266467, 0.287372] | -2.35% [-14.07%, +4.19%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.324750 [0.319322, 0.325304] | 0.318296 [0.315556, 0.327047] | -1.62% [-2.98%, +0.69%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 2.849011 [2.798804, 2.895808] | 2.811966 [2.785252, 2.854604] | -0.95% [-3.12%, +1.29%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 2.952211 [2.918300, 3.020000] | 2.942694 [2.910329, 3.014765] | +0.27% [-3.14%, +2.93%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.140000 [0.140000, 0.150000] | 0.140000 [0.140000, 0.140000] | +0.00% [-6.67%, +0.00%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.160000 [0.160000, 0.170000] | 0.160000 [0.160000, 0.160000] | +0.00% [-5.88%, +0.00%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.270000 [0.270000, 0.280000] | 0.270000 [0.260000, 0.270000] | -1.79% [-3.70%, +0.00%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.345000 [0.340000, 0.360000] | 0.330000 [0.330000, 0.340000] | -4.33% [-8.33%, +0.00%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 0.340000 [0.340000, 0.350000] | 0.330000 [0.330000, 0.330000] | -2.94% [-5.71%, -2.94%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.250000 [0.250000, 0.270000] | 0.250000 [0.250000, 0.260000] | +0.00% [-7.41%, +4.00%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.300000 [0.300000, 0.310000] | 0.290000 [0.290000, 0.300000] | -3.33% [-6.45%, +0.00%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 2.775000 [2.770000, 2.800000] | 2.770000 [2.750000, 2.790000] | -0.54% [-1.07%, +0.36%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 2.905000 [2.890000, 2.940000] | 2.895000 [2.880000, 2.910000] | -0.17% [-1.70%, +0.00%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 56.242 [55.922, 56.266] | 56.102 [55.469, 56.219] | -0.11% [-1.20%, +0.17%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 57.383 [57.078, 57.422] | 57.375 [57.266, 57.391] | -0.03% [-0.16%, +0.49%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 146.844 [146.156, 146.984] | 146.758 [146.734, 146.797] | -0.06% [-0.17%, +0.43%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 148.031 [147.312, 148.141] | 148.000 [147.984, 148.031] | -0.02% [-0.11%, +0.47%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 148.000 [147.953, 148.016] | 147.992 [147.953, 148.016] | -0.01% [-0.01%, +0.02%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 102.797 [101.906, 104.188] | 103.227 [102.125, 104.141] | +0.00% [-1.06%, +2.15%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 104.547 [103.766, 105.328] | 104.211 [103.359, 104.547] | -0.58% [-1.51%, +0.75%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 116.203 [115.672, 117.188] | 116.047 [115.016, 116.500] | -0.26% [-0.79%, +0.15%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 118.305 [116.797, 118.484] | 117.312 [116.547, 117.609] | -0.72% [-1.54%, -0.04%] | 6 |

### Million-entry redirected text stdin

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.158200 [0.157198, 0.174794] | 0.152281 [0.151397, 0.176300] | -3.64% [-6.39%, +0.86%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.320966 [0.319114, 0.323330] | 0.313962 [0.311518, 0.314846] | -2.51% [-2.71%, -1.39%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.140000 [0.140000, 0.150000] | 0.140000 [0.130000, 0.140000] | -3.33% [-7.14%, +0.00%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.300000 [0.300000, 0.300000] | 0.290000 [0.290000, 0.290000] | -3.33% [-3.33%, -3.33%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 56.203 [55.516, 56.281] | 56.148 [55.484, 56.250] | -0.08% [-1.28%, +1.15%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 104.203 [103.797, 104.547] | 103.688 [102.969, 104.531] | -0.66% [-1.44%, +0.36%] | 6 |

## Linux ARM64

### Million-entry file input

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.206117 [0.204545, 0.207417] | 0.205829 [0.203130, 0.208598] | +0.04% [-2.07%, +1.46%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.246440 [0.243476, 0.292731] | 0.244817 [0.239671, 0.250842] | -0.39% [-16.78%, +2.49%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.325372 [0.318475, 0.338662] | 0.330691 [0.318404, 0.368554] | -0.39% [-5.24%, +14.47%] | 6 |
| text-ipv6-canonical-no-stats / followup | 6 | 0.324132 [0.317405, 0.337074] | 0.322100 [0.315421, 0.326932] | -0.77% [-3.01%, +0.80%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.423664 [0.412291, 0.458293] | 0.421274 [0.407177, 0.444533] | -0.52% [-11.15%, +6.83%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 0.414099 [0.404715, 0.456247] | 0.411372 [0.405880, 0.555965] | -0.12% [-6.56%, +32.16%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.319806 [0.316625, 0.324005] | 0.320537 [0.316632, 0.325814] | +0.20% [-1.17%, +1.32%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.389766 [0.385598, 0.414836] | 0.392170 [0.385471, 0.421994] | +0.13% [-5.14%, +9.22%] | 6 |
| text-mixed-noncanonical-stats / followup | 6 | 0.388088 [0.386295, 0.392910] | 0.395669 [0.381614, 0.405588] | +2.22% [-1.72%, +3.60%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 3.168584 [3.132565, 3.304642] | 3.153801 [3.142590, 3.386588] | +0.04% [-4.75%, +6.59%] | 6 |
| text-mixed-ranges-no-stats / followup | 6 | 3.216187 [3.143419, 3.325172] | 3.165516 [3.127663, 3.371098] | -1.24% [-3.88%, +4.90%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 3.381825 [3.320727, 3.671491] | 3.407353 [3.359259, 3.417668] | +0.84% [-8.50%, +2.64%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.205950 [0.204384, 0.207252] | 0.205660 [0.202894, 0.208413] | +0.04% [-2.10%, +1.46%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.246271 [0.243318, 0.292580] | 0.244638 [0.239513, 0.250672] | -0.40% [-16.79%, +2.46%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 0.325200 [0.318287, 0.338482] | 0.330461 [0.318242, 0.368336] | -0.39% [-5.25%, +14.49%] | 6 |
| text-ipv6-canonical-no-stats / followup | 6 | 0.323937 [0.317207, 0.336879] | 0.321897 [0.315258, 0.326751] | -0.77% [-3.01%, +0.81%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 0.423478 [0.412109, 0.458137] | 0.421084 [0.407020, 0.444281] | -0.52% [-11.16%, +6.81%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 0.413932 [0.404542, 0.456075] | 0.411210 [0.405724, 0.555790] | -0.12% [-7.30%, +32.17%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 0.319590 [0.316437, 0.323835] | 0.320369 [0.316425, 0.325642] | +0.19% [-1.17%, +1.32%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.389544 [0.385422, 0.414483] | 0.391933 [0.385306, 0.421839] | +0.14% [-5.13%, +9.22%] | 6 |
| text-mixed-noncanonical-stats / followup | 6 | 0.387917 [0.386143, 0.391946] | 0.395509 [0.381437, 0.404556] | +2.22% [-1.73%, +3.60%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 3.166613 [3.132331, 3.304329] | 3.151559 [3.141995, 3.386331] | -0.02% [-4.76%, +6.70%] | 6 |
| text-mixed-ranges-no-stats / followup | 6 | 3.216019 [3.143238, 3.324948] | 3.165328 [3.127444, 3.369363] | -1.19% [-3.88%, +4.85%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 3.379616 [3.320536, 3.671268] | 3.405974 [3.359011, 3.416931] | +0.81% [-8.51%, +2.64%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 42.229 [42.215, 42.234] | 42.234 [42.176, 42.238] | +0.00% [-0.11%, +0.06%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 45.285 [45.215, 45.301] | 45.291 [45.273, 45.312] | +0.01% [-0.06%, +0.22%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 110.904 [110.848, 110.914] | 110.895 [110.855, 110.918] | -0.02% [-0.05%, +0.06%] | 6 |
| text-ipv6-canonical-no-stats / followup | 6 | 110.906 [110.836, 110.922] | 110.918 [110.898, 110.930] | +0.01% [-0.01%, +0.08%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 110.896 [110.840, 110.922] | 110.902 [110.895, 110.922] | +0.00% [-0.02%, +0.06%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 110.914 [110.902, 110.922] | 110.850 [110.824, 110.922] | -0.05% [-0.08%, +0.00%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 76.656 [76.578, 76.660] | 76.648 [76.637, 76.656] | -0.01% [-0.02%, +0.10%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 76.645 [76.586, 76.660] | 76.635 [76.578, 76.664] | -0.01% [-0.11%, +0.07%] | 6 |
| text-mixed-noncanonical-stats / followup | 6 | 76.646 [76.598, 76.660] | 76.615 [76.531, 76.660] | -0.04% [-0.15%, +0.08%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 76.586 [76.488, 76.664] | 76.604 [76.570, 76.613] | +0.01% [-0.07%, +0.14%] | 6 |
| text-mixed-ranges-no-stats / followup | 6 | 76.605 [76.582, 76.645] | 76.592 [76.453, 76.668] | -0.01% [-0.20%, +0.11%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 80.529 [80.523, 80.539] | 80.520 [80.461, 80.539] | -0.01% [-0.09%, +0.02%] | 6 |

### Million-entry redirected text stdin

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.205570 [0.203096, 0.210488] | 0.204716 [0.202991, 0.217701] | +0.06% [-1.86%, +3.43%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.387961 [0.381978, 0.426425] | 0.392525 [0.382217, 0.398300] | -0.02% [-8.33%, +3.72%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.205385 [0.202938, 0.210238] | 0.204537 [0.202829, 0.217487] | +0.06% [-1.84%, +3.45%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 0.387774 [0.381774, 0.425653] | 0.392248 [0.382067, 0.398100] | -0.02% [-8.25%, +3.73%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 41.723 [41.660, 41.727] | 41.729 [41.672, 41.738] | +0.03% [-0.01%, +0.07%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 76.123 [75.949, 76.148] | 76.107 [76.070, 76.156] | +0.00% [-0.08%, +0.16%] | 6 |

## Linux x86-64

### Million-entry file input

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.595626 [0.587835, 0.659690] | 0.564965 [0.560952, 0.577316] | -5.12% [-14.94%, -1.87%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.697133 [0.682131, 0.712112] | 0.660481 [0.652308, 0.712743] | -4.48% [-8.29%, +4.49%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 1.103645 [1.088323, 1.172888] | 1.072821 [1.063476, 1.162749] | -2.44% [-8.68%, +5.87%] | 6 |
| text-ipv6-canonical-no-stats / followup | 6 | 1.123176 [1.082375, 1.202815] | 1.074716 [1.055114, 1.097354] | -4.55% [-8.77%, -0.86%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 1.451025 [1.426152, 1.526410] | 1.416050 [1.385420, 1.507135] | -2.78% [-8.09%, +5.06%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 1.444024 [1.425547, 1.477042] | 1.417756 [1.375699, 1.498529] | -1.14% [-5.51%, +2.63%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 1.027838 [1.023521, 1.040223] | 0.999245 [0.995870, 1.029917] | -2.89% [-3.81%, +0.19%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.303620 [1.286238, 1.335599] | 1.258274 [1.239626, 1.341958] | -2.30% [-7.11%, +3.02%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 13.858350 [13.668278, 14.097827] | 13.699923 [13.557440, 13.909508] | -1.50% [-3.12%, +1.33%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 14.926856 [14.752484, 15.097117] | 14.775091 [14.750906, 15.374344] | -0.41% [-1.32%, +1.84%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.592609 [0.584752, 0.656428] | 0.562135 [0.558166, 0.574423] | -5.10% [-14.97%, -1.84%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 0.694079 [0.679226, 0.708945] | 0.657765 [0.649150, 0.709417] | -4.49% [-8.25%, +4.44%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 1.100540 [1.085268, 1.169760] | 1.069636 [1.059846, 1.159355] | -2.50% [-8.71%, +5.87%] | 6 |
| text-ipv6-canonical-no-stats / followup | 6 | 1.120131 [1.078973, 1.199305] | 1.071443 [1.051989, 1.094082] | -4.59% [-8.77%, -0.87%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 1.447573 [1.422626, 1.522939] | 1.412771 [1.381919, 1.503944] | -2.79% [-8.09%, +5.07%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 1.440418 [1.422439, 1.473954] | 1.414022 [1.372080, 1.495349] | -1.15% [-5.53%, +2.66%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 1.024637 [1.020286, 1.037240] | 0.996094 [0.992809, 1.027021] | -2.90% [-3.85%, +0.24%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.300285 [1.282704, 1.332504] | 1.255057 [1.236528, 1.339302] | -2.27% [-7.15%, +3.07%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 13.849598 [13.660084, 14.089459] | 13.691422 [13.548674, 13.900412] | -1.50% [-3.11%, +1.33%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 14.917562 [14.742944, 15.088848] | 14.765988 [14.742556, 15.365251] | -0.40% [-1.32%, +1.83%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 43.459 [43.359, 43.543] | 43.363 [43.332, 43.430] | -0.24% [-0.30%, +0.02%] | 6 |
| text-ipv4-canonical-stats / primary | 6 | 46.678 [46.527, 46.781] | 46.656 [46.574, 46.715] | +0.03% [-0.32%, +0.23%] | 6 |
| text-ipv6-canonical-no-stats / primary | 6 | 112.111 [112.062, 112.258] | 112.135 [112.016, 112.305] | -0.02% [-0.17%, +0.22%] | 6 |
| text-ipv6-canonical-no-stats / followup | 6 | 112.023 [111.961, 112.172] | 112.086 [111.977, 112.156] | +0.00% [-0.08%, +0.17%] | 6 |
| text-ipv6-canonical-stats / primary | 6 | 112.043 [111.926, 112.141] | 112.080 [112.023, 112.203] | +0.04% [-0.06%, +0.15%] | 6 |
| text-ipv6-canonical-stats / followup | 6 | 112.057 [111.953, 112.242] | 112.156 [112.012, 112.227] | +0.03% [-0.05%, +0.24%] | 6 |
| text-mixed-noncanonical-no-stats / primary | 6 | 77.785 [77.754, 77.918] | 77.816 [77.711, 77.953] | +0.03% [-0.10%, +0.20%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 77.762 [77.715, 77.797] | 77.844 [77.742, 77.957] | +0.10% [-0.01%, +0.24%] | 6 |
| text-mixed-ranges-no-stats / primary | 6 | 77.871 [77.844, 78.074] | 77.857 [77.797, 77.941] | -0.01% [-0.36%, +0.11%] | 6 |
| text-mixed-ranges-stats / primary | 6 | 81.994 [81.855, 82.039] | 81.941 [81.820, 81.984] | -0.04% [-0.26%, +0.09%] | 6 |

### Million-entry redirected text stdin

**Elapsed time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.599808 [0.594255, 0.616021] | 0.568521 [0.562909, 0.647311] | -5.26% [-8.47%, +8.78%] | 6 |
| text-ipv4-canonical-no-stats / followup | 6 | 0.591587 [0.589328, 0.598163] | 0.567245 [0.561504, 0.573878] | -4.04% [-5.17%, -2.79%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.308095 [1.274307, 1.371970] | 1.272762 [1.251542, 1.435736] | -1.94% [-8.38%, +10.36%] | 6 |
| text-mixed-noncanonical-stats / followup | 6 | 1.282886 [1.274345, 1.336030] | 1.280241 [1.267087, 1.407303] | +0.18% [-5.16%, +9.57%] | 6 |

**CPU time (s)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 0.596980 [0.591207, 0.612989] | 0.565571 [0.559943, 0.644635] | -5.31% [-8.50%, +8.86%] | 6 |
| text-ipv4-canonical-no-stats / followup | 6 | 0.588508 [0.586500, 0.595227] | 0.564199 [0.558616, 0.570925] | -4.06% [-5.16%, -2.82%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 1.304496 [1.270878, 1.368832] | 1.269425 [1.248042, 1.431987] | -1.92% [-8.40%, +10.37%] | 6 |
| text-mixed-noncanonical-stats / followup | 6 | 1.279427 [1.270930, 1.332887] | 1.276938 [1.263604, 1.403797] | +0.20% [-5.20%, +9.58%] | 6 |

**Peak RSS (MiB)**

| Case / phase | Pairs | B median [min, max] | P median [min, max] | Paired change [min, max] | Valid change pairs |
|---|---:|---:|---:|---:|---:|
| text-ipv4-canonical-no-stats / primary | 6 | 42.904 [42.844, 43.000] | 42.895 [42.832, 43.000] | +0.01% [-0.26%, +0.33%] | 6 |
| text-ipv4-canonical-no-stats / followup | 6 | 42.982 [42.883, 43.027] | 43.018 [42.988, 43.086] | +0.11% [-0.09%, +0.47%] | 6 |
| text-mixed-noncanonical-stats / primary | 6 | 77.354 [77.246, 77.477] | 77.342 [77.277, 77.465] | -0.01% [-0.26%, +0.17%] | 6 |
| text-mixed-noncanonical-stats / followup | 6 | 77.371 [77.324, 77.418] | 77.318 [77.266, 77.516] | -0.11% [-0.17%, +0.25%] | 6 |

Mac CPU observations have 0.01-second accounting resolution. Linux lifetime peak RSS uses wait4; it is an end-to-end process measurement, not a heap allocation count. This focused experiment has no startup or cold-cache timing groups.
