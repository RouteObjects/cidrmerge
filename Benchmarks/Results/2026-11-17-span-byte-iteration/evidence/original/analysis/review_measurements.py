#!/usr/bin/env python3
"""Independently reconcile completed Data.span audit metadata without new measurements."""
from pathlib import Path
import argparse,csv,datetime,json,math,statistics

def require(condition,message):
    if not condition:raise ValueError(message)
def equivalent(a,b):return a==b or (a is not None and b is not None and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12))
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',required=True,type=Path);parser.add_argument('--platform',required=True,choices=['macos','arm64','x86_64']);parser.add_argument('--audit-summary',required=True,type=Path);parser.add_argument('--output-prefix',required=True,type=Path);args=parser.parse_args();root=args.root.resolve();summary=json.loads(args.audit_summary.read_text());require(summary['passed'],'Audit summary failed');rows=[];totals={'primary':{'measured_samples':0,'warmups':0},'followup':{'measured_samples':0,'warmups':0}};checks=0;seen=set();primary_cases={};follow_cases={};triggers={};phases=[]
    cases_by_kind={kind:{c['id'] for c in json.loads((root/'control'/name).read_text())['configs']} for kind,name in [('throughput','cases.json'),('stdin','stdin-cases.json')]}
    for a in summary['audit_rows']:
        phase=a['phase'];kind=a['kind'];require(phase in totals and kind in cases_by_kind,'Unexpected group or phase');key=(kind,phase);require(key not in seen,'Duplicate phase');seen.add(key)
        d=json.loads((root/a['receipt']).read_text());require(d['passed'] and d['result']['passed'],'Phase audit failed');v=d['result'];require(not v['postprocessing_recovered'],'Unexpected recovery');require(v['phase']==phase and v['comparison']=='B-vs-P' and v['artifact_profile']=='ordinary' and not v['startup'],'Unexpected comparison/profile')
        require(v['rounds']==6,'Wrong pair count');require(v['role_mapping']=={'B':'B','C':'P'},'Wrong role mapping');require(v['measured_samples']==a['measured_samples'] and v['warmups']==a['warmups'],'Audit inventory mismatch');require(v['measured_samples']==len(v['recomputed'])*12 and v['warmups']==len(v['recomputed'])*2,'Config totals mismatch')
        for k in totals[phase]:totals[phase][k]+=v[k]
        (primary_cases if phase=='primary' else follow_cases)[kind]=set(v['recomputed']);triggers.setdefault(kind,set());phases.append({'kind':kind,'phase':phase,'receipt':a['receipt'],'measured_samples':v['measured_samples'],'warmups':v['warmups']})
        for case,values in v['recomputed'].items():
            obs=values['pairs'];require(len(obs)==6 and {p['round'] for p in obs}==set(range(1,7)),'Pair inventory mismatch')
            for metric,field in [('elapsed','elapsed_ns'),('cpu','cpu_seconds'),('rss','peak_rss_bytes')]:
                changes=[]
                for p in obs:
                    calculated=(p['C'][field]/p['B'][field]-1)*100 if p['B'][field] else None;observed=p[metric+'_change_pct'];require(equivalent(calculated,observed),'Pair percentage mismatch');checks+=1
                    if observed is not None:changes.append(observed)
                require(values['paired_change_medians'][metric]==(statistics.median(changes) if changes else None),'Paired median mismatch');require(values['paired_change_ranges'][metric]==([min(changes),max(changes)] if changes else None),'Paired range mismatch');checks+=2
            if phase=='primary' and any(p['elapsed_change_pct']>5 or p['rss_change_pct']>5 for p in obs):triggers[kind].add(case)
            absolute={role:{'elapsed_seconds':statistics.median(p[src]['elapsed_ns']/1e9 for p in obs),'cpu_seconds':statistics.median(p[src]['cpu_seconds'] for p in obs),'peak_rss_bytes':statistics.median(p[src]['peak_rss_bytes'] for p in obs)} for role,src in [('B','B'),('P','C')]}
            rows.append({'kind':kind,'profile':'ordinary','comparison':'B-vs-P','phase':phase,'case':case,'n':6,'absolute_medians':absolute,'paired_change_medians':values['paired_change_medians'],'paired_change_ranges':values['paired_change_ranges'],'all_elapsed_pairs_improved':all(p['elapsed_change_pct']<0 for p in obs),'elapsed_pairs_above_5_percent':sum(p['elapsed_change_pct']>5 for p in obs),'rss_pairs_above_5_percent':sum(p['rss_change_pct']>5 for p in obs),'audit_receipt':a['receipt']})
    require(primary_cases==cases_by_kind,'Primary case inventory differs from selected protocol');require(totals['primary']=={'measured_samples':120,'warmups':20},'Primary totals mismatch')
    for kind in cases_by_kind:require(follow_cases.get(kind,set())==triggers[kind],'Missing or unsolicited followup')
    repeated=[]
    for row in rows:
        if row['phase']!='primary':continue
        follows=[x for x in rows if x['kind']==row['kind'] and x['case']==row['case'] and x['phase']=='followup'];require(len(follows)<=1,'Duplicate followup case')
        for metric in ['elapsed','rss']:
            if follows and row['paired_change_medians'][metric]>5 and follows[0]['paired_change_medians'][metric]>5:repeated.append({'kind':row['kind'],'case':row['case'],'metric':metric,'primary_median':row['paired_change_medians'][metric],'followup_median':follows[0]['paired_change_medians'][metric]})
    text=[x for x in rows if x['kind']=='throughput' and x['phase']=='primary'];require(len(text)==8,'Wrong text count')
    record={'passed':True,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':args.platform,'scope':'Metadata-only independent arithmetic and inventory reconciliation from passed phase audits. No new product execution, measurement, corpus hashing, or excluded observations.','audits':len(phases),'phases':phases,'totals':totals,'measured_samples':sum(x['measured_samples'] for x in totals.values()),'warmups':sum(x['warmups'] for x in totals.values()),'row_count':len(rows),'rows':rows,'numeric_checks':checks,'primary_trigger_configs':{k:sorted(v) for k,v in triggers.items()},'repeated_primary_followup_median_regressions_over5_percent':repeated,'text_primary_elapsed_median_range_percent':[min(x['paired_change_medians']['elapsed'] for x in text),max(x['paired_change_medians']['elapsed'] for x in text)],'text_primary_rss_median_range_percent':[min(x['paired_change_medians']['rss'] for x in text),max(x['paired_change_medians']['rss'] for x in text)],'limitations':['Paired min/max ranges are observed extrema, not confidence intervals.','Ratios of absolute medians may differ from paired median changes.','Fixed primary-triggered followups are separate and nonrecursive.','Small/noisy changes require cautious interpretation; absence of a repeated median regression is not proof of equivalence.','No startup/Searchbot timing or static shipping-artifact comparison was performed.']}
    args.output_prefix.parent.mkdir(parents=True,exist_ok=True)
    with args.output_prefix.with_suffix('.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    def fmt(row,metric):
        mid=row['paired_change_medians'][metric];spread=row['paired_change_ranges'][metric]
        return 'n/a' if mid is None else f'{mid:+.3f}% [{spread[0]:+.3f}, {spread[1]:+.3f}]'
    lines=[f'# Independent {args.platform} Data.span measurement review','','All listed phase audits passed. This review recalculates pair percentages and statistics, verifies all selected primary configurations and exactly the required fixed follow-ups, and keeps every phase separate.', '',f"Primary 120 measured / 20 warmups; follow-ups {totals['followup']['measured_samples']}/{totals['followup']['warmups']}; total {record['measured_samples']}/{record['warmups']}.",'','| Kind / case | Phase | n | B / P elapsed median (ms) | Paired elapsed median [min,max] | Paired CPU median [min,max] | Paired RSS median [min,max] |','|---|---|---:|---:|---|---|---|']
    for row in rows:
        b=row['absolute_medians']['B']['elapsed_seconds']*1000;p=row['absolute_medians']['P']['elapsed_seconds']*1000
        lines.append(f'| {row["kind"]} / {row["case"]} | {row["phase"]} | 6 | {b:.3f} / {p:.3f} | {fmt(row,"elapsed")} | {fmt(row,"cpu")} | {fmt(row,"rss")} |')
    lines+=['',f'Repeated primary/follow-up elapsed or RSS median increases above 5%: {json.dumps(repeated)}.','','Spreads are complete per-pair extrema. All observations remain included. Interpret small or noisy changes as inconclusive; no primary/follow-up or cross-platform pooling.']
    with args.output_prefix.with_suffix('.md').open('x') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({k:record[k] for k in ['passed','platform','audits','row_count','measured_samples','warmups','text_primary_elapsed_median_range_percent','text_primary_rss_median_range_percent','repeated_primary_followup_median_regressions_over5_percent']}))
if __name__=='__main__':main()
