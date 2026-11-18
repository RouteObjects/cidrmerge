from pathlib import Path
import datetime, hashlib, json, os, re, subprocess, sys
R=Path(__file__).resolve().parents[1]
SRC=R/'sources/upstream-validation'
OUT=R/'macos/upstream-qualification'
OUT.mkdir(parents=True,exist_ok=False)
ENV=os.environ.copy()
ENV.update(DEVELOPER_DIR='/Applications/Xcode-27.2.0.app/Contents/Developer',TMPDIR=str(R/'tmp')+'/',CLANG_MODULE_CACHE_PATH=str(OUT/'clang-module-cache'),GIT_TERMINAL_PROMPT='0',GIT_SSH_COMMAND='false')
(R/'tmp').mkdir(exist_ok=True)
freeze=json.loads((R/'control/upstream-source-freeze.json').read_text())
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def output(args):return subprocess.check_output(args,cwd=SRC,env=ENV,text=True)
def preserve():
 changed=[name for name,want in freeze['files'].items() if not (SRC/name).is_file() or sha(SRC/name)!=want]
 return {'changed_files':changed,'git_status':output(['git','status','--porcelain']),'head':output(['git','rev-parse','HEAD']).strip(),'threshold_files':sum(name.startswith('Benchmarks/Thresholds/') and name.endswith('.json') for name in freeze['files'])}
summary={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'head':freeze['expected_merge'],'steps':[],'timed_benchmarks_started':False}
try:
 summary['entry']=preserve();assert not summary['entry']['changed_files'] and not summary['entry']['git_status']
 summary['swift_version']=output(['swift','--version']);assert 'Swift version 6.4.2' in summary['swift_version']
 summary['xcode_version']=output(['xcodebuild','-version'])
 summary['ios_sdk']=output(['xcrun','--sdk','iphonesimulator','--show-sdk-path']).strip()
 targets=['CIDR','CIDRArgumentParser','CIDRPOSIX','CIDRNIO']
 steps=[]
 for config in ['debug','release']:
  for target in targets:
   steps.append((f'{config}-build-{target}',['swift','build','--scratch-path',str(OUT/'build'),'--only-use-versions-from-resolved-file','-j','6','-c',config,'--target',target],{'MACOSX_DEPLOYMENT_TARGET':'15.0'},False))
  steps.append((f'test-{config}',['./scripts/test.sh','--scratch-path',str(OUT/'build'),'--disable-automatic-resolution','-j','6','-c',config],{},True))
 for target in targets:
  steps.append((f'ios18-build-{target}',['swift','build','--scratch-path',str(OUT/'ios18-build'),'--only-use-versions-from-resolved-file','-j','6','--target',target,'--triple','arm64-apple-ios18.0-simulator','--sdk',summary['ios_sdk']],{},False))
 for target in ['CIDRBenchmarkTarget','CIDRCPUBenchmarkTarget','CIDRNIOBenchmarkTarget','CIDRSummarizationBenchmarkTarget']:
  args=['./scripts/benchmarks.sh','build','--scratch-path',str(OUT/'benchmark-build'),'--only-use-versions-from-resolved-file','-j','6']
  if target=='CIDRSummarizationBenchmarkTarget':args+=['-Xswiftc','-DSUMMARIZATION_APPEND_APIS']
  steps.append((f'benchmark-build-{target}',args,{'CIDR_BENCHMARK_TARGET':target},False))
 steps.append(('benchmark-build-CIDRProfileTarget',['swift','build','--package-path',str(SRC/'Benchmarks'),'--scratch-path',str(OUT/'benchmark-build'),'--only-use-versions-from-resolved-file','-j','6','--product','CIDRProfileTarget'],{},False))
 steps.append(('format-changed-files',['xcrun','swift-format','lint','--strict','--configuration','$USER_HOME/Developer/Route Objects/.swift-format.json',str(SRC/'Sources/CIDR/IPAddressRange.swift'),str(SRC/'Tests/CIDRTests/InPlaceCoalescingTests.swift')],{},False))
 for name,argv,extra,is_test in steps:
  item={'name':name,'command':argv,'environment':extra,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False}
  print(json.dumps({'starting':name}),flush=True)
  env=ENV.copy();env.update(extra)
  log=OUT/(name+'.log')
  with log.open('xb') as stream:process=subprocess.run(argv,cwd=SRC,env=env,stdout=stream,stderr=subprocess.STDOUT)
  item.update(exit_code=process.returncode,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),log=str(log.relative_to(R)),log_sha256=sha(log))
  if is_test:
   counts=[int(x) for x in re.findall(r'Test run with (\d+) tests? (?:in .*? )?passed',log.read_text(errors='replace'))]
   item.update(test_counts=counts,total_tests=sum(counts));item['passed']=process.returncode==0 and sum(counts)==311
  else:item['passed']=process.returncode==0
  with (OUT/(name+'.json')).open('x') as f:json.dump(item,f,indent=2);f.write('\n')
  summary['steps'].append(item)
  print(json.dumps(item),flush=True)
  preservation=preserve()
  assert not preservation['changed_files'] and not preservation['git_status'],preservation
 summary['exit']=preserve()
 summary['passed']=all(x['passed'] for x in summary['steps'])
except BaseException as error:
 summary['error']=repr(error);raise
finally:
 summary['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (OUT/'summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
 print(json.dumps({'passed':summary['passed'],'receipt':str(OUT/'summary.json'),'failed_steps':[x['name'] for x in summary['steps'] if not x['passed']]}),flush=True)
if not summary['passed']:raise SystemExit(1)
