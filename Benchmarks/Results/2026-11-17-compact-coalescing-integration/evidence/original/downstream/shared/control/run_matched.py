#!/usr/bin/env python3
"""Six-pair coalescing integration run. Fresh evidence only; exact child resources."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,re,shutil,signal,statistics,subprocess,time

def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def equal(a,b):
 with Path(a).open('rb') as x,Path(b).open('rb') as y:
  while True:
   left=x.read(1024*1024);right=y.read(1024*1024)
   if left!=right:return False
   if not left:return True
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write(chr(10))
def timeout(*_):raise TimeoutError('Child exceeded 180 seconds')
def run_part(args,case,part,variant,directory,env):
 directory.mkdir(parents=True,exist_ok=False);stdout=directory/'stdout';stderr=directory/'stderr';native=directory/'native.time'
 free=shutil.disk_usage(args.output).free;assert free>=3*1024**3+part['output_bytes'],'Insufficient measurement headroom'
 binary=args.baseline if variant=='B' else args.candidate
 cmd=[str(binary),*case['flags'],str(args.shared/part['input'])]
 invocation=['/usr/bin/time','-p','-l','-o',str(native),*cmd] if args.platform=='macos' else cmd
 row={'passed':False,'label':part['label'],'variant':variant,'started_at':now(),'command':cmd,'invocation':invocation,'free_bytes_before':free,'directory':str(directory.relative_to(args.output))};proc=None;usage=None;previous=signal.signal(signal.SIGALRM,timeout)
 try:
  with stdout.open('xb') as out,stderr.open('xb') as err:
   start=time.perf_counter_ns();signal.setitimer(signal.ITIMER_REAL,180)
   try:
    proc=subprocess.Popen(invocation,stdin=subprocess.DEVNULL,stdout=out,stderr=err,cwd=args.output,env=env,start_new_session=True)
    if args.platform=='macos':proc.wait()
    else:
     pid,status,usage=os.wait4(proc.pid,0);assert pid==proc.pid;proc.returncode=os.waitstatus_to_exitcode(status)
   except BaseException:
    if proc is not None and proc.returncode is None:
     try:os.killpg(proc.pid,signal.SIGKILL)
     except ProcessLookupError:pass
     try:
      if args.platform=='macos':proc.wait()
      else:
       _,status,usage=os.wait4(proc.pid,0);proc.returncode=os.waitstatus_to_exitcode(status)
     except ChildProcessError:row['cleanup_note']='Owned child already reaped'
    raise
   finally:
    row['elapsed_ns']=time.perf_counter_ns()-start;signal.setitimer(signal.ITIMER_REAL,0)
    if proc is not None:row['exit_code']=proc.returncode
    if usage is not None:row['wait4_rusage']={k:getattr(usage,k) for k in ('ru_utime','ru_stime','ru_maxrss','ru_minflt','ru_majflt','ru_nswap','ru_inblock','ru_oublock','ru_nvcsw','ru_nivcsw')}
  if args.platform=='macos':
   raw=native.read_text();rss=re.search(r'^\s*(\d+)\s+maximum resident set size\s*$',raw,re.M);fields={k:re.search(r'^'+k+r'\s+(\d+(?:\.\d+)?)\s*$',raw,re.M) for k in ('real','user','sys')};assert rss and all(fields.values()),'Missing native resource metrics';row['native_time']={k:float(v[1]) for k,v in fields.items()};row['cpu_seconds']=row['native_time']['user']+row['native_time']['sys'];row['peak_rss_bytes']=int(rss[1])
  else:row['cpu_seconds']=usage.ru_utime+usage.ru_stime;row['peak_rss_bytes']=int(usage.ru_maxrss)*1024
  row.update(output_bytes=stdout.stat().st_size,output_sha256=sha(stdout),stderr_bytes=stderr.stat().st_size,stderr_sha256=sha(stderr));assert row['exit_code']==0 and row['stderr_bytes']==0 and row['peak_rss_bytes']>0,row
  assert (row['output_bytes'],row['output_sha256'])==(part['output_bytes'],part['output_sha256']),'Output reference hash mismatch'
  assert equal(stdout,args.shared/part['reference']),'Complete output bytes differ';row['complete_reference_bytes_match']=True
  if args.content_store:
   canonical=args.content_store/row['output_sha256']
   if not canonical.exists():os.link(stdout,canonical)
   assert sha(canonical)==row['output_sha256'] and equal(stdout,canonical),'Content-store collision or corruption'
   if not os.path.samefile(stdout,canonical):
    replacement=directory/'stdout.link';os.link(canonical,replacement);os.replace(replacement,stdout)
   row['post_verification_identical_output_hardlink']=True
  row['free_bytes_after']=shutil.disk_usage(args.output).free;assert row['free_bytes_after']>=3*1024**3;row['passed']=True;return row
 except BaseException as error:row['error']=repr(error);raise
 finally:signal.signal(signal.SIGALRM,previous);row['finished_at']=now();save(directory/'process.json',row)
def run_sample(args,case,variant,phase,round_index,sequence,env):
 directory=args.output/phase/case['id']/variant;directory.mkdir(parents=True,exist_ok=False);row={'passed':False,'id':case['id'],'group':case['group'],'suite':case['suite'],'variant':variant,'round':round_index,'sequence':sequence,'started_at':now(),'parts':[]}
 try:
  for part in case['parts']:row['parts'].append(run_part(args,case,part,variant,directory/part['label'],env))
  row.update(elapsed_ns=sum(x['elapsed_ns'] for x in row['parts']),cpu_seconds=sum(x['cpu_seconds'] for x in row['parts']),peak_rss_bytes=max(x['peak_rss_bytes'] for x in row['parts']),passed=True);return row
 except BaseException as error:row['error']=repr(error);raise
 finally:row['finished_at']=now();save(directory/'sample.json',row)
def main():
 p=argparse.ArgumentParser();p.add_argument('--platform',choices=['macos','linux'],required=True);p.add_argument('--shared',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--bindings',type=Path,required=True);p.add_argument('--group',choices=['original','scale','sparse'],required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime-library-path');p.add_argument('--content-store',type=Path);p.add_argument('--only',nargs='+');a=p.parse_args()
 assert platform.system()==('Darwin' if a.platform=='macos' else 'Linux')
 for k in ['shared','baseline','candidate','bindings','output','content_store']:
  if getattr(a,k) is not None:setattr(a,k,getattr(a,k).resolve())
 a.output.mkdir(parents=True,exist_ok=False)
 if a.content_store:a.content_store.mkdir(parents=True,exist_ok=True)
 summary={'passed':False,'started_at':now(),'group':a.group,'platform':a.platform,'measured_samples':0,'warmups':0,'measured_processes':0,'warmup_processes':0,'pairs':{},'followup_required':[]};rows={};sequence=0
 try:
  casefile=a.shared/'control/cases.json';spec=json.loads(casefile.read_text());cases=[x for x in spec['configs'] if x['group']==a.group and (not a.only or x['id'] in a.only)];assert cases and (not a.only or set(a.only)=={x['id'] for x in cases})
  bindings=json.loads(a.bindings.read_text());assert bindings['passed'];assert bindings['binaries']=={'B':{'path':str(a.baseline),'sha256':sha(a.baseline)},'C':{'path':str(a.candidate),'sha256':sha(a.candidate)}},'Bindings do not match timed binaries'
  frozen=dict(bindings['files']);frozen.update({str(a.bindings):sha(a.bindings),str(casefile):sha(casefile),str(a.shared/'control/protocol.json'):sha(a.shared/'control/protocol.json'),str(Path(__file__).resolve()):sha(Path(__file__))})
  for case in cases:
   for part in case['parts']:
    for k,h in [('input','input_sha256'),('reference','output_sha256')]:frozen[str(a.shared/part[k])]=part[h]
  for file,digest in frozen.items():assert sha(file)==digest,('Freeze mismatch',file)
  env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC','TMPDIR':str(a.output/'tmp')+'/'};(a.output/'tmp').mkdir()
  if a.runtime_library_path:env['LD_LIBRARY_PATH']=a.runtime_library_path
  save(a.output/'freeze.json',{'files':frozen,'platform':a.platform,'host':platform.platform(),'environment':env,'configs':cases,'bindings':str(a.bindings),'baseline':str(a.baseline),'candidate':str(a.candidate),'shared':str(a.shared),'output':str(a.output),'content_store':str(a.content_store) if a.content_store else None,'script_sha256':sha(Path(__file__))})
  for case in cases:
   for v in ('B','C'):run_sample(a,case,v,'warmup',0,sequence,env);sequence+=1;summary['warmups']+=1;summary['warmup_processes']+=len(case['parts'])
  for rnd in range(6):
   ordered=cases[rnd%len(cases):]+cases[:rnd%len(cases)];variants=('B','C') if rnd%2==0 else ('C','B')
   for case in ordered:
    for v in variants:rows[(case['id'],rnd,v)]=run_sample(a,case,v,f'round-{rnd+1:02d}',rnd+1,sequence,env);sequence+=1;summary['measured_samples']+=1;summary['measured_processes']+=len(case['parts'])
   print('finished',a.group,'pair round',rnd+1,flush=True)
  for case in cases:
   pairs=[]
   for rnd in range(6):
    b=rows[(case['id'],rnd,'B')];c=rows[(case['id'],rnd,'C')];pair={'round':rnd+1,'B':{k:b[k] for k in ('elapsed_ns','cpu_seconds','peak_rss_bytes')},'C':{k:c[k] for k in ('elapsed_ns','cpu_seconds','peak_rss_bytes')}}
    for key,field in [('elapsed','elapsed_ns'),('cpu','cpu_seconds'),('rss','peak_rss_bytes')]:pair[key+'_change_pct']=(c[field]/b[field]-1)*100 if b[field] else None
    pairs.append(pair)
   result={'pairs':pairs,'paired_change_medians':{},'paired_change_ranges':{}}
   for key in ['elapsed','cpu','rss']:
    values=[x[key+'_change_pct'] for x in pairs if x[key+'_change_pct'] is not None];result['paired_change_medians'][key]=statistics.median(values) if values else None;result['paired_change_ranges'][key]=[min(values),max(values)] if values else None
   summary['pairs'][case['id']]=result
   if result['paired_change_medians']['elapsed']>5 or result['paired_change_medians']['rss']>5:summary['followup_required'].append(case['id'])
  for file,digest in frozen.items():assert sha(file)==digest,('Freeze changed',file)
  summary.update(passed=True,freeze_unchanged=True)
 except BaseException as error:summary['error']=repr(error);raise
 finally:summary['finished_at']=now();save(a.output/'summary.json',summary)
 print(json.dumps({k:summary[k] for k in ['passed','group','measured_samples','warmups','measured_processes','warmup_processes','followup_required']}),flush=True)
if __name__=='__main__':main()
