# Reportable Analysis

This folder contains a reproducible analysis of GPT triage performance for 39 clinical vignettes from `Reportable Analysis.xlsx`.

## Files

- `run_analysis.py`: regenerates all outputs from the source workbook
- `results/analysis_report.md`: GitHub-ready full report with methods, tables, and interpretation
- `results/manuscript_results_section.md`: publication-style Results section
- `results/overall_summary.csv`: overall range-aware performance against gold and nurse standards
- `results/behavioral_health_summary.csv`: Behavioral Health subgroup summary for vignettes 28-35
- `results/subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health agreement, including Holm-adjusted p-values
- `results/vignette_level_comparison.csv`: vignette-level comparison labels and directional error magnitudes

## How to Regenerate

From the repository root:

```bash
python3 analyses/reportable_analysis/run_analysis.py
```

Place `Reportable Analysis.xlsx` in `data/raw/`, or pass a custom workbook path with `--source`.

## Notes

- Range-aware scoring treats `A < B < C < D`.
- GPT is counted as a match when its triage label falls within an allowable reference range such as `B/C` or `C/D`.
- Undertriage means GPT is below the reference range; overtriage means GPT is above it.
- Confidence intervals are 95% Wilson intervals.
- Raw and Holm-adjusted p-values are reported for the inferential tests.
