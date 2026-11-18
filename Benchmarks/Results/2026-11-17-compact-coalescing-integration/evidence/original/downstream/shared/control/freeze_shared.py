#!/usr/bin/env python3
"""Freeze the reviewed shared controls and preserved fixtures into a portable archive."""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,tarfile
p=argparse.ArgumentParser();p.add_argument('--controls-receipt',type=Path,required=True,action='append');p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];assert not a.archive.exists() and not a.output.exists();assert not (root/'control/shared-freeze.json').exists()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
controls=[]
for source in a.controls_receipt:
 data=json.loads(source.read_text());assert data['passed'];target=root/'provenance'/('controls-'+source.parent.name+'.json');assert not target.exists();target.write_bytes(source.read_bytes());controls.append({'path':str(source),'sha256':sha(source),'checks':data['count'],'preserved_receipt':str(target.relative_to(root))})
provenance=json.loads((root/'control/fixture-provenance.json').read_text());assert sha(root/'provenance/prepare_shared-original.py')==provenance['script_sha256']
for rel,meta in provenance['files'].items():assert sha(root/rel)==meta['sha256'],rel
files={}
for file in sorted(root.rglob('*')):
 assert not file.is_symlink(),file
 if file.is_file():files[str(file.relative_to(root))]={'sha256':sha(file),'bytes':file.stat().st_size}
receipt={'passed':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'file_count':len(files),'bytes':sum(x['bytes'] for x in files.values()),'fixture_provenance_sha256':sha(root/'control/fixture-provenance.json'),'harness_controls_receipts':controls,'synthetic_checks':sum(x['checks'] for x in controls),'historical_files_read_only':True}
save(root/'control/shared-freeze.json',receipt)
with a.archive.open('xb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=1) as gz,tarfile.open(fileobj=gz,mode='w',format=tarfile.GNU_FORMAT) as tar:
 for file in sorted(root.rglob('*')):
  if not file.is_file():continue
  info=tar.gettarinfo(str(file),arcname=str(file.relative_to(root)));info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
  with file.open('rb') as f:tar.addfile(info,f)
with tarfile.open(a.archive,'r:gz') as tar:
 members=tar.getmembers();assert all(x.isfile() and '..' not in Path(x.name).parts and not Path(x.name).is_absolute() for x in members)
 for member in members:
  with tar.extractfile(member) as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  assert digest==sha(root/member.name)
for rel,meta in files.items():assert sha(root/rel)==meta['sha256'],rel
save(a.output,{'passed':True,'archive':str(a.archive),'sha256':sha(a.archive),'bytes':a.archive.stat().st_size,'members':len(members),'shared_freeze_sha256':sha(root/'control/shared-freeze.json'),'all_archive_members_hash_verified':True});print(json.dumps({'passed':True,'archive':str(a.archive),'members':len(members),'bytes':a.archive.stat().st_size}))
