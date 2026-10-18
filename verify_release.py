#!/usr/bin/env python3
"""Verify fixed release files without running an analysis or making network calls."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
mp = root/'release_manifest.json'
manifest = json.loads(mp.read_text())
bad = []
for item in manifest['files']:
    path = root/item['file']
    if not path.is_file() or path.is_symlink() or sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
        bad.append(item['file'])
seal_ok = mp.with_name('release_manifest.json.sha256').read_text().split() == [sha(mp), mp.name]
core = json.loads((root/'tested_core.json').read_text())
changed = [name for name, digest in core['files'].items() if not (root/name).is_file() or sha(root/name) != digest]
result = {'ok': not bad and seal_ok and not changed, 'tracked_files': len(manifest['files']),
          'bad_files': bad, 'manifest_seal_ok': seal_ok, 'changed_reproduction_core': changed,
          'publication_status': manifest['state'],
          'scope': 'integrity of tracked files and fixed reproduction core; not a scientific admission'}
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['ok'] else 2)
