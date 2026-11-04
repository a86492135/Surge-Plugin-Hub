"""Conservative Loon plugin translation. Unsupported syntax requires review."""
import re


def convert(text):
    names = {'Rule': 'Rule', 'URL Rewrite': 'URL Rewrite', 'Rewrite': 'URL Rewrite',
             'Body Rewrite': 'Body Rewrite', 'Map Local': 'Map Local',
             'Script': 'Script', 'Mitm': 'MITM', 'MITM': 'MITM', 'Host': 'Host'}
    sections = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(('#', ';', '//')):
            continue
        if line.startswith('[') and line.endswith(']'):
            name = line[1:-1]
            if name not in names:
                raise ValueError('Loon section requires manual translation: ' + name)
            current = names[name]
            sections.setdefault(current, [])
            continue
        if current is None:
            raise ValueError('Unrecognized Loon header')
        if current == 'Script':
            match = re.fullmatch(r'(http-request|http-response)\s+(\S+)\s+(.+)', line)
            if not match:
                # Includes external JQLang files, event hooks and other Loon-only engines.
                raise ValueError('Loon script/JQLang requires manual translation')
            kind, pattern, attrs = match.groups()
            options = {}
            for item in re.split(r',\s*(?=[\w-]+\s*=)', attrs):
                if '=' not in item:
                    raise ValueError('Invalid Loon script option')
                key, value = item.split('=', 1)
                options[key.strip()] = value.strip()
            allowed = {'script-path', 'tag', 'enable', 'requires-body', 'binary-body-mode', 'timeout', 'max-size', 'argument'}
            if set(options) - allowed or 'script-path' not in options:
                raise ValueError('Unsupported Loon script option')
            if options.get('enable', 'true').lower() in ('false', '0'):
                continue
            options.pop('tag', None)
            options.pop('enable', None)
            label = 'Belief-Converted-%02d' % (len(sections[current]) + 1)
            line = label + ' = type=' + kind + ', pattern=' + pattern + ', ' + ', '.join(k + '=' + v for k, v in options.items())
        elif current == 'URL Rewrite':
            if re.fullmatch(r'\S+\s+reject(?:-200|-dict|-array|-img)?', line):
                pattern, action = line.split()
                if action != 'reject':
                    raise ValueError('Loon local response action requires manual translation')
                line = pattern + ' - reject'
            elif not re.fullmatch(r'\S+\s+\S+\s+(?:reject|30[1278])', line):
                raise ValueError('Unrecognized Loon rewrite')
        elif current == 'MITM':
            if not line.startswith('hostname') or '=' not in line:
                raise ValueError('Loon certificate/settings must not be imported')
            line = 'hostname = %APPEND% ' + line.split('=', 1)[1].replace('%APPEND%', '').strip()
        elif current == 'Rule':
            if not line.split(',', 1)[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'URL-REGEX', 'IP-CIDR', 'IP-CIDR6', 'AND', 'OR', 'NOT', 'DEST-PORT'}:
                raise ValueError('Loon rule requires manual translation')
            if 'pre-matching' in line or 'extended-matching' in line:
                raise ValueError('Loon-only matching option')
        sections[current].append(line)
    if not sections:
        raise ValueError('Empty Loon plugin')
    return '\n'.join('[' + k + ']\n' + '\n'.join(v) for k, v in sections.items()) + '\n'
