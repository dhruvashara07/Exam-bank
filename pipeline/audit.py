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
  differs     stored copy differs from the page (review/store/<paper>.json)
"""
import collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ROOT = paths.ROOT
STORE = os.path.join(ROOT, 'store', 'cambridge-igcse', '0625-physics')
CODE = re.compile(r'^\(?([ABCM])(\d)\)?$')
BAD = re.compile(r'Ã.|â€|�|[-]')
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
