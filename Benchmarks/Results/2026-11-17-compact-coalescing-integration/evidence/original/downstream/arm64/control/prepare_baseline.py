#!/usr/bin/env python3
from pathlib import Path
import datetime,hashlib,json,os,shutil,stat,subprocess,tarfile,traceback
EXPERIMENT=Path('$EXPERIMENT');ROOT=EXPERIMENT/'downstream/arm64';SEED=Path('$REPOSITORY/.build');OLDPY=EXPERIMENT/'arm64/python';record={'passed':False,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seeds':[],'alternate_relocations':[]}
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):return subprocess.check_output([str(x) for x in args],text=True).strip()
try:
 record['host_free_bytes']=shutil.disk_usage(ROOT).free;assert record['host_free_bytes']>10*1024**3
 for name in ['bin','sources','build','cache','config','security','tmp','clang-cache','runtime/lib','metadata']:(ROOT/name).mkdir(parents=True,exist_ok=True)
 config=ROOT/'control/docker-config';config.mkdir();(config/'config.json').write_text('{}'+chr(10));run(['/bin/cp','-cR',OLDPY,ROOT/'python'])
 archive=EXPERIMENT/'control/cidrmerge-baseline-portable.tar';manifest=json.loads((EXPERIMENT/'control/cidrmerge-baseline-freeze.json').read_text());assert sha(archive)==manifest['archive_sha256']=='17b550797da0292f42759b83929b9f6dda1489334ad5f9a9417e23a84efdcf80';source=ROOT/'sources/B';source.mkdir()
 with tarfile.open(archive) as tar:
  assert all(x.isfile() and not Path(x.name).is_absolute() and '..' not in Path(x.name).parts for x in tar.getmembers());tar.extractall(source,filter='data')
 actual={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()};assert actual==manifest['files'];record['source']={'commit':manifest['commit'],'tree':manifest['tree'],'file_count':len(actual),'archive_sha256':sha(archive),'verified_all_hashes':True};expected={p['identity']:p['state'] for p in json.loads((source/'Package.resolved').read_text())['pins']};assert len(expected)==8
 for name in ['B-ordinary','B-tests']:
  build=ROOT/'build'/name;build.mkdir()
  for item in ['checkouts','repositories']:run(['/bin/cp','-cR',SEED/item,build/item])
  shutil.copy2(SEED/'workspace-state.json',build/'workspace-state.json');state=json.loads((build/'workspace-state.json').read_text());assert {x['packageRef']['identity']:x['state']['checkoutState'] for x in state['object']['dependencies']}==expected
  for checkout in (build/'checkouts').iterdir():
   alternate=checkout/'.git/objects/info/alternates'
   if alternate.exists():
    before=alternate.read_text();targets=[]
    for line in before.splitlines():
     old=(alternate.parent.parent/line).resolve() if not line.startswith('/') else Path(line);target=build/'repositories'/str(old).split('/repositories/',1)[1];assert target.exists();targets.append(os.path.relpath(target,alternate.parent.parent))
    mode=stat.S_IMODE(alternate.stat().st_mode);alternate.chmod(mode|stat.S_IWUSR);alternate.write_text(chr(10).join(targets)+chr(10));alternate.chmod(mode);record['alternate_relocations'].append({'file':str(alternate.relative_to(ROOT)),'before':before,'after':alternate.read_text()})
   git=['git','-c','safe.directory='+str(checkout),'-C',checkout];assert run(git+['rev-parse','HEAD'])==expected[checkout.name]['revision'];assert not run(git+['status','--porcelain','--untracked-files=all'])
  record['seeds'].append({'name':name,'source':str(SEED),'compiled_products_reused':False,'eight_pins':expected})
 docker=['/usr/local/bin/docker','--config',str(config),'--host','unix://$USER_HOME/.orbstack/run/docker.sock'];image='sha256:23d9b28ad97fb1cf1999edc3a0cb265ee915ed42299a9344e7173d5a6d2b05f4';inspection=json.loads(run(docker+['image','inspect',image]))[0];assert inspection['Architecture']=='arm64';name='coalescing-downstream-arm642-20261118T031137Z';command=docker+['create','--name',name,'--pull=never','--platform','linux/arm64','--network','none','--init','--workdir','$PLATFORM','--env','PYTHONHOME=$PLATFORM/python','--env','PYTHONDONTWRITEBYTECODE=1','--mount','type=bind,source='+str(ROOT)+',target=$PLATFORM','--mount','type=bind,source='+str(EXPERIMENT)+',target=$EXPERIMENT,readonly',image,'sleep','infinity'];cid=run(command);run(docker+['start',name]);record.update(passed=True,container={'name':name,'id':cid,'image':image,'command':command,'inspection':inspection},source_pins_unchanged=True,script_sha256=sha(Path(__file__)))
except BaseException as error:record.update(error=repr(error),traceback=traceback.format_exc());raise
finally:
 record['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (ROOT/'control/B-preparation.json').open('x') as f:json.dump(record,f,indent=2);f.write(chr(10))
 print(json.dumps({'passed':record['passed'],'container':record.get('container',{}).get('name')}),flush=True)
