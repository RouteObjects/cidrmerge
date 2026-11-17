#!/usr/bin/env python3
"""Render audited, unpooled benchmark summaries. Does not execute product binaries."""
import argparse
import csv
import json
from pathlib import Path

PLATFORMS = [('macos', 'macOS ARM64'), ('arm64', 'Linux ARM64'), ('x86_64', 'Linux x86-64')]
CASES = [
    f'{case}-{mode}'
    for case in ['text-ipv4-canonical', 'text-ipv6-canonical', 'text-mixed-noncanonical',
                 'text-mixed-addresses', 'text-mixed-ranges', 'text-mixed-overlap',
                 'searchbot-canonical', 'searchbot-noncanonical']
    for mode in ['no-stats', 'stats']
]


def pct(value):
    return 'n/a' if value is None else f'{value:+.2f}%'


def interval(row, metric):
    key = metric + '_change_pct_'
    return f"{pct(row[key+'median'])} [{pct(row[key+'min'])}, {pct(row[key+'max'])}]"


def label(case):
    return case.replace('text-', '').replace('-no-stats', ' / no stats').replace('-stats', ' / stats')


def run(root, data_dir, output, allow_partial):
    data = json.loads((data_dir / 'dataset.json').read_text())
    assert data['passed']
    assert data['complete_platform_set'] or allow_partial
    rows = data['summaries']
    output.mkdir(parents=True, exist_ok=False)
    indices = {(r['platform'], r['kind'], r['profile'], r['comparison'], r['phase'], r['case']): r for r in rows}
    assert len(indices) == len(rows)

    def phases_for(platform, kind, profile, comparison, case):
        matches = [r for r in rows if (r['platform'],r['kind'],r['profile'],r['comparison'],r['case'])
                   == (platform,kind,profile,comparison,case)]
        assert sum(r['phase'].startswith('primary') for r in matches) == 1
        assert sum(r['phase'].startswith('followup') for r in matches) <= 1
        assert all(r['phase'].startswith(('primary','followup')) for r in matches)
        return sorted(matches,key=lambda r:(not r['phase'].startswith('primary'),r['phase']))

    selected_platforms = [(p, title) for p, title in PLATFORMS if p in data['platforms']]
    for r in rows:
        assert r['n']==(20 if r['kind']=='startup' else 6), ('unexpected pair count',r)
    expected_direct = {
        ('throughput','ordinary'):set(CASES),
        ('stdin','ordinary'):{'searchbot-canonical-no-stats','searchbot-noncanonical-stats'},
        ('startup','ordinary'):{'empty-stdin','mixed-100','mixed-10000','version'},
        ('startup','release-style'):{'empty-stdin','mixed-100','mixed-10000','version'},
    }
    for platform,_ in selected_platforms:
        for (kind,profile),expected in expected_direct.items():
            actual={r['case'] for r in rows if r['platform']==platform and r['kind']==kind
                    and r['profile']==profile and r['comparison']=='B-vs-R3'
                    and r['phase'].startswith('primary')}
            assert actual==expected,('incomplete direct comparison',platform,kind,profile,actual,expected)
    retained = [r for r in rows if r['comparison'] == 'B-vs-R3']
    with (output / 'retained.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(retained)
    lines = ['# Retained prototype: direct baseline comparison', '',
             'All changes are paired `100 × (R3 / B − 1)`. Negative is lower elapsed time or memory. '
             'Brackets show the minimum and maximum paired change, not a confidence interval. '
             'Each throughput/stdin row has six pairs; each startup row has twenty. '
             'Follow-ups remain separate. Absolute medians are medians of observations, '
             'so their ratio can differ from the median paired change.', '']
    for platform, title in selected_platforms:
        lines += [f'## {title}: million-entry file input', '',
                  '| Case | B elapsed (s) | R3 elapsed (s) | Paired elapsed change [min, max] | B peak RSS (MiB) | R3 peak RSS (MiB) | Paired RSS change [min, max] |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        for case in CASES:
            for r in phases_for(platform,'throughput','ordinary','B-vs-R3',case):
                suffix = f" ({r['phase']})"
                lines.append(f"| {label(case)}{suffix} | {r['B_elapsed_seconds_median']:.4f} | {r['C_elapsed_seconds_median']:.4f} | {interval(r,'elapsed')} | {r['B_rss_bytes_median']/2**20:.2f} | {r['C_rss_bytes_median']/2**20:.2f} | {interval(r,'rss')} |")
        for kind, profile, heading in [('stdin', 'ordinary', 'large redirected Searchbot stdin'), ('startup', 'release-style', 'shipping-style warm-cache startup')]:
            subset = [r for r in retained if r['platform']==platform and r['kind']==kind and r['profile']==profile]
            lines += ['', f'### {title}: {heading}', '',
                      '| Case / phase | B elapsed (ms) | R3 elapsed (ms) | Paired elapsed change [min, max] | B / R3 peak RSS (MiB) | Paired RSS change [min, max] |',
                      '|---|---:|---:|---:|---:|---:|']
            for r in sorted(subset, key=lambda r:(r['case'],not r['phase'].startswith('primary'),r['phase'])):
                lines.append(f"| {r['case']} / {r['phase']} | {r['B_elapsed_seconds_median']*1000:.3f} | {r['C_elapsed_seconds_median']*1000:.3f} | {interval(r,'elapsed')} | {r['B_rss_bytes_median']/2**20:.2f} / {r['C_rss_bytes_median']/2**20:.2f} | {interval(r,'rss')} |")
    lines += ['', 'CPU time, ordinary startup, all intermediate variants, and individual pairs are retained in the companion CSV files. '
              'macOS CPU time is quantized to 0.01 seconds; tiny-call CPU percentages are not useful. '
              'The Linux fork/exec measurement harness can impose a peak-RSS floor on tiny calls; '
              'equal startup RSS is not evidence of equal application-only memory.', '']
    (output / 'RETAINED.md').write_text('\n'.join(lines))

    # Every positive >5% observation is accounted for, without discarding outliers.
    regression_lines = ['# Regression observations and separate follow-ups', '',
                        'The trigger was any paired elapsed-time or RSS increase above 5%, not only a median increase. '
                        'Every triggered primary case gets a separate fixed-size follow-up. Primary and follow-up values are never pooled. '
                        '“Repeated >5% median” below means both phase medians exceed 5%; it is a descriptive rule, not a significance test.', '',
                        'Migration-only regressions are evaluated separately from the retained R3 result. '
                        'The S2 borrowed-line implementation was rejected after repeatable text-throughput regressions. '
                        'Small/noisy startup changes need their absolute durations and spread considered; see RETAINED.md and the CSVs.', '']
    triggers = []
    for platform, title in selected_platforms:
        regression_lines += [f'## {title}', '',
                            '| Workload / comparison / profile | Case | Metric | Primary median [min, max] | Follow-up median [min, max] | Interpretation |',
                            '|---|---|---|---:|---:|---|']
        for r in rows:
            if r['platform'] != platform or not r['phase'].startswith('primary'):
                continue
            for metric in ['elapsed','rss']:
                if r[metric+'_change_pct_max'] <= 5:
                    continue
                matches = [f for f in phases_for(platform,r['kind'],r['profile'],r['comparison'],r['case'])
                           if f['phase'].startswith('followup')]
                assert len(matches)==1, ('missing or ambiguous triggered follow-up',r,metric)
                follow = matches[0]
                med, fmed = r[metric+'_change_pct_median'], follow[metric+'_change_pct_median']
                if med > 5 and fmed > 5:
                    interpretation = 'Repeated >5% median'
                elif med > 5 or fmed > 5:
                    interpretation = 'Not repeatable at >5%; mixed/noisy phases'
                elif med > 0 and fmed > 0:
                    interpretation = 'Both medians positive but ≤5%; inspect absolute size/spread'
                else:
                    interpretation = 'Triggered observation; no repeated positive median'
                regression_lines.append(f"| {r['kind']} / {r['comparison']} / {r['profile']} | {r['case']} | {metric} | {interval(r,metric)} ({r['phase']}) | {interval(follow,metric)} ({follow['phase']}) | {interpretation} |")
                triggers.append({'platform':platform, 'kind':r['kind'], 'profile':r['profile'], 'comparison':r['comparison'], 'case':r['case'], 'metric':metric, 'primary_phase':r['phase'], 'followup_phase':follow['phase'], 'primary_median_pct':med, 'followup_median_pct':fmed, 'interpretation':interpretation,'primary_trigger':True})
        additional=[]
        for follow in rows:
            if follow['platform']!=platform or not follow['phase'].startswith('followup'):
                continue
            primary=[r for r in phases_for(platform,follow['kind'],follow['profile'],follow['comparison'],follow['case'])
                     if r['phase'].startswith('primary')][0]
            for metric in ['elapsed','rss']:
                if follow[metric+'_change_pct_max']>5 and primary[metric+'_change_pct_max']<=5:
                    additional.append((primary,follow,metric))
        if additional:
            regression_lines += ['', '### Additional >5% observations first seen in follow-up', '',
                                 'These metrics did not trigger in the primary phase. The case was already selected '
                                 'for follow-up by its other metric. All follow-up observations remain preserved; '
                                 'the protocol does not recursively schedule a third phase.', '',
                                 '| Workload / comparison / profile | Case | Metric | Primary median [min, max] | Follow-up median [min, max] |',
                                 '|---|---|---|---:|---:|']
            for primary,follow,metric in additional:
                regression_lines.append(f"| {follow['kind']} / {follow['comparison']} / {follow['profile']} | {follow['case']} | {metric} | {interval(primary,metric)} ({primary['phase']}) | {interval(follow,metric)} ({follow['phase']}) |")
                triggers.append({'platform':platform,'kind':follow['kind'],'profile':follow['profile'],'comparison':follow['comparison'],'case':follow['case'],'metric':metric,'primary_phase':primary['phase'],'followup_phase':follow['phase'],'primary_median_pct':primary[metric+'_change_pct_median'],'followup_median_pct':follow[metric+'_change_pct_median'],'interpretation':'Additional >5% observation first seen in follow-up','primary_trigger':False})
    (output/'REGRESSIONS.md').write_text('\n'.join(regression_lines)+'\n')
    (output/'regression-observations.json').write_text(json.dumps(triggers,indent=2)+'\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
    for metric, metric_title in [('elapsed','Elapsed time'), ('rss','Peak resident memory')]:
        fig, axes = plt.subplots(1,len(selected_platforms),figsize=(max(13,5.5*len(selected_platforms)),9),sharey=True,squeeze=False)
        limits = [0.0]
        for ax,(platform,title) in zip(axes[0],selected_platforms):
            for y,case in enumerate(CASES):
                for r in phases_for(platform,'throughput','ordinary','B-vs-R3',case):
                    is_primary=r['phase'].startswith('primary')
                    offset,color,marker=(0.0,'#17638c','o') if is_primary else (0.22,'#bb5b16','D')
                    lo,mid,hi=[r[metric+'_change_pct_'+stat] for stat in ['min','median','max']]
                    limits += [lo,hi]
                    ax.errorbar(mid,y+offset,xerr=[[mid-lo],[hi-mid]],fmt=marker,color=color,
                                markersize=4.6,linewidth=1.1,capsize=2.2,
                                markerfacecolor=color if is_primary else 'white')
            ax.axvline(0,color='#777777',linewidth=.8)
            ax.set_title(title,pad=12)
            ax.grid(axis='x',color='#dddddd',linewidth=.6)
            ax.set_xlabel('Paired change (%) · lower is better')
            ax.set_yticks(range(len(CASES)),[label(c) for c in CASES])
        margin=max(1,(max(limits)-min(limits))*.06)
        for ax in axes[0]: ax.set_xlim(min(limits)-margin,max(limits)+margin)
        axes[0][0].invert_yaxis()
        fig.suptitle(f'{metric_title}: retained R3 vs baseline',fontsize=17,y=.99)
        fig.text(.5,.025,'Six alternating pairs per case; dots = paired median, whiskers = full min–max.\n'
                 'Blue = primary; hollow orange = separate triggered follow-up. No outliers removed.',ha='center',fontsize=10)
        fig.tight_layout(rect=(0,.065,1,.96))
        for extension in ['png','svg']:
            fig.savefig(output/f'retained-{metric}.{extension}',dpi=170)
        plt.close(fig)
    (output/'render.json').write_text(json.dumps({'complete_platform_set':data['complete_platform_set'],
        'platforms':data['platforms'],'source_dataset':str(data_dir.relative_to(root)/'dataset.json'),
        'regression_metric_triggers':len(triggers), 'passed':True},indent=2)+'\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args()
    run(args.root,args.root/args.data,args.root/args.output,args.allow_partial)
