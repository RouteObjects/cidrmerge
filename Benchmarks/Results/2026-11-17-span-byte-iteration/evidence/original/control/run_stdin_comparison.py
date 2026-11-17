#!/usr/bin/env python3
"""Run an isolated redirected-stdin comparison with its own preserved evidence."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,subprocess,sys

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--platform-root',type=Path,required=True);p.add_argument('--platform',choices=['macos','linux'],required=True);p.add_argument('--comparison',required=True);p.add_argument('--phase',default='primary');p.add_argument('--runtime-library-path');p.add_argument('--only',nargs='+');p.add_argument('--startup',action='store_true');p.add_argument('--artifact-profile',choices=['ordinary','release-style'],default='ordinary');a=p.parse_args()
root=a.root.resolve();platform_root=a.platform_root.resolve();left,right=a.comparison.split('-vs-');assert (left,right)==('B','P');assert not a.startup and a.artifact_profile=='ordinary';base=platform_root/'stdin'/a.artifact_profile/a.comparison;base.mkdir(parents=True,exist_ok=True)
runner=root/'control/run_stdin.py';cases=root/'control/stdin-cases.json';binary_root=platform_root/'bin'/('release-style' if a.artifact_profile=='release-style' else ('stripped' if a.startup else ''))
command=[sys.executable,str(runner),'--platform',a.platform,'--fixtures-root',str(root),'--cases',str(cases),'--baseline',str(binary_root/left),'--candidate',str(binary_root/right),'--output',str(base/a.phase),'--deduplicate']
if a.runtime_library_path:command+=['--runtime-library-path',a.runtime_library_path]
if a.only:command+=['--only',*a.only]
receipt={'stdin_transport':'regular-file-redirection','wrapper_source':Path(__file__).name,'wrapper_path':str(Path(__file__).resolve()),'post_timing_cross_comparison_dedup':False,'wrapper_sha256':sha(Path(__file__)), 'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'comparison':a.comparison,'role_mapping':{'B':left,'C':right},'phase':a.phase,'startup':a.startup,'artifact_profile':a.artifact_profile,'command':command,'source_runner_sha256':sha(runner),'cases_sha256':sha(cases),'binary_sha256':{v:sha(binary_root/v) for v in [left,right]},'baseline':str(binary_root/left),'candidate':str(binary_root/right),'status':'started'}
save(base/(a.phase+'-invocation.json'),receipt)
with (base/(a.phase+'-driver.log')).open('x') as log:
 completed=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
# Cross-phase relinking is deliberately omitted on every platform; outputs remain preserved within each phase.
receipt.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=completed.returncode,driver_log_sha256=sha(base/(a.phase+'-driver.log')),status='completed')
save(base/(a.phase+'-completion.json'),receipt)
print(json.dumps({'comparison':a.comparison,'phase':a.phase,'startup':a.startup,'exit_code':completed.returncode,'output':str(base/a.phase)}),flush=True)
raise SystemExit(completed.returncode)
