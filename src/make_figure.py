"""One empirical figure: directly labeled prevalence with survey intervals."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parents[1]
def main():
    r=json.loads((ROOT/'results/results.json').read_text())
    rows=[next(x for x in r['prevalence'] if x['year']=='Pooled' and x['outcome']=='outcome' and x['exposed']==g) for g in [1,0]]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.hashsalt':'PsychologicalRecession-2026','axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#999999','text.color':'#20252A','axes.labelcolor':'#20252A','xtick.color':'#444444'})
    fig,ax=plt.subplots(figsize=(6.5,2.75))
    fig.subplots_adjust(left=.34,right=.975,bottom=.24,top=.92)
    for y,row in zip([1,0],rows):
        p=row['prevalence']*100;lo=row['lower']*100;hi=row['upper']*100
        ax.errorbar(p,y,xerr=[[p-lo],[hi-p]],fmt='o',color='#245766',markersize=7,linewidth=1.6,capsize=4,capthick=1.3)
        ax.text(p,y+.19,f'{p:.1f}%',ha='center',va='bottom',fontweight='bold',fontsize=12)
    ax.set_yticks([1,0],['Unemployed, laid off,\nor looking for work','Employed'])
    ax.tick_params(axis='y',length=0,pad=12)
    ax.set_xlim(0,25);ax.set_ylim(-.52,1.5)
    ax.set_xticks([0,5,10,15,20,25]);ax.xaxis.set_major_formatter(PercentFormatter(100,decimals=0))
    ax.set_xlabel('Moderate or severe anxiety or depressive symptoms',labelpad=10,fontsize=10)
    ax.set_axisbelow(True);ax.grid(axis='x',color='#E7E9EB',linewidth=.6)
    for extension in ['png','svg','pdf']:
        metadata={'Creator':'PsychologicalRecession reproducible figure'}
        if extension=='pdf':metadata.update(CreationDate=None,ModDate=None)
        if extension=='svg':metadata['Date']=None
        fig.savefig(ROOT/f'results/figure1.{extension}',dpi=300,facecolor='white',metadata=metadata)
        if extension=='svg':
            p=ROOT/'results/figure1.svg'
            p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n',encoding='utf8',newline='\n')
    plt.close(fig)
    print('Created figure1.png, figure1.svg, figure1.pdf')

if __name__=='__main__': main()
