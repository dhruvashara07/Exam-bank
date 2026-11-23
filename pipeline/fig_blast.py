"""Blast radius of a figure-rule change (extract.diagrams / store.fit_crop) on EVERY 0607 question figure (M3 lesson:
an 'arrowhead = graph' rule would have changed ~100 approved crops; ERROR_PATTERNS 251 lesson).

    git worktree add /tmp/oldtree HEAD                                   # the code before your change
    python3 pipeline/fig_blast.py run /tmp/oldtree /tmp/figs_old.json    # old code (PDFs from this repo's raw/)
    python3 pipeline/fig_blast.py run . /tmp/figs_new.json               # new code
    python3 pipeline/fig_blast.py diff /tmp/figs_old.json /tmp/figs_new.json
    FL=<file with pdf paths> limits a run to some papers. Needs every 0607 PDF fetched (raw_store.py fetch). ~15 min / 2 CPUs.
Each figure: [page, extract box, stored (fit_crop) box]. Look at every BIG change on the page before pushing.
"""
import glob
import json
import os
import re
import sys
from multiprocessing import Pool

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw', '0607')


def one(f):
    import warnings
    warnings.filterwarnings('ignore')
    import pymupdf, extract, store
    m = re.search(r'/0607/(\d{4})-([A-Z]{2})/qp_(\d+)\.pdf', f)
    try:
        meta, qs = extract.extract(f, '0607', m.group(1), m.group(2), m.group(3))
    except Exception as e:
        return f, {'err': str(e)[:100]}
    d = pymupdf.open(f)
    res = {}

    def walk(n, acc):
        acc += n.get('figures', []) or []
        for p in n.get('parts', []) or []:
            walk(p, acc)
    for q in qs:
        acc = []
        walk(q, acc)
        for fg in acc:
            try:
                fb = store.fit_crop(d[fg['page'] - 1], pymupdf.Rect(fg['bbox']), maths=True)
            except Exception:
                fb = None
            res[fg.get('id', '?')] = [fg['page'], [round(v, 1) for v in fg['bbox']], [round(v, 1) for v in fb] if fb else None]
    return f, res


def run(tree, out):
    sys.path.insert(0, os.path.join(os.path.abspath(tree), 'pipeline'))
    os.chdir(tree)
    fs = open(os.environ['FL']).read().split() if os.environ.get('FL') else sorted(glob.glob(os.path.join(RAW, '*', 'qp_*.pdf')))
    with Pool(4) as p:
        r = dict(p.map(one, fs, chunksize=4))
    json.dump(r, open(out, 'w'))
    print('done', len(r))


def diff(a_, b_):
    o, n = json.load(open(a_)), json.load(open(b_))
    for f in sorted(set(o) | set(n)):
        a, b = o.get(f, {}), n.get(f, {})
        if 'err' in a or 'err' in b:
            print('ERR', f, a.get('err'), b.get('err'))
            continue
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                A, B = a.get(k), b.get(k)
                big = not A or not B or max(abs(x - y) for x, y in zip((A[2] or A[1]), (B[2] or B[1]))) > 3
                print(('BIG ' if big else '    ') + f.split('/0607/')[1], k.split('_', 3)[-1], A and (A[2] or A[1]), '->',
                      B and (B[2] or B[1]))


if __name__ == '__main__':
    {'run': run, 'diff': diff}[sys.argv[1]](*sys.argv[2:4])
