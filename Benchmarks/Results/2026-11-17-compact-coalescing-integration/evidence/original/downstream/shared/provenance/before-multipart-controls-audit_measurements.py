#!/usr/bin/env python3
"""Independent evidence audit; does not import a runner or execute product binaries."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,re,statistics,traceback
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--map',action='append',default=[]);a=p.parse_args();a.run=a.run.resolve();mapping=[]
for item in a.map:
 old,new=item.split('=',1);mapping.append((old.rstrip('/'),new.rstrip('/')))
mapping.sort(key=lambda x:len(x[0]),reverse=True)
def path(value):
 text=str(value)
 for old,new in mapping:
  if text==old or text.startswith(old+'/'):return Path(new+text[len(old):])
 return Path(text)
def load(p):return json.loads(Path(p).read_text())
def sha(p):
 before=Path(p).stat()
 with Path(p).open('rb') as f:value=hashlib.file_digest(f,'sha256').hexdigest()
 after=Path(p).stat();fields=['st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns'];assert tuple(getattr(before,x) for x in fields)==tuple(getattr(after,x) for x in fields),'File changed during read';return value
def equal(x,y):
 with Path(x).open('rb') as a,Path(y).open('rb') as b:
  while True:
   left=a.read(1024*1024);right=b.read(1024*1024)
   if left!=right:return False
   if not left:return True
def close(x,y):assert math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12),(x,y)
def compare(x,y):
 if isinstance(x,dict):assert set(x)==set(y),(set(x),set(y));[compare(x[k],y[k]) for k in x]
 elif isinstance(x,list):assert len(x)==len(y);[compare(i,j) for i,j in zip(x,y)]
 elif isinstance(x,(float,int)) and not isinstance(x,bool):close(x,y)
 else:assert x==y,(x,y)
result={'passed':False,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run':str(a.run),'path_mapping':mapping,'auditor_sha256':sha(Path(__file__))};assert not a.output.exists()
try:
 frozen=load(a.run/'freeze.json');summary=load(a.run/'summary.json');assert summary['passed'] and summary['freeze_unchanged'];assert path(frozen['output'])==a.run;cases=frozen['configs'];assert cases and len({x['id'] for x in cases})==len(cases);assert all(x['group']==summary['group'] for x in cases)
 for name,digest in frozen['files'].items():assert sha(path(name))==digest,('Frozen artifact mismatch',name)
 all_cases=load(path(Path(frozen['shared'])/'control/cases.json'))['configs'];wanted=[x for x in all_cases if x['group']==summary['group'] and x['id'] in {c['id'] for c in cases}];assert wanted==cases,'Frozen cases do not match the immutable case specification'
 if a.run.name=='primary':assert cases==[x for x in all_cases if x['group']==summary['group']],'Primary group omitted a configuration'
 if a.run.name=='followup':
  primary=load(a.run.parent/'primary/summary.json');assert primary['passed'];assert [x['id'] for x in cases]==primary['followup_required'],'Follow-up group differs from primary paired-median triggers'
 bindings=load(path(frozen['bindings']));assert bindings['passed']
 for v,k in [('B','baseline'),('C','candidate')]:assert bindings['binaries'][v]=={'path':frozen[k],'sha256':sha(path(frozen[k]))}
 records={};expected_sample_paths=set();expected_process_paths=set();sequence=0;measured=warmups=measured_processes=warmup_processes=0;timeline=[]
 for rnd in range(7):
  ordered=cases if rnd==0 else cases[(rnd-1)%len(cases):]+cases[:(rnd-1)%len(cases)];variants=['B','C'] if rnd==0 or rnd%2 else ['C','B'];phase='warmup' if rnd==0 else f'round-{rnd:02d}'
  for case in ordered:
   for v in variants:
    d=a.run/phase/case['id']/v;sfile=d/'sample.json';expected_sample_paths.add(sfile);row=load(sfile);assert row['passed'] and (row['id'],row['group'],row['suite'],row['variant'],row['round'],row['sequence'])==(case['id'],case['group'],case['suite'],v,rnd,sequence);sequence+=1;assert len(row['parts'])==len(case['parts']);timeline.append((row['started_at'],row['finished_at']));assert row['started_at']<=row['finished_at']
    parts=[]
    for part,expected in zip(row['parts'],case['parts'],strict=True):
     pd=d/expected['label'];pf=pd/'process.json';expected_process_paths.add(pf);assert load(pf)==part;assert part['passed'] and part['variant']==v and part['label']==expected['label'];assert pd==a.run/part['directory'];assert part['exit_code']==0 and part['stderr_bytes']==0;assert part['elapsed_ns']>0 and part['cpu_seconds']>=0 and part['peak_rss_bytes']>0
     assert row['started_at']<=part['started_at']<=part['finished_at']<=row['finished_at'];cmd=[frozen['baseline' if v=='B' else 'candidate'],*case['flags'],str(Path(frozen['shared'])/expected['input'])];assert part['command']==cmd
     for key,digest,size in [('input','input_sha256','input_bytes'),('reference','output_sha256','output_bytes')]:
      reference=path(Path(frozen['shared'])/expected[key]);assert reference.stat().st_size==expected[size] and sha(reference)==expected[digest]
     out=pd/'stdout';err=pd/'stderr';assert out.stat().st_size==part['output_bytes']==expected['output_bytes'];assert sha(out)==part['output_sha256']==expected['output_sha256'];assert err.stat().st_size==0 and sha(err)==part['stderr_sha256']==hashlib.sha256(b'').hexdigest();assert equal(out,path(Path(frozen['shared'])/expected['reference']));assert part['complete_reference_bytes_match'];assert part['free_bytes_before']>=3*1024**3+expected['output_bytes'] and part['free_bytes_after']>=3*1024**3
     if frozen['platform']=='macos':
      assert part['invocation']==['/usr/bin/time','-p','-l','-o',str(Path(frozen['output'])/part['directory']/'native.time'),*cmd];raw=(pd/'native.time').read_text();rss=re.search(r'^\s*(\d+)\s+maximum resident set size\s*$',raw,re.M);assert rss;fields={k:float(re.search(r'^'+k+r'\s+(\d+(?:\.\d+)?)\s*$',raw,re.M)[1]) for k in ['real','user','sys']};compare(part['native_time'],fields);close(part['cpu_seconds'],fields['user']+fields['sys']);assert part['peak_rss_bytes']==int(rss[1])
     else:
      assert part['invocation']==cmd;usage=part['wait4_rusage'];close(part['cpu_seconds'],usage['ru_utime']+usage['ru_stime']);assert part['peak_rss_bytes']==usage['ru_maxrss']*1024
     parts.append(part)
    assert row['elapsed_ns']==sum(x['elapsed_ns'] for x in parts);close(row['cpu_seconds'],sum(x['cpu_seconds'] for x in parts));assert row['peak_rss_bytes']==max(x['peak_rss_bytes'] for x in parts)
    if rnd:records[(case['id'],rnd,v)]=row;measured+=1;measured_processes+=len(parts)
    else:warmups+=1;warmup_processes+=len(parts)
 assert all(timeline[i][1]<=timeline[i+1][0] for i in range(len(timeline)-1)),'Samples overlapped or order differs'
 assert set(a.run.glob('warmup/*/*/sample.json'))|set(a.run.glob('round-*/*/*/sample.json'))==expected_sample_paths
 assert set(a.run.glob('warmup/*/*/*/process.json'))|set(a.run.glob('round-*/*/*/*/process.json'))==expected_process_paths
 expected_followup=[];recomputed={}
 for case in cases:
  pairs=[]
  for rnd in range(1,7):
   b=records[(case['id'],rnd,'B')];c=records[(case['id'],rnd,'C')];pair={'round':rnd,'B':{k:b[k] for k in ['elapsed_ns','cpu_seconds','peak_rss_bytes']},'C':{k:c[k] for k in ['elapsed_ns','cpu_seconds','peak_rss_bytes']}}
   for key,field in [('elapsed','elapsed_ns'),('cpu','cpu_seconds'),('rss','peak_rss_bytes')]:pair[key+'_change_pct']=(c[field]/b[field]-1)*100 if b[field] else None
   pairs.append(pair)
  value={'pairs':pairs,'paired_change_medians':{},'paired_change_ranges':{}}
  for key in ['elapsed','cpu','rss']:
   values=[x[key+'_change_pct'] for x in pairs if x[key+'_change_pct'] is not None];value['paired_change_medians'][key]=statistics.median(values) if values else None;value['paired_change_ranges'][key]=[min(values),max(values)] if values else None
  compare(value,summary['pairs'][case['id']]);recomputed[case['id']]=value
  if value['paired_change_medians']['elapsed']>5 or value['paired_change_medians']['rss']>5:expected_followup.append(case['id'])
 assert expected_followup==summary['followup_required'];assert set(summary['pairs'])=={c['id'] for c in cases}
 for key,value in [('measured_samples',measured),('warmups',warmups),('measured_processes',measured_processes),('warmup_processes',warmup_processes)]:assert summary[key]==value;result[key]=value
 assert measured==len(cases)*12 and warmups==len(cases)*2;result.update(passed=True,platform=frozen['platform'],group=summary['group'],case_count=len(cases),recomputed=recomputed,followup_required=expected_followup,frozen_files_verified=len(frozen['files']),all_output_bytes_verified=True,resource_metrics_reconciled=True)
except BaseException as error:result.update(error=repr(error),traceback=traceback.format_exc());raise
finally:
 result['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
 print(json.dumps({k:result[k] for k in ['passed','measured_samples','warmups','measured_processes','warmup_processes'] if k in result}),flush=True)
