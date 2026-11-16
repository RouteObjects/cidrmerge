# macos paired results

Negative changes favor the candidate. Each row is six pairs; changes are medians of paired percentages. CPU/RSS come from native resources. Timing spreads retain every observation.

## measurements

144 measured samples; 24 excluded warmups.

| Configuration | B median s | C median s | Elapsed change | Pair spread | CPU change | RSS change |
|---|---:|---:|---:|---:|---:|---:|
| ipv4-disjoint-ranges | 0.3188 | 0.2278 | -28.87% | -31.77…-25.93% | -30.00% | -0.08% |
| ipv4-disjoint-cidr | 0.2454 | 0.2236 | -8.98% | -29.29…-5.67% | -8.70% | -0.03% |
| ipv6-disjoint-ranges | 0.5686 | 0.4322 | -24.58% | -33.81…-20.44% | -22.64% | -0.02% |
| ipv6-disjoint-cidr | 0.4624 | 0.4128 | -10.61% | -21.63…-3.15% | -10.23% | -0.04% |
| mixed-disjoint-ranges | 0.4741 | 0.3421 | -27.10% | -29.81…-25.72% | -28.57% | -0.17% |
| mixed-disjoint-cidr | 0.3603 | 0.3266 | -9.51% | -11.18…-8.10% | -11.76% | -0.05% |
| mixed-permuted-ranges | 0.5685 | 0.4353 | -22.87% | -24.35…-12.66% | -24.07% | -0.19% |
| mixed-permuted-cidr | 0.4536 | 0.4203 | -6.96% | -12.64…+9.51% | -6.98% | -0.57% |
| mixed-overlap-ranges | 0.3528 | 0.3524 | -0.39% | -8.42…+0.51% | +0.00% | -0.34% |
| mixed-overlap-cidr | 0.3558 | 0.3541 | -0.06% | -6.58…+1.99% | +0.00% | -0.02% |
| range-derived-mixed-ranges | 0.3688 | 0.3207 | -13.64% | -14.87…-3.31% | -14.29% | +0.09% |
| range-derived-mixed-cidr | 0.3832 | 0.3388 | -10.87% | -29.75…-8.83% | -11.27% | -0.05% |

## followup-01

12 measured samples; 2 excluded warmups.

| Configuration | B median s | C median s | Elapsed change | Pair spread | CPU change | RSS change |
|---|---:|---:|---:|---:|---:|---:|
| mixed-permuted-cidr | 0.4532 | 0.4199 | -6.84% | -21.27…+5.14% | -6.98% | +0.86% |

