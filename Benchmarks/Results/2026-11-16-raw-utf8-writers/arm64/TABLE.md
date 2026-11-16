# arm64 paired results

Negative changes favor the candidate. Each row is six pairs; changes are medians of paired percentages. CPU/RSS come from native resources. Timing spreads retain every observation.

## measurements

144 measured samples; 24 excluded warmups.

| Configuration | B median s | C median s | Elapsed change | Pair spread | CPU change | RSS change |
|---|---:|---:|---:|---:|---:|---:|
| ipv4-disjoint-ranges | 0.4314 | 0.3108 | -26.89% | -39.19…-25.71% | -26.93% | +0.21% |
| ipv4-disjoint-cidr | 0.3364 | 0.3008 | -10.23% | -13.04…-4.30% | -10.24% | -0.16% |
| ipv6-disjoint-ranges | 0.6557 | 0.5069 | -22.49% | -24.43…-16.59% | -22.49% | -0.05% |
| ipv6-disjoint-cidr | 0.5479 | 0.4829 | -12.05% | -14.35…-9.38% | -12.04% | +0.08% |
| mixed-disjoint-ranges | 0.5672 | 0.4180 | -26.51% | -28.00…-20.83% | -26.53% | +0.15% |
| mixed-disjoint-cidr | 0.4376 | 0.3918 | -11.31% | -11.99…+9.24% | -11.32% | -0.06% |
| mixed-permuted-ranges | 0.6698 | 0.5148 | -23.86% | -32.52…-20.91% | -23.94% | +0.02% |
| mixed-permuted-cidr | 0.5341 | 0.4876 | -8.75% | -10.40…-4.33% | -8.76% | +0.09% |
| mixed-overlap-ranges | 0.4089 | 0.4065 | -0.36% | -4.66…+20.06% | -0.36% | +0.04% |
| mixed-overlap-cidr | 0.3990 | 0.3952 | -1.04% | -8.52…+5.40% | -1.02% | +0.03% |
| range-derived-mixed-ranges | 0.4647 | 0.3748 | -18.21% | -26.96…+0.24% | -18.26% | -0.19% |
| range-derived-mixed-cidr | 0.4854 | 0.4225 | -16.85% | -19.33…+1.91% | -16.86% | +0.04% |

## followup-01

36 measured samples; 6 excluded warmups.

| Configuration | B median s | C median s | Elapsed change | Pair spread | CPU change | RSS change |
|---|---:|---:|---:|---:|---:|---:|
| mixed-disjoint-cidr | 0.4425 | 0.3974 | -8.65% | -12.06…-5.07% | -8.67% | +0.01% |
| mixed-overlap-ranges | 0.4009 | 0.4010 | +1.06% | -14.43…+13.16% | +1.05% | +0.04% |
| mixed-overlap-cidr | 0.4155 | 0.3968 | -0.47% | -12.54…+10.22% | -0.48% | +0.01% |

