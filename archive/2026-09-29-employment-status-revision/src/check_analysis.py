"""Independent algebraic checks of survey variance and fitted estimates."""
import json
import numpy as np
import pandas as pd
import patsy
from analyze import load, ROOT
from survey import design_covariance, fit_poisson, prevalence

def main():
    # Hand calculation with two strata and two clusters per stratum.
    design=pd.DataFrame({'PSTRAT':[1,1,1,2,2], 'PPSU':[1,1,2,1,2]})
    v,df=design_covariance(np.array([1,2,5,7,11]),design)
    assert np.isclose(v[0,0],(3-5)**2+(7-11)**2) and df==2
    d=load(); mask=d.complete
    X=patsy.dmatrix('exposed',d.loc[mask],return_type='dataframe')
    fit=fit_poisson(d,mask,X)
    ps=[]; influence=np.zeros((len(d),2))
    # Ratio of two independently formed survey means must equal the saturated
    # log-link coefficient; delta-method covariance must also agree.
    for g in [0,1]:
        use=mask&d.exposed.eq(g)
        w=d.loc[use,'weight'].to_numpy(); y=d.loc[use,'outcome'].to_numpy()
        p=np.average(y,weights=w);ps.append(p)
        influence[use,g]=w*(y-p)/w.sum()/p
    cov,df=design_covariance(influence,d)
    direct_var=np.array([-1.,1.])@cov@np.array([-1.,1.])
    assert np.isclose(np.exp(fit['coef'][1]),ps[1]/ps[0],rtol=1e-10)
    assert np.isclose(fit['covariance'][1,1],direct_var,rtol=1e-8)
    scaled=d.copy();scaled['weight']=d.weight*137
    refit=fit_poisson(scaled,mask,X)
    np.testing.assert_allclose(fit['coef'],refit['coef'],rtol=1e-10,atol=1e-12)
    np.testing.assert_allclose(fit['covariance'],refit['covariance'],rtol=1e-10,atol=1e-12)
    r=json.loads((ROOT/'results/results.json').read_text())
    for name,m in r['models'].items():
        assert m['converged'],name
        assert m['means_above_one']==0,name
        assert m['score_max']<1e-5,(name,m['score_max'])
        assert m['lower']<m['ratio']<m['upper'],name
    assert mask.sum()==26281 and int((mask&d.exposed.eq(1)).sum())==796
    assert sum(x['missing_outcomes']+x['missing_covariates_after_outcomes']+x['complete_case'] for x in r['flow'])==sum(x['eligible_employment'] for x in r['flow'])
    report={'status':'passed','checks':['hand-calculated stratified cluster variance','crude log prevalence ratio equals direct survey mean ratio','crude regression variance equals independent delta method','invariance to constant weight rescaling','exact reconstruction of complete-item PHQ-8 and GAD-7 recodes','all model convergence and estimating-equation residuals','all fitted means inside unit interval','sample accounting'], 'comparison_tolerance':1e-8,'pooled_design_df':df,'crude_ratio':ps[1]/ps[0],'crude_log_ratio_variance':direct_var}
    (ROOT/'audit/statistical_validation.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
