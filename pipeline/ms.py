"""Read Cambridge mark schemes.

MCQ (papers 1, 2): a table of question number -> letter.
Structured (papers 3-6): landscape table with a Question column (labels like 1(b)(iii)),
an Answer column and a Marks column. Each label's rows become one or more page strips.
"""
import re
import pymupdf as fitz
from layout import norm

LABEL = re.compile(r'^(\d{1,2})((?:\([a-z]\))?)((?:\([ivx]+\))?)$')


def _lines(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            if abs(l['dir'][1]) > 0.1:
                continue
            t = norm(''.join(s['text'] for s in l['spans'])).strip()
            if t:
                out.append({'x0': l['bbox'][0], 'y0': l['bbox'][1], 'x1': l['bbox'][2], 'y1': l['bbox'][3], 'text': t})
    return sorted(out, key=lambda d: (round(d['y0']), d['x0']))


def mcq_key(doc):
    key = {}
    for page in doc:
        lines = _lines(page)
        nums = [l for l in lines if re.fullmatch(r'\d{1,2}', l['text']) and l['x0'] < 110]
        for n in nums:
            ans = [l for l in lines if abs(l['y0'] - n['y0']) < 3 and re.fullmatch(r'[ABCD]', l['text'])]
            if ans:
                key[int(n['text'])] = ans[0]['text']
    return key


def _table_area(page, lines):
    """Top (below the header row) and bottom (above the footer) of the answer table."""
    header = [l for l in lines if l['text'] == 'Question' and l['y0'] < 120]
    if not header:
        return None
    top = header[0]['y1'] + 3
    foot = [l['y0'] for l in lines if l['y0'] > page.rect.height - 80 and ('©' in l['text'] or 'Page ' in l['text'])]
    bottom = (min(foot) if foot else page.rect.height - 40) - 6
    return top, bottom


def structured_rows(doc):
    """[{'label': '1(b)(iii)', 'path': (1,'b','iii'), 'segments': [{page, bbox}], 'text', 'marks_codes'}]"""
    rows, current = [], None
    for pno, page in enumerate(doc):
        lines = _lines(page)
        area = _table_area(page, lines)
        if not area:
            continue
        top, bottom = area
        qcol = [l for l in lines if l['x0'] < 120 and top <= l['y0'] <= bottom]
        labels = [l for l in qcol if LABEL.match(l['text'].replace(' ', ''))]
        if not labels and not current:
            continue
        x0, x1 = 58.0, page.rect.width - 58.0
        cuts = [(l['y0'] - 4, l) for l in labels]
        if current and (not cuts or cuts[0][0] > top + 4):
            cuts.insert(0, (top, None))          # continuation of the previous label
        headers = [l['y0'] for l in lines if l['text'] == 'Question' and l['x0'] < 130]
        for i, (y, lab) in enumerate(cuts):
            y_end = cuts[i + 1][0] if i + 1 < len(cuts) else bottom
            y_end = min([y_end] + [h - 3 for h in headers if h > y + 6])   # a new table starts mid-page
            if lab is not None:
                text = lab['text'].replace(' ', '')
                m = LABEL.match(text)
                path = (int(m.group(1)),) + tuple(g.strip('()') for g in m.groups()[1:] if g)
                current = {'label': text, 'path': path, 'segments': [], 'text': '', 'marks_codes': []}
                rows.append(current)
            body = [l for l in lines if y - 1 <= l['y0'] < y_end - 1 and l['x0'] >= 120 and l['x0'] < 730]
            codes = [l['text'] for l in lines if y - 1 <= l['y0'] < y_end - 1 and l['x0'] >= 730 and re.fullmatch(r'[ABCM]\d|\d', l['text'])]
            ink = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines if y - 1 <= l['y0'] < y_end - 1]
            if not ink:
                continue
            seg_bottom = min(y_end, max(r.y1 for r in ink) + 6)
            current['segments'].append({'page': pno + 1, 'bbox': [x0, round(y, 1), x1, round(seg_bottom, 1)]})
            current['text'] = (current['text'] + '\n' + '\n'.join(l['text'] for l in body)).strip()
            current['marks_codes'] += codes
    return rows
