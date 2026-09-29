"""Extract public fixed-width files using the accompanying CDC SAS positions."""
from pathlib import Path
import json,zipfile,numpy as np,pandas as pd,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
LAYOUT=json.loads((ROOT/'data'/'layouts.json').read_text())
STATES={1,2,4,5,6,8,9,10,11,12,13,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,47,48,49,50,51,53,54,55,56}
(ROOT/'data'/'derived').mkdir(exist_ok=True)

def prepare(year):
    layout=LAYOUT[str(year)]
    names={'state':'_STATE','interview_year':'IYEAR','month':'IMONTH','days':'MENTHLTH','employment':'EMPLOY1','age':'_AGEG5YR','sex':next(k for k in ['_SEX','SEXVAR','SEX1','SEX'] if k in layout),'education':'EDUCA','race':next(k for k in ['_RACEGR3','_RACEGR4'] if k in layout),'weight':'_LLCPWT'}
    archive=next((ROOT/'data'/'source_cache').glob(f'{year}_LLCP*'))
    flow={'year':year,'raw':0,'states_dc':0,'age18_64':0,'employed_or_out_of_work':0,'valid_mental_health':0,'complete':0,'out_of_work':0,'employed':0,'interview_outside_year':0}
    samples=[];present=set()
    with zipfile.ZipFile(archive) as z:
        member=z.namelist()[0]
        with z.open(member) as f: line=f.readline(); length=len(line)
        assert z.getinfo(member).file_size%length==0,(year,length)
        dtype=np.dtype({'names':list(names),'formats':['S'+str(layout[k][1]-layout[k][0]) for k in names.values()], 'offsets':[layout[k][0] for k in names.values()],'itemsize':length})
        with z.open(member) as f:
            while block:=f.read(length*25000):
                records=np.frombuffer(block,dtype=dtype)
                a=pd.DataFrame({key:pd.to_numeric(pd.Series(records[key].copy()),errors='coerce') for key in names})
                flow['raw']+=len(a); present.update(a.state.dropna().astype(int).unique())
                a=a[a.state.isin(STATES)];flow['states_dc']+=len(a)
                a=a[a.age.between(1,9)];flow['age18_64']+=len(a)
                a=a[a.employment.isin([1,2,3,4])];flow['employed_or_out_of_work']+=len(a)
                a.loc[a.days==88,'days']=0
                a=a[a.days.between(0,30)];flow['valid_mental_health']+=len(a)
                a=a[a.sex.isin([1,2]) & a.education.between(1,6) & a.race.between(1,5) & (a.weight>0)].copy()
                a.education=a.education.map({1:1,2:1,3:1,4:2,5:3,6:4})
                for key in names:
                    if key!='weight':a[key]=a[key].fillna(0).astype(int)
                a['year']=year;a['fmd']=(a.days>=14).astype(int)
                flow['complete']+=len(a);flow['out_of_work']+=int((a.employment>=3).sum());flow['employed']+=int((a.employment<=2).sum())
                flow['interview_outside_year']+=int((a.interview_year!=year).sum())
                samples.append(a)
    data=pd.concat(samples,ignore_index=True)
    flow['missing_states']=sorted(STATES-present)
    (ROOT/'data'/'derived'/f'flow_{year}.json').write_text(json.dumps(flow,indent=2),encoding='utf8',newline='\n')
    # Collapsing identical design rows exactly preserves weighted OLS cross-products
    # and the state-level score used for clustered variance; n retains original N.
    data['fmd_weighted']=data.fmd*data.weight;data['days_weighted']=data.days*data.weight
    keys=['year','state','employment','age','sex','education','race']
    profiles=data.groupby(keys,observed=True).agg(n=('fmd','size'),weight=('weight','sum'),fmd_weighted=('fmd_weighted','sum'),days_weighted=('days_weighted','sum')).reset_index()
    profiles.to_csv(ROOT/'data'/'derived'/f'profiles_{year}.csv.gz',index=False,lineterminator="\n",float_format='%.12g',compression={'method':'gzip','mtime':0})
    # Small out-of-work microdata subset supports independent replication checks.
    data.loc[data.employment>=3,list(names)+['year','fmd']].to_csv(ROOT/'data'/'derived'/f'out_of_work_{year}.csv.gz',index=False,lineterminator="\n",float_format='%.12g',compression={'method':'gzip','mtime':0})
    print(year,flow, 'profiles',len(profiles),flush=True)
    return flow

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p: flows=list(p.map(prepare,range(2013,2026)))
    (ROOT/'data'/'derived'/'sample_flow.json').write_text(json.dumps(flows,indent=2),encoding='utf8',newline='\n')
    pd.DataFrame(flows).to_csv(ROOT/'data'/'derived'/'sample_flow.csv',index=False,lineterminator="\n")
