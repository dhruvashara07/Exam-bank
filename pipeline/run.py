"""Process question papers + mark schemes into question JSON and SVG assets.

Usage:  python3 pipeline/run.py                              # every paper under raw/
        python3 pipeline/run.py 2025-MJ/41 0625/2025-ON/42   # some papers
Outputs: bank/<board-exam>/<syllabus-subject>/<year-session>/p<pv>/  (layout: see paths.py)
         bank/index.json, review/queue.json
"""
import json, os, re, sys, glob, hashlib
import pymupdf as fitz

sys.path.insert(0, os.path.dirname(__file__))
from clean import clean
from extract import extract, segment_text_all
from layout import page_bounds, visible_lines, ink_boxes
from render import region_svg
from ms import mcq_key, structured_rows
import paths

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CACHE = os.path.join(ROOT, 'out', 'clean')


def cleaned(path):
    rel = os.path.relpath(path, os.path.join(ROOT, 'raw'))
    dst = os.path.join(CACHE, rel)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(path):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        clean(path, dst)
    return dst


def label_of(path):
    return '-'.join(str(x) for x in path[1:]) or 'stem'


def paren(path):
    return f"{path[0]}" + ''.join(f'({x})' for x in path[1:])


class Writer:
    def __init__(self, meta):
        self.pdir = paths.paper_dir(meta)
        if os.path.isdir(self.pdir):          # a re-run replaces the paper completely (no stale files)
            import shutil; shutil.rmtree(self.pdir)
        os.makedirs(self.pdir)

    def qdir(self, qid):
        return os.path.join(self.pdir, qid.split('_')[3][:3])      # 'q01' from 'q01', 'q01b', ...

    def svg(self, doc, page, bbox, name, kind):
        d = os.path.join(self.qdir(name), kind)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, name + '.svg')
        svg = region_svg(doc, page - 1, bbox)
        with open(path, 'w') as f:
            f.write(svg)
        return {'file': os.path.relpath(path, ROOT), 'public_id': paths.public_id(path), 'url': None,
                'kb': round(len(svg) / 1024, 1)}


_PIX = {}


def visible_ink(page, r, text_rects, zoom=2):
    """True if the rendered page shows non-white pixels inside r outside text boxes.
    Pattern (hatching) cells are reported by PyMuPDF at positions where nothing is drawn."""
    import numpy as np
    key = (id(page.parent), page.number)
    if key not in _PIX:
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
        _PIX.clear()
        _PIX[key] = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    img = _PIX[key]
    x0, y0 = max(int((r.x0 - 1) * zoom), 0), max(int((r.y0 - 1) * zoom), 0)
    x1, y1 = int((r.x1 + 1) * zoom) + 1, int((r.y1 + 1) * zoom) + 1
    mask = img[y0:y1, x0:x1] < 200
    for t in text_rects:
        tx0, ty0 = int(t.x0 * zoom) - x0, int(t.y0 * zoom) - y0
        tx1, ty1 = int(t.x1 * zoom) + 1 - x0, int(t.y1 * zoom) + 1 - y0
        if tx1 > 0 and ty1 > 0:
            mask[max(ty0, 0):max(ty1, 0), max(tx0, 0):max(tx1, 0)] = False
    return bool(mask.any())


def mcq_figures(doc, q):
    """Uncaptioned diagrams/tables in an MCQ.

    A figure is every drawing between two lines of question prose (stem sentences, option rows),
    plus all the short labels on or around it. No vertical-gap limit, so dots, hatching and
    split curves stay in one figure; prose lines are the only separators.
    """
    figs = []
    for s in q['segments']:
        page = doc[s['page'] - 1]
        top, bottom = page_bounds(page)
        y0, y1 = s['bbox'][1], s['bbox'][3]
        lines = [l for l in visible_lines(page, top, bottom) if y0 <= l['y0'] <= y1]
        def option_label(l):
            """'A 4.0 m/s' or a bare 'A' with answer text right after it (not a label above a diagram)."""
            if re.match(r'^[ABCD]\s+\S', l['text']):
                return True
            return re.fullmatch(r'[ABCD]', l['text']) is not None and any(
                abs(o['y0'] - l['y0']) < 4 and 0 <= o['x0'] - l['x1'] < 40 and not re.fullmatch(r'[ABCD]', o['text'])
                for o in lines)
        option_rows = [l['y0'] for l in lines if option_label(l)]
        def is_prose(l):
            t = l['text']
            return (len(t) >= 25 and ' ' in t) or l['x0'] < 60 or t.rstrip().endswith('?') \
                or (any(abs(l['y0'] - y) < 4 for y in option_rows) and len(option_rows) >= 2)
        prose = [l for l in lines if is_prose(l)]
        labels = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines if not is_prose(l)]
        prose_r = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in prose]
        draw = [r for r in ink_boxes(page, top, bottom) if r.y0 >= y0 - 1 and r.y1 <= y1 + 1]
        draw = [r for r in draw if not any(r in (p + (-1, -1, 1, 1)) for p in prose_r + labels)]   # text glyph boxes
        draw = [r for r in draw if (r.width > 0.3 or r.height > 0.3) and not any(r.intersects(p) for p in prose_r)]
        draw = [r for r in draw if visible_ink(page, r, prose_r + labels)]
        draw.sort(key=lambda r: r.y0)

        def union(a, b):                 # fitz '|' ignores zero-width rects (straight lines), so do it by hand
            return fitz.Rect(min(a.x0, b.x0), min(a.y0, b.y0), max(a.x1, b.x1), max(a.y1, b.y1))
        clusters, members = [], []
        for r in draw:
            if clusters and not any(clusters[-1].y1 < p.y0 and p.y1 < r.y0 for p in prose_r):
                clusters[-1] = union(clusters[-1], r); members[-1].append(r)
            else:
                clusters.append(fitz.Rect(r)); members.append([r])
        for c, mem in zip(clusters, members):
            if c.height < 8 and c.width < 40:
                continue
            if all(m.height < 1.2 and m.width < 160 for m in mem):
                continue                 # only fraction bars: an equation in the text/options, not a figure
            for _ in range(3):           # labels hang off labels ("speed" over "m/s")
                for t in labels:
                    if t.intersects(c + (-14, -18, 14, 12)) and not any(c.y1 < p.y0 and p.y1 < t.y0 or t.y1 < p.y0 and p.y1 < c.y0 for p in prose_r):
                        c = union(c, t)
            if c.height < 10:            # a lone rule (e.g. end-of-paper line), not a figure
                continue
            figs.append({'page': s['page'], 'bbox': [round(c.x0 - 3, 1), round(c.y0 - 3, 1), round(c.x1 + 3, 1), round(c.y1 + 3, 1)]})
    return figs


def find_node(q, path):
    node = q
    for label in path[1:]:
        kids = {k['label']: k for k in node.get('parts', [])}
        if label not in kids:
            return node, False
        node = kids[label]
    return node, True


def process(qp_path):
    m = re.search(r'raw/(\w+)/(\d{4})-(\w\w)/qp_(\d\d)\.pdf$', qp_path.replace('\\', '/'))
    syl, year, session, pv = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    folder = f'{year}-{session}'
    qp = cleaned(qp_path)
    ms_raw = os.path.join(os.path.dirname(qp_path), f'ms_{pv}.pdf')
    ms = cleaned(ms_raw) if os.path.exists(ms_raw) else None
    meta, questions = extract(qp, syl, year, session, pv)
    doc = fitz.open(qp)
    msdoc = fitz.open(ms) if ms else None
    w = Writer(meta)
    key = mcq_key(msdoc) if (msdoc and meta['paper'] in (1, 2)) else {}
    ms_rows = structured_rows(msdoc) if (msdoc and meta['paper'] >= 3) else []
    if not msdoc:
        meta['mark_scheme'] = 'missing'

    def export_segments(node, path, qid):
        for i, s in enumerate(node.get('segments', []), 1):
            s['svg'] = w.svg(doc, s['page'], s['bbox'], f'{qid}_{label_of(path)}_s{i}', 'question')
        for k in node.get('parts', []):
            k['path'] = paren(path + (k['label'],))
            export_segments(k, path + (k['label'],), qid)

    queue = []
    for q in questions:
        qid = q['id']
        path = (q['number'],)
        export_segments(q, path, qid)
        for f in q['figures']:
            f['svg'] = w.svg(doc, f['page'], f['bbox'], f['id'], 'figures')
        if q['type'] == 'mcq':
            for i, f in enumerate(mcq_figures(doc, q)):
                f['id'] = f'{qid}_fig{chr(65 + i)}'
                f['caption'] = None; f['part'] = ''; f['alt'] = ''
                f['svg'] = w.svg(doc, f['page'], f['bbox'], f['id'], 'figures')
                q['figures'].append(f)
            q['answer'] = key.get(q['number'])
            if not q['answer'] and msdoc:
                q['review']['reasons'].append('answer key not found in mark scheme')
        else:
            for row in [r for r in ms_rows if r['path'][0] == q['number']]:
                node, exact = find_node(q, row['path'])
                segs = []
                for j, s in enumerate(row['segments'], 1):
                    s = dict(s); s['svg'] = w.svg(msdoc, s['page'], s['bbox'], f"{qid}_{label_of(row['path'])}_ms{j}", 'markscheme')
                    segs.append(s)
                entry = {'label': row['label'], 'text': row['text'], 'codes': row['marks_codes'], 'segments': segs}
                node.setdefault('mark_scheme', []).append(entry)
                if not exact:
                    q['review']['reasons'].append(f"mark scheme row {row['label']} has no matching part in the paper")
            with_ms = {str(q['number'])} if q.get('mark_scheme') else set()
            def collect(n):
                for k in n.get('parts', []):
                    if k.get('mark_scheme'):
                        with_ms.add(k['path'])
                    collect(k)
            collect(q)
            def covered(p):   # answered on its own row or on a parent's combined row
                return any(p == a or p.startswith(a + '(') for a in with_ms)
            for k in leaves(q):
                if not k.get('mark_scheme') and covered(k['path']):
                    k['mark_scheme_on'] = max((a for a in with_ms if k['path'].startswith(a + '(')), key=len)
            missing = [k['path'] for k in leaves(q) if k.get('marks') and not covered(k['path'])]
            if missing and msdoc:
                q['review']['reasons'].append('no mark scheme for ' + ', '.join(missing))
        q.update({k: meta[k] for k in ('syllabus', 'subject', 'board', 'exam', 'year', 'session', 'season',
                                       'paper', 'variant', 'paper_code', 'paper_type')})
        q.setdefault('total_marks', q['marks'])
        q.update({'topic': None, 'subtopic': None, 'keywords': [], 'difficulty': None})
        q['review']['status'] = 'flagged' if q['review']['reasons'] else 'auto'
        with open(os.path.join(w.qdir(qid), f"{qid}.json"), 'w') as f:
            json.dump(q, f, ensure_ascii=False, indent=1)
        if q['review']['reasons']:
            queue.append({'id': qid, 'reasons': q['review']['reasons']})

    found = sum(q['marks'] for q in questions)
    meta['questions'] = len(questions)
    meta['marks_found'] = found
    meta['checks'] = {'marks_match_total': found == meta['total_marks']}
    if found != meta['total_marks']:
        queue.append({'id': f'{syl}_{year}{session}_{pv}', 'reasons': [f"paper marks found {found}, cover says {meta['total_marks']}"]})
    meta['question_ids'] = [q['id'] for q in questions]
    with open(os.path.join(w.pdir, 'paper.json'), 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta, queue


def leaves(node):
    kids = node.get('parts', [])
    if not kids:
        return [node] if 'label' in node else []
    out = []
    for k in kids:
        out += leaves(k)
    return out


def write_index():
    """bank/index.json: one small row per question, for searching and the test builder."""
    rows = []
    for f in paths.question_files():
        q = json.load(open(f))
        rows.append({'id': q['id'], 'file': os.path.relpath(f, ROOT), 'paper_code': q['paper_code'],
                     'year': q['year'], 'session': q['session'], 'paper': q['paper'], 'variant': q['variant'],
                     'number': q['number'], 'type': q['type'], 'marks': q['marks'],
                     'parts': [k['path'] for k in leaves(q)], 'answer': q.get('answer'),
                     'figures': len(q['figures']), 'topic': q.get('topic'), 'keywords': q.get('keywords', []),
                     'review': q['review']['status'], 'text': (q.get('text') or '')[:160]})
    with open(os.path.join(paths.BANK, 'index.json'), 'w') as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=0)


if __name__ == '__main__':
    sels = sys.argv[1:]              # '2025-MJ/41' or '0625/2025-MJ/41'; none = every paper
    sel = bool(sels)
    papers = sorted(glob.glob(os.path.join(ROOT, 'raw', '*', '*', 'qp_*.pdf')))
    def wanted(p):
        p = p.replace('\\', '/')
        return any(p.endswith(f"{s.rsplit('/', 1)[0]}/qp_{s.rsplit('/', 1)[1]}.pdf") for s in sels)
    if sels:
        papers = [p for p in papers if wanted(p)]
    all_queue = []
    for p in papers:
        try:
            meta, queue = process(p)
            all_queue += queue
            print(f"{meta['paper_code']} {meta['year']}-{meta['session']}: {meta['questions']} questions, "
                  f"marks {meta['marks_found']}/{meta['total_marks']}, flagged {len(queue)}")
        except Exception as e:  # keep going; record the failure for review
            all_queue.append({'id': os.path.relpath(p, ROOT), 'reasons': [f'pipeline error: {e!r}']})
            print('ERROR', p, repr(e))
    os.makedirs(os.path.join(ROOT, 'review'), exist_ok=True)
    qfile = os.path.join(ROOT, 'review', 'queue.json')
    old = json.load(open(qfile)) if (sel and os.path.exists(qfile)) else []
    def paper_id(p):
        m = re.search(r'raw/(\w+)/(\d{4})-(\w\w)/qp_(\d\d)\.pdf$', p.replace('\\', '/'))
        return f'{m.group(1)}_{m.group(2)}{m.group(3)}_{m.group(4)}'
    done = {paper_id(p) for p in papers} | {os.path.relpath(p, ROOT) for p in papers}
    merged = [o for o in old if o['id'].rsplit('_q', 1)[0] not in done] + all_queue
    json.dump(merged, open(qfile, 'w'), ensure_ascii=False, indent=1)
    print('review queue:', len(merged))
    write_index()

