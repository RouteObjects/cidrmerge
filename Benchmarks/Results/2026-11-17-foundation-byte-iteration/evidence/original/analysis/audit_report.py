#!/usr/bin/env python3
"""Independently audit completed B/P phases after timing, then reconcile phase totals."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(path):return json.loads(path.read_text())
def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--platform-root',type=Path,required=True)
    parser.add_argument('--platform',choices=['macos','linux'],required=True)
    parser.add_argument('--remote-root')
    parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--timing-finished',action='store_true')
    args=parser.parse_args()
    assert args.timing_finished,'No corpus auditing before host timing finishes'
    root=args.root.resolve();platform=args.platform_root.resolve();output=args.output_root.resolve()
    output.relative_to(root);output.mkdir(parents=True,exist_ok=False)
    receipt={'passed':False,'started_at':stamp(),'scope':'Independent post-timing phase audits and primary/follow-up inventory reconciliation; no product execution.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'audit_rows':[],'errors':[]}
    totals={'primary':{'measured_samples':0,'warmups':0},'followup':{'measured_samples':0,'warmups':0}}
    expected={'throughput':(192,32),'stdin':(24,4),'startup':(160,8)}
    for kind,parent in [('throughput','comparisons'),('stdin','stdin'),('startup','startup')]:
        base=platform/parent/'ordinary/B-vs-P'
        summaries=sorted(base.glob('*/summary.json'))
        passed=[p for p in summaries if load(p).get('passed')]
        failed=[str(p.relative_to(root)) for p in summaries if not load(p).get('passed')]
        if failed:receipt.setdefault('preserved_failed_phases',[]).extend(failed)
        primaries=[p for p in passed if p.parent.name.startswith('primary')]
        followups=[p for p in passed if p.parent.name.startswith('followup')]
        if len(primaries)!=1 or len(followups)>1:
            receipt['errors'].append(f'{kind}: expected exactly one completed primary and at most one follow-up');continue
        primary=load(primaries[0]);required=set(primary['followup_required'])
        if bool(required)!=bool(followups):receipt['errors'].append(f'{kind}: missing or unsolicited follow-up')
        if followups and set(load(followups[0])['pairs'])!=required:receipt['errors'].append(f'{kind}: follow-up selection differs from primary trigger')
        if (primary['measured_samples'],primary['warmups'])!=expected[kind]:receipt['errors'].append(f'{kind}: primary inventory mismatch')
        for summary_path in primaries+followups:
            directory=summary_path.parent;phase=directory.name;destination=output/f'{kind}-{phase}'
            auditor=root/'control'/('audit_stdin_comparison.py' if kind=='stdin' else 'audit_comparison.py')
            command=[sys.executable,str(auditor),'--root',str(root),'--platform-root',str(platform),'--directory',str(directory),'--platform',args.platform,'--output',str(destination),'--timing-finished']
            if args.remote_root:command+=['--remote-root',args.remote_root]
            result=subprocess.run(command,capture_output=True,text=True)
            (output/f'{kind}-{phase}.stdout').write_text(result.stdout);(output/f'{kind}-{phase}.stderr').write_text(result.stderr)
            audit_path=destination/'audit.json'
            if result.returncode or not audit_path.exists() or not load(audit_path).get('passed'):
                receipt['errors'].append(f'{kind}/{phase}: independent audit failed');continue
            audit=load(audit_path)['result'];group='primary' if phase.startswith('primary') else 'followup'
            for key in totals[group]:totals[group][key]+=audit[key]
            receipt['audit_rows'].append({'kind':kind,'profile':'ordinary','comparison':'B-vs-P','phase':phase,'receipt':str(audit_path.relative_to(root)),'measured_samples':audit['measured_samples'],'warmups':audit['warmups'],'case_count':len(audit['configs']),'rounds':audit['rounds']})
    if totals['primary']!={'measured_samples':376,'warmups':44}:receipt['errors'].append('All-group primary totals do not reconcile to376/44')
    receipt['totals']=totals;receipt['audit_count']=len(receipt['audit_rows']);receipt['passed']=not receipt['errors'];receipt['finished_at']=stamp()
    save(output/'summary.json',receipt);print(json.dumps({'passed':receipt['passed'],'audits':receipt['audit_count'],'totals':totals,'errors':receipt['errors']}))
    return 0 if receipt['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
