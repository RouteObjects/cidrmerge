#!/usr/bin/env python3
"""Independent redirected-stdin comparison audit; primary auditors remain unchanged."""
from pathlib import Path
import argparse, datetime as dt, hashlib, json, math, re, statistics, traceback

def require(value, message):
    if not value: raise ValueError(message)
def load(p): return json.loads(Path(p).read_text())
def stamp(): return dt.datetime.now(dt.timezone.utc).isoformat()
def save(p,v):
    with p.open('x') as f: json.dump(v,f,indent=2);f.write(chr(10))
class Auditor:
    def __init__(self,args):
        self.a=args;self.root=args.root.resolve();self.platform_root=args.platform_root.resolve();self.directory=args.directory.resolve();self.cache={};self.hash_bytes=0
    def digest(self,p):
        p=Path(p);s=p.stat();key=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if key not in self.cache:
            with p.open('rb') as f:self.cache[key]=hashlib.file_digest(f,'sha256').hexdigest()
            after=p.stat();require((after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)==key,'Content identity changed while hashing: '+str(p));self.hash_bytes+=s.st_size
        return self.cache[key]
    def check_hash(self,p,h):require(self.digest(p)==h,'Hash mismatch: '+str(p))
    def resolve(self,value):
        p=Path(value)
        if not p.is_absolute():return self.platform_root/p
        mappings=[(str(self.root),self.root),(str(self.platform_root),self.platform_root),('$EXPERIMENT',self.root),('$PLATFORM',self.platform_root)]
        if self.a.remote_root:mappings.append((self.a.remote_root,self.platform_root))
        for prefix,replacement in sorted(mappings,key=lambda x:len(x[0]),reverse=True):
            try:return replacement/p.relative_to(prefix)
            except ValueError:pass
        raise ValueError('Unrecognized preserved path: '+str(p))
    def run(self):
        directory=self.directory;summary=load(directory/'summary.json');freeze=load(directory/'freeze.json')
        invocation=load(directory.parent/(directory.name+'-invocation.json'))
        require(invocation['phase']==directory.name,'Wrapper phase mismatch')
        wrapper=invocation.get('wrapper_source','run_stdin_comparison.py')
        require(wrapper=='run_stdin_comparison.py','Unrecognized wrapper source')
        self.check_hash(self.root/'control'/wrapper,invocation['wrapper_sha256'])
        if 'wrapper_path' in invocation:require(self.resolve(invocation['wrapper_path'])==self.root/'control'/wrapper,'Wrapper path mismatch')
        completion_path=directory.parent/(directory.name+'-completion.json');recovered=False
        require(completion_path.exists(),'Missing wrapper completion')
        completion=load(completion_path)
        require(completion['exit_code']==0 and completion['status']=='completed','Unsuccessful wrapper')
        for k,v in invocation.items():
            if k!='status':require(completion[k]==v,'Invocation/completion mismatch: '+k)
        self.check_hash(directory.parent/(directory.name+'-driver.log'),completion['driver_log_sha256'])
        require(invocation['comparison']=='B-vs-P' and invocation['artifact_profile']=='ordinary','Unexpected variant/profile')
        require(not invocation['post_timing_cross_comparison_dedup'],'Unexpected crossphase relinking')
        require(summary['passed'] and summary['freeze_unchanged'],'Incomplete runner')
        startup=invocation['startup'];require(not startup and invocation['stdin_transport']=='regular-file-redirection','Unexpected stdin protocol');rounds=6;cases=load(self.root/'control/stdin-cases.json')['configs'];byid={c['id']:c for c in cases};selected=freeze['configs'];ids=[c['id'] for c in selected]
        require(len(ids)==len(set(ids)) and all(c==byid[c['id']] for c in selected),'Changed case definitions')
        if directory.name.startswith('primary'):require(selected==cases,'Primary omitted configurations')
        role=invocation['role_mapping'];require(role==dict(zip(('B','C'),invocation['comparison'].split('-vs-'))),'Role mapping changed')
        binary_root=self.platform_root/'bin'/('release-style' if invocation['artifact_profile']=='release-style' else ('stripped' if startup else ''))
        binaries={r:binary_root/v for r,v in role.items()}
        for r,p in binaries.items():self.check_hash(p,invocation['binary_sha256'][role[r]])
        require(self.resolve(invocation['baseline'])==binaries['B'] and self.resolve(invocation['candidate'])==binaries['C'],'Wrapper binary path mismatch')
        self.check_hash(self.root/'control/run_stdin.py',invocation['source_runner_sha256'])
        self.check_hash(self.root/'control/stdin-cases.json',invocation['cases_sha256'])
        for path,h in freeze['files'].items():self.check_hash(self.resolve(path),h)
        require(all(str(p) in {str(self.resolve(x)) for x in freeze['files']} for p in binaries.values()),'Binary missing from runner freeze')
        expected=[]
        for c in selected:
            for v in ('B','C'):expected.append(('warmup',c['id'],v))
        for i in range(rounds):
            k=i%len(selected)
            for c in selected[k:]+selected[:k]:
                for v in (('B','C') if i%2==0 else ('C','B')):expected.append((f'round-{i+1:02d}',c['id'],v))
        paths=list(directory.rglob('sample.json'));require({str(p.relative_to(directory)) for p in paths}=={'/'.join(x)+'/sample.json' for x in expected},'Sample inventory mismatch')
        data={};chronological=[]
        for p in paths:
            q=load(p);phase,cid,v,_=p.relative_to(directory).parts;c=byid[cid]
            require(q['passed'] and q['exit_code']==0 and 'error' not in q,'Failed sample: '+str(p));require(q['id']==cid and q['variant']==v,'Sample identity mismatch')
            cmd=q['command'];require(self.resolve(cmd[0])==binaries[v],'Unexpected binary')
            if c.get('input'):
                require(cmd[1:]==c['flags'],'Changed stdin flags');require(q['stdin_transport']=='regular-file-redirection' and q['stdin_opened_before_timing'],'Wrong stdin transport');self.check_hash(self.resolve(q['stdin_file']),c['input_sha256'])
            else:require(cmd[1:]==c['flags'],'Changed no-input flags')
            require(q['elapsed_ns']>0 and q['cpu_seconds']>=0 and q['peak_rss_bytes']>0,'Invalid metrics')
            require(all(math.isfinite(q[k]) for k in ('elapsed_ns','cpu_seconds','peak_rss_bytes')),'Nonfinite metrics')
            if self.a.platform=='macos':
                raw=(p.parent/'native.time').read_text();native={k:float(re.search(r'^'+k+r'\s+(\d+(?:\.\d+)?)\s*$',raw,re.M)[1]) for k in ('real','user','sys')};rss=int(re.search(r'^\s*(\d+)\s+maximum resident set size\s*$',raw,re.M)[1]);require(q['native_time']==native and q['peak_rss_bytes']==rss and q['cpu_seconds']==native['user']+native['sys'],'Mac native measurement mismatch')
            else:
                u=q['wait4_rusage'];require(q['peak_rss_bytes']==u['ru_maxrss']*1024 and q['cpu_seconds']==u['ru_utime']+u['ru_stime'],'Linux native measurement mismatch')
            require(q['complete_reference_bytes_match'] and q['complete_statistics_bytes_match'],'Missing complete-byte verification')
            for filename,hkey,nkey,rkey in [('stdout','output_sha256','output_bytes','reference'),('stderr','stderr_sha256','stderr_bytes','stderr_reference')]:
                output=p.parent/filename;require(output.stat().st_size==q[nkey]==c[nkey],'Output size mismatch');require(q[hkey]==c[hkey],'Recorded output hash mismatch');self.check_hash(output,c[hkey]);self.check_hash(self.root/c[rkey],c[hkey])
            require(q['free_bytes_before']>=3*1024**3+c['output_bytes'] and q['free_bytes_after']>=3*1024**3,'Disk floor violated')
            begin,end=map(dt.datetime.fromisoformat,(q['started_at'],q['finished_at']));require(end>begin,'Invalid timestamps');chronological.append((begin,end,(phase,cid,v)));data[phase,cid,v]=q
        chronological.sort();require([x[2] for x in chronological]==expected,'Pair order/case rotation mismatch');require(all(x[1]<=y[0] for x,y in zip(chronological,chronological[1:])),'Samples overlap')
        require(summary['warmups']==len(selected)*2 and summary['measured_samples']==len(selected)*rounds*2,'Summary inventory mismatch')
        recalculated={};followup=[];fields={'elapsed':'elapsed_ns','cpu':'cpu_seconds','rss':'peak_rss_bytes'}
        for c in selected:
            cid=c['id'];pairs=[]
            for n in range(1,rounds+1):
                b,q=(data[f'round-{n:02d}',cid,v] for v in ('B','C'));pair={'round':n,'B':{k:b[k] for k in fields.values()},'C':{k:q[k] for k in fields.values()}}
                for k,f in fields.items():pair[k+'_change_pct']=(q[f]/b[f]-1)*100 if b[f] else None
                pairs.append(pair)
            ranges={};medians={}
            for k in fields:
                values=[p[k+'_change_pct'] for p in pairs if p[k+'_change_pct'] is not None];ranges[k]=[min(values),max(values)] if values else None;medians[k]=statistics.median(values) if values else None
            recalculated[cid]={'pairs':pairs,'paired_change_ranges':ranges,'paired_change_medians':medians}
            require(recalculated[cid]==summary['pairs'][cid],'Recomputed pair summary mismatch: '+cid)
            if any(p['elapsed_change_pct']>5 or p['rss_change_pct']>5 for p in pairs):followup.append(cid)
        require(set(summary['pairs'])==set(ids) and summary['followup_required']==followup,'Threshold selection mismatch')
        return {'passed':True,'postprocessing_recovered':recovered,'wrapper_source':wrapper,'comparison':invocation['comparison'],'artifact_profile':invocation['artifact_profile'],'startup':startup,'phase':directory.name,'role_mapping':role,'configs':ids,'rounds':rounds,'measured_samples':len(selected)*rounds*2,'warmups':len(selected)*2,'binary_sha256':invocation['binary_sha256'],'started_at':chronological[0][0].isoformat(),'finished_at':chronological[-1][1].isoformat(),'followup_required':followup,'recomputed':recalculated}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--platform-root',type=Path,required=True);p.add_argument('--directory',type=Path,required=True);p.add_argument('--platform',choices=['macos','linux'],required=True);p.add_argument('--remote-root');p.add_argument('--output',type=Path,required=True);p.add_argument('--timing-finished',action='store_true');a=p.parse_args();require(a.timing_finished,'Audit hashing must wait until timing finishes');a.output.mkdir(parents=True,exist_ok=False)
    receipt={'passed':False,'started_at':stamp(),'scope':'Independent hashes, role mapping, exact sample inventory/order, native resource units, retained output bytes, pair medians/spread and follow-up threshold. Build/source qualification is separate.'};auditor=Auditor(a)
    try:receipt['result']=auditor.run();receipt['passed']=True
    except BaseException as e:receipt.update(error=repr(e),traceback=traceback.format_exc())
    receipt.update(finished_at=stamp(),auditor_sha256=auditor.digest(Path(__file__)),unique_files_hashed=len(auditor.cache),bytes_hashed=auditor.hash_bytes);save(a.output/'audit.json',receipt);print(json.dumps({'passed':receipt['passed'],'receipt':str(a.output/'audit.json'),'error':receipt.get('error')}));return 0 if receipt['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
