#!/usr/bin/env python3
"""Summarize passed gates and freeze measurement bindings; never times products."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path('$PLATFORM');E=Path('$EXPERIMENT');S=E/'downstream/shared';OUT=R/'control/qualification-gate.json';assert not OUT.exists()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
def normalize(command,variant):return [s.replace('/sources/'+variant,'/sources/VAR').replace('/build/'+variant+'-','/build/VAR-') for s in command]
checks={};evidence=[]
for v in ['B','C']:
 path=R/'control'/(v+'-qualification/summary.json');j=load(path);assert j['passed'] and j['test_count_debug']==j['test_count_release']==85;assert j['ordinary_binary_unchanged_after_tests'] and j['source_unchanged'] and j['pins_unchanged'];checks[v]=j;evidence.append(path)
 metadata=load(R/'metadata'/(v+'-ordinary.json'));assert metadata['frozen_before_test_builds'] and metadata['created_at']<=j['steps'][1]['started_at'];assert sha(R/'bin'/v)==metadata['sha256'];evidence.append(R/'metadata'/(v+'-ordinary.json'))
assert [normalize(s['command'],'B') for s in checks['B']['steps']]==[normalize(s['command'],'C') for s in checks['C']['steps']]
environments={v:load(R/'control'/(v+'-qualification/environment.json')) for v in ['B','C']};assert environments['B']['swift_sha256']==environments['C']['swift_sha256'];assert all('Swift version 6.4.2' in j['swift'] for j in environments.values())
floor_path=R/'floor-6.2.4/control/C-qualification/summary.json';floor=load(floor_path);assert floor['passed'] and floor['test_counts']=={'debug':85,'release':85};evidence.append(floor_path)
diff_path=R/'differential-01/summary.json';diff=load(diff_path);assert diff['passed'] is True and diff['case_count']==254 and diff['process_count']==508;evidence.append(diff_path)
io_path=R/'io-differential-01/summary.json';io=load(io_path);assert io['total']==io['passed']==86 and io['failed']==0 and not io['failures'];evidence.append(io_path)
final_path=R/'final-validation-01/summary.json';final=load(final_path);assert final['passed'] is True and final['frozen_source_unchanged'] and final['frozen_binary_unchanged'];evidence.append(final_path)
for path in [R/'control/B-preparation.json',R/'control/C-preparation.json']:
 assert load(path)['passed'];evidence.append(path)
for version in ['B','C']:
 events={k:int(v) for k,v in (line.split() for line in checks[version]['memory_events_after'].splitlines())};assert events.get('oom')==events.get('oom_kill')==events.get('oom_group_kill')==0
record={'passed':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':'native ARM64 Linux OrbStack','build_system':'native','baseline_candidate_commands_match_after_variant_path_normalization':True,'swift_sha256':environments['B']['swift_sha256'],'full_tests':{'B':{'debug':85,'release':85},'C':{'debug':85,'release':85}},'floor_swift_6_2_4_C':{'debug':85,'release':85},'cli_differential':{'cases':254,'processes':508},'io_differential':{'total':86,'passed':86,'failed':0},'final_validation_steps':[x['label'] for x in final['steps']],'evidence':{str(p):sha(p) for p in evidence},'no_oom_events':True};save(OUT,record)
command=['$PLATFORM/python/bin/python3',str(S/'control/freeze_bindings.py'),'--shared',str(S),'--baseline-source',str(R/'sources/B'),'--candidate-source',str(R/'sources/C'),'--baseline',str(R/'bin/B'),'--candidate',str(R/'bin/C'),'--swift','/usr/bin/swift','--candidate-version','0.11.0','--candidate-revision','ae956313ebbcb5a6f9d20b74626ce5b6e2e69839','--publication-receipt',str(E/'control/upstream-publication.json'),'--baseline-workspace',str(R/'build/B-ordinary/workspace-state.json'),'--candidate-workspace',str(R/'build/C-ordinary/workspace-state.json'),'--runtime-library-path','$PLATFORM/runtime/lib','--evidence',str(OUT),'--output',str(R/'control/premeasurement.json')]
for path in evidence+[E/'control/cidrmerge-baseline-freeze.json',E/'control/cidrmerge-candidate-freeze.json',R/'control/B-qualification/environment.json',R/'control/C-qualification/environment.json',Path(__file__)]:command+=['--extra-file',str(path)]
with (R/'control/binding-freeze.log').open('x') as f:proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
save(R/'control/binding-freeze-command.json',{'passed':proc.returncode==0,'command':command,'exit_code':proc.returncode});assert proc.returncode==0
print(json.dumps({'passed':True,'full_tests':record['full_tests'],'floor':record['floor_swift_6_2_4_C'],'differential_cases':254,'io_cases':86,'binding_files':len(load(R/'control/premeasurement.json')['files'])}),flush=True)
