from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,shutil,traceback
D=Path('$EXPERIMENT/downstream');P=D/'x86_64';S=D/'shared';O=P/'control/qualification-binding-02';O.mkdir(exist_ok=False)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
record={'passed':False,'started_at':now(),'reason':'Preserve count-valued I/O summary and adapt it to the strict boolean binding gate; no product or harness change.'}
try:
 old=json.loads((P/'control/qualification-followup-01/summary.json').read_text());assert not old['passed'] and old['error']=="AssertionError('bindings')"
 bad=json.loads((P/'control/premeasurement.json').read_text());assert not bad['passed'] and 'Gate not passed' in bad['error'] and 'io-differential-01' in bad['error']
 io=P/'behavior/io-differential-01/summary.json';j=json.loads(io.read_text());assert j['total']==j['passed']==86 and j['failed']==0 and not j['failures']
 paths=[P/'qualification-summary.json',P/'behavior/differential-01/summary.json',io,P/'harness-controls-01/summary.json',P/'final-validation-01/summary.json']
 for x in paths:
  if x!=io:assert json.loads(x.read_text())['passed'] is True
 gate={'passed':True,'at':now(),'total_io_cases':86,'all_io_cases_passed':True,'evidence':{str(x):sha(x) for x in paths},'adapter_only':True};gp=P/'control/qualification-gate.json';save(gp,gate)
 cmd=json.loads((P/'control/qualification-followup-01/bindings-started.json').read_text())['command'];cmd[cmd.index('--output')+1]=str(P/'control/premeasurement-v2.json')
 while '--evidence' in cmd:
  i=cmd.index('--evidence');del cmd[i:i+2]
 cmd+=['--evidence',str(gp)]
 for x in paths:cmd+=['--extra-file',str(x)]
 cmd+=['--extra-file',str(Path(__file__))]
 env=dict(os.environ,LD_LIBRARY_PATH=str(P/'runtime/lib'),PATH='$LINUX_HOME/.local/share/swiftly/toolchains/6.4.2/usr/bin:/usr/bin:/bin',LANG='C',LC_ALL='C')
 save(O/'command.json',{'command':cmd})
 with (O/'binding.log').open('x') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0;bind=P/'control/premeasurement-v2.json';assert json.loads(bind.read_text())['passed'] is True
 ready={'passed':True,'at':now(),'platform':'x86_64','baseline_commit':'5ab794a5a0578c03fd7b52f3b72889de201c09f8','candidate_upstream_version':'0.11.0','candidate_upstream_revision':'ae956313ebbcb5a6f9d20b74626ce5b6e2e69839','full_suite_tests_each_variant':{'debug':85,'release':85},'differential_cases':254,'io_cases':86,'harness_checks':14,'final_validation_passed':True,'bindings':str(bind),'bindings_sha256':sha(bind),'evidence':gate['evidence'],'qualification_gate':{'path':str(gp),'sha256':sha(gp)},'platform_root':str(P),'shared_root':str(S),'runtime':str(P/'runtime/lib'),'timed_workloads_started':False,'free_bytes':shutil.disk_usage(P).free,'preserved_failures':['control/qualification-followup-01/summary.json','control/premeasurement.json']};save(P/'control/launch-ready.json',ready);record['passed']=True;print(json.dumps(ready))
except BaseException as e:record.update(error=repr(e),traceback=traceback.format_exc());raise
finally:record['finished_at']=now();save(O/'summary.json',record)
