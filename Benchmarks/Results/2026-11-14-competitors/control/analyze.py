#!/usr/bin/env python3
"""Summarize every completed measured sample; never trim or replace observations."""
from pathlib import Path
import datetime
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]

def percentile(values, fraction):
    ordered = sorted(values)
    location = (len(ordered) - 1) * fraction
    low = int(location)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (location - low)

def describe(values):
    return {'median': statistics.median(values), 'min': min(values), 'max': max(values),
            'p25': percentile(values, .25), 'p75': percentile(values, .75)}

def main():
    assert json.loads((ROOT / 'measurement-complete.json').read_text())['passed']
    matrix = json.loads((ROOT / 'verification-matrix.json').read_text())
    assert len(matrix) == 41 and all(item['passed'] for item in matrix)
    groups = {}
    samples = []
    for path in sorted((ROOT / 'runs').glob('*/*/*/*/sample.json')):
        sample = json.loads(path.read_text())
        assert sample['passed'] and sample['matches_verified_warmup_bytes']
        round_number = int(path.parents[2].name.split('-')[1])
        key = (sample['suite'], sample['case'], sample['tool'])
        groups.setdefault(key, {})[round_number] = sample
        samples.append({'suite': sample['suite'], 'case': sample['case'], 'tool': sample['tool'],
                        'round': round_number, 'elapsed_seconds': sample['elapsed_ns'] / 1e9,
                        'peak_rss_bytes': sample['peak_rss_bytes'], 'cpu_seconds': sample['cpu_seconds'],
                        'output_bytes': sample['output_bytes'],
                        'parts': [{k: part[k] for k in ('family', 'elapsed_ns', 'peak_rss_bytes',
                                                        'bsd_time', 'output_bytes', 'output_sha256',
                                                        'exit_code', 'stderr_bytes')} for part in sample['parts']]})
    assert len(samples) == 337, len(samples)
    rows = []
    for (suite, case, tool), rounds in sorted(groups.items()):
        expected_rounds = 8 if suite == 'split' else 9
        assert set(rounds) == set(range(1, expected_rounds + 1))
        baseline = groups[(suite, case, 'cidrmerge')]
        ordered = [rounds[index] for index in sorted(rounds)]
        row = {'suite': suite, 'case': case, 'tool': tool, 'samples': len(ordered),
               'elapsed_seconds': describe([item['elapsed_ns'] / 1e9 for item in ordered]),
               'peak_rss_mib': describe([item['peak_rss_bytes'] / 1048576 for item in ordered]),
               'cpu_seconds': describe([item['cpu_seconds'] for item in ordered]),
               'cpu_to_wall_ratio': describe([item['cpu_seconds'] / (item['elapsed_ns'] / 1e9) for item in ordered]),
               'paired_elapsed_tool_over_cidrmerge': describe([rounds[index]['elapsed_ns'] / baseline[index]['elapsed_ns'] for index in sorted(rounds)]),
               'output_bytes': ordered[0]['output_bytes']}
        assert len({item['output_bytes'] for item in ordered}) == 1
        rows.append(row)
    fixtures = {}
    for path in sorted((ROOT / 'fixtures').glob('*/expected.json')):
        expected = json.loads(path.read_text())
        manifest = json.loads((path.parent / 'manifest.json').read_text())
        fixtures[path.parent.name] = {key: expected[key] for key in ('input_count', 'family_counts',
            'coverage_sha256', 'range_count', 'minimal_cidr_count', 'addresses_covered')}
        fixtures[path.parent.name].update(recipe=manifest['recipe'], files=manifest['files'])
    result = {'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'measured_samples': len(samples), 'verified_combinations': len(matrix),
              'excluded_outliers': 0, 'automatic_retries': 0,
              'percentile_method': 'linear interpolation on sorted samples; descriptive, not confidence intervals',
              'fixtures': fixtures, 'groups': rows, 'samples': samples}
    with (ROOT / 'summary.json').open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    for suite in ['split', 'native']:
        print('\n' + suite.upper())
        for case in fixtures:
            entries = [row for row in rows if row['suite'] == suite and row['case'] == case]
            if not entries:
                continue
            print(case)
            for row in entries:
                print(f"  {row['tool']:13} {row['elapsed_seconds']['median']:.4f}s "
                      f"{row['peak_rss_mib']['median']:.2f}MiB "
                      f"range={row['elapsed_seconds']['min']:.4f}..{row['elapsed_seconds']['max']:.4f}s "
                      f"paired/cidr={row['paired_elapsed_tool_over_cidrmerge']['median']:.3f}")

if __name__ == '__main__':
    main()
