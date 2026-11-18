from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,re,subprocess,uuid
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
env={**os.environ,'DEVELOPER_DIR':'/Applications/Xcode-27.2.0.app/Contents/Developer'}
def command(argv):
 x=subprocess.run(argv,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);return {'command':argv,'exit_code':x.returncode,'stdout':x.stdout,'stderr':x.stderr}
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
link=command(['otool','-L',str(a.binary)]);assert link['exit_code']==0
libs=re.findall(r'^\s+(/\S+) \(',link['stdout'],re.M);assert libs
swift=command(['xcrun','--find','swift']);assert swift['exit_code']==0;compiler=Path(swift['stdout'].strip()).resolve()
cache_uuid=(ctypes.c_ubyte*16)();api=ctypes.CDLL(None)._dyld_get_shared_cache_uuid;api.argtypes=[ctypes.POINTER(ctypes.c_ubyte)];api.restype=ctypes.c_bool;assert api(cache_uuid)
d={'passed':True,'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary':{'path':str(a.binary),'sha256':sha(a.binary)},'system':command(['sw_vers']),'kernel':command(['uname','-a']),'compiler':{'invocation_path':swift['stdout'].strip(),'resolved_path':str(compiler),'sha256':sha(compiler),'version':command([swift['stdout'].strip(),'--version'])},'swift_package_help':command([swift['stdout'].strip(),'package','--help']),'build_backend':'Swift Build (swiftbuild), Swift6.4.2 default; no --build-system override. Both matched Mac builds must use the same command/backend.','linkage':link,'linked_image_uuids':command(['xcrun','dyld_info','-uuid',*libs]),'loaded_shared_cache':{'uuid':str(uuid.UUID(bytes=bytes(cache_uuid))),'method':'Read-only _dyld_get_shared_cache_uuid query in this native host Python process; not a product dependency.','copied':False},'linked_paths':[],'runtime_scope':'Records host OS build, system shared-cache identity and linked image UUIDs. System/shared-cache libraries are not copied or claimed as frozen redistributable runtime files.'}
for path in libs:
 q=Path(path);row={'path':path,'ordinary_file_exists':q.is_file()}
 if q.is_file():row.update(bytes=q.stat().st_size,sha256=sha(q))
 d['linked_paths'].append(row)
cache=Path('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld');d['shared_cache_files']=[{'path':str(q),'bytes':q.stat().st_size,'mtime_ns':q.stat().st_mtime_ns} for q in sorted(cache.glob('dyld_shared_cache_arm64e*')) if q.is_file()]
assert d['linked_image_uuids']['exit_code']==0,d['linked_image_uuids']
with a.output.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'passed':d['passed'],'shared_cache_uuid':d['loaded_shared_cache']['uuid'],'linked_images':len(libs),'compiler_sha256':d['compiler']['sha256']}))
