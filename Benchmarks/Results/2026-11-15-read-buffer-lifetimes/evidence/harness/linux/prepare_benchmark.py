#!/usr/bin/env python3
"""Freeze after complete tests and exact differential correctness; never starts timings."""
import sys
from common import ROOT, config, digest, disk_guard, host_snapshot, load, verify_fixtures, verify_sources, write_json


def main():
    assert sys.platform == 'linux'
    disk_guard()
    result = load(ROOT / 'control/build-tests/summary.json')
    counts = config()['expected_tests']
    assert result['passed'] and result['test_executions'] == 2 * sum(counts.values()), result
    assert result['expected_tests'] == counts
    steps = {(r['variant'], r['action'], r['configuration']) for r in result['results'] if r['exit_code'] == 0}
    wanted = {(v, 'build', 'release') for v in ('B', 'C')} | {(v, 'test', c) for v in ('B', 'C') for c in ('debug', 'release')}
    assert steps == wanted
    differential_path = ROOT / 'control/differential/summary.json'
    differential = load(differential_path)
    assert differential['passed']
    assert differential['script_sha256'] == digest(ROOT / 'control/differential.py')
    binary_hashes = {}
    for v, name in [('B', 'baseline'), ('C', 'candidate')]:
        binary_hashes[v] = digest(ROOT / 'bin' / v)
        assert binary_hashes[v] == result['bin'][v] == differential['binaries'][name]['sha256']
    inventory = load(ROOT / 'control/runtime-linked-libraries.json')
    assert inventory['phase'] == 'premeasurement' and inventory['binary_sha256'] == binary_hashes
    for path, meta in inventory['libraries'].items():
        assert digest(path) == meta['sha256'], path
    verify_sources()
    verify_fixtures()
    write_json(ROOT / 'control/correctness-gate.json', {'passed': True, 'binary_sha256': binary_hashes,
               'differential_summary_sha256': digest(differential_path), 'test_summary_sha256': digest(ROOT / 'control/build-tests/summary.json')})
    files = ['bin/B', 'bin/C', 'control/config.json', 'control/runtime.json', 'control/common.py',
             'control/linux_runner.py', 'control/run_matched.py', 'control/prepare_benchmark.py',
             'control/differential.py', 'control/differential/summary.json', 'control/source-reference.json',
             'control/reference.json', 'control/matched-protocol.json', 'control/correctness-gate.json',
             'control/build-tests/summary.json', 'control/build_tests.py',
             'control/freeze_runtime_libraries.py', 'control/runtime-linked-libraries.json']
    files += list(load(ROOT / 'control/source-reference.json')['files'])
    write_json(ROOT / 'control/pre-benchmark-freeze.json', {'files': {p: digest(ROOT / p) for p in files}})
    write_json(ROOT / 'control/host-before-benchmark.json', host_snapshot())
    print('Frozen binaries, source, runtime, protocol and references after tests/differential; timing needs separate launch.', flush=True)


if __name__ == '__main__':
    main()
