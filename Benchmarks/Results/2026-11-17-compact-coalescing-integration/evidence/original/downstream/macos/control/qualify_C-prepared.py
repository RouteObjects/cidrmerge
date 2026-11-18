from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[3]
P=R/'downstream/macos';S=P/'sources/C';F=json.loads((R/'control/cidrmerge-candidate-freeze.json').read_text());assert (R/'control/upstream-publication.json').exists(), 'Published upstream receipt is required before candidate qualification'
ENV=os.environ.copy();ENV.update(DEVELOPER_DIR='/Applications/Xcode-27.2.0.app/Contents/Developer',TMPDIR=str(P/'tmp')+'/',CLANG_MODULE_CACHE_PATH=str(P/'build/module-cache'),GIT_TERMINAL_PROMPT='0',GIT_SSH_COMMAND='false')
O=P/'control/B-qualification';O.mkdir(exist_ok=False)
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def out(argv):return subprocess.check_output(argv,cwd=S,env=ENV,text=True)
def verify():
 changed=[n for n,h in F['files'].items() if not (S/n).is_file() or sha(S/n)!=h]
 pins=json.loads((S/'Package.resolved').read_text());assert pins==F['pins'] and len(pins['pins'])==8
 actual={str(p.relative_to(S)) for p in S.rglob('*') if p.is_file()}
 assert actual==set(F['files']),sorted(actual-set(F['files']))
 assert not changed,changed
 if (P/'bin/C').exists() and (P/'metadata/C-ordinary.json').exists():assert sha(P/'bin/C')==json.loads((P/'metadata/C-ordinary.json').read_text())['sha256']
 return {'passed':True,'file_count':len(actual),'all_source_hashes_match':True,'eight_pins_match':True,'free_bytes':shutil.disk_usage(P).free}
def run(name,argv,test=False):
 print('START',name,flush=True);d={'name':name,'command':argv,'started_at':now()};log=P/'logs'/(name+'.log')
 with log.open('xb') as f:proc=subprocess.run(argv,cwd=S,env=ENV,stdout=f,stderr=subprocess.STDOUT)
 d.update(exit_code=proc.returncode,finished_at=now(),log=str(log.relative_to(R)),log_sha256=sha(log));d['passed']=proc.returncode==0
 if test:
  d['test_counts']=[int(x) for x in re.findall(r'Test run with (\d+) tests? (?:in .*? )?passed',log.read_text(errors='replace'))];d['total_tests']=sum(d['test_counts']);d['passed']=d['passed'] and d['total_tests']==85
 d['preservation']=verify();save(O/(name+'.json'),d);Q['steps'].append(d);print(json.dumps({'name':name,'passed':d['passed'],'exit_code':proc.returncode,'total_tests':d.get('total_tests')}),flush=True);return d
Q={'passed':False,'variant':'C','source_commit':F['commit'],'source_freeze':'control/cidrmerge-candidate-freeze.json','started_at':now(),'steps':[],'timed_measurements_started':False}
try:
 Q['entry']=verify();Q['swift_version']=out(['swift','--version']);assert 'Swift version 6.4.2' in Q['swift_version'];Q['xcode_version']=out(['xcodebuild','-version'])
 sdk=out(['xcrun','--sdk','macosx','--show-sdk-path']).strip();swift=Path(out(['xcrun','--find','swift']).strip()).resolve();Q['compiler']={'path':str(swift),'sha256':sha(swift),'sdk':sdk}
 Q['environment']={k:ENV[k] for k in ['DEVELOPER_DIR','TMPDIR','CLANG_MODULE_CACHE_PATH']};Q['system']={'sw_vers':out(['sw_vers']),'uname':out(['uname','-a']),'hardware':out(['sysctl','hw.model','hw.ncpu','hw.memsize'])}
 ordinary=P/'build/C-ordinary';d=run('C-ordinary-release',['swift','build','--scratch-path',str(ordinary),'--only-use-versions-from-resolved-file','-j','6','-c','release','--product','cidrmerge']);assert d['passed'],d
 binary=Path(out(['swift','build','--scratch-path',str(ordinary),'--only-use-versions-from-resolved-file','-c','release','--show-bin-path']).strip())/'cidrmerge';shutil.copy2(binary,P/'bin/C');assert sha(binary)==sha(P/'bin/C')
 v=out([str(P/'bin/C'),'--version']);assert v=='0.4.2\n',v
 meta={'passed':True,'variant':'C','source_commit':F['commit'],'frozen_at':now(),'path':str(P/'bin/C'),'build_artifact':str(binary),'sha256':sha(P/'bin/C'),'bytes':(P/'bin/C').stat().st_size,'version':v,'ordinary_unstripped':True,'compiler':Q['compiler'],'swift_version':Q['swift_version'],'otool_L':out(['otool','-L',str(P/'bin/C')]),'otool_l':out(['otool','-l',str(P/'bin/C')]),'file':out(['file',str(P/'bin/C')]),'runtime_note':'macOS system libraries are provided by this host/shared cache; linkage and OS identity are captured, not claimed as copied runtime files.'};save(P/'metadata/C-ordinary.json',meta)
 test=P/'build/C-tests'
 for config in ['debug','release']:run('C-test-'+config,['./scripts/test.sh','--scratch-path',str(test),'--disable-automatic-resolution','-j','6','-c',config],True)
 Q['exit']=verify();Q['binary_metadata']='downstream/macos/metadata/C-ordinary.json';Q['passed']=all(x['passed'] for x in Q['steps'])
except BaseException as e:Q['error']=repr(e);raise
finally:
 Q['finished_at']=now();save(O/'summary.json',Q);print(json.dumps({'passed':Q['passed'],'receipt':str(O/'summary.json')}),flush=True)
raise SystemExit(0 if Q['passed'] else 1)
