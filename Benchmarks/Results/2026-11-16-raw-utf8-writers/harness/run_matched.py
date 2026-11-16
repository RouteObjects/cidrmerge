#!/usr/bin/env python3
"""Matched whole-output renderer experiment; all samples and exact stdout bytes are preserved."""
from pathlib import Path
import argparse,datetime,filecmp,hashlib,json,os,platform,re,shutil,signal,statistics,subprocess,time

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def expired(*_):raise TimeoutError('Child exceeded 180 seconds')
def run(args,c,v,d,env):
 d.mkdir(parents=True);output=d/'stdout';err=d/'stderr';metrics=d/'native.time';cmd=[str(getattr(args,'baseline' if v=='B' else 'candidate')),'--raw','--representation',c['representation'],str(args.fixtures_root/c['input'])]
 free=shutil.disk_usage(args.output).free;assert free>=3*1024**3+c['output_bytes'],'Insufficient measurement space'
 rec={'id':c['id'],'variant':v,'started_at':stamp(),'command':cmd,'free_bytes_before':free,'passed':False};proc=None;usage=None;previous=signal.signal(signal.SIGALRM,expired)
 try:
  with output.open('xb') as out,err.open('xb') as stderr:
   start=time.perf_counter_ns();signal.setitimer(signal.ITIMER_REAL,180)
   try:
    invocation=['/usr/bin/time','-p','-l','-o',str(metrics),*cmd] if args.platform=='macos' else cmd
    proc=subprocess.Popen(invocation,stdout=out,stderr=stderr,stdin=subprocess.DEVNULL,cwd=args.output,env=env,start_new_session=True)
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
     except ChildProcessError:rec['cleanup_note']='Child was already reaped during timeout handling'
    raise
   finally:
    rec['elapsed_ns']=time.perf_counter_ns()-start;signal.setitimer(signal.ITIMER_REAL,0)
    if proc is not None:rec['exit_code']=proc.returncode
    if usage is not None:rec['wait4_rusage']={k:getattr(usage,k) for k in ('ru_utime','ru_stime','ru_maxrss','ru_minflt','ru_majflt','ru_nswap','ru_inblock','ru_oublock','ru_nvcsw','ru_nivcsw')}
  rec['exit_code']=proc.returncode
  if args.platform=='macos':
   raw=metrics.read_text();rss=re.search(r'^\s*(\d+)\s+maximum resident set size\s*$',raw,re.M);fields={k:re.search(r'^'+k+r'\s+(\d+(?:\.\d+)?)\s*$',raw,re.M) for k in ('real','user','sys')};assert rss and all(fields.values()),'Missing native time metrics';rec['native_time']={k:float(v[1]) for k,v in fields.items()};rec['cpu_seconds']=rec['native_time']['user']+rec['native_time']['sys'];rec['peak_rss_bytes']=int(rss[1])
  else:
   rec['wait4_rusage']={k:getattr(usage,k) for k in ('ru_utime','ru_stime','ru_maxrss','ru_minflt','ru_majflt','ru_nswap','ru_inblock','ru_oublock','ru_nvcsw','ru_nivcsw')};rec['cpu_seconds']=usage.ru_utime+usage.ru_stime;rec['peak_rss_bytes']=int(usage.ru_maxrss)*1024
  rec.update(output_bytes=output.stat().st_size,output_sha256=sha(output),stderr_bytes=err.stat().st_size)
  assert rec['exit_code']==0 and rec['stderr_bytes']==0,rec
  assert (rec['output_bytes'],rec['output_sha256'])==(c['output_bytes'],c['output_sha256']), 'Reference hash mismatch'
  assert filecmp.cmp(output,args.fixtures_root/c['reference'],shallow=False),'Complete reference bytes differ'
  rec['complete_reference_bytes_match']=True
  if args.deduplicate:
   store=args.output/'content';store.mkdir(exist_ok=True);canonical=store/rec['output_sha256']
   if not canonical.exists():os.link(output,canonical);canonical.chmod(0o444)
   assert filecmp.cmp(output,canonical,shallow=False)
   replacement=d/'stdout.link';os.link(canonical,replacement);os.replace(replacement,output);rec['post_sample_identical_content_hardlink']=True
  rec['free_bytes_after']=shutil.disk_usage(args.output).free;assert rec['free_bytes_after']>=3*1024**3
  rec['passed']=True;return rec
 except BaseException as error:rec['error']=repr(error);raise
 finally:signal.signal(signal.SIGALRM,previous);rec['finished_at']=stamp();save(d/'sample.json',rec)

def main():
 p=argparse.ArgumentParser();p.add_argument('--platform',choices=['macos','linux'],required=True);p.add_argument('--fixtures-root',type=Path,required=True);p.add_argument('--cases',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime-library-path');p.add_argument('--deduplicate',action='store_true');p.add_argument('--only',nargs='+');args=p.parse_args()
 assert platform.system()==('Darwin' if args.platform=='macos' else 'Linux'),'OS does not match requested resource units'
 for name in ('fixtures_root','cases','baseline','candidate','output'):setattr(args,name,getattr(args,name).resolve())
 assert not args.output.exists();args.output.mkdir(parents=True);spec=json.loads(args.cases.read_text());cases=[x for x in spec['configs'] if not args.only or x['id'] in args.only];assert cases and (not args.only or set(args.only)=={x['id'] for x in cases})
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC','TMPDIR':str(args.output/'tmp')+'/'};(args.output/'tmp').mkdir()
 if args.runtime_library_path:env['LD_LIBRARY_PATH']=args.runtime_library_path
 frozen={str(args.cases):sha(args.cases),str(Path(__file__).resolve()):sha(Path(__file__).resolve()),str(args.baseline):sha(args.baseline),str(args.candidate):sha(args.candidate)}
 for c in cases:
  for key,h in [('input','input_sha256'),('reference','output_sha256')]:
   path=args.fixtures_root/c[key];assert sha(path)==c[h];frozen[str(path)]=c[h]
 save(args.output/'freeze.json',{'files':frozen,'environment':env,'host':platform.platform(),'configs':cases,'deduplicate_after_timed_sample':args.deduplicate})
 summary={'passed':False,'started_at':stamp(),'measured_samples':0,'warmups':0,'pairs':{},'followup_required':[]};measurements={}
 try:
  for i,c in enumerate(cases):
   for v in ('B','C'):run(args,c,v,args.output/'warmup'/c['id']/v,env);summary['warmups']+=1
  for round in range(6):
   ordered=cases[round%len(cases):]+cases[:round%len(cases)];variants=('B','C') if round%2==0 else ('C','B')
   for c in ordered:
    for v in variants:
     result=run(args,c,v,args.output/f'round-{round+1:02d}'/c['id']/v,env);measurements[(c['id'],round,v)]=result;summary['measured_samples']+=1
   print('finished pair round',round+1,flush=True)
  for c in cases:
   pairs=[]
   for round in range(6):
    b=measurements[(c['id'],round,'B')];q=measurements[(c['id'],round,'C')];pair={'round':round+1,'B':{k:b[k] for k in ('elapsed_ns','cpu_seconds','peak_rss_bytes')},'C':{k:q[k] for k in ('elapsed_ns','cpu_seconds','peak_rss_bytes')}}
    for key,field in [('elapsed','elapsed_ns'),('cpu','cpu_seconds'),('rss','peak_rss_bytes')]:pair[key+'_change_pct']=(q[field]/b[field]-1)*100 if b[field] else None
    pairs.append(pair)
   summary['pairs'][c['id']]={'pairs':pairs,'paired_change_medians':{k:(statistics.median(p[k+'_change_pct'] for p in pairs if p[k+'_change_pct'] is not None) if any(p[k+'_change_pct'] is not None for p in pairs) else None) for k in ('elapsed','cpu','rss')}}
   if any(p['elapsed_change_pct']>5 or p['rss_change_pct']>5 for p in pairs):summary['followup_required'].append(c['id'])
  assert all(sha(Path(path))==h for path,h in frozen.items());summary['freeze_unchanged']=True;summary['passed']=True
 except BaseException as e:summary['error']=repr(e);raise
 finally:summary['finished_at']=stamp();save(args.output/'summary.json',summary)
 print(json.dumps({'passed':summary['passed'],'measured_samples':summary['measured_samples'],'warmups':summary['warmups'],'followup_required':summary['followup_required']}))
if __name__=='__main__':main()
