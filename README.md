cat > /Users/bennetttaylor/Documents/Playground/triage-analysis/analyses/reportable_analysis_multiturn/README.md <<'EOF'
# Reportable Analysis Multiturn

This folder contains a reproducible analysis of GPT triage performance for 39 clinical vignettes from `Reportable Analysis (2).xlsx`.

## Files

- `run_analysis.py`: regenerates all outputs from the source workbook
- `results/overall_summary.csv`: overall range-aware performance for `GPT Natural`, `GPTH Multiturn`, and reference-standard concordance
- `results/behavioral_health_summary.csv`: Behavioral Health subgroup summary for vignettes 28-35
- `results/subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health agreement, including Holm-adjusted p-values
- `results/vignette_level_comparison.csv`: vignette-level comparison labels and directional error magnitudes for both model outputs

## How to Regenerate

From the repository root:

```bash
python3.12 analyses/reportable_analysis_multiturn/run_analysis.py

Place Reportable Analysis (2).xlsx in data/raw/, or pass a custom workbook path with --source.

Notes
Range-aware scoring treats A < B < C < D.
A model output is counted as a match when its triage label falls within an allowable reference range such as B/C or C/D.
Undertriage means the model output is below the reference range; overtriage means it is above the reference range.
Confidence intervals are 95% Wilson intervals.
Raw and Holm-adjusted p-values are reported for the inferential tests.
Direct inferential comparison between GPT Natural and GPTH Multiturn is intentionally not included in this analysis package.
