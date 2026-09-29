# Study review and current state

Repository: `jethomasphd/PsychologicalRecession`. Review and linked-data revision: September 29, 2026.

## The question and the corrected scope

Job seeking places people in a structural environment that can constrain access to income, security, control and participation. The user’s intended paper asks whether that environment is a psychiatric exposure. It is an empirical editorial written with an industry perspective. It must relate measured mental-health burden to market conditions and include relevant grey literature, preprints and popular reporting.

The first revision compared employment groups in NHIS. That answered a different question. It has been preserved in full at `archive/2026-09-29-employment-status-revision/` (commit `1c651fdac40ea736028b56c75beb6ff67e497691`), and none of its estimates are presented as evidence of the market-condition effect in the current paper.

## What was in the original repository

The original main commit was `b6ceb3fe006a99774dda29196cd79fcaaf1cac8d`. All 14 files were inspected: Word manuscript and bibliography, two Python scripts, README, five source CSVs, derived PRI table, OLS output, dashboard and figure files. Their bytes remain at the archive root and are checked by `audit/archive_sha256.json`.

The project combined a conceptual paper with an index based on a consumer-sentiment regression residual and selected anxiety/depression values. It was not an analysis directly linking individual mental-health outcomes to measured job-market conditions. Machine-specific paths prevented a portable rebuild. The HPS component used `(prevalence − 10.8) / 1.5` without establishing an appropriate reference standard deviation; components changed with data availability. NHIS and HPS measures, modes and recall periods were treated as comparable without a linking model. Some supplied 2025 HPS observations could not be traced to the cited legacy release, which ended in September 2024. Those observations remain unverified; no fabrication finding is asserted. Time-series dependence and index construction were not adequately reflected in inference. The 64-reference bibliography also contained incorrect titles, authors and identifiers, alongside incomplete records.

Those original materials are historical, not current evidence endorsed by the revision. Their full earlier methodological review and audit remain in the archived first revision.

## Current empirical state

- Public CDC BRFSS respondent files, 2013–2025, were obtained with the original SAS layouts. Public BLS state JOLTS and LAUS files were downloaded, checked and frozen.
- The primary sample contains 193,060 out-of-work adults in 607 state-years during 2013–2024. A separate contextual model contains 2,223,024 employed adults. No active-search status or diagnosis is inferred.
- Weighted fixed-effect regressions link distress to actual state hiring, competition for openings, and opening rates. State-clustered uncertainty is explicit. The analysis uses original respondent counts in the finite-sample correction.
- Lower same-year hiring has an uncertain inverse coefficient; the prior-year coefficient reverses sign. Competition per opening has a positive, imprecise coefficient. All prespecified checks and the labeled post hoc logistic check are reported. No significant-only selection, composite psychiatric index, or unsupported mediation analysis is used.
- The 2025 extension is separated because BLS’s annual unemployment inputs have 11 months. The missing October competition observation is not interpolated.
- Individual respondent records reproduce the main collapsed-profile coefficients and covariance with statsmodels. Source reconstruction, official extraction positions, sample flow and archive hashes are checked by the executable pipeline.

The conclusions are bounded by selection into current out-of-work status, annual timing, geography, changing confounding, self-report, nonresponse and model-assisted market estimates. These findings do not rule out individual harm and do not establish that a particular recruitment feature causes it.

## Evidence and presentation

The paper has 24 references with recorded identity, claim support, review depth and limits. Ten are peer-reviewed papers; others include a working paper, preprint, Federal Reserve qualitative report, industry reports, media, official sources and repository. The audit differentiates abstract-level review from full-text review, traces duplicate media coverage to its source, and corrects misleading denominators. It is not advertised as a systematic literature review or an exhaustive retraction screen.

The manuscript contains one simple coefficient figure, a short primary-results table and a compact technical note with all main hiring checks. Its sources, model terms, population and noncausal interpretation are stated in ordinary public-health language. The PDF page count and visual review are recorded in `release_validation.json`; the 20-page ceiling includes every part of the paper, with no external supplement required to understand its essential methods and results.

## Authorship and publication state

Jacob E. Thomas, PhD is the only named author. Affiliation, correspondence, employment disclosure and funding statement are carried forward from the original manuscript; a future job-board coauthor was omitted at the user’s explicit request. No coauthor agreement, journal submission, ethics-board determination, or external peer review has been invented. The author will need to confirm declarations and complete the chosen journal’s contributor and AI-assistance disclosures before submission.
