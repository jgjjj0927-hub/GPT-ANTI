import tempfile
import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

from core.scanner import ScanEngine
import core.quarantine as quarantine


class ScannerTests(unittest.TestCase):
    def test_entropy_empty(self):
        self.assertEqual(ScanEngine._calc_entropy(b""), 0.0)

    def test_entropy_uniform(self):
        self.assertEqual(ScanEngine._calc_entropy(bytes(range(256))), 8.0)

    def test_symlink_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target.txt"
            target.write_text("safe", encoding="utf-8")
            link = root / "link.txt"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable")
            self.assertIsNone(ScanEngine()._analyze_file(link))


class QuarantineTests(unittest.TestCase):
    def test_quarantine_and_restore_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            qdir = home / "quarantine"
            source = root / "sample.bin"
            source.write_bytes(b"sample")
            digest = hashlib.sha256(b"sample").hexdigest()
            record = {"path": str(source), "name": source.name, "hash": digest, "severity": "ÐÐ¸Ð·ÐºÐ°Ñ"}
            def make_dirs():
                qdir.mkdir(parents=True, exist_ok=True)
            with patch.object(quarantine, "HOME_DIR", home), patch.object(quarantine, "QUARANTINE_DIR", qdir), patch.object(quarantine, "DB_FILE", home / "quarantine.json"), patch.object(quarantine, "ensure_dirs", make_dirs):
                self.assertTrue(quarantine.add_to_quarantine(record))
                self.assertFalse(source.exists())
                self.assertEqual(len(quarantine.list_quarantine()), 1)
                self.assertTrue(quarantine.restore_file(0))
                self.assertEqual(source.read_bytes(), b"sample")
                self.assertEqual(quarantine.list_quarantine(), [])

    def test_rejects_file_changed_after_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            qdir = home / "quarantine"
            source = root / "sample.bin"
            source.write_bytes(b"changed")
            record = {"path": str(source), "name": source.name, "hash": "a" * 64}
            def make_dirs():
                qdir.mkdir(parents=True, exist_ok=True)
            with patch.object(quarantine, "HOME_DIR", home), patch.object(quarantine, "QUARANTINE_DIR", qdir), patch.object(quarantine, "DB_FILE", home / "quarantine.json"), patch.object(quarantine, "ensure_dirs", make_dirs):
                self.assertFalse(quarantine.add_to_quarantine(record))
                self.assertTrue(source.exists())

    def test_rejects_path_outside_quarantine(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            qdir = home / "quarantine"
            outside = root / "outside.bin"
            outside.write_bytes(b"x")
            with patch.object(quarantine, "QUARANTINE_DIR", qdir):
                self.assertIsNone(quarantine._safe_quarantine_path(str(outside)))


if __name__ == "__main__":
    unittest.main()
