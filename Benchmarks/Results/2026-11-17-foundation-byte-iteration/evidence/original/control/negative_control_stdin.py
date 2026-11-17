#!/usr/bin/env python3
"""Reject wrong stdout and statistics using tiny fake children, never target benchmarks."""
from pathlib import Path
import argparse, importlib.util,json,platform,hashlib
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--runner',choices=['run_stdin.py'],required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
runner=Path(__file__).resolve().parent/a.runner;spec=importlib.util.spec_from_file_location('runner',runner);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);results=[]
for mode in ['statistics','stdout']:
 root=a.output/mode;root.mkdir();fake=root/'fake-cli';fake.write_text('#!/bin/sh'+chr(10)+"printf 'ok\\n'"+chr(10)+( "printf 'wrong\\n' >&2"+chr(10) if mode=='statistics' else ''));fake.chmod(0o755)
 (root/'input').write_bytes(b'');(root/'stdout.expected').write_bytes(b'ok\n' if mode=='statistics' else b'expected\n');(root/'stderr.expected').write_bytes(b'expected\n' if mode=='statistics' else b'')
 case={'id':'intentional-wrong-'+mode,'flags':[],'input':'input','reference':'stdout.expected','stderr_reference':'stderr.expected'}
 for path,size,hashkey in [('stdout.expected','output_bytes','output_sha256'),('stderr.expected','stderr_bytes','stderr_sha256')]:case[size]=(root/path).stat().st_size;case[hashkey]=m.sha(root/path)
 opts=argparse.Namespace(baseline=fake,candidate=fake,fixtures_root=root,output=root,platform='macos' if platform.system()=='Darwin' else 'linux',deduplicate=False)
 try:m.run(opts,case,'B',root/'sample',{'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'})
 except AssertionError as error:
  expected='Statistics reference hash mismatch' if mode=='statistics' else 'Reference hash mismatch';assert str(error)==expected,(str(error),expected);record=json.loads((root/'sample/sample.json').read_text());assert not record['passed'] and record['exit_code']==0;results.append({'mode':mode,'caught':str(error),'failed_sample_retained':True})
 else:raise AssertionError('Invalid bytes were accepted')
with (a.output/'summary.json').open('x') as f:json.dump({'passed':True,'runner':a.runner,'runner_sha256':hashlib.sha256(runner.read_bytes()).hexdigest(),'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'observations':results,'scope':'Harness-only fake children; not benchmark observations'},f,indent=2);f.write(chr(10))
print(json.dumps({'passed':True,'runner':a.runner,'rejections_verified':len(results)}))
