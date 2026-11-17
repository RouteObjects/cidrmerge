#!/usr/bin/env python3
"""Check exact large stdout output through a deliberately slow successful pipe."""
import argparse
from datetime import datetime, timezone
import errno
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def observed_pipe_capacity():
    read_fd, write_fd = os.pipe()
    os.set_blocking(write_fd, False)
    count = 0
    try:
        while True:
            count += os.write(write_fd, b'x' * 65536)
    except BlockingIOError:
        return count
    finally:
        os.close(write_fd)
        os.close(read_fd)


def run(binary, fixture, directory, reference, timeout):
    directory.mkdir()
    output_path = directory / 'stdout.bin'
    stderr_path = directory / 'stderr.bin'
    chunks = []
    reader_errors = []
    digest = hashlib.sha256()
    command = [str(binary), '--raw', '--representation', 'cidr', '--stats', str(fixture)]
    environment = dict(os.environ)
    environment.update(LANG='C', LC_ALL='C', TZ='UTC')
    with stderr_path.open('wb') as stderr:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=stderr, env=environment, start_new_session=True)
        pipe_buf = os.fpathconf(process.stdout.fileno(), 'PC_PIPE_BUF')
        def consume():
            try:
                with output_path.open('wb') as output:
                    while True:
                        data = os.read(process.stdout.fileno(), 4093)
                        if not data:
                            break
                        output.write(data)
                        digest.update(data)
                        chunks.append(len(data))
                        time.sleep(0.001)
            except BaseException as error:
                reader_errors.append(repr(error))
        thread = threading.Thread(target=consume, daemon=True)
        thread.start()
        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
        thread.join(timeout=5)
        process.stdout.close()
    result = dict(command=command, binary_sha256=sha(binary.read_bytes()), returncode=process.returncode,
                  timeout=timed_out, reader_alive=thread.is_alive(), reader_errors=reader_errors,
                  pipe_atomic_write_limit=pipe_buf, reader_chunk_limit=4093, reader_delay_seconds=0.001,
                  reads=chunks, bytes=sum(chunks), stdout_sha256=digest.hexdigest(),
                  stderr_sha256=sha(stderr_path.read_bytes()),
                  independent_reference_match=output_path.read_bytes() == reference)
    dump(directory / 'result.json', result)
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
    count = 30000
    ipv4 = [str(ipaddress.IPv4Address(0x0A000000 + 2*i)) for i in range(count)]
    ipv6_base = int(ipaddress.IPv6Address('2001:db8::'))
    ipv6 = [str(ipaddress.IPv6Address(ipv6_base + 2*i)) for i in range(count)]
    fixture = root / 'input.txt'
    fixture.write_text('\n'.join(ipv4 + ipv6) + '\n')
    # Every address is separated by a one-address hole; exact cover must retain singleton CIDRs.
    reference = ('\n'.join([x+'/32' for x in ipv4] + [x+'/128' for x in ipv6]) + '\n').encode()
    (root / 'reference.bin').write_bytes(reference)
    capacity = observed_pipe_capacity()
    assert len(reference) > capacity * 2, (len(reference), capacity)
    dump(root / 'manifest.json', dict(created=datetime.now(timezone.utc).isoformat(),
        harness_sha256=sha(Path(__file__).read_bytes()), fixture_sha256=sha(fixture.read_bytes()),
        reference_sha256=sha(reference), reference_bytes=len(reference), entries=count*2,
        observed_nonblocking_pipe_capacity=capacity, timeout=options.timeout,
        reference_method='independent ipaddress formatting of disjoint singleton CIDRs'))
    records = {label:run(binary, fixture, root/label, reference, options.timeout)
               for label,binary in [('B',baseline),('C',candidate)]}
    equal = all(records['B'][key] == records['C'][key] for key in ['returncode','stdout_sha256','stderr_sha256'])
    success = equal and all(r['returncode']==0 and not r['timeout'] and not r['reader_alive']
                           and not r['reader_errors'] and r['independent_reference_match']
                           for r in records.values())
    summary = dict(passed=success, equal=equal, reference_bytes=len(reference), entries=count*2,
                   baseline_status=records['B']['returncode'],candidate_status=records['C']['returncode'])
    dump(root / 'summary.json', summary)
    print(json.dumps(summary))
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
