"""One publication figure, with one exposure scale and direct numeric labels."""
from pathlib import Path
import pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
    d=pd.read_csv(ROOT/'results/models.csv')
    choices=[('Primary','Main analysis'),('Previous-year conditions','Previous-year conditions'),('Exclude 2020–2021','Exclude 2020–2021'),('State-specific trends','State-specific trends'),('Equal state-year weights','Equal state-year weights'),('Through 2025 (11-month unemployment input)','Include 2025*')]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'PsychologicalRecession','axes.unicode_minus':True})
    fig=plt.figure(figsize=(8,4.25),facecolor='white')
    ax=fig.add_axes([.35,.23,.37,.66]);ax.axvline(0,color='#72797d',lw=.9,zorder=0)
    for i,(key,label) in enumerate(choices):
        x=d[(d.model==key)&d.term.isin(['lower_hiring','lag_lower_hiring'])].iloc[0]
        color='#1B5961' if i==0 else '#56616A';y=5-i
        ax.errorbar(x.estimate,y,xerr=[[x.estimate-x.lower],[x.upper-x.estimate]],fmt='o',color=color,ms=6 if i==0 else 4.8,lw=1.5,capsize=3)
        ax.text(-.065,y,label,ha='right',va='center',transform=ax.get_yaxis_transform(),fontweight='bold' if i==0 else 'normal')
        ax.text(1.10,y,f'{x.estimate:+.2f}  ({x.lower:.2f}, {x.upper:.2f})',ha='left',va='center',transform=ax.get_yaxis_transform(),fontsize=9.5)
    ax.set(xlim=(-3,3),ylim=(-.6,5.6),xticks=[-3,-2,-1,0,1,2,3],yticks=[])
    ax.set_xlabel('Difference in frequent mental distress\n(percentage points)',labelpad=10)
    ax.text(1.10,6.05,'Estimate (95% CI)',transform=ax.get_yaxis_transform(),ha='left',fontsize=9.5,fontweight='bold')
    ax.tick_params(axis='x',length=3,color='#72797d')
    for side in ['top','left','right']:ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#72797d')
    fig.text(.04,.96,'Association per one-percentage-point lower hiring rate',ha='left',va='top',fontsize=12,fontweight='bold')
    fig.text(.04,.015,'*2025 unemployment input covers 11 months. Intervals are state-clustered.',ha='left',fontsize=8.5,color='#454B50')
    for ext in ['png','pdf','svg']:
        fig.savefig(ROOT/f'results/figure1.{ext}',dpi=300,metadata=({'Creator':'PsychologicalRecession reproducible analysis','CreationDate':None,'ModDate':None} if ext=='pdf' else {'Date':None} if ext=='svg' else {}))
    svg=ROOT/'results/figure1.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8',newline='\n')
    plt.close(fig)
if __name__=='__main__':main()
