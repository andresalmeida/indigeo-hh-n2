#!/usr/bin/env python3
"""Descriptive analysis from seven frozen CSV snapshots. No raster or service IO."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import statistics
import sys
from pathlib import Path

YEARS = (2014, 2016, 2018, 2020, 2022)
EPSILONS = (0.10, 0.25, 0.50)
NAMES = {1: 'Muy baja', 2: 'Baja', 3: 'Moderada', 4: 'Alta'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_inputs(root):
    provenance = json.loads((root / 'source_provenance.json').read_bytes())
    result = {}
    for item in provenance['sources']:
        data = (root / item['local_file']).read_bytes()
        require(sha(data) == item['sha256'] and len(data) == item['bytes'],
                f"Source identity: {item['local_file']}")
        result[Path(item['local_file']).name] = list(csv.DictReader(io.StringIO(data.decode('utf-8'))))
    require(len(result) == 7, 'Seven inputs required')
    return result, provenance


def unique(rows, key, label):
    indexed = {}
    for row in rows:
        k = key(row)
        require(k not in indexed, f'Duplicate {label}: {k}')
        indexed[k] = row
    return indexed


def joined_rows(inputs):
    utm = unique(inputs['utm.csv'], lambda r: r['code4'], 'UTM canton')
    require(len(utm) == 218, 'UTM census size')
    require(sum(r['in_strip'] == 'True' for r in utm.values()) == 32, 'UTM strip count')
    result = []
    for support in ('own', 'common'):
        means = unique(inputs[f'means_{support}.csv'],
                       lambda r: (r['code4'], int(r['year'])), 'mean')
        bands = unique([r for r in inputs[f'bands_{support}.csv'] if r['kind'] == 'canton'],
                       lambda r: (r['unit'], int(r['year']), int(r['band'])), 'band')
        partitions = unique([r for r in inputs[f'partition_{support}.csv'] if r['kind'] == 'canton'],
                            lambda r: (r['unit'], int(r['year'])), 'partition')
        expected = {(code, year) for code in utm for year in YEARS}
        require(set(means) == set(partitions) == expected, 'Complete mean/partition keys')
        require(set(bands) == {(c, y, b) for c, y in expected for b in range(1, 5)}, 'Complete band keys')
        for code, year in sorted(expected):
            a, p = means[code, year], partitions[code, year]
            require(a['name'] == utm[code]['name'], f'Name mismatch {code}')
            require(p['covers_the_whole_canton'] == 'True', 'Partial canton')
            n, invalid = int(p['valid_support_cells']), int(p['invalid_interval_cells'])
            total = int(p['support_cells'])
            require(n > 0 and total == n + invalid, 'Partition denominator')
            require(int(a[f'{support}_support']) == total, 'Mean/band support mismatch')
            # Input A has no separate mean for invalid intervals: do not silently compare unlike supports.
            require(invalid == 0, 'Unexpected invalid interval: methodology must be reconciled first')
            L, U = float(a['mean_HH_lower']), float(a['mean_HH_upper'])
            require(math.isfinite(L) and math.isfinite(U) and 0 <= L <= U, 'Mean endpoints')
            row = dict(support=support, code4=code, name=a['name'], province=a['province'],
                       year=year, in_utm_strip=utm[code]['in_strip'] == 'True',
                       mean_lower=L, mean_upper=U, mean_band_lower=int(a['band_lower']),
                       mean_band_upper=int(a['band_upper']), mean_classification=a['classification'],
                       support_cells=total, valid_support_cells=n, invalid_interval_cells=invalid,
                       between_bands_cells=int(p['between_bands_cells']))
            for b in range(1, 5):
                r = bands[code, year, b]
                require(r['covers_the_whole_canton'] == 'True', 'Partial band canton')
                require(int(r['valid_support_cells']) == n, 'Band denominator mismatch')
                g, possible = int(r['guaranteed_cells']), int(r['possible_cells'])
                require(0 <= g <= possible <= n, 'Invalid band counts')
                require(g == int(p[f'single_band_{b}_cells']), 'Guaranteed/partition mismatch')
                for kind, cells in [('guaranteed', g), ('possible', possible)]:
                    require(abs(float(r[f'{kind}_pct_of_valid']) - 100 * cells / n) < 1e-10,
                            'Percentage inconsistent with count')
                    require(abs(float(r[f'{kind}_ha']) - .09 * cells) < 1e-7, 'Nominal area mismatch')
                    row[f'band{b}_{kind}_cells'] = cells
                    row[f'band{b}_{kind}_pct'] = 100 * cells / n
            require(sum(row[f'band{b}_guaranteed_cells'] for b in range(1, 5)) + row['between_bands_cells'] == n,
                    'Single bands plus ambiguity must partition support')
            row['between_bands_pct'] = 100 * row['between_bands_cells'] / n
            result.append(row)
    for code in utm:
        require(len({r['valid_support_cells'] for r in result if r['code4'] == code and r['support'] == 'common'}) == 1,
                'COMMON denominator changes across years')
    return result


def quantile(values, fraction):
    if not values:
        return None
    vals = sorted(values)
    x = (len(vals) - 1) * fraction
    lo, hi = math.floor(x), math.ceil(x)
    return vals[lo] + (vals[hi] - vals[lo]) * (x - lo)


def pair_record(a, b):
    distance = max(abs(a['mean_lower'] - b['mean_upper']), abs(a['mean_upper'] - b['mean_lower']))
    if distance > max(EPSILONS):
        return None
    ag, ap = a['band4_guaranteed_pct'], a['band4_possible_pct']
    bg, bp = b['band4_guaranteed_pct'], b['band4_possible_pct']
    gap = max(0., ag - bp, bg - ap)
    max_gap = max(ap - bg, bp - ag)
    same = a['mean_band_lower'] == a['mean_band_upper'] == b['mean_band_lower'] == b['mean_band_upper']
    return dict(support=a['support'], year=a['year'], code_i=a['code4'], name_i=a['name'],
                code_j=b['code4'], name_j=b['name'], either_in_utm_strip=a['in_utm_strip'] or b['in_utm_strip'],
                robust_mean_distance=distance, same_single_mean_band=same,
                mean_band=a['mean_band_lower'] if same else '',
                mean_i_lower=a['mean_lower'], mean_i_upper=a['mean_upper'],
                mean_j_lower=b['mean_lower'], mean_j_upper=b['mean_upper'],
                high_i_guaranteed_pct=ag, high_i_possible_pct=ap,
                high_j_guaranteed_pct=bg, high_j_possible_pct=bp,
                high_gap_min_pp=gap, high_gap_max_pp=max_gap)


def rank_key(p):
    return (-p['high_gap_min_pp'], p['robust_mean_distance'], int(p['code_i']), int(p['code_j']))


def analyze(rows):
    pairs = []
    for support, year in itertools.product(('own', 'common'), YEARS):
        cohort = [r for r in rows if r['support'] == support and r['year'] == year]
        for a, b in itertools.combinations(cohort, 2):
            require(int(a['code4']) < int(b['code4']), 'Nonordered/duplicate pair')
            p = pair_record(a, b)
            if p is not None:
                pairs.append(p)
    robustness, band_summaries = [], []
    for support, year, excluded in itertools.product(('own', 'common'), YEARS, (False, True)):
        cohort = [r for r in rows if r['support'] == support and r['year'] == year
                  and (not excluded or not r['in_utm_strip'])]
        for band in range(1, 5):
            block = [r for r in cohort if r['mean_band_lower'] == r['mean_band_upper'] == band]
            g, p = [r['band4_guaranteed_pct'] for r in block], [r['band4_possible_pct'] for r in block]
            record = dict(support=support, year=year, exclude_utm_strip=excluded, mean_band=band,
                          mean_band_name=NAMES[band], cantons=len(block))
            for label, vals in [('guaranteed', g), ('possible', p)]:
                for qname, q in [('min', 0), ('q1', .25), ('median', .5), ('q3', .75), ('max', 1)]:
                    record[f'high_pct_{label}_{qname}'] = quantile(vals, q)
            band_summaries.append(record)
        for eps in EPSILONS:
            close = [p for p in pairs if p['support'] == support and p['year'] == year
                     and p['robust_mean_distance'] <= eps and (not excluded or not p['either_in_utm_strip'])]
            same = [p for p in close if p['same_single_mean_band']]
            selected = min(same, key=rank_key) if same else None
            record = dict(support=support, year=year, exclude_utm_strip=excluded, epsilon=eps,
                          cantons=len(cohort), unordered_close_pairs=len(close),
                          same_single_band_close_pairs=len(same),
                          max_gap_min_pp=selected['high_gap_min_pp'] if selected else None,
                          selected_code_i=selected['code_i'] if selected else '',
                          selected_code_j=selected['code_j'] if selected else '')
            for threshold in (1, 5, 10):
                record[f'close_pairs_gap_ge_{threshold}pp'] = sum(p['high_gap_min_pp'] >= threshold for p in close)
                record[f'same_band_pairs_gap_ge_{threshold}pp'] = sum(p['high_gap_min_pp'] >= threshold for p in same)
            robustness.append(record)
    primary = [p for p in pairs if p['support'] == 'common' and p['year'] == 2020
               and p['robust_mean_distance'] <= .25 and p['same_single_mean_band']]
    selected = min(primary, key=rank_key) if primary else None
    fixed_pair = []
    if selected:
        for support, year in itertools.product(('own', 'common'), YEARS):
            a = next(r for r in rows if r['support'] == support and r['year'] == year and r['code4'] == selected['code_i'])
            b = next(r for r in rows if r['support'] == support and r['year'] == year and r['code4'] == selected['code_j'])
            # Preserve the fixed pair even if it ceases to meet the maximum window.
            distance = max(abs(a['mean_lower'] - b['mean_upper']), abs(a['mean_upper'] - b['mean_lower']))
            ag, ap, bg, bp = (a['band4_guaranteed_pct'], a['band4_possible_pct'],
                              b['band4_guaranteed_pct'], b['band4_possible_pct'])
            fixed_pair.append(dict(support=support, year=year, code_i=a['code4'], code_j=b['code4'],
                                   robust_mean_distance=distance, meets_primary_proximity=distance <= .25,
                                   high_gap_min_pp=max(0., ag - bp, bg - ap), high_gap_max_pp=max(ap - bg, bp - ag)))
    support_comparison = []
    lookup = {(r['support'], r['code4'], r['year']): r for r in rows}
    for code, year in sorted({(r['code4'], r['year']) for r in rows}):
        own, common = lookup['own', code, year], lookup['common', code, year]
        support_comparison.append(dict(code4=code, year=year, name=own['name'],
              mean_class_unchanged=(own['mean_band_lower'], own['mean_band_upper']) == (common['mean_band_lower'], common['mean_band_upper']),
              mean_max_endpoint_shift=max(abs(own['mean_lower']-common['mean_lower']), abs(own['mean_upper']-common['mean_upper'])),
              high_pct_max_bound_shift_pp=max(abs(own['band4_guaranteed_pct']-common['band4_guaranteed_pct']),
                                             abs(own['band4_possible_pct']-common['band4_possible_pct'])),
              common_cells_removed_from_own=own['valid_support_cells'] - common['valid_support_cells']))
        require(support_comparison[-1]['common_cells_removed_from_own'] >= 0, 'COMMON larger than OWN')
    by_year = []
    for year in YEARS:
        block = [r for r in support_comparison if r['year'] == year]
        by_year.append(dict(year=year, cantons=len(block), mean_classes_changed=sum(not r['mean_class_unchanged'] for r in block),
                            high_bound_shift_max_pp=max(r['high_pct_max_bound_shift_pp'] for r in block),
                            high_bound_shift_median_pp=statistics.median(r['high_pct_max_bound_shift_pp'] for r in block),
                            mean_endpoint_shift_max=max(r['mean_max_endpoint_shift'] for r in block)))
    summary = dict(primary_year=2020, primary_support='common', primary_epsilon=.25,
                   selected_extreme_pair=selected, same_band_primary_pairs=len(primary),
                   fixed_pair=fixed_pair, support_comparison_by_year=by_year,
                   rows=len(rows), close_pairs_max_epsilon=len(pairs),
                   invalid_interval_cells=sum(r['invalid_interval_cells'] for r in rows),
                   inference='descriptive census of modeled outputs; not independent validation or observed change',
                   percent_denominator='valid support cells in the same canton, year and support',
                   pair_dependence='Pairs share cantons and are not independent observations',
                   band_summary_weighting='unweighted canton summaries; not national area shares')
    return pairs, robustness, band_summaries, support_comparison, summary


def write_csv(path, rows):
    require(bool(rows), f'Empty output {path.name}')
    with path.open('x', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); root = Path(__file__).resolve().parent
    inputs, provenance = read_inputs(root); rows = joined_rows(inputs)
    pairs, robustness, bands, support, summary = analyze(rows)
    args.out.mkdir(exist_ok=False)
    for name, data in [('cantons_joined', rows), ('all_close_pairs', pairs), ('robustness', robustness),
                       ('by_mean_band', bands), ('own_common_comparison', support), ('fixed_primary_pair', summary['fixed_pair'])]:
        write_csv(args.out / (name + '.csv'), data)
    summary['analysis_code_sha256'] = sha(Path(__file__).read_bytes())
    summary['source_provenance_sha256'] = sha((root/'source_provenance.json').read_bytes())
    summary['runtime'] = sys.version
    (args.out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
