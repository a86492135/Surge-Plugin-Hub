import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
import re
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

    def test_homepage_empty_reply_does_not_shadow_patch(self):
        source = '[Map Local]\n(?i)^https://m5\\.amap\\.com/ws/faas/amap-navigation/main-page-assets\\? data-type=text data="{}"\n(?i)^https://m5\\.amap\\.com/ws/faas/amap-navigation/main-page-aiqs\\? data-type=text data="{}"\n^https://ads.test/ data-type=text data="{}"\n[MITM]\nhostname = m5.amap.com\n'
        entry = dict(self.config['modules']['amap'])
        entry.pop('override')
        rendered = sync.render_module('amap',entry,source,{},self.config)
        self.assertIn('main-page-assets',rendered)
        self.assertNotIn('main-page-aiqs',rendered)
        self.assertIn('^https://ads.test/',rendered)

    def test_splash_rewrite_only_targets_ad_paths(self):
        sections = sync.read_sections((ROOT / 'overrides/amap.sgmodule').read_text())
        rule = next(line for line in sections['URL Rewrite'] if line.endswith(' _ reject'))
        pattern = re.compile(rule.split()[0])
        for url in ['https://amap-aos-info-nogw.amap.com/ws/aos/alimama/splash_screen_rt?ent=2', 'https://m5.amap.com/ws/valueadded/alimama/splash_screen?x=1']:
            self.assertIsNotNone(pattern.search(url))
        for url in ['https://m5.amap.com/ws/shield/frogserver/aocs/updatable/1?x=1','https://m5.amap.com/ws/faas/amap-navigation/main-page-aiqs?x=1','https://m5.amap.com/ws/aos/alimama/splash_screen_other?x=1','https://example.com/ws/aos/alimama/splash_screen_rt?x=1']:
            self.assertIsNone(pattern.search(url))
        self.assertIn('amap-aos-info-nogw.amap.com',sections['MITM'][0])

    def test_local_rules_build_without_mitm_or_scripts(self):
        entry = self.config['modules']['variflight-pro']
        source, record = sync.load_local_rules(entry)
        rendered = sync.render_module('variflight-pro',entry,source,{},self.config)
        sections = sync.read_sections(rendered)
        expected = [line for line in source.splitlines() if line.startswith('DOMAIN-SUFFIX,')]
        self.assertEqual(sections['Rule'],expected)
        self.assertNotIn('MITM',sections)
        self.assertNotIn('Script',sections)
        self.assertEqual(record['kind'],'local_rules')

    def test_local_rules_cannot_read_outside_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                sync.load_local_rules({'local_rules':'../outside.list'},Path(temp))

    def test_manual_snapshot_keeps_imported_content(self):
        entry=self.config['modules']['blockads']
        text,record=sync.load_manual_snapshot(entry)
        self.assertEqual(text,(ROOT/entry['file']).read_text())
        self.assertEqual(record['kind'],'manual_snapshot')
        lines=[line for line in sync.read_sections(text)['Script'] if line.strip() and not line.startswith('#')]
        self.assertEqual(len(lines),32)
        self.assertEqual(len(set(line.split('=',1)[0] for line in lines)),32)
        self.assertNotIn('{{{',text)

    def test_manual_snapshot_runtime_changes_require_review(self):
        entry=dict(self.config['modules']['blockads'])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            target=root/entry['file']
            target.parent.mkdir(parents=True)
            text=(ROOT/entry['file']).read_text()
            first=entry['runtime_scripts'][0]
            target.write_text(text.replace(first,'https://example.invalid/unreviewed.js'))
            with self.assertRaises(ValueError):
                sync.load_manual_snapshot(entry,root)

    def test_index_catalog_and_verification_share_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'modules').mkdir()
            for entry in self.config['modules'].values():
                (root/entry['file']).write_bytes((ROOT/entry['file']).read_bytes())
            (root/'README.md').write_text('before\n<!-- MODULES:START -->\nstale\n<!-- MODULES:END -->\nafter\n')
            sync.refresh_index(self.config,root)
            manifest=json.loads((root/'manifest.json').read_text())
            amap=next(item for item in manifest['modules'] if item['id']=='amap')
            self.assertTrue(amap['device_verified'])
            self.assertEqual(amap['verification']['level'],'partial_device')
            self.assertIn('开屏广告',amap['verification']['passed'])
            readme=(root/'README.md').read_text()
            self.assertIn('飞常准业内版',readme)
            self.assertIn('手动维护',readme)
            self.assertNotIn('stale',readme)
            self.assertTrue(readme.startswith('before\n'))
            self.assertTrue(readme.endswith('after\n'))

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

if __name__ == '__main__':
    unittest.main()
