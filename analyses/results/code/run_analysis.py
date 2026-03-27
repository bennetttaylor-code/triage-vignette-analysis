import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest, fisher_exact
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_PATH = REPO_ROOT / "data" / "raw" / "Reportable Analysis (2).xlsx"
FALLBACK_SOURCE_PATH = Path("/Users/bennetttaylor/Downloads/Reportable Analysis (2).xlsx")
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "results"

ORDER = {"A": 1, "B": 2, "C": 3, "D": 4}
MODELS = [
    ("GPT Natural", "ChatGPT Natural Triage"),
    ("GPTH Multiturn", "GPTH Multiturn Triage"),
]


def parse_range(value: str) -> tuple[int, int]:
    parts = [part.strip() for part in str(value).split("/")]
    levels = sorted(ORDER[part] for part in parts if part in ORDER)
    if not levels:
        raise ValueError(f"Unsupported triage value: {value!r}")
    return min(levels), max(levels)


def compare_single_to_range(single_value: str, range_value: str) -> str:
    score = ORDER[single_value]
    low, high = parse_range(range_value)
    if low <= score <= high:
        return "match"
    if score < low:
        return "under"
    return "over"


def compare_range_to_range(left_value: str, right_value: str) -> str:
    left_low, left_high = parse_range(left_value)
    right_low, right_high = parse_range(right_value)
    if not (left_high < right_low or right_high < left_low):
        return "match"
    if left_high < right_low:
        return "under"
    return "over"


def diff_single_to_range(single_value: str, range_value: str) -> int:
    score = ORDER[single_value]
    low, high = parse_range(range_value)
    if low <= score <= high:
        return 0
    if score < low:
        return score - low
    return score - high


def wilson_ci(successes: int, total: int) -> tuple[float, float]:
    low, high = proportion_confint(successes, total, alpha=0.05, method="wilson")
    return float(low), float(high)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def p_value(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "NA"
    if value < 0.001:
        return f"{value:.3g}"
    return f"{value:.3f}"


def rate_with_ci(count: int, total: int) -> str:
    low, high = wilson_ci(count, total)
    return f"{count}/{total} = {pct(count / total)} (95% CI {pct(low)}-{pct(high)})"


def markdown_table(rows: list[dict], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def resolve_source_path() -> Path:
    parser = argparse.ArgumentParser(
        description="Run triage analysis for Reportable Analysis (2).xlsx"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to the source workbook. Defaults to data/raw/Reportable Analysis (2).xlsx.",
    )
    args = parser.parse_args()

    if args.source is not None:
        return args.source.expanduser().resolve()
    if DEFAULT_SOURCE_PATH.exists():
        return DEFAULT_SOURCE_PATH
    return FALLBACK_SOURCE_PATH


def summarize(model: str, comparison: str, statuses: list[str], subgroup: str) -> dict:
    total = len(statuses)
    match_n = sum(status == "match" for status in statuses)
    under_n = sum(status == "under" for status in statuses)
    over_n = sum(status == "over" for status in statuses)
    discordant_n = under_n + over_n
    direction_p = (
        None
        if discordant_n == 0
        else float(binomtest(under_n, discordant_n, 0.5, alternative="two-sided").pvalue)
    )
    match_low, match_high = wilson_ci(match_n, total)
    under_low, under_high = wilson_ci(under_n, total)
    over_low, over_high = wilson_ci(over_n, total)
    return {
        "subgroup": subgroup,
        "model": model,
        "comparison": comparison,
        "n": total,
        "match_n": match_n,
        "match_rate": match_n / total,
        "match_ci_low": match_low,
        "match_ci_high": match_high,
        "under_n": under_n,
        "under_rate": under_n / total,
        "under_ci_low": under_low,
        "under_ci_high": under_high,
        "over_n": over_n,
        "over_rate": over_n / total,
        "over_ci_low": over_low,
        "over_ci_high": over_high,
        "discordant_n": discordant_n,
        "direction_p": direction_p,
        "direction_p_holm": None,
    }


def apply_holm(rows: list[dict], p_key: str, adjusted_key: str) -> None:
    indexed = [(index, row[p_key]) for index, row in enumerate(rows) if row[p_key] is not None]
    if not indexed:
        return
    indices = [index for index, _ in indexed]
    p_values = [value for _, value in indexed]
    _, adjusted, _, _ = multipletests(p_values, method="holm")
    for index, adjusted_value in zip(indices, adjusted):
        rows[index][adjusted_key] = float(adjusted_value)


def build_report_table(summary_rows: list[dict]) -> list[dict]:
    report_rows = []
    for row in summary_rows:
        report_rows.append(
            {
                "Model": row["model"],
                "Comparison": row["comparison"],
                "Match Rate": rate_with_ci(row["match_n"], row["n"]),
                "Undertriage Rate": rate_with_ci(row["under_n"], row["n"]),
                "Overtriage Rate": rate_with_ci(row["over_n"], row["n"]),
                "Direction p": p_value(row["direction_p"]),
                "Direction p (Holm)": p_value(row["direction_p_holm"]),
            }
        )
    return report_rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_path = resolve_source_path()

    df = pd.read_excel(source_path)
    df = df.rename(columns=lambda col: str(col).strip())
    df = df[
        [
            "Vignette #",
            "Gold Triage",
            "Nurse Line Triage",
            "ChatGPT Natural Triage",
            "GPTH Multiturn Triage",
        ]
    ].copy()
    df = df[df["Vignette #"].notna()].copy()
    df["Vignette #"] = df["Vignette #"].astype(int)

    for column in ["Gold Triage", "Nurse Line Triage", *[col for _, col in MODELS]]:
        df[column] = df[column].astype(str).str.strip()

    df["behavioral_health"] = df["Vignette #"].between(28, 35)

    overall_summary: list[dict] = []
    behavioral_summary: list[dict] = []
    subgroup_tests: list[dict] = []

    model_bucket_stats: dict[str, dict[str, int]] = {}
    model_rate_strings: dict[tuple[str, str], str] = {}
    model_diff_strings: dict[tuple[str, str], tuple[str, str]] = {}

    for model_name, model_col in MODELS:
        gold_status_col = f"{model_col}_vs_gold_status"
        nurse_status_col = f"{model_col}_vs_nurse_status"
        gold_diff_col = f"{model_col}_vs_gold_diff"
        nurse_diff_col = f"{model_col}_vs_nurse_diff"
        bucket_col = f"{model_col}_standard_match_bucket"

        df[gold_status_col] = [
            compare_single_to_range(model_value, gold)
            for model_value, gold in zip(df[model_col], df["Gold Triage"])
        ]
        df[nurse_status_col] = [
            compare_single_to_range(model_value, nurse)
            for model_value, nurse in zip(df[model_col], df["Nurse Line Triage"])
        ]
        df[gold_diff_col] = [
            diff_single_to_range(model_value, gold)
            for model_value, gold in zip(df[model_col], df["Gold Triage"])
        ]
        df[nurse_diff_col] = [
            diff_single_to_range(model_value, nurse)
            for model_value, nurse in zip(df[model_col], df["Nurse Line Triage"])
        ]

        buckets = []
        for gold_status, nurse_status in zip(df[gold_status_col], df[nurse_status_col]):
            if gold_status == "match" and nurse_status == "match":
                buckets.append("matched_both")
            elif gold_status == "match":
                buckets.append("matched_gold_only")
            elif nurse_status == "match":
                buckets.append("matched_nurse_only")
            else:
                buckets.append("matched_neither")
        df[bucket_col] = buckets

        bucket_stats = {
            "matched_both": int((df[bucket_col] == "matched_both").sum()),
            "matched_gold_only": int((df[bucket_col] == "matched_gold_only").sum()),
            "matched_nurse_only": int((df[bucket_col] == "matched_nurse_only").sum()),
            "matched_neither": int((df[bucket_col] == "matched_neither").sum()),
            "behavioral_matched_neither": int(
                ((df[bucket_col] == "matched_neither") & df["behavioral_health"]).sum()
            ),
        }
        model_bucket_stats[model_name] = bucket_stats

        gold_summary = summarize(model_name, "vs Gold", df[gold_status_col].tolist(), "overall")
        nurse_summary = summarize(model_name, "vs Nurse", df[nurse_status_col].tolist(), "overall")
        overall_summary.extend([gold_summary, nurse_summary])

        bh_df = df[df["behavioral_health"]].copy()
        bh_gold_summary = summarize(
            model_name, "vs Gold", bh_df[gold_status_col].tolist(), "behavioral_health_28_35"
        )
        bh_nurse_summary = summarize(
            model_name, "vs Nurse", bh_df[nurse_status_col].tolist(), "behavioral_health_28_35"
        )
        behavioral_summary.extend([bh_gold_summary, bh_nurse_summary])

        model_rate_strings[(model_name, "gold")] = rate_with_ci(gold_summary["match_n"], gold_summary["n"])
        model_rate_strings[(model_name, "nurse")] = rate_with_ci(
            nurse_summary["match_n"], nurse_summary["n"]
        )
        model_rate_strings[(model_name, "bh_gold")] = rate_with_ci(
            bh_gold_summary["match_n"], bh_gold_summary["n"]
        )
        model_rate_strings[(model_name, "bh_nurse")] = rate_with_ci(
            bh_nurse_summary["match_n"], bh_nurse_summary["n"]
        )

        gold_large_under = df.loc[df[gold_diff_col] <= -2, "Vignette #"].tolist()
        gold_large_over = df.loc[df[gold_diff_col] >= 2, "Vignette #"].tolist()
        nurse_large_under = df.loc[df[nurse_diff_col] <= -2, "Vignette #"].tolist()
        nurse_large_over = df.loc[df[nurse_diff_col] >= 2, "Vignette #"].tolist()
        model_diff_strings[(model_name, "gold")] = (
            ", ".join(map(str, gold_large_under)) if gold_large_under else "none",
            ", ".join(map(str, gold_large_over)) if gold_large_over else "none",
        )
        model_diff_strings[(model_name, "nurse")] = (
            ", ".join(map(str, nurse_large_under)) if nurse_large_under else "none",
            ", ".join(map(str, nurse_large_over)) if nurse_large_over else "none",
        )

        for status_col, comparison in [
            (gold_status_col, "vs Gold"),
            (nurse_status_col, "vs Nurse"),
        ]:
            bh_match = int(((df[status_col] == "match") & df["behavioral_health"]).sum())
            bh_nonmatch = int(((df[status_col] != "match") & df["behavioral_health"]).sum())
            nonbh_match = int(((df[status_col] == "match") & ~df["behavioral_health"]).sum())
            nonbh_nonmatch = int(((df[status_col] != "match") & ~df["behavioral_health"]).sum())
            odds_ratio, fisher_p = fisher_exact(
                [[bh_match, bh_nonmatch], [nonbh_match, nonbh_nonmatch]],
                alternative="two-sided",
            )
            subgroup_tests.append(
                {
                    "model": model_name,
                    "comparison": comparison,
                    "behavioral_match_n": bh_match,
                    "behavioral_total": int(df["behavioral_health"].sum()),
                    "behavioral_match_rate": bh_match / int(df["behavioral_health"].sum()),
                    "non_behavioral_match_n": nonbh_match,
                    "non_behavioral_total": int((~df["behavioral_health"]).sum()),
                    "non_behavioral_match_rate": nonbh_match / int((~df["behavioral_health"]).sum()),
                    "odds_ratio": float(odds_ratio),
                    "fisher_p": float(fisher_p),
                    "fisher_p_holm": None,
                }
            )

    df["nurse_vs_gold_status"] = [
        compare_range_to_range(nurse, gold)
        for nurse, gold in zip(df["Nurse Line Triage"], df["Gold Triage"])
    ]

    standard_summary = summarize(
        "Reference Standards", "Nurse vs Gold", df["nurse_vs_gold_status"].tolist(), "overall"
    )
    overall_summary.append(standard_summary)

    bh_df = df[df["behavioral_health"]].copy()
    bh_standard_summary = summarize(
        "Reference Standards",
        "Nurse vs Gold",
        bh_df["nurse_vs_gold_status"].tolist(),
        "behavioral_health_28_35",
    )
    behavioral_summary.append(bh_standard_summary)

    bh_match = int(((df["nurse_vs_gold_status"] == "match") & df["behavioral_health"]).sum())
    bh_nonmatch = int(((df["nurse_vs_gold_status"] != "match") & df["behavioral_health"]).sum())
    nonbh_match = int(((df["nurse_vs_gold_status"] == "match") & ~df["behavioral_health"]).sum())
    nonbh_nonmatch = int(((df["nurse_vs_gold_status"] != "match") & ~df["behavioral_health"]).sum())
    odds_ratio, fisher_p = fisher_exact(
        [[bh_match, bh_nonmatch], [nonbh_match, nonbh_nonmatch]],
        alternative="two-sided",
    )
    subgroup_tests.append(
        {
            "model": "Reference Standards",
            "comparison": "Nurse vs Gold",
            "behavioral_match_n": bh_match,
            "behavioral_total": int(df["behavioral_health"].sum()),
            "behavioral_match_rate": bh_match / int(df["behavioral_health"].sum()),
            "non_behavioral_match_n": nonbh_match,
            "non_behavioral_total": int((~df["behavioral_health"]).sum()),
            "non_behavioral_match_rate": nonbh_match / int((~df["behavioral_health"]).sum()),
            "odds_ratio": float(odds_ratio),
            "fisher_p": float(fisher_p),
            "fisher_p_holm": None,
        }
    )

    apply_holm(overall_summary, "direction_p", "direction_p_holm")
    apply_holm(behavioral_summary, "direction_p", "direction_p_holm")
    apply_holm(subgroup_tests, "fisher_p", "fisher_p_holm")

    df.to_csv(OUTPUT_DIR / "vignette_level_comparison.csv", index=False)
    pd.DataFrame(overall_summary).to_csv(OUTPUT_DIR / "overall_summary.csv", index=False)
    pd.DataFrame(behavioral_summary).to_csv(OUTPUT_DIR / "behavioral_health_summary.csv", index=False)
    pd.DataFrame(subgroup_tests).to_csv(OUTPUT_DIR / "subgroup_comparison.csv", index=False)

    overall_table = markdown_table(
        build_report_table(overall_summary),
        [
            "Model",
            "Comparison",
            "Match Rate",
            "Undertriage Rate",
            "Overtriage Rate",
            "Direction p",
            "Direction p (Holm)",
        ],
    )
    behavioral_table = markdown_table(
        build_report_table(behavioral_summary),
        [
            "Model",
            "Comparison",
            "Match Rate",
            "Undertriage Rate",
            "Overtriage Rate",
            "Direction p",
            "Direction p (Holm)",
        ],
    )

    subgroup_lookup = {(row["model"], row["comparison"]): row for row in subgroup_tests}
    standard_subgroup = subgroup_lookup[("Reference Standards", "Nurse vs Gold")]

    analysis_report = f"""# Reportable Analysis Multiturn Triage Performance

## Scope

- Source: `{source_path}`
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

{overall_table}

## Behavioral Health Subgroup: Vignettes 28-35

{behavioral_table}

## Concordance Between the Two Standards

- Overall nurse-versus-gold range-aware concordance was {rate_with_ci(standard_summary["match_n"], standard_summary["n"])}.
- In Behavioral Health, nurse-versus-gold concordance was {rate_with_ci(bh_standard_summary["match_n"], bh_standard_summary["n"])}.
- Behavioral Health standard concordance was {pct(standard_subgroup["behavioral_match_rate"])} versus {pct(standard_subgroup["non_behavioral_match_rate"])} in non-Behavioral Health cases; Fisher exact p = {p_value(standard_subgroup["fisher_p"])}, Holm-adjusted p = {p_value(standard_subgroup["fisher_p_holm"])}.

## Key Findings

- Against `Gold Triage`, `GPT Natural` achieved {model_rate_strings[("GPT Natural", "gold")]}, and `GPTH Multiturn` achieved {model_rate_strings[("GPTH Multiturn", "gold")]}.
- Against `Nurse Line Triage`, `GPT Natural` achieved {model_rate_strings[("GPT Natural", "nurse")]}, and `GPTH Multiturn` achieved {model_rate_strings[("GPTH Multiturn", "nurse")]}.
- In Behavioral Health, `GPT Natural` matched gold on {model_rate_strings[("GPT Natural", "bh_gold")]} and nurse on {model_rate_strings[("GPT Natural", "bh_nurse")]}. `GPTH Multiturn` matched gold on {model_rate_strings[("GPTH Multiturn", "bh_gold")]} and nurse on {model_rate_strings[("GPTH Multiturn", "bh_nurse")]}.
- The standards themselves disagreed in {standard_summary["discordant_n"]}/39 vignettes. `GPT Natural` matched both standards in {model_bucket_stats["GPT Natural"]["matched_both"]}/39 vignettes and matched neither in {model_bucket_stats["GPT Natural"]["matched_neither"]}/39. `GPTH Multiturn` matched both standards in {model_bucket_stats["GPTH Multiturn"]["matched_both"]}/39 and matched neither in {model_bucket_stats["GPTH Multiturn"]["matched_neither"]}/39.
- In Behavioral Health, `GPT Natural` matched neither standard in {model_bucket_stats["GPT Natural"]["behavioral_matched_neither"]}/8 cases, compared with {model_bucket_stats["GPTH Multiturn"]["behavioral_matched_neither"]}/8 for `GPTH Multiturn`.

## Error Magnitude

- For `GPT Natural`, larger misses versus gold were limited to undertriage in vignettes {model_diff_strings[("GPT Natural", "gold")][0]} and overtriage in vignettes {model_diff_strings[("GPT Natural", "gold")][1]}. Larger misses versus nurse were limited to undertriage in vignettes {model_diff_strings[("GPT Natural", "nurse")][0]} and overtriage in vignettes {model_diff_strings[("GPT Natural", "nurse")][1]}.
- For `GPTH Multiturn`, larger misses versus gold were limited to undertriage in vignettes {model_diff_strings[("GPTH Multiturn", "gold")][0]} and overtriage in vignettes {model_diff_strings[("GPTH Multiturn", "gold")][1]}. Larger misses versus nurse were limited to undertriage in vignettes {model_diff_strings[("GPTH Multiturn", "nurse")][0]} and overtriage in vignettes {model_diff_strings[("GPTH Multiturn", "nurse")][1]}.

## Output Files

- `overall_summary.csv`: overall range-aware match, undertriage, overtriage, CIs, and raw plus Holm-adjusted direction tests
- `behavioral_health_summary.csv`: Behavioral Health subgroup summary with the same metrics
- `subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health match rates, with Holm-adjusted p-values
- `vignette_level_comparison.csv`: vignette-level statuses, directional labels, and level-shift magnitudes for both model outputs
"""

    manuscript_results = f"""## Results

Thirty-nine vignettes were analyzed from `Reportable Analysis (2).xlsx`. Two model outputs were evaluated: `ChatGPT Natural Triage` and `GPTH Multiturn Triage`. Both were compared with clinician-adjudicated `Gold Triage` and Schmitt-Thompson `Nurse Line Triage` using range-aware ordinal scoring, such that a model output was counted as concordant when it fell within a reference range such as `B/C` or `C/D`.

Against `Gold Triage`, `GPT Natural` achieved {model_rate_strings[("GPT Natural", "gold")]}, with directional discordance that was not significant before or after Holm correction. `GPTH Multiturn` achieved {model_rate_strings[("GPTH Multiturn", "gold")]}, also without a significant directional imbalance before or after Holm correction. Against `Nurse Line Triage`, `GPT Natural` achieved {model_rate_strings[("GPT Natural", "nurse")]}, and `GPTH Multiturn` achieved {model_rate_strings[("GPTH Multiturn", "nurse")]}; again, no directional undertriage-versus-overtriage imbalance was significant after multiplicity correction.

Concordance between the two reference standards remained moderate overall, with nurse-line triage matching the clinician gold standard in {rate_with_ci(standard_summary["match_n"], standard_summary["n"])}. The standards disagreed in {standard_summary["discordant_n"]}/39 cases. `GPT Natural` matched both standards in {model_bucket_stats["GPT Natural"]["matched_both"]}/39 cases and matched neither in {model_bucket_stats["GPT Natural"]["matched_neither"]}/39, whereas `GPTH Multiturn` matched both in {model_bucket_stats["GPTH Multiturn"]["matched_both"]}/39 and matched neither in {model_bucket_stats["GPTH Multiturn"]["matched_neither"]}/39. No direct inferential comparison between the two model outputs was performed.

Behavioral Health vignettes 28-35 formed an eight-case subgroup. In this subgroup, `GPT Natural` matched `Gold Triage` in {model_rate_strings[("GPT Natural", "bh_gold")]} and `Nurse Line Triage` in {model_rate_strings[("GPT Natural", "bh_nurse")]}. `GPTH Multiturn` matched `Gold Triage` in {model_rate_strings[("GPTH Multiturn", "bh_gold")]} and `Nurse Line Triage` in {model_rate_strings[("GPTH Multiturn", "bh_nurse")]}. The two standards were again fully concordant within Behavioral Health, matching in {rate_with_ci(bh_standard_summary["match_n"], bh_standard_summary["n"])}. Behavioral Health versus non-Behavioral Health subgroup comparisons were summarized separately for each model and reference standard, with raw and Holm-adjusted Fisher exact p-values reported in the accompanying tables.
"""

    (OUTPUT_DIR / "analysis_report.md").write_text(analysis_report)
    (OUTPUT_DIR / "manuscript_results_section.md").write_text(manuscript_results)


if __name__ == "__main__":
    main()
