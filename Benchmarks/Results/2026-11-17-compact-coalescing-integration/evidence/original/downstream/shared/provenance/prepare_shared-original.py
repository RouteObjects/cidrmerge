#!/usr/bin/env python3
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];OLD=Path('$PRIOR_EXPERIMENT');ORACLE=Path('$PRIOR_EXPERIMENT');MODERN=Path('$PRIOR_EXPERIMENT');records={};configs=[]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
def copy(source,relative,expected=None):
 target=ROOT/relative
 if str(relative) in records:assert sha(source)==records[str(relative)]['sha256'];return
 digest=sha(source);assert expected is None or digest==expected,(source,digest,expected);target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();subprocess.run(['/bin/cp','-c',str(source),str(target)],check=True);assert sha(target)==digest;records[str(relative)]={'source':str(source),'sha256':digest,'bytes':target.stat().st_size,'copy':'APFS clone, separate inode; original never modified'}
ref=json.loads((OLD/'shared/reference.json').read_text());copy(OLD/'shared/reference.json','provenance/compact-original-reference.json');copy(OLD/'shared/matched-protocol.json','provenance/compact-original-protocol.json')
for suite in ['split','native']:
 for case,expected in ref['expected'][suite].items():
  parts=[]
  assert expected['coverage_receipt']['passed']
  for part,original_output in zip(expected['parts'],expected['coverage_receipt']['output_files'],strict=True):
   ip=part['input'];im=ref['inputs'][ip];op=f'references/original/{suite}/{case}/{part["family"] or "mixed"}.txt';copy(OLD/'arm64'/ip,ip,im['sha256']);copy(Path(original_output['path']),op,part['output_sha256']);assert part['output_bytes']==original_output['bytes'];parts.append({'label':str(part['family'] or 'mixed'),'family':part['family'],'input':ip,'input_sha256':im['sha256'],'input_bytes':im['bytes'],'input_entries':im['lines'],'reference':op,'output_sha256':part['output_sha256'],'output_bytes':part['output_bytes']})
  configs.append({'id':suite+'-'+case,'group':'original','suite':suite,'case':case,'entries':sum(x['input_entries'] for x in parts),'flags':['--raw','--representation','cidr'],'parts':parts})
for relative,h in ref['original_reference_files'].items():copy(ORACLE/relative,'provenance/original/'+relative,h)
for file in ['generate_fixtures.py','verify_coverage.py','independent-coverage-audit.json']:
 copy(ORACLE/'control'/file,'provenance/original/control/'+file)
for case in ref['expected']['split']:
 for f in ['expected.json','manifest.json']:copy(ORACLE/'fixtures'/case/f,'provenance/original/fixtures/'+case+'/'+f)
for group in ['scale','sparse']:
 reference=json.loads((OLD/group/'reference.json').read_text());copy(OLD/group/'reference.json','provenance/'+group+'-reference.json')
 for c in reference['cases']:
  ip=group+'/'+c['input'];op=group+'/'+c['output'];copy(OLD/group/c['input'],ip,c['input_sha256']);copy(OLD/group/c['output'],op,c['output_sha256']);part={'label':'mixed','family':None,'input':ip,'input_sha256':c['input_sha256'],'input_bytes':c['input_bytes'],'input_entries':c['entries'],'reference':op,'output_sha256':c['output_sha256'],'output_bytes':c['output_bytes']};configs.append({'id':c['case'],'group':group,'suite':'native','case':c['case'],'entries':c['entries'],'flags':['--raw','--representation','cidr'],'parts':[part]})
for file in ['control/prepare_scale.py','control/reused-scale-reference-provenance.json','sparse/prepare.py','sparse/provenance.json']:
 copy(OLD/file,'provenance/compact/'+file)
for file in ['differential.py','io_differential_v2.py','final_validation_v2.py','slow_stdout.py']:
 copy(MODERN/'control'/file,'control/'+file)
assert len(configs)==25
save(ROOT/'control/cases.json',{'schema':1,'variants':['B','C'],'configs':configs})
protocol={'schema':1,'comparison':'current cidrmerge, published swift-cidr 0.10.1 versus new published upstream release; no local path overrides; seven other pins identical','variants':['B','C'],'cli_version_before_release_bump':'0.4.2','groups':{'original':{'configurations':11,'measured_samples':132,'warmups':22,'measured_processes':192,'warmup_processes':32},'scale':{'configurations':12,'measured_samples':144,'warmups':24,'measured_processes':144,'warmup_processes':24},'sparse':{'configurations':2,'measured_samples':24,'warmups':4,'measured_processes':24,'warmup_processes':4}},'total':{'configurations':25,'measured_samples':300,'warmups':50,'measured_processes':360,'warmup_processes':60},'pairs':6,'warmup':'one excluded warmup per variant/configuration, B then C','schedule':'each group separately; round 1 B,C then alternate; rotate configuration order by round index','aggregation':'split observations sum elapsed and CPU; maximum constituent-process peak RSS','followup':'one separate fixed six-pair phase per group for configurations with any primary paired elapsed or RSS increase above 5%; retain all samples; no recursive follow-ups or pooling','output':'full bytes and SHA256 matched to independent preserved references after timing; stderr must be empty','resource_measurement':'perf_counter_ns around child launch/wait; macOS /usr/bin/time -p -l; Linux exact-child wait4 ru_maxrss KiB times1024','disk_minimum_bytes':3*1024**3,'timeout_seconds':180,'deduplication':'after timing and complete-byte/hash verification, outputs hardlinked only to a fresh platform-local content store; never links to historical reference files','isolation':'serialize macOS and OrbStack timed windows; no concurrent builds/tests/profiling/transfers/corpus hashing; swift-dev independent'}
save(ROOT/'control/protocol.json',protocol);save(ROOT/'control/fixture-provenance.json',{'passed':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records,'copied_file_count':len(records),'total_bytes':sum(x['bytes'] for x in records.values()),'original_results_unchanged':True,'script_sha256':sha(Path(__file__))});print(json.dumps({'files':len(records),'configurations':len(configs),'bytes':sum(x['bytes'] for x in records.values())}))
