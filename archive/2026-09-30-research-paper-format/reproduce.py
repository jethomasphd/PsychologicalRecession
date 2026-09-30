"""Rebuild linked analyses and publication; optionally rebuild from public sources."""
from pathlib import Path
import argparse,hashlib,io,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from fetch_data import verify_frozen,verify_layouts,sources

def run(name):
    env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='2';env['OMP_NUM_THREADS']='2';env['PYTHONIOENCODING']='utf-8';env['MPLBACKEND']='Agg'
    subprocess.run([sys.executable,str(ROOT/'src'/name)],cwd=ROOT,env=env,check=True)

def verify_archives():
    original=json.loads((ROOT/'audit/archive_sha256.json').read_text())
    snapshot=ROOT/'archive/2026-09-29-employment-status-revision'
    record=json.loads((snapshot/'SNAPSHOT.json').read_text());previous=record['files'];stored=record.get('stored_paths',{})
    for folder,records in [(ROOT/'archive',original),(snapshot,previous)]:
        for name,expected in records.items():
            path=folder/(stored.get(name,name) if folder==snapshot else name)
            with path.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
            assert actual==expected,f'Archive changed: {folder/name}'
    extra=json.loads((snapshot/'EXTRA_EXTRACTS.json').read_text())
    for name,expected in extra.items():assert hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==expected,name
    print(f'PASS: {len(original)} original and {len(previous)} previous-revision files, plus {len(extra)} auxiliary extracts, preserved byte for byte')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from-source',action='store_true',help='Regenerate inputs from the CDC ASCII files and frozen official BLS files')
    p.add_argument('--download',action='store_true',help='Download missing public source files; implies --from-source')
    p.add_argument('--analysis-only',action='store_true',help='Skip manuscript and figure generation')
    a=p.parse_args();verify_frozen();verify_layouts();verify_archives()
    if a.from_source or a.download:
        sources(a.download)
        # Compare regenerated values, not gzip headers or platform line endings.
        import pandas as pd
        before={path.name:path.read_bytes() for path in (ROOT/'data/derived').iterdir()}
        try:
            run('prepare_brfss.py');run('prepare_market.py')
            for name,content in sorted(before.items()):
                new=ROOT/'data/derived'/name
                if name.endswith('.json'):assert json.loads(content)==json.loads(new.read_text()),name
                else:
                    old=pd.read_csv(io.BytesIO(content),compression='gzip' if name.endswith('.gz') else None)
                    pd.testing.assert_frame_equal(old,pd.read_csv(new),check_exact=False,rtol=1e-10,atol=1e-10,obj=name)
            print('PASS: all regenerated public-source inputs reproduce the frozen values')
        finally:
            # Preserve the canonical serialized inputs after checking equivalence.
            for name,content in before.items():(ROOT/'data/derived'/name).write_bytes(content)
    run('analyze.py');run('validate.py')
    if not a.analysis_only:run('make_figure.py');run('build_manuscript.py');run('audit_references.py')
    print('PASS: linked analysis and independent respondent-level validation. PDF rendering is a separate layout step; see README.')

if __name__=='__main__':main()
