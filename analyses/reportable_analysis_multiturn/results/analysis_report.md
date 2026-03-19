# Reportable Analysis Multiturn Triage Performance

## Scope

- Source: `/Users/bennetttaylor/Downloads/Reportable Analysis (2).xlsx`
- Sheet analyzed: `Sheet1`
- Vignettes analyzed: 39
- Model outputs analyzed:
  - `ChatGPT Natural Triage`
  - `GPTH Multiturn Triage`
- Reference standards:
  - `Gold Triage`: clinician adjudication
  - `Nurse Line Triage`: Schmitt-Thompson protocol triage
- Behavioral Health subgroup: vignettes 28-35
- Direct inferential comparison between `GPT Natural` and `GPTH Multiturn` was not performed by design.

## Scoring Rules

- Triage levels were treated as ordered: `A < B < C < D`.
- Range-aware matching counted a model output as concordant when the model level fell within a standard range such as `A/B`, `B/C`, or `C/D`.
- Undertriage was defined as a model output below the minimum acceptable level of the standard range.
- Overtriage was defined as a model output above the maximum acceptable level of the standard range.
- Standard-to-standard concordance was scored range-aware as well: the nurse-line label counted as concordant with gold if it fell inside the gold range.
- Confidence intervals are 95% Wilson intervals.
- Directional significance uses a two-sided exact binomial test on discordant cases only.
- Behavioral Health versus non-Behavioral Health comparisons use two-sided Fisher exact tests.
- Holm correction was applied within each family of related inferential tests: the five overall directional tests, the five Behavioral Health directional tests, and the five Behavioral Health versus non-Behavioral Health subgroup comparisons.

## Overall Performance

| Model | Comparison | Match Rate | Undertriage Rate | Overtriage Rate | Direction p | Direction p (Holm) |
| --- | --- | --- | --- | --- | --- | --- |
| GPT Natural | vs Gold | 23/39 = 59.0% (95% CI 43.4%-72.9%) | 9/39 = 23.1% (95% CI 12.6%-38.3%) | 7/39 = 17.9% (95% CI 9.0%-32.7%) | 0.804 | 1.000 |
| GPT Natural | vs Nurse | 23/39 = 59.0% (95% CI 43.4%-72.9%) | 10/39 = 25.6% (95% CI 14.6%-41.1%) | 6/39 = 15.4% (95% CI 7.2%-29.7%) | 0.454 | 1.000 |
| GPTH Multiturn | vs Gold | 23/39 = 59.0% (95% CI 43.4%-72.9%) | 5/39 = 12.8% (95% CI 5.6%-26.7%) | 11/39 = 28.2% (95% CI 16.5%-43.8%) | 0.210 | 1.000 |
| GPTH Multiturn | vs Nurse | 21/39 = 53.8% (95% CI 38.6%-68.4%) | 6/39 = 15.4% (95% CI 7.2%-29.7%) | 12/39 = 30.8% (95% CI 18.6%-46.4%) | 0.238 | 1.000 |
| Reference Standards | Nurse vs Gold | 25/39 = 64.1% (95% CI 48.4%-77.3%) | 8/39 = 20.5% (95% CI 10.8%-35.5%) | 6/39 = 15.4% (95% CI 7.2%-29.7%) | 0.791 | 1.000 |

## Behavioral Health Subgroup: Vignettes 28-35

| Model | Comparison | Match Rate | Undertriage Rate | Overtriage Rate | Direction p | Direction p (Holm) |
| --- | --- | --- | --- | --- | --- | --- |
| GPT Natural | vs Gold | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 2/8 = 25.0% (95% CI 7.1%-59.1%) | 1.000 | 1.000 |
| GPT Natural | vs Nurse | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 3/8 = 37.5% (95% CI 13.7%-69.4%) | 2/8 = 25.0% (95% CI 7.1%-59.1%) | 1.000 | 1.000 |
| GPTH Multiturn | vs Gold | 4/8 = 50.0% (95% CI 21.5%-78.5%) | 0/8 = 0.0% (95% CI 0.0%-32.4%) | 4/8 = 50.0% (95% CI 21.5%-78.5%) | 0.125 | 0.375 |
| GPTH Multiturn | vs Nurse | 2/8 = 25.0% (95% CI 7.1%-59.1%) | 0/8 = 0.0% (95% CI 0.0%-32.4%) | 6/8 = 75.0% (95% CI 40.9%-92.9%) | 0.031 | 0.125 |
| Reference Standards | Nurse vs Gold | 8/8 = 100.0% (95% CI 67.6%-100.0%) | 0/8 = 0.0% (95% CI 0.0%-32.4%) | 0/8 = 0.0% (95% CI 0.0%-32.4%) | NA | NA |

## Concordance Between the Two Standards

- Overall nurse-versus-gold range-aware concordance was 25/39 = 64.1% (95% CI 48.4%-77.3%).
- In Behavioral Health, nurse-versus-gold concordance was 8/8 = 100.0% (95% CI 67.6%-100.0%).
- Behavioral Health standard concordance was 100.0% versus 54.8% in non-Behavioral Health cases; Fisher exact p = 0.034, Holm-adjusted p = 0.168.

## Key Findings

- Against `Gold Triage`, `GPT Natural` achieved 23/39 = 59.0% (95% CI 43.4%-72.9%), and `GPTH Multiturn` achieved 23/39 = 59.0% (95% CI 43.4%-72.9%).
- Against `Nurse Line Triage`, `GPT Natural` achieved 23/39 = 59.0% (95% CI 43.4%-72.9%), and `GPTH Multiturn` achieved 21/39 = 53.8% (95% CI 38.6%-68.4%).
- In Behavioral Health, `GPT Natural` matched gold on 3/8 = 37.5% (95% CI 13.7%-69.4%) and nurse on 3/8 = 37.5% (95% CI 13.7%-69.4%). `GPTH Multiturn` matched gold on 4/8 = 50.0% (95% CI 21.5%-78.5%) and nurse on 2/8 = 25.0% (95% CI 7.1%-59.1%).
- The standards themselves disagreed in 14/39 vignettes. `GPT Natural` matched both standards in 15/39 vignettes and matched neither in 8/39. `GPTH Multiturn` matched both standards in 13/39 and matched neither in 8/39.
- In Behavioral Health, `GPT Natural` matched neither standard in 5/8 cases, compared with 4/8 for `GPTH Multiturn`.

## Error Magnitude

- For `GPT Natural`, larger misses versus gold were limited to undertriage in vignettes 13 and overtriage in vignettes 17, 19, 20. Larger misses versus nurse were limited to undertriage in vignettes 5, 13 and overtriage in vignettes 19.
- For `GPTH Multiturn`, larger misses versus gold were limited to undertriage in vignettes 13 and overtriage in vignettes 5, 17, 19, 20. Larger misses versus nurse were limited to undertriage in vignettes 13 and overtriage in vignettes 16, 19.

## Output Files

- `overall_summary.csv`: overall range-aware match, undertriage, overtriage, CIs, and raw plus Holm-adjusted direction tests
- `behavioral_health_summary.csv`: Behavioral Health subgroup summary with the same metrics
- `subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health match rates, with Holm-adjusted p-values
- `vignette_level_comparison.csv`: vignette-level statuses, directional labels, and level-shift magnitudes for both model outputs
