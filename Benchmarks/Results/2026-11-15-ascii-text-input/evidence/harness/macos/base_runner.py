#!/usr/bin/env python3
"""Frozen native CLI comparison; all outputs and timing evidence stay in this run directory."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ['cidrmerge', 'rs-aggregate', 'iprange', 'mapcidr']
CASES = ['ipv4-disjoint', 'ipv6-disjoint', 'mixed-disjoint', 'mixed-permuted',
         'mixed-overlap', 'mixed-adjacent', 'bgp-like-ipv4', 'range-derived-mixed']
NATIVE_CASES = ['mixed-disjoint', 'mixed-permuted', 'mixed-overlap']

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def write_json(path, data):
    with path.open('x') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def deadline_expired(signum, frame):
    raise TimeoutError('180-second process timeout')

def invocation(tool, input_path, family):
    binary = ROOT / 'bin' / tool
    if tool == 'cidrmerge':
        return [str(binary), '--raw', '--representation', 'cidr', str(input_path)]
    if tool == 'rs-aggregate':
        return [str(binary), str(input_path)]
    if tool == 'iprange':
        assert family in (4, 6)
        return [str(binary), f'-{family}', str(input_path)]
    return [str(binary), '-aggregate', '-silent', '-disable-update-check',
            '-auth=false', '-cidr', str(input_path)]

def run_one(suite, case, tool, location, baseline=None):
    location.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / 'fixtures' / case
    sources = [(None, fixture / 'input.txt')] if suite == 'native' else [
        (family, fixture / f'ipv{family}.txt') for family in (4, 6)
        if (fixture / f'ipv{family}.txt').stat().st_size
    ]
    record = {'suite': suite, 'case': case, 'tool': tool, 'started_at': stamp(),
              'parts': [], 'passed': False}
    try:
        for family, input_path in sources:
            label = str(family or 'mixed')
            temp = location / f'tmp-{label}'
            temp.mkdir()
            output = location / f'{label}.stdout'
            stderr = location / f'{label}.stderr'
            metrics = location / f'{label}.time'
            command = invocation(tool, input_path, family)
            # Fresh environment keeps thread defaults and excludes inherited credentials/config.
            env = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
                   'TMPDIR': str(temp) + '/'}
            cwd = ROOT
            if tool == 'mapcidr':
                env['PDCP_API_KEY'] = 'benchmark-no-credentials'
                cwd = ROOT / 'mapcidr' / 'run'
            with output.open('xb') as out, stderr.open('xb') as err:
                previous_handler = signal.signal(signal.SIGALRM, deadline_expired)
                signal.setitimer(signal.ITIMER_REAL, 180)
                process = None
                start = time.perf_counter_ns()
                try:
                    process = subprocess.Popen(['/usr/bin/time', '-p', '-l', '-o', str(metrics),
                                                *command], env=env, cwd=cwd,
                                               stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                               start_new_session=True)
                    # Blocking wait avoids the polling delay of wait(timeout=...).
                    process.wait()
                    elapsed_ns = time.perf_counter_ns() - start
                except BaseException as error:
                    if process is not None and process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    record['error'] = repr(error)
                    raise
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, previous_handler)
            part = {'family': family, 'command': command, 'input': str(input_path.relative_to(ROOT)),
                    'elapsed_ns': elapsed_ns, 'exit_code': process.returncode,
                    'output': str(output.relative_to(ROOT)), 'output_bytes': output.stat().st_size,
                    'output_sha256': digest(output), 'stderr_bytes': stderr.stat().st_size}
            record['parts'].append(part)
            if process.returncode != 0 or stderr.stat().st_size:
                raise RuntimeError(f'{tool}/{case}: nonzero exit or unexpected stderr')
            raw = metrics.read_text()
            rss = re.search(r'^\s*(\d+)\s+maximum resident set size\s*$', raw, re.M)
            fields = {key: re.search(r'^' + key + r'\s+(\d+(?:\.\d+)?)\s*$', raw, re.M)
                      for key in ['real', 'user', 'sys']}
            if not rss or not all(fields.values()):
                raise RuntimeError('Missing native timing metrics')
            part.update(peak_rss_bytes=int(rss[1]),
                        bsd_time={key: float(match[1]) for key, match in fields.items()})
        record.update(elapsed_ns=sum(x['elapsed_ns'] for x in record['parts']),
                      peak_rss_bytes=max(x['peak_rss_bytes'] for x in record['parts']),
                      cpu_seconds=sum(x['bsd_time']['user'] + x['bsd_time']['sys'] for x in record['parts']),
                      output_bytes=sum(x['output_bytes'] for x in record['parts']))
        if baseline:
            expected = {x['family']: x for x in baseline['parts']}
            for part in record['parts']:
                before = expected[part['family']]
                if (part['output_sha256'], part['output_bytes']) != (before['output_sha256'], before['output_bytes']):
                    raise RuntimeError('Timed output differs from independently verified warmup')
            record['matches_verified_warmup_bytes'] = True
        else:
            verification = location / 'coverage.json'
            command = [sys.executable, str(ROOT / 'control/verify_coverage.py'), str(fixture),
                       *[str(ROOT / part['output']) for part in record['parts']],
                       '--receipt', str(verification)]
            with (location / 'coverage.log').open('xb') as log:
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            record['independent_coverage_receipt'] = str(verification.relative_to(ROOT))
        record['passed'] = True
        # Retain every output in this experiment, including exact duplicates.
        return record
    except Exception as error:
        record['error'] = repr(error)
        raise
    finally:
        record['finished_at'] = stamp()
        write_json(location / 'sample.json', record)

def suite_cases(suite):
    return CASES if suite == 'split' else NATIVE_CASES

def suite_tools(suite):
    return TOOLS if suite == 'split' else [x for x in TOOLS if x != 'iprange']

def validate_frozen_inputs():
    freeze = json.loads((ROOT / 'control/freeze.json').read_text())
    for name, expected in freeze['files'].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('Frozen input changed: ' + name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['verify', 'measure'])
    args = parser.parse_args()
    validate_frozen_inputs()
    if args.phase == 'verify':
        results = []
        for suite in ['split', 'native']:
            for case in suite_cases(suite):
                for tool in suite_tools(suite):
                    print(f'Verifying {suite}/{case}/{tool}', flush=True)
                    location = ROOT / 'warmup' / suite / case / tool
                    try:
                        record = run_one(suite, case, tool, location)
                        results.append({'suite': suite, 'case': case, 'tool': tool, 'passed': record['passed']})
                    except Exception as error:
                        results.append({'suite': suite, 'case': case, 'tool': tool, 'passed': False,
                                        'error': repr(error)})
                        print('Verification failed: ' + repr(error), flush=True)
        write_json(ROOT / 'verification-matrix.json', results)
        if not all(x['passed'] for x in results):
            raise SystemExit('Coverage preflight has failures; review before measurement')
    else:
        matrix = json.loads((ROOT / 'verification-matrix.json').read_text())
        if not all(x['passed'] for x in matrix):
            raise SystemExit('Refusing to measure failed coverage candidates')
        for suite, rounds in [('split', 8), ('native', 9)]:
            cases = suite_cases(suite)
            toolset = suite_tools(suite)
            for round_index in range(rounds):
                case_order = cases[round_index % len(cases):] + cases[:round_index % len(cases)]
                direction = toolset if (round_index // len(toolset)) % 2 == 0 else list(reversed(toolset))
                order = direction[round_index % len(direction):] + direction[:round_index % len(direction)]
                for case in case_order:
                    for tool in order:
                        baseline = json.loads((ROOT / 'warmup' / suite / case / tool / 'sample.json').read_text())
                        location = ROOT / 'runs' / suite / f'round-{round_index + 1:02}' / case / tool
                        record = run_one(suite, case, tool, location, baseline)
                        print(json.dumps({'suite': suite, 'round': round_index + 1, 'case': case,
                                          'tool': tool, 'seconds': record['elapsed_ns'] / 1e9,
                                          'peak_mib': record['peak_rss_bytes'] / 1048576}), flush=True)
        validate_frozen_inputs()
        write_json(ROOT / 'measurement-complete.json', {'passed': True, 'finished_at': stamp(),
                                                      'split_rounds': 8, 'native_rounds': 9})

if __name__ == '__main__':
    main()
