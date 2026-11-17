#!/usr/bin/env python3
"""Exact CLI parity for real descriptor failures and fragmented inputs; no timing claims."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def cases():
    result = []
    for grammar in ['text', 'searchbot']:
        for failure in ['missing', 'parent-file', 'directory', 'permissions', 'long-name', 'empty', 'dot']:
            result.append(dict(id=f'{grammar}-input-{failure}', grammar=grammar,
                               setup=f'input-{failure}', failure=True))
        for special in ['symlink-dotdot', 'file-trailing-slash', 'unicode-path']:
            result.append(dict(id=f'{grammar}-input-{special}', grammar=grammar,
                               setup=f'input-{special}', failure=None))
        for destination in ['missing-parent', 'directory', 'permissions']:
            result.append(dict(id=f'{grammar}-output-{destination}', grammar=grammar,
                               setup=f'output-{destination}', failure=True))
        for failure in ['checksum-directory', 'primary-after-checksum']:
            result.append(dict(id=f'{grammar}-{failure}', grammar=grammar,
                               setup=failure, failure=True))
        for transport in ['write-only-stdin', 'closed-stdin', 'broken-stdout']:
            result.append(dict(id=f'{grammar}-{transport}', grammar=grammar,
                               transport=transport, failure=True))
        if sys.platform.startswith('linux'):
            result.append(dict(id=f'{grammar}-full-stdout', grammar=grammar,
                               transport='full-stdout', failure=True))
    bom = b'\xef\xbb\xbf'
    text_inputs = {
        'unicode-bom-crlf': bom + ' \u200b192.0.2.129/24\u200b # caf\u00e9\r\n2001:DB8::1\r\n'.encode(),
        'bom-split-no-newline': bom + b'2001:db8::1',
        'repeated-cr': b'\r\n192.0.2.0/24\r\r\r\n2001:db8::/32\r\r',
        'invalid-after-hash': b'192.0.2.1\n# \xff\n',
        'invalid-split-utf8': b'192.0.2.1 #\xf0\x90\x80',
        'hash-combining': '192.0.2.1 #\u0301 ignored\n'.encode(),
        'zero-width-boundaries': '\u200b192.0.2.0/24\u200b\n\u200b2001:db8::/32\u200b\n'.encode(),
        'grapheme-boundary': ' \u0301192.0.2.1\n'.encode(),
        'long-comment': b'192.0.2.0/24 #' + b'x' * 131_071 + ' caf\u00e9\r\n2001:db8::/32\n'.encode(),
        'unicode-at-64k': b'#' + b'x' * 65_533 + '\u00e9\r\n192.0.2.1\n'.encode(),
        'invalid-after-64k': b'#' + b'x' * 65_535 + b'\xff\n192.0.2.1\n',
        'six-point-two-five-percent': b''.join(f'192.0.2.{2*i}\n'.encode() for i in range(15)) + b'192.0.2.0\n',
    }
    failures = {'invalid-after-hash', 'invalid-split-utf8', 'hash-combining', 'grapheme-boundary', 'invalid-after-64k'}
    searchbot_inputs = {
        'unicode-metadata': '{"metadata":"caf\u00e9 \U0001f30d","prefixes":[{"ipv4Prefix":"192.0.2.129/24"},{"ipv6Prefix":"2001:DB8::1/64"}]}'.encode(),
        'bom': bom + b'{"prefixes":[]}',
        'invalid-utf8': b'{"prefixes":[],"metadata":"\xff"}',
        'long-metadata': b'{"metadata":"' + b'x' * 131_071 + '\u00e9","prefixes":[{"ipv6Prefix":"2001:db8::/32"}]}'.encode(),
    }
    for grammar, inputs in [('text', text_inputs), ('searchbot', searchbot_inputs)]:
        for name, data in inputs.items():
            for output in ['raw', 'json', 'checksum']:
                result.append(dict(id=f'{grammar}-fragment-{name}-{output}', grammar=grammar,
                                   transport='fragmented', data=data, output=output,
                                   failure=(name in failures or name == 'invalid-utf8')))
    return result


def prepare(directory, case):
    # Only this run's explicitly created per-case workspace is reset between variants.
    if directory.exists():
        for current, dirs, files in os.walk(directory):
            os.chmod(current, 0o777)
            for name in files:
                os.chmod(Path(current) / name, 0o666)
        shutil.rmtree(directory)
    directory.mkdir(mode=0o777)
    os.chmod(directory, 0o777)
    grammar = case['grammar']
    data = case.get('data', b'192.0.2.129/24\n2001:DB8::1/64\n' if grammar == 'text' else
                    b'{"prefixes":[{"ipv4Prefix":"192.0.2.129/24"},{"ipv6Prefix":"2001:DB8::1/64"}]}')
    (directory / 'input.txt').write_bytes(data)
    (directory / 'input.txt').chmod(0o644)
    args = ['--input-format', grammar, '--stats', '--representation', 'cidr']
    setup = case.get('setup', '')
    transport = case.get('transport', 'file')
    if setup == 'input-empty':
        args += ['']
    elif setup == 'input-dot':
        args += ['.']
    elif setup == 'input-file-trailing-slash':
        args += ['input.txt/']
    elif setup == 'input-unicode-path':
        (directory / 'café-🌍.txt').write_bytes(data)
        args += ['café-🌍.txt']
    elif setup == 'input-symlink-dotdot':
        (directory / 'other' / 'nested').mkdir(parents=True)
        alternative = b'198.51.100.0/24\n' if grammar == 'text' else b'{"prefixes":[{"ipv4Prefix":"198.51.100.0/24"}]}'
        (directory / 'other' / 'input.txt').write_bytes(alternative)
        (directory / 'link').symlink_to('other/nested', target_is_directory=True)
        args += ['link/../input.txt']
    elif setup == 'input-missing':
        args += ['missing-parent/input.txt']
    elif setup == 'input-parent-file':
        args += ['input.txt/child']
    elif setup == 'input-directory':
        (directory / 'input-directory').mkdir()
        args += ['input-directory']
    elif setup == 'input-permissions':
        (directory / 'input.txt').chmod(0)
        args += ['input.txt']
    elif setup == 'input-long-name':
        args += ['x' * 300]
    elif transport == 'file':
        args += ['input.txt']
    if setup == 'output-missing-parent':
        args += ['--output', 'missing-parent/output.txt']
    elif setup == 'output-directory':
        (directory / 'output.txt').mkdir()
        (directory / 'output.txt' / 'sentinel').write_bytes(b'keep directory contents\n')
        args += ['--output', 'output.txt']
    elif setup == 'output-permissions':
        (directory / 'blocked').mkdir(mode=0o555)
        (directory / 'blocked').chmod(0o555)
        args += ['--output', 'blocked/output.txt']
    elif setup == 'checksum-directory':
        (directory / 'output.txt').write_bytes(b'keep previous output\n')
        (directory / 'output.txt.sha256').mkdir()
        (directory / 'output.txt.sha256' / 'sentinel').write_bytes(b'keep checksum directory\n')
        args += ['--output', 'output.txt', '--checksum']
    elif setup == 'primary-after-checksum':
        (directory / 'output.txt').mkdir()
        (directory / 'output.txt' / 'sentinel').write_bytes(b'keep output directory\n')
        args += ['--output', 'output.txt', '--checksum']
    elif case.get('output') == 'checksum':
        args += ['--output', 'output.txt', '--checksum']
    if case.get('output') == 'json':
        args += ['--json']
    else:
        args += ['--raw']
    return args, data


def snapshot(directory, artifact):
    result = []
    for path in sorted(directory.rglob('*')):
        info = path.lstat()
        item = dict(path=str(path.relative_to(directory)), mode=stat.S_IMODE(info.st_mode))
        if path.is_symlink():
            item['kind'] = 'symlink'
            item['target'] = os.readlink(path)
        elif path.is_dir():
            item['kind'] = 'directory'
        elif path.is_file():
            item['kind'] = 'file'
            try:
                data = path.read_bytes()
            except PermissionError:
                path.chmod(item['mode'] | stat.S_IRUSR)
                try:
                    data = path.read_bytes()
                finally:
                    path.chmod(item['mode'])
            item.update(size=len(data), sha256=sha(data))
            target = artifact / 'files' / item['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        else:
            item['kind'] = 'other'
        result.append(item)
    return result


def run(binary, directory, artifact, case, args, data, timeout):
    artifact.mkdir(parents=True)
    transport = case.get('transport', 'file')
    root_drop = os.geteuid() == 0 and case.get('setup', '').endswith('permissions')
    def child_setup():
        if root_drop:
            os.setgroups([])
            os.setgid(65534)
            os.setuid(65534)
        if transport == 'closed-stdin':
            os.close(0)
    stdin = subprocess.DEVNULL
    stdout = subprocess.PIPE
    handles = []
    writer = None
    writer_events = []
    if transport == 'write-only-stdin':
        stdin = os.open(directory / 'input.txt', os.O_WRONLY)
        handles.append(stdin)
    elif transport == 'fragmented':
        stdin, write_fd = os.pipe()
        handles.append(stdin)
        def feed():
            position = 0
            chunks = [1] if len(data) < 4096 else [1, 2, 3, 4093]
            try:
                while position < len(data):
                    count = min(chunks[len(writer_events) % len(chunks)], len(data) - position)
                    wrote = os.write(write_fd, data[position:position + count])
                    writer_events.append(dict(offset=position, bytes=wrote))
                    position += wrote
                    time.sleep(0.0002)
            except BrokenPipeError:
                writer_events.append(dict(broken_pipe_at=position))
            finally:
                os.close(write_fd)
        writer = threading.Thread(target=feed, daemon=True)
    elif transport in ['broken-stdout', 'full-stdout', 'closed-stdin']:
        stdin = subprocess.PIPE if transport != 'closed-stdin' else subprocess.DEVNULL
    if transport == 'broken-stdout':
        read_fd, stdout = os.pipe()
        os.close(read_fd)
        handles.append(stdout)
    elif transport == 'full-stdout':
        stdout = os.open('/dev/full', os.O_WRONLY)
        handles.append(stdout)
    environment = dict(os.environ)
    environment.update(LANG='C', LC_ALL='C', TZ='UTC')
    command = [str(binary), *args]
    started = datetime.now(timezone.utc).isoformat()
    process = subprocess.Popen(command, cwd=directory, env=environment, stdin=stdin,
                               stdout=stdout, stderr=subprocess.PIPE, start_new_session=True,
                               preexec_fn=child_setup)
    for handle in handles:
        os.close(handle)
    if writer:
        writer.start()
    timed_out = False
    try:
        output, error = process.communicate(data if stdin == subprocess.PIPE else None, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        output, error = process.communicate()
    if writer:
        writer.join(timeout=1)
    output = output or b''
    error = error or b''
    (artifact / 'stdout.bin').write_bytes(output)
    (artifact / 'stderr.bin').write_bytes(error)
    result = dict(command=command, cwd=str(directory), started=started, status=process.returncode,
                  timeout=timed_out, dropped_uid=65534 if root_drop else None,
                  stdout_sha256=sha(output), stderr_sha256=sha(error), stdout_bytes=len(output),
                  stderr_bytes=len(error), fragmented_writer_events=writer_events,
                  writer_still_alive=writer.is_alive() if writer else False,
                  files=snapshot(directory, artifact))
    write_json(artifact / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=30)
    options = parser.parse_args()
    baseline = options.baseline.resolve(strict=True)
    candidate = options.candidate.resolve(strict=True)
    root = options.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    work = root / 'work'
    work.mkdir(mode=0o755)
    records = []
    selected = cases()
    write_json(root / 'manifest.json', dict(platform=sys.platform, uid=os.geteuid(),
        baseline=dict(path=str(baseline), sha256=sha(baseline.read_bytes())),
        candidate=dict(path=str(candidate), sha256=sha(candidate.read_bytes())),
        harness_sha256=sha(Path(__file__).read_bytes()), timeout=options.timeout,
        cases=[{**{k:v for k,v in case.items() if k != 'data'},
                'data_sha256':sha(case['data']) if 'data' in case else None} for case in selected]))
    for case in selected:
        directory = work / case['id']
        observations = {}
        for label, binary in [('B', baseline), ('C', candidate)]:
            args, data = prepare(directory, case)
            artifact = root / 'observations' / case['id'] / label
            observations[label] = run(binary, directory, artifact, case, args, data, options.timeout)
        fields = ['status', 'stdout_sha256', 'stderr_sha256', 'files']
        differences = [field for field in fields if observations['B'][field] != observations['C'][field]]
        failures = []
        for label, observation in observations.items():
            if observation['timeout'] or observation['writer_still_alive']:
                failures.append(label + '-timeout-or-writer-leak')
            if case['failure'] is not None and case['failure'] != (observation['status'] != 0):
                failures.append(label + '-unexpected-status')
        record = dict(id=case['id'], equal=not differences and not failures,
                      differences=differences, failures=failures,
                      baseline_status=observations['B']['status'], candidate_status=observations['C']['status'])
        records.append(record)
        write_json(root / 'comparisons.json', records)
        if not record['equal']:
            print(json.dumps(record), flush=True)
    summary = dict(total=len(records), passed=sum(x['equal'] for x in records),
                   failed=sum(not x['equal'] for x in records),
                   failures=[x for x in records if not x['equal']])
    write_json(root / 'summary.json', summary)
    print(json.dumps(summary), flush=True)
    return 0 if summary['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
