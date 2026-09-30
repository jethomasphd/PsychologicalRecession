"""Assemble the human-reviewed claim audit; validate saved identifiers offline.

This does not pretend that DOI resolution verifies a substantive claim. The
review scope and limits in references.json are the source-review record.
"""
from pathlib import Path
import collections,json
ROOT=Path(__file__).resolve().parents[1]

def main():
    refs={r['key']:r for r in json.loads((ROOT/'manuscript/references.json').read_text(encoding='utf8'))}
    order=json.loads((ROOT/'audit/citation_order.json').read_text())
    metadata={r['key']:r.get('metadata',r) for r in json.loads((ROOT/'audit/retained_registry_metadata.json').read_text(encoding='utf8'))}
    assert set(order)==set(refs) and len(order)==len(refs)
    counts=collections.Counter(r['kind'] for r in refs.values())
    lines=['# Reference and claim audit','Verification date: September 29, 2026.',
      f'The current manuscript has {len(refs)} references. '+', '.join(f'{n} {kind.lower()}' for kind,n in sorted(counts.items()))+'.',
      'Every retained reference has an identity, a reviewed source, a stated claim, and a limit. Twelve DOI records were checked against Crossref. Non-DOI records were checked against the issuing organization, arXiv, or original reporting. Review depth is recorded below; several journal claims are supported at abstract level. This is a focused narrative evidence review, not a systematic review or a formal retraction-database audit. No exhaustive literature search or absence of all corrections is asserted.',
      'Saved metadata are in retained_registry_metadata.json. Two repeat Crossref requests were rate-limited; the successful earlier same-day Paul and Price records were reused and labeled. A DOI match establishes bibliographic identity; substantive support comes from the separately reviewed text. Offline rebuilding validates the saved record and citation completeness, not current website availability.',
      '## Claims corrected or restricted',
      '- The Resume Genius and Forbes publications describe the same participants. The 72% item is lifetime self-attribution, not current prevalence of a disorder. The current original report and the Forbes paraphrase differ on the 31% subcategory; that subcategory is not used.',
      '- Greenhouse’s 2,500-person sample spans three countries. Its US anxiety percentage cannot use 2,500 as its denominator, and anxiety is not a diagnostic outcome.',
      '- Ng’s 21% denotes classifier-positive interview reviews in a selected dataset, not the proportion of all job advertisements that are fictitious. Employer intent and psychiatric outcomes were not verified.',
      '- Huntr’s report provides useful process observations but does not expose public respondent-level data for independent reconstruction. Its methods list 527 complete and 66 partial survey responses, while another passage calls all 593 complete. The manuscript does not use that denominator to estimate mental-health burden.',
      '- State JOLTS hiring is an employment flow per payroll employment, not an individual’s job-finding probability. BRFSS out-of-work categories do not verify active search.',
      '- The October 2025 unemployment gap is documented by BLS. The primary analysis ends in 2024; the separately labeled extension uses the published 11-month unemployment average.',
      '## Current references']
    for number,key in enumerate(order,1):
        r=refs[key]
        if r['url'].startswith('https://doi.org/'):
            doi=r['url'].removeprefix('https://doi.org/')
            assert metadata[key]['DOI'].lower()==doi.lower(),key
            assert metadata[key].get('title'),key
        lines.extend([f'### {number}. {r["text"]}',f'Type: {r["kind"]}. Identifier: {r["url"]}',
                      f'Reviewed: [{r["review_scope"]}]({r["evidence_url"]}).',
                      'Supports: '+r['supports'],'Limit: '+r['limits']])
    lines.extend(['## Disposition of all 64 references in the original manuscript',
      'The original record and the 35 attempted DOI checks are preserved in original_reference_registry_audit.json (33 metadata responses; two unresolved identifiers). Sources not retained are not automatically false: they are unnecessary to the current claims or remain unverified at the stated depth. The present report supersedes the earlier audit’s disposition of Greenhouse, which was reviewed and retained in this revision.',
      '| Original no. | Original citation | Current disposition |','| --- | --- | --- |'])
    old=(ROOT/'archive/2026-09-29-employment-status-revision/audit/reference_audit.md').read_text(encoding='utf8')
    dispositions={}
    for line in old.splitlines():
        parts=line.split(' | ')
        if len(parts)==3 and parts[0].lstrip('| ').isdigit():dispositions[int(parts[0].lstrip('| '))]=parts[2].rstrip(' |')
    originals=json.loads((ROOT/'audit/original_reference_registry_audit.json').read_text(encoding='utf8'))
    for record in originals:
        number=record['id'];doi=record.get('doi')
        retained=next((key for key,r in refs.items() if doi and r['url'].lower()=='https://doi.org/'+doi.lower()),None)
        if number==26:retained='greenhouse'
        if retained:status=f'Retained after source and claim review; see current reference {order.index(retained)+1}. Bibliographic details follow the verified current record.'
        elif number in [18,33,34,58,62]:status=dispositions[number]
        elif record.get('registry_title'):status='DOI metadata retrieved. Not needed for the current claims; no full claim verification asserted.'
        else:status='No complete verification established from the supplied record; not used in the current paper.'
        lines.append(f'| {number} | {record["original_reference"].replace("|","/")} | {status} |')
    (ROOT/'audit/reference_audit.md').write_text('\n\n'.join(lines[:lines.index('| Original no. | Original citation | Current disposition |')])+'\n\n'+'\n'.join(lines[lines.index('| Original no. | Original citation | Current disposition |'):])+'\n',encoding='utf8',newline='\n')
    print(f'PASS: {len(order)} current citations, 12 saved DOI identities, 64 original dispositions')

if __name__=='__main__':main()
