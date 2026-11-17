#!/usr/bin/env python3
"""Offline validation in fresh scratch trees; never change frozen source or timing binaries."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,stat,subprocess,traceback,shlex
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--baseline-source',type=Path);p.add_argument('--seed',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--release-style-binary',type=Path);p.add_argument('--swift',default='/usr/bin/swift');p.add_argument('--jobs',type=int,default=8);a=p.parse_args()
source=a.source.resolve();output=a.output.resolve();binary=a.binary.resolve();output.mkdir(parents=True,exist_ok=False)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):
 with Path(p).open('x') as f:json.dump(x,f,indent=2);f.write(chr(10))
def inventory(base):return {str(p.relative_to(base)):sha(p) for p in base.rglob('*') if p.is_file() and '.git' not in p.relative_to(base).parts}
record={'passed':False,'started_at':now(),'script_sha256':sha(Path(__file__)),'source':str(source),'binary':str(binary),'binary_sha256':sha(binary),'source_inventory':inventory(source),'steps':[]}
env=dict(os.environ,LANG='C',LC_ALL='C',TZ='UTC',TMPDIR=str(output/'tmp'),CLANG_MODULE_CACHE_PATH=str(output/'clang-cache'));(output/'tmp').mkdir();(output/'clang-cache').mkdir();env['PATH']=str(Path(a.swift).resolve().parent)+':/usr/bin:/bin'
trusted=[]
def trust(path):
 trusted.append(str(path));env['GIT_CONFIG_COUNT']=str(len(trusted))
 for i,value in enumerate(trusted):env[f'GIT_CONFIG_KEY_{i}']='safe.directory';env[f'GIT_CONFIG_VALUE_{i}']=value

def run(label,cmd,cwd=output,custom_env=None,expected_codes=(0,),empty_output=False):
 step={'label':label,'command':[str(x) for x in cmd],'cwd':str(cwd),'started_at':now()};save(output/(label+'-started.json'),step)
 with (output/(label+'.log')).open('x') as h:q=subprocess.run(step['command'],cwd=cwd,env=custom_env or env,stdout=h,stderr=subprocess.STDOUT)
 step.update(exit_code=q.returncode,finished_at=now(),log_sha256=sha(output/(label+'.log')));save(output/(label+'.json'),step);record['steps'].append(step);print(label,q.returncode,flush=True)
 if q.returncode not in expected_codes or (empty_output and (output/(label+'.log')).stat().st_size):raise RuntimeError(label+' failed; evidence retained')

def seed(target):
 target.mkdir()
 for name in ['checkouts','repositories']:shutil.copytree(a.seed/name,target/name,symlinks=True)
 shutil.copy2(a.seed/'workspace-state.json',target/'workspace-state.json')
 for checkout in (target/'checkouts').iterdir():
  trust(checkout);alt=checkout/'.git/objects/info/alternates'
  if alt.exists():
   lines=alt.read_text().splitlines();replacement=[]
   for line in lines:
    old=(alt.parent.parent/line).resolve() if not line.startswith('/') else Path(line)
    suffix=str(old).split('/repositories/',1)[1];dest=target/'repositories'/suffix;assert dest.exists();replacement.append(os.path.relpath(dest,alt.parent.parent))
   mode=stat.S_IMODE(alt.stat().st_mode);alt.chmod(mode|stat.S_IWUSR);alt.write_text(chr(10).join(replacement)+chr(10));alt.chmod(mode)
 return target

def swift_build(package,scratch,extra):
 return [a.swift,'build','--package-path',str(package),'--scratch-path',str(scratch),'--cache-path',str(output/'cache'),'--config-path',str(output/'config'),'--security-path',str(output/'security'),'--disable-netrc','--skip-update','--only-use-versions-from-resolved-file','--disable-sandbox','--build-system','native','-j',str(a.jobs),*extra]
try:
 clone=output/'source';shutil.copytree(source,clone,symlinks=True);assert inventory(clone)==record['source_inventory'];trust(clone)
 run('source-git-init',['git','init','--quiet',str(clone)]);run('source-git-index',['git','-C',str(clone),'add','--force','--all']);baseline=(a.baseline_source or source.parent/'B').resolve();assert baseline.is_dir();run('whitespace',['git','diff','--no-index','--check',str(baseline),str(source)],expected_codes=(0,1),empty_output=True)
 scripts=clone/'scripts';assert scripts.is_dir()
 run('content-audit',['bash',str(scripts/'audit-release-content.sh'),'tree'])
 run('format',[a.swift,'format','lint','--configuration',str(clone/'.swift-format.json'),'--recursive','--strict',str(clone/'Package.swift'),str(clone/'Sources'),str(clone/'Tests'),str(clone/'Benchmarks')])
 docbuild=seed(output/'docs-build');graphs=output/'symbol-graphs';graphs.mkdir()
 run('documentation-symbol-graph',swift_build(clone,docbuild,['--target','CIDRMergeCore','-Xswiftc','-emit-symbol-graph','-Xswiftc','-emit-symbol-graph-dir','-Xswiftc',str(graphs),'-Xswiftc','-symbol-graph-minimum-access-level','-Xswiftc','public']))
 graph=graphs/'CIDRMergeCore.symbols.json';symbols=json.loads(graph.read_text());assert symbols['module']['name']=='CIDRMergeCore' and any(s['names']['title']=='CIDRMergeCoverage' for s in symbols['symbols'])
 catalog=clone/'Sources/CIDRMergeCore/CIDRMergeCore.docc';assert (catalog/'CIDRMergeCore.md').is_file() and (catalog/'CompilingSearchbotPrefixLists.md').is_file()
 if os.uname().sysname=='Darwin':
  docgraphs=output/'docc-symbol-graphs';docgraphs.mkdir();shutil.copy2(graph,docgraphs/graph.name);archive=output/'CIDRMergeCore.doccarchive'
  run('documentation-convert',['xcrun','docc','convert',str(catalog),'--additional-symbol-graph-dir',str(docgraphs),'--output-path',str(archive),'--fallback-display-name','CIDRMergeCore','--fallback-bundle-identifier','org.routeobjects.cidrmerge.core','--fallback-default-module-kind','Library','--warnings-as-errors']);assert (archive/'metadata.json').stat().st_size>0
  for n in ['cidrmergecore.json','compilingsearchbotprefixlists.json']:assert any(p.stat().st_size for p in (archive/'data/documentation').rglob(n))
 consumer=output/'consumer';(consumer/'Sources/CoreConsumer').mkdir(parents=True);original=(scripts/'check-core-consumer.sh').read_text();manifest=re.search(r'cat >"\$\{CONSUMER_ROOT\}/Package.swift" <<EOF\n(.*?)\nEOF',original,re.S)[1].replace('${PACKAGE_ROOT}',str(clone));program=re.search(r'cat >"\$\{CONSUMER_ROOT\}/Sources/CoreConsumer/main.swift" <<\x27EOF\x27\n(.*?)\nEOF',original,re.S)[1];(consumer/'Package.swift').write_text(manifest+chr(10));(consumer/'Sources/CoreConsumer/main.swift').write_text(program+chr(10));shutil.copy2(source/'Package.resolved',consumer/'Package.resolved');consumerbuild=seed(output/'consumer-build')
 run('core-consumer-build',swift_build(consumer,consumerbuild,['--product','CoreConsumer']))
 expectedpins=json.loads((source/'Package.resolved').read_text())['pins'];actualpins=json.loads((consumer/'Package.resolved').read_text())['pins'];assert expectedpins==actualpins and len(expectedpins)==8
 forbidden=[]
 for module in ['Crypto.swiftmodule','SystemPackage.swiftmodule']:
  forbidden += [str(x.relative_to(consumerbuild)) for x in consumerbuild.rglob(module)]
 assert not forbidden,forbidden
 executables=[p for p in consumerbuild.glob('*/debug/CoreConsumer') if p.is_file()];assert len(executables)==1,executables
 run('core-consumer-run',[str(executables[0])]);assert (output/'core-consumer-run.log').read_bytes()==b'192.0.2.0...192.0.2.191\n2001:db8::...2001:db8::ffff\n'
 save(output/'core-boundary.json',{'passed':True,'forbidden_compiled_modules':['Crypto.swiftmodule','SystemPackage.swiftmodule'],'found':forbidden,'lockfile_pins_equal':True,'dependency_pin_count':len(expectedpins),'program_sha256':sha(consumer/'Sources/CoreConsumer/main.swift')})
 smoke=(scripts/'smoke-test.sh').read_text();begin='swift build --package-path "$PACKAGE_ROOT" -c release --product cidrmerge\nBINARY_DIRECTORY="$(swift build --package-path "$PACKAGE_ROOT" -c release --show-bin-path)"\nBINARY="$BINARY_DIRECTORY/cidrmerge"';assert begin in smoke;smoke=smoke.replace(begin,'BINARY_DIRECTORY='+shlex.quote(str(binary.parent))+'\nBINARY='+shlex.quote(str(binary)));smoke=smoke.replace('rm -rf -- "$TEMPORARY_DIRECTORY"',': # Preserve this experiment smoke workspace');smoke=smoke.replace('PACKAGE_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"','PACKAGE_ROOT='+shlex.quote(str(clone)));derived=output/'smoke-frozen.sh';derived.write_text(smoke);save(output/'smoke-adaptation.json',{'original_sha256':sha(scripts/'smoke-test.sh'),'derived_sha256':sha(derived),'changes':['Use separately frozen ordinary release binary instead of rebuilding it','Preserve smoke temporary files','Point package root at validation copy'],'assertions_unchanged':True});run('cli-smoke',['bash',str(derived)])
 if a.release_style_binary:run('release-style-binary-audit',['bash',str(scripts/'audit-release-content.sh'),'binary',str(a.release_style_binary.resolve())])
 assert inventory(source)==record['source_inventory'] and sha(binary)==record['binary_sha256'];record.update(passed=True,frozen_source_unchanged=True,frozen_binary_unchanged=True)
except BaseException as e:record.update(error=repr(e),traceback=traceback.format_exc());raise
finally:record['finished_at']=now();save(output/'summary.json',record);print(json.dumps({'passed':record['passed'],'output':str(output),'error':record.get('error')}),flush=True)
