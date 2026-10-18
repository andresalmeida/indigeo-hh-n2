# National reproduction test — 2026-10-17

**Scope:** all 218 continental cantons, five reference years, OWN/COMMON; starting from the seven supplied frozen aggregate tables. Not a single-canton demo and not a raw-input-to-HH-raster computation.

A new CPython 3.13.0 venv on macOS arm64 had system site-packages disabled and no NumPy/Matplotlib before dependency installation. Eleven exact versions were installed from public package wheels with verified hashes. A reviewer copied the candidate to a new checkout outside the project SSD and invoked the documented entry point with `python -I -B`. Only one execution was used.

| Check | Result |
|---|---|
| Six complete CSV outputs | Byte-identical to expected outputs |
| National joined matrix | All 218 × 5 × 2 = 2,180 rows reproduced |
| Robustness table | All 60 contexts reproduced |
| Analytical summary | Identical apart from runtime metadata |
| Figure numerical content | All 218 points, two compositions and 12 robustness contexts identical |
| SVG, PDF and PNG | All generated |
| PNG decoded pixels | Identical RGBA content at 2160 × 3090 pixels |
| Scientific code/input core | Same fixed SHA-256 before and after |
| Visual review | Complete, legible, no clipping/overlap found |

`reproduction_receipt.json` preserves the machine-readable receipt, dependency versions and module origins relative to the venv. Full independent comparisons and first-run logs are retained in the separate preparation audit. SVG/PDF binary hashes differed; no binary-identity claim is made for those exporters. Numerical bindings and PNG pixels matched.

The test used an isolated Python environment, **not** an operating-system sandbox. It does not establish inability to access the SSD/network, portability to Windows/Linux, independent validity of the source data, thematic accuracy or observed temporal change. It establishes reproduction of the stated national analysis stage from the supplied snapshots.
