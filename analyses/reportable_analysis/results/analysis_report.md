# Reportable Analysis Triage Performance

## Scope

- Source: `/Users/bennetttaylor/Downloads/Reportable Analysis.xlsx`
- Sheet analyzed: `Sheet1`
- Vignettes analyzed: 39
- GPT model analyzed: `ChatGPT Natural Triage`
- Reference standards:
  - `Gold Triage`: clinician adjudication
  - `Nurse Line Triage`: Schmitt-Thompson protocol triage
- Behavioral Health subgroup: vignettes 28-35

## Scoring Rules

- Triage levels were treated as ordered: `A < B < C < D`.
- Range-aware matching counted GPT as concordant when the GPT level fell within a standard range such as `A/B`, `B/C`, or `C/D`.
- Undertriage was defined as GPT below the minimum acceptable level of the standard range.
- Overtriage was defined as GPT above the maximum acceptable level of the standard range.
- Standard-to-standard concordance was scored range-aware as well: the nurse-line label counted as concordant with gold if it fell inside the gold range.
- Confidence intervals are 95% Wilson intervals.
- Directional significance uses a two-sided exact binomial test on discordant cases only.
- Behavioral Health versus non-Behavioral Health comparisons use two-sided Fisher exact tests.
- Holm correction was applied within each family of related inferential tests: the three overall directional tests, the three Behavioral Health directional tests, and the three Behavioral Health versus non-Behavioral Health subgroup comparisons.

## Overall Performance

| Comparison | Match Rate | Undertriage Rate | Overtriage Rate | Direction p | Direction p (Holm) |
| --- | --- | --- | --- | --- | --- |
| GPT vs Gold | 23/39 = 59.0% (95% CI 43.4%-72.9%) | 9/39 = 23.1% (95% CI 12.6%-38.3%) | 7/39 = 17.9% (95% CI 9.0%-32.7%) | 0.804 | 1.000 |
| GPT vs Nurse | 23/39 = 59.0% (95% CI 43.4%-72.9%) | 10/39 = 25.6% (95% CI 14.6%-41.1%) | 6/39 = 15.4% (95% CI 7.2%-29.7%) | 0.454 | 1.000 |
| Nurse vs Gold | 25/39 = 64.1% (95% CI 48.4%-77.3%) | 8/39 = 20.5% (95% CI 10.8%-35.5%) | 6/39 = 15.4% (95% CI 7.2%-29.7%) | 0.791 | 1.000 |

## Behavioral Health Subgroup: Vignettes 28-35

| Comparison | Match Rate | Undertriage Rate | Overtriage Rate | Direction p | Direction p (Holm) |
| --- | --- | --- | --- | --- | --- |
| GPT vs Gold | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 2/8 = 25.0% (95% CI 7.1%-59.1%) | 1.000 | 1.000 |
| GPT vs Nurse | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 2/8 = 25.0% (95% CI 7.1%-59.1%) | 1.000 | 1.000 |
| Nurse vs Gold | 8/8 = 100.0% (95% CI 67.6%-100.0%) | 0/8 = 0.0% (95% CI 0.0%-32.4%) | 0/8 = 0.0% (95% CI 0.0%-32.4%) | NA | NA |

## Concordance Between the Two Standards

- Overall nurse-versus-gold range-aware concordance was 25/39 = 64.1% (95% CI 48.4%-77.3%).
- In Behavioral Health, nurse-versus-gold concordance was 8/8 = 100.0% (95% CI 67.6%-100.0%).
- Behavioral Health standard concordance was higher than non-Behavioral Health concordance: 100.0% vs 54.8%; Fisher exact p = 0.034, Holm-adjusted p = 0.101.

## Key Findings

- GPT achieved the same overall range-aware match rate against both standards: 23/39 = 59.0% (95% CI 43.4%-72.9%) against gold and 23/39 = 59.0% (95% CI 43.4%-72.9%) against nurse.
- Undertriage was numerically more frequent than overtriage against both standards, but the directional imbalance was not statistically significant before or after Holm correction.
- The standards themselves disagreed in 14/39 vignettes. When they disagreed, GPT split evenly between the two references: 8 gold-only matches and 8 nurse-only matches.
- GPT matched both standards in 15/39 vignettes and matched neither standard in 8/39 vignettes.
- Behavioral Health was the weakest GPT subgroup, with only 3/8 = 37.5% (95% CI 13.7%-69.4%) agreement against gold and the same 3/8 = 37.5% (95% CI 13.7%-69.4%) agreement against nurse.
- GPT agreement in Behavioral Health was lower than in the other 31 vignettes, but that difference was not statistically significant: 37.5% vs 64.5%; Fisher exact p = 0.235, Holm-adjusted p = 0.470.
- Because gold and nurse were perfectly concordant in Behavioral Health, GPT's five Behavioral Health misses all represent departures from both standards. Those five misses included 3 undertriage cases and 2 overtriage cases, all by a single triage level. GPT matched neither standard in 5/8 Behavioral Health vignettes.

## Error Magnitude

- Against gold, most discordances were one-level shifts. Larger misses were limited to undertriage in vignettes 13 and overtriage in vignettes 17, 19, 20.
- Against nurse, larger misses were limited to undertriage in vignettes 5, 13 and overtriage in vignette 19.

## Output Files

- `overall_summary.csv`: overall range-aware match, undertriage, overtriage, CIs, and raw plus Holm-adjusted direction tests
- `behavioral_health_summary.csv`: Behavioral Health subgroup summary with the same metrics
- `subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health match rates, with Holm-adjusted p-values
- `vignette_level_comparison.csv`: vignette-level statuses, directional labels, and level-shift magnitudes
