# Data dictionary and analytical grain

## Input snapshots

| File | Grain | Main fields |
|---|---|---|
| `means_own.csv`, `means_common.csv` | 218 cantons × five years per file | `code4`, `name`, `province`, `year`, annual/common support cell count, `mean_HH_lower`, `mean_HH_upper`, endpoint bands and classification |
| `bands_own.csv`, `bands_common.csv` | unit × year × band | `kind`, `unit`, `band`, guaranteed/possible counts, nominal ha, valid support count and percentages |
| `partition_own.csv`, `partition_common.csv` | unit × year | support, invalid intervals, four unambiguous band counts, between-band count/pairs |
| `utm.csv` | 218 cantons | `code4`, `name`, `in_strip`; only the code/name/strip flag is used in this analysis |

The band/partition snapshots include aggregate territory categories; the analysis selects only `kind=canton`. National subtotals and territory auxiliaries must not be added to the cantons again. Codes remain zero-padded strings. Years are indicator reference years, not CONALI boundary dates. The seven snapshots preserve original headers; the code documents the exact join.

## Definitions and units

- OWN: valid support of each year. COMMON: intersection of eligible cells across the five years; denominator fixed within each canton across dates.
- Band 1 [0,1): very low; band 2 [1,4): low; band 3 [4,15): moderate; band 4 [15,∞): high. Values exactly at 1/4/15 enter the band starting there.
- A cell interval belongs to a band with guaranteed membership when the whole interval falls inside; membership is possible when the interval intersects that band. Possible counts across bands may overlap. Guaranteed counts plus between-band cells form a disjoint partition.
- Percentages = 100 × relevant cell count / valid support cell count for the same unit/year/support. Nominal surface = 900 m² or 0.09 ha per grid cell; not cadastral/geodesic area. No average of cantonal percentages represents national surface.
- `mean_lower`, `mean_upper`: modeled mean endpoints, retained without replacing them by a midpoint.
- `robust_mean_distance`: max of the absolute cross-endpoint mean differences. A qualifying pair has two distinct cantons, unordered, and distance ≤ ε. It does not imply statistical/ecological equivalence.
- `high_gap_min_pp`: max(0, guaranteed_i − possible_j, guaranteed_j − possible_i), using the high-band percentages. Units: percentage points. This is conditional on model ranges, not a confidence bound relative to ground truth.
- ε values: 0.10/0.25/0.50 HH units; the primary descriptive analysis uses 0.25 and COMMON/2020. Extreme selection also requires the same single band for both means.
- `exclude_utm_strip`: drops all 32 flagged cantons (186 remain), not just their strip cells. It is an exclusion sensitivity, not a repaired or counterfactual UTM solution.
- Invalid intervals are not zero pressure. The frozen inputs used here contain none; the analysis stops if unexpected invalid intervals would make mean/surface supports incomparable.

## Regenerated outputs

`cantons_joined.csv` has all 2,180 canton-year-support rows and their four band memberships. `all_close_pairs.csv` contains all unordered pairs with robust distance ≤0.50 for each year/support. `robustness.csv` has 60 year/support/strip/ε contexts. `by_mean_band.csv` summarizes high-pressure share among cantons in each mean band; these canton summaries are unweighted. `own_common_comparison.csv` has 1,090 paired support comparisons. `fixed_primary_pair.csv` retains the selected 2020 pair across all dates/supports, including dates when it no longer qualifies as close.

The figure JSON records the exact 218-point cohort, compositions and 12 contexts bound to F7. Pair rows share cantons and must not be treated as independent observations. No private validation coordinates, human labels, API credentials or satellite pixels are included.
