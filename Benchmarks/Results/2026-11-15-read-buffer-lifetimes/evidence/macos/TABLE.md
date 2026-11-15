# macos matched benchmark

Six paired rounds per case. Negative change favors C. CPU/RSS are child-process measurements; warmups are excluded.

| Suite / case | B elapsed s | C elapsed s | B CPU s | C CPU s | B RSS MiB | C RSS MiB | Paired elapsed % median [min, max] | Paired CPU % median [min, max] | Paired RSS % median [min, max] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| split / ipv4-disjoint | 0.245653 | 0.236208 | 0.230000 | 0.220000 | 70.188 | 56.148 | -3.04 [-4.81, -1.35] | -4.35 [-4.55, 0.00] | -19.99 [-20.12, -19.88] |
| split / ipv6-disjoint | 0.460979 | 0.457906 | 0.440000 | 0.440000 | 167.062 | 146.820 | -0.35 [-1.80, 0.89] | 0.00 [-2.27, 2.27] | -12.12 [-12.13, -12.10] |
| split / mixed-disjoint | 0.359149 | 0.354302 | 0.320000 | 0.325000 | 86.844 | 76.992 | -0.89 [-3.70, -0.00] | 0.00 [-3.03, 3.12] | -11.34 [-11.64, -11.34] |
| split / mixed-permuted | 0.449074 | 0.448128 | 0.420000 | 0.415000 | 86.859 | 76.992 | -0.42 [-2.04, 0.86] | -1.19 [-2.38, 2.44] | -11.36 [-11.44, -11.32] |
| split / mixed-overlap | 0.355887 | 0.352981 | 0.320000 | 0.320000 | 71.188 | 61.781 | -0.34 [-1.68, 0.45] | 0.00 [0.00, 3.23] | -13.22 [-13.32, -13.19] |
| split / mixed-adjacent | 0.281075 | 0.274615 | 0.240000 | 0.240000 | 71.484 | 61.758 | -2.48 [-11.62, -0.20] | 0.00 [-7.69, 0.00] | -13.62 [-13.68, -13.60] |
| split / bgp-like-ipv4 | 0.362354 | 0.356555 | 0.345000 | 0.340000 | 50.977 | 35.891 | -1.44 [-3.37, 0.43] | -1.43 [-2.86, 0.00] | -29.61 [-29.68, -29.46] |
| split / range-derived-mixed | 0.396347 | 0.369132 | 0.340000 | 0.330000 | 94.922 | 84.656 | -3.48 [-7.65, -0.26] | -2.94 [-2.94, 0.00] | -10.82 [-10.88, -10.77] |
| native / mixed-disjoint | 0.358641 | 0.353833 | 0.340000 | 0.335000 | 118.766 | 101.797 | -1.39 [-2.75, 0.07] | -1.43 [-2.94, 0.00] | -14.29 [-14.33, -13.05] |
| native / mixed-permuted | 0.448625 | 0.443411 | 0.430000 | 0.430000 | 118.773 | 101.758 | -1.58 [-2.08, -0.44] | -1.14 [-2.33, 0.00] | -14.33 [-15.16, -14.29] |
| native / mixed-overlap | 0.353021 | 0.348321 | 0.340000 | 0.335000 | 82.109 | 65.656 | -1.42 [-2.68, 0.46] | -1.47 [-2.94, 0.00] | -20.03 [-20.04, -18.59] |

All 66 individual elapsed/RSS pairs screened at >+5%; triggers: 0.

Display values are rounded only in this table. JSON retains full floating-point scalars and every pair. Full min/max spread is not a confidence interval.
