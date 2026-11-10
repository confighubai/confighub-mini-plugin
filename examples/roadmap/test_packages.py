"""The downloader must not replace a good cached archive with bad bytes."""
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('packages', Path(__file__).with_name('get-packages.py'))
packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)

class DownloadTests(unittest.TestCase):
    def test_bad_checksum_preserves_cache_and_removes_partial_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            archive = directory / 'package.tar.xz'
            archive.write_bytes(b'older-cache')
            digest = hashlib.sha256(b'expected').hexdigest()
            with patch.object(packages.urllib.request, 'urlopen', return_value=io.BytesIO(b'bad-download')):
                with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
                    packages.download(archive.name, directory, digest)
            self.assertEqual(archive.read_bytes(), b'older-cache')
            self.assertEqual(list(directory.iterdir()), [archive])

    def test_verified_cache_is_reused_without_network(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            archive = directory / 'package.tar.xz'
            archive.write_bytes(b'expected')
            with patch.object(packages.urllib.request, 'urlopen') as request:
                self.assertEqual(packages.download(archive.name, directory, hashlib.sha256(b'expected').hexdigest()), archive)
                request.assert_not_called()

if __name__ == '__main__': unittest.main()
