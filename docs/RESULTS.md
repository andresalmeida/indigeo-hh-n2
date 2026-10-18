# Descriptive results and claim boundaries

HH N2-T v1.2 supplies five continental reference cuts (2014, 2016, 2018, 2020, 2022), summarized for 218 cantons. The continuous score remains primary. This repository also includes identified exploratory band-distribution analyses.

## Continental summaries

- F3 and `products/tables/levels.csv` show modeled levels on annual valid support. OWN support can vary, so these means must not be subtracted across years.
- F4 and `products/tables/differences.csv` show 872 modeled biennial differences on common support: 739 positive, 69 negative and 64 with conditional intervals including zero. Those intervals bound model scenarios, not confidence or observed change.
- F5 identifies 32 cantons affected by the UTM strip. Assignment sensitivities do not resolve the failed grid-crossing control.
- The 2020–2022 electrical input crosses VIIRS V2.1 to V2.2. Substitution of that band changes the sign state in 17 cantons; it does not isolate a causal version effect or supply a bridge.

## Aggregate benchmark

F6 describes 150 complete D0 parcels. Spearman association with the historical visual proxy is approximately 0.872 for SDG15 and 0.870 for N2. Paired resampling intervals for the difference include zero. Similar association does not establish equivalence, noninferiority, superiority or thematic accuracy. The maps are not independent predictions, and the sample is not a weighted estimate for Ecuador or its cantons.

R0 yields the same selection count of 529 as the article without establishing parcel identity, and does not reproduce Table 6 metrics. The local backup's statistic labeled “kappa” is tolerance agreement, not Cohen kappa; the exact computational origin of the article's statistic is not established here. Reasons for exclusions can overlap.

## Within-canton distributions

The executable analysis joins 218 cantons, five cuts and two supports (2,180 rows), retains all qualifying close-mean pairs and evaluates 60 robustness contexts. For 2020 COMMON support, Puebloviejo and Manta have robustly close means in the same band but high-pressure shares of 2.1741% and 22.0179%: a minimum gap of 19.8438 percentage points.

The selection rule chooses an extreme, not a representative pair. This illustrates information a mean cannot encode; it does not quantify ecological damage, locate patches or prove the mean wrong. Pairs share cantons and are not independent observations. See the frozen specification in `ANALYSIS_SPEC.md`.

## Common limitations

Independent temporal validation remains incomplete. Static inputs, MAATE edition semantics, VIIRS versions and the UTM transition constrain interpretation. Conditional model bounds and benchmark resampling intervals have different meanings; neither is total uncertainty. Galápagos, BR and future N2.5 work are outside this repository.
