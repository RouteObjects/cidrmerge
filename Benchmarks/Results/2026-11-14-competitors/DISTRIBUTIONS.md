# Sample distributions

Elapsed quartiles and full ranges are descriptive. No samples were removed.
The machine-readable summary retains every sample, RSS quartiles, CPU time, output bytes, and hashes.

| Suite | Corpus | Tool | n | Elapsed p25–p75 (s) | Elapsed min–max (s) | RSS min–max (MiB) |
|---|---|---|---:|---:|---:|---:|
| split | ipv4-disjoint | cidrmerge | 8 | 0.828–0.837 | 0.814–0.893 | 68.5–70.9 |
| split | ipv4-disjoint | rs-aggregate | 8 | 0.171–0.177 | 0.170–0.221 | 29.8–31.1 |
| split | ipv4-disjoint | iprange | 8 | 0.306–0.322 | 0.302–0.350 | 11.5–11.5 |
| split | ipv4-disjoint | mapcidr | 8 | 11.330–11.718 | 11.207–11.930 | 993.3–1288.9 |
| split | ipv6-disjoint | cidrmerge | 8 | 1.164–1.206 | 1.155–1.253 | 166.4–167.2 |
| split | ipv6-disjoint | rs-aggregate | 8 | 0.254–0.276 | 0.253–0.306 | 98.5–99.6 |
| split | ipv6-disjoint | iprange | 8 | 1.608–1.628 | 1.582–1.665 | 34.4–34.4 |
| split | ipv6-disjoint | mapcidr | 8 | 14.004–15.414 | 13.923–17.552 | 1215.7–1389.4 |
| split | mixed-disjoint | cidrmerge | 8 | 1.007–1.030 | 0.993–1.066 | 86.2–86.9 |
| split | mixed-disjoint | rs-aggregate | 8 | 0.223–0.228 | 0.220–0.229 | 51.7–52.8 |
| split | mixed-disjoint | iprange | 8 | 0.695–0.703 | 0.689–0.731 | 19.1–19.1 |
| split | mixed-disjoint | mapcidr | 8 | 12.526–12.952 | 12.354–13.167 | 670.2–708.2 |
| split | mixed-permuted | cidrmerge | 8 | 2.284–2.325 | 2.271–2.363 | 86.6–86.9 |
| split | mixed-permuted | rs-aggregate | 8 | 0.261–0.271 | 0.261–0.280 | 51.7–52.8 |
| split | mixed-permuted | iprange | 8 | 0.803–0.825 | 0.800–0.896 | 34.4–34.4 |
| split | mixed-permuted | mapcidr | 8 | 16.757–17.652 | 16.605–18.666 | 666.8–713.6 |
| split | mixed-overlap | cidrmerge | 8 | 1.805–1.835 | 1.795–1.923 | 70.6–71.3 |
| split | mixed-overlap | rs-aggregate | 8 | 0.152–0.153 | 0.150–0.155 | 34.9–35.0 |
| split | mixed-overlap | iprange | 8 | 0.211–0.216 | 0.209–0.217 | 19.1–19.1 |
| split | mixed-overlap | mapcidr | 8 | 10.166–10.525 | 10.130–11.392 | 566.0–597.5 |
| split | mixed-adjacent | cidrmerge | 8 | 0.826–0.880 | 0.823–0.928 | 70.8–71.6 |
| split | mixed-adjacent | rs-aggregate | 8 | 0.119–0.121 | 0.115–0.132 | 27.3–27.3 |
| split | mixed-adjacent | iprange | 8 | 0.128–0.130 | 0.127–0.133 | 1.8–1.8 |
| split | mixed-adjacent | mapcidr | 8 | 6.323–6.578 | 6.248–6.790 | 611.6–679.5 |
| split | bgp-like-ipv4 | cidrmerge | 8 | 2.025–2.058 | 2.017–2.143 | 55.9–58.0 |
| split | bgp-like-ipv4 | rs-aggregate | 8 | 0.148–0.149 | 0.145–0.152 | 25.6–26.9 |
| split | bgp-like-ipv4 | iprange | 8 | 0.265–0.271 | 0.263–0.287 | 13.0–13.0 |
| split | bgp-like-ipv4 | mapcidr | 8 | 24.577–25.687 | 24.535–26.336 | 908.9–1148.9 |
| split | range-derived-mixed | cidrmerge | 8 | 1.036–1.047 | 1.021–1.130 | 94.7–95.0 |
| split | range-derived-mixed | rs-aggregate | 8 | 0.223–0.227 | 0.219–0.233 | 44.1–45.2 |
| split | range-derived-mixed | iprange | 8 | 0.692–0.700 | 0.688–0.725 | 11.5–11.5 |
| split | range-derived-mixed | mapcidr | 8 | 23.931–24.847 | 23.885–25.223 | 633.1–747.3 |
| native | mixed-disjoint | cidrmerge | 9 | 1.003–1.027 | 0.990–1.082 | 117.8–119.3 |
| native | mixed-disjoint | rs-aggregate | 9 | 0.215–0.216 | 0.212–0.217 | 63.1–66.7 |
| native | mixed-disjoint | mapcidr | 9 | 12.407–12.812 | 12.373–13.013 | 1139.0–1337.5 |
| native | mixed-permuted | cidrmerge | 9 | 2.284–2.333 | 2.275–2.370 | 118.6–119.6 |
| native | mixed-permuted | rs-aggregate | 9 | 0.243–0.246 | 0.242–0.254 | 66.2–68.2 |
| native | mixed-permuted | mapcidr | 9 | 16.949–17.069 | 16.797–17.218 | 1145.4–1322.6 |
| native | mixed-overlap | cidrmerge | 9 | 1.806–1.813 | 1.801–1.847 | 82.5–84.0 |
| native | mixed-overlap | rs-aggregate | 9 | 0.136–0.138 | 0.136–0.139 | 46.5–46.9 |
| native | mixed-overlap | mapcidr | 9 | 10.380–10.408 | 10.359–10.710 | 877.8–989.3 |
