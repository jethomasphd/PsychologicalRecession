# Job seeking as a psychiatric exposure

**A public health position from the hiring industry**
Jacob E. Thomas, PhD · September 2026

The central question is whether the structural conditions people encounter while seeking work contribute to psychiatric symptoms. This paper argues that employers, recruitment intermediaries, and job platforms should measure those conditions and test ways to reduce avoidable harm.

[Read the paper in Word](manuscript/Job_seeking_as_a_psychiatric_exposure.docx) · [Read the PDF](manuscript/Job_seeking_as_a_psychiatric_exposure.pdf) · [Read the text](manuscript/manuscript.md) · [Review the evidence audit](audit/reference_audit.md)

## What the public data show

Across 26,281 adults aged 18–64 in the 2022 and 2025 National Health Interview Survey, moderate or severe anxiety or depressive symptoms were present in **17.3%** of the combined unemployment/layoff/search category and **8.2%** of the employed category. The adjusted prevalence ratio was **1.92 (95% CI 1.58–2.33)**.

![Survey-weighted symptom prevalence with 95% confidence intervals](results/figure1.png)

The NHIS category is broader than active job seeking. These cross-sectional data establish symptom burden and association. They do **not** identify an effect of job seeking, a particular platform, or a hiring practice. The manuscript describes a regression and longitudinal structural equation framework for testing those questions, and proposes organizational trials.

## Reproduce the paper

Use Python 3.12. The two official public-use CSV archives are included, so the analysis and manuscript build need no network after dependency installation. No API key, proprietary dataset, or manual spreadsheet step is required.

```sh
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements-lock.txt
python reproduce.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`; on macOS/Linux, use `source .venv/bin/activate`. Alternatively invoke the environment's Python executable directly.

The command verifies source checksums, reconstructs the analytic sample, fits survey-weighted regressions, runs algebraic validation checks, creates the figure, and builds the Word manuscript and reference audit. A clean Python environment was used for the release check. `requirements-lock.txt` pins direct and transitive package versions; `requirements.txt` lists the direct dependencies. See [statistical validation](audit/statistical_validation.json) and [release validation](audit/release_validation.json).

If source files are absent, `python reproduce.py --download` fetches them from NCHS and requires the frozen SHA-256 hashes to match. A changed upstream file stops the build for review. To also verify or fetch the four official documentation PDFs, use `python src/fetch_data.py --documents --download`. For results without document generation, use `python reproduce.py --analysis-only`.

The Word file is editable and generated from `manuscript/paper.md`, `manuscript/references.json`, and the calculated results. PDF export is a separate rendering step. The distributed PDF was rendered and every page inspected; the exact renderer and page count are in the release record. Word processors and font substitutions can change pagination, so recheck the **20-page total limit** after editing. The paper contains all its essential methods, tables, declarations, and references within that limit.

## Repository map

| Location | Contents |
| --- | --- |
| `manuscript/` | Editable Word manuscript, inspected PDF, generated readable text, text source, and verified references |
| `src/` | Acquisition, survey variance, regression, checks, figure, manuscript, and audit scripts |
| `data/` | Frozen official public-use files, documentation, source URLs, and checksums |
| `results/` | Complete coefficients and diagnostics, sample flow, descriptive tables, analytic derivative, and figure in PNG/SVG/PDF |
| `audit/` | Reference and study review, original-file checksums, statistical and release validation |
| `archive/` | All 14 original repository files, preserved byte for byte |
| `analysis_plan.md` | Exploratory plan written before the revised models were fitted |

## Evidence and interpretation

The main illustration uses modified Poisson regression to estimate prevalence ratios, with NHIS weights and a stratified cluster sandwich variance. All sampled variance units are retained for domain estimation. Sensitivities examine complete symptom items, a narrower employed comparator, disability exclusion, and missing outcomes. The exploratory year interaction does not establish a worsening time trend.

The reference audit distinguishes bibliographic identity from support for a claim. It screens all 64 original entries and documents all 15 retained references. Unsupported industry survey percentages and inaccurate citations are removed from the current paper. The old consumer-sentiment composite is preserved in `archive/` and is not used as a psychiatric measure. [Study review and revision decisions](audit/study_review.md) explain why.

## Authorship and data use

The current version names Jacob E. Thomas only. His recruitment-industry affiliation is disclosed. No coauthor identity, contribution, or institutional approval is presumed. Author declarations should be confirmed before journal submission.

NHIS files are official NCHS public-use releases. Follow the agency's [data documentation and use conditions](https://www.cdc.gov/nchs/nhis/documentation/2025-nhis.html); do not attempt to identify respondents. This repository contains no proprietary job-board records. No new license is asserted over third-party literature or the archived materials.
