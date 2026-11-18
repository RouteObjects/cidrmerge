#!/usr/bin/env python3
"""Serialize three primary groups and one fixed follow-up per affected group."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--shared',type=Path,required=True);p.add_argument('--platform-root',type=Path,required=True);p.add_argument('--platform',choices=['macos','linux'],required=True);p.add_argument('--bindings',type=Path,required=True);p.add_argument('--runtime-library-path');p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.shared=a.shared.resolve();a.platform_root=a.platform_root.resolve();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False);steps=[];receipt={'passed':False,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'steps':steps}
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
try:
 for group in ['original','scale','sparse']:
  for phase in ['primary','followup']:
   only=[]
   if phase=='followup':
    only=json.loads((a.output/group/'primary/summary.json').read_text())['followup_required']
    if not only:continue
   output=a.output/group/phase;command=[sys.executable,str(a.shared/'control/run_matched.py'),'--platform',a.platform,'--shared',str(a.shared),'--baseline',str(a.platform_root/'bin/B'),'--candidate',str(a.platform_root/'bin/C'),'--bindings',str(a.bindings.resolve()),'--group',group,'--output',str(output),'--content-store',str(a.output/'content')]
   if a.runtime_library_path:command+=['--runtime-library-path',a.runtime_library_path]
   if only:command+=['--only',*only]
   label=group+'-'+phase;print('START',label,flush=True);start=time.monotonic();step={'group':group,'phase':phase,'command':command,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()};save(a.output/(label+'-started.json'),step)
   with (a.output/(label+'.log')).open('x') as f:proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
   step.update(exit_code=proc.returncode,elapsed_s=time.monotonic()-start,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());save(a.output/(label+'.json'),step);steps.append(step);assert proc.returncode==0,step;print('DONE',label,flush=True)
 receipt['passed']=True
except BaseException as error:receipt['error']=repr(error);raise
finally:receipt['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(a.output/'driver-summary.json',receipt)
