"""Build the review website (GitHub Pages) from bank/ and review/.

    python3 site/build.py OUT_DIR [--img BASE]

OUT_DIR gets index.html, config.js and data/:
    data/papers.json        one row per paper (status, marks, flags)
    data/p/<paper id>.json  the paper's meta + every question JSON (exact SVG pieces, editable content,
                            mark scheme pieces)
    data/queue.json         the to-check list (review/queue.json + papers waiting for approval)
Pictures are not copied: the page loads each SVG from BASE + public_id + '.svg'
(Cloudinary in the Action: https://res.cloudinary.com/<cloud>/image/upload/). For a local preview pass
--img ./ and put a link OUT_DIR/question_bank -> bank.
"""
import argparse, glob, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline'))
import paths

REPO = os.environ.get('GITHUB_REPOSITORY', 'dhruvashara07/Exam-bank')


def flags(q):
    return len(q.get('review', {}).get('reasons', []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--img', default=None)
    a = ap.parse_args()
    img = a.img
    if img is None:
        from sync_mongo import cloud_name
        img = f'https://res.cloudinary.com/{cloud_name()}/image/upload/'
    out = a.out
    os.makedirs(os.path.join(out, 'data', 'p'), exist_ok=True)
    approvals = paths.approvals()
    queue = json.load(open(os.path.join(paths.ROOT, 'review', 'queue.json'))) \
        if os.path.exists(os.path.join(paths.ROOT, 'review', 'queue.json')) else []
    rows = []
    for pj in paths.paper_files():
        meta = json.load(open(pj))
        pid = paths.paper_id(meta)
        qs = []
        for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
            q = json.load(open(qf))
            q.pop('text', None)
            qs.append(q)
        ap_ = approvals.get(pid)
        paper_flags = [x for x in queue if x['id'] == pid]
        rows.append({
            'id': pid, 'code': meta['paper_code'], 'year': meta['year'], 'session': meta['session'],
            'paper': meta['paper'], 'variant': meta['variant'], 'type': meta.get('paper_type'),
            'mcq': meta.get('is_mcq', False), 'questions': len(qs), 'marks': meta.get('marks_found'),
            'total': meta.get('total_marks'), 'ms': meta.get('mark_scheme') != 'missing',
            'erratum': bool(meta.get('erratum')),
            'status': 'approved' if ap_ else 'pending',
            'approved_at': ap_.get('at') if ap_ else None,
            'flagged': sum(1 for q in qs if flags(q)) + len(paper_flags),
        })
        with open(os.path.join(out, 'data', 'p', pid + '.json'), 'w') as f:
            json.dump({'meta': meta, 'approval': ap_, 'paper_flags': paper_flags, 'questions': qs},
                      f, ensure_ascii=False, separators=(',', ':'))
    rows.sort(key=lambda r: (-r['year'], r['session'], r['code']))
    with open(os.path.join(out, 'data', 'papers.json'), 'w') as f:
        json.dump(rows, f, separators=(',', ':'))
    with open(os.path.join(out, 'data', 'queue.json'), 'w') as f:
        json.dump(queue, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(out, 'config.js'), 'w') as f:
        f.write('window.BANK = ' + json.dumps({'img': img, 'repo': REPO}) + ';\n')
    shutil.copy(os.path.join(HERE, 'index.html'), os.path.join(out, 'index.html'))
    open(os.path.join(out, '.nojekyll'), 'w').close()
    print(f'{len(rows)} papers, {sum(r["questions"] for r in rows)} questions -> {out}')


if __name__ == '__main__':
    main()
