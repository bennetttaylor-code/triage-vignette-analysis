import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest, fisher_exact
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.multitest import multipletests


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_PATH = REPO_ROOT / "data" / "raw" / "Reportable Analysis.xlsx"
FALLBACK_SOURCE_PATH = Path("/Users/bennetttaylor/Downloads/Reportable Analysis.xlsx")
OUTPUT_DIR = Path(__file__).resolve().parent / "results"

ORDER = {"A": 1, "B": 2, "C": 3, "D": 4}


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
    if value is None:
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
    parser = argparse.ArgumentParser(description="Run triage analysis for Reportable Analysis.xlsx")
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to the source workbook. Defaults to data/raw/Reportable Analysis.xlsx.",
    )
    args = parser.parse_args()

    if args.source is not None:
        return args.source.expanduser().resolve()
    if DEFAULT_SOURCE_PATH.exists():
        return DEFAULT_SOURCE_PATH
    return FALLBACK_SOURCE_PATH


def summarize(label: str, statuses: list[str], subgroup: str) -> dict:
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
        "comparison": label,
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
    df = df[["Vignette #", "Gold Triage", "Nurse Line Triage", "ChatGPT Natural Triage"]].copy()
    df = df[df["Vignette #"].notna()].copy()
    df["Vignette #"] = df["Vignette #"].astype(int)

    for column in ["Gold Triage", "Nurse Line Triage", "ChatGPT Natural Triage"]:
        df[column] = df[column].astype(str).str.strip()

    df["behavioral_health"] = df["Vignette #"].between(28, 35)
    df["gpt_vs_gold_status"] = [
        compare_single_to_range(gpt, gold)
        for gpt, gold in zip(df["ChatGPT Natural Triage"], df["Gold Triage"])
    ]
    df["gpt_vs_nurse_status"] = [
        compare_single_to_range(gpt, nurse)
        for gpt, nurse in zip(df["ChatGPT Natural Triage"], df["Nurse Line Triage"])
    ]
    df["nurse_vs_gold_status"] = [
        compare_range_to_range(nurse, gold)
        for nurse, gold in zip(df["Nurse Line Triage"], df["Gold Triage"])
    ]
    df["gpt_vs_gold_diff"] = [
        diff_single_to_range(gpt, gold)
        for gpt, gold in zip(df["ChatGPT Natural Triage"], df["Gold Triage"])
    ]
    df["gpt_vs_nurse_diff"] = [
        diff_single_to_range(gpt, nurse)
        for gpt, nurse in zip(df["ChatGPT Natural Triage"], df["Nurse Line Triage"])
    ]

    match_bucket = []
    for gold_status, nurse_status in zip(df["gpt_vs_gold_status"], df["gpt_vs_nurse_status"]):
        if gold_status == "match" and nurse_status == "match":
            match_bucket.append("matched_both")
        elif gold_status == "match":
            match_bucket.append("matched_gold_only")
        elif nurse_status == "match":
            match_bucket.append("matched_nurse_only")
        else:
            match_bucket.append("matched_neither")
    df["gpt_standard_match_bucket"] = match_bucket

    overall_summary = [
        summarize("GPT vs Gold", df["gpt_vs_gold_status"].tolist(), "overall"),
        summarize("GPT vs Nurse", df["gpt_vs_nurse_status"].tolist(), "overall"),
        summarize("Nurse vs Gold", df["nurse_vs_gold_status"].tolist(), "overall"),
    ]

    bh_df = df[df["behavioral_health"]].copy()
    behavioral_summary = [
        summarize("GPT vs Gold", bh_df["gpt_vs_gold_status"].tolist(), "behavioral_health_28_35"),
        summarize("GPT vs Nurse", bh_df["gpt_vs_nurse_status"].tolist(), "behavioral_health_28_35"),
        summarize("Nurse vs Gold", bh_df["nurse_vs_gold_status"].tolist(), "behavioral_health_28_35"),
    ]

    apply_holm(overall_summary, "direction_p", "direction_p_holm")
    apply_holm(behavioral_summary, "direction_p", "direction_p_holm")

    subgroup_tests = []
    for column, label in [
        ("gpt_vs_gold_status", "GPT vs Gold"),
        ("gpt_vs_nurse_status", "GPT vs Nurse"),
        ("nurse_vs_gold_status", "Nurse vs Gold"),
    ]:
        bh_match = int(((df[column] == "match") & df["behavioral_health"]).sum())
        bh_nonmatch = int(((df[column] != "match") & df["behavioral_health"]).sum())
        nonbh_match = int(((df[column] == "match") & ~df["behavioral_health"]).sum())
        nonbh_nonmatch = int(((df[column] != "match") & ~df["behavioral_health"]).sum())
        odds_ratio, fisher_p = fisher_exact(
            [[bh_match, bh_nonmatch], [nonbh_match, nonbh_nonmatch]],
            alternative="two-sided",
        )
        subgroup_tests.append(
            {
                "comparison": label,
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

    apply_holm(subgroup_tests, "fisher_p", "fisher_p_holm")

    df.to_csv(OUTPUT_DIR / "vignette_level_comparison.csv", index=False)
    pd.DataFrame(overall_summary).to_csv(OUTPUT_DIR / "overall_summary.csv", index=False)
    pd.DataFrame(behavioral_summary).to_csv(OUTPUT_DIR / "behavioral_health_summary.csv", index=False)
    pd.DataFrame(subgroup_tests).to_csv(OUTPUT_DIR / "subgroup_comparison.csv", index=False)

    overall_table = markdown_table(
        build_report_table(overall_summary),
        [
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
            "Comparison",
            "Match Rate",
            "Undertriage Rate",
            "Overtriage Rate",
            "Direction p",
            "Direction p (Holm)",
        ],
    )

    matched_both_n = int((df["gpt_standard_match_bucket"] == "matched_both").sum())
    matched_gold_only_n = int((df["gpt_standard_match_bucket"] == "matched_gold_only").sum())
    matched_nurse_only_n = int((df["gpt_standard_match_bucket"] == "matched_nurse_only").sum())
    matched_neither_n = int((df["gpt_standard_match_bucket"] == "matched_neither").sum())
    bh_matched_neither_n = int(
        ((df["gpt_standard_match_bucket"] == "matched_neither") & df["behavioral_health"]).sum()
    )

    gold_large_under = df.loc[df["gpt_vs_gold_diff"] <= -2, "Vignette #"].tolist()
    gold_large_over = df.loc[df["gpt_vs_gold_diff"] >= 2, "Vignette #"].tolist()
    nurse_large_under = df.loc[df["gpt_vs_nurse_diff"] <= -2, "Vignette #"].tolist()
    nurse_large_over = df.loc[df["gpt_vs_nurse_diff"] >= 2, "Vignette #"].tolist()

    bh_gpt_gold = behavioral_summary[0]
    bh_nurse_gold = behavioral_summary[2]
    bh_vs_non_gpt_gold = subgroup_tests[0]
    bh_vs_non_nurse_gold = subgroup_tests[2]

    analysis_report = f"""# Reportable Analysis Triage Performance

## Scope

- Source: `{source_path}`
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

{overall_table}

## Behavioral Health Subgroup: Vignettes 28-35

{behavioral_table}

## Concordance Between the Two Standards

- Overall nurse-versus-gold range-aware concordance was {rate_with_ci(overall_summary[2]["match_n"], overall_summary[2]["n"])}.
- In Behavioral Health, nurse-versus-gold concordance was {rate_with_ci(bh_nurse_gold["match_n"], bh_nurse_gold["n"])}.
- Behavioral Health standard concordance was higher than non-Behavioral Health concordance: {pct(bh_vs_non_nurse_gold["behavioral_match_rate"])} vs {pct(bh_vs_non_nurse_gold["non_behavioral_match_rate"])}; Fisher exact p = {p_value(bh_vs_non_nurse_gold["fisher_p"])}, Holm-adjusted p = {p_value(bh_vs_non_nurse_gold["fisher_p_holm"])}.

## Key Findings

- GPT achieved the same overall range-aware match rate against both standards: {rate_with_ci(overall_summary[0]["match_n"], overall_summary[0]["n"])} against gold and {rate_with_ci(overall_summary[1]["match_n"], overall_summary[1]["n"])} against nurse.
- Undertriage was numerically more frequent than overtriage against both standards, but the directional imbalance was not statistically significant before or after Holm correction.
- The standards themselves disagreed in {overall_summary[2]["discordant_n"]}/39 vignettes. When they disagreed, GPT split evenly between the two references: {matched_gold_only_n} gold-only matches and {matched_nurse_only_n} nurse-only matches.
- GPT matched both standards in {matched_both_n}/39 vignettes and matched neither standard in {matched_neither_n}/39 vignettes.
- Behavioral Health was the weakest GPT subgroup, with only {rate_with_ci(bh_gpt_gold["match_n"], bh_gpt_gold["n"])} agreement against gold and the same {rate_with_ci(behavioral_summary[1]["match_n"], behavioral_summary[1]["n"])} agreement against nurse.
- GPT agreement in Behavioral Health was lower than in the other 31 vignettes, but that difference was not statistically significant: {pct(bh_vs_non_gpt_gold["behavioral_match_rate"])} vs {pct(bh_vs_non_gpt_gold["non_behavioral_match_rate"])}; Fisher exact p = {p_value(bh_vs_non_gpt_gold["fisher_p"])}, Holm-adjusted p = {p_value(bh_vs_non_gpt_gold["fisher_p_holm"])}.
- Because gold and nurse were perfectly concordant in Behavioral Health, GPT's five Behavioral Health misses all represent departures from both standards. Those five misses included {behavioral_summary[0]["under_n"]} undertriage cases and {behavioral_summary[0]["over_n"]} overtriage cases, all by a single triage level. GPT matched neither standard in {bh_matched_neither_n}/8 Behavioral Health vignettes.

## Error Magnitude

- Against gold, most discordances were one-level shifts. Larger misses were limited to undertriage in vignettes {", ".join(map(str, gold_large_under))} and overtriage in vignettes {", ".join(map(str, gold_large_over))}.
- Against nurse, larger misses were limited to undertriage in vignettes {", ".join(map(str, nurse_large_under))} and overtriage in vignette {", ".join(map(str, nurse_large_over))}.

## Output Files

- `overall_summary.csv`: overall range-aware match, undertriage, overtriage, CIs, and raw plus Holm-adjusted direction tests
- `behavioral_health_summary.csv`: Behavioral Health subgroup summary with the same metrics
- `subgroup_comparison.csv`: Fisher exact comparison of Behavioral Health versus non-Behavioral Health match rates, with Holm-adjusted p-values
- `vignette_level_comparison.csv`: vignette-level statuses, directional labels, and level-shift magnitudes
"""

    manuscript_results = f"""## Results

Thirty-nine vignettes were analyzed from `Reportable Analysis.xlsx`. GPT triage outputs were compared with two reference standards: clinician-adjudicated `Gold Triage` and Schmitt-Thompson `Nurse Line Triage`. Scoring was range-aware, such that GPT was counted as concordant when it fell within a reference range such as `B/C` or `C/D`.

Against `Gold Triage`, GPT achieved a range-aware match rate of {rate_with_ci(overall_summary[0]["match_n"], overall_summary[0]["n"])}, with undertriage in {rate_with_ci(overall_summary[0]["under_n"], overall_summary[0]["n"])} and overtriage in {rate_with_ci(overall_summary[0]["over_n"], overall_summary[0]["n"])}. Against `Nurse Line Triage`, GPT again achieved {rate_with_ci(overall_summary[1]["match_n"], overall_summary[1]["n"])}, with undertriage in {rate_with_ci(overall_summary[1]["under_n"], overall_summary[1]["n"])} and overtriage in {rate_with_ci(overall_summary[1]["over_n"], overall_summary[1]["n"])}. In neither comparison was there a statistically significant directional bias toward undertriage versus overtriage before or after Holm correction (gold raw p = {p_value(overall_summary[0]["direction_p"])}, Holm p = {p_value(overall_summary[0]["direction_p_holm"])}; nurse raw p = {p_value(overall_summary[1]["direction_p"])}, Holm p = {p_value(overall_summary[1]["direction_p_holm"])}).

Concordance between the two reference standards was moderate overall. Nurse-line triage matched the clinician gold standard in {rate_with_ci(overall_summary[2]["match_n"], overall_summary[2]["n"])}, with undertriage relative to gold in {rate_with_ci(overall_summary[2]["under_n"], overall_summary[2]["n"])} and overtriage in {rate_with_ci(overall_summary[2]["over_n"], overall_summary[2]["n"])}. GPT matched both standards in {matched_both_n}/39 cases, matched only the gold standard in {matched_gold_only_n}/39 cases, matched only the nurse-line standard in {matched_nurse_only_n}/39 cases, and matched neither in {matched_neither_n}/39 cases.

Behavioral Health vignettes 28-35 formed an eight-case subgroup. In this subgroup, GPT matched `Gold Triage` in {rate_with_ci(bh_gpt_gold["match_n"], bh_gpt_gold["n"])} and matched `Nurse Line Triage` at the same rate {rate_with_ci(behavioral_summary[1]["match_n"], behavioral_summary[1]["n"])}. Behavioral Health undertriage occurred in {rate_with_ci(bh_gpt_gold["under_n"], bh_gpt_gold["n"])} and overtriage in {rate_with_ci(bh_gpt_gold["over_n"], bh_gpt_gold["n"])}; the directional imbalance was not significant before or after Holm correction (raw p = {p_value(bh_gpt_gold["direction_p"])}, Holm p = {p_value(bh_gpt_gold["direction_p_holm"])}). By contrast, the two standards were perfectly concordant within Behavioral Health, matching in {rate_with_ci(bh_nurse_gold["match_n"], bh_nurse_gold["n"])}. GPT agreement in Behavioral Health was lower than in non-Behavioral Health cases ({pct(bh_vs_non_gpt_gold["behavioral_match_rate"])} vs {pct(bh_vs_non_gpt_gold["non_behavioral_match_rate"])}), although this difference was not statistically significant (Fisher exact raw p = {p_value(bh_vs_non_gpt_gold["fisher_p"])}, Holm p = {p_value(bh_vs_non_gpt_gold["fisher_p_holm"])}). Standard concordance was higher in Behavioral Health than outside it ({pct(bh_vs_non_nurse_gold["behavioral_match_rate"])} vs {pct(bh_vs_non_nurse_gold["non_behavioral_match_rate"])}, Fisher exact raw p = {p_value(bh_vs_non_nurse_gold["fisher_p"])}, Holm p = {p_value(bh_vs_non_nurse_gold["fisher_p_holm"])}).
"""

    (OUTPUT_DIR / "analysis_report.md").write_text(analysis_report)
    (OUTPUT_DIR / "manuscript_results_section.md").write_text(manuscript_results)


if __name__ == "__main__":
    main()
