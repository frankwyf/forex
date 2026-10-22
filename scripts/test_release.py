import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from scripts.build_release import build, git


class ReleaseArchiveTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        (self.root / "forex").mkdir(parents=True)
        (self.root / "forex" / "__init__.py").write_text('__version__ = "0.2.0"\n', encoding="utf-8")
        (self.root / "README.md").write_text("Synthetic release fixture\n", encoding="utf-8")
        git(self.root, "init", "-b", "main")
        git(self.root, "add", "forex", "README.md")
        git(self.root, "-c", "user.name=Release Test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-m", "Synthetic fixture")
        git(self.root, "tag", "v0.2.0")
        self.output = Path(self.directory.name) / "dist"

    def test_archives_include_tracked_source_and_exclude_local_files(self):
        (self.root / ".env").write_text("SYNTHETIC_TEST_ONLY=1", encoding="utf-8")
        (self.root / "db.sqlite3").write_bytes(b"synthetic non-database fixture")
        archives = build(self.root, self.output, "v0.2.0")
        self.assertEqual(len(archives), 2)
        with zipfile.ZipFile(archives[1]) as archive:
            names = archive.namelist()
        self.assertIn("forex-0.2.0/README.md", names)
        self.assertFalse(any(".env" in name or ".sqlite3" in name for name in names))
        expected = hashlib.sha256(archives[1].read_bytes()).hexdigest()
        self.assertIn(expected, (self.output / "SHA256SUMS.txt").read_text())

    def test_tag_version_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "match"):
            build(self.root, self.output, "v9.0.0")

    def test_dirty_tracked_tree_is_rejected(self):
        (self.root / "README.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "clean"):
            build(self.root, self.output)

    def test_tracked_runtime_file_is_rejected(self):
        (self.root / ".env").write_text("SYNTHETIC_TEST_ONLY=1", encoding="utf-8")
        git(self.root, "add", ".env")
        git(self.root, "-c", "user.name=Release Test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-m", "Synthetic forbidden fixture")
        with self.assertRaisesRegex(ValueError, "sensitive"):
            build(self.root, self.output)
