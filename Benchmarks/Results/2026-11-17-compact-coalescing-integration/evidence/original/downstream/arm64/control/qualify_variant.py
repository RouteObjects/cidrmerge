#!/usr/bin/env python3
"""Isolated ordinary release build, binary freeze, then separate full test builds."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,re,shutil,subprocess,time,traceback
p=argparse.ArgumentParser();p.add_argument('--variant',choices=['B','C'],required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--expected-tests',type=int,default=85);a=p.parse_args();ROOT=Path('$PLATFORM');SOURCE=ROOT/'sources'/a.variant;SWIFT='/usr/bin/swift';OUT=ROOT/'control'/(a.variant+'-qualification');OUT.mkdir(exist_ok=False);manifest=json.loads(a.manifest.read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
def capture(cmd,env=None):return subprocess.check_output([str(x) for x in cmd],text=True,env=env)
def source_files():return {str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file()}
def verify_pins(build):
 expected={x['identity']:x['state'] for x in json.loads((SOURCE/'Package.resolved').read_text())['pins']};actual={}
 for dep in json.loads((build/'workspace-state.json').read_text())['object']['dependencies']:
  identity=dep['packageRef']['identity'];assert dep['packageRef']['kind']=='remoteSourceControl' and dep['state']['name']=='sourceControlCheckout';actual[identity]=dep['state']['checkoutState'];checkout=build/'checkouts'/dep['subpath'];git=['git','-c','safe.directory='+str(checkout),'-C',str(checkout)];assert capture(git+['rev-parse','HEAD']).strip()==actual[identity]['revision'];assert not capture(git+['status','--porcelain','--untracked-files=all'])
 assert actual==expected and len(actual)==8;return actual
receipt={'passed':False,'variant':a.variant,'started_at':now(),'script_sha256':sha(Path(__file__)),'source_manifest_sha256':sha(a.manifest),'steps':[]}
try:
 frozen=source_files();assert frozen==manifest['files'];swift=capture([SWIFT,'--version']);assert 'Swift version 6.4.2' in swift and platform.machine()=='aarch64';target=json.loads(capture([SWIFT,'-print-target-info']));env=dict(os.environ);env.update(PATH=str(Path(SWIFT).resolve().parent)+':/usr/bin:/bin',LD_LIBRARY_PATH=':'.join(target['paths']['runtimeLibraryPaths']),LANG='C',LC_ALL='C',TZ='UTC',TMPDIR=str(ROOT/'tmp'),CLANG_MODULE_CACHE_PATH=str(ROOT/'clang-cache'))
 host={'at':now(),'architecture':platform.machine(),'swift':swift,'swift_sha256':sha(Path(SWIFT).resolve()),'target_info':target,'kernel':platform.release(),'cpu_affinity':sorted(os.sched_getaffinity(0)),'cpuinfo':Path('/proc/cpuinfo').read_text(),'meminfo':Path('/proc/meminfo').read_text(),'os_release':Path('/etc/os-release').read_text(),'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text(),'memory_events_before':Path('/sys/fs/cgroup/memory.events').read_text(),'disk_free_before':shutil.disk_usage(ROOT).free};assert host['disk_free_before']>=10*1024**3;save(OUT/'environment.json',host)
 for action,configuration,scratch_suffix in [('build','release','ordinary'),('test','debug','tests'),('test','release','tests')]:
  build=ROOT/'build'/(a.variant+'-'+scratch_suffix);verify_pins(build);trusted=[str(x) for x in sorted((build/'checkouts').iterdir())];step_env=dict(env);step_env['GIT_CONFIG_COUNT']=str(len(trusted))
  for i,x in enumerate(trusted):step_env['GIT_CONFIG_KEY_'+str(i)]='safe.directory';step_env['GIT_CONFIG_VALUE_'+str(i)]=x
  command=[SWIFT,action,'--package-path',str(SOURCE),'--scratch-path',str(build),'--cache-path',str(ROOT/'cache'),'--config-path',str(ROOT/'config'),'--security-path',str(ROOT/'security'),'--disable-netrc','--skip-update','--only-use-versions-from-resolved-file','--disable-sandbox','--build-system','native','-c',configuration,'-j','8']
  if action=='build':command+=['--product','cidrmerge']
  label=action+'-'+configuration;rec={'label':label,'command':command,'started_at':now(),'disk_free_before':shutil.disk_usage(ROOT).free};assert rec['disk_free_before']>=3*1024**3;save(OUT/(label+'-started.json'),rec);print('START',a.variant,label,flush=True);start=time.monotonic();log=OUT/(label+'.log')
  with log.open('x') as f:proc=subprocess.run(command,cwd=ROOT,env=step_env,stdout=f,stderr=subprocess.STDOUT)
  rec.update(exit_code=proc.returncode,elapsed_s=time.monotonic()-start,finished_at=now(),log_sha256=sha(log));rec['pins']=verify_pins(build)
  if proc.returncode==0 and action=='test':
   matches=re.findall(r'Test run with (\d+) tests? in (\d+) suites? passed',log.read_text(errors='replace'));rec['test_count']=sum(int(x) for x,_ in matches);rec['test_summaries']=matches
  if proc.returncode==0 and action=='build':
   original=build/'aarch64-unknown-linux-gnu/release/cidrmerge';binary=ROOT/'bin'/a.variant;assert not binary.exists();shutil.copy2(original,binary);assert capture([binary,'--version'],env=env)=='0.4.2\n';stripdir=ROOT/'bin/stripped';stripdir.mkdir(exist_ok=True);stripped=stripdir/a.variant;shutil.copy2(binary,stripped);subprocess.run(['strip','--strip-unneeded',str(stripped)],check=True);ldd=capture(['ldd',binary],env=env);assert 'not found' not in ldd;libs={}
   for name in re.findall(r'(?:=>\s+)?(/[^\s(]+)',ldd):
    path=Path(name);digest=sha(path);destination=ROOT/'runtime/lib'/path.name
    if destination.exists():assert sha(destination)==digest
    else:shutil.copy2(path.resolve(),destination)
    libs[name]={'sha256':digest,'bytes':path.stat().st_size,'frozen_path':str(destination),'frozen_sha256':sha(destination)}
   metadata={'passed':True,'variant':a.variant,'binary':str(binary),'sha256':sha(binary),'bytes':binary.stat().st_size,'stripped_path':str(stripped),'stripped_sha256':sha(stripped),'stripped_bytes':stripped.stat().st_size,'elf_header':capture(['readelf','-hW',binary]),'architecture':'aarch64','file_utility_available':shutil.which('file') is not None,'version':'0.4.2','ldd':ldd,'readelf_dynamic':capture(['readelf','-dW',binary]),'runtime_libraries':libs,'frozen_before_test_builds':True,'swift_sha256':host['swift_sha256'],'source_manifest_sha256':sha(a.manifest),'ordinary_scratch':str(build),'created_at':now()};save(ROOT/'metadata'/(a.variant+'-ordinary.json'),metadata);rec['binary_sha256']=metadata['sha256'];rec['stripped_bytes']=metadata['stripped_bytes'];rec['ordinary_binary_frozen_before_tests']=True
  save(OUT/(label+'.json'),rec);receipt['steps'].append(rec);print('DONE',a.variant,label,'exit',proc.returncode,'tests',rec.get('test_count'),flush=True);assert proc.returncode==0
  if action=='test':assert rec['test_count']==a.expected_tests
 assert source_files()==frozen
 for suffix in ['ordinary','tests']:verify_pins(ROOT/'build'/(a.variant+'-'+suffix))
 metadata=json.loads((ROOT/'metadata'/(a.variant+'-ordinary.json')).read_text());assert sha(ROOT/'bin'/a.variant)==metadata['sha256'];receipt.update(passed=True,source_unchanged=True,pins_unchanged=True,ordinary_binary_unchanged_after_tests=True,test_count_debug=a.expected_tests,test_count_release=a.expected_tests,memory_events_after=Path('/sys/fs/cgroup/memory.events').read_text(),disk_free_after=shutil.disk_usage(ROOT).free)
except BaseException as error:receipt.update(error=repr(error),traceback=traceback.format_exc());raise
finally:receipt['finished_at']=now();save(OUT/'summary.json',receipt);print('SUMMARY',a.variant,receipt['passed'],flush=True)
