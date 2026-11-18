#!/usr/bin/env python3
from pathlib import Path
import datetime,hashlib,json,os,shutil,stat,subprocess,tarfile,traceback
E=Path('$EXPERIMENT');R=E/'downstream/arm64';SEED=Path('$REPOSITORY/.build');record={'passed':False,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seeds':[],'alternate_relocations':[]}
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(a):return subprocess.check_output([str(x) for x in a],text=True).strip()
try:
 assert shutil.disk_usage(R).free>10*1024**3
 archive=E/'control/cidrmerge-candidate-portable.tar';m=json.loads((E/'control/cidrmerge-candidate-freeze.json').read_text());pub=json.loads((E/'control/upstream-publication.json').read_text());assert pub['passed'] and pub['published'] and pub['local_signature_verified'] and pub['github_tag_verification']['verified'];assert pub['version']=='0.11.0' and pub['revision']=='ae956313ebbcb5a6f9d20b74626ce5b6e2e69839';assert sha(E/'control/upstream-publication.json')==m['publication_receipt_sha256'];assert sha(archive)==m['archive_sha256']=='fd04ea7e2e978f06e7852a177897c5cdf1f85cc64cf1a98ec55af28284fa9b3e';source=R/'sources/C';source.mkdir()
 with tarfile.open(archive) as tar:
  assert all(x.isfile() and not Path(x.name).is_absolute() and '..' not in Path(x.name).parts for x in tar.getmembers());tar.extractall(source,filter='data')
 files={str(x.relative_to(source)):sha(x) for x in source.rglob('*') if x.is_file()};assert files==m['files'];baseline=json.loads((E/'control/cidrmerge-baseline-freeze.json').read_text());changes=sorted(x for x in set(files)|set(baseline['files']) if files.get(x)!=baseline['files'].get(x));assert changes==m['changed_files'];assert all(not x.startswith(('Sources/','Tests/')) for x in changes)
 expected={x['identity']:x['state'] for x in json.loads((source/'Package.resolved').read_text())['pins']};b={x['identity']:x['state'] for x in json.loads((R/'sources/B/Package.resolved').read_text())['pins']};assert expected['swift-cidr']=={'version':'0.11.0','revision':pub['revision']};assert {k:v for k,v in expected.items() if k!='swift-cidr'}=={k:v for k,v in b.items() if k!='swift-cidr'}
 floor=R/'floor-6.2.4'
 for name in ['build','cache','config','security','tmp','clang-cache','control']:(floor/name).mkdir(parents=True,exist_ok=True)
 for build in [R/'build/C-ordinary',R/'build/C-tests',floor/'build/C-tests']:
  build.mkdir()
  for item in ['checkouts','repositories']:run(['/bin/cp','-cR',SEED/item,build/item])
  shutil.copy2(SEED/'workspace-state.json',build/'workspace-state.json');state=json.loads((build/'workspace-state.json').read_text());assert {x['packageRef']['identity']:x['state']['checkoutState'] for x in state['object']['dependencies']}==expected
  for checkout in (build/'checkouts').iterdir():
   alternate=checkout/'.git/objects/info/alternates'
   if alternate.exists():
    before=alternate.read_text();targets=[]
    for line in before.splitlines():
     old=(alternate.parent.parent/line).resolve() if not line.startswith('/') else Path(line);target=build/'repositories'/str(old).split('/repositories/',1)[1];assert target.exists();targets.append(os.path.relpath(target,alternate.parent.parent))
    mode=stat.S_IMODE(alternate.stat().st_mode);alternate.chmod(mode|stat.S_IWUSR);alternate.write_text(chr(10).join(targets)+chr(10));alternate.chmod(mode);record['alternate_relocations'].append({'file':str(alternate.relative_to(R)),'before':before,'after':alternate.read_text()})
   git=['git','-c','safe.directory='+str(checkout),'-C',checkout];assert run(git+['rev-parse','HEAD'])==expected[checkout.name]['revision'];assert not run(git+['status','--porcelain','--untracked-files=all'])
  record['seeds'].append({'path':str(build),'source':str(SEED),'compiled_products_reused':False,'eight_pins':expected})
 docker=['/usr/local/bin/docker','--config',str(R/'control/docker-config'),'--host','unix://$USER_HOME/.orbstack/run/docker.sock'];image='sha256:e508ef1e4be68087f720de622b91cbf1e32799a7aa96134b35e6f1a1d656db7a';inspection=json.loads(run(docker+['image','inspect',image]))[0];assert inspection['Architecture']=='arm64';name='coalescing-downstream-arm624-20261118T031137Z';command=docker+['create','--name',name,'--pull=never','--platform','linux/arm64','--network','none','--init','--workdir','$PLATFORM','--env','PYTHONHOME=$PLATFORM/python','--env','PYTHONDONTWRITEBYTECODE=1','--mount','type=bind,source='+str(R)+',target=$PLATFORM','--mount','type=bind,source='+str(E)+',target=$EXPERIMENT,readonly',image,'sleep','infinity'];cid=run(command);run(docker+['start',name]);run(docker+['start','coalescing-downstream-arm642-20261118T031137Z']);record.update(passed=True,source_file_count=len(files),changed_files=changes,cli_source_tests_identical=True,published_upstream={'version':pub['version'],'revision':pub['revision'],'publication_receipt_sha256':sha(E/'control/upstream-publication.json')},container_floor={'name':name,'id':cid,'image':image,'command':command,'inspection':inspection},script_sha256=sha(Path(__file__)))
except BaseException as error:record.update(error=repr(error),traceback=traceback.format_exc());raise
finally:
 record['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (R/'control/C-preparation.json').open('x') as f:json.dump(record,f,indent=2);f.write(chr(10))
 print(json.dumps({'passed':record['passed'],'candidate_files':record.get('source_file_count'),'changed_files':record.get('changed_files')}),flush=True)
