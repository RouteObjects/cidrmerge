# Independent final report review

**Passed.** All three platform datasets and rendered tables agree with the preserved independent audits. The checker made 193,373 assertions covering 75 audit phases, 464 case summaries, 4,492 pairs, 78 displayed retained-result rows, and 117 regression rows. Totals reconcile to 8,984 measured observations and 928 excluded warmups. The main report's direct-result ranges and platform totals also match.

The direct B-versus-R3 comparisons contain no repeated greater-than-5% elapsed-time or RSS median regression. This describes primary and follow-up medians; it is not a significance test and does not imply every observation improved. Intermediate migration/S2 results remain separate.

On x86-64, twelve text-case elapsed medians improve 1.88–12.88%, with RSS medians down 5.06–19.31%. CPU changes agree in direction. The roughly 2% range-case changes are modest. The primary IPv4/stats case contains a +30.00% elapsed observation, while its separate follow-up median is −13.44% with every follow-up pair improved.

The x86 Searchbot file cases include +67.24% and +32.39% individual elapsed observations. Their follow-up medians are −1.69% and −0.29%, respectively; the full primary and follow-up spreads remain visible. File and stdin Searchbot changes are small and do not support a general JSON parsing speedup claim.

The Mac startup caveat remains: ordinary `--version` is +3.68% in the primary and +5.35% in the follow-up, about 0.35–0.42 ms difference between absolute observation medians. Shipping-profile tiny-call changes are small/noisy increases; the 10,000-entry case improves. Linux startup improves, but equal shipping RSS sits at the independently demonstrated launcher floor and cannot establish equal application memory. Tiny Mac CPU percentages are unavailable or uninformative because of accounting resolution.

All twelve S2 primary text elapsed medians are slower than R3 on each of the three platforms, corroborating the rejection of that implementation. This does not prove the hypothesized generic-indexing cause. Ordinary throughput measurements must remain distinct from static shipping size/startup evidence, as the main report already states.

Two optional prose clarifications remain: say the **primary** >5% observations trigger the fixed follow-up (further observations do not recursively trigger another phase), and state the small Mac startup increase directly in the main report as well as its companion tables. No numeric correction or new measurement is required.

Receipts: `review-final-independent.json` and `review-final-conclusions.json`. Existing data, reports, reviewer attempts, and source snapshots were not changed.
