"""Reproduce the empirical illustration from frozen official NHIS files."""
from pathlib import Path
import json, zipfile, hashlib, sys, platform
import numpy as np
import pandas as pd
import patsy
from survey import prevalence, fit_poisson, contrast, design_covariance

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data/raw'
OUT = ROOT/'results'
OUT.mkdir(exist_ok=True)
YEARS = (2022, 2025)


def load():
    frames=[]
    for year in YEARS:
        path=RAW/f'adult{str(year)[-2:]}csv.zip'
        with zipfile.ZipFile(path) as z:
            name=next(n for n in z.namelist() if n.lower().endswith('.csv'))
            needed={'WTFA_A','PSTRAT','PPSU','EMPWHYNOT_A','EMPWRKLSW1_A','PHQCAT_A','GADCAT_A','AGEP_A','SEX_A','HISPALLP_A','EDUCP_A','REGION','DISAB3_A','EMPLASTWK_A','EMPNOWRK_A'}
            needed.update({f'PHQ8{j}_A' for j in range(1,9)})
            needed.update({f'GAD7{j}_A' for j in range(1,8)})
            f=pd.read_csv(z.open(name), usecols=lambda c:c in needed, low_memory=False).copy()
        f['year']=year
        frames.append(f)
    d=pd.concat(frames,ignore_index=True).copy()
    d['weight']=d.WTFA_A/len(YEARS)
    d['exposed']=np.where(d.EMPWHYNOT_A.eq(1),1,np.where(d.EMPWRKLSW1_A.eq(1),0,np.nan))
    assert not (d.EMPWHYNOT_A.eq(1)&d.EMPWRKLSW1_A.eq(1)).any()
    for name,col in [('depression','PHQCAT_A'),('anxiety','GADCAT_A')]:
        d[name]=np.where(d[col].isin([1,2,3,4]),d[col].isin([3,4]).astype(float),np.nan)
    d['outcome']=np.where(d.depression.notna()&d.anxiety.notna(),
                          (d.depression.eq(1)|d.anxiety.eq(1)).astype(float),np.nan)
    d['age_group']=pd.cut(d.AGEP_A,[17,29,44,54,64],labels=['18-29','30-44','45-54','55-64'])
    d['sex']=d.SEX_A.where(d.SEX_A.isin([1,2]))
    d['race_ethnicity']=d.HISPALLP_A.map({1:'Hispanic',2:'NH White',3:'NH Black',4:'NH Asian',5:'NH other',6:'NH other',7:'NH other'})
    d['education']=d.EDUCP_A.map({0:'Less than high school',1:'Less than high school',2:'Less than high school',3:'High school or GED',4:'High school or GED',5:'Some college or associate',6:'Some college or associate',7:'Some college or associate',8:'Bachelor or higher',9:'Bachelor or higher',10:'Bachelor or higher'})
    d['region']=d.REGION.where(d.REGION.isin([1,2,3,4]))
    d['eligible']=d.AGEP_A.between(18,64)&d.exposed.notna()
    covs=['age_group','sex','race_ethnicity','education','region','year']
    d['complete']=d.eligible&d.outcome.notna()&d[covs].notna().all(axis=1)
    # Independently reconstruct complete-item scales for sensitivity analysis.
    valid_items=[]
    for scale,count in [('PHQ8',8),('GAD7',7)]:
        cols=[f'{scale}{j}_A' for j in range(1,count+1)]
        valid=d[cols].isin([1,2,3,4]).all(axis=1)
        score=(d[cols]-1).sum(axis=1).where(valid)
        d[scale+'_score']=score
        valid_items.append(valid)
        category=pd.cut(score,[-1,4,9,14,100],labels=[1,2,3,4]).astype(float)
        existing=d.PHQCAT_A if scale=='PHQ8' else d.GADCAT_A
        assert (category.loc[valid]==existing.loc[valid]).all(), 'NCHS score reconstruction disagrees'
    d['all_items']=valid_items[0]&valid_items[1]
    return d


def estimate(d, mask, formula, outcome='outcome'):
    X=patsy.dmatrix(formula, d.loc[mask],return_type='dataframe')
    assert len(X)==int(mask.sum())
    m=fit_poisson(d,mask,X,outcome)
    c=np.zeros(X.shape[1]); c[X.columns.get_loc('exposed')]=1
    e=contrast(m,c)
    e.update({k:v for k,v in m.items() if k not in ['coef','covariance']})
    e['terms']=list(X.columns)
    e['coefficients']=[dict(term=n,estimate=float(b),se=float(np.sqrt(m['covariance'][i,i]))) for i,(n,b) in enumerate(zip(X.columns,m['coef']))]
    return e,m,X


def main():
    d=load()
    mask=d.complete
    adjusted='exposed+C(year)+C(age_group)+C(sex)+C(race_ethnicity)+C(education)+C(region)'
    result={'years':list(YEARS),'source_sha256':{f'adult{str(y)[-2:]}csv.zip':hashlib.sha256((RAW/f'adult{str(y)[-2:]}csv.zip').read_bytes()).hexdigest() for y in YEARS}}
    result['flow']=[]
    for year in YEARS:
        y=d.year.eq(year)
        age=y&d.AGEP_A.between(18,64)
        eligible=y&d.eligible
        observed=eligible&d.outcome.notna()
        result['flow'].append({'year':year,'sample_adults':int(y.sum()),'aged_18_64':int(age.sum()),'eligible_employment':int(eligible.sum()),'both_symptom_recodes':int(observed.sum()),'complete_case':int((y&mask).sum()),'exposed_complete':int((y&mask&d.exposed.eq(1)).sum()),'comparator_complete':int((y&mask&d.exposed.eq(0)).sum()),'missing_outcomes':int((eligible&d.outcome.isna()).sum()),'missing_covariates_after_outcomes':int((observed&~mask).sum())})
    prevalence_rows=[]
    for year in [*YEARS,'Pooled']:
        for exposed in [0,1]:
            for outcome in ['outcome','depression','anxiety']:
                sub=mask&d.exposed.eq(exposed)
                if year!='Pooled': sub &= d.year.eq(year)
                if year=='Pooled':
                    row=prevalence(d,sub,outcome)
                else:
                    one=d.loc[d.year.eq(year)].copy().reset_index(drop=True)
                    one['weight']=one.WTFA_A
                    row=prevalence(one,one.complete&one.exposed.eq(exposed),outcome)
                row.update(year=year,exposed=exposed,outcome=outcome)
                prevalence_rows.append(row)
    result['prevalence']=prevalence_rows
    result['models']={}
    for label,formula in [('unadjusted','exposed'),('adjusted',adjusted)]:
        e,_,_=estimate(d,mask,formula)
        result['models'][label]=e
    for outcome in ['depression','anxiety']:
        result['models'][outcome]=estimate(d,mask,adjusted,outcome)[0]
    result['models']['all_items']=estimate(d,mask&d.all_items,adjusted)[0]
    narrow=mask&(d.exposed.eq(1)|d.EMPLASTWK_A.eq(1)|d.EMPNOWRK_A.eq(1))
    result['models']['narrow_comparator']=estimate(d,narrow,adjusted)[0]
    result['models']['no_disability']=estimate(d,mask&d.DISAB3_A.eq(2),adjusted)[0]
    e,m,X=estimate(d,mask,adjusted.replace('exposed+C(year)','exposed*C(year)'))
    result['models']['interaction']=e
    c=np.zeros(X.shape[1]); c[X.columns.get_loc('exposed:C(year)[T.2025]')]=1
    result['interaction']=contrast(m,c)
    c[X.columns.get_loc('exposed')]=1
    result['year_specific_adjusted']={'2022':contrast(m,np.array([1. if n=='exposed' else 0. for n in X.columns])), '2025':contrast(m,c)}
    # Simple characteristics table uses the same complete-case sample.
    chars=[]
    for group in [0,1]:
        sub=mask&d.exposed.eq(group)
        for variable in ['age_group','sex','race_ethnicity','education','region','year']:
            for category in sorted(d.loc[sub,variable].dropna().unique()):
                numerator=d.loc[sub&d[variable].eq(category),'weight'].sum()
                chars.append({'exposed':group,'variable':variable,'category':str(category),'weighted_percent':float(100*numerator/d.loc[sub,'weight'].sum()),'n':int((sub&d[variable].eq(category)).sum())})
    result['characteristics']=chars
    # No assumptions about missing symptom outcomes: assign all 0 versus all 1.
    missing=[]
    for group in [0,1]:
        sub=d.eligible&d.exposed.eq(group)
        denom=d.loc[sub,'weight'].sum()
        event=d.loc[sub&d.outcome.eq(1),'weight'].sum()
        unknown=d.loc[sub&d.outcome.isna(),'weight'].sum()
        missing.append({'exposed':group,'eligible_n':int(sub.sum()),'missing_n':int((sub&d.outcome.isna()).sum()),'weighted_missing_percent':float(100*unknown/denom),'prevalence_lower_bound':float(event/denom),'prevalence_upper_bound':float((event+unknown)/denom)})
    result['missing_bounds']=missing
    import scipy,statsmodels,matplotlib
    result['software']={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__,'matplotlib':matplotlib.__version__,'patsy':patsy.__version__}
    (OUT/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',newline='\n')
    pd.DataFrame(prevalence_rows).to_csv(OUT/'prevalence.csv',index=False,float_format='%.12g',lineterminator='\n')
    pd.DataFrame(result['flow']).to_csv(OUT/'sample_flow.csv',index=False,lineterminator='\n')
    pd.DataFrame(chars).to_csv(OUT/'sample_characteristics.csv',index=False,float_format='%.12g',lineterminator='\n')
    rows=[]
    for name,e in result['models'].items():
        rows.append({'model':name,**{k:e[k] for k in ['n','events','ratio','lower','upper','p','converged','max_mean','means_above_one','df']}})
    pd.DataFrame(rows).to_csv(OUT/'models.csv',index=False,float_format='%.12g',lineterminator='\n')
    # Analysis input is a reproducible public-data derivative, not restricted data.
    cols=['year','PSTRAT','PPSU','weight','AGEP_A','exposed','outcome','depression','anxiety','age_group','sex','race_ethnicity','education','region','eligible','complete','all_items','DISAB3_A','EMPLASTWK_A','EMPNOWRK_A']
    d[cols].to_csv(OUT/'analysis_input.csv.gz',index=False,compression={'method':'gzip','mtime':0},lineterminator='\n')
    print(json.dumps({k:result[k] for k in ['flow','interaction','year_specific_adjusted','missing_bounds','software']},indent=2))
    print(pd.DataFrame(rows).to_string(index=False))


if __name__=='__main__': main()
