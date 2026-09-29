"""Weighted fixed-effect regressions using exactly collapsed respondent profiles.

The sums of X'WX, X'Wy, and state scores equal the uncollapsed respondent analysis.
State-clustered CR1 covariance uses original respondent N, not collapsed-row N.
"""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import json,numpy as np,pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'results').mkdir(exist_ok=True)

def design(d,terms,trends=False):
    columns={'intercept':np.ones(len(d))}
    for term in terms:columns[term]=d[term].to_numpy(float)
    for name in ['state','year','age','sex','education','race']:
        for value in sorted(d[name].unique())[1:]:columns[f'{name}_{value}']=(d[name].to_numpy()==value).astype(float)
    if trends:
        for value in sorted(d.state.unique())[1:]:columns[f'trend_{value}']=(d.state.to_numpy()==value)*(d.year.to_numpy()-2018)
    return np.column_stack(list(columns.values())),list(columns)

def fit(d,terms,*,trends=False,equal=False,outcome='fmd',label='',influence=False):
    d=d.dropna(subset=terms).reset_index(drop=True)
    X,names=design(d,terms,trends);w=d.weight.to_numpy(float)
    if equal:w=w/d.groupby(['state','year']).weight.transform('sum').to_numpy()
    w=w/w.mean();y=d[outcome+'_weighted'].to_numpy()/d.weight.to_numpy()
    p=X.shape[1];groups=sorted(d.state.unique());G=len(groups);N=int(d.n.sum())
    sums=[]
    for group in groups:
        ix=d.state.to_numpy()==group;x=X[ix];wg=w[ix];yg=y[ix]
        sums.append((x.T@(wg[:,None]*x),x.T@(wg*yg),int(d.loc[ix,'n'].sum())))
    A=sum(s[0] for s in sums);b=sum(s[1] for s in sums)
    rank=int(np.linalg.matrix_rank(A));assert rank==p,(label,rank,p)
    bread=np.linalg.inv(A);beta=np.linalg.solve(A,b)
    score=np.vstack([bs-As@beta for As,bs,_ in sums]);meat=score.T@score
    vcov=bread@meat@bread*(G/(G-1))*((N-1)/(N-p))
    se=np.sqrt(np.diag(vcov));crit=stats.t.ppf(.975,G-1);scale=100 if outcome=='fmd' else 1
    estimates=[]
    for term in terms:
        j=names.index(term)
        estimates.append(dict(model=label,term=term,estimate=float(beta[j]*scale),se=float(se[j]*scale),lower=float((beta[j]-crit*se[j])*scale),upper=float((beta[j]+crit*se[j])*scale),p=float(2*stats.t.sf(abs(beta[j]/se[j]),G-1)),n=N,state_years=len(d[['state','year']].drop_duplicates()),clusters=G,parameters=p,outcome=outcome))
    if influence:
        rows=[]
        for state,(As,bs,ns) in zip(groups,sums):
            # A state dummy is zero after removing that state; pseudoinverse handles it.
            sub=np.linalg.pinv(A-As,hermitian=True)@(b-bs)
            rows.append({'omitted_state':int(state),'estimate':float(sub[names.index(terms[0])]*scale)})
        pd.DataFrame(rows).to_csv(ROOT/'results'/'leave_one_state_out.csv',index=False,lineterminator="\n")
        j=names.index(terms[0]);other=np.delete(X,j,axis=1)
        c=np.linalg.solve(other.T@(w[:,None]*other),other.T@(w*X[:,j]))
        residual=X[:,j]-other@c
        checks=dict(weighted_residual_exposure_sd=float(np.sqrt(np.average(residual**2,weights=w))),condition_number=float(np.linalg.cond(A)),prediction_min=float((X@beta).min()),prediction_max=float((X@beta).max()),score_max=float(abs(score.sum(axis=0)).max()),n=N,collapsed_rows=len(d),columns=names)
        (ROOT/'results'/'model_diagnostics.json').write_text(json.dumps(checks,indent=2),encoding='utf8',newline='\n')
        np.savez_compressed(ROOT/'results'/'primary_crossproducts.npz',A=A,b=b,beta=beta,vcov=vcov,state_A=np.stack([s[0] for s in sums]),state_b=np.stack([s[1] for s in sums]),state_n=np.array([s[2] for s in sums]),states=groups,columns=names)
    return estimates

def main():
    profiles=pd.concat([pd.read_csv(ROOT/'data'/'derived'/f'profiles_{y}.csv.gz') for y in range(2013,2026)],ignore_index=True)
    market=pd.read_csv(ROOT/'data'/'derived'/'market_annual.csv')
    d=profiles.merge(market,on=['state','year'],how='left',validate='many_to_one')
    assert d.lower_hiring.notna().all()
    d['group']=np.where(d.employment>=3,'Out of work','Employed')
    agg=d.groupby(['year','group']).agg(n=('n','sum'),weight=('weight','sum'),fmd_weighted=('fmd_weighted','sum'),days_weighted=('days_weighted','sum')).reset_index()
    agg['fmd_percent']=100*agg.fmd_weighted/agg.weight;agg['mental_health_days']=agg.days_weighted/agg.weight
    agg.to_csv(ROOT/'results'/'annual_burden.csv',index=False,lineterminator="\n",float_format='%.12g')
    cells=d.groupby(['state','year','group']).agg(n=('n','sum'),weight=('weight','sum'),fmd_weighted=('fmd_weighted','sum'),days_weighted=('days_weighted','sum')).reset_index()
    cells['fmd_percent']=100*cells.fmd_weighted/cells.weight
    cells.merge(market,on=['state','year'],validate='many_to_one').to_csv(ROOT/'results'/'linked_state_year.csv',index=False,lineterminator="\n",float_format='%.12g')
    base=d[(d.year<=2024)&(d.employment>=3)].copy()
    balanced=base.groupby('state').year.nunique(); balanced=balanced[balanced==12].index
    specs=[
      ('Primary',base,['lower_hiring','unemployment_rate'],{'influence':True}),
      ('No unemployment adjustment',base,['lower_hiring'],{}),
      ('Previous-year conditions',base,['lag_lower_hiring','lag_unemployment_rate'],{}),
      ('Exclude 2020–2021',base[~base.year.isin([2020,2021])],['lower_hiring','unemployment_rate'],{}),
      ('State-specific trends',base,['lower_hiring','unemployment_rate'],{'trends':True}),
      ('Equal state-year weights',base,['lower_hiring','unemployment_rate'],{'equal':True}),
      ('Complete-state panel',base[base.state.isin(balanced)],['lower_hiring','unemployment_rate'],{}),
      ('Out of work <1 year',base[base.employment==4],['lower_hiring','unemployment_rate'],{}),
      ('Out of work >=1 year',base[base.employment==3],['lower_hiring','unemployment_rate'],{}),
      ('Employed adults',d[(d.year<=2024)&(d.employment<=2)],['lower_hiring','unemployment_rate'],{}),
      ('Poor mental health days',base,['lower_hiring','unemployment_rate'],{'outcome':'days'}),
      ('Competition per opening',base,['competition'],{}),
      ('Job-opening rate',base,['lower_openings'],{}),
      ('Through 2025 (11-month unemployment input)',d[d.employment>=3],['lower_hiring','unemployment_rate'],{})]
    rows=[]
    for label,frame,terms,kwargs in specs:
        rows.extend(fit(frame,terms,label=label,**kwargs));print(label,rows[-len(terms)],flush=True)
    result=pd.DataFrame(rows);result.to_csv(ROOT/'results'/'models.csv',index=False,lineterminator="\n",float_format='%.12g')
    meta={'primary_years':[2013,2024],'primary_n':int(base.n.sum()),'employed_n':int(d[(d.year<=2024)&(d.employment<=2)].n.sum()),'primary_state_years':len(base[['state','year']].drop_duplicates()),'primary_states':int(base.state.nunique()),'balanced_states':list(map(int,balanced)),'models':result.to_dict('records'),'sample_flow':json.loads((ROOT/'data'/'derived'/'sample_flow.json').read_text())}
    (ROOT/'results'/'results.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf8',newline='\n')
if __name__=='__main__':main()
