"""Build the manuscript from one text source and computed results.

No network calls and no manual numerical transcription in the principal result.
Word pagination is renderer-dependent; the distributed file is separately
rendered and checked. The editable source uses [@key] citation markers.
"""
from pathlib import Path
import json,re,datetime,zipfile,io
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parents[1]

def hyperlink(p,text,url):
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    col=OxmlElement('w:color');col.set(qn('w:val'),'244D5B');pr.append(col)
    size=OxmlElement('w:sz');size.set(qn('w:val'),'21');pr.append(size)
    r.append(pr);t=OxmlElement('w:t');t.text=text;r.append(t);h.append(r);p._p.append(h)

def table(doc,headers,rows,widths):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    for cell,label in zip(t.rows[0].cells,headers):cell.text=label
    for row in rows:
        for cell,text in zip(t.add_row().cells,row):cell.text=str(text)
    pr=t._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'CFD5D9');borders.append(el)
    pr.append(borders)
    margins=OxmlElement('w:tblCellMar')
    for side,val in [('top','90'),('bottom','90'),('left','100'),('right','100')]:
        el=OxmlElement('w:'+side);el.set(qn('w:w'),val);el.set(qn('w:type'),'dxa');margins.append(el)
    pr.append(margins)
    for i,row in enumerate(t.rows):
        rp=row._tr.get_or_add_trPr();rp.append(OxmlElement('w:cantSplit'))
        if i==0:rp.append(OxmlElement('w:tblHeader'))
        for j,cell in enumerate(row.cells):
            cell.width=Inches(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if i==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EDF0F2');cell._tc.get_or_add_tcPr().append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=1.05
                p.paragraph_format.keep_with_next=(i<len(t.rows)-1)
                for run in p.runs:run.font.size=Pt(10.5);run.bold=(i==0)
    return t

def main():
    import pandas as pd
    result=json.loads((ROOT/'results/results.json').read_text(encoding='utf8'))
    models=pd.read_csv(ROOT/'results/models.csv');annual=pd.read_csv(ROOT/'results/annual_burden.csv')
    val=json.loads((ROOT/'results/validation.json').read_text());diag=json.loads((ROOT/'results/model_diagnostics.json').read_text())
    influence=pd.read_csv(ROOT/'results/leave_one_state_out.csv')
    refs={x['key']:x for x in json.loads((ROOT/'manuscript/references.json').read_text(encoding='utf8'))}
    def model(label,term='lower_hiring'):return models[(models.model==label)&(models.term==term)].iloc[0]
    def interval(row):return f"{row.estimate:.2f} ({row.lower:.2f} to {row.upper:.2f})"
    values={'N':f"{result['primary_n']:,}",'NE':f"{result['employed_n']:,}",'SY':str(result['primary_state_years'])}
    for token,label,term in [('H','Primary','lower_hiring'),('C','Competition per opening','competition'),('U','Primary','unemployment_rate'),('LAG','Previous-year conditions','lag_lower_hiring')]:
        m=model(label,term)
        for suffix,k in [('', 'estimate'),('LO','lower'),('HI','upper')]:values[token+suffix]=f'{m[k]:.2f}'
    for year in [2013,2024]:
        for prefix,group in [('P','Out of work'),('E','Employed')]:values[prefix+str(year)]=f'{annual[(annual.year==year)&(annual.group==group)].iloc[0].fmd_percent:.1f}'
    for suffix,key in [('', 'estimate_pp'),('LO','lower_pp'),('HI','upper_pp')]:values['LOG'+suffix]=f"{val['posthoc_logistic'][key]:.2f}"
    values.update(RSD=f"{diag['weighted_residual_exposure_sd']:.2f}",OUTSIDE=f"{val['weighted_fraction_linear_predictions_outside_0_1']*100:.3f}",LOOLO=f'{influence.estimate.min():.2f}',LOOHI=f'{influence.estimate.max():.2f}')
    source=(ROOT/'manuscript/paper.md').read_text(encoding='utf8')
    for key,value in values.items():source=source.replace('{{'+key+'}}',value)
    assert not re.search(r'\{\{.+?\}\}',source)
    order=[]
    def cite(m):
        keys=[x.strip().lstrip('@') for x in m.group(1).split(';')]
        for key in keys:
            assert key in refs,key
            if key not in order:order.append(key)
        return '['+', '.join(str(order.index(k)+1) for k in keys)+']'
    source=re.sub(r'\[(@[^\]]+)\]',cite,source)
    assert set(order)==set(refs),set(refs)-set(order)
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=Inches(.85);sec.bottom_margin=Inches(.85);sec.left_margin=Inches(1);sec.right_margin=Inches(1);sec.footer_distance=Inches(.42)
    for element in list(doc.styles.element.iter()):
        if element.tag==qn('w:pBdr') or (element.tag==qn('w:spacing') and element.getparent().tag==qn('w:rPr')):element.getparent().remove(element)
        elif element.tag==qn('w:rFonts'):
            for attr in list(element.attrib):
                if attr.endswith('Theme'):del element.attrib[attr]
    normal=doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(11.5);normal.font.color.rgb=RGBColor.from_string('111111')
    normal.paragraph_format.line_spacing=1.14;normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.widow_control=True
    for name,size in [('Title',23),('Subtitle',13),('Heading 1',14),('Heading 2',12),('Caption',11)]:
        s=doc.styles[name];s.font.name='Times New Roman';s.font.size=Pt(size);s.font.color.rgb=RGBColor.from_string('111111');s.font.bold=name!='Subtitle';s.font.italic=False
        s.paragraph_format.space_before=Pt(12 if name.startswith('Heading') else 0);s.paragraph_format.space_after=Pt(6);s.paragraph_format.keep_with_next=True
    foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
    doc.core_properties.title='Job seeking as a psychiatric exposure'
    doc.core_properties.subject='Labor-market conditions, mental distress, and the responsibilities of the hiring industry'
    doc.core_properties.author='Jacob E. Thomas';doc.core_properties.keywords='job seeking; labor market; mental distress; public health'
    doc.core_properties.created=doc.core_properties.modified=datetime.datetime(2026,9,29,0,0,0)
    md=[];front=True
    def para(text,style=None):
        p=doc.add_paragraph(text,style=style);md.append(text);return p
    def note(text):
        p=para(text);p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(9)
        for r in p.runs:r.font.size=Pt(10)
    def put_table(headers,rows,widths):
        t=table(doc,headers,rows,widths)
        # Keep rows intact, but allow long tables to continue rather than pushing a whole page.
        for i,row in enumerate(t.rows):
            for cell in row.cells:
                for p in cell.paragraphs:p.paragraph_format.keep_with_next=(i==0)
        md.extend(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |',*['| '+' | '.join(map(str,row))+' |' for row in rows]])
    for block in source.strip().split('\n\n'):
        if block=='@@PAGEBREAK@@':doc.add_page_break();front=False;continue
        if block=='@@TABLE1@@':
            para('Table 1. Labor-market conditions and frequent mental distress','Caption')
            rows=[]
            for label,term,exposure in [('Primary','lower_hiring','1-point lower hiring rate (primary)'),('Primary','unemployment_rate','1-point higher unemployment rate (same model)'),('Competition per opening','competition','Doubling unemployed people per opening (separate model)'),('Job-opening rate','lower_openings','1-point lower job-opening rate (separate model)')]:
                m=model(label,term);rows.append([exposure,f'{m.estimate:.2f}',f'{m.lower:.2f} to {m.upper:.2f}'])
            put_table(['Change in market condition','Distress difference, pp','95% confidence interval'],rows,[3.4,1.35,1.75])
            note('Out-of-work adults aged 18–64, 2013–2024; n = 193,060 in 607 state-years. pp = percentage points. All models include state, year, and demographic terms. Hiring and unemployment appear jointly in the primary model; other exposures are fitted separately. Exposure changes have different units, so coefficient magnitudes should not be ranked as equivalent effects. Confidence intervals are clustered by state.')
            continue
        if block=='@@FIGURE1@@':
            para('Figure 1. Hiring estimates across model specifications','Caption')
            p=doc.add_paragraph();p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(3)
            shape=p.add_run().add_picture(str(ROOT/'results/figure1.png'),width=Inches(6.5))
            shape._inline.docPr.set('descr','Hiring coefficients and 95% confidence intervals for the main model and five sensitivity checks. Intervals cross zero; the lagged estimate has the opposite direction from the same-year estimate.')
            md.append('![Hiring estimates](../results/figure1.png)')
            note('Each point is an adjusted association with frequent mental distress per one-percentage-point lower state hiring rate. Lines show 95% confidence intervals. Positive values indicate more distress; negative values indicate less. The previous-year model uses lagged hiring and unemployment. The 2025 extension uses the published 11-month unemployment input and has different state coverage. These observational estimates are not effects of an intervention.')
            continue
        if block=='@@FLOW@@':
            flows=pd.DataFrame(result['sample_flow']).query('year<=2024');totals=flows.select_dtypes('number').sum()
            rows=[[label,f'{int(totals[key]):,}'] for key,label in [('raw','All public records, 2013–2024'),('states_dc','50 states and District of Columbia'),('age18_64','Age 18–64'),('employed_or_out_of_work','Employed, self-employed, or out of work'),('valid_mental_health','Valid mental-health-days response'),('complete','Complete demographics and positive weight'),('out_of_work','Out of work: primary analysis'),('employed','Employed: contextual analysis')]]
            put_table(['Sequential sample definition','Respondents'],rows,[4.7,1.8]);note('The final two rows partition the complete sample. Counts represent different respondents in repeated annual cross-sections. Year-specific counts, missing states, and the 2025 extension are supplied in the reproducibility files.')
            continue
        if block=='@@EQUATION@@':
            p=para('Pr(Y = 1) = a(state) + g(year) + b × (−H) + c × U + X′d')
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:run.font.name='Cambria';run.font.size=Pt(11)
            continue
        if block=='@@CHECKS@@':
            rows=[]
            specs=[('Primary','Primary model'),('No unemployment adjustment','Without unemployment adjustment'),('Previous-year conditions','Previous-year conditions'),('Exclude 2020–2021','Exclude 2020–2021'),('State-specific trends','State-specific linear trends'),('Equal state-year weights','Equal total weight per state-year'),('Complete-state panel','46 continuously observed states'),('Out of work <1 year','Out of work <1 year'),('Out of work >=1 year','Out of work ≥1 year'),('Employed adults','Employed adults'),('Through 2025 (11-month unemployment input)','Through 2025: 11-month unemployment input')]
            for key,label in specs:
                m=model(key,'lag_lower_hiring' if key=='Previous-year conditions' else 'lower_hiring');rows.append([label,f'{int(m.n):,}',interval(m)])
            log=val['posthoc_logistic'];rows.append(['Logistic average marginal association (post hoc)',values['N'],f"{log['estimate_pp']:.2f} ({log['lower_pp']:.2f} to {log['upper_pp']:.2f})"])
            put_table(['Model or population','Respondents','Difference in distress, pp (95% CI)'],rows,[2.95,1.05,2.5])
            note('All rows use a one-percentage-point lower hiring rate; all except the explicitly unadjusted-for-unemployment row include unemployment. The continuous-days check gave '+interval(model('Poor mental health days'))+' mentally unhealthy days per month. The outcome units in this last estimate are days, not percentage points. Full coefficients, including the unemployment term in every model, are in results/models.csv.')
            continue
        if block=='@@REFERENCES@@':
            doc.add_page_break();para('References','Heading 1')
            for i,key in enumerate(order,1):
                ref=refs[key];p=doc.add_paragraph();p.paragraph_format.left_indent=Inches(.23);p.paragraph_format.first_line_indent=Inches(-.23);p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(6);p.paragraph_format.keep_together=True
                p.add_run(f"{i}. {ref['text']} ");hyperlink(p,ref['url'],ref['url'])
                for run in p.runs:run.font.size=Pt(10.5)
                md.append(f"{i}. {ref['text']} {ref['url']}")
            continue
        if block.startswith('# '):para(block[2:],'Title');continue
        if block.startswith('## '):para(block[3:],'Subtitle' if front else 'Heading 1');continue
        if block.startswith('### '):para(block[4:],'Heading 2');continue
        p=para(block)
        if front:
            p.paragraph_format.space_after=Pt(5)
            if block.startswith(('Correspondence:','Article type:','Keywords:')):
                for run in p.runs:run.font.size=Pt(10)
    target=ROOT/'manuscript/Job_seeking_as_a_psychiatric_exposure.docx';memory=io.BytesIO();doc.save(memory)
    with zipfile.ZipFile(memory) as original,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as out:
        for name in original.namelist():
            info=zipfile.ZipInfo(name,date_time=(2026,9,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;out.writestr(info,original.read(name))
    (ROOT/'manuscript/manuscript.md').write_text('\n\n'.join(md)+'\n',encoding='utf8',newline='\n')
    (ROOT/'audit/citation_order.json').write_text(json.dumps(order,indent=2)+'\n',encoding='utf8',newline='\n')
    print(f'Built {target.name}; {len(order)} references; {len(" ".join(md).split())} words including references and tables')

if __name__=='__main__':main()
