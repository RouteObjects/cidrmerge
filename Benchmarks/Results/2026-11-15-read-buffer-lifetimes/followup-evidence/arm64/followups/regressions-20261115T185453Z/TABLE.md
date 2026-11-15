# arm64 separate follow-up

Six new measured pairs per selected case and one excluded warmup per configuration. Results remain separate from the primary run.

| Suite / case | B elapsed s | C elapsed s | Paired elapsed % median [min, max] | Paired RSS % median [min, max] |
|---|---:|---:|---:|---:|
| native / mixed-permuted | 0.521892 | 0.514354 | -0.67 [-4.18, 4.27] | 0.01 [0.00, 0.07] |
| split / ipv4-disjoint | 0.318217 | 0.318437 | 0.53 [-1.14, 8.33] | -0.03 [-0.08, 0.10] |
| split / mixed-permuted | 0.502600 | 0.505673 | 1.20 [-1.99, 4.64] | -0.01 [-0.12, 0.08] |

Retained 36 measured samples and 6 excluded warmups; 18 pairs. Individual >+5% elapsed/RSS triggers in this follow-up: 2.

JSON retains all unrounded scalar values and pairs. Min/max describes observed spread, not a confidence interval. Follow-up timing is not pooled with primary timing.
