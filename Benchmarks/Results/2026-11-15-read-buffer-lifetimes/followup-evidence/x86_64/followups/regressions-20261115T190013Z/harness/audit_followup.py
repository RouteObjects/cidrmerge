#!/usr/bin/env python3
"""Independent evidence-only audit of a separate Linux six-pair follow-up."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
import traceback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('followup')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-runtime-files', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    out = root / 'followups' / args.followup
    counts = Counter()
    receipt = {'passed': False, 'scope': 'Independent evidence-only audit; no harness imports or subprocess execution',
               'followup': str(out), 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}

    def load(path):
        return json.loads(path.read_text())

    def check(condition, label):
        counts['assertions'] += 1
        if not condition:
            raise AssertionError(label)

    def sha(path):
        with path.open('rb') as stream:
            value = hashlib.file_digest(stream, 'sha256').hexdigest()
        counts['files_hashed'] += 1
        counts['bytes_hashed'] += path.stat().st_size
        return value

    def close(a, b, label):
        check(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), label)

    try:
        summary = load(out / 'summary.json')
        selection = load(out / 'selection.json')
        start = load(out / 'start.json')
        primary = load(root / 'measurements/summary.json')
        protocol = load(root / 'control/matched-protocol.json')
        reference = load(root / 'control/reference.json')
        freeze = load(root / 'control/pre-benchmark-freeze.json')
        runtime = load(root / 'control/runtime.json')
        inventory = load(root / 'control/runtime-linked-libraries.json')
        selected = {(x['suite'], x['case']) for x in selection['cases']}
        primary_hash = sha(root / 'measurements/summary.json')
        check(primary_hash == selection['primary_summary_sha256'] == start['primary_summary_sha256'] == summary['primary_summary_sha256'], 'primary summary binding')
        check(primary['passed'] and summary['passed'] and summary['separate_followup_not_pooled'], 'successful separate follow-up')
        triggered = {(c['suite'], c['case']) for c in primary['comparisons'] if any(p['elapsed_change_pct'] > 5 or p['rss_change_pct'] > 5 for p in c['pairs'])}
        check(selected == triggered, 'complete selection of all individual primary regressions above five percent')
        check(summary['selected_cases'] == selection['cases'], 'selection/summary parity')
        check(start['script_sha256'] == sha(root / 'control/followup_runner.py'), 'follow-up driver hash')
        check(start['child_harness_sha256'] == sha(root / 'control/linux_runner.py') == freeze['files']['control/linux_runner.py'], 'unchanged frozen child harness')
        for relative, expected in freeze['files'].items():
            check(sha(root / relative) == expected, 'frozen file: ' + relative)
        for relative, metadata in reference['inputs'].items():
            path = root / relative
            check(path.stat().st_size == metadata['bytes'] and sha(path) == metadata['sha256'], 'fixture: ' + relative)
        check(start['validation'] == primary['validation_after'], 'same premeasurement freeze validation')
        check(inventory['phase'] == 'premeasurement', 'runtime inventory predates measurements')
        if args.check_runtime_files:
            for path, metadata in inventory['libraries'].items():
                check(sha(Path(path)) == metadata['sha256'], 'runtime library: ' + path)
            receipt['runtime_libraries_verified'] = len(inventory['libraries'])
        else:
            receipt['runtime_libraries_verified'] = False
        expected_sequence = []
        for suite, all_cases in [('split', protocol['split_cases']), ('native', protocol['native_cases'])]:
            cases = [c for c in all_cases if (suite, c) in selected]
            if not cases:
                continue
            for iteration in range(7):
                order = ['B', 'C'] if iteration == 0 or iteration % 2 else ['C', 'B']
                offset = max(0, iteration - 1) % len(cases)
                for case in cases[offset:] + cases[:offset]:
                    for tool in order:
                        expected_sequence.append((suite, iteration, case, tool, order))
        measured, warmups = summary['samples'], summary['warmup_samples']
        check(len(measured) == summary['measured_samples'] == 12 * len(selected), 'measured sample count')
        check(len(warmups) == summary['excluded_warmup_samples'] == 2 * len(selected), 'warmup count')
        indexed = {(x['suite'], x['round'], x['case'], x['tool']): x for x in measured + warmups}
        check(len(indexed) == len(expected_sequence), 'unique samples')
        seen_outputs, seen_samples, seen_metrics, seen_stderr, native_roots, execution_times, progress = set(), set(), set(), set(), set(), [], []
        for suite, iteration, case, tool, order in expected_sequence:
            row = indexed[(suite, iteration, case, tool)]
            check(row['order'] == order, 'balanced pair order')
            phase = 'warmup' if iteration == 0 else f'round-{iteration:02}'
            location = out / 'measurements' / suite / phase / case / tool
            seen_samples.add(str(location / 'sample.json'))
            progress.append({'suite': suite, 'case': case, 'tool': tool, 'round': iteration, 'elapsed_s': row['elapsed_ns'] / 1e9, 'peak_mib': row['peak_rss_bytes'] / 1048576})
            check(load(location / 'sample.json') == {k: v for k, v in row.items() if k not in ('round', 'order')}, 'raw sample parity')
            check(row['passed'] and row['matches_verified_warmup_bytes'] and 'error' not in row, 'successful sample')
            check(row['free_bytes_before'] >= protocol['minimum_free_bytes'], 'disk guard')
            refs = reference['expected'][suite][case]['parts']
            check(len(row['parts']) == len(refs), 'family partition count')
            for part, expected in zip(row['parts'], refs):
                family = str(part['family'] or 'mixed')
                stdout, stderr = location / (family + '.stdout'), location / (family + '.stderr')
                check(str(stdout) not in seen_outputs, 'unique output path')
                seen_outputs.add(str(stdout))
                seen_stderr.add(str(stderr))
                seen_metrics.add(str(location / (family + '.rusage.json')))
                native_root = Path(part['command'][0]).parent.parent
                native_roots.add(str(native_root))
                check(part['family'] == expected['family'] and part['input'] == expected['input'], 'family and input')
                check(load(location / (family + '.rusage.json')) == part, 'raw wait4 metrics parity')
                check(part['raw_metrics'] == str((location / (family + '.rusage.json')).relative_to(root)), 'metrics path')
                check(part['output'] == str(stdout.relative_to(root)) and part['stderr'] == str(stderr.relative_to(root)), 'output paths')
                check(part['command'] == [str(native_root / 'bin' / tool), '--raw', '--representation', 'cidr', str(native_root / expected['input'])], 'measured command')
                env = {'PATH': runtime['toolchain_bin'] + ':/usr/bin:/bin', 'LD_LIBRARY_PATH': ':'.join(runtime['library_paths']), 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC', 'TMPDIR': str(native_root / location.relative_to(root) / ('tmp-' + family)) + '/'}
                check(part['environment'] == env, 'controlled environment')
                check(sha(stdout) == part['output_sha256'] == expected['output_sha256'], 'exact independent-reference output hash')
                check(stdout.stat().st_size == part['output_bytes'] == expected['output_bytes'], 'output byte count')
                check(part['exit_code'] == 0 and stderr.stat().st_size == part['stderr_bytes'] == 0 and 'error' not in part, 'exit/stderr')
                usage = part['wait4_rusage']
                check(part['elapsed_ns'] > 0 and part['peak_rss_bytes'] == int(usage['ru_maxrss']) * 1024 > 0, 'elapsed and KiB-to-bytes RSS')
                close(part['cpu_seconds'], usage['ru_utime'] + usage['ru_stime'], 'CPU total')
                counts['outputs_verified'] += 1
            check(row['elapsed_ns'] == sum(x['elapsed_ns'] for x in row['parts']), 'sample elapsed sum')
            check(row['peak_rss_bytes'] == max(x['peak_rss_bytes'] for x in row['parts']), 'sample peak RSS maximum')
            close(row['cpu_seconds'], sum(x['cpu_seconds'] for x in row['parts']), 'sample CPU sum')
            check(row['output_bytes'] == sum(x['output_bytes'] for x in row['parts']), 'sample output sum')
            execution_times.append((row['started_at'], row['finished_at']))
        check(len(native_roots) == 1, 'single measured native root')
        for pattern, expected in [('*.stdout', seen_outputs), ('*.stderr', seen_stderr), ('sample.json', seen_samples), ('*.rusage.json', seen_metrics)]:
            check({str(p) for p in (out / 'measurements').rglob(pattern)} == expected, 'complete raw inventory: ' + pattern)
        check(not list(out.rglob('failed.json')), 'no unaccounted failure receipt')
        check([json.loads(line) for line in (out / 'progress.log').read_text().splitlines()] == progress, 'complete progress sequence and metrics')
        check(all(a <= b for a, b in execution_times), 'sample start/end timestamps')
        check(all(execution_times[i][1] <= execution_times[i + 1][0] for i in range(len(execution_times) - 1)), 'sequential alternating execution')
        groups = {(g['suite'], g['case'], g['tool']): g for g in summary['groups']}
        comparisons = {(g['suite'], g['case']): g for g in summary['comparisons']}
        check(len(groups) == 2 * len(selected) and set(comparisons) == selected, 'group inventory')
        for suite, case in sorted(selected):
            for tool in ['B', 'C']:
                rows = [indexed[(suite, i, case, tool)] for i in range(1, 7)]
                group = groups[(suite, case, tool)]
                check(group['n'] == 6, 'six observations per configuration')
                for field, key, scale in [('elapsed', 'elapsed_ns', 1e9), ('peak_rss', 'peak_rss_bytes', 1048576)]:
                    values = [x[key] / scale for x in rows]
                    suffix = 's' if field == 'elapsed' else 'mib'
                    for stat, expected in [('median', statistics.median(values)), ('min', min(values)), ('max', max(values))]:
                        close(group[f'{field}_{stat}_{suffix}'], expected, 'group descriptive statistic')
                close(group['cpu_median_s'], statistics.median(x['cpu_seconds'] for x in rows), 'group CPU median')
            comparison = comparisons[(suite, case)]
            check(comparison['n_pairs'] == 6 and len(comparison['pairs']) == 6, 'six paired comparisons')
            for i, pair in enumerate(comparison['pairs'], 1):
                b, c = indexed[(suite, i, case, 'B')], indexed[(suite, i, case, 'C')]
                check(pair['round'] == i and pair['order'] == b['order'] == c['order'], 'pair identity')
                for key, wanted in [('elapsed_change_pct', (c['elapsed_ns'] / b['elapsed_ns'] - 1) * 100), ('rss_change_pct', (c['peak_rss_bytes'] / b['peak_rss_bytes'] - 1) * 100), ('elapsed_difference_s', (c['elapsed_ns'] - b['elapsed_ns']) / 1e9), ('rss_difference_mib', (c['peak_rss_bytes'] - b['peak_rss_bytes']) / 1048576)]:
                    close(pair[key], wanted, 'paired metric: ' + key)
            pairs = comparison['pairs']
            for key, wanted in [('paired_elapsed_change_median_pct', statistics.median(x['elapsed_change_pct'] for x in pairs)), ('paired_elapsed_change_min_pct', min(x['elapsed_change_pct'] for x in pairs)), ('paired_elapsed_change_max_pct', max(x['elapsed_change_pct'] for x in pairs)), ('paired_rss_change_median_pct', statistics.median(x['rss_change_pct'] for x in pairs)), ('paired_rss_difference_median_mib', statistics.median(x['rss_difference_mib'] for x in pairs))]:
                close(comparison[key], wanted, 'comparison statistic: ' + key)
        receipt.update(passed=True, audit_script_sha256=sha(Path(__file__)), summary_sha256=sha(out / 'summary.json'), primary_summary_sha256=primary_hash, native_root=next(iter(native_roots)),
                       frozen_files_verified=len(freeze['files']), fixtures_verified=len(reference['inputs']),
                       measured_samples_verified=len(measured), warmup_samples_verified=len(warmups),
                       measured_processes_verified=sum(len(x['parts']) for x in measured), warmup_processes_verified=sum(len(x['parts']) for x in warmups),
                       pairs_verified=6 * len(selected), comparisons=summary['comparisons'], groups=summary['groups'],
                       all_outputs_match_original_independent_coverage=True, separate_followup_not_pooled=True)
    except BaseException as error:
        receipt.update(error=repr(error), traceback=traceback.format_exc())
    receipt.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), counters=dict(counts))
    with args.output.open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('comparisons', 'groups', 'traceback')}, indent=2))
    if not receipt['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
