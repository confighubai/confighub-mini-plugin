"""Failure cleanup and result files are part of the runnable contract."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('roadmap', Path(__file__).with_name('run.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class RunnerTests(unittest.TestCase):
    def test_constructor_failure_removes_only_its_workspace(self):
        with tempfile.TemporaryDirectory() as home, patch.object(runner.Path, 'home', return_value=Path(home)), patch.object(runner, 'run', side_effect=RuntimeError('install failed')):
            unrelated = Path(home) / 'unrelated'
            unrelated.write_text('keep')
            with self.assertRaises(RuntimeError): runner.Example('r2', Path('/package'))
            self.assertEqual(list(Path(home).iterdir()), [unrelated])

    def test_cleanup_rejects_unowned_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError): runner.cleanup(Path(temporary), Path('/package'))
            self.assertTrue(Path(temporary).is_dir())

    def test_cleanup_failure_still_writes_incomplete_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / 'package'
            (package / 'bin').mkdir(parents=True)
            (package / 'bin/confighub-mini-app').touch()
            result = Path(temporary) / 'result.json'
            class Example:
                checks = []
                def finish(self): raise RuntimeError('cleanup failed')
            with patch.object(runner, 'Example', return_value=Example()), patch.object(runner, 'r2'), patch('sys.argv', ['run.py', 'r2', '--package', str(package), '--out', str(result)]):
                with self.assertRaises(RuntimeError): runner.main()
            record = json.loads(result.read_text())
            self.assertFalse(record['complete'])
            self.assertEqual(record['failed'], 1)

if __name__ == '__main__': unittest.main()
