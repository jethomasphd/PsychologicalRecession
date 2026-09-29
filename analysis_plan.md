# Analysis plan

Specified on 2026-09-29 before fitting the revised models. This is an exploratory empirical illustration for a position paper, not a registered protocol or a causal study.

## Scientific question

The substantive hypothesis is that the structural conditions of job seeking can damage mental health. The available public NHIS data cannot identify the effects of rejection, opacity, delays, or other hiring practices. The empirical question is narrower: how common are moderate or severe anxiety or depressive symptoms among adults classified as unemployed, laid off, or looking for work, compared with adults classified as working?

## Population and measures

- Use the official 2022 and 2025 NHIS Sample Adult public-use CSV files. These years have the same employment recode and PHQ-8/GAD-7 scales. Do not pool 2019, whose employment recode differs.
- Adults aged 18 through 64. Compare EMPWHYNOT_A=1 with EMPWRKLSW1_A=1. The former is a combined unemployment/layoff/job-search category, not a verified measure of active job seeking. Check for overlap.
- Primary outcome: PHQCAT_A or GADCAT_A in categories 3 or 4, requiring both recodes to be observed in categories 1 through 4. Outcomes denote symptoms in the previous two weeks, not clinical diagnoses.
- Secondary outcomes: depression and anxiety separately, on the same primary analytic sample.
- Prespecified covariates: survey year; age 18-29, 30-44, 45-54, 55-64; recorded sex; Hispanic origin and race (Hispanic, non-Hispanic White, non-Hispanic Black, non-Hispanic Asian, other non-Hispanic groups); education (less than high school, high school/GED, some college/associate, bachelor's or higher); Census region.
- Use complete cases; report exclusions sequentially and missingness by exposure. Do not adjust the primary model for current income, financial strain, or symptom-related functioning, which may sit on the hypothesized pathway.

## Estimation

Survey-weighted prevalence and 95% confidence intervals. Fit modified Poisson regressions with a log link for prevalence ratios. Use a Taylor-linearized, stratum-centered PSU sandwich variance, retaining all sampled PSUs with zero contributions outside the analysis domain. Divide WTFA_A by two for pooled estimates and preserve PSTRAT/PPSU as recommended by NHIS for pooling these years. Use design degrees of freedom (PSUs minus strata) for t intervals. Report the unadjusted and adjusted exposure coefficient, exponentiated.

Assess year-by-exposure interaction as exploratory; report year-specific prevalence and adjusted ratios rather than imply a continuous time trend from two snapshots. Examine fitted means, condition number, and convergence.

## Sensitivity analyses

1. Require all 15 symptom items to be answered and reconstruct scores, rather than use the NCHS recodes that can handle one missing item per scale.
2. Restrict the employed comparator to respondents who report working in the previous week or being temporarily absent from a job.
3. Exclude adults with disability on DISAB3_A. This is a sensitivity to health selection, not a causal correction.
4. Show worst-case bounds for missing symptom outcomes by exposure group.

## Interpretation and presentation

The main result is an association, not an effect of job seeking or hiring systems. Reverse causation, prior health, unmeasured financial resources, and exposure misclassification remain. No SEM or mediation model will be fitted without direct, temporally ordered measures of the hypothesized exposure and mediators. Use one simple empirical figure and a compact regression table; explain the proposed structural framework in prose and a short measurement table. No composite psychiatric index, consumer-sentiment proxy, or cross-survey baseline standardization.
