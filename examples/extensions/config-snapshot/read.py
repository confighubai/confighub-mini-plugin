#!/usr/bin/env python3
"""An extension that reads one pinned configuration revision with cub.

Uses the caller's CUB_CONFIG/CUB_CONTEXT. No owner login or new authentication.
Writes a versioned JSON snapshot; a retry with the same revision is byte-identical.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

CONTRACT = 'confighub.config-snapshot/v1'

def cub(arguments, retries=2):
    for attempt in range(retries + 1):
        result = subprocess.run(['cub', *arguments], capture_output=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        error = result.stderr.decode(errors='replace')
        # Retry only a read that was refused by a transient transport/server
        # fault. Never retry denied access, missing objects or arbitrary errors.
        transient = any(s in error for s in ('HTTP 429', 'HTTP 502', 'HTTP 503', 'connection refused', 'connection reset'))
        if not transient or attempt == retries:
            raise RuntimeError('cub could not read the requested revision; check its scoped key, coordinates and connectivity')
        time.sleep(0.25 * 2 ** attempt)
    raise AssertionError('unreachable')

def snapshot(space, unit, revision=None):
    if revision is None:
        metadata = json.loads(cub(['unit', 'get', unit, '--space', space, '-o', 'json']))
        revision = metadata.get('Unit', metadata).get('HeadRevisionNum')
    if type(revision) is not int or revision < 1:
        raise ValueError('A positive revision is required; no unversioned data is read')
    data = cub(['revision', 'data', unit, str(revision), '--space', space])
    return {'contract': CONTRACT, 'space': space, 'unit': unit, 'revision': revision,
            'sha256': hashlib.sha256(data).hexdigest(), 'content': data.decode('utf-8')}

def write_snapshot(destination, value):
    data = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    path = Path(destination)
    # Existing output is an idempotent retry only if it is already identical.
    # Never replace a symlink or another snapshot silently.
    if path.is_symlink():
        raise ValueError('Output is a symbolic link')
    if path.exists():
        if path.is_file() and path.read_bytes() == data:
            return
        raise ValueError('Output already contains different data; choose a new path')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.snapshot-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        # link creates the destination only when it does not exist. A racing
        # caller cannot overwrite a result after the earlier existence check.
        os.link(temporary, path)
    finally:
        os.unlink(temporary)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--space', required=True)
    parser.add_argument('--unit', required=True)
    parser.add_argument('--revision', type=int, help='pin a known revision; default reads and then pins the listed head')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        value = snapshot(args.space, args.unit, args.revision)
        write_snapshot(args.out, value)
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, str(error) + '\n')
    print(f'{CONTRACT}: {args.space}/{args.unit} revision {value["revision"]} -> {args.out}')

if __name__ == '__main__':
    main()
