from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys,time
R=Path(__file__).resolve().parents[1];P=R/'macos';V,action,config=sys.argv[1:];assert V in ('B','C') and action in ('build','test') and config in ('debug','release')
for name in ('control','logs','tmp','bin','cache','config','security','clang-cache'): (P/name).mkdir(parents=True,exist_ok=True)
source=R/'sources'/V;swift='/Applications/Xcode-27.2.0.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift';env=dict(os.environ,DEVELOPER_DIR='/Applications/Xcode-27.2.0.app/Contents/Developer',TMPDIR=str(P/'tmp'),CLANG_MODULE_CACHE_PATH=str(P/'clang-cache'))
flags=['--package-path',str(source),'--scratch-path',str(P/'build'/V),'--cache-path',str(P/'cache'),'--config-path',str(P/'config'),'--security-path',str(P/'security'),'--disable-netrc','--disable-sandbox','--only-use-versions-from-resolved-file','--skip-update','-c',config,'-j','8']
cmd=[swift,action,*flags]+(['--product','cidrmerge'] if action=='build' else []);label=f'{V}-{action}-{config}';log=P/'logs'/(label+'.log');receipt=P/'control'/(label+'.json');assert not log.exists() and not receipt.exists()
rec={'command':cmd,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'swift':subprocess.check_output([swift,'--version'],env=env,text=True)};start=time.monotonic()
with log.open('x') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
rec.update(exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
if p.returncode==0:
 if action=='build':
  path=Path(subprocess.check_output([swift,'build',*flags,'--show-bin-path'],env=env,text=True).strip())/'cidrmerge';target=P/'bin'/V;assert not target.exists();shutil.copy2(path,target);rec['binary_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
 else:rec['test_summaries']=re.findall(r'Test run with (\d+) tests? in (\d+) suites? passed',log.read_text(errors='replace'));assert rec['test_summaries']
receipt.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True);sys.exit(p.returncode)
