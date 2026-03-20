# Triage Analysis

This repository contains a reproducible analysis of GPT-based triage recommendations for 39 clinical vignettes against two reference standards:

- `CAV Triage`: clinician adjudication
- `Nurse Line Triage`: Schmitt-Thompson protocol triage

The current repository includes a finalized analysis package:

- `analyses/reportable_analysis_multiturn/`: workbook-based analysis of `GPT Natural` and `GPTH Multiturn`

## Repository Layout

```text
triage-analysis/
├── README.md
├── .gitignore
├── requirements.txt
├── analyses/
│   └── reportable_analysis_multiturn/
├── data/
│   ├── raw/
│   └── processed/
└── docs/
    └── methods.md
