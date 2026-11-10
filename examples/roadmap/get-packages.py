#!/usr/bin/env python3
"""Download pinned mini packages, verify SHA-256, and write shell environment paths."""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

VERSION = '0.10.7-mini.17'
BASE = 'https://github.com/confighubai/confighub-mini-plugin/releases/download/mini-v' + VERSION


def download(name, directory, digest=None):
    path = directory / name
    if path.exists() and digest and hashlib.sha256(path.read_bytes()).hexdigest() == digest:
        return path
    fd, temporary = tempfile.mkstemp(prefix='.download-', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as output, urllib.request.urlopen(BASE + '/' + name, timeout=60) as response:
            shutil.copyfileobj(response, output)
        if digest and hashlib.sha256(Path(temporary).read_bytes()).hexdigest() != digest:
            raise ValueError('Checksum mismatch for ' + name)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vm', help='also fetch the Linux architecture of this existing OrbStack machine')
    parser.add_argument('--cache', type=Path, default=Path.home() / '.cache/confighub-examples')
    parser.add_argument('--env', type=Path, default=Path('.confighub-example-env'), help='new shell file containing only the package paths')
    args = parser.parse_args()
    if args.env.exists():
        parser.error('The environment output already exists; choose another --env path')
    if not hasattr(tarfile, 'data_filter'):
        parser.error('Safe archive extraction needs Python 3.12+ (or a Python with tarfile.data_filter)')
    system = platform.system().lower()
    arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'amd64', 'amd64': 'amd64'}.get(platform.machine())
    if system not in ('darwin', 'linux') or not arch:
        parser.error('Only macOS/Linux ARM64 and AMD64 packages are available')
    targets = [('CONFIGHUB_MINI_PACKAGE', system + '-' + arch)]
    if args.vm:
        if system != 'darwin':
            parser.error('--vm uses OrbStack on macOS; a Linux host needs only its own package')
        vm_arch = subprocess.check_output(['orb', '-m', args.vm, 'uname', '-m'], text=True).strip()
        vm_arch = {'aarch64': 'arm64', 'x86_64': 'amd64'}.get(vm_arch)
        if not vm_arch:
            parser.error('Unsupported Linux VM architecture')
        targets.append(('VM_SERVICE_LINUX_PACKAGE', 'linux-' + vm_arch))
    directory = (args.cache / VERSION).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    sums = dict(line.split()[::-1] for line in download('SHA256SUMS', directory).read_text().splitlines())
    assignments = []
    for variable, target in targets:
        name = 'confighub-mini-' + VERSION + '-' + target
        archive = download(name + '.tar.xz', directory, sums[name + '.tar.xz'])
        package = directory / name
        if not package.exists():
            unpack = Path(tempfile.mkdtemp(prefix='.unpack-', dir=directory))
            try:
                with tarfile.open(archive) as bundle:
                    # data_filter rejects escaping links, special files and
                    # paths outside the temporary extraction directory.
                    if any(m.name.split('/')[0] != name for m in bundle):
                        raise ValueError('Unexpected package root')
                    bundle.extractall(unpack, filter='data')
                os.rename(unpack / name, package)
            finally:
                shutil.rmtree(unpack)
        assignments.append('export ' + variable + '=' + shlex.quote(str(package)))
        print('Verified package: ' + name)
    args.env.parent.mkdir(parents=True, exist_ok=True)
    # The file is never sourced here. It contains quoted paths, no credentials.
    with args.env.open('x') as output:
        output.write('\n'.join(assignments) + '\n')
    print('Load the package paths with: . ' + shlex.quote(str(args.env.resolve())))


if __name__ == '__main__':
    main()
