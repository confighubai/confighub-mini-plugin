#!/usr/bin/env python3
"""Runnable product examples. Each uses isolated hubs and ordinary cub commands."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def run(command, *, env=None, cwd=None, data=None, allow=False):
    result = subprocess.run([str(x) for x in command], input=data, capture_output=True, env=env, cwd=cwd, timeout=180)
    if result.returncode and not allow:
        raise RuntimeError(f'{command[0]} {command[1:3]} failed: {result.stderr.decode(errors="replace")[-1200:]}')
    return result


def cleanup(work, package):
    work = Path(work).resolve()
    marker = work / '.roadmap-example.json'
    if work.parent != Path.home().resolve() or not work.name.startswith('.confighub-roadmap-') or not marker.is_file():
        raise ValueError('Not a workspace created by these examples')
    record = json.loads(marker.read_text())
    env = {k: v for k, v in os.environ.items() if not k.startswith('CUB_')}
    env.update(CUB_CONFIG=str(work / 'config'), PATH=str(package / 'bin') + os.pathsep + env['PATH'], CONFIGHUB_MINI_PACKAGE=str(package))
    for hub in reversed(record['hubs']):
        result = run([package / 'bin/cub', 'mini', 'uninstall', '--name', hub, '--delete-data'], env=env, allow=True)
        if result.returncode and (work / 'config/servers' / hub).exists():
            raise RuntimeError('Could not remove an example hub; workspace retained for inspection')
    shutil.rmtree(work)


class Example:
    def __init__(self, outcome, package, keep=False):
        self.outcome, self.package, self.keep = outcome, package, keep
        self.work = Path(tempfile.mkdtemp(prefix='.confighub-roadmap-', dir=Path.home()))
        self.cfg = self.work / 'config'
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('CUB_')}
        self.env.update(CUB_CONFIG=str(self.cfg), CONFIGHUB_MINI_PACKAGE=str(package),
                        PATH=str(package / 'bin') + os.pathsep + self.env['PATH'], CUB_MINI_TIPS='0')
        self.checks, self.hubs = [], []
        self.write_marker()
        try:
            run([package / 'bin/confighub-mini-app', 'mini', 'install-plugin', self.cfg], env=self.env)
        except BaseException:
            shutil.rmtree(self.work)
            raise

    def write_marker(self):
        (self.work / '.roadmap-example.json').write_text(json.dumps({'hubs': self.hubs, 'package': str(self.package)}))

    def cub(self, *args, context=None, allow=False, data=None, environment=None):
        env = dict(self.env if environment is None else environment)
        if context:
            env['CUB_CONTEXT'] = context
        return run([self.package / 'bin/cub', *args], env=env, cwd=self.work, allow=allow, data=data)

    def hub(self, name):
        self.hubs.append(name)
        self.write_marker()
        self.cub('mini', 'install', '--name', name, '--use')
        context = json.loads(self.cub('context', 'get', '-o', 'json').stdout)['name']
        return context

    def check(self, name, passed):
        self.checks.append({'check': name, 'pass': bool(passed)})
        print(('PASS ' if passed else 'FAIL ') + name, flush=True)
        if not passed:
            raise RuntimeError(name)

    def app(self, name, settings):
        folder = self.work / name
        folder.mkdir()
        (folder / '.env').write_text(settings)
        (folder / 'server.py').write_text('print("This example checks stored configuration; R1 runs the HTTP service.")\n')
        return folder

    def data(self, space, context=None):
        text = self.cub('unit', 'data', 'app', '--space', space, context=context).stdout.decode()
        return dict(line.split('=', 1) for line in text.splitlines() if '=' in line and not line.startswith('configHub.'))

    def approve(self, context, app, order='adopt'):
        self.cub('variant', 'approve', app + '-base', '--change-order', app + '-base/' + order,
                 '--note', 'Scripted example fixture; not human acceptance', context=context)
        self.cub('mini', 'promote', app + '-live', '--change-order', app + '-base/' + order, context=context)

    def finish(self):
        if self.keep:
            print(f'Workspace kept: {self.work}')
            print(f'Inspect with CUB_CONFIG={self.cfg} {self.package / "bin/cub"} mini waiting')
            print(f'Cleanup: python3 {HERE / "run.py"} cleanup {self.work}')
        else:
            cleanup(self.work, self.package)
        self.check('example workspace removed or explicitly kept', self.keep or not self.work.exists())


def r2(ex):
    context = ex.hub('second-use')
    source = ex.app('first', 'PORT=3000\nLOG_LEVEL=info\nREGION=eu\n')
    ex.cub('mini', 'adopt', source, context=context)
    ex.approve(context, 'first')
    ex.cub('mini', 'set', 'first', 'LOG_LEVEL=warn', '--variant', 'base', '--change-desc',
           'Keep logs quiet so operational errors stand out', context=context)
    recipient = ex.app('second', 'PORT=3001\nREGION=us\nAPI_TOKEN=tok-private-recipient-77aa88bb99\n')
    ex.cub('mini', 'adopt', recipient, '--pattern', 'first', context=context)
    ex.approve(context, 'second')
    before = ex.data('second-live', context)
    ex.check('second app keeps its own port and region', before['PORT'] == '3001' and before['REGION'] == 'us')
    ex.check('the inherited log setting has its reason', b'Keep logs quiet' in ex.cub('unit', 'blame', 'app', '--space', 'second-base', '-o', 'json', context=context).stdout)
    ex.cub('mini', 'set', 'first', 'LOG_LEVEL=error', '--variant', 'base', '--change-desc',
           'The next pattern version logs errors only', context=context)
    ex.cub('mini', 'set', 'first', 'PORT=3100', '--variant', 'base', '--change-desc',
           'The default port moved', context=context)
    ex.cub('mini', 'upgrade', 'first-base/app', '--change-desc', 'Take the next shared version', context=context)
    base = ex.data('second-base', context)
    ex.check('upstream update arrives without replacing recipient choices', base['LOG_LEVEL'] == 'error' and base['PORT'] == '3001' and base['REGION'] == 'us')
    ex.check('upstream update does not bypass live approval', ex.data('second-live', context) == before)
    ex.check('the updated inherited value retains its reason', b'The next pattern version' in ex.cub('unit', 'blame', 'app', '--space', 'second-base', '-o', 'json', context=context).stdout)
    ex.cub('changeorder', 'create', 'pattern-update', '--space', 'second-base', '--in-scope-space', 'second-live',
           '--change-workflow', 'workflows/second-live-approval', '--description', 'Take the new pattern, keeping this app values', context=context)
    ex.check('new pattern revision waits for its own approval', ex.cub('mini', 'promote', 'second-live', '--change-order', 'second-base/pattern-update', context=context, allow=True).returncode != 0 and ex.data('second-live', context) == before)
    ex.approve(context, 'second', 'pattern-update')
    after = ex.data('second-live', context)
    ex.check('approved pattern reaches live with recipient values kept', after['LOG_LEVEL'] == 'error' and after['PORT'] == '3001' and after['REGION'] == 'us')
    export = ex.work / 'shared.tgz'
    ex.cub('mini', 'copy', 'second', '--to-file', export, context=context)
    with tarfile.open(export) as bundle:
        payloads = [bundle.extractfile(member).read() for member in bundle if member.isfile()]
    ex.check('shared setup contains no recipient credential', all(b'tok-private-recipient-77aa88bb99' not in p and b'PRIVATE KEY' not in p for p in payloads))
    ex.check('recipient credential stays in its local file', 'tok-private-recipient-77aa88bb99' in (recipient / '.env').read_text())
    print('R2 checks configuration reuse. It does not claim an unaided recipient or generated Kubernetes manifests.')


def r3(ex):
    source = ex.hub('source')
    folder = ex.app('notes', 'PORT=3000\nLOG_LEVEL=info\n')
    ex.cub('mini', 'adopt', folder, context=source)
    ex.approve(source, 'notes')
    ex.cub('mini', 'set', 'notes', 'PORT=3001', '--variant', 'live', '--change-desc',
           'This runtime uses its own port', context=source)
    original = ex.data('notes-live', source)
    destination = ex.hub('destination')
    ex.cub('mini', 'copy', 'notes', '--from-context', source, context=destination)
    ex.check('destination retains the app values', ex.data('notes-live', destination) == original)
    blame = ex.cub('unit', 'blame', 'app', '--space', 'notes-live', '-o', 'json', context=destination).stdout
    ex.check('destination retains the kept value and reason', b'This runtime uses its own port' in blame and any(f.get('Path') == 'PORT' and f.get('Protected') is True for f in json.loads(blame)))
    linked = ex.cub('mini', 'connect', '--to-context', destination, context=source).stdout.decode()
    match = re.search(r'as the context (\S+?)[;,]', linked)
    if not match:
        raise RuntimeError('connect did not return its scoped parent context')
    parent = match.group(1)
    ex.cub('mini', 'set', 'notes', 'LOG_LEVEL=warn', '--variant', 'base', '--change-desc',
           'Shared hub reduces log noise', context=destination)
    ex.cub('mini', 'copy', 'notes', '--from-context', parent, '--yes', context=source)
    ex.check('taking a parent update preserves local choices', ex.data('notes-live', source)['PORT'] == '3001')
    plain = ex.work / 'plain-files'
    ex.cub('mini', 'copy', 'notes', '--variant', 'live', '--to-dir', plain, context=destination)
    files = list(plain.rglob('*.env'))
    changes = list(plain.rglob('CHANGES.md'))
    ex.check('return to plain files contains the kept value', any('PORT=3001' in f.read_text() for f in files))
    ex.check('plain-file return includes the reason', bool(changes) and any('This runtime uses its own port' in f.read_text() for f in changes))
    ex.check('copying did not import an owner key', not list(plain.rglob('*.jwk')))
    print('R3 uses two local hubs with one owner. It does not demonstrate cloud signup, two human users, or full history/cost replay.')


def r4(ex):
    context = ex.hub('extension')
    folder = ex.app('notes', 'PORT=3000\nLOG_LEVEL=info\n')
    ex.cub('mini', 'adopt', folder, context=context)
    ex.approve(context, 'notes')
    ex.cub('mini', 'pull-key', 'extension-reader', 'notes', '--variant', 'live', context=context)
    key = ex.cfg / 'keys/extension-reader.jwk'
    reader_cfg = ex.work / 'reader'
    env = dict(ex.env, CUB_CONFIG=str(reader_cfg))
    run([ex.package / 'bin/confighub-mini-app', 'mini', 'install-plugin', reader_cfg], env=env)
    server = json.loads(ex.cub('context', 'get', context, '-o', 'json').stdout)['coordinate']['serverURL']
    run([ex.package / 'bin/cub', 'auth', 'login', '--new-context', '--private-key=' + str(key), '--server', server], env=env)
    extension = ROOT / 'extensions/config-snapshot/read.py'
    output = ex.work / 'snapshot.json'
    command = [sys.executable, extension, '--space', 'notes-live', '--unit', 'app', '--out', output]
    run(command, env=env)
    first = output.read_bytes()
    value = json.loads(first)
    ex.check('extension reads a pinned revision with the v1 contract', value['contract'] == 'confighub.config-snapshot/v1' and value['revision'] > 0 and value['sha256'] == hashlib.sha256(value['content'].encode()).hexdigest())
    run(command + ['--revision', str(value['revision'])], env=env)
    ex.check('retrying the same revision is idempotent', output.read_bytes() == first)
    denied = ex.cub('unit', 'data', 'app', '--space', 'notes-base', allow=True, environment=env)
    ex.check('extension cannot read outside its assigned variant', denied.returncode != 0)
    denied = ex.cub('function', 'set', '--space', 'notes-live', '--unit', 'app', '--toolchain', 'AppConfig/Env', '--change-desc', 'Extension must not write', '--', 'set-string-path', '*', 'PORT', '9999', allow=True, environment=env)
    ex.check('extension cannot write its input', denied.returncode != 0 and ex.data('notes-live', context)['PORT'] == '3000')
    denied = ex.cub('variant', 'approve', 'notes-base', '--change-order', 'notes-base/adopt', '--note', 'Extension must not approve', allow=True, environment=env)
    ex.check('extension cannot approve', denied.returncode != 0)
    ex.check('snapshot contains no credentials or machine paths', b'PRIVATE KEY' not in first and str(ex.cfg).encode() not in first and key.read_bytes() not in first)
    print('R4 is a read-only extension using existing cub authentication. It is not agent delegation or a new SDK.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outcome', choices=['r1', 'r2', 'r3', 'r4', 'cleanup'])
    parser.add_argument('workspace', nargs='?', type=Path, help='only for cleanup')
    parser.add_argument('--package', type=Path, default=os.environ.get('CONFIGHUB_MINI_PACKAGE'))
    parser.add_argument('--linux-package', type=Path, default=os.environ.get('VM_SERVICE_LINUX_PACKAGE'))
    parser.add_argument('--vm', default='sam-vm')
    parser.add_argument('--scripted', action='store_true', help='R1 test with scripted approvals instead of a real terminal prompt')
    parser.add_argument('--keep', action='store_true', help='retain R2–R4 workspaces for inspection')
    parser.add_argument('--out', type=Path, help='new result JSON file; kept outside the example workspace')
    args = parser.parse_args()
    if args.out and args.out.exists():
        parser.error('--out must name a new file')
    if args.outcome == 'cleanup':
        if not args.workspace:
            parser.error('cleanup needs the printed workspace path')
        marker = json.loads((args.workspace / '.roadmap-example.json').read_text())
        cleanup(args.workspace, Path(marker['package']))
        return
    if not args.package or not (args.package / 'bin/confighub-mini-app').is_file():
        parser.error('Set CONFIGHUB_MINI_PACKAGE or --package to an unpacked mini package; see README.md')
    package = args.package.resolve()
    if args.outcome == 'r1':
        if not args.scripted and not sys.stdin.isatty():
            parser.error('R1 needs your terminal for approval; --scripted explicitly selects a test')
        if not args.linux_package:
            parser.error('R1 needs --linux-package for the existing Linux VM')
        env = dict(os.environ, CONFIGHUB_MINI_PACKAGE=str(package), VM_SERVICE_LINUX_PACKAGE=str(args.linux_package.resolve()), VM_SERVICE_MACHINE=args.vm)
        if args.keep:
            parser.error('--keep is supported for R2–R4 only')
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            env['VM_SERVICE_RESULT'] = str(args.out.resolve())
        command = [sys.executable, ROOT / 'vm-service/run'] + ([] if args.scripted else ['--interactive'])
        raise SystemExit(subprocess.run(command, env=env).returncode)
    ex = Example(args.outcome, package, args.keep)
    complete = False
    try:
        {'r2': r2, 'r3': r3, 'r4': r4}[args.outcome](ex)
        complete = True
    finally:
        try:
            ex.finish()
        except Exception:
            complete = False
            ex.checks.append({'check': 'cleanup succeeded', 'pass': False})
            raise
        finally:
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(json.dumps({'outcome': args.outcome, 'complete': complete,
                    'approval': 'scripted fixture; no human acceptance claimed', 'checks': ex.checks,
                    'passed': sum(c['pass'] for c in ex.checks), 'failed': sum(not c['pass'] for c in ex.checks)}, indent=2) + '\n')
    if not complete:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
