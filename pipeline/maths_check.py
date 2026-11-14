"""Strict automatic checks for maths papers (PLAYBOOK 2b-2d, round 27). Run on EVERY paper before Claude's pass 2.

    python3 pipeline/maths_check.py <paper ids...>        # prints every hit, writes review/claude/<pid>.maths_check.json

Checks (each hit is a problem to fix as a pattern, or to look at on the contact sheet):
  ms_words    every printed word of the question's mark-scheme rows is in our table once (missing / extra words)
  ms_overflow a word of our table that runs past its column edge or the table edge
  ms_overlap  two words of one row drawn on top of each other
  ms_font     more than one font family in our table (MS_TABLE_RULES 25)
  fig_overlap two figure crops of one question overlapping (one diagram cut in two)
  not_to_scale 'NOT TO SCALE' left as question text while the part has a diagram (rule: inside the picture)
"""
import collections, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

W = 523.0
LABEL = re.compile(r'^\d{1,2}(\([a-z]\))*(\([ivx]+\))*$|^\([a-z]\)$|^\([ivx]+\)$|^\d{1,2}$')


def words(ts):
    return [t['t'].strip() for t in ts if t.get('t', '').strip()]


def check_question(rec):
    hits = []
    mp = rec.get('ms_p')
    if mp and 'maths' in (mp.get('modes') or {}):
        src = collections.Counter()
        seen = set()
        for p in rec['parts']:
            for r in p.get('ms', []):
                for u in r['layout']:
                    k = (u['src']['page'], tuple(u['src']['box']))
                    if k in seen:
                        continue
                    seen.add(k)
                    src.update(w for w in words(u['text']) if not LABEL.match(w))
        ours = collections.Counter()
        rows = mp['rows'][1:]
        if rows and any(t['t'] == 'Total' for t in rows[-1]['text']):
            rows = rows[:-1]
        for v in rows:
            ours.update(w for w in words(v['text']) if not LABEL.match(w))
        miss, extra = src - ours, ours - src
        if any(v.get('images') for v in rows):       # a cell kept as its printed picture: its words are in the picture
            miss = collections.Counter()
        if miss:
            hits.append(('ms_words', 'missing: ' + ' '.join(list(miss.elements())[:8])))
        if extra:
            hits.append(('ms_words', 'extra: ' + ' '.join(list(extra.elements())[:8])))
        edges = (mp.get('info') or {}).get('new_edges') or []
        for v in rows:
            for t in v['text']:
                x1 = t['x'] + t['w']
                if x1 > W + 0.5:
                    hits.append(('ms_overflow', f"'{t['t']}' past the table edge")); break
                nxt = [e for e in edges if e > t['x'] + 0.5]
                if nxt and x1 > nxt[0] + 1.0:
                    hits.append(('ms_overflow', f"'{t['t']}' crosses a column rule")); break
            ts = [t for t in v['text'] if t.get('t', '').strip() and t['w'] > 2]
            found = None
            for i, a in enumerate(ts):
                for b in ts[i + 1:]:
                    if abs(a['y'] - b['y']) < 1.5 and min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x']) > 0.4 * min(a['w'], b['w']):
                        found = (a, b); break
                if found:
                    break
            if found:
                hits.append(('ms_overlap', f"'{found[0]['t']}' / '{found[1]['t']}'"))
        fams = {t.get('f') for v in mp['rows'] for t in v['text'] if t.get('f') in ('serif', 'sans', 'mono')}
        if len(fams) > 1:
            hits.append(('ms_font', ' + '.join(sorted(fams))))
    figs = [f for f in rec.get('figures', [])]
    for i, a in enumerate(figs):
        for b in figs[i + 1:]:
            sa, sb = a.get('source', {}), b.get('source', {})
            if sa.get('page') == sb.get('page') and sa.get('box') and sb.get('box'):
                A, B = sa['box'], sb['box']
                if min(A[2], B[2]) - max(A[0], B[0]) > 2 and min(A[3], B[3]) - max(A[1], B[1]) > 2:
                    hits.append(('fig_overlap', f"{a['id'].split('_')[-1]} / {b['id'].split('_')[-1]}"))
    for p in rec['parts']:
        txt = ' '.join(t['t'] for u in p['layout'] for t in u['text'])
        if re.search(r'NOT\s+TO\s+SCALE', txt) and any(u.get('figs') for u in p['layout']):
            hits.append(('not_to_scale', p['path']))
    return hits


def check_paper(pid):
    out = []
    for f in sorted(glob.glob(os.path.join(paths.store_dir(pid), 'q*.json'))):
        rec = json.load(open(f))
        if rec.get('stub'):
            continue
        for kind, d in check_question(rec):
            out.append({'id': rec['id'], 'kind': kind, 'detail': d})
    os.makedirs(paths.CLAUDE_CHECKS, exist_ok=True)
    json.dump(out, open(os.path.join(paths.CLAUDE_CHECKS, f'{pid}.maths_check.json'), 'w'), indent=1)
    return out


if __name__ == '__main__':
    tot = collections.Counter()
    for pid in sys.argv[1:]:
        for h in check_paper(pid):
            tot[h['kind']] += 1
            print(f"  {h['id']}  {h['kind']}: {h['detail']}")
    print('maths_check:', dict(tot) or 'no hits')
