#!/usr/bin/env python3
"""Export audited paired measurements without pooling primary and follow-up phases."""
import argparse,csv,hashlib,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--x86-data-root',type=Path);a=p.parse_args();root=a.root.resolve();out=a.output.resolve();assert not out.exists()
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
casefile=root/'downstream/shared/control/cases.json';cases={x['id']:x for x in json.loads(casefile.read_text())['configs']};sources={str(casefile.relative_to(root)):sha(casefile)};rows=[];pairrows=[];counts={}
for platform in ['macos','arm64','x86_64']:
 auditbase=root/'downstream'/platform;base=a.x86_data_root.resolve() if platform=='x86_64' and a.x86_data_root else auditbase;driver=base/'measurements-01/driver-summary.json';assert json.loads(driver.read_text())['passed'];sources[str(driver.relative_to(root))]=sha(driver);counts[platform]={'primary_measured':0,'primary_warmups':0,'followup_measured':0,'followup_warmups':0}
 for group in ['original','scale','sparse']:
  for phase in ['primary','followup']:
   path=base/'measurements-01'/group/phase/'summary.json'
   if not path.exists():assert phase=='followup';continue
   j=json.loads(path.read_text());assert j['passed'] and j['freeze_unchanged'];audit=auditbase/'audits-01'/(group+'-'+phase+'.json');aj=json.loads(audit.read_text());assert aj['passed'] is True
   for src in [path,audit]:sources[str(src.relative_to(root))]=sha(src)
   counts[platform][phase+'_measured']+=j['measured_samples'];counts[platform][phase+'_warmups']+=j['warmups']
   for case_id,result in j['pairs'].items():
    case=cases[case_id];pairs=result['pairs'];assert len(pairs)==6 and {x['round'] for x in pairs}==set(range(1,7))
    row={'platform':platform,'group':group,'phase':phase,'case':case_id,'input_entries':case['entries'],'processes_per_observation':len(case['parts']),'pairs':6,'elapsed_or_rss_paired_median_above_5pct':case_id in j['followup_required']}
    for metric,field,scale in [('elapsed_seconds','elapsed_ns',1e9),('cpu_seconds','cpu_seconds',1),('rss_mib','peak_rss_bytes',1024**2)]:
     for variant in ['B','C']:row[variant+'_'+metric+'_median']=statistics.median(pair[variant][field] for pair in pairs)/scale
    for metric in ['elapsed','cpu','rss']:
     row[metric+'_paired_median_pct']=result['paired_change_medians'][metric];limits=result['paired_change_ranges'][metric]
     row[metric+'_paired_min_pct']=limits[0] if limits else None;row[metric+'_paired_max_pct']=limits[1] if limits else None
    rows.append(row)
    for pair in pairs:
     pr={'platform':platform,'group':group,'phase':phase,'case':case_id,'round':pair['round']}
     for variant in ['B','C']:
      for field,value in pair[variant].items():pr[variant+'_'+field]=value
     for metric in ['elapsed','cpu','rss']:pr[metric+'_change_pct']=pair[metric+'_change_pct']
     pairrows.append(pr)
 assert counts[platform]['primary_measured']==300 and counts[platform]['primary_warmups']==50
out.mkdir(parents=True)
for filename,data in [('summaries.csv',rows),('pairs.csv',pairrows)]:
 with (out/filename).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
with (out/'analysis.json').open('x') as f:json.dump({'passed':True,'counts':counts,'source_hashes':sources,'script_sha256':sha(Path(__file__)),'summaries':rows,'scope':'Ordinary Swift6.4.2 release binaries; within-platform B/C comparisons only; excluded warmups and separate follow-ups remain distinct.'},f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'counts':counts,'summary_rows':len(rows),'paired_rows':len(pairrows)}))
