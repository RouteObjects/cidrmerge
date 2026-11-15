#!/usr/bin/env python3
"""Separate six-pair investigation of primary-run pairs above 5%; never pooled."""
import argparse,statistics
from common import ROOT,CASES,NATIVE_CASES,digest,load,stamp,write_json,host_snapshot
import linux_runner as runner
from run_matched import validate

def main():
 p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();assert a.name.startswith('regressions-') and '/' not in a.name
 out=ROOT/'followups'/a.name;gate=load(out/'space-gate.json');assert gate['passed']
 selection=load(out/'selection.json');selected={(s['suite'],s['case']) for s in selection['cases']}
 assert selected and selection['primary_summary_sha256']==digest(ROOT/'measurements/summary.json')
 assert not (out/'measurements').exists();measure=out/'measurements';measure.mkdir()
 validation=validate();refs=load(ROOT/'control/reference.json')['expected'];rows=[];warmups=[]
 write_json(out/'start.json',{'at':stamp(),'validation':validation,'host':host_snapshot(),'script_sha256':digest(__file__),'child_harness_sha256':digest(ROOT/'control/linux_runner.py'),'primary_summary_sha256':selection['primary_summary_sha256'],'separate_followup_not_pooled':True})
 try:
  for suite,allcases in [('split',CASES),('native',NATIVE_CASES)]:
   cases=[c for c in allcases if (suite,c) in selected]
   if not cases:continue
   for iteration in range(7):
    order=['B','C'] if iteration==0 or iteration%2 else ['C','B'];offset=max(0,iteration-1)%len(cases)
    for case in cases[offset:]+cases[:offset]:
     for tool in order:
      phase='warmup' if not iteration else f'round-{iteration:02}'
      row={'round':iteration,'order':order,**runner.run_one(suite,case,tool,measure/suite/phase/case/tool,refs[suite][case])}
      (rows if iteration else warmups).append(row)
      print(__import__('json').dumps({'suite':suite,'case':case,'tool':tool,'round':iteration,'elapsed_s':row['elapsed_ns']/1e9,'peak_mib':row['peak_rss_bytes']/1048576}),flush=True)
  assert len(rows)==12*len(selected) and len(warmups)==2*len(selected)
  groups=[];comparisons=[]
  for suite,case in sorted(selected):
   by={v:{x['round']:x for x in rows if (x['suite'],x['case'],x['tool'])==(suite,case,v)} for v in ['B','C']}
   for v,index in by.items():
    assert sorted(index)==list(range(1,7));values=list(index.values());elapsed=[x['elapsed_ns']/1e9 for x in values];rss=[x['peak_rss_bytes']/1048576 for x in values]
    groups.append({'suite':suite,'case':case,'tool':v,'n':6,'elapsed_median_s':statistics.median(elapsed),'elapsed_min_s':min(elapsed),'elapsed_max_s':max(elapsed),'peak_rss_median_mib':statistics.median(rss),'peak_rss_min_mib':min(rss),'peak_rss_max_mib':max(rss),'cpu_median_s':statistics.median(x['cpu_seconds'] for x in values)})
   pairs=[]
   for i in range(1,7):
    b,c=by['B'][i],by['C'][i];assert b['order']==c['order']
    pairs.append({'round':i,'order':b['order'],'elapsed_change_pct':(c['elapsed_ns']/b['elapsed_ns']-1)*100,'rss_change_pct':(c['peak_rss_bytes']/b['peak_rss_bytes']-1)*100,'elapsed_difference_s':(c['elapsed_ns']-b['elapsed_ns'])/1e9,'rss_difference_mib':(c['peak_rss_bytes']-b['peak_rss_bytes'])/1048576})
   comparisons.append({'suite':suite,'case':case,'n_pairs':6,'paired_elapsed_change_median_pct':statistics.median(x['elapsed_change_pct'] for x in pairs),'paired_elapsed_change_min_pct':min(x['elapsed_change_pct'] for x in pairs),'paired_elapsed_change_max_pct':max(x['elapsed_change_pct'] for x in pairs),'paired_rss_change_median_pct':statistics.median(x['rss_change_pct'] for x in pairs),'paired_rss_difference_median_mib':statistics.median(x['rss_difference_mib'] for x in pairs),'pairs':pairs})
  assert validate()==validation
  write_json(out/'summary.json',{'passed':True,'completed_at':stamp(),'selected_cases':selection['cases'],'primary_summary_sha256':selection['primary_summary_sha256'],'separate_followup_not_pooled':True,'samples':rows,'warmup_samples':warmups,'measured_samples':len(rows),'excluded_warmup_samples':len(warmups),'groups':groups,'comparisons':comparisons,'no_samples_removed_or_retried':True,'all_outputs_retained':True,'all_outputs_match_original_independent_coverage':True,'host_after':host_snapshot()})
 except BaseException as e:
  write_json(out/'failed.json',{'at':stamp(),'error':repr(e),'completed_measured_samples':len(rows),'completed_warmups':len(warmups),'no_retry_performed':True});raise
if __name__=='__main__':main()
