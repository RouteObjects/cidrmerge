#!/usr/bin/env python3
"""Run only the frozen B/P matrix, with one nonrecursive follow-up per triggered group."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--platform-root',type=Path,required=True)
    parser.add_argument('--platform',choices=['macos','linux'],required=True)
    parser.add_argument('--runtime-library-path')
    parser.add_argument('--output-control',type=Path,required=True)
    parser.add_argument('--kind',choices=['throughput','stdin','startup'],action='append')
    args=parser.parse_args()
    root=args.root.resolve();platform=args.platform_root.resolve();control=args.output_control.resolve()
    control.mkdir(parents=True,exist_ok=False)
    kinds=args.kind or ['throughput','stdin','startup']
    assert len(set(kinds))==len(kinds)
    record={'passed':False,'started_at':stamp(),'driver_sha256':sha(__file__),'comparison':'B-vs-P','artifact_profile':'ordinary','kinds':kinds,'observations':[],
        'policy':'Only primary paired elapsed/RSS increases above5% trigger one fixed follow-up of the same pair count; no recursive third phase, no pooled observations.'}
    expected={'throughput':(192,32),'stdin':(24,4),'startup':(160,8)}
    try:
        freeze=json.loads((root/'control/common-harness-freeze.json').read_text())
        for rel,digest in freeze['control_sha256'].items():assert sha(root/rel)==digest,rel
        for kind in kinds:
            startup=kind=='startup';parent={'throughput':'comparisons','stdin':'stdin','startup':'startup'}[kind]
            base=platform/parent/'ordinary/B-vs-P'
            wrapper=root/'control'/('run_stdin_comparison.py' if kind=='stdin' else 'run_comparison.py')
            common=[sys.executable,str(wrapper),'--root',str(root),'--platform-root',str(platform),'--platform',args.platform,'--comparison','B-vs-P','--artifact-profile','ordinary']
            if startup:common+=['--startup']
            if args.runtime_library_path:common+=['--runtime-library-path',args.runtime_library_path]
            triggers=None
            for phase in ['primary','followup']:
                if phase=='followup' and not triggers:continue
                command=common+['--phase',phase]+(['--only',*triggers] if phase=='followup' else [])
                row={'kind':kind,'phase':phase,'started_at':stamp(),'command':command}
                result=subprocess.run(command);row.update(finished_at=stamp(),exit_code=result.returncode)
                record['observations'].append(row);save(control/f'{kind}-{phase}.json',row)
                assert result.returncode==0,f'{kind}/{phase} failed; preserve its evidence'
                summary=json.loads((base/phase/'summary.json').read_text())
                assert summary['passed'] and summary['freeze_unchanged']
                if phase=='primary':
                    assert (summary['measured_samples'],summary['warmups'])==expected[kind]
                    triggers=summary['followup_required']
                    save(control/f'{kind}-followup-selection.json',{'primary_summary':str(base/phase/'summary.json'),'primary_summary_sha256':sha(base/phase/'summary.json'),'configurations':triggers,'followup_rounds':20 if startup else 6,'nonrecursive':True})
                else:
                    assert set(summary['pairs'])==set(triggers)
                    assert summary['measured_samples']==len(triggers)*(40 if startup else 12)
                    assert summary['warmups']==len(triggers)*2
        record['primary_expected_measured']=sum(expected[k][0] for k in kinds)
        record['primary_expected_warmups']=sum(expected[k][1] for k in kinds)
        record['passed']=True
    except BaseException as error:
        record['error']=repr(error);raise
    finally:
        record['finished_at']=stamp();save(control/'summary.json',record)
        print(json.dumps({'passed':record['passed'],'output':str(control),'error':record.get('error')}),flush=True)

if __name__=='__main__':main()
