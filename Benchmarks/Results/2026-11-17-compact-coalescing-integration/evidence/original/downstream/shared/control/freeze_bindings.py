#!/usr/bin/env python3
"""Bind current published dependencies, immutable sources, binaries, runtime and gates."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,subprocess
p=argparse.ArgumentParser();p.add_argument('--shared',type=Path,required=True);p.add_argument('--baseline-source',type=Path,required=True);p.add_argument('--candidate-source',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--evidence',type=Path,action='append',required=True);p.add_argument('--extra-file',type=Path,action='append',default=[]);p.add_argument('--extra-manifest',type=Path,action='append',default=[]);p.add_argument('--swift',type=Path,required=True);p.add_argument('--runtime-library-path');p.add_argument('--candidate-version',required=True);p.add_argument('--candidate-revision',required=True);p.add_argument('--publication-receipt',type=Path,required=True);p.add_argument('--baseline-workspace',type=Path);p.add_argument('--candidate-workspace',type=Path);a=p.parse_args();files={};sources={};binaries={};receipt={'passed':False,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()};assert not a.output.exists()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def add(p):p=Path(p).resolve();assert p.is_file();files[str(p)]=sha(p)
try:
 for variant,source,binary in [('B',a.baseline_source,a.baseline),('C',a.candidate_source,a.candidate)]:
  source=source.resolve();binary=binary.resolve();inventory={}
  for file in source.rglob('*'):
   if '.git' in file.relative_to(source).parts:continue
   assert not file.is_symlink(),file
   if file.is_file():add(file);inventory[str(file.relative_to(source))]=sha(file)
  pins=json.loads((source/'Package.resolved').read_text())['pins'];assert len(pins)==8;assert all(x['kind']=='remoteSourceControl' for x in pins);assert not re.search(r'\.package\s*\(\s*path\s*:',(source/'Package.swift').read_text());pinmap={x['identity']:x['state'] for x in pins};sources[variant]={'path':str(source),'file_count':len(inventory),'files':inventory,'pins':pinmap};add(binary);binaries[variant]={'path':str(binary),'sha256':sha(binary)}
  env={**os.environ}
  if a.runtime_library_path:env['LD_LIBRARY_PATH']=a.runtime_library_path
  version=subprocess.check_output([str(binary),'--version'],text=True,env=env);assert version=='0.4.2\n',(variant,version)
  if os.uname().sysname=='Linux':
   ldd=subprocess.check_output(['ldd',str(binary)],text=True,env=env);assert 'not found' not in ldd;paths=re.findall(r'(?:=>\s+)?(/[^\s(]+)',ldd);assert paths
   for file in paths:add(file)
   sources[variant]['runtime_ldd']=ldd
 b=sources['B']['pins'];c=sources['C']['pins'];assert b['swift-cidr']=={'revision':'5e4b3d2f881340a6ced05742429f1bd680dfd1e0','version':'0.10.1'};assert a.candidate_version=='0.11.0' and re.fullmatch(r'[0-9a-f]{40}',a.candidate_revision);assert c['swift-cidr']=={'revision':a.candidate_revision,'version':a.candidate_version};assert {k:v for k,v in b.items() if k!='swift-cidr'}=={k:v for k,v in c.items() if k!='swift-cidr'}
 publication=json.loads(a.publication_receipt.read_text());assert publication['passed'] is True and publication['published'] is True;assert publication['version']==a.candidate_version and publication['revision']==a.candidate_revision;assert publication['release_url']=='https://github.com/RouteObjects/swift-cidr/releases/tag/'+a.candidate_version;add(a.publication_receipt)
 workspaces={}
 for variant,workspace in [('B',a.baseline_workspace),('C',a.candidate_workspace)]:
  if workspace is None:continue
  workspace=workspace.resolve();state=json.loads(workspace.read_text());observed={}
  for dependency in state['object']['dependencies']:
   identity=dependency['packageRef']['identity'];assert dependency['packageRef']['kind']=='remoteSourceControl';assert dependency['state']['name']=='sourceControlCheckout';observed[identity]=dependency['state']['checkoutState'];checkout=workspace.parent/'checkouts'/dependency['subpath'];git=['git','-c','safe.directory='+str(checkout),'-C',str(checkout)];assert subprocess.check_output([*git,'rev-parse','HEAD'],text=True).strip()==observed[identity]['revision'];assert not subprocess.check_output([*git,'status','--porcelain','--untracked-files=all'],text=True)
  assert observed==sources[variant]['pins'];add(workspace);workspaces[variant]={'path':str(workspace),'remote_pins':observed,'no_local_substitution':True,'checkouts_clean_at_exact_revision':True}
 for path in a.evidence:
  obj=json.loads(path.read_text());assert obj.get('passed') is True,('Gate not passed',path);add(path)
 for path in a.extra_file:add(path)
 for path in a.extra_manifest:
  obj=json.loads(path.read_text());add(path)
  for name,h in obj['files'].items():assert sha(name)==h;add(name)
 add(a.swift.resolve());swift_version=subprocess.check_output([str(a.swift),'--version'],text=True);assert 'Swift version 6.4.2' in swift_version
 for file in (a.shared.resolve()/'control').iterdir():
  if file.is_file():add(file)
 receipt.update(passed=True,files=files,sources=sources,binaries=binaries,swift_version=swift_version,seven_other_dependency_pins_identical=True,published_dependency_only=True,publication_receipt={'path':str(a.publication_receipt.resolve()),'sha256':sha(a.publication_receipt),'version':a.candidate_version,'revision':a.candidate_revision,'release_url':publication['release_url']},workspace_verification=workspaces)
except BaseException as error:receipt['error']=repr(error);raise
finally:
 receipt['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(receipt,f,indent=2);f.write(chr(10))
 print(json.dumps({'passed':receipt['passed'],'bound_files':len(files)}),flush=True)
