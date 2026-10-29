"""Upload SVG assets to Cloudinary (runs in GitHub Actions, where Cloudinary is reachable).

Needs the secret CLOUDINARY_URL = cloudinary://<api_key>:<api_secret>@<cloud_name>
(copy it from the Cloudinary dashboard, "API Environment variable").

    python3 pipeline/sync_cloudinary.py                 # files changed since BEFORE_SHA (env), else all
    python3 pipeline/sync_cloudinary.py --all           # everything
Public id = repo path without '.svg' (bank/cambridge-igcse/0625-physics/2025-MJ/p41/q01/question/...),
so Cloudinary folders mirror the repo. Matches svg.public_id in the JSON.
"""
import hashlib, os, re, subprocess, sys, time, glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests

sys.path.insert(0, os.path.dirname(__file__))
import paths
ROOT = paths.ROOT


def creds():
    """CLOUDINARY_URL (cloudinary://KEY:SECRET@CLOUD) or the three separate secrets
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET."""
    raw = os.environ.get('CLOUDINARY_URL', '').strip()
    if raw.startswith('cloudinary://'):
        u = urlparse(raw)
        return u.hostname, u.username, u.password
    c, k, s = (os.environ.get(n, '').strip() for n in ('CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET'))
    if c and k and s:
        return c, k, s
    sys.exit('Cloudinary secrets missing: add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET '
             '(or one CLOUDINARY_URL) in GitHub -> Settings -> Secrets and variables -> Actions')


def public_id(path):
    return paths.public_id(path)


def changed_files():
    before = os.environ.get('BEFORE_SHA', '')
    if '--all' in sys.argv or not before or set(before) == {'0'}:
        return paths.svg_files()
    out = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=AM', before, 'HEAD', '--', 'bank'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return [os.path.join(ROOT, p) for p in out if p.endswith('.svg')]


def upload(path, cloud, key, secret):
    pid = public_id(path)
    ts = int(time.time())
    params = {'overwrite': 'true', 'public_id': pid, 'timestamp': ts, 'invalidate': 'true',
              'asset_folder': pid.rsplit('/', 1)[0]}     # same folders in the Media Library
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


def existing(cloud, key, secret):
    """{public_id: (bytes, etag)} of everything already in Cloudinary under question_bank/ (Admin API)."""
    out, cursor = {}, None
    while True:
        params = {'prefix': paths.CLOUD_ROOT + '/', 'max_results': 500}
        if cursor:
            params['next_cursor'] = cursor
        r = requests.get(f'https://api.cloudinary.com/v1_1/{cloud}/resources/image/upload',
                         params=params, auth=(key, secret), timeout=60)
        if r.status_code != 200:
            note('warning', f'could not list existing files (HTTP {r.status_code}); uploading all')
            return {}
        j = r.json()
        for x in j.get('resources', []):
            out[x['public_id']] = (x.get('bytes'), x.get('etag'))
        cursor = j.get('next_cursor')
        if not cursor:
            return out


def note(level, msg):
    """Print, and also as a GitHub annotation (readable through the API even when logs are not)."""
    print(msg)
    if os.environ.get('GITHUB_ACTIONS'):
        print(f'::{level}::{msg}'.replace('\n', ' '))


if __name__ == '__main__':
    cloud, key, secret = creds()
    files = changed_files()
    have = existing(cloud, key, secret) if files else {}
    todo = []
    for f in files:
        b = open(f, 'rb').read()
        prev = have.get(public_id(f))
        if prev and (prev[1] == hashlib.md5(b).hexdigest() or (prev[1] is None and prev[0] == len(b))):
            continue                       # already there, unchanged
        todo.append(f)
    print(f'{len(files)} SVGs to check, {len(files) - len(todo)} already in Cloudinary, uploading {len(todo)} to {cloud}')
    failed = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(upload, f, cloud, key, secret): f for f in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                fut.result()
            except Exception as e:
                failed.append(str(e))
            if i % 250 == 0:
                print(f'  {i}/{len(todo)}')
    note('notice' if not failed else 'error',
         f'Cloudinary: {len(files)} checked, {len(files) - len(todo)} unchanged, '
         f'{len(todo) - len(failed)} uploaded, {len(failed)} failed')
    kinds = {}
    for f in failed:
        k = f.split(': ', 1)[1][:80] if ': ' in f else f[:80]
        kinds.setdefault(k, []).append(f.split(':', 1)[0])
    for k, ids in list(kinds.items())[:8]:
        note('error', f'{len(ids)} x {k}  e.g. {ids[0]}')
    sys.exit(1 if failed else 0)
