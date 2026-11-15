#!/usr/bin/env python3
"""Record every resolved B/C shared library before measurements; no target execution."""
from pathlib import Path
import subprocess
from common import ROOT, digest, load, runtime_environment, stamp, write_json


def main():
    runtime = load(ROOT / 'control/runtime.json')
    env = {**runtime_environment(), 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}
    inventory = {'captured_at': stamp(), 'phase': 'premeasurement', 'environment': env,
                 'binary_sha256': {}, 'ldd': {}, 'libraries': {}, 'virtual_entries': []}
    for variant in ('B', 'C'):
        binary = ROOT / 'bin' / variant
        inventory['binary_sha256'][variant] = digest(binary)
        p = subprocess.run(['ldd', str(binary)], env=env, text=True, capture_output=True)
        assert p.returncode == 0 and 'not found' not in p.stdout, p.stderr + p.stdout
        inventory['ldd'][variant] = {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
        for line in p.stdout.splitlines():
            entry = line.split('=>', 1)[-1].strip().split(' (', 1)[0].strip()
            if not entry.startswith('/'):
                inventory['virtual_entries'].append({'variant': variant, 'line': line.strip()})
                continue
            path = Path(entry)
            assert path.is_file(), entry
            metadata = {'resolved_path': str(path.resolve()), 'bytes': path.stat().st_size,
                        'sha256': digest(path), 'mtime_ns': path.stat().st_mtime_ns}
            if entry in runtime['libswiftCore_sha256']:
                assert metadata['sha256'] == runtime['libswiftCore_sha256'][entry]
            if entry in inventory['libraries']:
                assert inventory['libraries'][entry] == metadata
            inventory['libraries'][entry] = metadata
    assert inventory['libraries']
    write_json(ROOT / 'control/runtime-linked-libraries.json', inventory)
    print('Frozen ' + str(len(inventory['libraries'])) + ' linked runtime libraries before measurement.', flush=True)


if __name__ == '__main__':
    main()
