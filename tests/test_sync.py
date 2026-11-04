import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync_upstream', ROOT / 'scripts/sync_upstream.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/modules.json').read_text())
        self.lock = json.loads((ROOT / 'upstream.lock.json').read_text())

    def test_metadata_and_short_desc(self):
        for entry in self.config['modules'].values():
            text = (ROOT / entry['file']).read_text()
            self.assertIn('#!name=' + entry['name'], text)
            self.assertIn('#!category=Belief’s Ad Block', text)
            self.assertIn('#!desc=' + entry['desc'], text)
            self.assertLess(len(entry['desc']), 20)

    def test_reject_new_control_settings(self):
        with self.assertRaises(ValueError):
            sync.read_sections('[General]\nhttp-api = secret@0.0.0.0:6171\n[MITM]\nhostname = x')

    def test_reject_unknown_sections(self):
        with self.assertRaises(ValueError):
            sync.read_sections('[Unknown]\nx = 1')

    def test_weibo_pins_scripts_and_excludes_non_ad_features(self):
        text = (ROOT / 'modules/Belief-Weibo.sgmodule').read_text()
        self.assertNotIn('解锁微博会员APP图标', text)
        self.assertNotIn('非会员设置tab皮肤', text)
        for dep in self.lock['dependencies'].values():
            self.assertIn(dep['url'], text)
            self.assertRegex(dep['revision'], '^[a-f0-9]{40}$')
        names = [l.split('=', 1)[0].strip() for l in sync.read_sections(text)['Script'] if l and not l.startswith('#')]
        self.assertEqual(len(names), len(set(names)))

    def test_idempotent_build_preserves_date(self):
        source = '[Rule]\nDOMAIN,ads.test,REJECT\n[MITM]\nhostname = %APPEND% api.test\n'
        entry = dict(self.config['modules']['amap'])
        entry.pop('override')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'modules').mkdir()
            first = sync.render_module('amap', entry, source, {}, self.config, root)
            previous = first.replace('#!date=' + first.split('#!date=')[1].splitlines()[0], '#!date=2020-01-02')
            (root / entry['file']).write_text(previous)
            self.assertEqual(previous, sync.render_module('amap', entry, source, {}, self.config, root))

    def test_no_unrelated_app_domains(self):
        text = (ROOT / 'modules/Belief-Weibo.sgmodule').read_text()
        self.assertNotIn('viber.com', text)

if __name__ == '__main__':
    unittest.main()

class LoonTranslationTests(unittest.TestCase):
    def test_script_rewrite_and_hosts(self):
        source = '[URL Rewrite]\n^https://ads.example/ - reject\n[Script]\nhttp-response ^https://api.example/ script-path=https://example.test/code.js, tag=test, requires-body=true\n[Mitm]\nhostname = api.example\n'
        result = sync.convert_loon(source)
        self.assertIn('type=http-response, pattern=^https://api.example/', result)
        self.assertIn('hostname = %APPEND% api.example', result)
        self.assertNotIn('tag=test', result)

    def test_unknown_engine_requires_review(self):
        with self.assertRaises(ValueError):
            sync.convert_loon('[Script]\nhttp-response ^https://api.example/ script-path=https://example.test/code.js, engine=webview\n')

    def test_external_jqlang_requires_review(self):
        with self.assertRaises(ValueError):
            sync.convert_loon('[Script]\nhttp-response-jq ^https://api.example/ script-path=https://example.test/a.jq\n')
