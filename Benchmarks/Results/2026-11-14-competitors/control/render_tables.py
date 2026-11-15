#!/usr/bin/env python3
"""Render measured summaries without rounding the underlying retained data."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
summary = json.loads((root / 'summary.json').read_text())
groups = {(x['suite'], x['case'], x['tool']): x for x in summary['groups']}
cases = ['ipv4-disjoint', 'ipv6-disjoint', 'mixed-disjoint', 'mixed-permuted',
         'mixed-overlap', 'mixed-adjacent', 'bgp-like-ipv4', 'range-derived-mixed']
tools = ['cidrmerge', 'rs-aggregate', 'iprange', 'mapcidr']
lines = []
for suite in ['split', 'native']:
    active_tools = tools if suite == 'split' else [x for x in tools if x != 'iprange']
    active_cases = cases if suite == 'split' else ['mixed-disjoint', 'mixed-permuted', 'mixed-overlap']
    lines += [f'## {suite.title()} results', '',
              'Each cell is **median elapsed seconds / median peak RSS MiB**; lower is better.', '',
              '| Corpus | ' + ' | '.join(active_tools) + ' |',
              '|---|' + '---:|' * len(active_tools)]
    for case in active_cases:
        cells = []
        for tool in active_tools:
            row = groups[(suite, case, tool)]
            cells.append(f"{row['elapsed_seconds']['median']:.3f} / {row['peak_rss_mib']['median']:.1f}")
        lines.append('| ' + case + ' | ' + ' | '.join(cells) + ' |')
    lines += ['', 'Paired elapsed ratios are the median of `tool elapsed / cidrmerge elapsed` within each round.',
              'Below 1 means that tool was faster; above 1 means cidrmerge was faster.', '',
              '| Corpus | ' + ' | '.join(active_tools[1:]) + ' |',
              '|---|' + '---:|' * (len(active_tools) - 1)]
    for case in active_cases:
        cells = [f"{groups[(suite, case, tool)]['paired_elapsed_tool_over_cidrmerge']['median']:.3f}" for tool in active_tools[1:]]
        lines.append('| ' + case + ' | ' + ' | '.join(cells) + ' |')
    lines.append('')

lines += ['## Sample distributions', '',
          'Elapsed quartiles and full ranges are descriptive. No samples were removed.',
          'The machine-readable summary retains every sample, RSS quartiles, CPU time, output bytes, and hashes.', '',
          '| Suite | Corpus | Tool | n | Elapsed p25–p75 (s) | Elapsed min–max (s) | RSS min–max (MiB) |',
          '|---|---|---|---:|---:|---:|---:|']
for suite in ['split', 'native']:
    for case in cases:
        for tool in tools:
            row = groups.get((suite, case, tool))
            if row is None:
                continue
            t, m = row['elapsed_seconds'], row['peak_rss_mib']
            lines.append(f"| {suite} | {case} | {tool} | {row['samples']} | {t['p25']:.3f}–{t['p75']:.3f} | {t['min']:.3f}–{t['max']:.3f} | {m['min']:.1f}–{m['max']:.1f} |")
with (root / 'control/tables.md').open('x') as output:
    output.write('\n'.join(lines) + '\n')
print('Wrote tables.md from all measured samples.')
