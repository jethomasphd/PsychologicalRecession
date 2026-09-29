"""Reproduce analysis, checks, figure, manuscript, and audit without network."""
from pathlib import Path
import argparse,subprocess,sys,hashlib,json,platform
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--download',action='store_true',help='Fetch absent official files, checking frozen SHA-256 hashes');p.add_argument('--analysis-only',action='store_true')
    a=p.parse_args()
    def run(script,*args):
        subprocess.run([sys.executable,str(ROOT/script),*args],cwd=ROOT,check=True)
    run('src/fetch_data.py',*(['--download'] if a.download else []))
    run('src/analyze.py');run('src/check_analysis.py')
    if not a.analysis_only:
        run('src/make_figure.py');run('src/build_manuscript.py');run('src/audit_references.py')
    original=json.loads((ROOT/'audit/archive_sha256.json').read_text())
    for name,expected in original.items():
        assert hashlib.sha256((ROOT/'archive'/name).read_bytes()).hexdigest()==expected,f'Archive changed: {name}'
    print(f'PASS: reproduced results and verified all {len(original)} archived originals. PDF rendering is a separate optional step.')

if __name__=='__main__':main()
