# Methods

## Triage Scale

Triage recommendations were analyzed on a four-level ordinal scale:

- `A`: home care
- `B`: non-urgent physician visit
- `C`: same-day urgent care or primary care visit
- `D`: call 911 or go to the emergency department

## Reference Standards

- `Gold Triage` represents clinician-adjudicated triage decisions.
- `Nurse Line Triage` represents Schmitt-Thompson protocol triage decisions.

## Concordance

Concordance was assessed using range-aware ordinal scoring, such that a triage recommendation was counted as concordant if it matched a single reference level exactly or fell within an allowable reference range. For example, `C` was treated as concordant with `C/D`, whereas recommendations below the reference range were classified as undertriage and recommendations above the reference range were classified as overtriage.

## Confidence Intervals

Confidence intervals for match, undertriage, and overtriage rates were calculated as 95% Wilson score intervals for binomial proportions.

## Inferential Testing

- Directional imbalance between undertriage and overtriage was assessed with two-sided exact binomial tests on discordant cases only.
- Behavioral Health subgroup comparisons were assessed with two-sided Fisher exact tests.
- Holm correction was applied within related families of inferential tests.

## Behavioral Health Subgroup

The Behavioral Health subgroup was defined a priori as vignette numbers 28 through 35.
