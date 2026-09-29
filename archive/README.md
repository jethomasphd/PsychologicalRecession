# The Psychological Recession Index — Empirical Estimation v2

**United States, 2010–2026Q1** · Jacob E. Thomas, PhD · Results Generation · `2026-05-19`

---

## What this is

A first empirical operationalization of the Psychological Recession Index (PRI) proposed in *The Psychological Recession: Conceptualizing and Operationalizing the Post-Pandemic United States Labor Market as a Distal Psychiatric Exposure*. The construct claim is that the macroeconomic→psychiatric relationship stable across 2010–2019 has broken down post-2020, and that the unexplained residual is the empirical signature of what this paper names a *psychological recession*. The numbers below test that claim against publicly available data.

## Headline numbers

| Quantity | Value |
| --- | --- |
| Baseline R² (2010Q1–2019Q4, OLS on three macro indicators) | **0.915** |
| Baseline residual σ | 3.09 sentiment-index points |
| Latest composite PRI (2026Q1) | **+10.8 σ** |
| Mean composite PRI 2022Q1 → present | **+11.8 σ** |
| Peak composite PRI (2025Q4) | **+13.5 σ** |
| Latest HPS anxiety+depression | 33.5% (vs. NHIS 2019 anchor of 10.8%) |
| Quarters post-2020 with composite PRI > +5σ | 22 of 25 |

The HPS-based PRI component runs *higher* than the sentiment-based component (+15.1σ vs. +10.8σ at latest), which is itself a finding: direct psychiatric measurement registers more deviation than sentiment-as-proxy does. This is the paper's measurement-failure thesis literally cashing out.

## What's in this directory

### Primary deliverable
- **`Psychological_Recession_APA.docx`** — full paper, APA 7th edition, SSRN-submission-ready. Methods §2.3 now describes the actual estimation procedure; Results §3.6 reports empirical numbers; Figure 1 has been replaced with the four-panel empirical PRI figure. 41 pages.

### Figure for the paper
- **`Figure_1_PRI_v2.png`** — 220 dpi PNG, 10.5 × 11.5 in, four panels (sentiment observed vs. predicted; HPS anxiety+depression; sentiment gap; composite PRI).
- **`Figure_1_PRI_v2.pdf`** — vector version for press / print.

### Interactive dashboard
- **`PRI_Dashboard.html`** — self-contained HTML, opens in any browser. Dark/ember aesthetic, Cormorant Garamond + IBM Plex Mono typography, scroll-reveal sections, four interactive Plotly charts, KPI cards, reading block, full quarterly data table, OLS fit output. Internet connection required to load the Plotly CDN; no other dependencies.

### Analysis outputs
- **`PRI_v2_quarterly.csv`** — the quarterly panel. Columns: `date, unrate, dpayems_yoy, jtsjol_thousands, observed_sentiment, predicted_sentiment, sentiment_gap, pri_sentiment, hps_obs, pri_hps, pri_composite`. 61 quarters × 11 columns.
- **`PRI_v2_OLS_fit.txt`** — statsmodels regression summary for the baseline fit.

### Reproducibility
- **`build_PRI_v2.py`** — full analysis script. Loads the five data CSVs, resamples to quarterly, fits the baseline OLS, computes both PRI components and the composite, generates the paper figure.
- **`build_dashboard_v2.py`** — reads `PRI_v2_quarterly.csv` and emits the interactive HTML dashboard.

### Raw input data (transparency)
- **`data_UNRATE.csv`** — BLS unemployment rate, monthly SA, 2010–2026.
- **`data_PAYEMS.csv`** — BLS total nonfarm payrolls, monthly SA, 2010–2026.
- **`data_UMCSENT.csv`** — Michigan Survey consumer sentiment, monthly NSA, 2010–2026 (©, citation required: Surveys of Consumers, University of Michigan).
- **`data_JTSJOL.csv`** — BLS JOLTS total nonfarm job openings, monthly SA, 2010–2026.
- **`data_HPS_ANXDEP.csv`** — Census/CDC HPS national anxiety-or-depression prevalence, compiled from CDC NCHS published wave tables and MMWR reports; includes the 2019 NHIS pre-pandemic anchor (10.8%) as the baseline observation.

## Specification

The estimated sentiment-on-macro regression, trained on 2010Q1–2019Q4 (n = 36):

```
UMCSENT = β₀ + β₁·UNRATE + β₂·Δ%PAYEMS_yoy + β₃·log(JTSJOL) + ε
```

| Coefficient | Estimate | SE | t | p |
| --- | --- | --- | --- | --- |
| β₀ (constant) | 336.26 | 134.01 | 2.51 | .017 |
| β₁ (unemployment %) | **−8.78** | 2.03 | −4.33 | < .001 |
| β₂ (ΔPAYEMS yoy %) | 2.15 | 2.05 | 1.05 | .303 |
| β₃ (log job openings) | −23.57 | 14.22 | −1.66 | .107 |

Adjusted R² = 0.907 · F(3,32) = 115.4 · *p* < .001 · residual σ = 3.09 sentiment-index points. The unemployment coefficient is the dominant predictor; the inclusion of payroll growth and log job openings improves explanatory power and absorbs collinear macro variation without changing the substantive story.

PRI definitions:

```
PRI_sentiment(t) = (predicted_sentiment - observed_sentiment) / σ_baseline
PRI_hps(t)       = (HPS_value - 10.8) / 1.5
PRI_composite(t) = mean of available standardized components
```

Positive values = mental health (or its proxy) worse than the macro state predicts.

## Caveats

1. **HPS pre-pandemic baseline.** The Household Pulse Survey did not exist before April 2020. The 10.8% anchor comes from the 2019 National Health Interview Survey (Vahratian et al., MMWR 2021), which fielded equivalent PHQ-8 and GAD-7 instruments. The 1.5-percentage-point baseline σ is a conservative estimate of year-to-year NHIS variation in equivalent K6-based prevalence; v3 should refine this with the full NHIS time series.

2. **Sentiment as proxy.** The sentiment-based PRI component depends on the documented sentiment-mental-health correlation rather than measuring psychiatric state directly. The HPS-based component is the direct measurement and serves as the validation. Both register the same direction and similar magnitude.

3. **Multicollinearity.** Condition number of the macro RHS is 2,640. The OLS coefficients are stable enough for the projection use case but ridge regularization would be the next refinement.

4. **Inflation memory.** Some portion of the sentiment-fundamentals gap is plausibly attributable to lagged price-level shock effects (Bernstein & Posthumus, 2025). The HPS divergence — measured on a clinical screening instrument — cannot be reduced to inflation memory.

5. **HPS series resolution.** The CDC dataset (8pt5-q6wp / xpsn-dxxd) carries 250+ rows per biweekly wave from state and demographic stratification. The national-mean values in `data_HPS_ANXDEP.csv` were compiled from CDC NCHS published wave tables rather than pulled row-by-row from the API; v3 should retrieve the full underlying dataset and re-aggregate.

## Citation

Thomas, J. E., & [Co-author]. (2026). *The Psychological Recession: Conceptualizing and Operationalizing the Post-Pandemic United States Labor Market as a Distal Psychiatric Exposure.* SSRN preprint.

Data sources: U.S. Bureau of Labor Statistics, *Employment Situation*; *Job Openings and Labor Turnover Survey*. University of Michigan, *Surveys of Consumers*. U.S. Census Bureau, *Household Pulse Survey*. CDC National Center for Health Statistics, *Indicators of Anxiety or Depression Based on Reported Frequency of Symptoms During Last 7 Days*. National Health Interview Survey, 2019, as compiled in Vahratian, Blumberg, Terlizzi, & Schiller (2021), *MMWR* 70(13), 490–494.

Series retrieved 2026-05-19 via FRED (https://fred.stlouisfed.org) and data.cdc.gov.
