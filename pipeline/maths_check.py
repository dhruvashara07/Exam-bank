"""Strict automatic checks for maths papers (PLAYBOOK 2b-2d, round 27). Run on EVERY paper before Claude's pass 2.

    python3 pipeline/maths_check.py <paper ids...>        # prints every hit, writes review/claude/<pid>.maths_check.json

Checks (each hit is a problem to fix as a pattern, or to look at on the contact sheet):
  q_rule      no full-width separator rule at the bottom of a question part
  ms_mode     the mark scheme was laid out by ms_maths (any fallback is a hit)
  ms_words    every printed word of the question's mark-scheme rows is in our table once (missing / extra words)
  ms_overflow a word of our table that runs past its column edge or the table edge
  ms_overlap  two words of one row drawn on top of each other
  ms_font     more than one font family in our table (MS_TABLE_RULES 25)
  fig_overlap two figure crops of one question overlapping (one diagram cut in two)
  not_to_scale 'NOT TO SCALE' left as question text while the part has a diagram (rule: inside the picture)
Appearance checks (round 28: the checks above test content only; 25 of 34 round-28 items were appearance faults):
  ms_stretch  a word of our table stored wider / narrower than its font draws it (guessed widths stretched labels)
  ms_edge     ink of a row closer than 2 pt to the row's top or bottom rule (fractions touching the rule)
  ms_piccut   a mark-scheme cell picture with ink on its border (picture cut)
  q_font      sans text in a maths question (maths papers print Times; 2025 'AllAndNone' was read as sans)
  fig_cut     a diagram crop whose edge runs through ink on the page (diagram cut)
  fig_text    a question sentence ('(ii) Sketch ...') inside a diagram crop
"""
import collections, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

W = 523.0
LABEL = re.compile(r'^\d{1,2}(\([a-z]\))*(\([ivx]+\))*$|^\([a-z]\)$|^\([ivx]+\)$|^\d{1,2}$')



def _rule_at(v, x, y):
    """Does row v draw a vertical rule at x through height y (a note band / merged row has none there)?"""
    import re as _re
    for l in v.get('lines', []):
        n = [float(a) for a in _re.findall(r'-?\d+(?:\.\d+)?', l.get('d', ''))]
        xs, ys = n[0::2], n[1::2]
        if xs and max(xs) - min(xs) < 1.3 and abs((max(xs) + min(xs)) / 2 - x) < 1.5 and min(ys) - 2 <= y <= max(ys) + 2:
            return True
    return False

def words(ts):
    return [t['t'].strip() for t in ts if t.get('t', '').strip()]


def check_question(rec):
    hits = []
    mp = rec.get('ms_p')
    if mp and 'maths' not in (mp.get('modes') or {}):
        hits.append(('ms_mode', f"mark scheme not laid out by ms_maths: {list((mp.get('modes') or {}))}"))   # (round 30: a
        # fallback layout of 2014 MJ 43 q9 was never checked, because every check below needs the maths layout)
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
                    pos = set()             # text printed twice on top of itself counts once (as in ms_maths._items)
                    for t in u['text']:
                        w = t.get('t', '').strip()
                        key = (w, round(t.get('x', 0)), round(t.get('y', 0)))
                        if w and not LABEL.match(w) and key not in pos:
                            pos.add(key); src[w] += 1
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
                nxt = [e for e in edges if e > t['x'] + 0.5 and _rule_at(v, e, t['y'])]
                if nxt and x1 > nxt[0] + 1.0:   # (only where this row draws that rule: notes across the table, M1)
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
        from ms_maths import text_width
        bad = None
        q_edge = ((mp.get('info') or {}).get('new_edges') or [60])[0]
        ours_rows = [mp['rows'][0]] + ([mp['rows'][-1]] if any(t['t'] == 'Total' for t in mp['rows'][-1]['text']) else [])
        for v in mp['rows']:                         # the words WE make: header, Q labels, Total (printed words keep
            for t in v['text']:                      # their printed widths and draw as printed)
                if not (v in ours_rows or t['x'] + t['w'] <= q_edge + 1):
                    continue
                if t.get('f') in ('serif', 'sans') and len(t['t'].strip()) >= 2 and t['w'] > 3 and re.fullmatch(r"[\w().,:;'\[\]=+/% -]+", t['t']):
                    m = text_width(t['t'], t['f'], t.get('s', 11), t.get('b'))
                    if m > 0 and not 0.85 <= t['w'] / m <= 1.18 and not t.get('i'):
                        bad = bad or f"'{t['t']}' {t['w']:.1f} pt for {m:.1f} pt"
        if bad:
            hits.append(('ms_stretch', bad))
        for v in rows:
            ink = [(t['y'] - 0.72 * t.get('s', 11), t['y'] + 0.2 * t.get('s', 11)) for t in v['text'] if t.get('t', '').strip()
                   and not re.fullmatch(r'[.\s…_]+', t['t'])]
            ink += [(g['y'], g['y'] + g['h']) for k in ('glyphs', 'images', 'figs') for g in v.get(k) or [] if 'h' in g]
            if ink and (min(a for a, _ in ink) < 2.0 or max(b for _, b in ink) > v['h'] - 1.5):
                hits.append(('ms_edge', ' '.join(t['t'] for t in v['text'][:4])[:40])); break
        for v in rows:                               # a cell picture whose edge runs through ink on the printed page
            for im in v.get('images') or []:
                if im.get('src') and _cut(rec, 'ms', im['src'][0], im['src'][1:]):
                    hits.append(('ms_piccut', im['file'])); break
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
    nsans = sum(1 for p in rec['parts'] for u in p['layout'] for t in u['text'] if t.get('f') == 'sans' and t['t'].strip()
                and not (len(t['t'].strip()) == 1 and not t['t'].strip().isalnum()))   # (a bullet / sign printed in Arial)
    if nsans:
        hits.append(('q_font', f'{nsans} words in sans'))
    from ms_maths import _bbox as _bb               # q_rule: the full-width rule printed between 2014 questions kept as
    for p_ in rec.get('parts', []):                 # content (round 29, ERROR_PATTERNS 130)
        for u_ in p_.get('layout', []):
            for l_ in u_.get('lines', []):
                b_ = _bb(l_['d'])
                if b_ and b_[3] - b_[1] < 1.6 and b_[2] - b_[0] > 0.85 * u_['w'] and b_[1] > u_['h'] - 10:
                    hits.append(('q_rule', f"part {p_.get('label')}: full-width rule at the bottom"))
    hits += fig_checks(rec)
    for p in rec['parts']:
        txt = ' '.join(t['t'] for u in p['layout'] for t in u['text'])
        if re.search(r'NOT\s+TO\s+SCALE', txt) and any(u.get('figs') for u in p['layout']):
            hits.append(('not_to_scale', p['path']))
    return hits


_DOCS = {}


def _doc(rec, kind):
    import fitz
    syl, ses, pv = rec['id'].split('_')[0], rec['id'].split('_')[1], rec['id'].split('_')[2]
    fp = os.path.join(paths.ROOT, 'raw', syl, ses[:4] + '-' + ses[4:], f'{kind}_{pv}.pdf')
    if not os.path.exists(fp):
        return None
    return _DOCS.setdefault(fp, fitz.open(fp))


def _cut(rec, kind, page, box, pad=0.0):
    """Sides of box (page coordinates) that run through ink: ink just inside AND just outside the edge."""
    import fitz
    import numpy as np
    doc = _doc(rec, kind)
    if doc is None:
        return []
    b = fitz.Rect(box) + (-pad, -pad, pad, pad)
    Z, o = 3, 18
    pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(Z, Z), clip=b + (-6, -6, 6, 6), colorspace=fitz.csGRAY)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w) < 140
    inner = {'top': a[o:o + 2, o:-o], 'bottom': a[-o - 2:-o, o:-o], 'left': a[o:-o, o:o + 2], 'right': a[o:-o, -o - 2:-o]}
    outer = {'top': a[o - 3:o - 1, o:-o], 'bottom': a[-o + 1:-o + 3, o:-o], 'left': a[o:-o, o - 3:o - 1], 'right': a[o:-o, -o + 1:-o + 3]}
    def rule(band):                                   # a table / column rule right beside the edge is not a cut
        return band.size and band.mean() > 0.8
    return [k for k in inner if (inner[k] & outer[k]).sum() >= 3 and not rule(outer[k][:1] if k in ('top', 'bottom') else outer[k][:, :1])
            and not rule(outer[k][1:2] if k in ('top', 'bottom') else outer[k][:, 1:2])]


def fig_checks(rec):
    """Diagram crops against the printed page: an edge running through ink (cut) or a question sentence inside."""
    import fitz
    import numpy as np
    out = []
    syl, ses, pv = rec['id'].split('_')[0], rec['id'].split('_')[1], rec['id'].split('_')[2]
    ses = ses[:4] + '-' + ses[4:]
    fp = os.path.join(paths.ROOT, 'raw', syl, ses, f'qp_{pv}.pdf')
    if not os.path.exists(fp):
        return out
    doc = _DOCS.setdefault(fp, fitz.open(fp))
    for f in rec.get('figures', []):
        src = f.get('source') or {}
        if not src.get('box') or not str(f['id']).count('diagram'):
            continue
        pg = doc[src['page'] - 1]
        b = fitz.Rect(src['box'])
        Z = 3
        pix = pg.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=b + (-6, -6, 6, 6), colorspace=fitz.csGRAY)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w) < 140
        o = 6 * Z
        inner = {'top': a[o:o + 2, o:-o], 'bottom': a[-o - 2:-o, o:-o], 'left': a[o:-o, o:o + 2], 'right': a[o:-o, -o - 2:-o]}
        outer = {'top': a[o - 3:o - 1, o:-o], 'bottom': a[-o + 1:-o + 3, o:-o], 'left': a[o:-o, o - 3:o - 1], 'right': a[o:-o, -o + 1:-o + 3]}
        cut = [k for k in inner if (inner[k] & outer[k]).sum() >= 3]
        if cut:
            out.append(('fig_cut', f"{f['id'].split('_')[-1]} {'/'.join(cut)}"))
        lines = {}
        for bl in pg.get_text('dict', clip=b)['blocks']:
            for l in bl.get('lines', []):
                t = ''.join(sp['text'] for sp in l['spans']).strip()
                if t and fitz.Rect(l['bbox']).intersects(b):
                    lines.setdefault(round(l['bbox'][1] / 3), []).append((l['bbox'][0], t))
        for k, ps in lines.items():
            bt = ' '.join(t for _, t in sorted(ps))
            if re.match(r'^(\d{1,2}\s+)?\(([a-z]|[ivx]+)\)\s+\S', bt) or (len(bt) > 30 and len(re.findall(r'[A-Za-z]{3,}', bt)) >= 5):
                out.append(('fig_text', f"{f['id'].split('_')[-1]}: {bt[:40]}")); break
    return out


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
