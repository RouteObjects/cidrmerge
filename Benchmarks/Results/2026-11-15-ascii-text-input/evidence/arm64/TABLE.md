# arm64 matched benchmark

Six paired rounds per case. Negative change favors C. CPU/RSS are child-process measurements; warmups are excluded.

| Suite / case | B elapsed s | C elapsed s | B CPU s | C CPU s | B RSS MiB | C RSS MiB | Paired elapsed % median [min, max] | Paired CPU % median [min, max] | Paired RSS % median [min, max] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 1.990870 | 0.331834 | 1.990699 | 0.331666 | 42.744 | 42.223 | -83.26 [-83.48, -82.50] | -83.27 [-83.48, -82.51] | -1.17 [-1.34, -1.06] |
| split / ipv6-disjoint | 2.620365 | 0.552179 | 2.620140 | 0.552006 | 111.430 | 110.900 | -78.86 [-80.77, -68.81] | -78.86 [-80.77, -68.81] | -0.47 [-0.48, -0.43] |
| split / mixed-disjoint | 2.307711 | 0.435522 | 2.307351 | 0.434337 | 65.697 | 65.170 | -81.17 [-81.46, -80.22] | -81.24 [-81.48, -80.23] | -0.80 [-0.86, -0.77] |
| split / mixed-permuted | 2.433764 | 0.529219 | 2.433390 | 0.528876 | 73.084 | 72.547 | -78.32 [-79.08, -76.64] | -78.33 [-79.09, -76.65] | -0.73 [-0.77, -0.65] |
| split / mixed-overlap | 2.253857 | 0.411706 | 2.252928 | 0.411363 | 57.826 | 57.289 | -81.58 [-83.20, -78.20] | -81.59 [-83.21, -78.21] | -0.93 [-0.96, -0.86] |
| split / mixed-adjacent | 2.144296 | 0.319313 | 2.143898 | 0.318972 | 50.441 | 49.918 | -85.11 [-85.65, -83.88] | -85.12 [-85.67, -83.92] | -1.03 [-1.09, -0.94] |
| split / bgp-like-ipv4 | 2.185972 | 0.413338 | 2.185778 | 0.413177 | 40.270 | 39.730 | -81.15 [-81.21, -80.41] | -81.16 [-81.22, -80.41] | -1.26 [-1.56, -1.14] |
| split / range-derived-mixed | 2.353254 | 0.446720 | 2.352907 | 0.446368 | 65.580 | 65.051 | -80.94 [-81.21, -80.26] | -80.94 [-81.23, -80.32] | -0.80 [-0.84, -0.72] |
| native / mixed-disjoint | 2.295913 | 0.435062 | 2.295751 | 0.434900 | 77.129 | 76.619 | -80.87 [-81.59, -80.49] | -80.87 [-81.60, -80.50] | -0.68 [-0.73, -0.63] |
| native / mixed-permuted | 2.385147 | 0.529110 | 2.384955 | 0.528960 | 84.613 | 84.117 | -77.63 [-78.70, -77.35] | -77.63 [-78.70, -77.35] | -0.59 [-0.63, -0.55] |
| native / mixed-overlap | 2.190705 | 0.401245 | 2.187721 | 0.401085 | 67.453 | 66.955 | -81.78 [-83.64, -80.95] | -81.79 [-83.64, -80.82] | -0.71 [-0.80, -0.24] |

All 66 individual elapsed/RSS pairs screened at >+5%; triggers: 0.

Display values are rounded only in this table. JSON retains full floating-point scalars and every pair. Full min/max spread is not a confidence interval.
