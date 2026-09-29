from pathlib import Path
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    d=pd.read_csv(ROOT/'data'/'source_cache'/name,sep='\t',dtype=str).rename(columns=str.strip)
    return d.map(lambda x:x.strip() if isinstance(x,str) else x)
def main():
    s=read('jt.series');v=read('jt.data.1.AllItems')
    s=s[(s.seasonal=='S') & (s.industry_code=='000000') & (s.area_code=='00000') & (s.sizeclass_code=='00') & s.state_code.str.fullmatch(r'\d\d')]
    d=v.merge(s,on='series_id',validate='many_to_one')
    d=d[d.period.isin([f'M{x:02d}' for x in range(1,13)])].copy()
    d['year']=d.year.astype(int);d['state']=d.state_code.astype(int);d['month']=d.period.str[1:].astype(int);d['value']=pd.to_numeric(d.value,errors='coerce')
    d=d[d.year.between(2012,2025)]
    d['measure']=d.dataelement_code+d.ratelevel_code
    assert not d.duplicated(['state','year','month','measure']).any()
    panel=d.pivot(index=['state','year','month'],columns='measure',values='value').reset_index()
    # LAUS annual average unemployment uses unadjusted M13, appropriate for annual controls.
    la=read('la.data.2.AllStatesU');la=la[(la.period=='M13') & la.series_id.str.fullmatch(r'LAUST\d{2}0000000000003')].copy()
    la['state']=la.series_id.str[5:7].astype(int);la['year']=la.year.astype(int);la['unemployment_rate']=pd.to_numeric(la.value,errors='coerce')
    annual=panel.groupby(['state','year']).agg(hires_rate=('HIR','mean'),openings_rate=('JOR','mean'),layoffs_rate=('LDR','mean'),unemployed_per_opening=('UOR','mean'),months=('month','nunique')).reset_index()
    assert (annual.months==12).all(),annual[annual.months!=12]
    assert panel[['HIR','JOR','LDR']].notna().all().all()
    assert panel.loc[panel.year<=2024,'UOR'].notna().all()
    counts=panel.groupby(['state','year']).UOR.count().rename('competition_months').reset_index()
    annual=annual.merge(counts,on=['state','year'],validate='one_to_one')
    annual.loc[annual.competition_months<12,'unemployed_per_opening']=np.nan
    annual=annual.merge(la[['state','year','unemployment_rate']],on=['state','year'],how='left',validate='one_to_one')
    # National LAUS unavailable in all-states file; state rows are the linked analysis.
    assert annual.loc[annual.state!=0,'unemployment_rate'].notna().all()
    annual['lower_hiring']=-annual.hires_rate
    annual['lower_openings']=-annual.openings_rate
    annual['competition']=np.log2(annual.unemployed_per_opening)
    for name in ['lower_hiring','unemployment_rate']:
        annual['lag_'+name]=annual.groupby('state')[name].shift(1)
    annual.to_csv(ROOT/'data'/'derived'/'market_annual.csv',index=False,lineterminator="\n",float_format='%.12g')
    panel.to_csv(ROOT/'data'/'derived'/'market_monthly.csv',index=False,lineterminator="\n",float_format='%.12g')
    print(annual.shape,annual.head().to_string(index=False),flush=True)
if __name__=='__main__':main()
