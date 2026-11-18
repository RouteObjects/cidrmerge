#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,tarfile,os,subprocess,datetime,shutil
R=Path('$EXPERIMENT');O=R/'upstream-qualification';B=R/'scratch/upstream';SRC=R/'sources/upstream-validation'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write(chr(10))
summary=json.loads((O/'summary.json').read_text());assert not summary['passed'] and 'FileNotFoundError' in summary['error'] and 'debug.yaml' in summary['error'],summary.get('error')
expected=[f'{c}-build-{t}' for c in ['debug','release'] for t in ['CIDR','CIDRArgumentParser','CIDRPOSIX','CIDRNIO']]+['test-debug','test-release'];assert len(summary['steps'])==10 and {x['name'] for x in summary['steps']}==set(expected)
for x in summary['steps']:
 assert x['passed'] and x['exit_code']==0 and sha(R/x['log'])==x['log_sha256']
 if x['name'].startswith('test-'):assert x['total_tests']==311
freeze=json.loads((R/'control/upstream-source-freeze.json').read_text());actual={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob('*') if p.is_file()};assert actual==freeze['files']
state=json.loads((B/'workspace-state.json').read_text());pins={p['identity']:p['state'] for p in freeze['pins']};assert {p['packageRef']['identity']:p['state']['checkoutState'] for p in state['object']['dependencies']}==pins
for d in state['object']['dependencies']:
 p=B/'checkouts'/d['subpath'];assert subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()==d['state']['checkoutState']['revision'];assert not subprocess.check_output(['git','-C',str(p),'status','--porcelain'],text=True)
files={};links={};products={}
for config in ['debug','release']:
 root=(B/config).resolve();assert root.is_relative_to(B);tests=['CIDRTests','CIDRArgumentParserTests','CIDRPOSIXTests','CIDRNIOTests'];libraries=['CIDR','CIDRArgumentParser','CIDRPOSIX','CIDRNIO']
 for name in tests:assert (root/(name+'-test-runner')).is_file() and (root/(name+'.so')).is_file()
 for name in libraries:assert (root/('lib'+name+'.a')).is_file() and (root/(name+'.swiftmodule')).is_dir()
 products[config]={'resolved_directory':str(root.relative_to(B)),'test_runners':{n:sha(root/(n+'-test-runner')) for n in tests},'test_libraries':{n:sha(root/(n+'.so')) for n in tests},'product_libraries':{n:{'sha256':sha(root/('lib'+n+'.a')),'bytes':(root/('lib'+n+'.a')).stat().st_size} for n in libraries}}
 for p in root.rglob('*'):
  relative=str(p.relative_to(B))
  if p.is_symlink():links[relative]=os.readlink(p)
  elif p.is_file():files[relative]={'bytes':p.stat().st_size,'sha256':sha(p)}
for name in ['workspace-state.json','manifest.pif','.buildSystem_debug','.buildSystem_release']:
 p=B/name;assert p.is_file();files[name]={'bytes':p.stat().st_size,'sha256':sha(p)}
archive=O/'preserved-swift-build-artifacts.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=1,dereference=False) as t:
 for rel in sorted(set(files)|set(links)):t.add(B/rel,arcname=rel,recursive=False)
seen=set()
with tarfile.open(archive,'r:gz') as t:
 for m in t:
  assert m.name not in seen;seen.add(m.name)
  if m.name in links:assert m.issym() and m.linkname==links[m.name]
  else:
   assert m.isfile() and m.size==files[m.name]['bytes']
   with t.extractfile(m) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==files[m.name]['sha256']
assert seen==set(files)|set(links)
art={'passed':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(archive.relative_to(R)),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'files':files,'symlinks':links,'products':products,'verified_decompressed_hashes':True,'scratch_retained':True};save(O/'artifact-preservation-swift-build.json',art)
final={'passed':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_merge':freeze['expected_merge'],'source_tree':freeze['tree'],'source_files_verified':len(actual),'source_freeze_sha256':sha(R/'control/upstream-source-freeze.json'),'pins':pins,'all_four_products_debug_release_passed':True,'debug_tests':311,'release_tests':311,'test_counts_by_bundle':{x['name']:x['test_counts'] for x in summary['steps'] if x['name'].startswith('test-')},'build_system':'Swift Build default under Swift6.4.2; preserved actual out/Products/<configuration>-linux-x86_64 artifacts','steps':summary['steps'],'original_summary':'upstream-qualification/summary.json','original_summary_sha256':sha(O/'summary.json'),'original_helper_failure':summary['error'],'recovery_scope':'Artifact preservation only. Successful builds/tests were not repeated; source and five pins independently reverified.','artifact_preservation':'upstream-qualification/artifact-preservation-swift-build.json','artifact_preservation_sha256':sha(O/'artifact-preservation-swift-build.json'),'free_bytes':shutil.disk_usage(R).free};save(O/'qualification-final.json',final);print(json.dumps({'passed':True,'debug_tests':311,'release_tests':311,'archive_bytes':art['archive_bytes'],'free_bytes':final['free_bytes']}))
