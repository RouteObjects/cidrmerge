#!/usr/bin/env python3
"""Post-timing method control only: unchanged /bin/true, variable parent allocation."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,platform,resource,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker-mib',type=int);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);control=Path(__file__).resolve().parent
assert platform.system()=='Linux'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
def current_memory():
 lines=Path('/proc/self/status').read_text().splitlines();return {k:int(next(x.split()[1] for x in lines if x.startswith(k+':'))) for k in ['VmRSS','VmHWM']}
if a.worker_mib is not None:
 assert a.worker_mib in [0,32,96]
 spec=importlib.util.spec_from_file_location('frozen_startup_runner',control/'run_startup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 empty=out/'empty.expected';empty.write_bytes(b'');memory=bytearray(a.worker_mib*1024*1024)
 for offset in range(0,len(memory),4096):memory[offset]=1
 args=argparse.Namespace(baseline=Path('/bin/true'),candidate=Path('/bin/true'),fixtures_root=out,output=out,platform='linux',deduplicate=False)
 case={'id':'unchanged-true','flags':[],'input':None,'reference':'empty.expected','output_bytes':0,'output_sha256':m.sha(empty),'stderr_reference':'empty.expected','stderr_bytes':0,'stderr_sha256':m.sha(empty)}
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','TZ':'UTC','TMPDIR':str(out)+'/'};rows=[]
 for index in range(3):
  before=current_memory();sample=m.run(args,case,'B',out/f'run-{index+1:02d}',env);rows.append({'parent_memory_kib_before':before,'parent_self_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'child_peak_rss_bytes':sample['peak_rss_bytes'],'sample':f'run-{index+1:02d}/sample.json'})
 assert all(memory[offset]==1 for offset in range(0,len(memory),4096))
 result={'passed':True,'allocated_parent_mib':a.worker_mib,'target':'/bin/true','target_sha256':sha('/bin/true'),'observations':rows,'runner_sha256':sha(control/'run_startup.py'),'scope':'Measurement-method control, not cidrmerge performance'}
 save(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0)
results=[]
for amount in [0,32,96]:
 command=[sys.executable,str(Path(__file__).resolve()),'--output',str(out/f'parent-{amount:02d}MiB'),'--worker-mib',str(amount)];q=subprocess.run(command,capture_output=True,text=True);(out/f'worker-{amount:02d}.stdout').write_text(q.stdout);(out/f'worker-{amount:02d}.stderr').write_text(q.stderr);assert q.returncode==0,q.stderr;results.append(json.loads((out/f'parent-{amount:02d}MiB/summary.json').read_text()))
assert len({x['target_sha256'] for x in results})==1
receipt={'passed':True,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'architecture':platform.machine(),'python':sys.version,'script_sha256':sha(Path(__file__)),'runner_sha256':sha(control/'run_startup.py'),'groups':results,'limitations':'Controls identify parent-memory influence on direct Popen/wait4 lifetime maxRSS; do not correct or pool any original startup observation.'}
save(out/'summary.json',receipt);print(json.dumps({'passed':True,'groups':len(results),'receipt':str(out/'summary.json')}))
