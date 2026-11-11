"""Delivery add-on contract checks. No real provider credentials or services."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('delivery', Path(__file__).with_name('delivery.py'))
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.provider = delivery.DirectoryProvider(self.root / 'provider')

    def snap(self, content='LIMIT=120\n', revision=7):
        import hashlib
        return dict(contract='confighub.config-snapshot/v1', space='api-live', unit='app',
                    revision=revision, sha256=hashlib.sha256(content.encode()).hexdigest(), content=content)

    def test_pinned_revision_applied_and_retry_makes_no_change(self):
        value = self.snap()
        with patch.object(delivery.snapshot_reader, 'snapshot', return_value=value) as read:
            first = delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
            mtime = self.provider.path('production').stat().st_mtime_ns
            second = delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json', revision=7)
        self.assertEqual(read.call_args_list[0].args, ('api-live', 'app', None))
        self.assertEqual(read.call_args_list[1].args, ('api-live', 'app', 7))
        self.assertEqual((first['result'], second['result']), ('applied', 'unchanged'))
        self.assertEqual(self.provider.path('production').stat().st_mtime_ns, mtime)
        self.assertEqual(first['revision'], 7)
        self.assertEqual((self.root / 'receipt.json').stat().st_mode & 0o777, 0o600)

    def test_wrong_key_or_unknown_revision_never_writes(self):
        for message in ('wrong key', 'unknown revision'):
            with self.subTest(message=message), patch.object(delivery.snapshot_reader, 'snapshot', side_effect=RuntimeError(message)):
                with self.assertRaises(RuntimeError):
                    delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
                self.assertFalse(self.provider.path('production').exists())
                self.assertFalse((self.root / 'receipt.json').exists())

    def test_racing_head_update_does_not_change_the_pinned_read(self):
        calls = []
        def read(args):
            calls.append(args)
            if args[0] == 'unit':
                return b'{"Unit":{"HeadRevisionNum":7}}'
            self.assertEqual(args, ['revision', 'data', 'app', '7', '--space', 'api-live'])
            # The head is now 8; only the pinned revision may be fetched.
            return b'LIMIT=120\n'
        with patch.object(delivery.snapshot_reader, 'cub', side_effect=read):
            receipt = delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
        self.assertEqual(len(calls), 2)
        self.assertEqual(receipt['revision'], 7)
        self.assertEqual(self.provider.read('production'), {'LIMIT': '120'})

    def test_transient_read_retries_but_denied_read_does_not(self):
        import subprocess
        failed = subprocess.CompletedProcess([], 1, b'', b'HTTP 503')
        head = subprocess.CompletedProcess([], 0, b'{"Unit":{"HeadRevisionNum":7}}', b'')
        data = subprocess.CompletedProcess([], 0, b'LIMIT=120\n', b'')
        with patch.object(delivery.snapshot_reader.subprocess, 'run', side_effect=[failed, head, data]) as run, patch.object(delivery.snapshot_reader.time, 'sleep'):
            delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
            self.assertEqual(run.call_count, 3)
        denied = subprocess.CompletedProcess([], 1, b'', b'403 credential-that-must-stay-private')
        with patch.object(delivery.snapshot_reader.subprocess, 'run', return_value=denied) as run:
            with self.assertRaises(RuntimeError) as error:
                delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
            self.assertEqual(run.call_count, 1)
            self.assertNotIn('credential-that-must-stay-private', str(error.exception))

    def test_atomic_files_leave_no_temporary_files_after_failure(self):
        with patch.object(delivery.os, 'link', side_effect=FileExistsError('racing writer')):
            with self.assertRaises(FileExistsError):
                delivery.private_write(self.root / 'new.env', b'LIMIT=120\n')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_secret_is_reference_only_and_compared_by_presence(self):
        settings = delivery.settings(self.snap('LIMIT=120\nAPI_TOKEN=secret://vault/project/token\n'))
        self.assertEqual(settings['API_TOKEN'], {'secret_ref': 'secret://vault/project/token'})
        self.provider.write('production', settings)
        different_ref = dict(settings, API_TOKEN={'secret_ref': 'secret://another/token'})
        self.assertEqual(delivery.differences(settings, different_ref), [])
        self.assertEqual(delivery.differences(settings, {'LIMIT': '120'}), ['API_TOKEN'])
        with self.assertRaisesRegex(ValueError, 'secret reference'):
            delivery.settings(self.snap('API_TOKEN=never-record-this-value\n'))

    def test_import_is_private_idempotent_and_never_overwrites(self):
        self.provider.write('preview', {'LIMIT': '60'})
        self.provider.write('production', {'LIMIT': '120', 'API_TOKEN': {'secret_ref': 'secret://vault/token'}})
        folder = self.root / 'import'
        delivery.import_settings(self.provider, folder, 'preview', 'production')
        delivery.import_settings(self.provider, folder, 'preview', 'production')
        p = folder / '.env.production'
        self.assertEqual(p.stat().st_mode & 0o777, 0o600)
        self.assertIn('secret://vault/token', p.read_text())
        p.write_text('LIMIT=other\n')
        with self.assertRaises(ValueError): delivery.import_settings(self.provider, folder, 'preview', 'production')
        self.assertEqual(p.read_text(), 'LIMIT=other\n')

    def test_identical_existing_import_must_also_be_private(self):
        path = self.root / 'existing.env'
        path.write_bytes(b'LIMIT=120\n')
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            delivery.private_write(path, b'LIMIT=120\n')

    def test_hash_mismatch_and_unknown_contract_are_refused(self):
        for change in ({'sha256': '0' * 64}, {'contract': 'unknown'}, {'revision': True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                delivery.settings(dict(self.snap(), **change))

    def test_compare_detects_dashboard_change_without_values(self):
        a = delivery.settings(self.snap())
        self.assertEqual(delivery.differences(a, dict(a, LIMIT='999')), ['LIMIT'])
        self.assertEqual(delivery.differences(a, dict(a, EXTRA='private')), ['EXTRA'])

    def test_hub_marker_is_not_an_application_setting(self):
        self.assertEqual(delivery.settings(self.snap('LIMIT=120\nconfigHub.configName=app\n')), {'LIMIT': '120'})

    def test_credential_shaped_values_are_refused_even_with_an_ordinary_name(self):
        for value in ('ghp_' + 'a' * 36, 'AKIA' + 'A' * 16, 'https://user:password@example.invalid', 'sk-' + 'a' * 48):
            with self.subTest(value_type=value[:4]):
                with self.assertRaises(ValueError):
                    delivery.settings(self.snap('SETTING=' + value + '\n'))
                self.provider.write('production', {'SETTING': value})
                with self.assertRaises(ValueError):
                    delivery.import_settings(self.provider, self.root / 'import')
                self.assertFalse((self.root / 'import/.env.production').exists())

    def test_output_symlinks_and_target_traversal_are_refused(self):
        elsewhere = self.root / 'elsewhere'
        elsewhere.write_text('keep')
        receipt = self.root / 'receipt.json'
        receipt.symlink_to(elsewhere)
        with patch.object(delivery.snapshot_reader, 'snapshot', return_value=self.snap()):
            with self.assertRaises(ValueError): delivery.apply(self.provider, 'production', 'api-live', 'app', receipt)
        self.assertFalse(self.provider.path('production').exists())
        self.assertEqual(elsewhere.read_text(), 'keep')
        with self.assertRaises(ValueError): self.provider.path('../elsewhere')

    def test_failed_provider_apply_has_no_success_receipt_and_retry_recovers(self):
        with patch.object(delivery.snapshot_reader, 'snapshot', return_value=self.snap()):
            with patch.object(self.provider, 'write', side_effect=OSError('provider unavailable')):
                with self.assertRaises(OSError): delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
            self.assertFalse((self.root / 'receipt.json').exists())
            result = delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
        self.assertEqual(result['result'], 'applied')

    def test_ambiguous_settings_are_refused(self):
        # A setting named twice could be read either way; neither is applied.
        for content in ('LIMIT=120\nLIMIT=999\n', 'LIMIT=120 999\n', '1LIMIT=120\n', 'LIMIT\n'):
            with self.subTest(content=content), patch.object(delivery.snapshot_reader, 'snapshot', return_value=self.snap(content)):
                with self.assertRaises(ValueError):
                    delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
                self.assertFalse(self.provider.path('production').exists())
                self.assertFalse((self.root / 'receipt.json').exists())

    def test_provider_file_that_is_a_symbolic_link_is_refused(self):
        # A provider file swapped for a link must not be read or written through.
        elsewhere = self.root / 'elsewhere.json'
        elsewhere.write_text('{"LIMIT": "120"}\n')
        self.provider.root.mkdir(parents=True)
        self.provider.path('production').symlink_to(elsewhere)
        with self.assertRaises(ValueError):
            self.provider.read('production')
        with patch.object(delivery.snapshot_reader, 'snapshot', return_value=self.snap('LIMIT=999\n')):
            with self.assertRaises(ValueError):
                delivery.apply(self.provider, 'production', 'api-live', 'app', self.root / 'receipt.json')
        self.assertEqual(elsewhere.read_text(), '{"LIMIT": "120"}\n')
        self.assertFalse((self.root / 'receipt.json').exists())


if __name__ == '__main__':
    unittest.main()
