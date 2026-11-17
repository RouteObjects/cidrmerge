# Regression observations and separate follow-ups

The trigger was any paired elapsed-time or RSS increase above 5%, not only a median increase. Every triggered primary case gets a separate fixed-size follow-up. Primary and follow-up values are never pooled. “Repeated >5% median” below means both phase medians exceed 5%; it is a descriptive rule, not a significance test.

Migration-only regressions are evaluated separately from the retained R3 result. The S2 borrowed-line implementation was rejected after repeatable text-throughput regressions. Small/noisy startup changes need their absolute durations and spread considered; see RETAINED.md and the CSVs.

## macOS ARM64

| Workload / comparison / profile | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| startup / B-vs-E4 / ordinary | empty-stdin | elapsed | +2.60% [-3.33%, +14.57%] (primary-02) | +2.27% [-18.46%, +10.67%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-E4 / ordinary | mixed-100 | elapsed | +3.94% [-5.88%, +17.61%] (primary-02) | +3.64% [-4.29%, +180.85%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-E4 / ordinary | mixed-10000 | elapsed | +0.83% [-35.61%, +15.77%] (primary-02) | +2.25% [-55.71%, +11.43%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-E4 / ordinary | version | elapsed | +4.15% [-17.27%, +11.42%] (primary-02) | +3.56% [-3.92%, +62.54%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-R3 / ordinary | empty-stdin | elapsed | +2.58% [-8.51%, +40.14%] (primary) | +3.55% [-8.05%, +30.84%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-R3 / ordinary | mixed-100 | elapsed | +1.02% [-3.45%, +5.24%] (primary) | +2.90% [-5.35%, +114.13%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-R3 / ordinary | mixed-10000 | elapsed | -2.49% [-14.30%, +5.52%] (primary) | -2.29% [-11.71%, +70.22%] (followup) | Triggered observation; no repeated positive median |
| startup / B-vs-R3 / ordinary | version | elapsed | +3.68% [-8.54%, +28.62%] (primary) | +5.35% [-15.22%, +14.69%] (followup) | Not repeatable at >5%; mixed/noisy phases |
| startup / B-vs-S2 / ordinary | empty-stdin | elapsed | +2.47% [-7.26%, +19.53%] (primary) | +0.96% [-14.30%, +11.79%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / ordinary | mixed-100 | elapsed | +0.76% [-20.55%, +16.47%] (primary) | +2.78% [-16.12%, +12.55%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / ordinary | mixed-10000 | elapsed | +1.40% [-13.71%, +8.20%] (primary) | +1.97% [-15.59%, +11.13%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / ordinary | version | elapsed | +2.00% [-6.47%, +11.46%] (primary) | +3.28% [-2.09%, +30.85%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / E4-vs-R3 / ordinary | empty-stdin | elapsed | +1.52% [-5.12%, +26.18%] (primary) | -0.53% [-10.00%, +13.60%] (followup) | Triggered observation; no repeated positive median |
| startup / E4-vs-R3 / ordinary | mixed-100 | elapsed | -0.71% [-9.97%, +10.32%] (primary) | +2.49% [-9.05%, +31.52%] (followup) | Triggered observation; no repeated positive median |
| startup / E4-vs-R3 / ordinary | version | elapsed | -0.28% [-16.82%, +7.04%] (primary) | +0.46% [-7.79%, +18.31%] (followup) | Triggered observation; no repeated positive median |
| startup / R3-vs-S2 / ordinary | empty-stdin | elapsed | +1.00% [-20.86%, +7.40%] (primary) | +4.68% [-52.04%, +27.43%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / R3-vs-S2 / ordinary | mixed-100 | elapsed | -0.08% [-11.54%, +16.65%] (primary) | +1.86% [-32.92%, +126.77%] (followup) | Triggered observation; no repeated positive median |
| startup / R3-vs-S2 / ordinary | mixed-10000 | elapsed | +3.30% [-6.59%, +11.75%] (primary) | +5.02% [-5.72%, +35.73%] (followup) | Not repeatable at >5%; mixed/noisy phases |
| startup / R3-vs-S2 / ordinary | version | elapsed | +1.01% [-3.69%, +11.20%] (primary) | -2.26% [-51.06%, +9.75%] (followup) | Triggered observation; no repeated positive median |
| startup / B-vs-R3 / release-style | empty-stdin | elapsed | +2.70% [-10.60%, +34.41%] (primary) | +2.09% [-22.84%, +28.99%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-R3 / release-style | mixed-100 | elapsed | +3.27% [-5.71%, +25.72%] (primary) | +1.65% [-15.10%, +150.51%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-R3 / release-style | mixed-10000 | elapsed | -3.35% [-13.53%, +5.76%] (primary) | -1.54% [-48.33%, +58.51%] (followup) | Triggered observation; no repeated positive median |
| startup / B-vs-R3 / release-style | version | elapsed | +4.19% [-14.72%, +16.22%] (primary) | +2.90% [-2.51%, +127.03%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / release-style | empty-stdin | elapsed | +2.56% [-45.50%, +16.93%] (primary) | +1.43% [-11.32%, +11.04%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / release-style | mixed-100 | elapsed | +2.89% [-21.83%, +10.67%] (primary) | +2.64% [-2.33%, +15.05%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / release-style | mixed-10000 | elapsed | +3.71% [-12.65%, +11.81%] (primary) | +2.82% [-9.05%, +11.19%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-S2 / release-style | version | elapsed | +2.95% [-59.03%, +19.11%] (primary) | +4.84% [-22.91%, +11.04%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | text-ipv4-canonical-stats | elapsed | +2.15% [+0.96%, +11.21%] (primary) | +1.58% [+0.99%, +3.11%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | text-mixed-overlap-no-stats | elapsed | +0.92% [-0.12%, +5.88%] (primary) | +0.73% [-4.32%, +0.95%] (followup) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | text-ipv4-canonical-no-stats | elapsed | +31.86% [+31.49%, +32.95%] (primary) | +31.12% [+29.12%, +32.04%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv4-canonical-stats | elapsed | +28.00% [+27.19%, +34.30%] (primary) | +28.30% [+27.03%, +29.35%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv6-canonical-no-stats | elapsed | +12.58% [+10.01%, +14.97%] (primary) | +12.95% [+11.05%, +13.96%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv6-canonical-stats | elapsed | +11.58% [+9.56%, +15.95%] (primary) | +11.20% [+10.19%, +12.28%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-addresses-no-stats | elapsed | +15.13% [+14.19%, +19.16%] (primary) | +15.37% [+14.52%, +21.15%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-addresses-stats | elapsed | +12.29% [+10.42%, +13.96%] (primary) | +13.13% [+11.02%, +34.16%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-noncanonical-no-stats | elapsed | +13.74% [+13.05%, +15.80%] (primary) | +14.06% [+12.78%, +23.53%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-noncanonical-stats | elapsed | +11.94% [+10.96%, +12.56%] (primary) | +12.06% [+9.64%, +13.20%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-overlap-no-stats | elapsed | +18.15% [+8.03%, +26.63%] (primary) | +18.48% [+18.05%, +20.73%] (followup) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-overlap-stats | elapsed | +16.43% [+13.44%, +16.99%] (primary) | +17.19% [+16.34%, +43.39%] (followup) | Repeated >5% median |

### Additional >5% observations first seen in follow-up

These metrics did not trigger in the primary phase. The case was already selected for follow-up by its other metric. All follow-up observations remain preserved; the protocol does not recursively schedule a third phase.

| Workload / comparison / profile | Case | Metric | Primary median [min, max] | Follow-up median [min, max] |
|---|---|---|---:|---:|
| startup / B-vs-S2 / ordinary | mixed-10000 | rss | +1.81% [-0.59%, +2.62%] (primary) | +2.01% [+1.40%, +5.03%] (followup) |
## Linux ARM64

| Workload / comparison / profile | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| startup / E4-vs-R3 / ordinary | empty-stdin | elapsed | -0.53% [-5.26%, +9.78%] (primary) | +0.20% [-15.04%, +5.91%] (followup-01) | Triggered observation; no repeated positive median |
| startup / E4-vs-R3 / ordinary | mixed-100 | elapsed | +0.17% [-8.07%, +14.40%] (primary) | -0.23% [-15.28%, +6.58%] (followup-01) | Triggered observation; no repeated positive median |
| startup / E4-vs-R3 / ordinary | mixed-10000 | elapsed | -7.86% [-47.55%, +48.01%] (primary) | -8.16% [-14.05%, -4.52%] (followup-01) | Triggered observation; no repeated positive median |
| startup / E4-vs-R3 / ordinary | version | elapsed | +1.75% [-4.82%, +8.46%] (primary) | +1.94% [-6.84%, +18.87%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / R3-vs-S2 / ordinary | empty-stdin | elapsed | +0.46% [-4.42%, +7.05%] (primary) | -0.44% [-5.85%, +10.07%] (followup-01) | Triggered observation; no repeated positive median |
| startup / R3-vs-S2 / ordinary | mixed-10000 | elapsed | +4.00% [+0.59%, +11.64%] (primary) | +3.27% [-44.11%, +8.17%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / R3-vs-S2 / ordinary | version | elapsed | +0.75% [-8.49%, +6.67%] (primary) | +0.88% [-5.05%, +111.43%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| startup / B-vs-R3 / release-style | mixed-10000 | elapsed | -14.75% [-26.12%, +9.55%] (primary) | -14.89% [-21.28%, -7.26%] (followup-01) | Triggered observation; no repeated positive median |
| stdin / B-vs-E4 / ordinary | searchbot-canonical-no-stats | elapsed | +0.97% [-4.03%, +5.57%] (primary) | +2.64% [-4.77%, +17.63%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| stdin / B-vs-R3 / ordinary | searchbot-canonical-no-stats | elapsed | +0.39% [-1.57%, +8.00%] (primary) | +0.15% [-1.07%, +4.48%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| stdin / B-vs-R3 / ordinary | searchbot-noncanonical-stats | elapsed | +2.13% [+0.91%, +8.87%] (primary) | +1.31% [-5.42%, +4.27%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| stdin / B-vs-S2 / ordinary | searchbot-canonical-no-stats | elapsed | +0.89% [-2.48%, +10.21%] (primary) | +0.92% [-11.09%, +4.18%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| stdin / B-vs-S2 / ordinary | searchbot-noncanonical-stats | elapsed | +2.69% [-4.33%, +5.19%] (primary) | +1.35% [-1.51%, +7.06%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | searchbot-canonical-no-stats | elapsed | +2.36% [-13.14%, +7.35%] (primary) | +2.63% [-1.37%, +4.57%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | searchbot-canonical-stats | elapsed | +1.49% [-1.98%, +6.14%] (primary) | +2.35% [+0.65%, +5.06%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | searchbot-noncanonical-no-stats | elapsed | -0.31% [-11.94%, +5.30%] (primary) | +2.81% [+1.15%, +5.62%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | searchbot-noncanonical-stats | elapsed | +1.64% [-7.92%, +6.14%] (primary) | +4.42% [+1.84%, +10.35%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | text-ipv4-canonical-stats | elapsed | -0.09% [-7.69%, +5.78%] (primary) | -1.37% [-2.72%, +0.32%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | text-ipv6-canonical-no-stats | elapsed | +1.21% [-1.03%, +11.26%] (primary) | -1.40% [-10.75%, +2.00%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | text-ipv6-canonical-stats | elapsed | -0.49% [-3.73%, +6.36%] (primary) | -0.19% [-9.35%, +10.95%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | text-mixed-overlap-no-stats | elapsed | -0.71% [-2.41%, +13.82%] (primary) | +0.01% [-1.27%, +2.91%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | text-mixed-ranges-stats | elapsed | -0.79% [-3.31%, +5.02%] (primary) | -0.70% [-4.51%, +2.24%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-R3 / ordinary | searchbot-canonical-stats | elapsed | +2.82% [+0.11%, +6.70%] (primary) | +2.17% [-1.02%, +8.25%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-R3 / ordinary | searchbot-noncanonical-stats | elapsed | +1.96% [-2.81%, +6.31%] (primary) | -1.00% [-7.00%, +2.29%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-S2 / ordinary | searchbot-canonical-no-stats | elapsed | +0.55% [-0.63%, +8.29%] (primary) | +4.74% [-1.03%, +8.68%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-S2 / ordinary | searchbot-noncanonical-no-stats | elapsed | +3.54% [+0.91%, +6.73%] (primary) | +0.57% [-7.20%, +3.44%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-S2 / ordinary | searchbot-noncanonical-stats | elapsed | +3.25% [-2.33%, +8.43%] (primary) | +2.84% [-10.91%, +7.88%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | searchbot-canonical-stats | elapsed | +1.08% [-4.06%, +6.52%] (primary) | +4.51% [-3.65%, +7.05%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | text-ipv4-canonical-no-stats | elapsed | +12.76% [+10.94%, +14.72%] (primary) | +12.57% [+9.41%, +29.77%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv4-canonical-stats | elapsed | +10.66% [+9.41%, +18.44%] (primary) | +8.38% [+2.68%, +12.00%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv6-canonical-stats | elapsed | +2.72% [-1.92%, +10.99%] (primary) | +2.61% [+0.70%, +8.01%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | text-mixed-addresses-stats | elapsed | +5.23% [+0.29%, +8.09%] (primary) | +3.38% [-2.75%, +6.22%] (followup-01) | Not repeatable at >5%; mixed/noisy phases |
| throughput / R3-vs-S2 / ordinary | text-mixed-overlap-no-stats | elapsed | +9.61% [+6.00%, +22.26%] (primary) | +7.51% [+4.57%, +11.95%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-overlap-stats | elapsed | +8.64% [+5.21%, +13.72%] (primary) | +6.46% [-5.43%, +7.88%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-ranges-stats | elapsed | +2.28% [+1.34%, +7.62%] (primary) | +1.85% [+0.63%, +54.02%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
## Linux x86-64

| Workload / comparison / profile | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |
|---|---|---|---:|---:|---|
| startup / E4-vs-R3 / ordinary | mixed-100 | elapsed | +0.23% [-1.82%, +6.10%] (primary) | -0.42% [-4.22%, +4.80%] (followup-01) | Triggered observation; no repeated positive median |
| startup / R3-vs-S2 / ordinary | mixed-10000 | elapsed | +9.54% [+2.59%, +13.97%] (primary) | +8.09% [+5.41%, +11.30%] (followup-01) | Repeated >5% median |
| startup / B-vs-S2 / release-style | mixed-10000 | elapsed | -6.09% [-9.96%, +5.20%] (primary) | -6.61% [-9.98%, -1.72%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | text-ipv4-canonical-no-stats | elapsed | +4.57% [+0.17%, +13.83%] (primary) | +9.79% [+6.69%, +11.84%] (followup-01) | Not repeatable at >5%; mixed/noisy phases |
| throughput / B-vs-E4 / ordinary | text-ipv6-canonical-no-stats | elapsed | +5.79% [-0.04%, +13.67%] (primary) | -0.64% [-2.66%, +11.53%] (followup-01) | Not repeatable at >5%; mixed/noisy phases |
| throughput / B-vs-E4 / ordinary | text-ipv6-canonical-stats | elapsed | +2.23% [+0.25%, +8.62%] (primary) | +1.88% [-1.21%, +11.06%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | text-mixed-addresses-no-stats | elapsed | +5.71% [-1.52%, +8.46%] (primary) | +5.21% [-1.83%, +9.26%] (followup-01) | Repeated >5% median |
| throughput / B-vs-E4 / ordinary | text-mixed-addresses-stats | elapsed | +9.55% [-3.05%, +11.99%] (primary) | +7.43% [-1.97%, +20.60%] (followup-01) | Repeated >5% median |
| throughput / B-vs-E4 / ordinary | text-mixed-noncanonical-no-stats | elapsed | +6.21% [-1.23%, +8.50%] (primary) | +6.82% [-1.34%, +8.18%] (followup-01) | Repeated >5% median |
| throughput / B-vs-E4 / ordinary | text-mixed-noncanonical-stats | elapsed | +1.53% [+0.47%, +9.86%] (primary) | +1.92% [-0.81%, +10.53%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | text-mixed-overlap-no-stats | elapsed | +3.58% [+1.94%, +5.86%] (primary) | +3.28% [-2.05%, +6.74%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-E4 / ordinary | text-mixed-ranges-no-stats | elapsed | +1.13% [+0.01%, +7.53%] (primary) | -0.16% [-3.51%, +0.22%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-E4 / ordinary | text-mixed-ranges-stats | elapsed | +1.28% [-2.02%, +7.95%] (primary) | +1.86% [-0.55%, +2.44%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-R3 / ordinary | searchbot-canonical-no-stats | elapsed | -1.61% [-3.71%, +67.24%] (primary) | -1.69% [-3.19%, +1.91%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-R3 / ordinary | searchbot-noncanonical-stats | elapsed | -1.36% [-1.97%, +32.40%] (primary) | -0.29% [-2.73%, +3.68%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-R3 / ordinary | text-ipv4-canonical-stats | elapsed | -12.88% [-13.39%, +30.00%] (primary) | -13.44% [-19.31%, -7.95%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-S2 / ordinary | searchbot-canonical-stats | elapsed | -0.20% [-4.70%, +5.02%] (primary) | +1.69% [-2.31%, +2.38%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-S2 / ordinary | text-ipv4-canonical-no-stats | elapsed | +9.29% [+3.14%, +14.91%] (primary) | +8.38% [+5.85%, +17.93%] (followup-01) | Repeated >5% median |
| throughput / B-vs-S2 / ordinary | text-ipv4-canonical-stats | elapsed | +15.39% [+12.03%, +24.71%] (primary) | +22.37% [+10.63%, +30.27%] (followup-01) | Repeated >5% median |
| throughput / B-vs-S2 / ordinary | text-ipv6-canonical-no-stats | elapsed | +3.59% [-2.69%, +6.21%] (primary) | +2.05% [-9.35%, +7.81%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-S2 / ordinary | text-ipv6-canonical-stats | elapsed | +7.07% [+1.44%, +11.77%] (primary) | +8.89% [+5.78%, +18.03%] (followup-01) | Repeated >5% median |
| throughput / B-vs-S2 / ordinary | text-mixed-addresses-no-stats | elapsed | +0.83% [-4.89%, +6.93%] (primary) | -2.19% [-9.65%, +3.34%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-S2 / ordinary | text-mixed-addresses-stats | elapsed | -0.69% [-4.46%, +8.47%] (primary) | +3.36% [+0.58%, +7.46%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / B-vs-S2 / ordinary | text-mixed-noncanonical-stats | elapsed | +2.67% [-5.53%, +7.06%] (primary) | +2.07% [-2.14%, +9.55%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / B-vs-S2 / ordinary | text-mixed-overlap-no-stats | elapsed | +7.92% [-0.02%, +12.60%] (primary) | +10.49% [+2.85%, +13.10%] (followup-01) | Repeated >5% median |
| throughput / B-vs-S2 / ordinary | text-mixed-overlap-stats | elapsed | +11.25% [+5.66%, +15.92%] (primary) | +10.53% [+7.97%, +14.10%] (followup-01) | Repeated >5% median |
| throughput / B-vs-S2 / ordinary | text-mixed-ranges-stats | elapsed | -1.04% [-3.56%, +13.11%] (primary) | -0.57% [-4.58%, +3.37%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / E4-vs-R3 / ordinary | text-mixed-addresses-no-stats | elapsed | -15.01% [-18.21%, +25.41%] (primary) | -14.45% [-17.72%, -12.75%] (followup-01) | Triggered observation; no repeated positive median |
| throughput / R3-vs-S2 / ordinary | searchbot-canonical-no-stats | elapsed | +2.27% [-1.14%, +5.74%] (primary) | +1.49% [-0.56%, +3.69%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | searchbot-noncanonical-no-stats | elapsed | +3.79% [+2.40%, +5.01%] (primary) | +2.25% [+0.13%, +4.22%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | text-ipv4-canonical-no-stats | elapsed | +25.08% [+15.72%, +32.48%] (primary) | +20.39% [+14.75%, +29.04%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv4-canonical-stats | elapsed | +30.22% [+19.51%, +42.91%] (primary) | +30.96% [+24.29%, +47.52%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv6-canonical-no-stats | elapsed | +14.55% [+7.95%, +19.68%] (primary) | +11.52% [+4.08%, +14.55%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-ipv6-canonical-stats | elapsed | +18.55% [+4.28%, +31.28%] (primary) | +16.59% [+7.28%, +23.44%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-addresses-no-stats | elapsed | +10.37% [+4.58%, +14.33%] (primary) | +4.98% [+4.66%, +8.65%] (followup-01) | Not repeatable at >5%; mixed/noisy phases |
| throughput / R3-vs-S2 / ordinary | text-mixed-addresses-stats | elapsed | +8.03% [-1.54%, +26.54%] (primary) | +8.30% [-3.65%, +17.57%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-noncanonical-no-stats | elapsed | +6.78% [+0.13%, +12.49%] (primary) | +8.78% [+3.25%, +13.57%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-noncanonical-stats | elapsed | +6.35% [-1.87%, +22.08%] (primary) | +9.22% [+4.72%, +16.47%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-overlap-no-stats | elapsed | +15.63% [+12.79%, +18.33%] (primary) | +14.36% [+9.27%, +25.32%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-overlap-stats | elapsed | +22.10% [+16.03%, +33.10%] (primary) | +22.00% [+16.34%, +28.90%] (followup-01) | Repeated >5% median |
| throughput / R3-vs-S2 / ordinary | text-mixed-ranges-no-stats | elapsed | +3.11% [+0.32%, +6.46%] (primary) | +1.82% [-1.33%, +5.63%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
| throughput / R3-vs-S2 / ordinary | text-mixed-ranges-stats | elapsed | +1.25% [-0.88%, +5.36%] (primary) | +0.58% [-0.27%, +4.33%] (followup-01) | Both medians positive but ≤5%; inspect absolute size/spread |
