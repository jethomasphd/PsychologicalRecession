"""Build readable audit records from frozen verification evidence."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def main():
    refs=json.loads((ROOT/'manuscript/references.json').read_text(encoding='utf8'))
    order=json.loads((ROOT/'audit/citation_order.json').read_text())
    keyed={r['key']:r for r in refs}
    old=json.loads((ROOT/'audit/original_reference_registry_audit.json').read_text(encoding='utf8'))
    metadata=json.loads((ROOT/'audit/retained_registry_metadata.json').read_text(encoding='utf8'))
    verified={x['key'] for x in metadata}
    assert all(r['key'] in verified for r in refs if 'doi.org' in r['url'])
    details={18:'Supplied DOI returned 404 in Crossref. Unverified; excluded. This is not proof that no related paper exists.',28:'Registry title includes “A systematic review and thematic synthesis of qualitative evidence from Western economies.” Earlier online publication and later issue date need distinction. Excluded from the new argument.',33:'DOI resolves, but original author list does not match. Registry authors are Frank, Mustard, Smith, Siddiqi, Cheng, Burdorf, and Rugulies. Excluded.',34:'DOI resolves to “Contribution to the study on the ‘right to disconnect’ from work. Are France and Spain examples for other countries and EU law?” Original title is inaccurate. Excluded.',58:'Supplied BMJ Open DOI returned 404. A related 2023 Thern article is in Journal of Epidemiology and Community Health 77:755–761, DOI 10.1136/jech-2023-220817, with a different author list. Do not silently equate records. Excluded.',62:'Supplied DOI 10.1016/j.jpubeco.2024.105170 resolves to “Spillover effects of specialized high schools,” not a Finnish basic-income study. The associated policy claim was removed.'}
    lines=['# Reference audit','Verification date: 2026-09-29. The revised manuscript contains 15 references: 12 journal articles, two official NHIS documentation records, and the reproducibility repository. Every retained source has a stated claim and limit. DOI records establish identity, not claim support. Review depth is recorded honestly; this is not a full-text systematic review or a formal retraction-database audit.','## Retained references']
    for i,key in enumerate(order,1):
        r=keyed[key]
        lines += [f'### {i}. {r["text"]}',f'Identifier: {r["url"]}',f'Evidence reviewed: [{r["review_scope"]}]({r["evidence_url"]}).',f'Supports: {r["supports"]}',f'Limit: {r["limits"]}']
    lines+=['## Original bibliography','All 64 original entries were screened. All 35 supplied DOI records were queried; 33 returned registry metadata and two returned 404. Metadata retrieval does not clear a citation for reuse. Non-DOI entries were not treated as verified simply because a recognizable organization or book was named. Unneeded or incompletely specified sources were removed rather than used to sustain numerical claims. The original manuscript is preserved without corrections in archive/.','### Material errors and unresolved records']
    for k,v in details.items():lines.append(f'- Original reference {k}: {v}')
    lines+=['### Entry-by-entry disposition','| Original number | Original citation | Identity check and disposition |','| --- | --- | --- |']
    retained_dois={r['url'].split('doi.org/')[-1].lower():r['key'] for r in refs if 'doi.org' in r['url']}
    for x in old:
        doi=(x.get('doi') or '').lower()
        if x['id'] in details:status=details[x['id']]
        elif doi in retained_dois:status='Retained after separate source/claim review; see '+retained_dois[doi]+' above. Bibliographic details rebuilt from verified records.'
        elif 'metadata retrieved' in x['verification']:status='DOI metadata retrieved; not retained because it is unnecessary for the revised claims. No full claim verification asserted.'
        else:status='No complete verification established from the supplied record; excluded from the revised manuscript.'
        lines.append('| '+str(x['id'])+' | '+x['original_reference'].replace('|','/')+' | '+status+' |')
    (ROOT/'audit/reference_audit.md').write_text('\n\n'.join(lines[:lines.index('### Entry-by-entry disposition')+1])+'\n\n'+'\n'.join(lines[lines.index('### Entry-by-entry disposition')+1:])+'\n',encoding='utf8',newline='\n')
    print(f'Built audit for {len(refs)} retained and {len(old)} original references')

if __name__=='__main__':main()
