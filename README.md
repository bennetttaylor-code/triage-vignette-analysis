# Triage Analysis

This repository contains reproducible analyses of GPT-based triage recommendations for 39 clinical vignettes against two reference standards:

- `CAV Triage`: clinician adjudication
- `Nurse Line Triage`: Schmitt-Thompson protocol triage

The current repository includes a finalized analysis package:

- `analyses/reportable_analysis_multiturn/`: workbook

## Repository Layout

```text
triage-analysis/
├── README.md
├── .gitignore
├── requirements.txt
├── analyses
│   └── reportable_analysis_multiturn/
├── data/
│   ├── raw/
│   └── processed/
```

## Data

Raw Excel workbooks are expected in `data/raw/` but are not committed by default.

Expected filenames:

- `data/raw/Reportable Analysis (2).xlsx`

The analysis script also accept a custom workbook path via `--source`.

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
python3 analyses/reportable_analysis_multiturn/run_analysis.py
```

Or with explicit workbook paths:

```bash
python3 analyses/reportable_analysis_multiturn/run_analysis.py --source "/path/to/Reportable Analysis (2).xlsx"
```

## Outputs

Each analysis folder contains:

- `run_analysis.py`: reproducible analysis script
- `results/*.csv`: summary tables and vignette-level outputs


