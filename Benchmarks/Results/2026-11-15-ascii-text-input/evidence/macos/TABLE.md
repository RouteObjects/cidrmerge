# macos matched benchmark

Six paired rounds per case. Negative change favors C. CPU/RSS are child-process measurements; warmups are excluded.

| Suite / case | B elapsed s | C elapsed s | B CPU s | C CPU s | B RSS MiB | C RSS MiB | Paired elapsed % median [min, max] | Paired CPU % median [min, max] | Paired RSS % median [min, max] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.598369 | 0.251597 | 0.580000 | 0.240000 | 70.266 | 70.172 | -57.85 [-59.02, -57.57] | -58.62 [-60.34, -58.62] | -0.11 [-0.29, 0.85] |
| split / ipv6-disjoint | 0.926228 | 0.460224 | 0.900000 | 0.440000 | 167.109 | 167.070 | -49.97 [-52.31, -48.83] | -51.11 [-52.17, -50.55] | -0.02 [-0.06, 0.17] |
| split / mixed-disjoint | 0.769838 | 0.366166 | 0.730000 | 0.330000 | 86.875 | 86.844 | -52.38 [-52.95, -50.76] | -54.79 [-55.41, -54.17] | -0.02 [-0.09, 0.25] |
| split / mixed-permuted | 0.858848 | 0.460873 | 0.825000 | 0.420000 | 86.906 | 86.836 | -46.15 [-46.72, -44.45] | -48.78 [-49.40, -48.19] | -0.05 [-0.11, 0.29] |
| split / mixed-overlap | 0.759216 | 0.363803 | 0.720000 | 0.320000 | 71.266 | 71.164 | -52.09 [-52.80, -51.39] | -55.24 [-56.16, -54.17] | -0.12 [-0.18, 0.84] |
| split / mixed-adjacent | 0.685922 | 0.284935 | 0.645000 | 0.240000 | 71.508 | 71.453 | -58.56 [-59.41, -57.08] | -62.50 [-63.64, -60.61] | -0.05 [-0.13, 0.33] |
| split / bgp-like-ipv4 | 0.741897 | 0.368072 | 0.725000 | 0.350000 | 50.875 | 50.984 | -50.33 [-51.14, -49.54] | -51.72 [-53.42, -50.68] | 0.84 [-0.15, 2.79] |
| split / range-derived-mixed | 0.787457 | 0.375090 | 0.750000 | 0.340000 | 94.984 | 94.906 | -52.37 [-54.21, -52.11] | -54.67 [-54.67, -54.05] | -0.07 [-0.12, 0.00] |
| native / mixed-disjoint | 0.769588 | 0.360037 | 0.750000 | 0.340000 | 119.422 | 120.016 | -53.18 [-53.40, -52.20] | -54.36 [-54.67, -53.95] | 0.15 [-0.58, 1.30] |
| native / mixed-permuted | 0.870425 | 0.461111 | 0.850000 | 0.430000 | 119.852 | 120.117 | -47.31 [-48.24, -45.64] | -48.24 [-50.00, -48.19] | 0.39 [-0.44, 1.07] |
| native / mixed-overlap | 0.764898 | 0.357469 | 0.740000 | 0.340000 | 83.477 | 83.578 | -53.24 [-55.32, -52.38] | -54.05 [-55.84, -54.05] | 0.05 [-0.86, 1.18] |

All 66 individual elapsed/RSS pairs screened at >+5%; triggers: 0.

Display values are rounded only in this table. JSON retains full floating-point scalars and every pair. Full min/max spread is not a confidence interval.
