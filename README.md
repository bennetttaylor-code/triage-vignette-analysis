# Reportable Analysis Multiturn

This folder contains a reproducible analysis of GPT triage performance for 39 clinical vignettes from `Reportable Analysis (2).xlsx`. 

## Files

- `run_analysis.py`: regenerates all outputs from the source workbook
- `results/overall_summary.csv`: overall range-aware performance for `GPT Natural`, `GPTH Multiturn`, and reference-standard concordance
- `results/behavioral_health_summary.csv`: Behavioral Health subgroup summary for vignettes 28-35
- `results/subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health agreement, including Holm-adjusted p-values
- `results/vignette_level_comparison.csv`: vignette-level comparison labels and directional error magnitudes for both model outputs
