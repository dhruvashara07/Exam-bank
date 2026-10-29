"""Automatic checks of processed papers. One result file per paper: review/checks/<paper id>.json

    python3 pipeline/checks.py                    # every paper
    python3 pipeline/checks.py 0625_2025MJ_41 ... # some papers
    python3 pipeline/checks.py --summary          # print the stored results only

What is checked (all from the PDF itself, nothing trusted from the cutter):
  marks       marks found == the cover total
  coverage    every printed mark on a question page lies inside some piece (rendered pixels)
  pieces      no footer / 'Turn over' / page notice / copyright box / barcode text inside a piece;
              no two pieces overlapping; no sliver pieces
  figures     no diagram crop cutting through a drawing or a text line
  text        editable copy contains the words printed in the question (score 0-1 per question;
              below TEXT_MIN the question is flagged)
  flags       the cutter's own review reasons (mark-scheme labelling differences, erratum, ...)
A paper is 'clean' when it has no blocking problem (marks, coverage, pieces). Figure-crop and editable-text
problems are warnings: they go into the review round. Flags are listed separately: they need a person.
"""
import collections, datetime, glob, html, json, os, re, sys
import pymupdf as fitz

sys.path.insert(0, os.path.dirname(__file__))
import paths
from run import cleaned
from layout import page_bounds, visible_lines, dark_mask, ZOOM, tight_ink
from coverage import paper_problems
from clean import is_barcode_span

TEXT_MIN = 0.97
NOTICE = re.compile(r'UCLES|Turn over|is on the (?:next|back) page|continues on the next page|'
                    r'(?:begins|starts) on the next page|BLANK\s+PAGE|Permission to reproduce|'
                    r'Cambridge Assessment International|\*\s*\d{8,}\s*\*')
WORD = re.compile(r"[A-Za-z]+|\d+(?:\.\d+)?")
SKIP_WORDS = re.compile(r'^\.+$')


def nodes(n):
    yield n
    for k in n.get('parts', []):
        yield from nodes(k)


def content_text(n):
    out = []
    for b in n.get('content', []):
        if b['type'] == 'text':
            out.append(b['html'])
        elif b['type'] == 'list':
            out += b['items']
        elif b['type'] == 'table':
            out += [c for r in b['rows'] for c in r]
        elif b['type'] == 'options':
            out += [o['label'] + ' ' + o['html'] for o in b['options']]
        elif b['type'] == 'answer':
            out += [b.get('prefix') or '', b.get('unit') or '']
        elif b['type'] == 'figure':
            out.append(b.get('caption') or '')
    t = ' '.join(out)
    t = re.sub(r'\\(frac|text|times|div)\b', ' ', t)
    t = re.sub(r'\\(sin|cos|tan|log|ln)\b', r' \1', t)
    t = re.sub(r'</?(sub|sup|b|i)>', '', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(t)


def words(t):
    return collections.Counter(w.lower() for w in WORD.findall(t))


def printed_words(doc, q):
    """Words printed in the question's pieces, outside its figure crops, without labels/marks/dots."""
    figs = collections.defaultdict(list)
    for f in q.get('figures', []):
        figs[f['page']].append(fitz.Rect(f['bbox']))
    c = collections.Counter()
    for n in nodes(q):
        for s in n.get('segments', []):
            r = fitz.Rect(s['bbox'])
            for x0, y0, x1, y1, w, *_ in doc[s['page'] - 1].get_text('words'):
                ctr = fitz.Point((x0 + x1) / 2, (y0 + y1) / 2)
                if not r.contains(ctr) or any(f.contains(ctr) for f in figs[s['page']]):
                    continue
                if re.fullmatch(r'\(?[a-z]{1,4}\)|\[\d+\]|\[Total:?|\d+\]|\.{3,}.*|\d{1,2}', w):
                    continue                       # part labels, marks, dotted answer lines, question number
                c.update(x.lower() for x in WORD.findall(w))
    return c


def text_score(doc, q):
    want = printed_words(doc, q)
    if not want:
        return 1.0
    have = collections.Counter()
    for n in nodes(q):
        have += words(content_text(n))
    hit = sum(min(v, have[k]) for k, v in want.items())
    return round(hit / sum(want.values()), 3)


def cut_edges(page, r, min_px=3):
    """Edges of a crop that printed ink crosses (ink just inside and just outside at the same place).
    Crops have a 3 pt margin around their ink, so anything crossing an edge was cut."""
    m = dark_mask(page); Z = ZOOM; H, W = m.shape
    y0, y1 = max(0, int(r.y0 * Z)), min(H, int(r.y1 * Z)); x0, x1 = max(0, int(r.x0 * Z)), min(W, int(r.x1 * Z))
    out = []
    for name, a, b in (('left', int((r.x0 - 1) * Z), int((r.x0 + 1) * Z)), ('right', int((r.x1 + 1) * Z), int((r.x1 - 1) * Z))):
        if 0 <= a < W and 0 <= b < W and (m[y0:y1, a] & m[y0:y1, b]).sum() >= min_px:
            out.append(name)
    for name, a, b in (('top', int((r.y0 - 1) * Z), int((r.y0 + 1) * Z)), ('bottom', int((r.y1 + 1) * Z), int((r.y1 - 1) * Z))):
        if 0 <= a < H and 0 <= b < H and (m[a, x0:x1] & m[b, x0:x1]).sum() >= min_px:
            out.append(name)
    return out


def check_paper(pj):
    meta = json.load(open(pj))
    pid = paths.paper_id(meta)
    doc = fitz.open(cleaned(paths.raw_pdfs(meta['question_ids'][0])[0]))
    problems, flags, scores = [], [], {}
    if meta.get('marks_found') != meta.get('total_marks'):
        problems.append({'id': pid, 'kind': 'marks', 'detail': f"marks found {meta.get('marks_found')}, cover {meta.get('total_marks')}"})
    for _, _, pno, n, bb, _ in paper_problems(pj):
        problems.append({'id': pid, 'kind': 'coverage', 'detail': f'page {pno}: {n} px of print outside every piece near {bb}'})
    spans, drawn, lines = {}, {}, {}
    def page_info(pno):
        if pno not in spans:
            p = doc[pno - 1]
            spans[pno] = [sp for b in p.get_text('dict')['blocks'] for l in b.get('lines', []) for sp in l['spans']]
            drawn[pno] = [d['rect'] for d in p.get_drawings()
                          if not (d.get('fill') in ((1.0, 1.0, 1.0),) and not d.get('color')) and d['rect'].width < 0.9 * p.rect.width]
            t, b = page_bounds(p)
            lines[pno] = [x for x in (tight_ink(p, fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])) for l in visible_lines(p, t, b)) if x]
        return spans[pno], drawn[pno], lines[pno]
    pieces = []
    for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
        q = json.load(open(qf))
        qid = q['id']
        for r in q['review'].get('reasons', []):
            flags.append({'id': qid, 'kind': 'flag', 'detail': r})
        for n in nodes(q):
            for s in n.get('segments', []):
                r = fitz.Rect(s['bbox']); where = f"{n.get('path') or q['number']} p{s['page']}"
                sp, _, _ = page_info(s['page'])
                inside = ' '.join(x['text'] for x in sp if r.contains(fitz.Point((x['bbox'][0] + x['bbox'][2]) / 2, (x['bbox'][1] + x['bbox'][3]) / 2)))
                m = NOTICE.search(inside)
                if m:
                    problems.append({'id': qid, 'kind': 'piece', 'detail': f"{where}: page furniture '{m.group(0)}' inside"})
                if any(is_barcode_span(x) and (fitz.Rect(x['bbox']) & r).height > 0.3 for x in sp):
                    problems.append({'id': qid, 'kind': 'piece', 'detail': f'{where}: barcode inside'})
                if r.height < 8:
                    problems.append({'id': qid, 'kind': 'piece', 'detail': f'{where}: sliver piece {r.height:.1f} pt'})
                pieces.append((qid, where, s['page'], r))
        for f in q.get('figures', []):
            r = fitz.Rect(f['bbox'])
            _, dr, ln = page_info(f['page'])
            edges = cut_edges(doc[f['page'] - 1], r)
            cut = [l for l in ln if 0.15 < (l & r).get_area() / max(l.get_area(), 1) < 0.85]
            if edges or cut:
                what = (['ink crosses the ' + '/'.join(edges) + ' edge'] if edges else []) + ([f'{len(cut)} text line(s) half inside'] if cut else [])
                problems.append({'id': qid, 'kind': 'figure', 'detail': f"{f['id']}: crop cut: {', '.join(what)}"})
        scores[qid] = text_score(doc, q)
        if scores[qid] < TEXT_MIN:
            problems.append({'id': qid, 'kind': 'text', 'detail': f'editable text has {scores[qid]:.0%} of the printed words'})
    for i, a in enumerate(pieces):
        for b in pieces[i + 1:]:
            if a[2] == b[2] and (a[3] & b[3]).height > 3 and (a[3] & b[3]).width > 50:
                problems.append({'id': a[0], 'kind': 'piece', 'detail': f'{a[1]} overlaps {b[0]} {b[1]}'})
    for p in problems:            # cut problems block approval; crop/editable-text ones go to the review round
        p['blocking'] = p['kind'] in ('marks', 'coverage', 'piece')
    res = {'paper': pid, 'pipeline_version': meta.get('pipeline_version'), 'checked_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
           'clean': not any(p['blocking'] for p in problems), 'warnings': sum(not p['blocking'] for p in problems),
           'problems': problems, 'flags': flags,
           'text_score_min': min(scores.values()) if scores else None,
           'text_scores': scores}
    os.makedirs(paths.CHECKS, exist_ok=True)
    with open(os.path.join(paths.CHECKS, pid + '.json'), 'w') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


def summary(results):
    kinds = collections.Counter(p['kind'] for r in results for p in r['problems'])
    clean = sum(r['clean'] for r in results)
    print(f'{len(results)} papers checked: {clean} with no blocking problem, {len(results) - clean} blocked; all problems {dict(kinds)}; '
          f"{sum(len(r['flags']) for r in results)} flags for a person")
    for r in results:
        for p in r['problems'][:5]:
            print(f"  {p['id']}  {p['kind']}: {p['detail']}")


if __name__ == '__main__':
    from batch import pid_of
    args = [pid_of(a) for a in sys.argv[1:] if not a.startswith('--')]
    if '--summary' in sys.argv:
        summary([json.load(open(f)) for f in sorted(glob.glob(os.path.join(paths.CHECKS, '*.json')))])
        sys.exit(0)
    out = []
    for pj in paths.paper_files():
        if args and paths.paper_id(json.load(open(pj))) not in args:
            continue
        out.append(check_paper(pj))
    summary(out)
    if os.environ.get('GITHUB_ACTIONS'):
        bad = [r['paper'] for r in out if not r['clean']]
        print(f"::notice::checks: {len(out)} papers, {len(out) - len(bad)} clean" + (f"; problems in {' '.join(bad[:30])}" if bad else ''))
