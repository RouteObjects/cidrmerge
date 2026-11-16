# x86_64 paired results

Negative changes favor the candidate. Each row is six pairs; changes are medians of paired percentages. CPU/RSS come from native resources. Timing spreads retain every observation.

## measurements

144 measured samples; 24 excluded warmups.

| Configuration | B median s | C median s | Elapsed change | Pair spread | CPU change | RSS change |
|---|---:|---:|---:|---:|---:|---:|
| ipv4-disjoint-ranges | 1.0593 | 0.8088 | -23.56% | -30.57…-16.74% | -23.60% | +0.03% |
| ipv4-disjoint-cidr | 0.7996 | 0.7407 | -6.98% | -8.47…+2.24% | -7.02% | -0.19% |
| ipv6-disjoint-ranges | 2.0352 | 1.6071 | -21.37% | -24.59…-16.42% | -21.39% | -0.01% |
| ipv6-disjoint-cidr | 1.6737 | 1.5308 | -8.01% | -14.93…-0.90% | -8.02% | +0.04% |
| mixed-disjoint-ranges | 1.6719 | 1.2778 | -24.00% | -26.82…-21.23% | -24.03% | -0.06% |
| mixed-disjoint-cidr | 1.2796 | 1.2108 | -4.55% | -6.01…-0.89% | -4.59% | -0.05% |
| mixed-permuted-ranges | 2.1055 | 1.7332 | -18.60% | -21.54…-14.21% | -18.59% | -0.00% |
| mixed-permuted-cidr | 1.7260 | 1.6310 | -4.73% | -7.75…-4.49% | -4.72% | -0.09% |
| mixed-overlap-ranges | 1.3875 | 1.4022 | +2.08% | -3.82…+7.46% | +2.06% | +0.19% |
| mixed-overlap-cidr | 1.3500 | 1.3670 | +2.10% | -0.63…+9.49% | +2.13% | -0.03% |
| range-derived-mixed-ranges | 1.3165 | 1.2034 | -7.99% | -16.43…-5.35% | -8.01% | +0.01% |
| range-derived-mixed-cidr | 1.2912 | 1.2568 | -3.14% | -6.60…+1.12% | -3.13% | -0.04% |

## followup-measurements

24 measured samples; 4 excluded warmups.

| Configuration | B median s | C median s | Elapsed change | Pair spread | CPU change | RSS change |
|---|---:|---:|---:|---:|---:|---:|
| mixed-overlap-ranges | 1.3538 | 1.3754 | +1.74% | -1.42…+5.75% | +1.77% | +0.11% |
| mixed-overlap-cidr | 1.3773 | 1.3793 | +1.90% | -0.77…+3.74% | +1.89% | +0.07% |

