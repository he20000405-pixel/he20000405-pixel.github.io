"""Verify the limited ownership handoff without requiring Docker in unit tests."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import build_sites


class SearchIndexOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='chonggrok-permissions-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.target = self.root / 'portal/search-index.json'
        self.target.parent.mkdir()
        self.target.write_text('[]', encoding='utf-8')
        self.run = self.enterContext(patch.object(build_sites, 'run'))
        self.enterContext(patch.object(build_sites.os, 'getuid', return_value=1001, create=True))
        self.enterContext(patch.object(build_sites.os, 'getgid', return_value=1002, create=True))

    def test_writable_index_needs_no_container(self):
        with patch.object(build_sites.os, 'access', return_value=True):
            result = build_sites.prepare_search_index(self.root)
        self.assertFalse(result['ownershipChanged'])
        self.run.assert_not_called()

    def test_only_the_index_is_mounted_and_reassigned(self):
        with patch.object(build_sites.os, 'access', side_effect=[False, True]):
            result = build_sites.prepare_search_index(self.root)
        self.run.assert_called_once_with(
            'docker', 'run', '--rm', '--network', 'none',
            '--mount', 'type=bind,source=' + str(self.target) + ',target=/search-index.json',
            '--entrypoint', '/bin/chown', build_sites.IMAGE, '1001:1002', '/search-index.json')
        self.assertTrue(result['ownershipChanged'])
        self.assertEqual(self.target.read_text(encoding='utf-8'), '[]')

    def test_still_unwritable_is_a_hard_failure(self):
        with patch.object(build_sites.os, 'access', return_value=False):
            with self.assertRaises(PermissionError):
                build_sites.prepare_search_index(self.root)

    def test_container_failure_is_not_suppressed(self):
        self.run.side_effect = subprocess.CalledProcessError(1, ['docker'])
        with patch.object(build_sites.os, 'access', return_value=False):
            with self.assertRaises(subprocess.CalledProcessError):
                build_sites.prepare_search_index(self.root)

    def test_missing_index_is_rejected_before_docker(self):
        self.target.unlink()
        with self.assertRaises(RuntimeError):
            build_sites.prepare_search_index(self.root)
        self.run.assert_not_called()

    def test_symlink_index_is_rejected_before_docker(self):
        with patch.object(Path, 'is_symlink', return_value=True):
            with self.assertRaises(RuntimeError):
                build_sites.prepare_search_index(self.root)
        self.run.assert_not_called()

    def test_resolved_path_outside_build_is_rejected(self):
        original_resolve = Path.resolve
        target = self.target
        outside = self.root.parent / 'outside-index.json'
        def resolve(path, *args, **kwargs):
            return outside if path == target else original_resolve(path, *args, **kwargs)
        with patch.object(Path, 'resolve', resolve):
            with self.assertRaises(RuntimeError):
                build_sites.prepare_search_index(self.root)
        self.run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
