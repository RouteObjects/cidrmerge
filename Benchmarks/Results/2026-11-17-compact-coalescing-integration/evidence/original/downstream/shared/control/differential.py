#!/usr/bin/env python3
"""Exact CLI parity gate for optional normalization accounting; no timing claims."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from datetime import datetime, timezone


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fixtures():
    bom = b"\xef\xbb\xbf"
    values = {
        "mixed-forms": (b" 192.0.2.1 # host\n192.0.3.129/24\n192.0.4.2...192.0.4.7\n"
                        b"2001:DB8::1\n2001:db8:1::123/64\n2001:DB8:2::1...2001:DB8:2::F\n", True),
        "empty": (b"", True),
        "comments-only": ("# ASCII\x00\x7f\n# caf\u00e9\n \t\v\f\r\n".encode(), True),
        "ascii-edges": (b"\t\v\f\r 192.0.2.0/24 \t\v\f\r\r\n", True),
        "ascii-comment-delimiters": (b"192.0.2.0/24## ignored / ...\x00\x7f\n", True),
        "unicode-edges": ("\u00a0\u2003\u2028192.0.2.0/24\u2029\u3000\n".encode(), True),
        "unicode-comment": ("192.0.2.0/24 # caf\u00e9 \U0001f30d\n".encode(), True),
        "bom-first": (bom + b"192.0.2.1\r\n", True),
        "bom-only": (bom, True),
        # Foundation's BOM decoding behavior is compared within each platform.
        "bom-later": (b"192.0.2.1\n" + bom + b"192.0.2.2\n", None),
        "bom-double": (bom + bom + b"192.0.2.1\n", None),
        "bom-after-space": (b" " + bom + b"192.0.2.1\n", False),
        "bom-interior": (b"192.0.2." + bom + b"1\n", False),
        "eof": (b"192.0.2.0/24", True),
        "repeated-cr": (b"\r\n192.0.2.0/24\r\r\r\n\n", True),
        "delimiter-range-first": (b"192.0.2.1...192.0.2.2/32\n", False),
        "delimiter-network-first": (b"192.0.2.1/32...192.0.2.2\n", False),
        "additional-columns": (b"# line one\n 192.0.2.0/24 64496 # ignored\n", False),
        "interior-tab": (b"2001:db8::1\t2001:db8::2\n", False),
        "interior-unicode-space": ("192.0.2.1\u00a0192.0.2.2\n".encode(), False),
        "nul-interior": (b"192.0.2.\x001\n", False),
        "hash-combining": ("192.0.2.1 #\u0301 comment\n".encode(), False),
        "hash-keycap": ("192.0.2.1 #\ufe0f\u20e3 comment\n".encode(), False),
        "comment-only-combining": ("#\u0301 comment\n".encode(), False),
        "invalid-utf8-token": (b"192.0.2.0/24\n\xff\n", False),
        "invalid-utf8-comment": (b"192.0.2.0/24\n#\xff\n", False),
        "invalid-utf8-precedence": (b"bad #\xc3(\n", False),
        "truncated-utf8-comment": (b"192.0.2.1 #\xf0\x90", False),
        "surrogate-comment": (b"192.0.2.1 #\xed\xa0\x80\n", False),
    }
    prefix = b"192.0.2.0/24 #"
    padding = b"x" * (65535 - len(prefix))
    values["chunk-crlf"] = (prefix + padding + b"\r\n2001:db8::/32", True)
    values["chunk-unicode"] = (prefix + padding + "\u00e9\n2001:db8::/32\n".encode(), True)
    values["chunk-invalid-comment"] = (b"192.0.2.0/24\n#" + b"x" * 65536 + b"\xff\n", False)
    for byte in list(range(32)) + [127]:
        if byte not in range(9, 14):
            values[f"control-{byte:02x}"] = (bytes([byte]) + b"192.0.2.1" + bytes([byte, 10]), False)
    return values


def cases(values):
    result = [{"id": name + "-file", "fixture": name, "stdin": False,
               "flags": ["--raw", "--stats"], "checksum": False}
              for name in values]
    for name in ["mixed-forms", "comments-only", "hash-combining", "hash-keycap",
                 "invalid-utf8-comment", "invalid-utf8-precedence", "chunk-unicode", "chunk-invalid-comment"]:
        result.append({"id": name + "-stdin", "fixture": name, "stdin": True,
                       "flags": ["--raw", "--stats"], "checksum": False})
    for representation in ["ranges", "cidr"]:
        for output_format in ["raw", "json"]:
            result.append({"id": f"mixed-{representation}-{output_format}", "fixture": "mixed-forms",
                           "stdin": False, "flags": ["--" + output_format, "--representation", representation, "--stats"],
                           "checksum": False})
            result.append({"id": f"checksum-{representation}-{output_format}", "fixture": "mixed-forms",
                           "stdin": False, "flags": ["--" + output_format, "--representation", representation,
                                                       "--stats", "--checksum", "--output", "output.txt"],
                           "checksum": True})
    result.append({"id": "invalid-checksum-output", "fixture": "invalid-utf8-comment", "stdin": False,
                   "flags": ["--stats", "--checksum", "--output", "output.txt"], "checksum": True})
    return result


_text_fixtures = fixtures
_text_cases = cases

def fixtures():
    values = _text_fixtures()
    documents = {
        "mixed": ('{"prefixes":[{"ipv4Prefix":"192.0.2.129/24"},{"ipv6Prefix":"2001:DB8::123/64"},{"ipv4Prefix":"198.51.100.0/24"},{"ipv6Prefix":"2001:db8:1::/64"}]}', True),
        "empty": ('{"prefixes":[]}', True),
        "unknown-duplicates": ('{"meta":1,"meta":2,"prefixes":[{"ipv4Prefix":"192.0.2.129/24","label":"a","label":"b"}]}', True),
        "escaped-keys": (r'{"pre\u0066ixes":[{"ipv6\u0050refix":"2001:DB8::123/64"}]}', True),
        "duplicate-root": ('{"prefixes":[],"prefixes":[]}', False),
        "duplicate-key-escaped": (r'{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv4\u0050refix":"198.51.100.0/24"}]}', False),
        "wrong-type": ('{"prefixes":[{"ipv4Prefix":17}]}', False),
        "wrong-family": ('{"prefixes":[{"ipv6Prefix":"192.0.2.0/24"}]}', False),
        "null-value": ('{"prefixes":[{"ipv4Prefix":null}]}', False),
        "both-families": ('{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv6Prefix":"2001:db8::/32"}]}', False),
        "missing-member": ('{"prefixes":[{}]}', False),
        "trailing-json": ('{"prefixes":[{"ipv4Prefix":"192.0.2.129/24"}]}{}', False),
        "invalid-prefix": ('{"prefixes":[{"ipv4Prefix":"192.0.2.1"}]}', False),
        "excessive-nesting": ('{"prefixes":[],"metadata":' + '['*130 + '0' + ']'*130 + '}', False),
        "unicode-metadata": ('{"metadata":"café 🌍","prefixes":[{"ipv6Prefix":"2001:DB8::123/64"}]}', True),
        "top-array": ('[]', False),
        "no-document": ('', False),
        "invalid-escape": (r'{"prefixes":[],"metadata":"\q"}', None),
    }
    for name,(document,success) in documents.items():
        values['searchbot-'+name]=(document.encode(),success)
    values['searchbot-bom']=(b'\xef\xbb\xbf{"prefixes":[]}',True)
    values['searchbot-invalid-utf8']=(b'{"prefixes":[],"metadata":"\xff"}',False)
    values['searchbot-invalid-utf8-tail']=(b'{"prefixes":[]}\xff',False)
    return values

def cases(values):
    text = {k:v for k,v in values.items() if not k.startswith('searchbot-')}
    original = _text_cases(text)
    for name in values:
        if name.startswith('searchbot-'):
            for use_stdin in [False,True]:
                original.append({'id':name+('-stdin' if use_stdin else '-file'), 'fixture':name,
                                 'stdin':use_stdin, 'flags':['--raw','--input-format','searchbot'], 'checksum':False})
    for representation in ['ranges','cidr']:
        for output_format in ['raw','json']:
            for checksum in [False,True]:
                flags=['--input-format','searchbot','--'+output_format,'--representation',representation]
                if checksum:flags+=['--checksum','--output','output.txt']
                original.append({'id':f'searchbot-mixed-{representation}-{output_format}-checksum-{checksum}',
                                 'fixture':'searchbot-mixed','stdin':False,'flags':flags,'checksum':checksum})
    result=[]
    for case in original:
        for stats in [False,True]:
            flags=[x for x in case['flags'] if x!='--stats']
            if stats:flags.append('--stats')
            result.append({**case,'id':case['id']+('-stats' if stats else '-no-stats'),'flags':flags})
    return result


def run_child(binary, case, fixture, directory, environment, timeout):
    directory.mkdir(parents=True)
    command = [str(binary), *case["flags"], "-" if case["stdin"] else str(fixture)]
    timed_out = False
    process = subprocess.Popen(command, cwd=directory, env=environment,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        stdout, stderr = process.communicate(fixture.read_bytes() if case["stdin"] else b"", timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    (directory / "stdout.bin").write_bytes(stdout)
    (directory / "stderr.bin").write_bytes(stderr)
    artifacts = {}
    for name in ["output.txt", "output.txt.sha256"]:
        path = directory / name
        if path.exists():
            artifacts[name] = path.read_bytes()
    record = {
        "command": command, "returncode": process.returncode, "timed_out": timed_out,
        "stdout": {"file": "stdout.bin", "bytes": len(stdout), "sha256": sha256(stdout)},
        "stderr": {"file": "stderr.bin", "bytes": len(stderr), "sha256": sha256(stderr)},
        "output_files": {name: {"bytes": len(data), "sha256": sha256(data)} for name, data in artifacts.items()},
    }
    (directory / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    return record, (process.returncode, timed_out, stdout, stderr, artifacts)


def checksum_valid(payload):
    code, timeout, stdout, _, files = payload
    if code != 0:
        return not files
    if timeout or stdout or set(files) != {"output.txt", "output.txt.sha256"}:
        return False
    expected = (sha256(files["output.txt"]) + "  output.txt\n").encode()
    return files["output.txt.sha256"] == expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--toolchain-bin", type=Path)
    parser.add_argument("--runtime-library-path", type=Path)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    baseline, candidate = args.baseline.resolve(), args.candidate.resolve()
    for binary in [baseline, candidate]:
        if not binary.is_file() or not os.access(binary, os.X_OK):
            parser.error(f"Executable is unavailable: {binary}")
    output = args.output.resolve()
    if output.exists():
        parser.error("Output directory already exists; existing evidence must not be overwritten")
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    environment.update({"LANG": "C", "LC_ALL": "C", "TZ": "UTC"})
    if args.toolchain_bin:
        environment["PATH"] = str(args.toolchain_bin.resolve()) + os.pathsep + environment.get("PATH", "")
    if args.runtime_library_path:
        environment["LD_LIBRARY_PATH"] = str(args.runtime_library_path.resolve())
    summary = {
        "schema_version": 1, "passed": False, "started_at": datetime.now(timezone.utc).isoformat(),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "binaries": {"baseline": {"path": str(baseline), "sha256": file_sha256(baseline)},
                     "candidate": {"path": str(candidate), "sha256": file_sha256(candidate)}},
        "environment": {key: environment.get(key) for key in ["PATH", "LD_LIBRARY_PATH", "LANG", "LC_ALL", "TZ"]},
        "fixture_count": 0, "case_count": 0, "process_count": 0, "fixtures": {}, "cases": [],
    }
    try:
        values = fixtures()
        fixture_dir = output / "fixtures"
        fixture_dir.mkdir()
        for name, (data, expected_success) in values.items():
            path = fixture_dir / (name + ".txt")
            path.write_bytes(data)
            summary["fixtures"][name] = {"file": str(path.relative_to(output)), "bytes": len(data),
                                         "sha256": sha256(data), "expected_success": expected_success}
        summary["fixture_count"] = len(values)
        for case in cases(values):
            name = case["fixture"]
            fixture = fixture_dir / (name + ".txt")
            baseline_record, baseline_payload = run_child(baseline, case, fixture, output / "cases" / case["id"] / "baseline", environment, args.timeout)
            summary["process_count"] += 1
            candidate_record, candidate_payload = run_child(candidate, case, fixture, output / "cases" / case["id"] / "candidate", environment, args.timeout)
            summary["process_count"] += 1
            expected_success = values[name][1]
            contract = expected_success is None or (baseline_payload[0] == 0) == expected_success
            equal = baseline_payload == candidate_payload
            checksum = not case["checksum"] or (checksum_valid(baseline_payload) and checksum_valid(candidate_payload))
            passed = equal and contract and checksum and not baseline_payload[1] and not candidate_payload[1]
            summary["cases"].append({**case, "passed": passed, "exactly_equal": equal,
                                     "baseline_contract_passed": contract, "checksum_verified": checksum,
                                     "baseline": baseline_record, "candidate": candidate_record})
            summary["case_count"] += 1
        summary["binary_hashes_unchanged"] = all(
            file_sha256(Path(record["path"])) == record["sha256"] for record in summary["binaries"].values()
        )
        summary["fixture_hashes_unchanged"] = all(
            file_sha256(output / record["file"]) == record["sha256"] for record in summary["fixtures"].values()
        )
        summary["passed"] = all(case["passed"] for case in summary["cases"]) and summary["binary_hashes_unchanged"] and summary["fixture_hashes_unchanged"]
    except Exception as error:
        summary["error"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in ["passed", "fixture_count", "case_count", "process_count"]}))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
