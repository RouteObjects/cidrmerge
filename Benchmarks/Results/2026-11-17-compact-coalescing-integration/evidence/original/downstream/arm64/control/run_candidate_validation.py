#!/usr/bin/env python3
from pathlib import Path
import datetime,json,subprocess,time
ROOT=Path('$EXPERIMENT/downstream/arm64');OUT=ROOT/'control/candidate-validation-driver-01';OUT.mkdir();docker=['/usr/local/bin/docker','--config',str(ROOT/'control/docker-config'),'--host','unix://$USER_HOME/.orbstack/run/docker.sock'];names={'642':'coalescing-downstream-arm642-20261118T031137Z','624':'coalescing-downstream-arm624-20261118T031137Z'};python='$PLATFORM/python/bin/python3';shared='$EXPERIMENT/downstream/shared/control';steps=[];record={'passed':False,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'steps':steps}
schedule=[('candidate-642','642',[python,'$PLATFORM/control/qualify_variant.py','--variant','C','--manifest','$EXPERIMENT/control/cidrmerge-candidate-freeze.json','--expected-tests','85']),('candidate-floor','624',[python,'$PLATFORM/control/qualify_floor.py']),('differential','642',[python,shared+'/differential.py','--baseline','$PLATFORM/bin/B','--candidate','$PLATFORM/bin/C','--output','$PLATFORM/differential-01','--runtime-library-path','$PLATFORM/runtime/lib']),('io-differential','642',[python,shared+'/io_differential_v2.py','--baseline','$PLATFORM/bin/B','--candidate','$PLATFORM/bin/C','--output','$PLATFORM/io-differential-01']),('final-validation','642',[python,shared+'/final_validation_v2.py','--source','$PLATFORM/sources/C','--baseline-source','$PLATFORM/sources/B','--seed','$PLATFORM/build/C-ordinary','--output','$PLATFORM/final-validation-01','--binary','$PLATFORM/bin/C','--swift','/usr/bin/swift','--jobs','8'])]
try:
 for label,version,args in schedule:
  command=docker+['exec','--env','LD_LIBRARY_PATH=$PLATFORM/runtime/lib',names[version],*args] if label in ['differential','io-differential','final-validation'] else docker+['exec',names[version],*args];step={'label':label,'command':command,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()};start=time.monotonic();print('START',label,flush=True)
  with (OUT/(label+'.log')).open('x') as f:proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
  step.update(exit_code=proc.returncode,elapsed_s=time.monotonic()-start,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());steps.append(step)
  with (OUT/(label+'.json')).open('x') as f:json.dump(step,f,indent=2);f.write(chr(10))
  print('DONE',label,'exit',proc.returncode,flush=True);assert proc.returncode==0,label
 record['passed']=True
except BaseException as error:record['error']=repr(error);raise
finally:
 record['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (OUT/'summary.json').open('x') as f:json.dump(record,f,indent=2);f.write(chr(10))
 print('SUMMARY',record['passed'],flush=True)
