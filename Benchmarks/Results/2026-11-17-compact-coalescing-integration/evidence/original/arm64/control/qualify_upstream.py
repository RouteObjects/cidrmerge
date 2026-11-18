#!/usr/bin/env python3
from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,re,shutil,subprocess,time,traceback
p=argparse.ArgumentParser();p.add_argument('--version',choices=['6.4.2','6.2.4'],required=True);a=p.parse_args()
ARM=Path('$PLATFORM');EXPERIMENT=Path('$EXPERIMENT');ROOT=ARM/('upstream-'+a.version);SOURCE=ARM/'upstream-source';OUT=ROOT/'control/qualification-01';OUT.mkdir(exist_ok=False);SWIFT='/usr/bin/swift';BUILD=ROOT/'build'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write(chr(10))
def check(a):return subprocess.check_output(a,text=True)
def files():return {str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file()}
def pins():
 expected={p['identity']:p['state'] for p in json.loads((SOURCE/'Package.resolved').read_text())['pins']};state=json.loads((BUILD/'workspace-state.json').read_text());actual={}
 for x in state['object']['dependencies']:
  name=x['packageRef']['identity'];d=BUILD/'checkouts'/x['subpath'];head=check(['git','-c','safe.directory='+str(d),'-C',str(d),'rev-parse','HEAD']).strip();dirty=check(['git','-c','safe.directory='+str(d),'-C',str(d),'status','--porcelain','--untracked-files=all']);assert not dirty and head==expected[name]['revision'],(name,head,dirty);actual[name]=x['state']['checkoutState']
 assert actual==expected;return actual
receipt={'passed':False,'started_at':now(),'version':a.version,'script_sha256':sha(Path(__file__)),'steps':[]}
try:
 frozen=files();assert frozen==json.loads((EXPERIMENT/'control/upstream-source-freeze.json').read_text())['files'];beforepins=pins();swift=check([SWIFT,'--version']);assert 'Swift version '+a.version in swift and platform.machine()=='aarch64';target=json.loads(check([SWIFT,'-print-target-info']))
 env=dict(os.environ);env.update(PATH=str(Path(SWIFT).resolve().parent)+':/usr/bin:/bin',LD_LIBRARY_PATH=':'.join(target['paths']['runtimeLibraryPaths']),LANG='C',LC_ALL='C',TZ='UTC',TMPDIR=str(ROOT/'tmp'),CLANG_MODULE_CACHE_PATH=str(ROOT/'clang-cache'))
 trusted=[str(x) for x in sorted((BUILD/'checkouts').iterdir())];env['GIT_CONFIG_COUNT']=str(len(trusted))
 for i,x in enumerate(trusted):env['GIT_CONFIG_KEY_'+str(i)]='safe.directory';env['GIT_CONFIG_VALUE_'+str(i)]=x
 host={'at':now(),'swift':swift,'swift_sha256':sha(Path(SWIFT).resolve()),'target_info':target,'architecture':platform.machine(),'kernel':platform.release(),'cpu_affinity':sorted(os.sched_getaffinity(0)),'cpuinfo':Path('/proc/cpuinfo').read_text(),'meminfo':Path('/proc/meminfo').read_text(),'os_release':Path('/etc/os-release').read_text(),'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text(),'memory_events_before':Path('/sys/fs/cgroup/memory.events').read_text(),'disk_free_before':shutil.disk_usage(ROOT).free}
 assert host['disk_free_before']>=10*1024**3;save(OUT/'environment.json',host)
 for configuration in ['debug','release']:
  command=[SWIFT,'test','--package-path',str(SOURCE),'--scratch-path',str(BUILD),'--cache-path',str(ROOT/'cache'),'--config-path',str(ROOT/'config'),'--security-path',str(ROOT/'security'),'--disable-netrc','--skip-update','--only-use-versions-from-resolved-file','--disable-sandbox','--build-system','native','-c',configuration,'-j','8']
  rec={'configuration':configuration,'command':command,'started_at':now(),'disk_free_before':shutil.disk_usage(ROOT).free};save(OUT/(configuration+'-started.json'),rec);print('START',a.version,configuration,flush=True);start=time.monotonic();log=OUT/(configuration+'.log')
  with log.open('x') as f:result=subprocess.run(command,env=env,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  rec.update(exit_code=result.returncode,elapsed_s=time.monotonic()-start,finished_at=now(),log_sha256=sha(log));matches=re.findall(r'Test run with (\d+) tests? in (\d+) suites? passed',log.read_text(errors='replace'));rec['test_summaries']=matches;rec['test_count']=sum(int(n) for n,_ in matches);rec['dependency_pins']=pins();save(OUT/(configuration+'.json'),rec);receipt['steps'].append(rec);print('DONE',a.version,configuration,'exit',result.returncode,'tests',rec['test_count'],flush=True)
  assert result.returncode==0 and rec['test_count']>=303,rec
 assert len({x['test_count'] for x in receipt['steps']})==1
 assert files()==frozen and pins()==beforepins
 receipt.update(passed=True,source_unchanged=True,lockfile_unchanged=True,test_count=receipt['steps'][0]['test_count'],memory_events_after=Path('/sys/fs/cgroup/memory.events').read_text(),disk_free_after=shutil.disk_usage(ROOT).free)
except BaseException as e:receipt.update(error=repr(e),traceback=traceback.format_exc());raise
finally:
 receipt['finished_at']=now();save(OUT/'summary.json',receipt);print('SUMMARY',a.version,receipt['passed'],flush=True)
