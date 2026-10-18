#!/usr/bin/env python3
"""Regenerate the full national cantonal table set and F7 from frozen CSVs."""
import argparse
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import site
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(); root = Path(__file__).resolve().parent
    out = args.out.resolve()
    if out.exists():
        raise SystemExit('STOP: destination must be new')
    cfg = Path(sys.prefix)/'pyvenv.cfg'
    if not (sys.prefix != sys.base_prefix and cfg.is_file()
            and 'include-system-site-packages = false' in cfg.read_text().lower()
            and site.ENABLE_USER_SITE is False):
        raise SystemExit('STOP: run with an isolated venv using python -I -B')
    versions = {}
    for line in (root/'requirements.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        name, version = line.split('=='); actual = importlib.metadata.version(name)
        if actual != version:
            raise SystemExit(f'STOP: dependency {name}: expected {version}, got {actual}')
        versions[name] = actual
    prefix = Path(sys.prefix).resolve()
    modules = {}
    for name in ('numpy', 'matplotlib', 'PIL', 'contourpy', 'fontTools', 'kiwisolver',
                 'cycler', 'packaging', 'pyparsing', 'dateutil', 'six'):
        spec = importlib.util.find_spec(name)
        if spec is None or not spec.origin:
            raise SystemExit(f'STOP: dependency module missing: {name}')
        path = Path(spec.origin).resolve()
        if not path.is_relative_to(prefix):
            raise SystemExit(f'STOP: dependency outside venv: {name}')
        modules[name] = str(path.relative_to(prefix))
    source = json.loads((root/'source_provenance.json').read_text())
    if not all(digest(root/r['local_file']) == r['sha256'] for r in source['sources']):
        raise SystemExit('STOP: input hash mismatch')
    core = json.loads((root/'tested_core.json').read_text())
    if not all(digest(root/rel) == expected for rel, expected in core['files'].items()):
        raise SystemExit('STOP: reproduction core differs from the fixed candidate')
    started = time.monotonic(); out.mkdir()
    env = dict(os.environ)
    env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None)
    env['MPLCONFIGDIR'] = str(out/'runtime_cache/matplotlib')
    env['XDG_CACHE_HOME'] = str(out/'runtime_cache/xdg')
    for script, argv, label in [
        ('analyze.py', ['--out', str(out/'analysis')], 'analysis'),
        ('render.py', ['--analysis', str(out/'analysis'), '--out', str(out/'figures')], 'render')]:
        result = subprocess.run([sys.executable, '-I', '-B', str(root/script)] + argv,
                                cwd=root, env=env, capture_output=True, text=True)
        (out/f'{label}.stdout.txt').write_text(result.stdout)
        (out/f'{label}.stderr.txt').write_text(result.stderr)
        if result.returncode:
            raise SystemExit(f'STOP: {script} exited {result.returncode}; preserve output for inspection')
    checks = {}
    checks['six_full_csvs_byte_identical'] = all(
        digest(q) == digest(out/'analysis'/q.name)
        for q in (root/'expected/analysis').glob('*.csv'))
    checks['six_csvs_present'] = len(list((out/'analysis').glob('*.csv'))) == 6
    expected = json.loads((root/'expected/analysis/summary.json').read_text())
    actual = json.loads((out/'analysis/summary.json').read_text())
    checks['analytical_summary_identical'] = ({k:v for k,v in expected.items() if k != 'runtime'} ==
                                            {k:v for k,v in actual.items() if k != 'runtime'})
    expected_fig = json.loads((root/'expected/figure/figure_data.json').read_text())
    actual_fig = json.loads((out/'figures/figure_data.json').read_text())
    excluded = {'exports', 'source_analysis_summary_sha256'}
    checks['figure_numerical_bindings_identical'] = (
        {k:v for k,v in expected_fig.items() if k not in excluded} ==
        {k:v for k,v in actual_fig.items() if k not in excluded})
    checks['all_218_cantons_in_figure'] = len(actual_fig['primary_cohort']) == 218
    checks['all_12_robustness_contexts_in_figure'] = len(actual_fig['robustness_panel']) == 12
    checks['all_2180_canton_year_support_rows'] = actual['rows'] == 2180
    checks['all_60_contexts_regenerated'] = sum(1 for _ in (out/'analysis/robustness.csv').open()) - 1 == 60
    checks['all_three_figure_formats_present'] = all((out/f'figures/F7_mean_and_distribution.{x}').is_file() for x in ('png','svg','pdf'))
    from PIL import Image
    with Image.open(root/'expected/figure/F7_mean_and_distribution.png') as e, Image.open(out/'figures/F7_mean_and_distribution.png') as a:
        expected_pixels, actual_pixels = e.convert('RGBA').tobytes(), a.convert('RGBA').tobytes()
        pixels_identical = e.size == a.size and expected_pixels == actual_pixels
        pixel_record = dict(size=list(a.size), expected_rgba_sha256=hashlib.sha256(expected_pixels).hexdigest(),
                            actual_rgba_sha256=hashlib.sha256(actual_pixels).hexdigest(), identical=pixels_identical)
    receipt = dict(ok=all(checks.values()), scope='all 218 continental cantons; analysis from frozen tables, not raw-to-HH reconstruction',
        checks=checks, png_pixels=pixel_record,
        environment=dict(python=sys.version, platform=platform.system(), machine=platform.machine(),
                         isolated_venv=True, user_site=False, requirements=versions,
                         module_origins_relative_to_venv=modules),
        source_fingerprint=digest(root/'tested_core.json'), elapsed_seconds=time.monotonic()-started,
        graphical_identity_note='SVG/PDF export timestamps and SVG identifiers may change; exact numerical bindings are required, PNG pixel identity is reported separately')
    (out/'REPRODUCTION_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    return 0 if receipt['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
