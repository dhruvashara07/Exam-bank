"""Full audit of stored questions (Dhruv 2026-11-05: check every question, not only flagged ones).

    python3 pipeline/audit.py <year-session...>        e.g. 2016-MJ 2016-ON 2017-FM   -> out/audit/<...>.json + summary

Checks per question (problem kinds):
  marks       question marks != sum of part marks, or != mark-scheme codes total (MCQ: answer key present)
  ms_total    our Total row missing / not the question's marks / more than one
  ms_header   header row is not Q | Answer | Marks (| Guidance)
  ms_rows     part with marks but no mark-scheme row; rows of another question
  ms_layout   a row still shrunk to fit ('scale') or drawn cell-wise ('cell')
  ms_words    a printed mark-scheme word missing in our layout (word check)
  text        doubled letters / broken characters (mojibake, private-use)
  figure      figure crop still cuts ink or a text line (on the stored, mended crop)
  options     MCQ without 4 options or without an answer
  ms_overlap  two words printed over each other
  ms_bullet   a bullet point run into the line before it
  ms_edges    a table line that ends in the air (lost inner-table edge, line short of the frame)
  differs     stored copy differs from the page (review/store/<paper>.json)
"""
import collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ROOT = paths.ROOT
STORE = os.path.join(ROOT, 'store', 'cambridge-igcse', '0625-physics')
CODE = re.compile(r'^\(?([ABCM])(\d)\)?$')
BAD = re.compile(r'(?<![A-Za-z])[æçèöø](?![A-Za-z])|Ã.|â€|�|[-]')
DOUBLE = re.compile(r'([a-z])\1\1|(?<![a-z])([b-df-hj-np-tv-z])\2(?=[a-z]{3})')   # 'ciir..'-like repeats are caught below


def codes_total(q):
    t = 0
    for p in q.get('parts', []):
        for r in p.get('ms', []):
            for c in r.get('codes', []):
                m = CODE.match(c)
                if m and not c.startswith('('):
                    t += int(m.group(2))
    return t


def doubled_words(text):
    """words with a letter doubled that is not a normal English double ('ciircuit', 'inpuuts')."""
    out = []
    for w in re.findall(r'[A-Za-z]{4,}', text):
        for m in re.finditer(r'([a-z])\1', w.lower()):
            pair = m.group(0)
            if pair in ('ll', 'ss', 'ee', 'oo', 'tt', 'ff', 'rr', 'nn', 'mm', 'pp', 'cc', 'dd', 'gg', 'zz', 'bb'):
                continue
            out.append(w)
    return out


def audit_question(q, verify):
    probs = []
    qid = q['id']
    parts = q.get('parts', [])
    pm = sum(p.get('marks') or 0 for p in parts if '(' in (p.get('path') or '') and not any(
        o.get('parent') == p.get('path') for o in parts))
    if q.get('type') == 'mcq':
        if not q.get('answer'):
            probs.append(('options', 'no answer key'))
        if len(q.get('options') or []) != 4 and not q.get('options_on_figure'):
            probs.append(('options', f"{len(q.get('options') or [])} options"))
        return probs
    leaf = [p for p in parts if not any(o.get('parent') == p.get('path') for o in parts)]
    lm = sum(p.get('marks') or 0 for p in leaf)
    if q.get('marks') and lm and lm != q['marks']:
        probs.append(('marks', f"parts add to {lm}, question has {q['marks']}"))
    ct = codes_total(q)
    if ct and q.get('marks') and ct != q['marks'] and abs(ct - q['marks']) > 0:
        probs.append(('marks', f"mark-scheme codes add to {ct}, question has {q['marks']} (OR/alternative marks can explain this)"))
    labs = {r['label'].split('(')[0] for p in parts for r in p.get('ms', [])}
    if labs - {str(q['number'])}:
        probs.append(('ms_rows', f"rows of another question: {sorted(labs)}"))
    for p in leaf:
        if (p.get('marks') or 0) > 0 and not p.get('ms') and not any(r for o in parts if o.get('path') and (p.get('path') or '').startswith(o['path']) for r in o.get('ms', [])):
            probs.append(('ms_rows', f"{p.get('path')} has {p.get('marks')} marks but no mark-scheme row"))
    mp = q.get('ms_p')
    if mp:
        rows = mp['rows']
        tots = [v for v in rows if len(v['text']) == 2 and v['text'][0]['t'] == 'Total']
        if len(tots) != 1:
            probs.append(('ms_total', f'{len(tots)} Total rows'))
        elif tots[0]['text'][1]['t'] != str(q.get('marks')):
            probs.append(('ms_total', f"Total {tots[0]['text'][1]['t']} vs {q.get('marks')} marks"))
        if [t['t'] for t in rows[0]['text']][:1] != ['Q']:
            probs.append(('ms_header', ' | '.join(t['t'] for t in rows[0]['text'])))
        for k in ('scale', 'cell'):
            if mp.get('modes', {}).get(k):
                probs.append(('ms_layout', f"{mp['modes'][k]} row(s) {'shrunk to fit' if k == 'scale' else 'drawn cell-wise (answer cell scaled)'}"))
        if mp.get('problems'):
            probs.append(('ms_words', f"{len(mp['problems'])} word problem(s): {mp['problems'][:1]}"))
        for v in rows:                                 # a bullet in the middle of a line: two bullet points run together (2023 MJ 41 q7)
            for t in v['text']:
                if t['t'].strip() in ('•', '▪') and any(abs(o['y'] - t['y']) < 2 and 50 < o['x'] < t['x'] - 3 for o in v['text']):
                    probs.append(('ms_bullet', f"bullet run into the line before it at y {t['y']:.0f}")); break
        for v in rows:                                 # words printed over each other ('8 (a)(ii)' -> '(a8)(ii)', 2019 MJ 32 q8)
            ws = sorted((t for t in v['text'] if t['t'].strip() and t.get('s', 11) >= 8), key=lambda t: (round(t['y']), t['x']))
            hit = next((f"'{a['t']}' / '{b['t']}'" for i, a in enumerate(ws) for b in ws[i + 1:] if abs(a['y'] - b['y']) < 1.5
                        and min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x']) > 2.5), None)
            if hit:
                probs.append(('ms_overlap', f'words over each other: {hit}')); break
        for v in rows:
            for e in loose_rules(v):
                probs.append(('ms_edges', e)); break
        txt = ' '.join(t['t'] for v in rows for t in v['text'])
        bad = BAD.findall(txt)
        if bad:
            probs.append(('text', f'broken characters in mark scheme: {bad[:3]}'))
        dw = [w for w in doubled_words(txt) if w.lower() not in KNOWN]
        if dw:
            probs.append(('text', f"doubled letters? {sorted(set(dw))[:6]}"))
    qtxt = ' '.join(t['t'] for p in parts for u in p.get('layout', []) for t in u['text'])
    bad = BAD.findall(qtxt)
    if bad:
        probs.append(('text', f'broken characters in question: {bad[:3]}'))
    for c in figure_cuts(q):
        probs.append(('figure', c))
    for d in verify.get(qid, []):
        probs.append(('differs', f"{d['unit']}: {d['missing']}% missing, {d['extra']}% extra"))
    return probs


KNOWN = set()


def loose_rules(v):
    """Dhruv, rounds 17-18: table lines must meet - a column rule with one end on a row rule and the other end in the
    air (an inner table's lost top/bottom edge, a column rule short of the frame)."""
    import ms_portrait as MP
    bx = [b for b in (MP._bbox(l['d']) for l in v.get('lines', [])) if b]
    hz = [b for b in bx if b[3] - b[1] < 1.5 and b[2] - b[0] > 4]
    vt = [b for b in bx if b[2] - b[0] < 1.5 and b[3] - b[1] >= 8]
    touch = lambda x, y: (y <= 1.0 or y >= v['h'] - 1.0 or
                          any(b[0] - 1.2 <= x <= b[2] + 1.2 and b[1] - 1.2 <= y <= b[3] + 1.2 for b in hz) or
                          any(abs((b[0] + b[2]) / 2 - x) < 1.2 and b[1] - 1.2 <= y <= b[3] + 1.2 and b is not o for b in vt for o in [None]))
    out = []
    W_ = v.get('w', 523.0)
    for b in hz:                                       # a row line a few pt short of the right frame
        if b[2] - b[0] > 40 and W_ - 8 < b[2] < W_ - 0.7 and not any(o[0] <= b[2] + 0.5 and o[2] >= W_ - 0.3 and abs(o[1] - b[1]) < 1 for o in hz):
            out.append(f"row line at y {b[1]:.0f} stops {W_ - b[2]:.1f} pt short of the frame")
    full = sorted(b[1] for b in hz if b[2] - b[0] > 0.6 * W_)
    for a, b in zip(full, full[1:]):                   # two row lines 1-6 pt apart: a doubled line (2024 ON 31 q7(c))
        if 1.2 < b - a < 6:
            out.append(f"double row line at y {a:.0f}/{b:.0f}"); break
    for b in hz:                                       # an underline with no word on it (moved apart: 2024 MJ 42 q1 'vectors')
        if b[2] - b[0] < 0.5 * W_ and b[3] - b[1] < 1.3 and not any(
                -1 <= b[1] - t['y'] <= 5 and (abs(t['x'] - b[0]) < 2.5 or (t['x'] - 1 <= b[0] and b[2] <= t['x'] + t['w'] + 1))
                for t in v['text']) and not any(
                0 < t['y'] - b[3] <= 13 and t['x'] < b[2] and t['x'] + t['w'] > b[0] for t in v['text']) and not any(
                o[2] - o[0] < 1.5 and o[1] - 1 <= b[1] <= o[3] + 1 and (abs(o[0] - b[0]) < 1.5 or abs(o[2] - b[2]) < 1.5) for o in bx) and any(-1 <= b[1] - t['y'] <= 5 and t['x'] < b[2] and t['x'] + t['w'] > b[0] for t in v['text']):
            out.append(f"underline at y {b[1]:.0f} not under its word"); break
    for b in vt:
        x = (b[0] + b[2]) / 2
        ends = [touch(x, b[1]), touch(x, b[3])]
        others = [o for o in vt if o is not b]
        ends = [e or any(abs((o[0] + o[2]) / 2 - x) < 1.2 and o[1] - 1.2 <= y <= o[3] + 1.2 for o in others)
                for e, y in zip(ends, (b[1], b[3]))]
        if ends.count(True) == 1:
            out.append(f"line at x {x:.0f}, y {b[1]:.0f}-{b[3]:.0f} ends in the air (row {v.get('src', {}).get('page')})")
    return out


_PG = {}


def figure_cuts(q):
    """the crop-cut check of checks.py, on the STORED (mended) figure crops."""
    import pymupdf as fitz
    from run import cleaned
    from checks import cut_edges
    from layout import page_bounds, visible_lines, tight_ink
    from extract import split_captions
    out = []
    for f in q.get('figures', []):
        if '_opt' in f['id'] or f.get('kind') == 'raster' and False:
            continue
        src = f.get('source') or {}
        if not src.get('box'):
            continue
        pdf = paths.raw_pdfs(q['id'])[0]
        key = (pdf, src['page'])
        if key not in _PG:
            pg = fitz.open(cleaned(pdf))[src['page'] - 1]
            t, b = page_bounds(pg)
            ln = [x for x in (tight_ink(pg, fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])) for l in split_captions(pg, visible_lines(pg, t, b))) if x]
            _PG[key] = (pg, ln)
        pg, ln = _PG[key]
        r = fitz.Rect(src['box'])
        edges = cut_edges(pg, r)
        cut = [l for l in ln if 0.15 < (l & r).get_area() / max(l.get_area(), 1) < 0.85]
        if edges or cut:
            out.append(f"{f['id'].split('_')[-1]}: " + ', '.join((['ink crosses ' + '/'.join(edges)] if edges else []) + ([f'{len(cut)} text line(s) half inside'] if cut else [])))
    return out


def main(sessions):
    global KNOWN
    allw = collections.Counter()
    files = []
    for s in sessions:
        files += sorted(glob.glob(os.path.join(STORE, s, 'p*', 'q*.json')))
    qs = []
    for f in files:
        q = json.load(open(f))
        if q.get('stub'):
            continue
        qs.append(q)
        txt = ' '.join(t['t'] for p in q.get('parts', []) for u in p.get('layout', []) for t in u['text'])
        allw.update(w.lower() for w in re.findall(r'[A-Za-z]{4,}', txt))
    KNOWN = {w for w, n in allw.items() if n >= 1}          # a word that appears in a question paper is a real word
    verify = collections.defaultdict(list)
    for s in sessions:
        for vf in glob.glob(os.path.join(ROOT, 'review', 'store', f"0625_{s.replace('-', '')}_*.json")):
            for d in json.load(open(vf)).get('differ', []):
                verify[d['q']].append(d)
    out, kinds = {}, collections.Counter()
    for q in qs:
        p = audit_question(q, verify)
        if p:
            out[q['id']] = p
            kinds.update({k for k, _ in p})
    os.makedirs(os.path.join(ROOT, 'out', 'audit'), exist_ok=True)
    name = '_'.join(sessions) if len(sessions) < 4 else f'{sessions[0]}..{sessions[-1]}'
    json.dump(out, open(os.path.join(ROOT, 'out', 'audit', name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'{len(qs)} questions, {len(out)} with a problem; by kind: {dict(kinds)}')
    return out


if __name__ == '__main__':
    main(sys.argv[1:])
