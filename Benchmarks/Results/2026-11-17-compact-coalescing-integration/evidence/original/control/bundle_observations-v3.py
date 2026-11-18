#!/usr/bin/env python3
"""Bundle audited numerical observations without copying stdout, binaries, or runtimes."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, required=True)
    parser.add_argument('--measurements', type=Path, required=True)
    parser.add_argument('--audits', type=Path, required=True)
    parser.add_argument('--platform', choices=['macos', 'arm64', 'x86_64'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--map', action='append', default=[], help='Explicit original audit-run prefix=local evidence prefix mapping')
    args = parser.parse_args()
    for key in ['experiment', 'measurements', 'audits', 'output']:
        setattr(args, key, getattr(args, key).resolve())
    mapping = []
    for item in args.map:
        original, local = item.split('=', 1)
        assert Path(original).is_absolute() and Path(local).is_absolute()
        mapping.append((original.rstrip('/'), str(Path(local).resolve()).rstrip('/')))
    mapping.sort(key=lambda pair: len(pair[0]), reverse=True)
    def mapped_path(value):
        text = str(value)
        for original, local in mapping:
            if text == original or text.startswith(original + '/'):
                return Path(local + text[len(original):]).resolve()
        return Path(text).resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    source_identities = {}
    index = {
        'passed': False,
        'started_at': now(),
        'platform': args.platform,
        'audit_path_mapping': mapping,
        'helper_sha256': sha(Path(__file__).read_bytes()),
        'record_policy': 'Original parsed JSON values plus original relative path, byte length and raw SHA256. native.time text is preserved exactly as UTF8. No stdout, stderr, binaries or runtime files are copied.',
        'scope': 'This bundles existing independently passed audits; it does not execute the product or replace the full-byte measurement audit.',
        'source_root': str(args.experiment),
        'phases': [],
        'totals': {key: 0 for key in ['measured_samples', 'warmups', 'measured_processes', 'warmup_processes', 'sample_records', 'process_records', 'native_time_records']},
    }

    def read(path, kind='json'):
        path = Path(path).resolve()
        relative = str(path.relative_to(args.experiment))
        before = path.stat()
        data = path.read_bytes()
        after = path.stat()
        fields = ['st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns']
        assert all(getattr(before, field) == getattr(after, field) for field in fields), ('Changed while reading', path)
        identity = {'original_relative_path': relative, 'raw_sha256': sha(data), 'raw_bytes': len(data)}
        if relative in source_identities:
            assert source_identities[relative] == identity
        source_identities[relative] = identity
        if kind == 'json':
            record = json.loads(data)
            assert json.loads(json.dumps(record, ensure_ascii=False, allow_nan=False)) == record
            return {**identity, 'record': record}
        if kind == 'text':
            text = data.decode('utf-8')
            assert text.encode('utf-8') == data
            return {**identity, 'text': text}
        assert kind == 'identity'
        return identity

    def save(path, value):
        data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
        with path.open('xb') as stream:
            stream.write(data)
        assert json.loads(path.read_bytes()) == value
        return {'file': str(path.relative_to(args.output)), 'sha256': sha(data), 'bytes': len(data)}

    try:
        driver = read(args.measurements / 'driver-summary.json')
        assert driver['record']['passed'] is True
        steps = driver['record']['steps']
        expected_phases = [(step['group'], step['phase']) for step in steps]
        assert len(expected_phases) == len(set(expected_phases))
        actual_phases = {(p.parent.parent.name, p.parent.name) for p in args.measurements.glob('*/*/summary.json')}
        assert actual_phases == set(expected_phases)
        primary_counts = {}
        for step in steps:
            group, phase = step['group'], step['phase']
            assert group in ['original', 'scale', 'sparse'] and phase in ['primary', 'followup']
            assert step['exit_code'] == 0
            run = args.measurements / group / phase
            audit_path = args.audits / (group + '-' + phase + '.json')
            audit = read(audit_path)
            summary = read(run / 'summary.json')
            assert audit['record']['passed'] is True and summary['record']['passed'] is True
            assert mapped_path(audit['record']['run']) == run
            assert audit['record']['group'] == group
            freeze = read(run / 'freeze.json', 'identity')
            assert audit['record']['all_output_bytes_verified'] is True
            assert audit['record']['resource_metrics_reconciled'] is True
            expected = {key: audit['record'][key] for key in ['measured_samples', 'warmups', 'measured_processes', 'warmup_processes']}
            assert all(summary['record'][key] == value for key, value in expected.items())
            sample_entries, process_entries = [], []
            counts = dict.fromkeys(expected, 0)
            native_count = 0
            process_by_path = {}
            for path in sorted(run.rglob('process.json')):
                relative = path.relative_to(run)
                assert relative.parts[0] == 'warmup' or re.fullmatch(r'round-0[1-6]', relative.parts[0])
                entry = read(path)
                process = entry['record']
                assert process['passed'] is True and process['exit_code'] == 0
                assert process['output_sha256'] and process['output_bytes'] >= 0
                key = 'warmup_processes' if relative.parts[0] == 'warmup' else 'measured_processes'
                counts[key] += 1
                native_path = path.parent / 'native.time'
                if args.platform == 'macos':
                    native = read(native_path, 'text')
                    rss = re.search(r'^\s*(\d+)\s+maximum resident set size\s*$', native['text'], re.M)
                    assert rss and int(rss[1]) == process['peak_rss_bytes']
                    entry['native_time'] = native
                    native_count += 1
                else:
                    assert not native_path.exists()
                    assert 'wait4_rusage' in process
                process_entries.append(entry)
                process_by_path[path] = process
            expected_processes = set()
            for path in sorted(run.rglob('sample.json')):
                relative = path.relative_to(run)
                assert relative.parts[0] == 'warmup' or re.fullmatch(r'round-0[1-6]', relative.parts[0])
                entry = read(path)
                sample = entry['record']
                assert sample['passed'] is True
                key = 'warmups' if relative.parts[0] == 'warmup' else 'measured_samples'
                counts[key] += 1
                for part in sample['parts']:
                    child = path.parent / part['label'] / 'process.json'
                    assert process_by_path[child] == part
                    expected_processes.add(child)
                sample_entries.append(entry)
            assert expected_processes == set(process_by_path)
            assert counts == expected, (group, phase, counts, expected)
            assert native_count == (len(process_entries) if args.platform == 'macos' else 0)
            assert counts['measured_samples'] == audit['record']['case_count'] * 12
            assert counts['warmups'] == audit['record']['case_count'] * 2
            if phase == 'primary':
                primary_counts[group] = audit['record']['case_count']
            bundle = {
                'platform': args.platform, 'group': group, 'phase': phase,
                'phase_summary': summary, 'independent_audit': audit,
                'original_freeze_identity': freeze, 'counts': counts,
                'sample_records': sample_entries, 'process_records': process_entries,
            }
            written = save(args.output / (group + '-' + phase + '.json'), bundle)
            index['phases'].append({**written, 'group': group, 'phase': phase, **counts,
                                    'sample_records': len(sample_entries), 'process_records': len(process_entries),
                                    'native_time_records': native_count,
                                    'audit_identity': {k: audit[k] for k in ['original_relative_path', 'raw_sha256', 'raw_bytes']}})
            for key, value in counts.items():
                index['totals'][key] += value
            index['totals']['sample_records'] += len(sample_entries)
            index['totals']['process_records'] += len(process_entries)
            index['totals']['native_time_records'] += native_count
        assert primary_counts == {'original': 11, 'scale': 12, 'sparse': 2}
        assert sum(primary_counts.values()) * 12 == 300
        assert sum(primary_counts.values()) * 2 == 50
        index['driver'] = save(args.output / 'driver.json', driver)
        if (args.audits / 'summary.json').exists():
            audit_summary = read(args.audits / 'summary.json')
            assert audit_summary['record']['passed'] is True
            totals = audit_summary['record'].get('totals')
            if totals:
                assert all(index['totals'][key] == value for key, value in totals.items() if key in index['totals'])
            index['audit_summary'] = save(args.output / 'audit-summary.json', audit_summary)
        elif (args.audits / 'driver-summary.json').exists():
            audit_driver = read(args.audits / 'driver-summary.json')
            assert audit_driver['record']['passed'] is True
            index['audit_driver'] = save(args.output / 'audit-driver.json', audit_driver)
        index['source_files'] = len(source_identities)
        index['source_inventory'] = save(args.output / 'source-identities.json', {'files': source_identities})
        index['passed'] = True
    except BaseException as error:
        index['error'] = repr(error)
        raise
    finally:
        index['finished_at'] = now()
        save(args.output / 'index.json', index)
        print(json.dumps({'passed': index['passed'], 'platform': args.platform, 'phases': len(index['phases']), 'totals': index['totals']}), flush=True)


if __name__ == '__main__':
    main()
