"""Verify frozen source files; download missing ones only when requested."""
from pathlib import Path
import argparse,hashlib,json,urllib.request,os
ROOT=Path(__file__).resolve().parents[1]

def verify(download=False,documents=False):
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    for entry in manifest:
        if not documents and not entry['file'].endswith('.zip'):continue
        path=ROOT/'data/raw'/entry['file']
        if not path.exists():
            if not download:raise FileNotFoundError(f'{path.name} missing. Run python reproduce.py --download')
            path.parent.mkdir(parents=True,exist_ok=True)
            temporary=path.with_suffix(path.suffix+'.partial')
            with urllib.request.urlopen(entry['url'],timeout=120) as response,temporary.open('wb') as output:
                while chunk:=response.read(1024*1024):output.write(chunk)
            if hashlib.sha256(temporary.read_bytes()).hexdigest()!=entry['sha256']:
                raise ValueError(f'Source changed: {entry["url"]}. Partial file retained for review; frozen data not overwritten.')
            os.replace(temporary,path)
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=entry['sha256']:raise ValueError(f'Checksum mismatch: {path}. Do not silently refresh a frozen analysis.')
        print(f'Verified {path.name}: {actual}')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');p.add_argument('--documents',action='store_true')
    a=p.parse_args();verify(a.download,a.documents)
