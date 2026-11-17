"""Check blank initialization and preservation of an existing archive."""

import json
from pathlib import Path
import tempfile
import unittest

from init_project import initialize


class InitializeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='canvas-study-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'courses'

    def test_new_project_uses_blank_assets(self):
        result = initialize(self.root)
        self.assertEqual(result['status'], 'initialized')
        self.assertEqual(len(result['created']), 10)
        for name in ('.planning/canvas-resources/inventory.json',
                     'Canvas邮件记录/发送记录.json'):
            self.assertEqual(json.loads((self.root / name).read_text(encoding='utf-8')), [])
        self.assertTrue((self.root / 'AGENTS.md').is_file())

    def test_repeat_preserves_user_changes(self):
        initialize(self.root)
        (self.root / 'AGENTS.md').write_text('My archive rules', encoding='utf-8')
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(initialize(self.root)['status'], 'existing_project')
        after = {p.relative_to(self.root): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_existing_index_prevents_initialization(self):
        self.root.mkdir()
        index = self.root / '课程资源目录.md'
        index.write_text('Existing courses', encoding='utf-8')
        self.assertEqual(initialize(self.root)['status'], 'existing_project')
        self.assertEqual(list(self.root.iterdir()), [index])
        self.assertEqual(index.read_text(encoding='utf-8'), 'Existing courses')


if __name__ == '__main__':
    unittest.main()
