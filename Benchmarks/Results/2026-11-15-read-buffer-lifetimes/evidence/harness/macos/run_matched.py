#!/usr/bin/env python3
"""Matched B/C CLI controls. Prepare a fresh run directory; never retry in place."""
import argparse
import json
import statistics
import shutil
import os
import subprocess
from pathlib import Path
import base_runner as runner

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = json.loads((ROOT / 'control/context.json').read_text())
OLD = Path(CONTEXT['previous_comparison'])
PROTOCOL = json.loads((ROOT / 'control/matched-protocol.json').read_text())
TOOLS = ['B', 'C']
SCHEDULE = [('split', runner.CASES), ('native', runner.NATIVE_CASES)]
ROUNDS = 6


def invocation(tool, input_path, family):
    assert tool in TOOLS
    return [str(ROOT / 'bin' / tool), '--raw', '--representation', 'cidr', str(input_path)]


runner.invocation = invocation


def check_manifest(root, manifest):
    data = json.loads(manifest.read_text())
    for name, expected in data['files'].items():
        actual = runner.digest(root / name)
        if actual != expected:
            raise RuntimeError(f'Frozen file changed: {root / name}')
    return len(data['files'])


def validate():
    if shutil.disk_usage(ROOT).free < 3 * 1024**3:
        raise RuntimeError('Less than 3 GiB free; no cleanup performed')
    runtime = json.loads((ROOT / 'control/host-runtime.json').read_text())['commands']['runtime']
    environment = dict(os.environ)
    environment['DEVELOPER_DIR'] = CONTEXT['developer_dir']
    assert subprocess.check_output(runtime['command'], env=environment, text=True) == runtime['stdout']
    own = ROOT / 'control/pre-benchmark-freeze.json'
    own_data = json.loads(own.read_text())
    required = {'bin/B', 'bin/C', 'control/run_matched.py', 'control/base_runner.py',
                'control/matched-protocol.json', 'control/reference-output-freeze.json',
                'control/context.json', 'control/correctness-gate.json', 'control/source-freeze.json',
                'control/host-runtime.json'}
    missing = required - set(own_data['files'])
    if missing:
        raise RuntimeError(f'Pre-benchmark freeze lacks required inputs: {sorted(missing)}')
    assert ROOT.joinpath('fixtures').resolve() == OLD.joinpath('fixtures').resolve()
    assert PROTOCOL['measured_rounds'] == ROUNDS
    assert PROTOCOL['split_cases'] == runner.CASES
    assert PROTOCOL['native_cases'] == runner.NATIVE_CASES
    counts = {
        'new_run_files': check_manifest(ROOT, own),
        'source_files': check_manifest(ROOT.parent, ROOT / 'control/source-freeze.json'),
        'previous_comparison_files': check_manifest(OLD, OLD / 'control/freeze.json'),
        'reference_output_files': check_manifest(OLD, ROOT / 'control/reference-output-freeze.json'),
    }
    for suite, cases in SCHEDULE:
        for case in cases:
            reference = json.loads((OLD / 'warmup' / suite / case / 'cidrmerge/sample.json').read_text())
            assert reference['passed'] and reference['suite'] == suite and reference['case'] == case
            expected_families = [None] if suite == 'native' else [
                family for family in (4, 6)
                if (ROOT / 'fixtures' / case / f'ipv{family}.txt').stat().st_size
            ]
            assert [x['family'] for x in reference['parts']] == expected_families
            for part in reference['parts']:
                output = OLD / part['output']
                assert output.stat().st_size == part['output_bytes']
                assert runner.digest(output) == part['output_sha256']
    return counts


def make_summary(samples, warmups):
    assert len(samples) == 132
    assert sum(len(x['parts']) for x in samples) == 192
    assert len(warmups) == 22
    assert sum(len(x['parts']) for x in warmups) == 32
    groups, comparisons = [], []
    for suite, cases in SCHEDULE:
        for case in cases:
            by_tool = {}
            for tool in TOOLS:
                selected = [x for x in samples if (x['suite'], x['case'], x['tool']) == (suite, case, tool)]
                assert len(selected) == ROUNDS
                assert sorted(x['round'] for x in selected) == list(range(1, ROUNDS + 1))
                by_tool[tool] = {x['round']: x for x in selected}
                elapsed = [x['elapsed_ns'] / 1e9 for x in selected]
                rss = [x['peak_rss_bytes'] / 1048576 for x in selected]
                groups.append({'suite': suite, 'case': case, 'tool': tool, 'n': ROUNDS,
                               'elapsed_median_s': statistics.median(elapsed),
                               'elapsed_min_s': min(elapsed), 'elapsed_max_s': max(elapsed),
                               'peak_rss_median_mib': statistics.median(rss),
                               'peak_rss_min_mib': min(rss), 'peak_rss_max_mib': max(rss),
                               'cpu_median_s': statistics.median(x['cpu_seconds'] for x in selected)})
            paired = []
            for i in range(1, ROUNDS + 1):
                b, c = by_tool['B'][i], by_tool['C'][i]
                assert b['order'] == c['order']
                paired.append({'round': i, 'order': b['order'],
                               'elapsed_change_pct': (c['elapsed_ns'] / b['elapsed_ns'] - 1) * 100,
                               'rss_change_pct': (c['peak_rss_bytes'] / b['peak_rss_bytes'] - 1) * 100,
                               'elapsed_difference_s': (c['elapsed_ns'] - b['elapsed_ns']) / 1e9,
                               'rss_difference_mib': (c['peak_rss_bytes'] - b['peak_rss_bytes']) / 1048576})
            comparisons.append({'suite': suite, 'case': case, 'n_pairs': ROUNDS,
                                'paired_elapsed_change_median_pct': statistics.median(x['elapsed_change_pct'] for x in paired),
                                'paired_elapsed_change_min_pct': min(x['elapsed_change_pct'] for x in paired),
                                'paired_elapsed_change_max_pct': max(x['elapsed_change_pct'] for x in paired),
                                'paired_rss_change_median_pct': statistics.median(x['rss_change_pct'] for x in paired),
                                'paired_rss_difference_median_mib': statistics.median(x['rss_difference_mib'] for x in paired),
                                'pairs': paired})
    return {'completed_at': runner.stamp(), 'passed': True, 'samples': samples,
            'warmup_samples': warmups, 'groups': groups, 'comparisons': comparisons,
            'measured_samples': 132, 'measured_processes': 192,
            'excluded_warmup_samples': 22, 'excluded_warmup_processes': 32,
            'no_samples_removed_or_retried': True, 'all_outputs_retained': True,
            'all_outputs_match_original_independent_coverage': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true', help='Check frozen files; launch no benchmark processes.')
    args = parser.parse_args()
    before = validate()
    assert json.loads((ROOT / 'control/correctness-gate.json').read_text())['passed']
    if args.validate_only:
        print(json.dumps({'passed': True, 'validation': before}), flush=True)
        return
    measurements = ROOT / 'measurements'
    measurements.mkdir(exist_ok=False)
    runner.write_json(measurements / 'start.json', {'started_at': runner.stamp(), 'validation': before})
    samples, warmups = [], []
    try:
        for suite, cases in SCHEDULE:
            for iteration in range(ROUNDS + 1):
                phase = 'warmup' if iteration == 0 else f'round-{iteration:02}'
                order = TOOLS if iteration == 0 or iteration % 2 else list(reversed(TOOLS))
                offset = max(0, iteration - 1) % len(cases)
                case_order = cases[offset:] + cases[:offset]
                for case in case_order:
                    reference = json.loads((OLD / 'warmup' / suite / case / 'cidrmerge/sample.json').read_text())
                    for tool in order:
                        if shutil.disk_usage(ROOT).free < 3 * 1024**3:
                            raise RuntimeError('Less than 3 GiB free; no cleanup performed')
                        record = runner.run_one(suite, case, tool, measurements / suite / phase / case / tool, reference)
                        # The immutable per-process sample.json is written by base_runner;
                        # round/order metadata is retained in this aggregate and progress log.
                        enriched = {'round': iteration, 'order': order, **record}
                        (samples if iteration else warmups).append(enriched)
                        print(json.dumps({'suite': suite, 'round': iteration, 'order': order,
                                          'case': case, 'tool': tool, 'elapsed_s': record['elapsed_ns'] / 1e9,
                                          'peak_mib': record['peak_rss_bytes'] / 1048576}), flush=True)
        after = validate()
        summary = make_summary(samples, warmups)
        summary['validation_before'] = before
        summary['validation_after'] = after
        runner.write_json(measurements / 'summary.json', summary)
    except BaseException as error:
        runner.write_json(measurements / 'failed.json', {'finished_at': runner.stamp(), 'error': repr(error),
                          'completed_measured_samples': len(samples), 'completed_warmup_samples': len(warmups),
                          'no_retry_performed': True})
        raise


if __name__ == '__main__':
    main()
