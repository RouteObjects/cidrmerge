#!/usr/bin/env python3
from pathlib import Path
import datetime,hashlib,json,os,platform,re,shutil,subprocess,time,traceback
BASE=Path('$PLATFORM');ROOT=BASE/'floor-6.2.4';SOURCE=BASE/'sources/C';BUILD=ROOT/'build/C-tests';OUT=ROOT/'control/C-qualification';OUT.mkdir(exist_ok=False);MANIFEST=Path('$EXPERIMENT/control/cidrmerge-candidate-freeze.json');SWIFT='/usr/bin/swift'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
def capture(a):return subprocess.check_output([str(x) for x in a],text=True)
def files():return {str(x.relative_to(SOURCE)):sha(x) for x in SOURCE.rglob('*') if x.is_file()}
def pins():
 expected={x['identity']:x['state'] for x in json.loads((SOURCE/'Package.resolved').read_text())['pins']};observed={}
 for dep in json.loads((BUILD/'workspace-state.json').read_text())['object']['dependencies']:
  identity=dep['packageRef']['identity'];assert dep['packageRef']['kind']=='remoteSourceControl' and dep['state']['name']=='sourceControlCheckout';observed[identity]=dep['state']['checkoutState'];p=BUILD/'checkouts'/dep['subpath'];git=['git','-c','safe.directory='+str(p),'-C',p];assert capture(git+['rev-parse','HEAD']).strip()==observed[identity]['revision'];assert not capture(git+['status','--porcelain','--untracked-files=all'])
 assert observed==expected and len(observed)==8;return observed
record={'passed':False,'started_at':now(),'script_sha256':sha(Path(__file__)),'manifest_sha256':sha(MANIFEST),'steps':[]}
try:
 original=files();assert original==json.loads(MANIFEST.read_text())['files'];binary_hashes={v:sha(BASE/'bin'/v) for v in ['B','C']};swift=capture([SWIFT,'--version']);assert 'Swift version 6.2.4' in swift and platform.machine()=='aarch64';target=json.loads(capture([SWIFT,'-print-target-info']));env=dict(os.environ);env.update(PATH=str(Path(SWIFT).resolve().parent)+':/usr/bin:/bin',LD_LIBRARY_PATH=':'.join(target['paths']['runtimeLibraryPaths']),LANG='C',LC_ALL='C',TZ='UTC',TMPDIR=str(ROOT/'tmp'),CLANG_MODULE_CACHE_PATH=str(ROOT/'clang-cache'));trusted=[str(x) for x in sorted((BUILD/'checkouts').iterdir())];env['GIT_CONFIG_COUNT']=str(len(trusted))
 for i,x in enumerate(trusted):env['GIT_CONFIG_KEY_'+str(i)]='safe.directory';env['GIT_CONFIG_VALUE_'+str(i)]=x
 save(OUT/'environment.json',{'swift':swift,'swift_sha256':sha(Path(SWIFT).resolve()),'target_info':target,'architecture':platform.machine(),'kernel':platform.release(),'memory_events_before':Path('/sys/fs/cgroup/memory.events').read_text(),'disk_free_before':shutil.disk_usage(ROOT).free})
 for configuration in ['debug','release']:
  pins();command=[SWIFT,'test','--package-path',str(SOURCE),'--scratch-path',str(BUILD),'--cache-path',str(ROOT/'cache'),'--config-path',str(ROOT/'config'),'--security-path',str(ROOT/'security'),'--disable-netrc','--skip-update','--only-use-versions-from-resolved-file','--disable-sandbox','--build-system','native','-c',configuration,'-j','8'];step={'command':command,'configuration':configuration,'started_at':now(),'free_bytes_before':shutil.disk_usage(ROOT).free};assert step['free_bytes_before']>=3*1024**3;save(OUT/(configuration+'-started.json'),step);start=time.monotonic();log=OUT/(configuration+'.log');print('START floor',configuration,flush=True)
  with log.open('x') as f:proc=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  matches=re.findall(r'Test run with (\d+) tests? in (\d+) suites? passed',log.read_text(errors='replace'));step.update(exit_code=proc.returncode,elapsed_s=time.monotonic()-start,finished_at=now(),test_summaries=matches,test_count=sum(int(n) for n,_ in matches),pins=pins(),log_sha256=sha(log));save(OUT/(configuration+'.json'),step);record['steps'].append(step);print('DONE floor',configuration,'exit',proc.returncode,'tests',step['test_count'],flush=True);assert proc.returncode==0 and step['test_count']==85
 assert files()==original;assert {v:sha(BASE/'bin'/v) for v in ['B','C']}==binary_hashes;record.update(passed=True,test_counts={'debug':85,'release':85},source_and_pins_unchanged=True,ordinary_binaries_unchanged=True,ordinary_binary_hashes=binary_hashes,memory_events_after=Path('/sys/fs/cgroup/memory.events').read_text())
except BaseException as error:record.update(error=repr(error),traceback=traceback.format_exc());raise
finally:record['finished_at']=now();save(OUT/'summary.json',record);print('SUMMARY floor',record['passed'],flush=True)
