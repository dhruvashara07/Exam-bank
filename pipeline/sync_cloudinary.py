"""Upload SVG assets to Cloudinary (runs in GitHub Actions, where Cloudinary is reachable).

Needs the secret CLOUDINARY_URL = cloudinary://<api_key>:<api_secret>@<cloud_name>
(copy it from the Cloudinary dashboard, "API Environment variable").

    python3 pipeline/sync_cloudinary.py                 # files changed since BEFORE_SHA (env), else all
    python3 pipeline/sync_cloudinary.py --all           # everything
Public id = igcse/<syl>/<year>-<session>/<pv>/<file name> (matches svg.public_id in the JSON).
"""
import hashlib, os, re, subprocess, sys, time, glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def creds():
    u = urlparse(os.environ['CLOUDINARY_URL'])
    return u.hostname, u.username, u.password


def public_id(path):
    rel = os.path.relpath(path, os.path.join(ROOT, 'assets')).replace('\\', '/')
    return 'igcse/' + rel[:-4]


def changed_files():
    before = os.environ.get('BEFORE_SHA', '')
    if '--all' in sys.argv or not before or set(before) == {'0'}:
        return sorted(glob.glob(os.path.join(ROOT, 'assets', '**', '*.svg'), recursive=True))
    out = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=AM', before, 'HEAD', '--', 'assets'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return [os.path.join(ROOT, p) for p in out if p.endswith('.svg')]


def upload(path, cloud, key, secret):
    pid = public_id(path)
    ts = int(time.time())
    params = {'overwrite': 'true', 'public_id': pid, 'timestamp': ts, 'invalidate': 'true'}
    to_sign = '&'.join(f'{k}={params[k]}' for k in sorted(params)) + secret
    params.update({'api_key': key, 'signature': hashlib.sha1(to_sign.encode()).hexdigest()})
    for attempt in range(4):
        with open(path, 'rb') as f:
            r = requests.post(f'https://api.cloudinary.com/v1_1/{cloud}/image/upload', data=params,
                              files={'file': (os.path.basename(path), f, 'image/svg+xml')}, timeout=60)
        if r.status_code == 200:
            return pid
        if r.status_code in (420, 429, 500, 502, 503, 504):
            time.sleep(2 ** attempt * 3); continue
        raise RuntimeError(f'{pid}: HTTP {r.status_code} {r.text[:200]}')
    raise RuntimeError(f'{pid}: gave up after retries')


if __name__ == '__main__':
    cloud, key, secret = creds()
    files = changed_files()
    print(f'uploading {len(files)} SVGs to {cloud}')
    failed = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(upload, f, cloud, key, secret): f for f in files}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                fut.result()
            except Exception as e:
                failed.append(str(e))
            if i % 250 == 0:
                print(f'  {i}/{len(files)}')
    print(f'done: {len(files) - len(failed)} uploaded, {len(failed)} failed')
    for f in failed[:20]:
        print('  FAILED', f)
    sys.exit(1 if failed else 0)
