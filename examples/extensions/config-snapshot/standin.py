"""A stand-in for cub, and a way to run an add-on against it, for the contract
tests of the reference add-ons. No hub, credential or network.

The stand-in reads its answers from a JSON file named by STANDIN_CUB, appends
each call's arguments to a log, and parses its arguments the way cub does: a
flag it does not know fails, a value given where a flag is expected is read as
that flag, and a command given the wrong number of arguments fails. It answers
-o json with the JSON it holds, and -o jq=EXPR by running jq on it, printing a
string as it is, as cub does.

The program under test is a path. A .sh program runs under TEST_SHELL (sh when
unset), anything else under this Python.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

STANDIN = r'''
import json, os, subprocess, sys
path = os.environ['STANDIN_CUB']
with open(path) as f:
    state = json.load(f)
args = sys.argv[1:]
with open(state['log'], 'a') as f:
    f.write(json.dumps(args) + '\n')
VALUED = {'--space', '-o', '--output', '--context'}
flags, words, i = {}, [], 0
while i < len(args):
    a = args[i]
    if a == '--':
        words += args[i + 1:]
        break
    if a.startswith('-') and a != '-':
        name, eq, value = a.partition('=')
        if name in ('-h', '--help'):
            print('Usage:\n  cub [command]')
            sys.exit(0)
        if name not in VALUED:
            sys.stderr.write('Error: unknown flag: ' + name + '\n')
            sys.exit(1)
        if not eq:
            i += 1
            if i >= len(args):
                sys.stderr.write('Error: flag needs an argument: ' + name + '\n')
                sys.exit(1)
            value = args[i]
        flags[name] = value
    else:
        words.append(a)
    i += 1
command, rest = ' '.join(words[:2]), words[2:]
for entry in state.get('fail', []):
    if entry.get('times', 0) > 0 and entry.get('when', command) == command:
        entry['times'] -= 1
        with open(path, 'w') as f:
            json.dump(state, f)
        sys.stderr.write(entry.get('stderr', 'Error'))
        sys.exit(entry.get('code', 1))
counts = {'space get': 1, 'unit get': 1, 'revision data': 2, 'revision list': 1, 'attestation list': 0}
if command not in counts:
    sys.stderr.write('Error: unknown command\n')
    sys.exit(1)
if len(rest) != counts[command]:
    sys.stderr.write('Error: accepts %d arg(s), received %d\n' % (counts[command], len(rest)))
    sys.exit(1)
if command == 'revision data':
    data = state.get('data', {}).get(rest[1])
    if data is None:
        sys.stderr.write('Error: revision not found\n')
        sys.exit(1)
    sys.stdout.buffer.write(bytes.fromhex(data))
    sys.exit(0)
if command == 'space get':
    value = state.get('space', {'Space': {'Slug': rest[0], 'Annotations': {}}})
elif command == 'unit get':
    value = state.get('unit', {'Unit': {'Slug': rest[0], 'HeadRevisionNum': 7}})
    if 'head_after' in state:
        # The head moves on as soon as it has been read once.
        state['unit'] = {'Unit': {'Slug': rest[0], 'HeadRevisionNum': state.pop('head_after')}}
        with open(path, 'w') as f:
            json.dump(state, f)
elif command == 'revision list':
    value = state.get('revisions', [])
else:
    value = state.get('attestations', [])
output = flags.get('-o', flags.get('--output', ''))
if output == 'json':
    print(json.dumps(value, indent=2))
elif output.startswith('jq='):
    p = subprocess.run(['jq', '-r', output[3:]], input=json.dumps(value).encode(), capture_output=True)
    sys.stdout.buffer.write(p.stdout)
    sys.stderr.buffer.write(p.stderr)
    sys.exit(p.returncode and 1)
else:
    sys.stderr.write('Error: unsupported output\n')
    sys.exit(1)
'''


class World:
    """A temporary folder with the stand-in cub on the PATH."""

    def __init__(self, root, program):
        self.root = Path(root)
        self.program = str(program)
        self.bin = self.root / 'standin-bin'
        self.bin.mkdir(parents=True)
        cub = self.bin / 'cub'
        cub.write_text('#!' + sys.executable + '\n' + STANDIN)
        cub.chmod(0o755)
        self.state_file = self.root / 'standin.json'
        self.log = self.root / 'standin-calls.jsonl'
        self.state = {'log': str(self.log), 'data': {}}
        self.save()

    def save(self):
        self.state_file.write_text(json.dumps(self.state))

    def load(self):
        self.state = json.loads(self.state_file.read_text())
        return self.state

    def set(self, **values):
        self.load().update(values)
        self.save()

    def revision(self, number, content):
        data = content if isinstance(content, bytes) else content.encode()
        self.load()['data'][str(number)] = data.hex()
        self.save()

    def fail(self, when, stderr, times=1):
        self.load().setdefault('fail', []).append({'when': when, 'stderr': stderr, 'times': times})
        self.save()

    def calls(self, command=None):
        if not self.log.exists():
            return []
        rows = [json.loads(line) for line in self.log.read_text().splitlines()]
        if command is None:
            return rows
        words = command.split()
        return [r for r in rows if [a for a in r if not a.startswith('-')][:len(words)] == words]

    def forget_calls(self):
        if self.log.exists():
            self.log.unlink()

    def tool(self, name, script):
        """Puts a program of the test's own before the system's on the PATH."""
        path = self.bin / name
        path.write_text('#!/bin/sh\n' + script)
        path.chmod(0o755)

    def run(self, *args, cwd=None):
        shell = os.environ.get('TEST_SHELL', 'sh')
        command = [shell, self.program] if self.program.endswith('.sh') else [sys.executable, self.program]
        env = {k: v for k, v in os.environ.items() if not k.startswith('CUB_')}
        env.update(PATH=str(self.bin) + os.pathsep + os.environ.get('PATH', ''), STANDIN_CUB=str(self.state_file), TMPDIR=str(self.root))
        return subprocess.run(command + [str(a) for a in args], cwd=cwd or self.root, env=env, capture_output=True, timeout=120)


def needs_jq(program):
    """Why a program cannot be tested here, or None."""
    if str(program).endswith('.sh') and not shutil.which('jq'):
        return 'the stand-in answers -o jq= with jq, which is not installed'
    return None
