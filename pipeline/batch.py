"""Batches: every upload is a batch; the tracker shows where each paper of it is.

    python3 pipeline/batch.py new "<name>" <papers...>   # papers as 0625/2025-MJ/41 or 0625_2025MJ_41
    python3 pipeline/batch.py status [batch id]           # table of stages
    python3 pipeline/batch.py json                        # all batches with stages (for the website)

Stages (worked out from the files, never typed by hand, so they cannot get out of date):
  uploaded        PDF stored (raw/manifest.json)
  processed       cut into questions (bank/.../paper.json)
  auto_checked    pipeline/checks.py ran on it            review/checks/<paper>.json
  claude_checked  Claude looked at every page            review/claude/<paper>.json
  your_review     items of it are in an open review round review/rounds/<n>.json (status open)
  approved        review/approvals/<paper>.json
  published       in MongoDB with that approval           review/published.json
A paper can also be 'needs_fix' (Claude found a problem; it stays there until the pipeline is fixed).
"""
import datetime, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import paths

STAGES = ['uploaded', 'processed', 'auto_checked', 'claude_checked', 'your_review', 'approved', 'published']


def pid_of(s):
    """'0625/2025-MJ/41' -> '0625_2025MJ_41'; ids pass through."""
    m = re.fullmatch(r'(\w+)/(\d{4})-(\w\w)/(\d\d)', s)
    return f'{m.group(1)}_{m.group(2)}{m.group(3)}_{m.group(4)}' if m else s


def load_json(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def papers_index():
    return {paths.paper_id(json.load(open(pj))): pj for pj in paths.paper_files()}


def open_round_items():
    out = {}
    for f in sorted(glob.glob(os.path.join(paths.ROUNDS, '*.json'))):
        r = json.load(open(f))
        if r.get('status') == 'open':
            for it in r.get('items', []):
                out.setdefault('_'.join(it['id'].split('_')[:3]), []).append(r['round'])
    return out


def _cut(pj):
    from golden import cut_hash
    return cut_hash(pj)


def stage_of(pid, index=None, approvals=None, published=None, rounds=None):
    index = index if index is not None else papers_index()
    approvals = approvals if approvals is not None else paths.approvals()
    published = published if published is not None else load_json(paths.PUBLISHED, {})
    rounds = rounds if rounds is not None else open_round_items()
    if pid in approvals:
        if published.get(pid, {}).get('approved_at') == approvals[pid].get('at'):
            return 'published'
        return 'approved'
    if pid in rounds:
        return 'your_review'
    cl = load_json(os.path.join(paths.CLAUDE_CHECKS, pid + '.json'), None)
    if cl and pid in index and cl.get('cut') and cl['cut'] != _cut(index[pid]):
        cl = None                        # re-cut since Claude looked: needs a new look
    if cl:
        return 'needs_fix' if cl.get('result') == 'needs_fix' else 'claude_checked'
    if os.path.exists(os.path.join(paths.CHECKS, pid + '.json')):
        return 'auto_checked'
    if pid in index:
        return 'processed'
    return 'uploaded'


def new(name, papers):
    os.makedirs(paths.BATCHES, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    bid = 'b' + now.strftime('%Y%m%d-%H%M')
    k = 1
    while os.path.exists(os.path.join(paths.BATCHES, bid + '.json')):
        k += 1; bid = 'b' + now.strftime('%Y%m%d-%H%M') + f'-{k}'
    rec = {'id': bid, 'name': name, 'created': now.strftime('%Y-%m-%dT%H:%MZ'),
           'papers': sorted({pid_of(p) for p in papers})}
    with open(os.path.join(paths.BATCHES, bid + '.json'), 'w') as f:
        json.dump(rec, f, indent=1)
    print(bid, len(rec['papers']), 'papers')
    return rec


def all_batches():
    index, approvals = papers_index(), paths.approvals()
    published, rounds = load_json(paths.PUBLISHED, {}), open_round_items()
    out = []
    for f in sorted(glob.glob(os.path.join(paths.BATCHES, '*.json'))):
        b = json.load(open(f))
        b['stages'] = {p: stage_of(p, index, approvals, published, rounds) for p in b['papers']}
        b['counts'] = {s: sum(1 for v in b['stages'].values() if v == s) for s in STAGES + ['needs_fix']}
        out.append(b)
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'new':
        new(sys.argv[2], sys.argv[3:])
    elif cmd == 'json':
        print(json.dumps(all_batches(), indent=1))
    else:
        for b in all_batches():
            if len(sys.argv) > 2 and b['id'] != sys.argv[2]:
                continue
            c = ', '.join(f'{k} {v}' for k, v in b['counts'].items() if v)
            print(f"{b['id']}  {b['name']}  ({len(b['papers'])} papers): {c}")
