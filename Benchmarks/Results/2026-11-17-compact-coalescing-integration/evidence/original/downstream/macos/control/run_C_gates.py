from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
R=Path(__file__).resolve().parents[3];P=R/'downstream/macos';H=R/'downstream/shared/control';O=P/'control/C-gates';O.mkdir(exist_ok=False)
ENV={**os.environ,'DEVELOPER_DIR':'/Applications/Xcode-27.2.0.app/Contents/Developer','TMPDIR':str(P/'tmp')+'/','GIT_TERMINAL_PROMPT':'0','GIT_SSH_COMMAND':'false'}
SWIFT='/Applications/Xcode-27.2.0.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift'
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,d):
 with path.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
Q={'passed':False,'started_at':now(),'steps':[],'timed_measurements_started':False}
def run(name,argv,receipt,kind='boolean'):
 d={'name':name,'command':argv,'started_at':now()};print('START',name,flush=True)
 with (P/'logs'/(name+'.log')).open('xb') as f:proc=subprocess.run(argv,cwd=P,env=ENV,stdout=f,stderr=subprocess.STDOUT)
 raw=json.loads(receipt.read_text()) if receipt.exists() else {};passed=proc.returncode==0 and (raw.get('passed') is True if kind=='boolean' else raw.get('total')==84 and raw.get('passed')==84 and raw.get('failed')==0)
 if name=='C-differential':passed=passed and raw.get('case_count')==254
 d.update(passed=passed,exit_code=proc.returncode,finished_at=now(),receipt=str(receipt.relative_to(R)),receipt_sha256=sha(receipt) if receipt.exists() else None,case_count=raw.get('case_count',raw.get('total')));save(O/(name+'.json'),d);Q['steps'].append(d);print(json.dumps(d),flush=True)
try:
 pending=P/'control/C-qualification/summary.json'
 while not pending.exists():time.sleep(5)
 assert json.loads(pending.read_text())['passed']
 for variant in ['B','C']:
  q=json.loads((P/f'control/{variant}-qualification/summary.json').read_text());assert q['passed'];assert [x['total_tests'] for x in q['steps'] if 'total_tests' in x]==[85,85]
 run('C-runtime-identity',[sys.executable,str(P/'control/capture_runtime.py'),'--binary',str(P/'bin/C'),'--output',str(P/'metadata/C-runtime-identity.json')],P/'metadata/C-runtime-identity.json')
 b=json.loads((P/'metadata/B-runtime-identity.json').read_text());c=json.loads((P/'metadata/C-runtime-identity.json').read_text());assert b['loaded_shared_cache']['uuid']==c['loaded_shared_cache']['uuid'] and b['compiler']['sha256']==c['compiler']['sha256'] and b['system']['stdout']==c['system']['stdout'];assert b['linked_image_uuids']['stdout']==c['linked_image_uuids']['stdout']
 run('C-differential',[sys.executable,str(H/'differential.py'),'--baseline',str(P/'bin/B'),'--candidate',str(P/'bin/C'),'--output',str(P/'differential-01')],P/'differential-01/summary.json')
 run('C-io-differential',[sys.executable,str(H/'io_differential_v2.py'),'--baseline',str(P/'bin/B'),'--candidate',str(P/'bin/C'),'--output',str(P/'io-differential-01')],P/'io-differential-01/summary.json','count')
 run('C-final-validation',[sys.executable,str(H/'final_validation_v2.py'),'--source',str(P/'sources/C'),'--baseline-source',str(P/'sources/B'),'--seed',str(P/'build/C-ordinary'),'--output',str(P/'final-validation-01'),'--binary',str(P/'bin/C'),'--swift',SWIFT,'--jobs','6'],P/'final-validation-01/summary.json')
 preserved={}
 for v,freeze in [('B','cidrmerge-baseline-freeze.json'),('C','cidrmerge-candidate-freeze.json')]:
  f=json.loads((R/'control'/freeze).read_text());assert all(sha(P/'sources'/v/n)==h for n,h in f['files'].items());meta=json.loads((P/f'metadata/{v}-ordinary.json').read_text());assert sha(P/'bin'/v)==meta['sha256'];preserved[v]={'source_files':len(f['files']),'binary_sha256':meta['sha256'],'source_and_binary_unchanged':True}
 Q.update(passed=all(x['passed'] for x in Q['steps']),runtime_and_compiler_matched=True,ordinary_backend_and_commands_matched=True,preservation=preserved)
except BaseException as e:Q['error']=repr(e);raise
finally:Q['finished_at']=now();save(O/'summary.json',Q);print(json.dumps({'passed':Q['passed'],'receipt':str(O/'summary.json'),'error':Q.get('error')}),flush=True)
raise SystemExit(0 if Q['passed'] else 1)
