#!/usr/bin/env python3
"""A delivery add-on against a directory stand-in, not a real provider.

The owner gates the copy being read. A snapshot itself does not certify approval.
Only a scoped reader is needed; no operation proposes or approves a change.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import tempfile

spec = importlib.util.spec_from_file_location('snapshot_reader', Path(__file__).resolve().parent.parent / 'config-snapshot/read.py')
snapshot_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot_reader)
SECRET = re.compile(r'(?:^|_)(?:SECRET|PASSWORD|PASSWD|TOKEN|KEY|CREDENTIAL)(?:_|$)', re.I)
NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
REFERENCE = re.compile(r'^secret://[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+$')
CREDENTIAL = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{20,}|://[^/\s]+:[^/\s]+@|-----BEGIN .*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.)')


def settings(snapshot):
    content = snapshot.get('content')
    if (snapshot.get('contract') != snapshot_reader.CONTRACT or not isinstance(content, str)
            or type(snapshot.get('revision')) is not int or snapshot['revision'] < 1
            or hashlib.sha256(content.encode()).hexdigest() != snapshot.get('sha256')):
        raise ValueError('Invalid snapshot contract, revision or content hash')
    values = {}
    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, equal, value = line.partition('=')
        key = key.strip()
        # Same marker omitted by cub mini pull and native render-configmap.
        # It identifies the config to the hub, not a provider environment key.
        if key.startswith('configHub.'):
            continue
        if not equal or not NAME.fullmatch(key) or key in values:
            raise ValueError('Expected unique environment setting names')
        words = shlex.split(value, comments=True, posix=True)
        if len(words) > 1:
            raise ValueError('A setting with spaces must be quoted')
        value = words[0] if words else ''
        if value.startswith('secret://'):
            if not REFERENCE.fullmatch(value):
                raise ValueError('Invalid secret reference')
            values[key] = {'secret_ref': value}
        elif SECRET.search(key) or CREDENTIAL.search(value):
            raise ValueError('Sensitive setting requires a secret reference; no value was recorded')
        else:
            values[key] = value
    return values


def output_path(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Output is a symbolic link')
    if path.exists() and not path.is_file():
        raise ValueError('Output is not a regular file')
    return path


def private_write(path, data, replace=False):
    path = output_path(path)
    if not replace and path.exists():
        if path.read_bytes() == data:
            if path.stat().st_mode & 0o777 != 0o600:
                raise ValueError('Existing output is not private; set mode 0600 before retrying')
            return
        raise ValueError('Output contains different data; choose another folder')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.delivery-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        if replace:
            output_path(path)
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class DirectoryProvider:
    name = 'directory-stand-in'

    def __init__(self, root):
        self.root = Path(root)

    def path(self, target):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', target):
            raise ValueError('Invalid provider target')
        return self.root / (target + '.json')

    def read(self, target):
        path = output_path(self.path(target))
        return json.loads(path.read_text()) if path.exists() else {}

    def write(self, target, values):
        private_write(self.path(target), (json.dumps(values, sort_keys=True, indent=2) + '\n').encode(), replace=True)


def differences(expected, actual):
    result = []
    for key in sorted(set(expected) | set(actual)):
        if isinstance(expected.get(key), dict) and 'secret_ref' in expected[key]:
            if key not in actual:
                result.append(key)
        elif expected.get(key) != actual.get(key):
            result.append(key)
    return result


def import_settings(provider, folder, staging='staging', live='production'):
    outputs = []
    for target, filename in [(staging, '.env.staging'), (live, '.env.production')]:
        values = provider.read(target)
        lines = []
        for key, value in sorted(values.items()):
            if not NAME.fullmatch(key):
                raise ValueError('Provider has an unsupported setting name')
            if isinstance(value, dict):
                value = value.get('secret_ref', '')
                if not REFERENCE.fullmatch(value):
                    raise ValueError('Secret reference unavailable; import refused')
            elif SECRET.search(key) or isinstance(value, str) and CREDENTIAL.search(value):
                raise ValueError('Provider returned a sensitive value; import refused')
            if not isinstance(value, str) or '\n' in value or '\r' in value:
                raise ValueError('Provider returned an unsupported setting')
            lines.append(key + '=' + shlex.quote(value))
        outputs.append((Path(folder) / filename, ('\n'.join(lines) + '\n').encode()))
    # Validate both destinations before writing either environment.
    for path, data in outputs:
        output_path(path)
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Output contains different data; choose another folder')
    for path, data in outputs:
        private_write(path, data)


def apply(provider, target, space, unit, receipt, revision=None):
    # Refuse an invalid receipt destination before making a provider change.
    output_path(receipt)
    snapshot = snapshot_reader.snapshot(space, unit, revision)
    desired = settings(snapshot)
    current = provider.read(target)
    changed = desired != current or bool(getattr(provider, 'needs_retry', lambda target: False)(target))
    if changed:
        provider.write(target, desired)
    record = dict(contract='confighub.delivery-receipt/v1', provider=provider.name, target=target,
                  space=space, unit=unit, revision=snapshot['revision'], sha256=snapshot['sha256'],
                  result='applied' if changed else 'unchanged')
    private_write(receipt, (json.dumps(record, sort_keys=True, indent=2) + '\n').encode(), replace=True)
    return record


def main(provider_factory=None, configure_parser=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['import', 'apply', 'compare'])
    parser.add_argument('--provider-root', type=Path, required=True)
    parser.add_argument('--dir', type=Path)
    parser.add_argument('--staging', default='staging')
    parser.add_argument('--live', default='production')
    parser.add_argument('--target')
    parser.add_argument('--space')
    parser.add_argument('--unit', default='app')
    parser.add_argument('--revision', type=int)
    parser.add_argument('--receipt', type=Path)
    if configure_parser:
        configure_parser(parser)
    args = parser.parse_args()
    try:
        provider = provider_factory(args) if provider_factory else DirectoryProvider(args.provider_root)
        if args.command == 'import':
            if not args.dir:
                parser.error('import requires --dir')
            import_settings(provider, args.dir, args.staging, args.live)
            print('Imported environment files; owner can now run cub mini adopt.')
        else:
            if not args.space or not args.target:
                parser.error('apply and compare require --space and --target')
            if args.command == 'apply':
                if not args.receipt:
                    parser.error('apply requires --receipt')
                print(json.dumps(apply(provider, args.target, args.space, args.unit, args.receipt, args.revision)))
            else:
                expected = settings(snapshot_reader.snapshot(args.space, args.unit, args.revision))
                # A provider with a read-back of its own is compared through it.
                changed = differences(expected, getattr(provider, 'read_back', provider.read)(args.target))
                print(json.dumps({'different_settings': changed, 'secret_comparison': 'presence only'}))
                return int(bool(changed))
    except Exception:
        # Provider output may contain credentials; never repeat it in an error.
        parser.exit(1, 'Delivery operation failed; check the scoped reader, target and private local files.\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
