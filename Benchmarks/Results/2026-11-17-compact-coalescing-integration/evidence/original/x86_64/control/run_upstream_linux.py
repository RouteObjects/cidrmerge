#!/usr/bin/env python3
"""Fresh x86-64 qualification only; no historical mutation or timed workloads."""
from pathlib import Path
import datetime,hashlib,json,os,platform,re,shutil,subprocess,time,traceback,tarfile
ROOT=Path('$EXPERIMENT')
SRC=ROOT/'sources/upstream-validation';OUT=ROOT/'upstream-qualification';BUILD=ROOT/'scratch/upstream';SWIFT='$LINUX_HOME/.local/share/swiftly/toolchains/6.4.2/usr/bin/swift'
assert platform.system()=='Linux' and platform.machine()=='x86_64'
assert shutil.disk_usage(ROOT).free>=8*1024**3,'Need at least8GiB initial free disk before fresh qualification'
OUT.mkdir(exist_ok=False);BUILD.mkdir(parents=True,exist_ok=False)
ENV=os.environ.copy();ENV.update(PATH=str(Path(SWIFT).parent)+':/usr/bin:/bin',LD_LIBRARY_PATH=str(Path(SWIFT).parents[1]/'lib/swift/linux'),TMPDIR=str(ROOT/'tmp'),CLANG_MODULE_CACHE_PATH=str(ROOT/'scratch/clang-upstream'),GIT_TERMINAL_PROMPT='0',GIT_SSH_COMMAND='false',GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='credential.helper',GIT_CONFIG_VALUE_0='',GIT_CONFIG_KEY_1='credential.interactive',GIT_CONFIG_VALUE_1='false',LANG='C',LC_ALL='C',TZ='UTC')
for p in [ROOT/'tmp',ROOT/'cache/upstream',ROOT/'config/upstream',ROOT/'security/upstream']:p.mkdir(parents=True,exist_ok=True)
freeze=json.loads((ROOT/'control/upstream-source-freeze.json').read_text());pins={p['identity']:p['state'] for p in freeze['pins']};assert len(pins)==5

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
def capture(cmd):
 p=subprocess.run(cmd,cwd=SRC,env=ENV,capture_output=True,text=True);return {'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def preserve_source():
 actual={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob('*') if p.is_file()};assert actual==freeze['files'];return {'passed':True,'files':len(actual),'pins':json.loads((SRC/'Package.resolved').read_text())['pins'],'threshold_files':sum(x.startswith('Benchmarks/Thresholds/') and x.endswith('.json') for x in actual)}
def check_pins():
 state=json.loads((BUILD/'workspace-state.json').read_text());deps=state['object']['dependencies'];actual={x['packageRef']['identity']:x['state']['checkoutState'] for x in deps};assert actual==pins,(actual,pins);rows=[]
 for d in deps:
  p=BUILD/'checkouts'/d['subpath'];head=capture(['git','-C',str(p),'rev-parse','HEAD']);status=capture(['git','-C',str(p),'status','--porcelain']);assert head['exit_code']==status['exit_code']==0 and head['stdout'].strip()==d['state']['checkoutState']['revision'] and not status['stdout'];rows.append({'identity':d['packageRef']['identity'],'revision':head['stdout'].strip(),'clean':True})
 return rows
common=['--scratch-path',str(BUILD),'--cache-path',str(ROOT/'cache/upstream'),'--config-path',str(ROOT/'config/upstream'),'--security-path',str(ROOT/'security/upstream'),'--disable-netrc','--disable-sandbox','-j','4']
summary={'started_at':now(),'passed':False,'source_merge':freeze['expected_merge'],'source_tree':freeze['tree'],'steps':[],'timed_workloads':False,'initial_disk':shutil.disk_usage(ROOT)._asdict()}
try:
 summary['entry']=preserve_source();summary['swift']=capture([SWIFT,'--version']);assert summary['swift']['exit_code']==0 and 'Swift version 6.4.2' in summary['swift']['stdout']
 steps=[]
 for config in ['debug','release']:
  for target in ['CIDR','CIDRArgumentParser','CIDRPOSIX','CIDRNIO']:steps.append((f'{config}-build-{target}',[SWIFT,'build',*common,'--only-use-versions-from-resolved-file','-c',config,'--target',target],False))
  steps.append((f'test-{config}',['./scripts/test.sh',*common,'--disable-automatic-resolution','-c',config],True))
 for name,cmd,is_test in steps:
  assert shutil.disk_usage(ROOT).free>=3*1024**3
  item={'name':name,'command':cmd,'started_at':now(),'free_bytes_before':shutil.disk_usage(ROOT).free};save(OUT/(name+'-started.json'),item);print('START',name,flush=True);log=OUT/(name+'.log');start=time.monotonic()
  with log.open('xb') as f:p=subprocess.run(cmd,cwd=SRC,env=ENV,stdout=f,stderr=subprocess.STDOUT)
  item.update(exit_code=p.returncode,elapsed_s=time.monotonic()-start,finished_at=now(),log=str(log.relative_to(ROOT)),log_sha256=sha(log),free_bytes_after=shutil.disk_usage(ROOT).free)
  if is_test:
   counts=[int(x) for x in re.findall(r'Test run with (\d+) tests? (?:in .*? )?passed',log.read_text(errors='replace'))];item.update(test_counts=counts,total_tests=sum(counts));item['passed']=p.returncode==0 and sum(counts)==311
  else:item['passed']=p.returncode==0
  if item['passed']:item['source_preservation']=preserve_source();item['resolved_dependencies']=check_pins()
  save(OUT/(name+'.json'),item);summary['steps'].append(item);assert item['passed'],name;assert item['free_bytes_after']>=3*1024**3;print('DONE',name,flush=True)
 artifacts={};artifact_paths=[]
 for config in ['debug','release']:
  path=BUILD/'x86_64-unknown-linux-gnu'/config
  for p in path.rglob('*'):
   if not p.is_file() or p.is_symlink():continue
   relative=p.relative_to(BUILD)
   if p.suffix=='.xctest' or any(x.endswith('.resources') for x in relative.parts) or (p.parent.name=='Modules' and p.stem in ['CIDR','CIDRArgumentParser','CIDRPOSIX','CIDRNIO']):
    artifacts[str(relative)]={'bytes':p.stat().st_size,'sha256':sha(p)};artifact_paths.append(p)
 for p in [BUILD/'workspace-state.json',BUILD/'debug.yaml',BUILD/'release.yaml']:
  artifacts[str(p.relative_to(BUILD))]={'bytes':p.stat().st_size,'sha256':sha(p)};artifact_paths.append(p)
 assert sum(name.endswith('.xctest') for name in artifacts)==2
 archive=OUT/'preserved-build-artifacts.tar.gz'
 with tarfile.open(archive,'w:gz',compresslevel=1) as t:
  for p in artifact_paths:t.add(p,arcname=str(p.relative_to(BUILD)),recursive=False)
 verified=set()
 with tarfile.open(archive,'r:gz') as t:
  for m in t:
   assert m.name in artifacts and m.isfile()
   with t.extractfile(m) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==artifacts[m.name]['sha256']
   verified.add(m.name)
 assert verified==set(artifacts)
 summary['preserved_artifacts']={'archive':str(archive.relative_to(ROOT)),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'files':artifacts,'verified_decompressed_hashes':True,'build_scratch_retained':True};save(OUT/'artifact-preservation.json',summary['preserved_artifacts'])
 summary['exit']=preserve_source();summary['passed']=True
except BaseException as e:summary.update(error=repr(e),traceback=traceback.format_exc());raise
finally:
 summary.update(finished_at=now(),final_disk=shutil.disk_usage(ROOT)._asdict());save(OUT/'summary.json',summary);print(json.dumps({'passed':summary['passed'],'receipt':str(OUT/'summary.json')}),flush=True)
