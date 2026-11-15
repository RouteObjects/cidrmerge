#!/usr/bin/env python3
"""Freeze ordinary CLI release binaries, then test both CLI/Core variants in Debug/Release."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from common import ROOT, config, digest, disk_guard, host_snapshot, prepare_runtime, runtime_environment, stamp, verify_pins, verify_sources, write_json


def main():
    cfg = config()
    expected_tests = cfg['expected_tests']
    assert set(expected_tests) == {'B', 'C'} and all(isinstance(n, int) and n > 0 for n in expected_tests.values())
    phase = ROOT / 'control/build-tests'
    phase.mkdir(exist_ok=False)
    host = host_snapshot()
    assert 'Swift version 6.4.2' in host['swift']['stdout'] and host['swift']['exit_code'] == 0, host['swift']
    verify_sources()
    prepare_runtime()
    write_json(phase / 'start.json', host)
    results = []
    schedule = [(v, 'build', 'release') for v in ('B', 'C')]
    schedule += [(v, 'test', c) for v in ('B', 'C') for c in ('debug', 'release')]
    env = dict(os.environ)
    env.update(runtime_environment())
    env.update(TMPDIR=str(ROOT / 'tmp'), CLANG_MODULE_CACHE_PATH=str(ROOT / 'clang-cache'), LANG='C', LC_ALL='C', TZ='UTC')
    (ROOT / 'tmp').mkdir(exist_ok=True)
    try:
        for variant, action, configuration in schedule:
            free = disk_guard()
            label = '-'.join([variant, 'cli', action, configuration])
            source = ROOT / 'sources' / variant / 'cidrmerge'
            command = [cfg['swift'], action, '--package-path', str(source), '--scratch-path', str(ROOT / 'build' / variant / 'cli'),
                       '--cache-path', str(ROOT / 'cache'), '--config-path', str(ROOT / 'config'), '--security-path', str(ROOT / 'security'),
                       '--disable-netrc', '--skip-update', '--only-use-versions-from-resolved-file', '--disable-sandbox',
                       '--build-system', 'native', '-c', configuration, '-j', str(cfg['jobs'])]
            if action == 'build':
                command += ['--product', 'cidrmerge']
            log = ROOT / 'logs' / (label + '.log')
            log.parent.mkdir(exist_ok=True)
            record = {'variant': variant, 'package': 'cli', 'action': action, 'configuration': configuration,
                      'command': command, 'started_at': stamp(), 'free_bytes_before': free, 'log': str(log.relative_to(ROOT))}
            write_json(phase / (label + '-started.json'), record)
            print('START ' + label, flush=True)
            start = time.monotonic()
            with log.open('x') as out:
                p = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT)
            record.update(exit_code=p.returncode, elapsed_s=time.monotonic()-start, log_sha256=digest(log))
            if p.returncode == 0:
                record['dependency_pins'] = verify_pins(variant, 'cli')
                if action == 'build':
                    show = command[:command.index('--product')] + ['--show-bin-path']
                    binary_dir = Path(subprocess.check_output(show, cwd=ROOT, env=env, text=True).strip())
                    target = ROOT / 'bin' / variant
                    target.parent.mkdir(exist_ok=True)
                    assert not target.exists(), target
                    shutil.copy2(binary_dir / 'cidrmerge', target)
                    linked = subprocess.run(['ldd', str(target)], env=env, text=True, capture_output=True)
                    record['ldd'] = {'exit_code': linked.returncode, 'stdout': linked.stdout, 'stderr': linked.stderr}
                    assert linked.returncode == 0 and 'not found' not in linked.stdout, linked.stdout
                    record.update(binary=str(target.relative_to(ROOT)), binary_sha256=digest(target))
                else:
                    text = log.read_text(errors='replace')
                    matches = re.findall(r'Test run with (\d+) tests in (\d+) suites passed', text)
                    assert len(matches) == 1, (label, 'missing/ambiguous final Swift Testing count')
                    count, suites = map(int, matches[0])
                    assert count == expected_tests[variant], (label, count, expected_tests[variant])
                    record.update(tests=count, suites=suites)
            write_json(phase / (label + '.json'), record)
            results.append(record)
            print('DONE ' + label + ' exit=' + str(p.returncode), flush=True)
            if p.returncode:
                raise RuntimeError(f'{label} failed with {p.returncode}')
        verify_sources()
        write_json(phase / 'summary.json', {'passed': True, 'finished_at': stamp(), 'results': results,
                    'test_executions': sum(x.get('tests', 0) for x in results), 'expected_tests': expected_tests,
                    'source_files_verified': verify_sources(), 'bin': {v: digest(ROOT / 'bin' / v) for v in ('B', 'C')}})
    except BaseException as error:
        write_json(phase / 'failed.json', {'at': stamp(), 'error': repr(error), 'completed_steps': results, 'no_retry_performed': True})
        raise


if __name__ == '__main__':
    main()
