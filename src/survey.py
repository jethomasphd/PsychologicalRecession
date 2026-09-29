"""Taylor linearization for stratified multistage survey estimates.

All design PSUs must be supplied, including those with zero contributions to a
subpopulation. No finite population correction is used. NHIS public-use masked
variance units are used exactly as released.
"""
import numpy as np
import pandas as pd
from scipy.stats import t
import statsmodels.api as sm


def design_covariance(influence, design):
    a = np.asarray(influence, dtype=float)
    if a.ndim == 1:
        a = a[:, None]
    assert len(a) == len(design)
    z = pd.DataFrame(a)
    z['stratum'] = design['PSTRAT'].to_numpy()
    z['psu'] = design['PPSU'].to_numpy()
    totals = z.groupby(['stratum', 'psu'], sort=True).sum()
    result = np.zeros((a.shape[1], a.shape[1]))
    for _, group in totals.groupby(level=0):
        n = len(group)
        if n < 2:
            raise ValueError('Singleton PSU in full design; do not silently adjust')
        centered = group.to_numpy() - group.to_numpy().mean(axis=0)
        result += (n / (n - 1)) * centered.T @ centered
    df = len(totals) - totals.index.get_level_values(0).nunique()
    return result, int(df)


def prevalence(data, mask, outcome='outcome'):
    mask = mask & data[outcome].notna()
    w = data.loc[mask, 'weight'].to_numpy()
    y = data.loc[mask, outcome].to_numpy()
    p = np.average(y, weights=w)
    influence = np.zeros(len(data))
    influence[mask] = w * (y - p) / w.sum()
    v, df = design_covariance(influence, data)
    se = np.sqrt(v[0, 0])
    # Logit confidence limits stay inside [0,1].
    q = t.ppf(.975, df)
    eta = np.log(p / (1-p))
    lo, hi = 1 / (1 + np.exp(-(eta + np.array([-1, 1])*q*se/(p*(1-p)))))
    return {'n':int(mask.sum()), 'events':int(y.sum()), 'prevalence':float(p),
            'se':float(se), 'lower':float(lo), 'upper':float(hi),
            'weighted_population':float(w.sum()), 'design_df':df}


def fit_poisson(data, mask, matrix, outcome='outcome'):
    X = np.asarray(matrix, dtype=float)
    y = data.loc[mask, outcome].to_numpy(dtype=float)
    w = data.loc[mask, 'weight'].to_numpy(dtype=float, copy=True)
    # Constant rescaling is immaterial to both the estimating equations and
    # the sandwich covariance, and improves numerical conditioning.
    w /= w.mean()
    model = sm.GLM(y, X, family=sm.families.Poisson(), freq_weights=w).fit(maxiter=100, tol=1e-11)
    mu = np.asarray(model.fittedvalues)
    bread = X.T @ ((w * mu)[:, None] * X)
    score = ((w * (y-mu))[:, None]) * X
    invbread = np.linalg.inv(bread)
    influence = np.zeros((len(data), X.shape[1]))
    influence[mask] = score @ invbread
    covariance, df = design_covariance(influence, data)
    return {'coef':np.asarray(model.params), 'covariance':covariance, 'df':df,
            'converged':bool(model.converged), 'max_mean':float(mu.max()),
            'min_mean':float(mu.min()), 'means_above_one':int((mu>1).sum()),
            'condition_number':float(np.linalg.cond(X)),
            'score_max':float(np.abs(score.sum(axis=0)).max()),
            'n':int(mask.sum()), 'events':int(y.sum())}


def contrast(model, vector):
    c = np.asarray(vector, dtype=float)
    estimate = float(c @ model['coef'])
    se = float(np.sqrt(c @ model['covariance'] @ c))
    q = t.ppf(.975, model['df'])
    return {'log_estimate':estimate, 'se':se, 'ratio':float(np.exp(estimate)),
            'lower':float(np.exp(estimate-q*se)), 'upper':float(np.exp(estimate+q*se)),
            'p':float(2*t.sf(abs(estimate/se), model['df']))}
