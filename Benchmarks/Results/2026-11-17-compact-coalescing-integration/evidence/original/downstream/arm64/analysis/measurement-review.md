# ARM64 Linux matched integration review

All four independent audits passed: 312 measured observations, 52 excluded warmups, 372 measured child processes and 62 warmup processes. There are26 phase-separated summaries and156 pairs.

Only the1,000-entry disjoint case triggered the prescribed follow-up: +5.72% elapsed/+6.07% CPU initially, then +2.12%/+1.76%. Its elapsed ranges cross zero widely in both phases (−10.85…+20.13%, then−12.39…+10.45%). No elapsed or RSS paired-median regression above5% repeated. All observations remain retained.

Original million-entry elapsed paired medians range from−1.24% to+3.50%; RSS from−4.47% to+0.09%. Range-derived input is+3.50% elapsed/+3.50% CPU and+0.08% RSS. The1,000,002-entry sparse input is+0.89% elapsed/+0.88% CPU and+0.02% RSS, with broad signed timing spread. These small changes should not be presented as general throughput gains.

Small-input RSS is limited by the Linux pre-exec parent high-water floor; equal RSS does not prove equal allocations.

| Group / phase | Case | B elapsed ms | C elapsed ms | Paired elapsed % [min,max] | Paired CPU % [min,max] | B RSS MiB | C RSS MiB | Paired RSS % [min,max] |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| original / primary | split-ipv4-disjoint | 205.5892 | 206.5008 | -0.027 [-6.346, +1.553] | -0.028 [-6.374, +1.565] | 42.2148 | 42.2383 | +0.028 [-0.139, +0.287] |
| original / primary | split-ipv6-disjoint | 324.3836 | 327.5944 | +1.414 [-0.701, +15.683] | +1.408 [-0.720, +15.672] | 110.8809 | 110.9336 | +0.041 [-0.039, +0.130] |
| original / primary | split-mixed-disjoint | 270.2983 | 267.9716 | -0.293 [-1.903, +2.974] | -0.285 [-1.902, +2.983] | 65.1250 | 65.1973 | +0.042 [-0.012, +0.150] |
| original / primary | split-mixed-permuted | 365.8564 | 364.8223 | +0.627 [-4.003, +7.800] | +0.624 [-3.995, +7.811] | 72.5156 | 72.5859 | +0.092 [+0.000, +0.151] |
| original / primary | split-mixed-overlap | 276.9686 | 277.4039 | -0.919 [-3.788, +1.975] | -0.941 [-3.808, +1.955] | 57.2852 | 57.3184 | +0.055 [-0.007, +0.171] |
| original / primary | split-mixed-adjacent | 201.3049 | 200.9747 | -0.239 [-3.447, +2.295] | -0.246 [-3.469, +2.264] | 49.9297 | 49.9414 | +0.035 [-0.047, +0.196] |
| original / primary | split-bgp-like-ipv4 | 302.7283 | 304.8420 | +0.860 [-0.593, +22.218] | +0.859 [-0.617, +22.225] | 39.7676 | 38.2480 | -3.781 [-3.831, -3.632] |
| original / primary | split-range-derived-mixed | 271.2102 | 279.9432 | +3.499 [-1.260, +6.908] | +3.498 [-1.245, +6.929] | 65.0137 | 65.0664 | +0.084 [-0.102, +0.102] |
| original / primary | native-mixed-disjoint | 272.7980 | 271.6228 | -1.243 [-16.041, +3.764] | -1.241 [-16.051, +3.780] | 76.5918 | 76.5977 | -0.015 [-0.138, +0.092] |
| original / primary | native-mixed-permuted | 362.6000 | 365.1860 | +0.850 [-2.714, +4.712] | +0.838 [-2.719, +4.712] | 84.1113 | 80.3262 | -4.474 [-4.542, -4.421] |
| original / primary | native-mixed-overlap | 277.6648 | 277.5205 | +0.142 [-1.909, +3.062] | +0.137 [-1.888, +3.063] | 66.8984 | 65.0430 | -2.788 [-2.893, -2.664] |
| scale / primary | mixed-disjoint-1000 | 6.1639 | 6.4570 | +5.721 [-10.853, +20.132] | +6.068 [-10.579, +21.369] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.000] |
| scale / primary | mixed-disjoint-10000 | 8.6597 | 8.3290 | -3.047 [-9.844, +5.009] | -3.008 [-9.865, +3.796] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.000] |
| scale / primary | mixed-disjoint-100000 | 32.3052 | 32.3770 | +0.908 [-0.767, +6.922] | +0.738 [-0.731, +7.226] | 25.3496 | 25.2832 | -0.231 [-0.370, +0.170] |
| scale / primary | mixed-permuted-1000 | 6.2160 | 6.3608 | -2.230 [-12.347, +14.451] | -2.498 [-12.331, +13.469] | 22.9531 | 22.8906 | +0.000 [-0.543, +0.000] |
| scale / primary | mixed-permuted-10000 | 9.3235 | 9.0239 | -4.400 [-7.999, +2.650] | -4.505 [-7.781, +2.701] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.000] |
| scale / primary | mixed-permuted-100000 | 40.2500 | 40.6420 | +0.700 [-3.395, +5.618] | +0.626 [-3.441, +5.541] | 26.0293 | 25.6621 | -1.411 [-1.500, -0.753] |
| scale / primary | mixed-overlap-1000 | 6.0713 | 6.3825 | +3.758 [-63.637, +22.063] | +3.417 [-42.984, +21.556] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.000] |
| scale / primary | mixed-overlap-10000 | 8.3439 | 7.8847 | -6.065 [-8.893, +38.622] | -5.932 [-8.655, +38.498] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.000] |
| scale / primary | mixed-overlap-100000 | 31.4306 | 31.5607 | +0.145 [-0.554, +1.829] | +0.062 [-0.523, +1.791] | 24.1465 | 23.7715 | -1.537 [-1.729, -1.408] |
| scale / primary | mixed-adjacent-1000 | 6.3478 | 6.1238 | -3.514 [-9.831, +13.785] | -3.468 [-9.949, +13.338] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.549] |
| scale / primary | mixed-adjacent-10000 | 7.6280 | 7.5582 | -0.851 [-9.861, +8.076] | -0.510 [-9.947, +8.018] | 22.9531 | 22.9531 | +0.000 [+0.000, +0.000] |
| scale / primary | mixed-adjacent-100000 | 24.9392 | 25.0128 | -1.902 [-8.235, +2.723] | -1.852 [-8.182, +2.634] | 23.3926 | 23.3945 | -0.008 [-0.084, +0.285] |
| scale / followup | mixed-disjoint-1000 | 5.8736 | 5.9647 | +2.123 [-12.395, +10.454] | +1.762 [-12.912, +9.628] | 21.7148 | 21.7148 | +0.000 [+0.000, +0.000] |
| sparse / primary | mixed-sparse-duplicate-10000 | 8.7105 | 8.9221 | +2.181 [-10.973, +11.903] | +2.358 [-10.492, +12.078] | 23.0859 | 23.0234 | +0.000 [-0.540, +0.000] |
| sparse / primary | mixed-sparse-duplicate-1000000 | 270.5138 | 272.9214 | +0.890 [-9.944, +18.082] | +0.879 [-9.872, +18.144] | 76.6328 | 76.6504 | +0.015 [-0.036, +0.051] |

All individual positive changes above5% (elapsed, CPU or RSS) are listed without removal in `measurement-review.json`; these individual observations are distinct from the paired-median follow-up criterion.

Postmeasurement checks verified both complete source inventories, all five ordinary/test/floor dependency workspaces, compiler and binary/runtime hashes, and zero memory/OOM events. The container is stopped and preserved.
