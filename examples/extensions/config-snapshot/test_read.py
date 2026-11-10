"""Contract boundaries: pinning, access failures and output ownership."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('snapshot_extension', Path(__file__).with_name('read.py'))
extension = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extension)

class ContractTests(unittest.TestCase):
    def test_head_is_read_once_and_data_is_pinned(self):
        calls = []
        def cub(args):
            calls.append(args)
            return b'{"Unit":{"HeadRevisionNum":7}}' if args[1] == 'get' else b'PORT=3000\n'
        with patch.object(extension, 'cub', side_effect=cub):
            value = extension.snapshot('app-live', 'app')
        self.assertEqual(value['revision'], 7)
        self.assertEqual(calls[1], ['revision', 'data', 'app', '7', '--space', 'app-live'])
        self.assertEqual(value['content'], 'PORT=3000\n')

    def test_unknown_revision_never_reads_unversioned_data(self):
        with patch.object(extension, 'cub', return_value=b'{}') as cub:
            with self.assertRaises(ValueError): extension.snapshot('live', 'app')
            self.assertEqual(cub.call_count, 1)
        for revision in (0, -1, True):
            with patch.object(extension, 'cub') as cub:
                with self.assertRaises(ValueError): extension.snapshot('live', 'app', revision)
                cub.assert_not_called()

    def test_only_transient_failures_retry_without_exposing_stderr(self):
        denied = subprocess.CompletedProcess([], 1, b'', b'403 private-key-material')
        with patch.object(extension.subprocess, 'run', return_value=denied) as run:
            with self.assertRaisesRegex(RuntimeError, 'scoped key') as error: extension.cub(['unit', 'get', 'app'])
            self.assertNotIn('private-key-material', str(error.exception))
            self.assertEqual(run.call_count, 1)
        transient = subprocess.CompletedProcess([], 1, b'', b'HTTP 503')
        success = subprocess.CompletedProcess([], 0, b'ok', b'')
        with patch.object(extension.subprocess, 'run', side_effect=[transient, success]) as run, patch.object(extension.time, 'sleep'):
            self.assertEqual(extension.cub(['unit', 'get', 'app']), b'ok')
            self.assertEqual(run.call_count, 2)

    def test_retry_preserves_output_but_changed_output_and_symlinks_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'snapshot.json'
            value = {'contract': extension.CONTRACT, 'revision': 1}
            extension.write_snapshot(path, value)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            first = path.read_bytes()
            extension.write_snapshot(path, value)
            with self.assertRaises(ValueError): extension.write_snapshot(path, dict(value, revision=2))
            self.assertEqual(path.read_bytes(), first)
            link = path.with_name('link.json')
            link.symlink_to(path)
            with self.assertRaises(ValueError): extension.write_snapshot(link, value)
            self.assertEqual(path.read_bytes(), first)

    def test_racing_writer_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'snapshot.json'
            def race(source, destination):
                Path(destination).write_text('other writer')
                raise FileExistsError(destination)
            with patch.object(extension.os, 'link', side_effect=race):
                with self.assertRaises(FileExistsError): extension.write_snapshot(path, {'revision': 1})
            self.assertEqual(path.read_text(), 'other writer')
            self.assertEqual(sorted(p.name for p in path.parent.iterdir()), ['snapshot.json'])

if __name__ == '__main__': unittest.main()
