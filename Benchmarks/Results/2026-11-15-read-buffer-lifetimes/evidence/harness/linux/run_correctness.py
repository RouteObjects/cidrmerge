#!/usr/bin/env python3
"""Run the shared exact-behavior gate with the same Swift runtime as measured binaries."""
import os
import subprocess
import sys
from common import ROOT, digest, disk_guard, load, runtime_environment, verify_sources, write_json


def main():
    disk_guard()
    result = load(ROOT / 'control/build-tests/summary.json')
    assert result['passed']
    for v in ('B', 'C'):
        assert digest(ROOT / 'bin' / v) == result['bin'][v]
    verify_sources()
    env = {**runtime_environment(), 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC', 'TMPDIR': str(ROOT / 'tmp')}
    if os.environ.get('PYTHONHOME'):
        env['PYTHONHOME'] = os.environ['PYTHONHOME']
    command = [sys.executable, str(ROOT / 'control/differential.py'), '--baseline', str(ROOT / 'bin/B'),
               '--candidate', str(ROOT / 'bin/C'), '--output', str(ROOT / 'control/differential')]
    log = ROOT / 'logs/differential.log'
    with log.open('x') as out:
        p = subprocess.run(command, env=env, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
    write_json(ROOT / 'control/differential-run.json', {'command': command, 'environment': env, 'exit_code': p.returncode,
               'log_sha256': digest(log)})
    if p.returncode:
        raise RuntimeError('Exact differential correctness gate failed; retained log and artifacts')
    summary = load(ROOT / 'control/differential/summary.json')
    assert summary['passed']
    print('Differential correctness passed', flush=True)


if __name__ == '__main__':
    main()
