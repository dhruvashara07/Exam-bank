"""Process question papers + mark schemes into question JSON and SVG assets.

Usage:  python3 pipeline/run.py                 # every paper under raw/
        python3 pipeline/run.py 2025-MJ/41      # one paper
Outputs (repo-relative):
  data/<syl>/<year>-<session>/<pv>/paper.json, qNN.json
  assets/<syl>/<year>-<session>/<pv>/*.svg
  review/queue.json
"""
import json, os, re, sys, glob, hashlib
import pymupdf as fitz

sys.path.insert(0, os.path.dirname(__file__))
from clean import clean
from extract import extract, segment_text_all
from layout import page_bounds, visible_lines, ink_boxes
from render import region_svg
from ms import mcq_key, structured_rows

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
    def __init__(self, syl, folder, pv):
        self.adir = os.path.join(ROOT, 'assets', syl, folder, pv)
        self.ddir = os.path.join(ROOT, 'data', syl, folder, pv)
        os.makedirs(self.adir, exist_ok=True); os.makedirs(self.ddir, exist_ok=True)
        self.cloud_prefix = f'igcse/{syl}/{folder}/{pv}'

    def svg(self, doc, page, bbox, name):
        svg = region_svg(doc, page - 1, bbox)
        with open(os.path.join(self.adir, name + '.svg'), 'w') as f:
            f.write(svg)
        return {'file': os.path.relpath(os.path.join(self.adir, name + '.svg'), ROOT),
                'public_id': f'{self.cloud_prefix}/{name}', 'url': None,
                'kb': round(len(svg) / 1024, 1)}


def mcq_figures(doc, q):
    """Uncaptioned diagrams/tables in an MCQ: clusters of vector drawings plus the labels on them."""
    figs = []
    for s in q['segments']:
        page = doc[s['page'] - 1]
        top, bottom = page_bounds(page)
        y0, y1 = s['bbox'][1], s['bbox'][3]
        text = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in visible_lines(page, top, bottom) if y0 <= l['y0'] <= y1]
        draw = [r for r in ink_boxes(page, top, bottom)
                if r.y0 >= y0 - 1 and r.y1 <= y1 + 1 and not any(r.intersects(t) and r.height < t.height * 1.5 for t in text)]
        draw = [r for r in draw if r.width * r.height > 4 or r.width > 8 or r.height > 8]
        draw.sort(key=lambda r: r.y0)
        clusters = []
        for r in draw:
            if clusters and r.y0 <= clusters[-1].y1 + 22:
                clusters[-1] |= r
            else:
                clusters.append(fitz.Rect(r))
        for c in clusters:
            if c.height < 12:
                continue
            for t in text:
                if t.intersects(c + (-6, -6, 6, 6)):
                    c |= t
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
    w = Writer(syl, folder, pv)
    key = mcq_key(msdoc) if (msdoc and meta['paper'] in (1, 2)) else {}
    ms_rows = structured_rows(msdoc) if (msdoc and meta['paper'] >= 3) else []
    if not msdoc:
        meta['mark_scheme'] = 'missing'

    def export_segments(node, path, qid):
        for i, s in enumerate(node.get('segments', []), 1):
            s['svg'] = w.svg(doc, s['page'], s['bbox'], f'{qid}_{label_of(path)}_s{i}')
        for k in node.get('parts', []):
            k['path'] = paren(path + (k['label'],))
            export_segments(k, path + (k['label'],), qid)

    queue = []
    for q in questions:
        qid = q['id']
        path = (q['number'],)
        export_segments(q, path, qid)
        for f in q['figures']:
            f['svg'] = w.svg(doc, f['page'], f['bbox'], f['id'])
        if q['type'] == 'mcq':
            for i, f in enumerate(mcq_figures(doc, q)):
                f['id'] = f'{qid}_fig{chr(65 + i)}'
                f['caption'] = None; f['part'] = ''; f['alt'] = ''
                f['svg'] = w.svg(doc, f['page'], f['bbox'], f['id'])
                q['figures'].append(f)
            q['answer'] = key.get(q['number'])
            if not q['answer'] and msdoc:
                q['review']['reasons'].append('answer key not found in mark scheme')
        else:
            for row in [r for r in ms_rows if r['path'][0] == q['number']]:
                node, exact = find_node(q, row['path'])
                segs = []
                for j, s in enumerate(row['segments'], 1):
                    s = dict(s); s['svg'] = w.svg(msdoc, s['page'], s['bbox'], f"{qid}_{label_of(row['path'])}_ms{j}")
                    segs.append(s)
                entry = {'label': row['label'], 'text': row['text'], 'codes': row['marks_codes'], 'segments': segs}
                node.setdefault('mark_scheme', []).append(entry)
                if not exact:
                    q['review']['reasons'].append(f"mark scheme row {row['label']} has no matching part in the paper")
            missing = [k['path'] for k in leaves(q) if not k.get('mark_scheme') and k.get('marks')]
            if missing and msdoc:
                q['review']['reasons'].append('no mark scheme for ' + ', '.join(missing))
        q.update({k: meta[k] for k in ('syllabus', 'subject', 'board', 'exam', 'year', 'session', 'season',
                                       'paper', 'variant', 'paper_code', 'paper_type')})
        q.setdefault('total_marks', q['marks'])
        q.update({'topic': None, 'subtopic': None, 'keywords': [], 'difficulty': None})
        q['review']['status'] = 'flagged' if q['review']['reasons'] else 'auto'
        with open(os.path.join(w.ddir, f"q{q['number']:02d}.json"), 'w') as f:
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
    with open(os.path.join(w.ddir, 'paper.json'), 'w') as f:
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


if __name__ == '__main__':
    sel = sys.argv[1] if len(sys.argv) > 1 else ''
    papers = sorted(glob.glob(os.path.join(ROOT, 'raw', '*', '*', 'qp_*.pdf')))
    papers = [p for p in papers if sel.replace('/', '/qp_') in p.replace('\\', '/')]
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
    done = {a['id'].rsplit('_q', 1)[0] for a in all_queue} | {os.path.relpath(p, ROOT) for p in papers}
    merged = [o for o in old if o['id'].rsplit('_q', 1)[0] not in done] + all_queue
    json.dump(merged, open(qfile, 'w'), ensure_ascii=False, indent=1)
    print('review queue:', len(merged))
