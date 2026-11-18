#!/usr/bin/env python3
from pathlib import Path
import datetime,json,subprocess,time
R=Path('$EXPERIMENT/arm64');out=R/'control/upstream-driver-01';out.mkdir()
docker=['/usr/local/bin/docker','--config',str(R/'control/docker-config'),'--host','unix://$USER_HOME/.orbstack/run/docker.sock'];steps=[]
for label,version in [('642','6.4.2'),('624','6.2.4')]:
 command=docker+['exec','coalescing-release-arm'+label+'-20261118T031137Z','$PLATFORM/python/bin/python3','$PLATFORM/control/qualify_upstream.py','--version',version]
 start=time.monotonic();proc=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(version+'.log')).write_text(proc.stdout);print(proc.stdout,flush=True);rec={'version':version,'command':command,'exit_code':proc.returncode,'elapsed_s':time.monotonic()-start};steps.append(rec)
 with (out/(version+'.json')).open('x') as f:json.dump(rec,f,indent=2);f.write(chr(10))
 if proc.returncode:break
with (out/'summary.json').open('x') as f:json.dump({'passed':len(steps)==2 and all(x['exit_code']==0 for x in steps),'steps':steps},f,indent=2);f.write(chr(10))
assert len(steps)==2 and all(x['exit_code']==0 for x in steps)
