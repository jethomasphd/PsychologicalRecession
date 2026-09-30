"""Independent numerical checks; no tests that merely restate manuscript claims."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import json,numpy as np,pandas as pd,statsmodels.api as sm
from scipy import stats,special
from analyze import design
ROOT=Path(__file__).resolve().parents[1]
def main():
    micro=pd.concat([pd.read_csv(ROOT/'data'/'derived'/f'out_of_work_{y}.csv.gz') for y in range(2013,2025)],ignore_index=True)
    market=pd.read_csv(ROOT/'data'/'derived'/'market_annual.csv')
    d=micro.merge(market,on=['state','year'],validate='many_to_one')
    X,names=design(d,['lower_hiring','unemployment_rate']);w=d.weight.to_numpy();w=w/w.mean();y=d.fmd.to_numpy()
    independent=sm.WLS(y,X,weights=w).fit(cov_type='cluster',cov_kwds={'groups':d.state.to_numpy()},use_t=True)
    saved=np.load(ROOT/'results'/'primary_crossproducts.npz')
    assert np.allclose(independent.params,saved['beta'],atol=1e-8)
    assert np.allclose(independent.cov_params(),saved['vcov'],atol=1e-8)
    out={'raw_respondent_n':len(d),'collapsed_and_uncollapsed_coefficients_max_difference':float(abs(independent.params-saved['beta']).max()),'cluster_covariance_max_difference':float(abs(independent.cov_params()-saved['vcov']).max()),'weighted_fraction_linear_predictions_outside_0_1':float(np.average((independent.fittedvalues<0)|(independent.fittedvalues>1),weights=w))}
    # Added after first results: a model-form check prompted by out-of-range LPM predictions.
    # Fit logistic IRLS directly and compute state-score covariance plus a delta-method
    # average marginal association. This is explicitly labeled post hoc.
    beta=np.zeros(X.shape[1]);beta[0]=special.logit(np.average(y,weights=w))
    for iteration in range(50):
        pr=special.expit(X@beta);v=pr*(1-pr)
        A=X.T@((w*v)[:,None]*X);score=X.T@(w*(y-pr))
        delta=np.linalg.solve(A,score);beta+=delta
        if abs(delta).max()<1e-9:break
    assert iteration<49
    pr=special.expit(X@beta);v=pr*(1-pr);A=X.T@((w*v)[:,None]*X);bread=np.linalg.inv(A)
    scores=[];state=d.state.to_numpy();groups=np.unique(state);G=len(groups);N=len(d);p=X.shape[1]
    for g in groups:
        ix=state==g;scores.append(X[ix].T@(w[ix]*(y[ix]-pr[ix])))
    scores=np.vstack(scores);vcov=bread@(scores.T@scores)@bread*G/(G-1)*(N-1)/(N-p)
    j=names.index('lower_hiring');grad=beta[j]*np.average((v*(1-2*pr))[:,None]*X,weights=w,axis=0);grad[j]+=np.average(v,weights=w)
    ame=beta[j]*np.average(v,weights=w);se=np.sqrt(grad@vcov@grad);crit=stats.t.ppf(.975,G-1)
    out['posthoc_logistic']={'estimate_pp':float(100*ame),'lower_pp':float(100*(ame-crit*se)),'upper_pp':float(100*(ame+crit*se)),'iterations':iteration+1,'n':N,'label':'Average marginal association per 1 percentage-point lower hiring rate; post hoc model-form check'}
    out['pass']=True
    (ROOT/'results'/'validation.json').write_text(json.dumps(out,indent=2),encoding='utf8',newline='\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
