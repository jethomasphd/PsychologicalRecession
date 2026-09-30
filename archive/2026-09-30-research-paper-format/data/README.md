# Public data, linkage, and dictionary

Vintage: September 29, 2026. `source_manifest.json` records 32 downloaded official files (13 BRFSS ASCII ZIPs, 13 SAS layouts, and six BLS flat files), totaling 785,351,574 downloaded bytes; the BRFSS data remain ZIP-compressed. No private records or credentials are needed. These are public-use survey records and US government statistics; the repository does not assert ownership of source data.

`derived/` contains the frozen analytic extracts. `frozen_manifest.json` protects their bytes and the retained source documentation. `layouts/` holds the exact official SAS files; `layouts.json` gives zero-based, end-exclusive byte slices. The pipeline checks every listed position against its original SAS layout. `source_snapshot/` losslessly compresses all six BLS source files so future BLS revisions cannot prevent reproduction of this vintage. `source_cache/` is populated as needed and excluded from Git.

## Health records

The [CDC BRFSS annual files](https://www.cdc.gov/brfss/annual_data/annual_data.htm) cover 2013–2025. Primary analysis: 2013–2024. Linkage uses the file's survey year and respondent state; some interviews occur after the nominal survey year. Monthly interview fields are preserved in the small individual extract for transparency but do not define the annual exposure.

| Analytic field | Official field | Definition |
| --- | --- | --- |
| state | _STATE | 50 states and DC, standard two-digit FIPS; territories excluded |
| year | source-file year | Annual survey cohort |
| interview_year, month | IYEAR, IMONTH | Numeric interview date components; unavailable/non-numeric components represented by zero, unused in models |
| days | MENTHLTH | 1–30 days; 88 becomes zero; 77, 99, blank excluded |
| fmd | MENTHLTH-derived | 1 if days ≥14, else 0 |
| employment | EMPLOY1 | 1 employed, 2 self-employed, 3 out of work ≥1 year, 4 out of work <1 year; other categories excluded |
| age | _AGEG5YR | 1–9: 18–24, then five-year bands 25–29 through 60–64 |
| sex | SEX / SEX1 / _SEX | Released binary field: SEX 2013–2017; SEX1 2018; _SEX 2019–2025. Keep valid codes 1/2. Derivation changes limit comparability. |
| education | EDUCA | 1–3 → less than high school; 4 → high school; 5 → some college; 6 → college graduate |
| race | _RACEGR3; _RACEGR4 in 2022 | Five released groups: non-Hispanic White, non-Hispanic Black, non-Hispanic other race, non-Hispanic multiracial, Hispanic; other/missing codes excluded |
| weight | _LLCPWT | Positive final respondent weight |

The primary population is out-of-work respondents with complete outcome, demographic, and weight information. This is not a direct measure of active search. Missing state-years are NJ 2019, FL 2021, KY and PA 2023, and TN 2024. The 2025 extension additionally lacks CA, MS, and NV in that year's files. No state-year is imputed.

`out_of_work_YEAR.csv.gz` retains each eligible out-of-work record without a personal identifier. `profiles_YEAR.csv.gz` contains all eligible out-of-work and employed respondents collapsed by state, year, employment, age, sex, education, and race. For each identical design profile it stores:

- `n`: original number of respondents;
- `weight`: sum of final weights;
- `fmd_weighted`: sum of weight × distress indicator;
- `days_weighted`: sum of weight × mentally unhealthy days.

These sums preserve individual-level weighted linear-regression cross-products and state-cluster scores, including the original-N finite-sample correction. They are not simply state prevalence means. The main result is independently reproduced from uncollapsed respondent records with statsmodels WLS. Year-specific and combined `sample_flow` files expose all exclusions.

## Market records

Source flat files are supplied by BLS at `https://downloadt.bls.gov/pub/time.series/`. JOLTS metadata in `jt.series`, `jt.state`, `jt.dataelement`, and `jt.ratelevel` define the codes; `jt.data.1.AllItems` contains observations. LAUS observations come from `la/la.data.2.AllStatesU`.

| Analytic field | Construction | Unit |
| --- | --- | --- |
| hires_rate | Mean of 12 seasonally adjusted HIR observations | Hires per 100 payroll employees |
| openings_rate | Mean of 12 seasonally adjusted JOR observations | Openings as percent of employment plus openings |
| layoffs_rate | Mean of 12 seasonally adjusted LDR observations; retained for transparency, not fitted | Layoffs/discharges per 100 payroll employees |
| unemployed_per_opening | Mean of 12 monthly UOR observations | People per opening; mean of ratios, not ratio of annual totals |
| unemployment_rate | Published LAUS unadjusted annual-average M13 observation | Percent of civilian labor force |
| lower_hiring, lower_openings | Negative of corresponding rate | A positive change denotes worsening condition |
| competition | log2(unemployed_per_opening) | One unit is a doubling |
| lag_lower_hiring, lag_unemployment_rate | Prior year within state | Same units as current-year field |

All JOLTS series are restricted to all-industry, all-size, whole-state, seasonally adjusted records; metadata-based joins identify their measures. Monthly data from 2012 permit the 2013 lag. National rows may remain in the market table for transparency but cannot join to a respondent state. State JOLTS estimates use survey and model-assisted inputs; they are not direct estimates of applicant success.

`market_monthly.csv` preserves the intermediate JOLTS panel, including unused level series. `market_annual.csv` holds exposures. The primary 607 state-years have complete linked exposure data. October 2025 UOR is missing; the annual competition measure is therefore missing for 2025, not an 11-month approximation. Published 2025 LAUS annual rates have 11 months and are used only in the labeled hiring extension.

## Reproducibility boundary

Offline reproduction starts from the frozen extracts. `python reproduce.py --from-source --download` reproduces those extracts from the official ASCII sources and the saved BLS vintage, checks semantic equality, then fits the models. Floating-point serialization and gzip headers may vary by platform; source bytes must match exactly and numerical comparison uses explicit tolerances. Source changes are never accepted silently. The code does not acquire an individual diagnosis, employer intent, exposure to a particular platform, occupational search market, or mediator from variables that do not measure it.
