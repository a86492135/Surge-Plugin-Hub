#!/usr/bin/env python3
"""Build reviewed Surge snapshots; never execute downloaded scripts."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request
import urllib.error

from loon_to_surge import convert as convert_loon

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {'Rule', 'URL Rewrite', 'Body Rewrite', 'Map Local', 'Script', 'MITM', 'Header Rewrite', 'Host', 'General'}


def read_sections(text):
    result = {}
    section = None
    for line in text.splitlines():
        match = re.fullmatch(r'\[([^\]]+)\]', line.strip())
        if match:
            section = match[1]
            if section not in SECTIONS:
                raise ValueError('Unreviewed upstream section: ' + section)
            result.setdefault(section, [])
        elif section:
            result[section].append(line)
    if not result:
        raise ValueError('Empty upstream module')
    if any(l.strip() and not l.lstrip().startswith('#') for l in result.get('General', [])):
        raise ValueError('Upstream General settings need manual review')
    if re.search(r'(?im)^\s*(?:ca-p12|ca-passphrase|http-api|external-controller-access)\s*=', text):
        raise ValueError('Credential/control setting in upstream module')
    return result


def get_bytes(url):
    headers = {'User-Agent': 'Belief-Surge-Plugin-Hub'}
    if urllib.parse.urlsplit(url).hostname == 'api.github.com' and os.getenv('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        body = resp.read(2_000_001)
    if len(body) > 2_000_000:
        raise ValueError('Upstream file is unexpectedly large')
    return body


def fetch_source(spec):
    repo, path, ref = spec['repo'], spec['path'], spec['ref']
    query = urllib.parse.urlencode({'sha': ref, 'path': path, 'per_page': 1})
    commits = json.loads(get_bytes('https://api.github.com/repos/' + repo + '/commits?' + query))
    if not commits:
        raise ValueError('Upstream path is missing: ' + path)
    revision = commits[0]['sha']
    if not re.fullmatch(r'[a-f0-9]{40}', revision):
        raise ValueError('Invalid upstream revision')
    url = 'https://raw.githubusercontent.com/' + repo + '/' + revision + '/' + path
    body = get_bytes(url)
    body.decode('utf-8-sig')
    return body.decode('utf-8-sig'), {**spec, 'revision': revision, 'sha256': hashlib.sha256(body).hexdigest(), 'url': url}


def load_local_rules(spec, root=ROOT):
    """User-maintained domain rules are built locally, never replaced by an upstream."""
    path = (root / spec['local_rules']).resolve()
    if root.resolve() not in path.parents:
        raise ValueError('Local rule source must stay inside the repository')
    body = path.read_bytes()
    lines = body.decode('utf-8-sig').splitlines()
    rules = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith('#')]
    if not rules or any(not re.fullmatch(r'DOMAIN-SUFFIX,[a-z0-9.-]+,REJECT', line) for line in rules):
        raise ValueError('Local source must contain reviewed domain-suffix reject rules')
    return '[Rule]\n' + '\n'.join(rules) + '\n', {
        'kind': 'local_rules', 'path': spec['local_rules'],
        'sha256': hashlib.sha256(body).hexdigest(),
    }


def preferred_candidates(spec):
    """Prefer the user's Surge directory, then the user's exact Loon URL."""
    policy = spec.get('preferred')
    if not policy:
        return []
    attempts = []
    try:
        tree = json.loads(get_bytes('https://api.github.com/repos/' + policy['repo'] + '/git/trees/' + policy['ref'] + '?recursive=1'))
        if tree.get('truncated'):
            raise ValueError('Preferred repository tree was truncated')
        matches = [i['path'] for i in tree['tree'] if i['type'] == 'blob' and i['path'].startswith(policy['directory']) and re.search(policy['filename_pattern'], i['path'].rsplit('/', 1)[-1], re.I)]
        if len(matches) > 1:
            attempts.append({'kind': 'surge', 'status': 'needs_review', 'reason': 'Multiple candidates', 'paths': matches})
        elif matches:
            text, record = fetch_source({'repo': policy['repo'], 'ref': policy['ref'], 'path': matches[0]})
            attempts.append({'kind': 'surge', 'status': 'available', 'record': record, 'text': text})
        else:
            attempts.append({'kind': 'surge', 'status': 'not_found'})
    except (urllib.error.URLError, ValueError, KeyError) as error:
        attempts.append({'kind': 'surge', 'status': 'unavailable', 'reason': type(error).__name__})
    if policy.get('loon_url'):
        try:
            body = get_bytes(policy['loon_url'])
            record = {'url': policy['loon_url'], 'sha256': hashlib.sha256(body).hexdigest(), 'format': 'loon'}
            attempts.append({'kind': 'loon', 'status': 'available', 'record': record, 'text': convert_loon(body.decode('utf-8-sig'))})
        except urllib.error.HTTPError as error:
            attempts.append({'kind': 'loon', 'status': 'unavailable', 'http_status': error.code, 'url': policy['loon_url']})
        except (urllib.error.URLError, UnicodeError, ValueError) as error:
            attempts.append({'kind': 'loon', 'status': 'needs_review', 'reason': str(error)[:160], 'url': policy['loon_url']})
    return attempts


def render_module(key, spec, source, dependencies, config, root=ROOT):
    sections = read_sections(source)
    if key == 'amap':
        # Empty homepage replies can retain a cached icon. Keep the real card so
        # the targeted script can explicitly disable its newIcon switch.
        replaced = ['/ws/faas/amap-navigation/main-page-aiqs\\?']
        sections['Map Local'] = [line for line in sections.get('Map Local', [])
                                 if not any(path in line and 'data="{}"' in line for path in replaced)]
    if key == 'weibo' and 'https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/weibo/' in source:
        # Retain ad cleanup, not subscription/icon/skin modifications.
        scripts = []
        for line in sections.get('Script', []):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            label = line.split('=', 1)[0]
            if any(word in label for word in ['自定义tab皮肤', '非会员设置tab皮肤', '解锁微博会员APP图标']):
                continue
            match = re.search(r'script-path=([^,\s]+)', line)
            if not match:
                raise ValueError('Upstream script has no script-path')
            url = match[1]
            if url == 'https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/weibo/weibo_ads.js':
                replacement = dependencies['weibo_ads']['url']
            elif url == 'https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/weibo/weibo_main.js':
                replacement = dependencies['weibo_main']['url']
            elif url == 'https://raw.githubusercontent.com/zmqcherish/proxy-script/main/weibo_launch.js':
                replacement = 'https://raw.githubusercontent.com/' + config['repository'] + '/main/scripts/weibo-launch.js'
            else:
                raise ValueError('New upstream script requires review: ' + url)
            line = line.replace(url, replacement)
            scripts.append('Belief-Weibo-%02d = %s' % (len(scripts) + 1, line.split('=', 1)[1].strip()))
        if not scripts:
            raise ValueError('No Weibo response scripts found')
        sections['Script'] = scripts
        # SDK hosts must reach their cleanup script. Remove unrelated-app and advertiser-console rules.
        sections['Rule'] = [l for l in sections.get('Rule', []) if not any(h in l for h in ['viber.com', ',ad.weibo.com,', ',sdkapp.uve.weibo.com,', ',wbapp.uve.weibo.com,'])]
    if spec.get('override'):
        extra = read_sections((root / spec['override']).read_text())
        for section, lines in extra.items():
            sections.setdefault(section, []).extend(lines)
    # Duplicate hostname keys in a section are not a reliable append operation.
    hosts = []
    for line in sections.get('MITM', []):
        if line.strip().startswith('hostname'):
            for host in line.split('=', 1)[1].replace('%APPEND%', '').split(','):
                if host.strip() and host.strip() not in hosts:
                    hosts.append(host.strip())
        elif line.strip() and not line.lstrip().startswith('#'):
            raise ValueError('Upstream MITM settings require review')
    populated = {name for name, lines in sections.items() if any(l.strip() and not l.lstrip().startswith('#') for l in lines)}
    if not hosts and populated != {'Rule'}:
        raise ValueError('Missing MITM hostnames')
    if hosts:
        sections['MITM'] = ['hostname = %APPEND% ' + ', '.join(hosts)]
    # No mutable external executable references may bypass the PR review gate.
    for section, lines in sections.items():
        if section == 'Script':
            for line in lines:
                m = re.search(r'script-path=([^,\s]+)', line)
                if not m:
                    if not line.strip() or line.lstrip().startswith('#'):
                        continue
                    raise ValueError('Unrecognized script line')
                url = m[1]
                own = 'https://raw.githubusercontent.com/' + config['repository'] + '/main/scripts/'
                if not url.startswith(own) and not re.match(r'^https://raw\.githubusercontent\.com/fmz200/wool_scripts/[a-f0-9]{40}/Scripts/weibo/(weibo_ads|weibo_main)\.js$', url):
                    raise ValueError('Unpinned executable dependency')
    header = '\n'.join(['#!name=' + spec['name'], '#!desc=' + spec['desc'], '#!author=' + config['author'], '#!date=DATE_PLACEHOLDER', '#!category=' + config['category']])
    header += '\n\n# SPDX-License-Identifier: ' + spec['license'] + '\n# 维护与来源记录见仓库 THIRD_PARTY_NOTICES.md。\n'
    for section, lines in sections.items():
        if any(l.strip() for l in lines):
            header += '\n[' + section + ']\n' + '\n'.join(lines).strip() + '\n'
    previous = root / spec['file']
    old = previous.read_text() if previous.exists() else ''
    neutral = lambda s: re.sub(r'(?m)^#!date=.*$', '#!date=DATE_PLACEHOLDER', s)
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
    if neutral(old) == header:
        return old
    return header.replace('DATE_PLACEHOLDER', today, 1)


def refresh_index(config, root=ROOT):
    modules = []
    for key, spec in config['modules'].items():
        data = (root / spec['file']).read_bytes()
        date = re.search(r'(?m)^#!date=(.+)$', data.decode()).group(1)
        verification = spec.get('verification', {'level': 'static_only'})
        modules.append({'id': key, 'name': spec['name'], 'path': spec['file'], 'version': spec['version'], 'status': spec['status'], 'device_verified': verification['level'] in {'partial_device', 'device'}, 'verification': verification, 'updated': date, 'sha256': hashlib.sha256(data).hexdigest()})
    (root / 'checksums.sha256').write_text(''.join(m['sha256'] + '  ' + m['path'] + '\n' for m in modules))
    manifest = {'name': 'Surge插件中心', 'maintainer': config['author'], 'category': config['category'], 'updated': max(m['updated'] for m in modules), 'modules': modules}
    (root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    readme = root / 'README.md'
    if readme.exists():
        rows = ['<!-- MODULES:START -->', '| 模块 | 版本 / 更新 | 维护方式 | 验证状态 | 获取 |', '| --- | --- | --- | --- | --- |']
        for item in modules:
            spec = config['modules'][item['id']]
            label = spec.get('label', spec['name'].split('丨')[-1])
            mode = '手动维护' if spec.get('local_rules') else '上游检查 + PR'
            state = {'partial_device': '部分实机通过', 'device': '实机通过', 'static_only': '待实机验证'}[item['verification']['level']]
            raw = 'https://raw.githubusercontent.com/' + config['repository'] + '/main/' + item['path']
            docs = spec.get('docs', 'docs/INSTALL.md')
            rows.append(f'| **{label}** | `{item["version"]}`<br>{item["updated"]} | {mode} | {state} | [Raw 模块]({raw}) · [说明]({docs}) |')
        rows.append('<!-- MODULES:END -->')
        old = readme.read_text()
        new = re.sub(r'<!-- MODULES:START -->.*?<!-- MODULES:END -->', '\n'.join(rows), old, flags=re.S)
        if new != old:
            readme.write_text(new)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline-index', action='store_true', help='Refresh checksums/manifest from existing local modules only')
    args = parser.parse_args()
    config = json.loads((ROOT / 'config/modules.json').read_text())
    if args.offline_index:
        refresh_index(config)
        return
    dependencies = {}
    lock = {'schema': 1, 'modules': {}, 'dependencies': {}}
    for name, source in config['dependencies'].items():
        _, record = fetch_source(source)
        dependencies[name] = record
        lock['dependencies'][name] = record
    generated = {}
    reviews = {}
    for key, spec in config['modules'].items():
        if spec.get('local_rules'):
            source, record = load_local_rules(spec)
            generated[spec['file']] = render_module(key, spec, source, dependencies, config)
            lock['modules'][key] = record
            continue
        attempts = preferred_candidates(spec)
        accepted = False
        for attempt in attempts:
            if attempt['status'] != 'available':
                continue
            try:
                generated[spec['file']] = render_module(key, spec, attempt['text'], dependencies, config)
                lock['modules'][key] = attempt['record']
                attempt['status'] = 'selected'
                accepted = True
                break
            except ValueError as error:
                attempt['status'] = 'needs_review'
                attempt['reason'] = str(error)[:160]
        if attempts:
            reviews[key] = [{k: v for k, v in a.items() if k != 'text'} for a in attempts]
        if accepted:
            continue
        source, record = fetch_source(spec['source'])
        generated[spec['file']] = render_module(key, spec, source, dependencies, config)
        lock['modules'][key] = record
    # Resolve and validate every source before any local output is changed.
    for path, text in generated.items():
        (ROOT / path).write_text(text)
    (ROOT / 'upstream.lock.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    (ROOT / 'upstream-review.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    refresh_index(config)
    print('Rebuilt modules with fixed branding and pinned upstream scripts. Device behavior is unverified.')


if __name__ == '__main__':
    main()
