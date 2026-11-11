"""The snapshot contract, run against the program itself: the shell version
read.sh and the Python version read.py pass the same tests, with a stand-in cub
on the PATH. READ_PROGRAM=/path/to/program tests that program alone."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import standin  # noqa: E402


class Contract:
    program = None

    def setUp(self):
        why = standin.needs_jq(self.program)
        if why:
            self.skipTest(why)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = standin.World(self.tmp.name, self.program)
        self.world.revision(7, 'PORT=3000\n')
        self.out = self.world.root / 'out' / 'snapshot.json'

    def read(self, *extra, out=None):
        return self.world.run('--space', 'app-live', '--unit', 'app', '--out', out or self.out, *extra)

    def test_head_is_read_once_and_data_is_pinned(self):
        # The head moves to 8 as soon as it is read; revision 7 is what is fetched.
        self.world.revision(8, 'PORT=4000\n')
        self.world.set(head_after=8)
        p = self.read()
        self.assertEqual(p.returncode, 0, p.stderr)
        value = json.loads(self.out.read_text())
        self.assertEqual(value, {'contract': 'confighub.config-snapshot/v1', 'space': 'app-live', 'unit': 'app', 'revision': 7,
                                 'sha256': hashlib.sha256(b'PORT=3000\n').hexdigest(), 'content': 'PORT=3000\n'})
        self.assertEqual(len(self.world.calls('unit get')), 1)
        data = self.world.calls('revision data')
        self.assertEqual(len(data), 1)
        self.assertEqual([a for a in data[0] if not a.startswith('-')][2:4], ['app', '7'])
        self.assertIn(b'revision 7 -> ', p.stdout)

    def test_unknown_revision_never_reads_unversioned_data(self):
        for head in ({}, {'Unit': {}}, {'Unit': {'HeadRevisionNum': 0}}, {'Unit': {'HeadRevisionNum': True}},
                     {'Unit': {'HeadRevisionNum': '7'}}, {'Unit': {'HeadRevisionNum': 7.5}}, {'Unit': {'HeadRevisionNum': -1}}):
            with self.subTest(head=head):
                self.world.forget_calls()
                self.world.set(unit=head)
                p = self.read()
                self.assertNotEqual(p.returncode, 0)
                self.assertEqual(len(self.world.calls('unit get')), 1)
                self.assertEqual(self.world.calls('revision data'), [])
                self.assertFalse(self.out.exists())
        for revision in ('0', '-1', 'True', '7x', ''):
            with self.subTest(revision=revision):
                self.world.forget_calls()
                p = self.read('--revision=' + revision)
                self.assertNotEqual(p.returncode, 0)
                self.assertEqual(self.world.calls(), [])
                self.assertFalse(self.out.exists())
        # A revision the hub does not have fails; the head is not used instead.
        self.world.forget_calls()
        p = self.read('--revision', '99')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.world.calls('unit get'), [])
        self.assertFalse(self.out.exists())

    def test_only_transient_failures_retry_without_exposing_stderr(self):
        self.world.fail('unit get', '403 private-key-material')
        p = self.read()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(b'scoped key', p.stderr)
        self.assertNotIn(b'private-key-material', p.stderr + p.stdout)
        self.assertEqual(len(self.world.calls('unit get')), 1)
        self.world.forget_calls()
        self.world.fail('unit get', 'HTTP 503')
        p = self.read()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(self.world.calls('unit get')), 2)
        # At most two retries.
        self.world.forget_calls()
        self.world.fail('revision data', 'connection reset', times=3)
        p = self.read(out=self.world.root / 'other.json')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(len(self.world.calls('revision data')), 3)

    def test_retry_preserves_output_but_changed_output_and_symlinks_fail(self):
        p = self.read()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.out.stat().st_mode & 0o777, 0o600)
        first = self.out.read_bytes()
        p = self.read('--revision', '7')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.out.read_bytes(), first)
        self.world.revision(8, 'PORT=4000\n')
        p = self.read('--revision', '8')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.out.read_bytes(), first)
        link = self.out.with_name('link.json')
        link.symlink_to(self.out)
        p = self.read(out=link)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.out.read_bytes(), first)
        self.assertTrue(link.is_symlink())
        folder = self.out.with_name('folder.json')
        folder.mkdir()
        self.assertNotEqual(self.read(out=folder).returncode, 0)
        self.assertEqual(list(folder.iterdir()), [])

    def test_racing_writer_is_not_overwritten(self):
        if not self.program.endswith('.sh'):
            self.skipTest("Python's os.link is not a program on the PATH; test_read.py patches it")
        # ln is the step that makes the snapshot; another writer gets there first.
        self.world.tool('ln', 'for last; do :; done\nprintf "other writer" > "$last"\nexec /bin/ln "$@"\n')
        p = self.read()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.out.read_text(), 'other writer')
        self.assertEqual(sorted(p.name for p in self.out.parent.iterdir()), ['snapshot.json'])

    def test_content_that_is_not_utf8_is_refused(self):
        self.world.revision(7, b'PORT=\xff\n')
        p = self.read()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.out.exists())

    def test_hostile_content_and_names_are_written_exactly(self):
        # Quotes, backslashes, $, backticks, control characters, other scripts and
        # no final newline: the snapshot is the same JSON Python's json.dumps writes.
        content = 'A="x y" \'$HOME\' `id` $(id) \\ \t\x01\x7f é 😀\r\nB=1'.encode()
        self.world.revision(7, content)
        out = self.world.root / 'a folder with spaces' / '-snapshot.json'
        p = self.world.run('--space', 'app live "$x"', '--unit=app`id`', '--out=' + str(out))
        self.assertEqual(p.returncode, 0, p.stderr)
        expected = {'content': content.decode(), 'contract': 'confighub.config-snapshot/v1', 'revision': 7,
                    'sha256': hashlib.sha256(content).hexdigest(), 'space': 'app live "$x"', 'unit': 'app`id`'}
        self.assertEqual(out.read_bytes(), (json.dumps(expected, sort_keys=True, indent=2) + '\n').encode())
        calls = self.world.calls('revision data')
        self.assertIn('app`id`', calls[0])
        self.assertIn('app live "$x"', calls[0])

    def test_a_relative_path_that_starts_with_a_dash(self):
        p = self.world.run('--space', 'app-live', '--unit', 'app', '--out=-snapshot.json', cwd=self.world.root)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((self.world.root / '-snapshot.json').is_file())


def programs():
    named = os.environ.get('READ_PROGRAM')
    return {'Program': named} if named else {'Shell': str(HERE / 'read.sh'), 'Python': str(HERE / 'read.py')}


for _name, _path in programs().items():
    globals()[_name] = type(_name, (Contract, unittest.TestCase), {'program': _path})

if __name__ == '__main__':
    unittest.main()
