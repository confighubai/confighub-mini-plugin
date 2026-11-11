"""The delivery add-on contract, run against the program itself, delivery.sh,
with a stand-in cub on the PATH and a directory as the provider.
DELIVERY_PROGRAM=/path/to/program tests another program with the same three
commands.

Python's standard library only; the stand-in answers cub's -o jq= with jq."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'config-snapshot'))
import standin  # noqa: E402

FAILED = b'Delivery operation failed; check the scoped reader, target and private local files.\n'
CREDENTIALS = ('ghp_' + 'a' * 36, 'AKIA' + 'A' * 16, 'https://user:password@example.invalid', 'sk-' + 'a' * 48)

# Settings written to break the reading of a value, each with the settings it
# gives, read the way Python's shlex.split(value, comments=True) reads a value,
# or None where it is refused.
HOSTILE_VALUES = [
    ('A="hello world"', {'A': 'hello world'}),
    ("A='hello world'", {'A': 'hello world'}),
    ('A="it\'s"', {'A': "it's"}),
    ('A=\'say "hi"\'', {'A': 'say "hi"'}),
    ('A=$HOME', {'A': '$HOME'}),
    ("A='$HOME'", {'A': '$HOME'}),
    ('A="$HOME"', {'A': '$HOME'}),
    ('A=`id`', {'A': '`id`'}),
    ('A=$(id)', {'A': '$(id)'}),
    ('A="a\\$b"', {'A': 'a\\$b'}),
    ('A="a\\"b"', {'A': 'a"b'}),
    ('A=a\\ b', {'A': 'a b'}),
    ('A=\\#x', {'A': '#x'}),
    ('A=a#comment', {'A': 'a'}),
    ('A= # nothing', {'A': ''}),
    ('A=B=C', {'A': 'B=C'}),
    ('A=--flag', {'A': '--flag'}),
    ('A=-1', {'A': '-1'}),
    ("A=''", {'A': ''}),
    ('A=""', {'A': ''}),
    ("A=''x", {'A': 'x'}),
    ('A="tab\there"', {'A': 'tab\there'}),
    ('A=é😀', {'A': 'é😀'}),
    ('A="%s%n"', {'A': '%s%n'}),
    ('A=\\\\', {'A': '\\'}),
    ('A=*', {'A': '*'}),
    ('A="a;b|c&d>e"', {'A': 'a;b|c&d>e'}),
    ("A='a\\nb'", {'A': 'a\\nb'}),
    ('A="multi', None),
    ('A="line\nB=x"', None),
    ('A=x\\', None),
    ('A=a b', None),
    ('  A = 1  ', {'A': '1'}),
    ('A=1\r\nB=2', {'A': '1', 'B': '2'}),
    ('A=1\x0bB=2', {'A': '1', 'B': '2'}),
    ('A=1\u2028B=2', {'A': '1', 'B': '2'}),
    ('A\x1f=1', {'A': '1'}),
    ('configHub.name=x\nA=1', {'A': '1'}),
    ('A=1 # trailing', {'A': '1'}),
    ('API_KEY=plain', None),
    ('api_token=secret://vault/a', {'api_token': {'secret_ref': 'secret://vault/a'}}),
    ('A=secret://vault', None),
    ('A=secret://v/x y', None),
    ('A="ghp_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"', None),
    ('A=x-----BEGIN RSA PRIVATE KEY-----', None),
    ('A=eyJabc.eyJdef.', None),
    ('A=postgres://u:p@h/db', None),
]


class Contract:
    program = None

    def setUp(self):
        why = standin.needs_jq(self.program)
        if why:
            self.skipTest(why)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.world = standin.World(self.tmp.name, self.program)
        self.root = self.world.root
        self.provider = self.root / 'provider'
        self.receipt = self.root / 'private' / 'receipt.json'
        self.world.revision(7, 'LIMIT=120\n')

    # What the add-on is run with.
    def apply(self, *extra, provider=None, receipt=None, target='production'):
        return self.world.run('apply', '--provider-root', provider or self.provider, '--target', target,
                              '--space', 'api-live', '--unit', 'app', '--receipt', receipt or self.receipt, *extra)

    def compare(self, *extra, provider=None):
        return self.world.run('compare', '--provider-root', provider or self.provider, '--target', 'production',
                              '--space', 'api-live', '--unit', 'app', *extra)

    def do_import(self, folder, *extra, provider=None):
        return self.world.run('import', '--provider-root', provider or self.provider, '--dir', folder, *extra)

    def content(self, text, revision=7):
        self.world.revision(revision, text)
        self.world.set(unit={'Unit': {'HeadRevisionNum': revision}})

    # The provider stand-in's files, as the reference writes them.
    def provider_file(self, target='production', provider=None):
        return (provider or self.provider) / (target + '.json')

    def write_provider(self, values, target='production', provider=None):
        path = self.provider_file(target, provider)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(values, sort_keys=True, indent=2) + '\n')
        return path

    def read_provider(self, target='production', provider=None):
        return json.loads(self.provider_file(target, provider).read_text())

    def assertNoChange(self, p, provider_was=None):
        self.assertNotEqual(p.returncode, 0)
        if provider_was is None:
            self.assertFalse(self.provider_file().exists())
        else:
            self.assertEqual(self.provider_file().read_bytes(), provider_was)
        self.assertFalse(self.receipt.exists())

    def test_pinned_revision_applied_and_retry_makes_no_change(self):
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        first = json.loads(p.stdout)
        self.assertEqual(self.read_provider(), {'LIMIT': '120'})
        self.assertEqual(self.provider_file().stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.receipt.stat().st_mode & 0o777, 0o600)
        written = self.provider_file().stat()
        self.assertEqual([len(self.world.calls(c)) for c in ('unit get', 'revision data')], [1, 1])
        self.world.forget_calls()
        p = self.apply('--revision', '7')
        self.assertEqual(p.returncode, 0, p.stderr)
        second = json.loads(p.stdout)
        self.assertEqual((first['result'], second['result']), ('applied', 'unchanged'))
        # No provider write: the same file, untouched.
        after = self.provider_file().stat()
        self.assertEqual((after.st_ino, after.st_mtime_ns), (written.st_ino, written.st_mtime_ns))
        self.assertEqual(self.world.calls('unit get'), [])
        self.assertEqual(json.loads(self.receipt.read_text()), dict(
            contract='confighub.delivery-receipt/v1', provider='directory-stand-in', target='production', space='api-live',
            unit='app', revision=7, sha256=hashlib.sha256(b'LIMIT=120\n').hexdigest(), result='unchanged'))
        self.assertEqual(second, json.loads(self.receipt.read_text()))
        # A named revision is the one applied, whatever the head is.
        self.world.revision(6, 'LIMIT=60\n')
        p = self.apply('--revision', '6')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((json.loads(p.stdout)['revision'], self.read_provider()), (6, {'LIMIT': '60'}))

    def test_wrong_key_or_unknown_revision_never_writes(self):
        for name, setup, extra in (('wrong key', lambda: self.world.fail('revision data', 'Error: HTTP 403 forbidden'), ()),
                                   ('wrong key at the head', lambda: self.world.fail('unit get', 'Error: HTTP 401'), ()),
                                   ('unknown revision', lambda: None, ('--revision', '99'))):
            with self.subTest(name=name):
                setup()
                p = self.apply(*extra)
                self.assertNoChange(p)
                self.assertEqual(p.stderr, FAILED)

    def test_racing_head_update_does_not_change_the_pinned_read(self):
        self.world.revision(8, 'LIMIT=999\n')
        self.world.set(head_after=8)
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(self.world.calls('unit get')), 1)
        self.assertEqual([[a for a in c if not a.startswith('-')][3] for c in self.world.calls('revision data')], ['7'])
        self.assertEqual(json.loads(self.receipt.read_text())['revision'], 7)
        self.assertEqual(self.read_provider(), {'LIMIT': '120'})

    def test_transient_read_retries_but_denied_read_does_not(self):
        self.world.fail('unit get', 'Error: HTTP 503')
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(self.world.calls('unit get')), 2)
        self.world.forget_calls()
        self.world.fail('revision data', '403 credential-that-must-stay-private')
        p = self.apply('--revision', '7', receipt=self.root / 'second.json')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(len(self.world.calls('revision data')), 1)
        self.assertNotIn(b'credential-that-must-stay-private', p.stdout + p.stderr)
        self.assertEqual(p.stderr, FAILED)
        self.assertFalse((self.root / 'second.json').exists())

    def test_atomic_files_leave_no_temporary_files_after_failure(self):
        if not self.program.endswith('.sh'):
            self.skipTest('the racing writer is planted as ln on the PATH, which only the shell version runs')
        # ln makes each imported file; another writer gets there first.
        self.write_provider({'LIMIT': '60'}, 'staging')
        self.world.tool('ln', 'for last; do :; done\nprintf "racing writer" > "$last"\nexec /bin/ln "$@"\n')
        folder = self.root / 'app'
        p = self.do_import(folder)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(sorted(f.name for f in folder.iterdir()), ['.env.staging'])
        self.assertEqual((folder / '.env.staging').read_text(), 'racing writer')

    def test_secret_is_reference_only_and_compared_by_presence(self):
        self.content('LIMIT=120\nAPI_TOKEN=secret://vault/project/token\n')
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.read_provider()['API_TOKEN'], {'secret_ref': 'secret://vault/project/token'})
        self.write_provider({'LIMIT': '120', 'API_TOKEN': {'secret_ref': 'secret://another/token'}})
        p = self.compare()
        self.assertEqual((p.returncode, json.loads(p.stdout)['different_settings']), (0, []))
        self.write_provider({'LIMIT': '120'})
        p = self.compare()
        self.assertEqual((p.returncode, json.loads(p.stdout)['different_settings']), (1, ['API_TOKEN']))
        self.provider_file().unlink()
        self.receipt.unlink()
        self.content('API_TOKEN=never-record-this-value\n', revision=8)
        p = self.apply()
        self.assertNoChange(p)
        self.assertNotIn(b'never-record-this-value', p.stdout + p.stderr)

    def test_import_is_private_idempotent_and_never_overwrites(self):
        self.write_provider({'LIMIT': '60'}, 'preview')
        self.write_provider({'LIMIT': '120', 'API_TOKEN': {'secret_ref': 'secret://vault/token'}})
        folder = self.root / 'import'
        for _ in range(2):
            p = self.do_import(folder, '--staging', 'preview', '--live', 'production')
            self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn(b'cub mini adopt', p.stdout)
        staging, production = folder / '.env.staging', folder / '.env.production'
        self.assertEqual(production.stat().st_mode & 0o777, 0o600)
        self.assertEqual(staging.stat().st_mode & 0o777, 0o600)
        self.assertEqual(production.read_text(), 'API_TOKEN=secret://vault/token\nLIMIT=120\n')
        self.assertEqual(staging.read_text(), 'LIMIT=60\n')
        production.write_text('LIMIT=other\n')
        staging.unlink()
        p = self.do_import(folder, '--staging', 'preview', '--live', 'production')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(production.read_text(), 'LIMIT=other\n')
        # Neither file is written when one of them cannot be.
        self.assertFalse(staging.exists())
        link = self.root / 'link-app'
        link.mkdir()
        (link / '.env.production').symlink_to(production)
        p = self.do_import(link, '--staging', 'preview', '--live', 'production')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(production.read_text(), 'LIMIT=other\n')

    def test_identical_existing_import_must_also_be_private(self):
        self.write_provider({'LIMIT': '120'})
        folder = self.root / 'import'
        self.assertEqual(self.do_import(folder).returncode, 0)
        (folder / '.env.production').chmod(0o644)
        p = self.do_import(folder)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual((folder / '.env.production').stat().st_mode & 0o777, 0o644)

    def test_invalid_snapshot_is_refused(self):
        # A head that is not a positive whole number, or content that is not
        # UTF-8, is refused before the provider is touched.
        for head in (True, 0, -1, '7', 7.5, None):
            with self.subTest(head=head):
                self.world.forget_calls()
                self.world.set(unit={'Unit': {'HeadRevisionNum': head}})
                self.assertNoChange(self.apply())
                self.assertEqual(self.world.calls('revision data'), [])
        for revision in ('0', '-1', 'seven', ''):
            with self.subTest(revision=revision):
                self.world.forget_calls()
                self.assertNoChange(self.apply('--revision=' + revision))
                self.assertEqual(self.world.calls('revision data') + self.world.calls('unit get'), [])
        self.content(b'LIMIT=\xff\n')
        self.assertNoChange(self.apply())

    def test_compare_detects_dashboard_change_without_values(self):
        self.assertEqual(self.apply().returncode, 0)
        self.write_provider({'LIMIT': '999'})
        p = self.compare()
        self.assertEqual((p.returncode, json.loads(p.stdout)), (1, {'different_settings': ['LIMIT'], 'secret_comparison': 'presence only'}))
        self.assertNotIn(b'999', p.stdout + p.stderr)
        self.write_provider({'LIMIT': '120', 'EXTRA': 'private'})
        p = self.compare()
        self.assertEqual((p.returncode, json.loads(p.stdout)['different_settings']), (1, ['EXTRA']))
        self.assertNotIn(b'private', p.stdout + p.stderr)
        self.write_provider({'LIMIT': '120'})
        p = self.compare()
        self.assertEqual((p.returncode, p.stdout), (0, b'{"different_settings": [], "secret_comparison": "presence only"}\n'))

    def test_apply_repairs_a_provider_side_edit(self):
        self.assertEqual(self.apply().returncode, 0)
        self.write_provider({'LIMIT': '999'})
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((json.loads(p.stdout)['result'], self.read_provider()), ('applied', {'LIMIT': '120'}))

    def test_hub_marker_is_not_an_application_setting(self):
        self.content('LIMIT=120\nconfigHub.configName=app\n')
        self.assertEqual(self.apply().returncode, 0)
        self.assertEqual(self.read_provider(), {'LIMIT': '120'})

    def test_credential_shaped_values_are_refused_even_with_an_ordinary_name(self):
        for number, value in enumerate(CREDENTIALS, 10):
            with self.subTest(value_type=value[:4]):
                self.content('SETTING=' + value + '\n', revision=number)
                p = self.apply()
                self.assertNoChange(p)
                self.assertNotIn(value.encode(), p.stdout + p.stderr)
                self.write_provider({'SETTING': value})
                folder = self.root / ('import-%d' % number)
                p = self.do_import(folder)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse((folder / '.env.production').exists())
                self.assertNotIn(value.encode(), p.stdout + p.stderr)
                self.provider_file().unlink()

    def test_output_symlinks_and_target_traversal_are_refused(self):
        elsewhere = self.root / 'elsewhere'
        elsewhere.write_text('keep')
        self.receipt.parent.mkdir()
        self.receipt.symlink_to(elsewhere)
        p = self.apply()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.provider_file().exists())
        self.assertEqual(elsewhere.read_text(), 'keep')
        self.assertTrue(self.receipt.is_symlink())
        for target in ('../elsewhere', '.hidden', 'a/b', '', '-x', 'a b'):
            with self.subTest(target=target):
                p = self.apply(receipt=self.root / 'r.json', target=target)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse((self.root / 'r.json').exists())
        self.assertEqual(elsewhere.read_text(), 'keep')

    def test_failed_provider_apply_has_no_success_receipt_and_retry_recovers(self):
        self.provider.mkdir()
        self.provider.chmod(0o500)
        self.addCleanup(self.provider.chmod, 0o700)
        p = self.apply()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.receipt.exists())
        self.provider.chmod(0o700)
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)['result'], 'applied')

    def test_ambiguous_settings_are_refused(self):
        for number, content in enumerate(('LIMIT=120\nLIMIT=999\n', 'LIMIT=120 999\n', '1LIMIT=120\n', 'LIMIT\n'), 10):
            with self.subTest(content=content):
                self.content(content, revision=number)
                self.assertNoChange(self.apply())

    def test_provider_file_that_is_a_symbolic_link_is_refused(self):
        elsewhere = self.root / 'elsewhere.json'
        elsewhere.write_text('{\n  "LIMIT": "120"\n}\n')
        self.provider.mkdir()
        self.provider_file().symlink_to(elsewhere)
        self.content('LIMIT=999\n')
        p = self.apply()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.receipt.exists())
        p = self.compare()
        self.assertEqual((p.returncode, p.stdout), (1, b''))
        p = self.do_import(self.root / 'app')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(elsewhere.read_text(), '{\n  "LIMIT": "120"\n}\n')
        self.assertTrue(self.provider_file().is_symlink())

    # Hostile inputs for the quoting a shell program can get wrong.
    def test_hostile_values_are_applied_as_the_reference_reads_them(self):
        for number, (line, expected) in enumerate(HOSTILE_VALUES, 100):
            with self.subTest(line=line):
                self.content(line + '\n', revision=number)
                receipt = self.root / ('r-%d.json' % number)
                provider = self.root / ('p-%d' % number)
                p = self.apply(provider=provider, receipt=receipt)
                if expected is None:
                    self.assertNotEqual(p.returncode, 0)
                    self.assertFalse(provider.exists())
                else:
                    self.assertEqual(p.returncode, 0, p.stderr)
                    self.assertEqual(self.read_provider(provider=provider), expected)
                    self.assertEqual(self.provider_file(provider=provider).read_bytes(), (json.dumps(expected, sort_keys=True, indent=2) + '\n').encode())

    def test_hostile_values_survive_import(self):
        values = {'SPACES': 'hello world', 'QUOTES': 'it\'s "quoted"', 'DOLLAR': '$HOME ${PATH}', 'TICKS': '`id` $(id)',
                  'BACKSLASH': 'a\\b\\\\c\\0101', 'PERCENT': '%s %b %n \\n', 'DASH': '-n', 'EQUALS': 'a=b=c', 'EMPTY': '',
                  'UNICODE': 'é😀 ', 'TAB': 'a\tb', 'GLOB': '*', 'SEMI': 'a;b|c&d>e<f', 'NUL_FREE_CONTROL': '\x01\x7f', 'CONTROL_THEN_DIGIT': '\x011\t7'}
        self.write_provider(values)
        folder = self.root / 'app with spaces'
        p = self.do_import(folder)
        self.assertEqual(p.returncode, 0, p.stderr)
        expected = ''.join(k + '=' + shlex.quote(v) + '\n' for k, v in sorted(values.items()))
        self.assertEqual((folder / '.env.production').read_bytes(), expected.encode())
        # Read back the way the add-on reads a revision, every value is the same.
        content = (folder / '.env.production').read_text()
        self.assertEqual({k: (shlex.split(v, comments=True) or [''])[0] for k, _, v in (line.partition('=') for line in content.splitlines())}, values)
        for refused in ({'MULTI': 'a\nb'}, {'RETURN': 'a\rb'}, {'A=B': 'x'}, {'-A': 'x'}, {'API_SECRET': 'plain'}, {'A': ['list']}, {'A': 1}):
            with self.subTest(refused=refused):
                self.write_provider(refused)
                other = self.root / ('refused-%d' % abs(hash(json.dumps(refused))))
                p = self.do_import(other)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse((other / '.env.production').exists())

    def test_a_space_or_unit_is_never_read_as_an_option_of_cub(self):
        if not self.program.endswith('.sh'):
            self.skipTest('a check of the shell version')
        for flag in ('--space', '--unit'):
            for value in ('--context=owner', '--help', '-o=json'):
                with self.subTest(flag=flag, value=value):
                    self.world.forget_calls()
                    p = self.world.run('apply', '--provider-root', self.provider, '--target', 'production', '--space', 'api-live',
                                       '--receipt', self.receipt, '--revision', '7', flag + '=' + value)
                    self.assertNoChange(p)
                    self.assertEqual(self.world.calls(), [])

    def test_paths_with_spaces_dashes_and_a_linked_provider_folder(self):
        real = self.root / 'real provider'
        real.mkdir()
        linked = self.root / 'linked provider'
        linked.symlink_to(real)
        p = self.world.run('apply', '--provider-root=-provider', '--target', 'production', '--space', 'api-live',
                           '--receipt=-receipts/a receipt.json', cwd=self.root)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.read_provider(provider=self.root / '-provider'), {'LIMIT': '120'})
        self.assertTrue((self.root / '-receipts' / 'a receipt.json').is_file())
        p = self.apply(provider=linked, receipt=self.root / 'my receipts' / 'r.json')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(linked.is_symlink())
        self.assertEqual(self.read_provider(provider=real), {'LIMIT': '120'})
        self.assertEqual(self.provider_file(provider=real).stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.compare(provider=linked).returncode, 0)
        p = self.do_import(self.root / '-app', provider=linked)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((self.root / '-app' / '.env.production').read_text(), 'LIMIT=120\n')

    def test_compare_refuses_a_provider_file_it_cannot_read_exactly(self):
        # Valid JSON in another layout is refused, never guessed at.
        self.assertEqual(self.apply().returncode, 0)
        for text in ('{"LIMIT": "120"}\n', '{\n  "LIMIT": "\\u0031\\u0032\\u0030"\n}\n', '{\n  "LIMIT": 120\n}\n', 'not json\n',
                     '{\n  "B": "1",\n  "A": "2"\n}\n', '{\n  "A": "1",\n  "A": "2"\n}\n', '{\n  "A": "1"\n}'):
            with self.subTest(text=text):
                self.provider_file().write_text(text)
                p = self.compare()
                if self.program.endswith('.sh'):
                    self.assertEqual((p.returncode, p.stdout, p.stderr), (1, b'', FAILED))
                else:
                    # Another program may read any JSON; it still prints no value.
                    self.assertNotIn(b'120', p.stdout + p.stderr)


def programs():
    named = os.environ.get('DELIVERY_PROGRAM')
    return {'Program': named} if named else {'Shell': str(HERE / 'delivery.sh')}


for _name, _path in programs().items():
    globals()[_name] = type(_name, (Contract, unittest.TestCase), {'program': _path})


if __name__ == '__main__':
    unittest.main()
