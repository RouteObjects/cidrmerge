# arm64 matched benchmark

Six paired rounds per case. Negative change favors C. CPU/RSS are child-process measurements; warmups are excluded.

| Suite / case | B elapsed s | C elapsed s | B CPU s | C CPU s | B RSS MiB | C RSS MiB | Paired elapsed % median [min, max] | Paired CPU % median [min, max] | Paired RSS % median [min, max] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.323222 | 0.324322 | 0.322506 | 0.324136 | 42.215 | 42.229 | 0.53 [-1.08, 5.34] | 0.53 [-1.08, 5.71] | 0.04 [-0.02, 0.34] |
| split / ipv6-disjoint | 0.509540 | 0.511151 | 0.509381 | 0.511001 | 110.896 | 110.916 | -0.07 [-1.62, 2.55] | -0.07 [-1.61, 2.55] | 0.02 [0.00, 0.06] |
| split / mixed-disjoint | 0.420854 | 0.421569 | 0.420556 | 0.421278 | 65.168 | 65.168 | 0.41 [-2.72, 2.10] | 0.41 [-2.72, 2.10] | 0.00 [-0.05, 0.14] |
| split / mixed-permuted | 0.516318 | 0.516193 | 0.515972 | 0.515716 | 72.541 | 72.551 | -0.16 [-4.25, 12.76] | -0.16 [-4.22, 12.77] | 0.02 [-0.02, 0.11] |
| split / mixed-overlap | 0.379014 | 0.380234 | 0.378713 | 0.379945 | 57.291 | 57.291 | 0.28 [-2.58, 2.05] | 0.29 [-2.58, 2.06] | -0.01 [-0.07, 0.14] |
| split / mixed-adjacent | 0.306602 | 0.305632 | 0.306304 | 0.305324 | 49.910 | 49.949 | -0.55 [-1.75, 1.33] | -0.52 [-1.75, 1.32] | 0.01 [-0.08, 0.15] |
| split / bgp-like-ipv4 | 0.403258 | 0.406354 | 0.403084 | 0.406179 | 39.744 | 39.734 | 0.01 [-0.58, 2.29] | 0.15 [-0.56, 2.31] | 0.04 [-0.14, 0.14] |
| split / range-derived-mixed | 0.425814 | 0.425612 | 0.425515 | 0.425316 | 65.045 | 65.057 | 0.45 [-0.85, 3.35] | 0.46 [-0.84, 3.35] | 0.02 [-0.01, 0.08] |
| native / mixed-disjoint | 0.424142 | 0.424827 | 0.423500 | 0.424638 | 76.596 | 76.596 | -0.40 [-3.92, 2.98] | -0.30 [-3.92, 2.98] | -0.01 [-0.04, 0.09] |
| native / mixed-permuted | 0.517610 | 0.515790 | 0.517446 | 0.515115 | 84.057 | 84.096 | -0.84 [-1.06, 5.09] | -0.85 [-1.21, 5.09] | 0.05 [0.02, 0.11] |
| native / mixed-overlap | 0.391856 | 0.382924 | 0.391695 | 0.382739 | 66.924 | 66.984 | -2.12 [-4.50, 0.13] | -2.12 [-4.50, 0.14] | 0.10 [0.00, 0.15] |

All 66 individual elapsed/RSS pairs screened at >+5%; triggers: 3.

Display values are rounded only in this table. JSON retains full floating-point scalars and every pair. Full min/max spread is not a confidence interval.
