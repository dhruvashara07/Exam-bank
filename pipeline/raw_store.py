"""Original PDFs live in GitHub Releases, not in git (keeps the repo small and fast).

One release per syllabus and year:  tag  raw-0625-2015  holds  0625_2015-MJ_qp_11.pdf, 0625_2015-MJ_ms_11.pdf, ...
raw/manifest.json (in git) lists every stored PDF:  {"0625/2015-MJ/qp_11.pdf": {tag, asset, size, sha256}}
Locally the files sit in raw/<syl>/<year>-<session>/ as before (git-ignored).

    python3 pipeline/raw_store.py upload             # (GitHub Action) upload raw/ PDFs missing from Releases
    python3 pipeline/raw_store.py fetch [papers...]  # download PDFs from Releases into raw/ (all, or e.g. 0625/2015-MJ/41)
    python3 pipeline/raw_store.py status             # what is local / stored
Needs the `gh` CLI with access to the repo (GH_TOKEN in Actions).
"""
import glob, hashlib, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from paths import ROOT

REPO = os.environ.get('GITHUB_REPOSITORY', 'dhruvashara07/Exam-bank')
MANIFEST = os.path.join(ROOT, 'raw', 'manifest.json')


def load():
    return json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}


def save(m):
    with open(MANIFEST, 'w') as f:
        json.dump(dict(sorted(m.items())), f, indent=1)


def rel(path):
    return os.path.relpath(path, os.path.join(ROOT, 'raw')).replace('\\', '/')


def asset_of(r):
    """'0625/2015-MJ/qp_11.pdf' -> ('raw-0625-2015', '0625_2015-MJ_qp_11.pdf')"""
    syl, folder, name = r.split('/')
    return f'raw-{syl}-{folder[:4]}', f'{syl}_{folder}_{name}'


def gh(*args, check=True):
    return subprocess.run(['gh', *args], capture_output=True, text=True, check=check)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def local_pdfs():
    return sorted(glob.glob(os.path.join(ROOT, 'raw', '*', '*', '*.pdf')))


def upload():
    m = load()
    tags = {}
    new = 0
    for p in local_pdfs():
        r = rel(p)
        digest = sha256(p)
        if r in m and m[r]['sha256'] == digest:
            continue
        tag, asset = asset_of(r)
        if tag not in tags:
            v = gh('release', 'view', tag, '-R', REPO, '--json', 'assets', check=False)
            if v.returncode != 0:
                gh('release', 'create', tag, '-R', REPO, '--title', tag,
                   '--notes', f'Original past-paper PDFs ({tag[4:]}). Managed by pipeline/raw_store.py.')
                tags[tag] = {}
            else:
                tags[tag] = {a['name']: a['size'] for a in json.loads(v.stdout)['assets']}
        if tags[tag].get(asset) == os.path.getsize(p):          # already stored (an earlier run)
            m[r] = {'tag': tag, 'asset': asset, 'size': os.path.getsize(p), 'sha256': digest}
            continue
        tmp = os.path.join('/tmp', asset)
        subprocess.run(['cp', p, tmp], check=True)
        gh('release', 'upload', tag, tmp, '-R', REPO, '--clobber')
        os.remove(tmp)
        m[r] = {'tag': tag, 'asset': asset, 'size': os.path.getsize(p), 'sha256': digest}
        new += 1
        if new % 50 == 0:
            print(f'  {new} uploaded'); save(m)
    save(m)
    print(f'{new} PDFs uploaded to Releases; manifest has {len(m)}')
    return new


def wanted(r, sels):
    if not sels:
        return True
    syl, folder, name = r.split('/')
    pv = re.search(r'_(\d\d)\.pdf$', name)
    for s in sels:
        parts = s.split('/')
        if len(parts) == 3 and parts[0] == syl and parts[1] == folder and (pv and parts[2] == pv.group(1)):
            return True
        if len(parts) == 2 and parts[0] == folder and pv and parts[1] == pv.group(1):
            return True
        if len(parts) == 1 and parts[0] in (folder, folder[:4], syl):
            return True
    return False


def fetch(sels=()):
    m = load()
    todo = [(r, v) for r, v in m.items() if wanted(r, sels)
            and not (os.path.exists(os.path.join(ROOT, 'raw', r)) and os.path.getsize(os.path.join(ROOT, 'raw', r)) == v['size'])]
    by_tag = {}
    for r, v in todo:
        by_tag.setdefault(v['tag'], []).append((r, v))
    got = 0
    for tag, items in by_tag.items():
        tmpdir = f'/tmp/raw_{tag}'
        os.makedirs(tmpdir, exist_ok=True)
        if len(items) > 20:       # most of a release: one call
            gh('release', 'download', tag, '-R', REPO, '-D', tmpdir, '--clobber', '-p', '*.pdf')
        else:
            for r, v in items:
                gh('release', 'download', tag, '-R', REPO, '-D', tmpdir, '--clobber', '-p', v['asset'])
        for r, v in items:
            src = os.path.join(tmpdir, v['asset'])
            dst = os.path.join(ROOT, 'raw', r)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(src):
                os.replace(src, dst); got += 1
            else:
                print('MISSING in release:', tag, v['asset'])
    print(f'{got} PDFs fetched from Releases')
    return got


def merge_into(path):
    """Merge this checkout's manifest into another manifest file (used to carry it over to main)."""
    other = json.load(open(path)) if os.path.exists(path) else {}
    other.update(load())
    with open(path, 'w') as f:
        json.dump(dict(sorted(other.items())), f, indent=1)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'merge-into':
        merge_into(sys.argv[2]); sys.exit(0)
    if cmd == 'upload':
        upload()
    elif cmd == 'fetch':
        fetch(sys.argv[2:])
    else:
        m = load(); loc = {rel(p) for p in local_pdfs()}
        print(f'manifest: {len(m)} stored, local: {len(loc)}, local but not stored: {len(loc - set(m))}, '
              f'stored but not local: {len(set(m) - loc)}')
