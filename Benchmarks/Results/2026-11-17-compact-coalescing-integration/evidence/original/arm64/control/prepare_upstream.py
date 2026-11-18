#!/usr/bin/env python3
from pathlib import Path
import datetime,hashlib,json,os,shutil,stat,subprocess,tarfile,traceback
ROOT=Path('$EXPERIMENT');ARM=ROOT/'arm64';OLD=Path('$PRIOR_EXPERIMENT/arm64');SEED=Path('$UPSTREAM_REPOSITORY/.build')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(a):return subprocess.check_output([str(x) for x in a],text=True).strip()
receipt={'passed':False,'started_at':now(),'host_free_bytes':shutil.disk_usage(ROOT).free,'scratch_seeds':[],'containers':[],'alternate_relocations':[]}
try:
 assert receipt['host_free_bytes']>10*1024**3
 for base in [ARM/'upstream-6.4.2',ARM/'upstream-6.2.4']:
  for name in ['build','cache','config','security','tmp','clang-cache','control']:(base/name).mkdir(parents=True,exist_ok=True)
 config=ARM/'control/docker-config';config.mkdir();(config/'config.json').write_text('{}'+chr(10))
 run(['/bin/cp','-cR',OLD/'python',ARM/'python'])
 archive=ROOT/'control/upstream-source-portable.tar';assert sha(archive)=='d7fca910ac4e6261bc6b12f2dbaade60a971466e1a871f1abd96a831e8bef5d6'
 source=ARM/'upstream-source';source.mkdir()
 with tarfile.open(archive) as t:
  for m in t.getmembers():assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts,m.name
  t.extractall(source,filter='data')
 manifest=json.loads((ROOT/'control/upstream-source-freeze.json').read_text())
 observed={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}
 assert observed==manifest['files'],(len(observed),len(manifest['files']))
 receipt['source']={'archive':str(archive),'sha256':sha(archive),'tracked_file_count':len(observed),'file_hashes_verified':True,'tree':manifest['tree']}
 expected={x['identity']:x['state'] for x in json.loads((source/'Package.resolved').read_text())['pins']}
 for version in ['6.4.2','6.2.4']:
  build=ARM/('upstream-'+version)/'build'
  for name in ['checkouts','repositories']:run(['/bin/cp','-cR',SEED/name,build/name])
  shutil.copy2(SEED/'workspace-state.json',build/'workspace-state.json')
  state=json.loads((build/'workspace-state.json').read_text());actual={x['packageRef']['identity']:x['state']['checkoutState'] for x in state['object']['dependencies']};assert actual==expected
  for checkout in (build/'checkouts').iterdir():
   alternate=checkout/'.git/objects/info/alternates'
   if alternate.exists():
    before=alternate.read_text();replacements=[]
    for line in before.splitlines():
     old=(alternate.parent.parent/line).resolve() if not line.startswith('/') else Path(line)
     suffix=str(old).split('/repositories/',1)[1];target=build/'repositories'/suffix;assert target.exists();replacements.append(os.path.relpath(target,alternate.parent.parent))
    mode=stat.S_IMODE(alternate.stat().st_mode);alternate.chmod(mode|stat.S_IWUSR);alternate.write_text(chr(10).join(replacements)+chr(10));alternate.chmod(mode)
    receipt['alternate_relocations'].append({'file':str(alternate.relative_to(ROOT)),'before':before,'after':alternate.read_text()})
   head=run(['git','-c','safe.directory='+str(checkout),'-C',checkout,'rev-parse','HEAD']);dirty=run(['git','-c','safe.directory='+str(checkout),'-C',checkout,'status','--porcelain','--untracked-files=all'])
   assert head==expected[checkout.name]['revision'] and not dirty,(checkout.name,head,dirty)
  receipt['scratch_seeds'].append({'target':str(build),'source':str(SEED),'content':['checkouts','repositories','workspace-state.json'],'compiled_products_reused':False,'pins':actual})
 docker=['/usr/local/bin/docker','--config',str(config),'--host','unix://$USER_HOME/.orbstack/run/docker.sock']
 for version,image in [('642','sha256:23d9b28ad97fb1cf1999edc3a0cb265ee915ed42299a9344e7173d5a6d2b05f4'),('624','sha256:e508ef1e4be68087f720de622b91cbf1e32799a7aa96134b35e6f1a1d656db7a')]:
  name='coalescing-release-arm'+version+'-20261118T031137Z';inspection=json.loads(run(docker+['image','inspect',image]))[0];assert inspection['Architecture']=='arm64'
  command=docker+['create','--name',name,'--pull=never','--platform','linux/arm64','--network','none','--init','--workdir','$PLATFORM','--env','PYTHONHOME=$PLATFORM/python','--env','PYTHONDONTWRITEBYTECODE=1','--mount','type=bind,source='+str(ARM)+',target=$PLATFORM','--mount','type=bind,source='+str(ROOT)+',target=$EXPERIMENT,readonly',image,'sleep','infinity']
  cid=run(command);receipt['containers'].append({'name':name,'image':image,'id':cid,'command':command,'image_inspection':inspection});run(docker+['start',name])
 receipt.update(passed=True,python_source=str(OLD/'python'),script_sha256=sha(Path(__file__)),network_access='disabled; cached pinned images; empty Docker config')
except BaseException as e:receipt.update(error=repr(e),traceback=traceback.format_exc());raise
finally:
 receipt['finished_at']=now()
 with (ARM/'control/upstream-preparation.json').open('x') as f:json.dump(receipt,f,indent=2);f.write(chr(10))
 print(json.dumps({'passed':receipt['passed'],'containers':[x['name'] for x in receipt['containers']],'compiled_products_reused':False}),flush=True)
