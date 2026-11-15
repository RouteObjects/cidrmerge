# x86_64 matched benchmark

Six paired rounds per case. Negative change favors C. CPU/RSS are child-process measurements; warmups are excluded.

| Suite / case | B elapsed s | C elapsed s | B CPU s | C CPU s | B RSS MiB | C RSS MiB | Paired elapsed % median [min, max] | Paired CPU % median [min, max] | Paired RSS % median [min, max] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.804869 | 0.846323 | 0.801830 | 0.843196 | 43.434 | 43.395 | 2.64 [-0.17, 16.45] | 2.62 [-0.14, 16.51] | -0.09 [-0.65, 0.60] |
| split / ipv6-disjoint | 1.672240 | 1.704706 | 1.668874 | 1.701339 | 112.098 | 112.172 | 0.47 [-2.65, 3.10] | 0.47 [-2.66, 3.08] | 0.06 [-0.30, 0.22] |
| split / mixed-disjoint | 1.252775 | 1.257696 | 1.247206 | 1.251936 | 66.318 | 66.346 | 0.80 [-3.26, 4.60] | 0.79 [-3.25, 4.63] | 0.09 [-0.34, 0.35] |
| split / mixed-permuted | 1.681835 | 1.687854 | 1.676082 | 1.682001 | 73.752 | 73.789 | 0.26 [-1.20, 3.46] | 0.26 [-1.23, 3.48] | 0.06 [-0.20, 0.37] |
| split / mixed-overlap | 1.331496 | 1.338994 | 1.325816 | 1.333631 | 58.553 | 58.436 | -0.41 [-3.24, 3.50] | -0.40 [-3.31, 3.47] | -0.20 [-0.28, -0.12] |
| split / mixed-adjacent | 0.957167 | 0.953111 | 0.952334 | 0.948128 | 51.084 | 51.127 | -0.04 [-1.21, 4.11] | -0.04 [-1.15, 4.15] | 0.10 [-0.36, 0.31] |
| split / bgp-like-ipv4 | 1.160517 | 1.157827 | 1.157455 | 1.154718 | 40.975 | 40.936 | -0.13 [-2.26, 0.68] | -0.14 [-2.25, 0.66] | -0.13 [-0.40, 0.27] |
| split / range-derived-mixed | 1.286520 | 1.285036 | 1.281019 | 1.279478 | 66.289 | 66.229 | -0.25 [-4.52, 2.08] | -0.29 [-4.52, 2.07] | -0.13 [-0.18, 0.07] |
| native / mixed-disjoint | 1.277912 | 1.280434 | 1.274837 | 1.277516 | 77.826 | 77.850 | 0.83 [-1.91, 4.63] | 0.84 [-1.88, 4.62] | -0.03 [-0.16, 0.46] |
| native / mixed-permuted | 1.698077 | 1.703529 | 1.694573 | 1.700099 | 85.248 | 85.305 | 0.92 [-3.87, 4.16] | 0.93 [-3.89, 4.16] | 0.04 [-0.09, 0.32] |
| native / mixed-overlap | 1.382276 | 1.360862 | 1.378576 | 1.357465 | 68.170 | 68.182 | -0.75 [-5.06, 0.75] | -0.76 [-5.04, 0.78] | 0.09 [-0.19, 0.24] |

All 66 individual elapsed/RSS pairs screened at >+5%; triggers: 2.

Display values are rounded only in this table. JSON retains full floating-point scalars and every pair. Full min/max spread is not a confidence interval.
