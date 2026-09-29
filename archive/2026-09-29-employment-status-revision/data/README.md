# Public data provenance

The empirical illustration uses the official 2022 and 2025 NHIS Sample Adult CSV archives. Original ZIP bytes are retained. `manifest.json` records exact agency URLs, SHA-256 hashes, file sizes, and acquisition date. Four official documentation PDFs are included for offline inspection. No credentials or data application are needed.

| Purpose | Variable or coding |
| --- | --- |
| Age domain | `AGEP_A` 18–64 |
| Unemployment/search category | `EMPWHYNOT_A = 1` (“Unemployed, laid off, looking for work”) |
| Employed comparator | `EMPWRKLSW1_A = 1` |
| Depressive symptoms | `PHQCAT_A` 3 or 4; valid recodes 1–4 |
| Anxiety symptoms | `GADCAT_A` 3 or 4; valid recodes 1–4 |
| Primary outcome | Either symptom criterion; both recodes observed |
| Weight | `WTFA_A / 2` for pooled estimates; original weight within year |
| Variance | Released `PSTRAT`, `PPSU`; all design units retained |
| Adjustment | Year, age groups, `SEX_A`, `HISPALLP_A`, `EDUCP_A`, `REGION` |
| Complete-item sensitivity | `PHQ81_A`–`PHQ88_A`, `GAD71_A`–`GAD77_A`; valid item codes 1–4 mapped to scores 0–3 |
| Narrow comparator sensitivity | `EMPLASTWK_A = 1` or `EMPNOWRK_A = 1` |
| Disability sensitivity | `DISAB3_A = 2` |

The official recodes can accommodate one missing item per scale under the NCHS scoring procedure; the complete-item sensitivity independently reconstructs both scores and checks agreement for all fully observed respondents. Missing special codes are not interpreted as symptoms or absence of symptoms.

The employment recode is not a direct measure of active search. The broader employed category includes certain temporary absences, seasonal/contract work, and unpaid family work. 2019 was considered but excluded because its employment recode differs. No NHIS–HPS prevalence calibration is performed.

The 2025 public-use design identifiers may be pooled with 2019-and-later public files without relabeling strata, per the 2025 Survey Description, pages 35–36. Restricted-use guidance differs. Pooled weighted population totals represent the average population across the two included years, not the sum of the populations or an average across the intervening years.

The included `results/analysis_input.csv.gz` is a deterministic derivative of public-use records. It retains all sampled adults for design accounting, including observations outside the analytic domain. The `eligible` and `complete` flags define the analysis population. No attempt is made to recover suppressed geography or respondent identities.
