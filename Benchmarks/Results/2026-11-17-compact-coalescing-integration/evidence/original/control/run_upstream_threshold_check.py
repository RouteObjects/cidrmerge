from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[1]
S=R/'sources/upstream-validation'
name=sys.argv[1]
O=R/'macos'/name
O.mkdir(parents=True,exist_ok=False)
F=json.loads((R/'control/upstream-source-freeze.json').read_text())
env=os.environ.copy();env.update(DEVELOPER_DIR='/Applications/Xcode-27.2.0.app/Contents/Developer',TMPDIR=str(R/'tmp')+'/',GIT_TERMINAL_PROMPT='0',GIT_SSH_COMMAND='false')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check():
 changed=[n for n,h in F['files'].items() if not (S/n).exists() or sha(S/n)!=h]
 return {'changed_files':changed,'git_status':subprocess.check_output(['git','status','--porcelain'],cwd=S,text=True),'threshold_count':sum(n.startswith('Benchmarks/Thresholds/') and n.endswith('.json') for n in F['files'])}
argv=['swift','package','--package-path',str(S/'Benchmarks'),'--scratch-path',str(R/'macos/upstream-qualification/benchmark-build'),'--disable-automatic-resolution','benchmark']+sys.argv[2:]
d={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':argv,'entry':check(),'source_freeze':'control/upstream-source-freeze.json','toolchain':subprocess.check_output(['swift','--version'],env=env,text=True),'passed':False}
assert not d['entry']['changed_files'] and not d['entry']['git_status']
with (O/'command.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
with (O/'command.log').open('xb') as f:result=subprocess.run(argv,cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT)
d.update(exit_code=result.returncode,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit=check(),log_sha256=sha(O/'command.log'))
d['passed']=result.returncode==0 and not d['exit']['changed_files'] and not d['exit']['git_status']
with (O/'summary.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'passed':d['passed'],'exit_code':result.returncode,'receipt':str(O/'summary.json')}),flush=True)
raise SystemExit(0 if d['passed'] else 1)
