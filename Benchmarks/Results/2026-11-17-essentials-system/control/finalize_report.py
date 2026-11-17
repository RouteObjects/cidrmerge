#!/usr/bin/env python3
"""Fill final report tables from independently audited metadata; never time binaries."""
import argparse
import json
from pathlib import Path

PLATFORMS=[('macos','macOS ARM64'),('arm64','Linux ARM64'),('x86_64','Linux x86-64')]


def range_pct(rows,key):
    values=[r[key] for r in rows]
    return f'{min(values):+.1f}% to {max(values):+.1f}%'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--data',default='analysis/report-data-final-01')
    parser.add_argument('--output',default='analysis/RESULTS-final.md')
    args=parser.parse_args()
    root=args.root
    d=json.loads((root/args.data/'dataset.json').read_text())
    assert d['passed'] and d['complete_platform_set']
    assert set(d['platforms'])=={p for p,_ in PLATFORMS}
    artifacts=json.loads((root/'analysis/report-drafts/ARTIFACTS.json').read_text())
    draft=(root/'analysis/RESULTS-draft.md').read_text()
    draft=draft.replace('**Draft: awaiting final x86-64 measurements, audits, and evidence export.**',
                        '**Complete prototype: R3 retained; S2 rejected. All requested platform suites and matched measurement phases are preserved and audited.**')
    result=['The following ranges span the per-case paired medians, not the individual sample spread. '
            'Each primary case has six alternating pairs; the linked detailed tables and charts retain all spreads and separate follow-ups. '
            'Negative means lower elapsed time or RSS.', '',
            '| Platform | Text elapsed, 12 configurations | Text peak RSS, 12 configurations | Named-file Searchbot elapsed, 4 configurations |',
            '|---|---:|---:|---:|']
    for platform,title in PLATFORMS:
        rows=[r for r in d['summaries'] if r['platform']==platform and r['kind']=='throughput'
              and r['comparison']=='B-vs-R3' and r['profile']=='ordinary' and r['phase'].startswith('primary')]
        text=[r for r in rows if r['case'].startswith('text-')]
        searchbot=[r for r in rows if r['case'].startswith('searchbot-')]
        assert len(text)==12 and len(searchbot)==4
        result.append(f"| {title} | {range_pct(text,'elapsed_change_pct_median')} | {range_pct(text,'rss_change_pct_median')} | {range_pct(searchbot,'elapsed_change_pct_median')} |")
    result += ['', '![Direct retained-candidate elapsed changes](retained-elapsed.png)', '',
               '![Direct retained-candidate peak-RSS changes](retained-rss.png)']
    draft=draft.replace('FINAL RESULTS TABLE PENDING.','\n'.join(result))
    size=['| Platform | Shipping-style stripped B | Shipping-style stripped R3 | Change |',
          '|---|---:|---:|---:|']
    for platform,title in PLATFORMS:
        a=artifacts['platforms'][platform]['artifacts']['shipping_stripped']
        b,c=a['B']['bytes'],a['R3']['bytes']
        assert b>0 and c>0
        size.append(f'| {title} | {b:,} bytes | {c:,} bytes | {(c/b-1)*100:+.2f}% |')
    size += ['', 'See [ARTIFACTS.md](ARTIFACTS.md) for separately stripped ordinary executables, '
             'runtime-library accounting, exact identities, and the startup-RSS method control.']
    draft=draft.replace('SHIPPING AND ORDINARY SIZE TABLES PENDING.','\n'.join(size))
    qualification=['| Platform / compiler | B Debug / Release | R3 Debug / Release | R3 CLI differential | R3 expanded I/O differential |',
                   '|---|---:|---:|---:|---:|']
    for platform,title in PLATFORMS:
        index=json.loads((root/f'analysis/{platform}-report-index.json').read_text())
        q=index['qualification']; b=q['B']['tests']; c=q['R3']['tests']
        assert q['R3']['final_validation']['passed']
        counts=lambda tests:f"{tests['debug']['swift_testing_count']} / {tests['release']['swift_testing_count']}"
        qualification.append(f"| {title} / 6.4.2 | {counts(b)} | {counts(c)} | {q['R3']['standard_differential']['cases']} cases | {q['R3']['io_differential']['cases']} cases |")
    qualification.append('| Linux ARM64 / 6.2.4 floor | Not repeated in this floor gate | 95 / 95 | Separate helper compatibility probes | Existing R3 suite |')
    qualification += ['', 'All counts above passed. E4 has 95 tests and S2 has 96 tests in each '
                      'Swift 6.4.2 Debug/Release platform suite; S2 also has separate 6.2.4 floor evidence. '
                      'Those variant results remain separate from retained R3.']
    draft=draft.replace('QUALIFICATION TABLE PENDING.','\n'.join(qualification))
    counts=['| Platform | Passed independent audit phases | Measured observations | Excluded warmups |',
            '|---|---:|---:|---:|']
    for platform,title in PLATFORMS:
        q=d['reconciliation'][platform]
        counts.append(f"| {title} | {q['phases']:,} | {q['measured_samples']:,} | {q['warmups']:,} |")
    q=d['totals']
    counts.append(f"| Total | {q['phases']:,} | {q['measured_samples']:,} | {q['warmups']:,} |")
    counts += ['', 'These totals include intermediate variants, direct retained comparisons, startup, '
              'stdin, and all prescribed follow-ups. Warmups are excluded from summary statistics. '
              'Compatibility probes and method controls are not counted as performance observations.']
    draft=draft.replace('AUDIT COUNT TABLE PENDING.','\n'.join(counts))
    target=root/args.output
    with target.open('x') as f:
        f.write(draft)
    print(json.dumps({'output':args.output,'tables_completed':True,'requires_final_narrative_review':True}))


if __name__=='__main__':
    main()
