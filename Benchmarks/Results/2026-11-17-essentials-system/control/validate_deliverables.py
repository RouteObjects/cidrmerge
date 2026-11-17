#!/usr/bin/env python3
"""Verify frozen code/preserved work and audit new report content in an isolated copy."""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--report',required=True)
    parser.add_argument('--output',default='validation/deliverables-final-01')
    args=parser.parse_args()
    root,repo=args.root,args.repo
    out=root/args.output
    out.mkdir(parents=True,exist_ok=False)
    commands=[]
    def run(command,cwd):
        result=subprocess.run(command,cwd=cwd,text=True,capture_output=True)
        commands.append({'command':command,'cwd':str(cwd),'exit_code':result.returncode,
                         'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode==0,(command,result.returncode,result.stderr)
        return result.stdout
    summary={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False}
    try:
        before=json.loads((root/'control/before.json').read_text())
        b=json.loads((root/'control/baseline-freeze.json').read_text())['files']
        c=json.loads((root/'control/R3-freeze.json').read_text())['files']
        for name,expected in before['preserved_files'].items():
            assert digest(repo/name)==expected,('preexisting file changed',name)
        owned=[name for name in c if Path(name).name!='.DS_Store' and
               (name.startswith(('Sources/','Tests/','scripts/','.github/'))
               or name in ['Package.swift','Package.resolved','THIRD_PARTY_NOTICES.txt'])]
        for name in owned:
            assert digest(repo/name)==c[name],('retained source changed',name)
        assert run(['git','branch','--show-current'],repo).strip()=='perf/essentials-system-io'
        assert run(['git','rev-parse','HEAD'],repo).strip()==before['baseline']
        assert not run(['git','diff','--cached','--name-only'],repo)
        tracked_before={line[3:] for line in before['status'].splitlines() if line[:2]!='??'}
        changed={name for name in c if name in b and c[name]!=b[name]}
        actual=set(run(['git','diff','--name-only'],repo).splitlines())
        assert actual==changed|tracked_before,('unexpected tracked diff',actual,changed|tracked_before)
        # Finder metadata remains in the full frozen inventory but is not new source code.
        added={name for name in set(c)-set(b) if Path(name).name!='.DS_Store'}
        untracked=set(run(['git','ls-files','--others','--exclude-standard'],repo).splitlines())
        unexpected={name for name in untracked if name not in added and name not in before['preserved_files']
                    and not name.startswith(args.report.rstrip('/')+'/')}
        assert not unexpected,('unexpected new files',unexpected)
        run(['git','diff','--check'],repo)
        isolated=out/'public-tree'
        isolated.mkdir()
        for name,expected in c.items():
            source=root/'sources/R3'/name
            assert digest(source)==expected,('frozen source changed',name)
            target=isolated/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
        report=repo/args.report
        assert report.is_dir()
        exported=json.loads((report/'evidence-export.json').read_text())
        for item in exported['files']:
            assert digest(report/item['destination'])==item['export_sha256'],('export changed',item['destination'])
        shutil.copytree(report,isolated/args.report)
        run(['git','init','-q'],isolated)
        run(['git','add','--all'],isolated)
        run(['bash','scripts/audit-release-content.sh','tree'],isolated)
        # Historical patch artifacts contain meaningful diff-context spaces. Their source
        # delta was already qualified; check only the newly authored report and Swift files.
        run(['git','diff','--cached','--check','--',args.report,*sorted(added)],isolated)
        assert not run(['git','diff','--cached','--name-only'],repo)
        summary.update({'passed':True,'retained':'R3','source_files_matched':len(owned),
                        'frozen_source_and_history_files_matched':len(c),
                        'preexisting_files_preserved':len(before['preserved_files']),
                        'actual_repo_index_empty':True,'actual_repo_head_unchanged':True,
                        'isolated_content_audit_passed':True,'report_whitespace_passed':True,
                        'exported_files_hash_verified':len(exported['files']),
                        'untracked_prototype_source_paths':sorted(added),
                        'new_report_files':sum(1 for path in report.rglob('*') if path.is_file())})
    except Exception as error:
        summary['error']=repr(error)
    summary['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
    raise SystemExit(0 if summary['passed'] else 1)


if __name__=='__main__':
    main()
