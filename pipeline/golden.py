"""Golden set: papers whose cutting was checked by eye. A pipeline change must not change them by surprise.

    python3 pipeline/golden.py check            # compare the bank with tests/golden/ (exit 1 if a cut changed)
    python3 pipeline/golden.py add <paper ids>  # store / refresh the fingerprint of checked papers

A fingerprint holds, per question: marks, every piece (part, page, box), figure crops, mark-scheme rows
and answer, plus a hash of the editable content. Changed pieces/marks/mark scheme = FAIL (look at the
paper again before accepting: `add` it after checking). Changed figures or editable text = CHANGED
(fine when it is an improvement you looked at).
"""
import glob, hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
import paths

GOLDEN = os.path.join(paths.ROOT, 'tests', 'golden')


def nodes(n):
    yield n
    for k in n.get('parts', []):
        yield from nodes(k)


def fingerprint(pj):
    meta = json.load(open(pj))
    out = {'paper': paths.paper_id(meta), 'marks': meta.get('marks_found'), 'questions': {}}
    for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
        q = json.load(open(qf))
        out['questions'][q['id']] = {
            'marks': q['marks'],
            'answer': q.get('answer'),
            'pieces': [[n.get('path') or str(q['number']), s['page'], [round(v, 1) for v in s['bbox']]]
                       for n in nodes(q) for s in n.get('segments', [])],
            'markscheme': [[n.get('path') or str(q['number']), m['label'], m.get('codes', [])]
                           for n in nodes(q) for m in n.get('mark_scheme', [])],
            'figures': [[f['id'], [round(v, 1) for v in f['bbox']]] for f in q.get('figures', [])],
            'editable': hashlib.sha1(json.dumps([n.get('content') for n in nodes(q)], sort_keys=True,
                                                ensure_ascii=False).encode()).hexdigest()[:12],
        }
    return out


def cut_hash(pj):
    """Hash of what a check approves: the exact pieces, marks, answers and mark-scheme rows of a paper
    (not figure crops or the editable text). Same hash = same cut, so an approval or a Claude check stays valid."""
    fp = fingerprint(pj)
    core = {q: {k: v[k] for k in ('marks', 'answer', 'pieces', 'markscheme')} for q, v in fp['questions'].items()}
    return hashlib.sha1(json.dumps([fp['marks'], core], sort_keys=True).encode()).hexdigest()[:16]


def paper_file(pid):
    for pj in paths.paper_files():
        if paths.paper_id(json.load(open(pj))) == pid:
            return pj
    sys.exit(f'no paper {pid}')


def compare(old, new):
    fail, changed = [], []
    if old['marks'] != new['marks']:
        fail.append(f"paper marks {old['marks']} -> {new['marks']}")
    for qid in sorted(set(old['questions']) | set(new['questions'])):
        a, b = old['questions'].get(qid), new['questions'].get(qid)
        if a is None or b is None:
            fail.append(f'{qid} {"added" if a is None else "missing"}'); continue
        for k in ('marks', 'answer', 'pieces', 'markscheme'):
            if a[k] != b[k]:
                fail.append(f'{qid} {k} changed')
        for k in ('figures', 'editable'):
            if a[k] != b[k]:
                changed.append(f'{qid} {k}')
    return fail, changed


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    os.makedirs(GOLDEN, exist_ok=True)
    if cmd == 'add':
        for pid in sys.argv[2:]:
            with open(os.path.join(GOLDEN, pid + '.json'), 'w') as f:
                json.dump(fingerprint(paper_file(pid)), f, ensure_ascii=False, indent=0)
            print('stored', pid)
        sys.exit(0)
    bad = 0
    files = sorted(glob.glob(os.path.join(GOLDEN, '*.json')))
    for gf in files:
        old = json.load(open(gf))
        fail, changed = compare(old, fingerprint(paper_file(old['paper'])))
        status = 'FAIL' if fail else ('changed' if changed else 'same')
        bad += bool(fail)
        print(f"{old['paper']}: {status}" + (f"  {'; '.join(fail[:6])}" if fail else '') +
              (f"  ({len(changed)} figure/editable changes)" if changed else ''))
    print(f'golden set: {len(files)} papers, {bad} with changed cuts')
    sys.exit(1 if bad else 0)
