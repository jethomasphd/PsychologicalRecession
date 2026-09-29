# Study review and revision decisions

Original repository: `jethomasphd/PsychologicalRecession`, main at `b6ceb3f` before revision. Review date: 2026-09-29.

## Core question

The user clarified that the question is whether the structural environment of looking for work makes people sick. The article is a position paper / empirical editorial written from an industry perspective. It is not principally about a divergence between macroeconomic indicators and consumer sentiment. The named future coauthor is intentionally absent at the user's request.

## What existed

All 14 original files were read or inspected in their relevant form: the Word manuscript (including tables and bibliography); both Python scripts; README; the five source CSV files; derived PRI CSV; OLS output; the dashboard HTML; and the PNG/PDF figure. They are preserved byte for byte under `archive/`. The checksum manifest is `archive_sha256.json`. The archive is a historical record, not current evidence endorsed by this revision.

The original project was a long conceptual paper plus an exploratory composite index. It regressed consumer sentiment on unemployment, payroll growth, and the log of job openings, then combined a standardized residual with selected anxiety/depression prevalence values. The supplied code depended on a machine-specific `/home/claude/pri` path and a data-directory structure that did not match the uploaded files. There was no executable source-acquisition pipeline or frozen environment.

## Why the old index is not the revised analysis

1. **Construct validity:** a consumer-sentiment residual is not a measure of psychiatric illness, job seeking, rejection, or exposure to a hiring system.
2. **Scaling:** the HPS component used `(prevalence − 10.8) / 1.5` without establishing the denominator as a valid reference standard deviation. Reported extreme standardized values therefore lacked an interpretable psychiatric scale.
3. **Changing composition:** averaging whatever components were available altered the meaning of the composite over time.
4. **Incompatible baseline:** NHIS and HPS measures, collection modes, and reference periods were combined without a justified linking model. Their raw prevalences cannot establish a comparable threefold increase.
5. **Source traceability:** the supplied HPS series included 2025 observations that could not be traced to the cited legacy CDC HPS release (which ends in September 2024). Those rows are unverified, not declared fabricated, and are excluded from the new analysis.
6. **Time-series inference:** the regression did not adequately establish uncertainty for serial dependence, specification choice, or the constructed index. The effective baseline after growth-rate construction was 2011–2019 (36 quarters), not a full 2010–2019 sample. The last 2026 quarter was incomplete.
7. **Interpretation:** the materials moved from an ecological sentiment pattern to claims about psychiatric harm without observing the proposed exposure or a defensible causal design.
8. **Bibliography:** the audit found wrong or unresolved identifiers, inaccurate titles/authors, incomplete gray-literature citations, and claims exceeding what their sources support. See `reference_audit.md`.

## New empirical state

The revised empirical illustration uses public 2022 and 2025 NHIS records with compatible employment recodes and PHQ-8/GAD-7 symptom measures. The 2019 file was reviewed but not pooled because its employment recode differs. Adults aged 18–64 are compared using the exact combined unemployment/layoff/search category and the employed recode. The analysis does not mislabel this as a direct measurement of active search.

Survey-weighted prevalence and modified Poisson regression provide transparent descriptive and adjusted associations. Masked strata/PSUs are retained, including zero domain contributions. Complete-case exclusions, item reconstruction, an interaction, and sensitivity analyses are explicit. The primary result is an adjusted prevalence ratio of approximately 1.92 (95% CI 1.58–2.33). It supports the relevance of the population, not a causal effect of hiring practices.

The structural argument is supported by focused literature on unemployment, daily job seeking, resources and control, applicant reactions, discrimination, and intervention. Four industry practices are proposed as measurable intervention targets. A future longitudinal regression / structural equation framework and an organizational randomized trial are described without pretending the current public data can identify their mechanisms.

## Meaningful checks

- Exact source SHA-256 verification; raw official files included for offline reproduction.
- Hand-calculated stratified cluster variance check.
- Independent ratio-of-means and delta-method comparison with the crude regression coefficient and variance.
- Weight-rescaling invariance, model convergence, score residuals, and fitted-probability checks.
- All 15 complete symptom items reproduce the official severity recodes exactly for fully observed respondents.
- Sample flow reconciles and all archived original checksums match.
- Separate rendering and visual review cover the complete manuscript, including front matter, tables, declarations, and references. The rendering record reports the actual result, not an assumed page count.

## Authorship handoff

The current byline is Jacob E. Thomas, PhD, using the affiliation and correspondence address in the supplied original. Funding and employment disclosure are carried forward from that source and should be confirmed by the author before journal submission. No future coauthor, ORCID, author contribution, approval, or institutional ethics determination has been invented. A journal-specific AI-assistance disclosure and final contributor statement should be completed by the authors under their chosen journal's requirements. No journal submission has been made.
