#!/usr/bin/env python3
"""Export an explicit small-text evidence selection; preserve original files and hashes."""
from pathlib import Path, PurePosixPath
import argparse,datetime,hashlib,json,os

ALLOWED_EXTENSIONS={'.json','.md','.txt','.log','.py','.patch','.sh','.csv','.tsv','.yaml','.yml'}
def digest(data):return hashlib.sha256(data).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)
def relative_name(value):
    require(isinstance(value,str) and value and '\\' not in value,'Selection paths must be nonempty POSIX relative strings')
    path=PurePosixPath(value)
    require(not path.is_absolute() and all(x not in ('','..','.') for x in value.split('/')),'Unsafe relative selection path: '+value)
    return path
def exclusive(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(data)
def transform(value,mappings):
    if isinstance(value,str):
        for prefix,replacement in mappings:value=value.replace(prefix,replacement)
        return value
    if isinstance(value,list):return [transform(x,mappings) for x in value]
    if isinstance(value,dict):
        pairs=[(transform(key,mappings),transform(item,mappings)) for key,item in value.items()]
        require(len({key for key,_ in pairs})==len(pairs),'Redaction would merge JSON keys')
        return dict(pairs)
    return value

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--selection',required=True,type=Path,help='JSON array of experiment-relative source file paths')
    parser.add_argument('--destination',required=True,type=Path,help='Existing report directory or a new directory; selected exports and manifest must not exist')
    parser.add_argument('--remote-root',action='append',default=[])
    parser.add_argument('--prior-root',action='append',default=[])
    parser.add_argument('--repository',required=True,type=Path)
    parser.add_argument('--user-home',type=Path,default=Path.home())
    parser.add_argument('--linux-home',type=Path)
    parser.add_argument('--container-mapping',action='append',default=[],metavar='PREFIX=PLACEHOLDER')
    parser.add_argument('--subdirectory',default='evidence/original')
    parser.add_argument('--max-file-bytes',type=int,default=8*1024**2)
    parser.add_argument('--max-total-bytes',type=int,default=64*1024**2)
    args=parser.parse_args()
    root=args.root.resolve(strict=True);destination=args.destination.resolve();sub=relative_name(args.subdirectory)
    require(not destination.is_relative_to(root/'sources'),'Do not export into frozen source snapshots')
    names=json.loads(args.selection.read_text());require(isinstance(names,list) and names,'Selection must be a nonempty JSON array')
    require(all(isinstance(x,str) for x in names),'Selection contains a non-string')
    require(len(names)==len(set(names)),'Duplicate selected path')
    home=str(args.user_home.resolve()).rstrip('/')
    linux_home=str(args.linux_home or Path('/home')/args.user_home.name).rstrip('/')
    mappings=[(str(root),'$EXPERIMENT'),(str(args.repository.resolve()),'$REPOSITORY'),(home,'$USER_HOME'),(linux_home,'$LINUX_HOME')]
    mappings += [(str(Path(x)).rstrip('/'),'$EXPERIMENT') for x in args.remote_root]
    mappings += [(str(Path(x)).rstrip('/'),'$PRIOR_EXPERIMENT') for x in args.prior_root]
    mappings += [('$EXPERIMENT','$EXPERIMENT'),('$PLATFORM','$PLATFORM')]
    for item in args.container_mapping:
        require('=' in item,'Container mapping requires PREFIX=PLACEHOLDER');prefix,replacement=item.split('=',1)
        require(prefix.startswith('/') and replacement.startswith('$'),'Invalid container mapping');mappings.append((prefix.rstrip('/'),replacement))
    by_prefix={}
    for prefix,replacement in mappings:
        require(prefix and prefix!='/' and '\n' not in prefix,'Invalid redaction prefix')
        require(prefix not in by_prefix or by_prefix[prefix]==replacement,'Conflicting redaction prefix')
        by_prefix[prefix]=replacement
    mappings=sorted(by_prefix.items(),key=lambda x:len(x[0]),reverse=True)
    manifest_path=destination/'evidence-export.json';require(not manifest_path.exists(),'Manifest already exists; no overwrite')
    prepared=[];total=0
    for name in names:
        relative=relative_name(name);source=root/relative
        require(source.is_file() and not source.is_symlink(),'Missing, non-file or symlink source: '+name)
        require(source.resolve().is_relative_to(root),'Source resolves outside experiment: '+name)
        require(not any((root/Path(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1)),'Symlink source ancestry: '+name)
        require(source.suffix.lower() in ALLOWED_EXTENSIONS,'Unsupported evidence extension: '+name)
        require(not ({'fixtures','startup-fixtures','checkouts','repositories'} & set(relative.parts)),'Raw fixture/dependency trees are not exportable: '+name)
        require(source.name not in ('stdout','stderr','stdout.link'),'Raw output is not exportable: '+name)
        size=source.stat().st_size;require(size<=args.max_file_bytes,'Selected file exceeds byte limit: '+name)
        total+=size;require(total<=args.max_total_bytes,'Selected evidence exceeds total byte limit')
        raw=source.read_bytes();require(b'\0' not in raw,'NUL byte in text evidence: '+name)
        text=raw.decode('utf-8');redactions=[];replaced=text
        for prefix,replacement in mappings:
            occurrences=replaced.count(prefix)
            if occurrences:
                redactions.append({'placeholder':replacement,'occurrences':occurrences})
                replaced=replaced.replace(prefix,replacement)
        # JSON serialization is preserved where possible. Verify that only string
        # values/keys changed; numeric observations and boolean decisions must agree.
        if source.suffix.lower()=='.json':
            original_json=json.loads(text);expected_json=transform(original_json,mappings)
            try:actual_json=json.loads(replaced)
            except json.JSONDecodeError:
                replaced=json.dumps(expected_json,indent=2,ensure_ascii=False)+'\n';actual_json=json.loads(replaced)
            require(actual_json==expected_json,'Non-string JSON transformation: '+name)
        exported=replaced.encode('utf-8')
        for prefix,_ in mappings:require(prefix not in replaced,'Unredacted known prefix: '+name)
        target=destination/sub/relative;require(not target.exists(),'Export target already exists: '+str(target))
        for parent in [target.parent,*target.parents]:
            if parent==destination.parent:break
            require(not parent.is_symlink(),'Symlink export ancestry is not allowed')
        prepared.append((source,target,exported,{'source':name,'destination':str(sub/relative),'source_sha256':digest(raw),'export_sha256':digest(exported),'source_bytes':len(raw),'export_bytes':len(exported),'path_redaction_applied':raw!=exported,'transformations':redactions,'measurement_values_unchanged':True if source.suffix.lower()=='.json' else None}))
    # Finish all validation before creating exports. Exclusive writes preserve any
    # partial evidence from an unexpected filesystem failure for later inspection.
    destination.mkdir(parents=True,exist_ok=True)
    entries=[]
    for source,target,exported,entry in prepared:
        require(digest(source.read_bytes())==entry['source_sha256'],'Source changed after preflight: '+entry['source'])
        exclusive(target,exported);require(digest(target.read_bytes())==entry['export_sha256'],'Export write verification failed')
        entries.append(entry)
    manifest={'schema':1,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Explicit selected text evidence only; originals remain unchanged. Raw output, binaries, runtimes and fixtures are not exported.','source_path_base':'$EXPERIMENT','destination_path_base':'report directory','selection_sha256':digest(args.selection.read_bytes()),'exporter_sha256':digest(Path(__file__).read_bytes()),'redaction':'Literal path-prefix substitutions only. JSON string/key transformations verified while numeric and boolean values remain identical.','file_count':len(entries),'source_bytes':total,'export_bytes':sum(x['export_bytes'] for x in entries),'files':entries}
    exclusive(manifest_path,(json.dumps(manifest,indent=2)+'\n').encode())
    print(json.dumps({'passed':True,'files':len(entries),'source_bytes':total,'export_bytes':manifest['export_bytes'],'manifest_sha256':digest(manifest_path.read_bytes())}))

if __name__=='__main__':main()
