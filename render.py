#!/usr/bin/env python3
"""Standalone manuscript figure; interval endpoints are never replaced by midpoints."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'hh046_matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

PALETTE = {1: '#86b6ef', 2: '#3987e5', 3: '#1c5cab', 4: '#0d366b'}
GREY = '#878c91'
INK = '#22282e'


def read_csv(p):
    with p.open() as f:
        return list(csv.DictReader(f))


def frame(ax):
    ax.spines[['top', 'right']].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#9da3a8'); ax.spines[side].set_linewidth(.6)
    ax.tick_params(width=.6, length=3, labelsize=8)
    ax.set_axisbelow(True)


def main():
    a = argparse.ArgumentParser(); a.add_argument('--analysis', type=Path, required=True)
    a.add_argument('--out', type=Path, required=True); args = a.parse_args()
    S = json.loads((args.analysis / 'summary.json').read_text())
    rows = read_csv(args.analysis / 'cantons_joined.csv')
    R = read_csv(args.analysis / 'robustness.csv')
    selected = S['selected_extreme_pair']
    assert selected and selected['year'] == 2020 and selected['support'] == 'common'
    codes = (selected['code_i'], selected['code_j'])
    cohort = [r for r in rows if r['year'] == '2020' and r['support'] == 'common']
    focus = {r['code4']: r for r in cohort if r['code4'] in codes}
    assert len(cohort) == 218 and len(focus) == 2
    args.out.mkdir(exist_ok=False)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.labelsize': 9, 'axes.titlesize': 10,
                         'axes.titleweight': 'bold', 'text.color': INK,
                         'axes.labelcolor': INK, 'svg.fonttype': 'none',
                         'pdf.fonttype': 42, 'axes.unicode_minus': True})
    fig = plt.figure(figsize=(7.2, 10.3), facecolor='white')
    gs = fig.add_gridspec(3, 1, height_ratios=[3.4, 1.8, 2.1],
                          left=.16, right=.97, top=.885, bottom=.16, hspace=.70)
    fig.text(.025, .975, 'La distribución añade información a la media cantonal',
             fontsize=12, fontweight='bold', va='top')
    fig.text(.025, .95, 'HH N2-T v1.2 · 2020 · 218 cantones continentales · resultados del modelo',
             fontsize=8, color='#525a62', va='top')
    ax = fig.add_subplot(gs[0]); frame(ax)
    ax.set_title('A  Media HH y superficie de presión alta', loc='left', pad=10)
    ax.grid(axis='y', color='#e4e6e8', linewidth=.5)
    for r in cohort:
        if r['code4'] in codes:
            continue
        L, U = float(r['mean_lower']), float(r['mean_upper'])
        g, p = float(r['band4_guaranteed_pct']), float(r['band4_possible_pct'])
        strip = r['in_utm_strip'] == 'True'
        ax.errorbar(L, g, xerr=[[0.], [U-L]], yerr=[[0.], [p-g]],
                    fmt='^' if strip else 'o', ms=3.1, color=GREY,
                    mfc='white' if strip else GREY, mew=.6, alpha=.65,
                    ecolor='#aeb3b7', elinewidth=.55, capsize=0, zorder=2)
    for code, marker in zip(codes, ('s', 'D')):
        r = focus[code]
        L, U = float(r['mean_lower']), float(r['mean_upper'])
        g, p = float(r['band4_guaranteed_pct']), float(r['band4_possible_pct'])
        ax.errorbar(L, g, xerr=[[0.], [U-L]], yerr=[[0.], [p-g]], fmt=marker,
                    ms=6, color=PALETTE[4], ecolor=PALETTE[4], elinewidth=1.2, zorder=5)
        # Labels refer to the recorded lower endpoint, not an invented central estimate.
        label = f"{r['name'].title()}\n{g:.2f} % de superficie alta"
        target = (14.2, 8.5) if code == codes[0] else (13.1, 30.8)
        ax.annotate(label, (L, g), xytext=target, fontsize=8,
                    color=PALETTE[4], arrowprops={'arrowstyle': '-', 'lw': .7, 'color': PALETTE[4]},
                    bbox={'fc': 'white', 'ec': 'none', 'pad': 1.5})
    for x in (1, 4, 15):
        ax.axvline(x, color='#bfc4c8', linewidth=.6, ls=':', zorder=1)
    ax.set_xlim(0, 26); ax.set_ylim(0, 80)
    ax.set_xticks([0, 1, 4, 8, 12, 15, 20, 25])
    ax.set_xlabel('Media cantonal de HH (unidades de la receta)')
    ax.set_ylabel('Superficie alta, HH ≥ 15\n(% del soporte válido común)')
    ax.legend(handles=[Line2D([], [], marker='o', color='none', mfc=GREY, mec=GREY, ms=3.5,
                              label='Fuera de la franja UTM'),
                       Line2D([], [], marker='^', color='none', mfc='white', mec=GREY, ms=4,
                              label='Tocado por la franja UTM')],
              frameon=False, loc='upper left', fontsize=7.2, handletextpad=.5)

    axb = fig.add_subplot(gs[1]); frame(axb)
    axb.set_title('B  Mismo grupo de la media, distinta composición', loc='left', pad=13)
    labels = []
    for y, code in enumerate(codes):
        r = focus[code]; left = 0.
        for band in range(1, 5):
            value = float(r[f'band{band}_guaranteed_pct'])
            axb.barh(y, value, left=left, height=.43, color=PALETTE[band], edgecolor='white', linewidth=.5)
            if value >= 12:
                axb.text(left + value/2, y, f'{value:.2f} %', ha='center', va='center',
                         fontsize=8, color='white' if band >= 2 else INK)
            left += value
        ambiguous = float(r['between_bands_pct'])
        axb.barh(y, ambiguous, left=left, height=.43, color='#d7d5cf',
                 edgecolor='#666666', hatch='////', linewidth=.4)
        assert abs(left + ambiguous - 100.) < 1e-9
        L, U = float(r['mean_lower']), float(r['mean_upper'])
        labels.append(r['name'].title())
        axb.text(100, y-.31, 'Media HH [' + f'{L:.4f}; {U:.4f}' + '] · moderada',
                 ha='right', va='center', fontsize=7.5, color='#525a62')
    axb.set_yticks(range(2), labels, fontsize=8); axb.invert_yaxis()
    axb.set_ylim(1.5, -.65)
    axb.set_xlim(0, 100); axb.set_xticks([0, 25, 50, 75, 100])
    axb.set_xlabel('Superficie (% del soporte válido común)')
    handles = [Patch(fc=PALETTE[b], label=f'{b} {name}') for b, name in enumerate(['Muy baja', 'Baja', 'Moderada', 'Alta'], 1)]
    handles.append(Patch(fc='#d7d5cf', ec='#666666', hatch='////', label='Entre bandas'))
    axb.legend(handles=handles, frameon=False, fontsize=7, ncol=5,
               bbox_to_anchor=(.5, -.44), loc='upper center', handlelength=1.1, columnspacing=.8)

    axc = fig.add_subplot(gs[2]); frame(axc)
    axc.set_title('C  El contraste persiste al cambiar soporte y excluir la franja', loc='left', pad=12)
    configurations = [('common', False), ('own', False), ('common', True), ('own', True)]
    markers = {0.1: ('o', '#8e969d'), .25: ('D', PALETTE[4]), .5: ('s', '#3987e5')}
    used = []
    for y, (support, excluded) in enumerate(configurations):
        for eps, (marker, color) in markers.items():
            r = next(r for r in R if r['support'] == support and r['year'] == '2020'
                     and (r['exclude_utm_strip'] == 'True') == excluded and float(r['epsilon']) == eps)
            value = float(r['max_gap_min_pp']); used.append(r)
            axc.plot(value, y, marker=marker, ms=5.3, mfc='white' if eps == .1 else color,
                     mec=color, ls='none', zorder=3)
        axc.axhline(y, color='#edf0f2', lw=.6, zorder=1)
    axc.set_yticks(range(4), ['COMMON · 218', 'OWN · 218', 'COMMON · 186\nsin franja', 'OWN · 186\nsin franja'], fontsize=8)
    axc.invert_yaxis(); axc.set_ylim(3.5, -.5); axc.set_xlim(0, 25)
    axc.set_xticks([0, 5, 10, 15, 20, 25])
    axc.set_xlabel('Mayor brecha mínima de superficie alta (puntos porcentuales)')
    axc.legend(handles=[Line2D([], [], marker=m, ms=4.8, mfc='white' if e==.1 else c,
                              mec=c, ls='none', label=f'ε = {e:.2f}') for e,(m,c) in markers.items()],
               frameon=False, fontsize=7.5, ncol=3, bbox_to_anchor=(.60, .09),
               bbox_transform=fig.transFigure, loc='center')
    fig.text(.025, .025, 'Extremos condicionales del modelo; no intervalos de confianza.\n'
             'El par de B es un ejemplo extremo seleccionado mediante una regla explícita.\n'
             'Las bandas son descriptivas N2 y los porcentajes usan únicamente el soporte válido.',
             fontsize=7.2, color='#525a62', va='bottom', linespacing=1.4)
    fig.canvas.draw()
    exports = {}
    for ext in ('svg', 'pdf', 'png'):
        target = args.out / f'F7_mean_and_distribution.{ext}'
        fig.savefig(target, dpi=300, facecolor='white', metadata={'Creator': 'IndiGeo HH N2-T analysis046'})
        exports[ext] = {'file': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    plt.close(fig)
    record = {'primary_cohort': cohort, 'focus_codes': codes, 'robustness_panel': used,
              'selected_pair': selected, 'exports': exports,
              'source_analysis_summary_sha256': hashlib.sha256((args.analysis/'summary.json').read_bytes()).hexdigest(),
              'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'matplotlib_version': matplotlib.__version__, 'point_encoding': 'lower corner plus positive endpoint segments; never midpoint'}
    (args.out/'figure_data.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(exports, indent=2))


if __name__ == '__main__':
    main()
