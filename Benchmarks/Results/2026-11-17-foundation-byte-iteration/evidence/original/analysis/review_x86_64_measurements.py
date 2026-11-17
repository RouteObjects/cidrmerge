from pathlib import Path
import datetime,json,statistics,math
r=Path('$EXPERIMENT')
summary=json.loads((r/'x86_64/local-audits/summary.json').read_text());assert summary['passed'];rows=[];counts={}
index=json.loads((r/'analysis/x86_64-report-index.json').read_text())
assert index['audit_rows']==summary['audit_rows']
for a in summary['audit_rows']:
    result=json.loads((r/a['receipt']).read_text());assert result['passed'] and result['result']['passed'];v=result['result'];assert not v['postprocessing_recovered']
    assert v['measured_samples']==a['measured_samples'] and v['warmups']==a['warmups']
    assert v['phase']==a['phase'] and v['comparison']=='B-vs-P' and v['artifact_profile']=='ordinary'
    assert sum(2*len(z['pairs']) for z in v['recomputed'].values())==a['measured_samples']
    phase=counts.setdefault(a['phase'],{'measured_samples':0,'warmups':0});phase['measured_samples']+=a['measured_samples'];phase['warmups']+=a['warmups']
    for case,values in v['recomputed'].items():
        for metric,field in [('elapsed','elapsed_ns'),('cpu','cpu_seconds'),('rss','peak_rss_bytes')]:
            changes=[]
            for p in values['pairs']:
                calculated=100*(p['C'][field]/p['B'][field]-1) if p['B'][field] else None
                observed=p[metric+'_change_pct']
                assert calculated==observed or (calculated is not None and observed is not None and math.isclose(calculated,observed,rel_tol=1e-10,abs_tol=1e-10)),(case,metric)
                if observed is not None:changes.append(observed)
            assert values['paired_change_medians'][metric]==(statistics.median(changes) if changes else None)
            assert values['paired_change_ranges'][metric]==([min(changes),max(changes)] if changes else None)
        absolute={variant:{'elapsed_seconds':statistics.median(p[variant]['elapsed_ns']/1e9 for p in values['pairs']),'cpu_seconds':statistics.median(p[variant]['cpu_seconds'] for p in values['pairs']),'peak_rss_bytes':statistics.median(p[variant]['peak_rss_bytes'] for p in values['pairs'])} for variant in ['B','C']};absolute['P']=absolute.pop('C')
        rows.append({'kind':a['kind'],'profile':'ordinary','comparison':'B-vs-P','phase':a['phase'],'case':case,'n':len(values['pairs']),'absolute_medians':absolute,'paired_change_medians':values['paired_change_medians'],'paired_change_ranges':values['paired_change_ranges'],'all_elapsed_pairs_improved':all(p['elapsed_change_pct']<0 for p in values['pairs']),'elapsed_pairs_above_5_percent':sum(p['elapsed_change_pct']>5 for p in values['pairs']),'rss_pairs_above_5_percent':sum(p['rss_change_pct']>5 for p in values['pairs']),'audit_receipt':a['receipt']})
assert counts=={'primary':{'measured_samples':376,'warmups':44},'followup':{'measured_samples':48,'warmups':8}}
assert summary['audit_totals']==index['audit_totals']=={'phases':4,'measured_samples':424,'warmups':52}
assert len(rows)==26
repeated=[]
for row in rows:
    if row['phase']!='primary':continue
    follow=[q for q in rows if q['kind']==row['kind'] and q['case']==row['case'] and q['phase']=='followup']
    assert len(follow)<=1
    for metric in ['elapsed','rss']:
        if row['paired_change_medians'][metric]>5 and follow and follow[0]['paired_change_medians'][metric]>5:repeated.append({'kind':row['kind'],'case':row['case'],'metric':metric})
text=[x for x in rows if x['kind']=='throughput' and x['phase']=='primary' and x['case'].startswith('text-')];assert len(text)==12 and not repeated
record={'passed':True,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Metadata-only independent arithmetic extraction from the four locally passed x86 audits; phases separate, no new measurements, corpus hashing, or sample exclusions.','audits':4,'totals':counts,'measured_samples':424,'warmups':52,'row_count':len(rows),'rows':rows,'repeated_primary_followup_median_regressions_over5_percent':repeated,'text_primary_elapsed_median_range_percent':[min(x['paired_change_medians']['elapsed'] for x in text),max(x['paired_change_medians']['elapsed'] for x in text)],'text_primary_rss_median_range_percent':[min(x['paired_change_medians']['rss'] for x in text),max(x['paired_change_medians']['rss'] for x in text)],'limitations':['Ranges are per-pair extrema, not confidence intervals.','Searchbot file path is an unchanged control; mixed-sign changes do not establish a JSON speedup.','The +70.822% text-ranges/stats elapsed pair remains preserved; no outliers discarded.','Fixed primary-triggered follow-ups are nonrecursive.','No repeated above5% median regression is an inventory statement, not proof of equivalence.','Absolute medians and paired median changes answer different questions; ratios of absolute medians are not substituted for paired changes.']}
with (r/'analysis/x86_64-measurement-review.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
def fmt(row,metric):
    median=row['paired_change_medians'][metric];spread=row['paired_change_ranges'][metric]
    return 'n/a' if median is None else f'{median:+.3f}% [{spread[0]:+.3f}, {spread[1]:+.3f}]'
lines=['# Independent x86-64 measurement review','','All four phases passed local independent output, artifact, metric, sample-order, inventory and follow-up-selection audits. This review independently recalculates every paired percentage, median and extrema from the small audit metadata. Primary 376 measured/44 warmups; fixed file follow-ups 48/8; total 424 measured/52 warmups. No repeated primary/follow-up elapsed or RSS median regression above 5%.','','| Kind / case | Phase | n | B / P elapsed median (ms) | Paired elapsed median [min,max] | Paired CPU median [min,max] | Paired RSS median [min,max] |','|---|---|---:|---:|---|---|---|']
for row in rows:
    b=row['absolute_medians']['B']['elapsed_seconds']*1000;p=row['absolute_medians']['P']['elapsed_seconds']*1000
    lines.append(f'| {row["kind"]} / {row["case"]} | {row["phase"]} | {row["n"]} | {b:.3f} / {p:.3f} | {fmt(row,"elapsed")} | {fmt(row,"cpu")} | {fmt(row,"rss")} |')
lines += ['', 'All twelve text-file elapsed medians improve 0.559–15.332%, with matching CPU direction. The smallest range-derived change is modest and does not establish a general improvement for that case. Text RSS medians change −0.075% to +0.184%. Ten of twelve text configurations improve in every elapsed pair. Both text-stdin configurations improve in all six pairs, with paired medians −12.874% and −12.568%.', '', 'Four file configurations received fixed follow-ups. Mixed-noncanonical/no-stats retains its improvement (−15.332% primary, −15.789% follow-up). Ranges/stats changes from −0.559% primary to −4.784% follow-up, with all six follow-up pairs improved. Its +70.822% primary elapsed observation remains included. The two unchanged Searchbot/stats controls have follow-up medians −0.535% and +1.723%, with mixed-sign pairs; no general JSON speedup or sustained regression is established.', '', 'No startup elapsed/RSS primary pair crosses the 5% follow-up threshold, so no startup follow-up is required. The empty, version and 100-entry medians are near zero; the 10,000-entry paired elapsed median is −4.138%. CPU-only threshold crossings do not trigger the agreed elapsed/RSS rule.', '', 'Spreads are paired minima/maxima, not confidence intervals. Absolute median ratios can differ from paired median changes. Linux lifetime RSS retains the measurement method and inherited-parent-memory limitation; no correction or subtraction is introduced. No phase, candidate or platform is pooled.']
with (r/'analysis/x86_64-measurement-review.md').open('x') as f:f.write('\n'.join(lines)+'\n')
print(json.dumps({'passed':True,'rows':len(rows),'measured_samples':424,'warmups':52,'text_elapsed_range':record['text_primary_elapsed_median_range_percent'],'text_rss_range':record['text_primary_rss_median_range_percent'],'repeated':repeated}))
