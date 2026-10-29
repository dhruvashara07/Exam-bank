"""Read Cambridge mark schemes.

MCQ (papers 1, 2): a table of question number -> letter.
Structured (papers 3-6): landscape table with a Question column (labels like 1(b)(iii)),
an Answer column and a Marks column. Each label's rows become one or more page strips.
"""
import re
import pymupdf as fitz
from layout import norm

LABEL = re.compile(r'^(\d{1,2})((?:\([a-z]\))?)((?:\([ivx]+\))?)((?:,\([a-z]+\))*)(\d?)\.?$')


def label_text(t):
    """A label cell as printed, tidied: no spaces, Cambridge typos '7(a)((i)' / '3(b((i)' fixed,
    '2(d)(i)&(ii)' read like '2(d)(i),(ii)'."""
    t = t.replace(' ', '').replace('&', ',')
    t = re.sub(r'\(\(+', '(', t)
    t = re.sub(r'^(\d{1,2})([a-z])(?=\(|$)', r'\1(\2)', t)          # '9b(i)'
    return re.sub(r'\(([a-z]+)\(', r'(\1)(', t)


NONUM = re.compile(r'^\([a-z]\)(\([ivx]+\))?$')     # '(b)(ii)' printed without its question number
# 1(a)(ii)        a normal row
# 2(a)(i),(ii)    one answer for several parts -> one row per listed part, same pieces
# 8(a)(ii)1       numbered item of 8(a)(ii) -> continues that row


def _lines(page):
    """Text lines of a mark-scheme page, rebuilt from characters. Some mark schemes draw every table
    cell's text in clipped pieces, so PyMuPDF reports 'Que' + 'estion' or '1' + '0(a)' with a character
    printed twice; duplicates are dropped and pieces on one baseline are joined. A gap of more than
    10 pt starts a new line (table columns stay apart)."""
    chars = []
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            if abs(l['dir'][1]) > 0.1:
                continue
            for s in l['spans']:
                for c in s['chars']:
                    chars.append((round(c['origin'][1], 1), c['bbox'][0], c['bbox'][2], c['c'], s['size'], c['bbox'][1], c['bbox'][3]))
    chars.sort(key=lambda c: (c[0], c[1]))
    rows = []                                    # group by baseline
    for c in chars:
        if rows and abs(rows[-1][0][0] - c[0]) < 1.2:
            rows[-1].append(c)
        else:
            rows.append([c])
    out = []
    for row in rows:
        row.sort(key=lambda c: c[1])
        kept = []
        for c in row:
            if kept and c[3] == kept[-1][3] and abs(c[1] - kept[-1][1]) < 1.5:
                continue                         # the same character printed twice
            kept.append(c)
        piece = []
        def flush():
            t = norm(''.join(p[3] for p in piece)).strip()
            if t:
                out.append({'x0': min(p[1] for p in piece), 'y0': min(p[5] for p in piece),
                            'x1': max(p[2] for p in piece), 'y1': max(p[6] for p in piece), 'text': re.sub(r'\s+', ' ', t)})
        last = None
        for c in kept:
            if c[3].strip():
                if last is not None and c[1] - last[2] > 10:
                    flush(); piece = []
                elif last is not None and c[1] - last[2] > 0.25 * c[4] and piece and piece[-1][3] != ' ':
                    piece.append((c[0], last[2], c[1], ' ', c[4], c[5], c[6]))
                last = c
            elif not piece:
                continue                         # leading spaces
            piece.append(c)
        flush()
    return sorted(out, key=lambda d: (round(d['y0']), d['x0']))


def mcq_key(doc):
    """Question number -> letter. Works for one table (2017+) and two side-by-side columns (2015-16):
    each number takes the nearest A-D letter to its right on the same row."""
    key = {}
    for page in doc:
        lines = _lines(page)
        nums = [l for l in lines if re.fullmatch(r'\d{1,2}', l['text']) and 1 <= int(l['text']) <= 40]
        letters = [l for l in lines if re.fullmatch(r'[ABCD]', l['text']) or re.search(r'discounted', l['text'], re.I)]
        for n in nums:
            right = [l for l in letters if abs(l['y0'] - n['y0']) < 3.5 and 0 < l['x0'] - n['x1'] < 180]
            if right:
                t = min(right, key=lambda l: l['x0'] - n['x1'])['text']
                key.setdefault(int(n['text']), 'DISCOUNTED' if 'discounted' in t.lower() else t)
    return key


def _table_area(page, lines):
    """Top (below the header row) and bottom (above the footer) of the answer table."""
    header = [l for l in lines if re.match(r'Question\b', l['text']) and l['y0'] < 120]
    if not header:
        return None
    top = header[0]['y1'] + 3
    foot = [l['y0'] for l in lines if l['y0'] > page.rect.height - 80 and ('©' in l['text'] or 'Page ' in l['text'])]
    bottom = (min(foot) if foot else page.rect.height - 40) - 6
    return top, bottom


def _columns(lines):
    """x limits of the label column and the marks column, from the header row
    ('Question | Answer | Marks'); the table layout moved a little between years."""
    for h in lines:
        if re.match(r'Question\b', h['text']) and h['y0'] < 120:
            mk = [l for l in lines if abs(l['y0'] - h['y0']) < 4 and re.fullmatch(r'Marks?', l['text'].strip())]
            if mk:
                return h['x1'] + 2, mk[0]['x0'] - 15
    return 120, 730


def structured_rows(doc):
    rows = structured_rows_columns(doc) if is_column_format(doc) else structured_rows_table(doc)
    out = []
    for r in rows:
        out.append(r)
        for p in r.pop('also', []):            # one answer for several parts: give each part the same pieces
            label = str(p[0]) + ''.join(f'({x})' for x in p[1:])
            out.append({**r, 'label': label, 'path': p, 'shared_with': r['label']})
    return out


def structured_rows_table(doc):
    """[{'label': '1(b)(iii)', 'path': (1,'b','iii'), 'segments': [{page, bbox}], 'text', 'marks_codes'}]"""
    rows, current = [], None
    for pno, page in enumerate(doc):
        lines = _lines(page)
        area = _table_area(page, lines)
        if not area:
            continue
        top, bottom = area
        QX, CX = _columns(lines)
        qcol = [l for l in lines if l['x0'] < QX and top <= l['y0'] <= bottom]
        labels = [l for l in qcol if LABEL.match(label_text(l['text'])) or (rows and NONUM.match(label_text(l['text'])))]
        if not labels and not current:
            continue
        x0, x1 = 58.0, page.rect.width - 58.0
        cuts = [(l['y0'] - 4, l) for l in labels]
        if current and (not cuts or cuts[0][0] > top + 4):
            cuts.insert(0, (top, None))          # continuation of the previous label
        headers = [l['y0'] for l in lines if re.match(r'Question\b', l['text']) and l['x0'] < 130]
        for i, (y, lab) in enumerate(cuts):
            y_end = cuts[i + 1][0] if i + 1 < len(cuts) else bottom
            y_end = min([y_end] + [h - 3 for h in headers if h > y + 6])   # a new table starts mid-page
            if lab is not None:
                text = label_text(lab['text'])
                if NONUM.match(text) and current:
                    text = str(current['path'][0]) + text
                m = LABEL.match(text)
                path = (int(m.group(1)),) + tuple(g.strip('()') for g in m.groups()[1:3] if g)
                extra = [x for x in m.group(4).split(',') if x]        # ',(ii),(iii)'
                if m.group(5) and current and current['path'] == path:
                    pass                                               # numbered item: same row continues
                else:
                    label = str(path[0]) + ''.join(f'({x})' for x in path[1:])
                    current = {'label': label, 'path': path, 'segments': [], 'text': '', 'marks_codes': [],
                               'also': [path[:-1] + (x.strip('()'),) for x in extra]}
                    rows.append(current)
            body = [l for l in lines if y - 1 <= l['y0'] < y_end - 1 and l['x0'] >= QX and l['x0'] < CX]
            codes = [l['text'] for l in lines if y - 1 <= l['y0'] < y_end - 1 and l['x0'] >= CX and re.fullmatch(r'\(?[ABCM]\d\)?|\d|\[\d\]', l['text'])]
            ink = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines if y - 1 <= l['y0'] < y_end - 1]
            if not ink:
                continue
            seg_bottom = min(y_end, max(r.y1 for r in ink) + 6)
            current['segments'].append({'page': pno + 1, 'bbox': [x0, round(y, 1), x1, round(seg_bottom, 1)]})
            current['text'] = (current['text'] + '\n' + '\n'.join(l['text'] for l in body)).strip()
            current['marks_codes'] += codes
    return rows


def is_column_format(doc):
    """2015-16 mark schemes: portrait pages, labels in columns (1 / (a) / (i)), no 'Question' table."""
    for page in doc:
        t = page.get_text()
        if 'Question' in t and re.search(r'\b[Aa]nswers?\b', t) and 'Mark' in t:    # 'Answer', 'Expected answer'
            return False
    return True


OLD_Q, OLD_L, OLD_R = (30, 58), (60, 80), (82, 100)
ROMANS = {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x'}


def structured_rows_columns(doc):
    """Rows for the old column layout: label tokens start rows; a row runs down to the next label."""
    rows, current, cur = [], None, [0, None, None]
    for pno, page in enumerate(doc):
        lines = _lines(page)
        words = page.get_text('words')
        head = [l['y1'] for l in lines if l['y0'] < 80 and ('Cambridge' in l['text'] or 'Mark Scheme' in l['text'])]
        top = (max(head) + 8) if head else 60
        foot = [l['y0'] for l in lines if l['y0'] > page.rect.height - 80 and ('©' in l['text'] or 'UCLES' in l['text'])]
        bottom = (min(foot) if foot else page.rect.height - 40) - 6
        toks = []
        for x0, y0, x1, y1, w, *_ in words:
            if not (top <= y0 <= bottom):
                continue
            m = re.fullmatch(r'(\d{1,2})\(([a-p])\)[–-]\(([a-p])\)', w)         # '4(a)–(g)'
            m2 = re.fullmatch(r'\(([a-p])\)[–-]?\(([a-p])\)', w)                # '(h)(l)' = (h) to (l)
            if OLD_Q[0] <= x0 <= OLD_Q[1] and re.fullmatch(r'\d{1,2}', w):
                toks.append((y0, 'q', int(w)))
            elif OLD_Q[0] <= x0 <= OLD_L[1] and m:
                toks.append((y0, 'q', int(m.group(1))))
                toks.append((y0 + 0.01, 'l', (m.group(2), m.group(3))))
            elif OLD_L[0] <= x0 <= OLD_L[1] and m2 and m2.group(2) not in ROMANS and m2.group(2) > m2.group(1):
                toks.append((y0, 'l', (m2.group(1), m2.group(2))))
            elif 44 <= x0 <= OLD_L[1] and re.fullmatch(r'\([a-p]\)', w):
                toks.append((y0, 'l', w[1:-1]))
            elif OLD_L[0] <= x0 <= OLD_L[1] and re.fullmatch(r'\((?:ii|iii|iv|vi|vii)\)', w):
                toks.append((y0, 'r', w[1:-1]))                          # a roman part printed in the letter column
            elif OLD_R[0] <= x0 <= OLD_R[1] and re.fullmatch(r'\([ivx]+\)', w):
                toks.append((y0, 'r', w[1:-1]))
        order = {'q': 0, 'l': 1, 'r': 2}
        toks.sort(key=lambda t: t[0])
        grouped, row = [], []
        for t in toks:                                  # same text row: number, then letter, then roman
            if row and abs(t[0] - row[0][0]) >= 3:
                grouped += sorted(row, key=lambda r: order[r[1]]); row = []
            row.append(t)
        grouped += sorted(row, key=lambda r: order[r[1]])
        starts = []                                     # (y, path) - tokens on one row combine
        lastrng, rng = [], []
        for y, kind, val in grouped:
            if kind == 'q':
                if val != cur[0] + 1:
                    continue
                cur = [val, None, None]
            elif kind == 'l' and cur[0] and isinstance(val, str) and val > 'h' and \
                    not (cur[1] and (cur[1] == chr(ord(val) - 1) or (lastrng and lastrng[-1] >= chr(ord(val) - 1)))):
                if val in ROMANS and cur[1]:                 # '(i)' in the letter column: a roman part
                    cur = [cur[0], cur[1], val]
                elif val in ROMANS:
                    continue
                else:
                    continue
            elif kind == 'l' and cur[0]:
                span = val if isinstance(val, tuple) else (val, val)
                cur = [cur[0], span[0], None]
                rng = [chr(c) for c in range(ord(span[0]) + 1, ord(span[1]) + 1)]
                lastrng = rng or lastrng
            elif kind == 'r' and cur[1]:
                cur = [cur[0], cur[1], val]
            else:
                continue
            path = tuple(x for x in cur if x is not None)
            also = [(cur[0], x) for x in rng] if kind == 'l' else []
            if starts and abs(starts[-1][0] - y) < 3:
                starts[-1] = (starts[-1][0], path, also or starts[-1][2])
            else:
                starts.append((y, path, also))
        cuts = [(y - 4, p, a) for y, p, a in starts]
        if current and (not cuts or cuts[0][0] > top + 4):
            cuts.insert(0, (top, None, []))
        for i, (y, path, also) in enumerate(cuts):
            y_end = cuts[i + 1][0] if i + 1 < len(cuts) else bottom
            if path is not None:
                label = str(path[0]) + ''.join(f'({x})' for x in path[1:])
                current = {'label': label, 'path': path, 'segments': [], 'text': '', 'marks_codes': [], 'also': also}
                rows.append(current)
            if current is None:
                continue
            band = [l for l in lines if y - 1 <= l['y0'] < y_end - 1]
            if not band:
                continue
            body = [l for l in band if 100 <= l['x0'] < 480]
            codes = [l['text'] for l in band if l['x0'] >= 480 and re.fullmatch(r'\(?[ABCM]\d\)?|\d|\[\d\]', l['text'])]
            seg_bottom = min(y_end, max(l['y1'] for l in band) + 6)
            current['segments'].append({'page': pno + 1, 'bbox': [36.0, round(y, 1), page.rect.width - 36.0, round(seg_bottom, 1)]})
            current['text'] = (current['text'] + '\n' + '\n'.join(l['text'] for l in body)).strip()
            current['marks_codes'] += codes
    return rows
