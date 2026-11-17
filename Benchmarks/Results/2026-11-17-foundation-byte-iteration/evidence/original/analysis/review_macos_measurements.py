from pathlib import Path
import datetime,json,statistics
r=Path('$EXPERIMENT')
summary=json.loads((r/'macos/audits-01/summary.json').read_text());assert summary['passed']
rows=[]
for a in summary['audit_rows']:
    result=json.loads((r/a['receipt']).read_text());assert result['passed']
    for case,values in result['result']['recomputed'].items():
        absolute={variant:{'elapsed_seconds':statistics.median(p[variant]['elapsed_ns']/1e9 for p in values['pairs']),'cpu_seconds':statistics.median(p[variant]['cpu_seconds'] for p in values['pairs']),'peak_rss_bytes':statistics.median(p[variant]['peak_rss_bytes'] for p in values['pairs'])} for variant in ['B','C']}
        absolute['P']=absolute.pop('C')
        rows.append({'kind':a['kind'],'profile':'ordinary','comparison':'B-vs-P','phase':a['phase'],'case':case,'n':len(values['pairs']),'absolute_medians':absolute,'paired_change_medians':values['paired_change_medians'],'paired_change_ranges':values['paired_change_ranges'],'all_elapsed_pairs_improved':all(p['elapsed_change_pct']<0 for p in values['pairs']),'elapsed_pairs_above_5_percent':sum(p['elapsed_change_pct']>5 for p in values['pairs']),'rss_pairs_above_5_percent':sum(p['rss_change_pct']>5 for p in values['pairs']),'audit_receipt':a['receipt']})
repeated=[]
for row in rows:
    if not row['phase'].startswith('primary'):continue
    follow=[q for q in rows if q['kind']==row['kind'] and q['case']==row['case'] and q['phase'].startswith('followup')]
    for metric in ['elapsed','rss']:
        if row['paired_change_medians'][metric]>5 and follow and follow[0]['paired_change_medians'][metric]>5:
            repeated.append({'kind':row['kind'],'case':row['case'],'metric':metric})
text=[x for x in rows if x['kind']=='throughput' and x['phase']=='primary' and x['case'].startswith('text-')]
assert len(text)==12
record={'passed':True,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Metadata-only extraction from independently passed Mac audits; phases are separate, no new measurement or sample exclusion.','audits':5,'totals':summary['totals'],'measured_samples':548,'warmups':54,'row_count':len(rows),'rows':rows,'repeated_primary_followup_median_regressions_over5_percent':repeated,'text_primary_elapsed_median_range_percent':[min(x['paired_change_medians']['elapsed'] for x in text),max(x['paired_change_medians']['elapsed'] for x in text)],'text_primary_rss_median_range_percent':[min(x['paired_change_medians']['rss'] for x in text),max(x['paired_change_medians']['rss'] for x in text)],'limitations':['Ranges are per-pair extrema, not confidence intervals.','Startup CPU percentages are undefined at native timing resolution; retain null values.','Searchbot named-file path is an unchanged control; small mixed-sign changes are inconclusive.','Follow-up observations above5% do not trigger a recursive third phase; all values are retained.','No repeated above5% median regression is an inventory statement, not statistical proof of equivalence.']}
assert not repeated
out=r/'analysis/macos-measurement-review.json'
with out.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
def fmt(row,metric):
    median=row['paired_change_medians'][metric];spread=row['paired_change_ranges'][metric]
    return 'n/a' if median is None else f'{median:+.3f}% [{spread[0]:+.3f}, {spread[1]:+.3f}]'
lines=['# Independent Mac measurement review','', 'All five phases passed independent output/hash, ordering, metric and inventory audits. Primary totals are376 measured/44warmups; follow-ups add172/10, for548 measured/54warmups. No primary/follow-up elapsed or RSS median regression above5% repeats. All phases and observations remain separate.','', '| Kind / case | Phase | n | B / P elapsed median (ms) | Paired elapsed median [min,max] | Paired CPU median [min,max] | Paired RSS median [min,max] |','|---|---|---:|---:|---|---|---|']
for row in rows:
    b=row['absolute_medians']['B']['elapsed_seconds']*1000;p=row['absolute_medians']['P']['elapsed_seconds']*1000
    lines.append(f'| {row["kind"]} / {row["case"]} | {row["phase"]} | {row["n"]} | {b:.3f} / {p:.3f} | {fmt(row,"elapsed")} | {fmt(row,"cpu")} | {fmt(row,"rss")} |')
lines += ['', 'Text-file primary elapsed medians improve3.596–26.309%; IPv4 canonical/no-stats is202.789→158.789ms, paired median−21.719%, and all six pairs improve. Eleven of twelve text configurations improve in every pair; mixed-ranges/stats includes one+0.675% pair. Text RSS median changes are−0.699% to+1.745%.', '', 'The unchanged Searchbot control triggering a follow-up has median elapsed+0.284% in primary and+0.285% in follow-up, despite individual+5.382% and+6.910% observations. Startup has broad mixed-sign spreads; all four received their fixed20-pair follow-ups. These small startup/control changes are inconclusive. No third phase was run or required by the frozen protocol.', '', 'The strongest individual apparent improvement (mixed-addresses/no-stats,−52.688%) remains included; it is not treated as a general speedup claim. CPU improves on all twelve text-file medians, supporting a real byte-iteration effect while preserving the reported elapsed spread.', '', 'All intervals are paired minima/maxima, not confidence intervals. Startup CPU ratios remain unavailable because of accounting resolution. The machine-readable companion includes exact audit paths, absolute medians, all spreads and regression flags.']
(r/'analysis/macos-measurement-review.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'passed':True,'rows':len(rows),'repeated_regressions':repeated,'text_elapsed_median_range':record['text_primary_elapsed_median_range_percent']}))
