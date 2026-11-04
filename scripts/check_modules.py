#!/usr/bin/env python3
"""Static checks only; these do not prove that ads disappear on a device."""
import hashlib
import pathlib
import re
import shlex
import shutil
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
modules = sorted((root / "modules").glob("*.sgmodule"))
if not modules:
    raise SystemExit("No modules found")
if not shutil.which("jq"):
    raise SystemExit("jq is required for expression compilation")
for path in modules:
    text = path.read_text(encoding="utf-8")
    for key in ("name", "author", "date"):
        assert re.search(r"^#!" + key + r"=.+$", text, re.M), (path.name, key)
    assert not re.search(r"(?im)^\s*(?:ca-p12|ca-passphrase|http-api|external-controller-access|http-listen|socks5-listen)\s*=", text), path.name
    assert "PRIVATE KEY-----" not in text, path.name
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("http-response-jq "):
            parts = shlex.split(line)
            assert len(parts) == 3, (path.name, number)
            compiled = subprocess.run(
                ["jq", "-n", "if false then (" + parts[2] + ") else null end"],
                capture_output=True, text=True,
            )
            assert compiled.returncode == 0, (path.name, number, compiled.stderr)
    checksums = (root / "checksums.sha256").read_text().splitlines()
    expected = {line.split(maxsplit=1)[1].strip(): line.split()[0] for line in checksums}
    relative = path.relative_to(root).as_posix()
    assert expected[relative] == hashlib.sha256(path.read_bytes()).hexdigest(), path.name
    print("OK:", relative, "(metadata / jq compilation / credential patterns / SHA-256)")
print("Static checks passed. Device behavior remains unverified.")
