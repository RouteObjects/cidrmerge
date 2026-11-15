#!/usr/bin/env python3
"""Run one explicit phase, retaining detached progress/failure receipts; no automatic timings."""
import argparse
import subprocess
import sys
from common import ROOT, digest, load, stamp, verify_sources, write_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['build-tests','correctness-freeze','benchmark'])
    args=parser.parse_args()
    receipt=ROOT/'control/phases'/args.phase
    receipt.mkdir(parents=True,exist_ok=False)
    write_json(receipt/'start.json',{'started_at':stamp(),'phase':args.phase})
    phases={'build-tests':[['build_tests.py']],
            'correctness-freeze':[['run_correctness.py'],['prepare_benchmark.py'],['run_matched.py','--validate-only']],
            'benchmark':[['run_matched.py']]}
    results=[]
    try:
        for step in phases[args.phase]:
            command=[sys.executable,str(ROOT/'control'/step[0]),*step[1:]]
            record={'command':command,'started_at':stamp()}
            p=subprocess.run(command,cwd=ROOT)
            record.update(finished_at=stamp(),exit_code=p.returncode)
            results.append(record)
            if p.returncode:
                raise RuntimeError(f'{step[0]} failed with {p.returncode}')
        if args.phase=='benchmark':
            runtime=load(ROOT/'control/runtime.json')
            hashes={p:digest(p) for p in runtime['libswiftCore_sha256']}
            assert hashes==runtime['libswiftCore_sha256']
            write_json(ROOT/'control/runtime-postcheck.json',{'passed':True,'files':hashes,'checked_at':stamp()})
            verify_sources()
        write_json(receipt/'complete.json',{'passed':True,'finished_at':stamp(),'steps':results})
    except BaseException as error:
        write_json(receipt/'failed.json',{'passed':False,'finished_at':stamp(),'error':repr(error),'steps':results})
        raise


if __name__=='__main__':
    main()
