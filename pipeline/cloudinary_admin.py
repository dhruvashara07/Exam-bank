"""Cloudinary housekeeping (runs in GitHub Actions: .github/workflows/cloudinary.yml, where the secrets are).

    python3 pipeline/cloudinary_admin.py list                        # read only: usage + every folder, counts and size
    python3 pipeline/cloudinary_admin.py delete <prefix> <confirm>   # delete everything whose public id starts with
                                                                     # <prefix>/ ; <confirm> must repeat <prefix>
The list is printed and written to out/cloudinary_list.json (uploaded as the run's artifact) and as annotations.
Delete never runs without the confirm word, never on an empty prefix, and only under question_bank/ (our folder:
paths.CLOUD_ROOT) - other folders in the account (the website's own images) are never touched.
"""
import collections, json, os, sys, time
import requests

sys.path.insert(0, os.path.dirname(__file__))
import paths
from sync_cloudinary import creds, note

TYPES = ('image', 'raw', 'video')


def listing(cloud, key, secret):
    out = []
    for rtype in TYPES:
        cursor = None
        while True:
            params = {'max_results': 500, 'type': 'upload'}
            if cursor:
                params['next_cursor'] = cursor
            r = requests.get(f'https://api.cloudinary.com/v1_1/{cloud}/resources/{rtype}', params=params,
                             auth=(key, secret), timeout=60)
            if r.status_code != 200:
                note('warning', f'list {rtype}: HTTP {r.status_code} {r.text[:150]}')
                break
            j = r.json()
            for x in j.get('resources', []):
                out.append({'id': x['public_id'], 'type': rtype, 'format': x.get('format'), 'bytes': x.get('bytes', 0),
                            'created': x.get('created_at', '')[:10]})
            cursor = j.get('next_cursor')
            if not cursor:
                break
    return out


def summary(items):
    by = collections.defaultdict(lambda: [0, 0])
    for x in items:
        parts = x['id'].split('/')
        top = parts[0] if len(parts) > 1 else '(root)'
        if top == paths.CLOUD_ROOT and len(parts) > 4:          # question_bank/cambridge-igcse/0625-physics/<session>
            top = '/'.join(parts[:4])
        by[(top, x['type'], x['format'])][0] += 1
        by[(top, x['type'], x['format'])][1] += x['bytes'] or 0
    return sorted(([k[0], k[1], k[2], v[0], round(v[1] / 1e6, 2)] for k, v in by.items()), key=lambda r: r[0])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    cloud, key, secret = creds()
    os.makedirs(os.path.join(paths.ROOT, 'out'), exist_ok=True)
    if cmd == 'list':
        u = requests.get(f'https://api.cloudinary.com/v1_1/{cloud}/usage', auth=(key, secret), timeout=60)
        usage = u.json() if u.status_code == 200 else {'error': u.status_code}
        items = listing(cloud, key, secret)
        rows = summary(items)
        dates = sorted(x['created'] for x in items if x['created'])
        res = {'usage': {k: usage.get(k) for k in ('plan', 'storage', 'bandwidth', 'resources', 'credits', 'last_updated')},
               'total_files': len(items), 'total_mb': round(sum(x['bytes'] or 0 for x in items) / 1e6, 2),
               'created_from': dates[0] if dates else None, 'created_to': dates[-1] if dates else None,
               'folders': rows}
        json.dump(res, open(os.path.join(paths.ROOT, 'out', 'cloudinary_list.json'), 'w'), indent=1)
        print(json.dumps(res, indent=1))
        note('notice', f"Cloudinary: {res['total_files']} files, {res['total_mb']} MB, created {res['created_from']} .. {res['created_to']}; "
                       f"usage {json.dumps(res['usage'])[:300]}")
        for r in rows[:40]:
            note('notice', f'{r[0]} [{r[1]}/{r[2]}]: {r[3]} files, {r[4]} MB')
        return
    if cmd == 'delete':
        if len(sys.argv) < 4 or sys.argv[2] != sys.argv[3]:
            sys.exit('delete needs <prefix> <prefix again> (confirm)')
        prefix = sys.argv[2].strip().strip('/')
        if not prefix or not (prefix == paths.CLOUD_ROOT or prefix.startswith(paths.CLOUD_ROOT + '/')):
            sys.exit(f'refused: only {paths.CLOUD_ROOT}/... may be deleted')
        total = 0
        for rtype in TYPES:
            while True:            # the Admin API deletes up to 1000 per call; repeat until nothing is left
                r = requests.delete(f'https://api.cloudinary.com/v1_1/{cloud}/resources/{rtype}/upload',
                                    params={'prefix': prefix + '/'}, auth=(key, secret), timeout=120)
                if r.status_code != 200:
                    note('warning', f'delete {rtype}: HTTP {r.status_code} {r.text[:150]}')
                    break
                n = len(r.json().get('deleted', {}))
                total += n
                if not r.json().get('partial') or n == 0:
                    break
                time.sleep(1)
        note('notice', f'Cloudinary: deleted {total} files under {prefix}/')
        return
    sys.exit(__doc__)


if __name__ == '__main__':
    main()
