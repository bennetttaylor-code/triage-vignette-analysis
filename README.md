# Triage Analysis

This repository contains reproducible analyses of GPT-based triage recommendations for 39 clinical vignettes against two reference standards:

- `Gold Triage`: clinician adjudication
- `Nurse Line Triage`: Schmitt-Thompson protocol triage

The current repository includes two finalized analysis packages:

- `analyses/reportable_analysis/`: original `ChatGPT Natural Triage` analysis
- `analyses/reportable_analysis_multiturn/`: updated workbook including `GPTH Multiturn Triage`

## Repository Layout

```text
triage-analysis/
├── README.md
├── .gitignore
├── requirements.txt
├── analyses/
│   ├── reportable_analysis/
│   └── reportable_analysis_multiturn/
├── data/
│   ├── raw/
│   └── processed/
└── docs/
    └── methods.md
```

## Data

Raw Excel workbooks are expected in `data/raw/` but are not committed by default.

Expected filenames:

- `data/raw/Reportable Analysis.xlsx`
- `data/raw/Reportable Analysis (2).xlsx`

Both analysis scripts also accept a custom workbook path via `--source`.

## Setup

Tested with Python `3.12.7`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Analyses

From the repository root:

```bash
python3 analyses/reportable_analysis/run_analysis.py
python3 analyses/reportable_analysis_multiturn/run_analysis.py
```

Or with explicit workbook paths:

```bash
python3 analyses/reportable_analysis/run_analysis.py --source "/path/to/Reportable Analysis.xlsx"
python3 analyses/reportable_analysis_multiturn/run_analysis.py --source "/path/to/Reportable Analysis (2).xlsx"
```

## Outputs

Each analysis folder contains:

- `run_analysis.py`: reproducible analysis script
- `results/analysis_report.md`: GitHub-ready narrative report
- `results/manuscript_results_section.md`: publication-style Results text
- `results/*.csv`: summary tables and vignette-level outputs

## Methods Summary

- Triage levels are treated as ordered: `A < B < C < D`
- Scoring is range-aware, so outputs within a reference range such as `B/C` are counted as matches
- Undertriage is below the reference range; overtriage is above it
- Confidence intervals are 95% Wilson intervals
- Directional imbalance tests use two-sided exact binomial tests on discordant cases
- Behavioral Health subgroup comparisons use two-sided Fisher exact tests
- Holm correction is applied within related families of inferential tests

Full wording for methods is in [docs/methods.md](/Users/bennetttaylor/Documents/Playground/triage-analysis/docs/methods.md).
