"""Verify frozen inputs; optionally retrieve the exact public-source vintage."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,shutil,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def verify_frozen():
    records=json.loads((ROOT/'data/frozen_manifest.json').read_text())
    for name,expected in records.items():
        path=ROOT/name
        if not path.exists() or sha(path)!=expected:raise ValueError(f'Frozen input changed or absent: {name}')
    print(f'PASS: {len(records)} frozen input checksums')

def verify_layouts():
    layouts=json.loads((ROOT/'data/layouts.json').read_text())
    for row in json.loads((ROOT/'data/source_manifest.json').read_text())['files']:
        if row['kind']!='layout':continue
        path=ROOT/'data/layouts'/row['filename']
        assert sha(path)==row['sha256'],path
        if path.suffix.lower()=='.zip':
            with zipfile.ZipFile(path) as z:text=z.read(z.namelist()[0]).decode('latin1')
        else:text=path.read_text(encoding='latin1')
        parsed={m[0]:[int(m[1])-1,int(m[2] or m[1])] for m in re.findall(r'^\s*([_A-Z0-9]+)\s+\$?(\d+)(?:-(\d+))?(?:\s|$)',text,re.M)}
        for key,value in layouts[str(row['year'])].items():assert parsed[key]==value,(row['year'],key,value,parsed.get(key))
    print('PASS: all fixed-width positions agree with the 13 official SAS layouts')

def sources(download=False):
    cache=ROOT/'data/source_cache';cache.mkdir(exist_ok=True)
    records=json.loads((ROOT/'data/source_manifest.json').read_text())['files']
    for row in records:
        path=cache/row['filename']
        if not path.exists():
            layout=ROOT/'data/layouts'/row['filename'];snapshot=ROOT/'data/source_snapshot'/(row['filename']+'.gz')
            if row['kind']=='layout' and layout.exists():shutil.copyfile(layout,path)
            elif row['kind']=='market' and snapshot.exists():
                with gzip.open(snapshot,'rb') as src,path.open('wb') as dest:shutil.copyfileobj(src,dest)
            elif download:
                partial=path.with_name(path.name+'.partial')
                try:
                    request=urllib.request.Request(row['url'],headers={'User-Agent':'PsychologicalRecession-public-data-reproduction/1.0'})
                    with urllib.request.urlopen(request,timeout=120) as response,partial.open('wb') as dest:shutil.copyfileobj(response,dest)
                    if partial.stat().st_size!=row['bytes'] or sha(partial)!=row['sha256']:
                        raise ValueError(f'Source vintage changed: {row["url"]}. Expected SHA-256 {row["sha256"]}. Frozen analysis inputs remain available; do not silently substitute a revised release.')
                    partial.replace(path)
                finally:
                    if partial.exists():partial.unlink()
            else:raise FileNotFoundError(f'Missing {path.name}; run reproduce.py --from-source --download, or supply the matching official file in data/source_cache/')
        if path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:raise ValueError(f'Source checksum mismatch: {path.name}')
        print('Verified',path.name,flush=True)
    verify_layouts()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');p.add_argument('--sources',action='store_true');a=p.parse_args()
    verify_frozen();verify_layouts()
    if a.sources or a.download:sources(a.download)
