"""Read Cambridge mark schemes.

MCQ (papers 1, 2): a table of question number -> letter.
Structured (papers 3-6): landscape table with a Question column (labels like 1(b)(iii)),
an Answer column and a Marks column. Each label's rows become one or more page strips.
"""
import os
import re
import pymupdf as fitz
from layout import norm

LABEL = re.compile(r'^(\d{1,2})((?:\([a-z]\))?)((?:\([ivx]+\))?)((?:,\([a-z]+\))*)(\d?)\.?$')


def label_text(t):
    """A label cell as printed, tidied: no spaces, Cambridge typos '7(a)((i)' / '3(b((i)' fixed,
    '2(d)(i)&(ii)' read like '2(d)(i),(ii)'."""
    t = t.replace(' ', '').replace('&', ',')
    t = re.sub(r'(?<=\d)MP\d+$', '', t)                              # '4 MP1' (practical marking points, 2017 MJ 53)
    t = re.sub(r'\(\(+', '(', t)
    t = re.sub(r'^(\d{1,2})([a-z])(?=\(|$)', r'\1(\2)', t)          # '9b(i)'
    t = re.sub(r'^(\d{1,2})([a-z])\)', r'\1(\2)', t)                 # '9a)(ii)' (2024 MJ 43 ms, M1)
    t = re.sub(r'^\((\d{1,2})([a-z])\)$', r'\1(\2)', t)                 # '(12b)' (2018 ON 22 ms, M3 pattern 244)
    return re.sub(r'\(([a-z]+)\(', r'(\1)(', t)


NONUM = re.compile(r'^\([a-z]\)(\([ivx]+\))?$')     # '(b)(ii)' printed without its question number
NONUM4 = re.compile(r'^\([a-z]\)\([ivx]+\)\([a-h]\)$')   # maths: '(a)(ii)(b)' (4th level, no number: 2024 MJ 41 q2, M1)
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
    if not header and _maths(page.parent):     # maths: the table can start lower on a page (general notes above it, 2019 ON 21 p3)
        header = [l for l in lines if re.match(r'Question\b', l['text']) and l['x0'] < 130
                  and any(abs(o['y0'] - l['y0']) < 4 and re.match(r'Answer', o['text'].strip()) for o in lines)]
    if not header:
        return None
    top = header[0]['y1'] + 3
    foot = [l['y0'] for l in lines if l['y0'] > page.rect.height - 80 and ('©' in l['text'] or 'Page ' in l['text'])]
    if not foot:                       # a landscape page printed shrunk onto portrait paper (2019 ON 42): footer higher up
        foot = [l['y0'] for l in lines if l['y0'] > top + 20 and ('©' in l['text'] or re.search(r'Page \d+ of \d+', l['text']))]
    bottom = (min(foot) if foot else page.rect.height - 40) - 6
    return top, bottom


def _columns(lines, maths=False):
    """x limits of the label column and the marks column, from the header row
    ('Question | Answer | Marks'); the table layout moved a little between years."""
    for h in lines:
        if re.match(r'Question\b', h['text']) and (h['y0'] < 120 or (maths and any(
                abs(o['y0'] - h['y0']) < 4 and re.match(r'Answer', o['text'].strip()) for o in lines))):
            mk = [l for l in lines if abs(l['y0'] - h['y0']) < 4 and re.fullmatch(r'Marks?', l['text'].strip())]
            if mk:
                return h['x1'] + 2, mk[0]['x0'] - 15
    return 120, 730


MS_RELABEL = {'2006ON_06': {'4(b)': ('4(b)(i)', (4, 'b', 'i')), '4(c)': ('4(b)(ii)', (4, 'b', 'ii')), '4(d)': ('4(b)(iii)', (4, 'b', 'iii'))},
              '2003ON_03': {'11(a)': ('11(a)(i)', (11, 'a', 'i')), '11(b)': ('11(a)(ii)', (11, 'a', 'ii')),
                            '11(c)(i)': ('11(b)(i)', (11, 'b', 'i')), '11(c)(ii)': ('11(b)(ii)', (11, 'b', 'ii'))}}
# a part the mark scheme does not label: (text the line starts with, label) - read by eye (Dhruv, round 23)
MS_SPLIT = {'0625_2005MJ_02_q07': [('sound ticked', '7(b)')],
            '0625_2005ON_06_q03': [('well judged', '3(c)')]}


QHEAD = re.compile(r'^(\d{1,2})\.?$')
TOTAL_LINE = re.compile(r'^TOTAL\s+(\d+)$')


def practical_rows(doc):
    """Practical-test mark schemes before 2009 (0625/05): numbered questions '1.' with one line per mark and
    'TOTAL 15' under the last one, no (a)/(b) labels and no table rules. One row per question, ended by its TOTAL line
    (marks_codes = [that total]; the paper itself prints no marks)."""
    rows, cur = [], None
    for pno, page in enumerate(doc):
        if pno == 0:
            continue
        lines = [l for l in _lines(page) if l['y0'] > 66 and l['y1'] < 800]    # page header / footer out
        seg = None

        def push():
            nonlocal seg
            if cur is not None and seg:
                cur['segments'].append({'page': pno + 1, 'bbox': [round(max(0.0, seg[2] - 6), 1), round(seg[0] - 3, 1),
                                                                  round(seg[3] + 6, 1), round(seg[1] + 4, 1)]})
            seg = None
        for l in lines:
            m = QHEAD.match(l['text'])
            if m and l['x0'] < 100 and (cur is None or cur.get('done')):
                cur = {'label': m.group(1), 'path': (int(m.group(1)),), 'segments': [], 'text': '', 'marks_codes': []}
                rows.append(cur)
            if cur is None or cur.get('done'):
                continue
            seg = [l['y0'], l['y1'], l['x0'], l['x1']] if not seg else \
                [seg[0], max(seg[1], l['y1']), min(seg[2], l['x0']), max(seg[3], l['x1'])]
            t = TOTAL_LINE.match(l['text'])
            if t:
                cur['marks_codes'], cur['done'] = [t.group(1)], True
                push()
            else:
                cur['text'] = (cur['text'] + '\n' + l['text']).strip()
        push()
    for r in rows:
        r.pop('done', None)
    return [r for r in rows if r['segments']]


def structured_rows(doc, old_practical=False):
    """old_practical: practical test before 2009 (one row per numbered question, ended by its TOTAL)."""
    rows = practical_rows(doc) if old_practical else []
    if len(rows) < 2:
        rows = structured_rows_columns(doc) if is_column_format(doc) else structured_rows_table(doc)
        if not rows:                   # 2008: the notes page names 'Question/Answer/Mark' but there is no table
            rows = structured_rows_columns(doc)
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
    MATHS = _maths(doc)
    for pno, page in enumerate(doc):
        lines = _lines(page)
        area = _table_area(page, lines)
        if not area:
            continue
        top, bottom = area
        QX, CX = _columns(lines, MATHS)
        if MATHS and (QX, CX) == (120, 730):        # header words not found (2019 ON 11): the printed column rules decide
            import collections as _c
            cov_ = _c.Counter()
            for d in page.get_drawings():
                if d['rect'].width < 2 and d['rect'].height > 5:
                    cov_[round(d['rect'].x0)] += d['rect'].height
            top_ = max(cov_.values()) if cov_ else 0
            vr = sorted(x for x, h_ in cov_.items() if h_ > 0.5 * top_)          # the table's own rules, not inner tables
            vr = [x for i_, x in enumerate(vr) if not i_ or x - vr[i_ - 1] > 3]
            if len(vr) >= 4:
                QX, CX = vr[1] - 1, vr[2] - 2
                MROW = vr[3] + 1 if len(vr) >= 5 else 1e9
        PX = 1e9                                 # maths 'Partial Marks' column: its numbers (fractions, tables) are no marks
        if MATHS and 'MROW' in locals() and MROW < 1e9 and (QX, CX) != _columns(lines, MATHS):
            PX = MROW
        elif MATHS:
            pm = [l['x0'] for l in lines if l['text'].strip().startswith('Partial') and l['y0'] < 130]
            if pm:
                vr = sorted(round(d['rect'].x0) for d in page.get_drawings() if d['rect'].width < 2 and d['rect'].height > 5
                            and CX + 10 < d['rect'].x0 < pm[0])
                PX = (vr[0] + 1) if vr else pm[0] - 5
        # notes printed UNDER the table, outside every cell ('Additional graph notes', 2023 ON 51 / 2020 ON 51 q4): general
        # marking notes, not the last question's answer - the row ends where the table's column rules end
        vb = [d['rect'].y1 for d in page.get_drawings() if d['rect'].height > 3 and d['rect'].width < 2 and d['rect'].y1 > top + 10]
        if vb and any(max(vb) + 4 < l['y0'] < bottom and l['x0'] < QX - 10 and not LABEL.match(label_text(l['text']))
                      for l in lines):
            bottom = min(bottom, max(vb) + 1)
        qcol = [l for l in lines if l['x0'] < QX and top <= l['y0'] <= bottom]
        labels = [l for l in qcol if LABEL.match(label_text(l['text'])) or ((rows or (MATHS and any(
                      LABEL.match(label_text(o['text'])) and o['y0'] < l['y0'] for o in qcol))) and NONUM.match(label_text(l['text'])))
                  or (MATHS and NONUM4.match(label_text(l['text'])))
                  or (MATHS and SUB4.match(label_text(l['text'])))
                  or (MATHS and COMM.match(l['text']))]
        #   maths: '(a)(ii)' without its number is a label also when the first labelled row is on this page (2020 ON 41 q2:
        #   every row after 2(a)(i) was lost; M3 reasons, pattern 243)
        if MATHS:                    # a label wrapped in the Q column ('5(a)(iv)' over '(b)', 2023 FM 62, M2 reasons):
            mg = []                  # one label '5(a)(iv)(b)' (a 4th level of 5(a)(iv)), not a row '(b)' = 5(b)
            for l in labels:
                if (mg and re.fullmatch(r'\([a-h]\)', label_text(l['text'])) and 0 <= l['y0'] - mg[-1]['y1'] < 4
                        and LABEL.match(label_text(mg[-1]['text'])) and abs(l['x0'] - mg[-1]['x0']) < 25
                        and SUB4.match(label_text(mg[-1]['text']) + label_text(l['text']))):
                    mg[-1] = dict(mg[-1], text=label_text(mg[-1]['text']) + label_text(l['text']), y1=l['y1'])
                    continue
                mg.append(l)
            labels = mg
        if not labels and not current:
            continue
        x0, x1 = 58.0, page.rect.width - 58.0
        # some papers (2016 MJ 41/42/62/63 ...) print the table wider than the usual cut: keep marks, totals and the right border
        xr = max([l['x1'] for l in lines if top <= l['y0'] <= bottom] + [0])
        xl = min([l['x0'] for l in lines if top <= l['y0'] <= bottom] + [page.rect.width])
        for d in page.get_drawings():
            r = d['rect']
            if r.height > 3 and r.width < 2 and top - 20 <= r.y0 <= bottom:
                xr = max(xr, r.x1); xl = min(xl, r.x0)
        if xr > x1 - 1:
            x1 = min(page.rect.width, xr + 3)
        if xl < x0 + 1:                          # ... and wider on the left (2016 ON 43: labels at x 56)
            x0 = max(0.0, xl - 3)
        hrules = [d['rect'].y0 for d in page.get_drawings()
                  if d['rect'].height < 2 and d['rect'].width > 0.5 * (x1 - x0)]   # full-width row rules
        # a label printed in the MIDDLE of its cell (2019 ON 33 q11): the row starts at the rule above it, not 4 pt above the label
        qrules_ = sorted((d['rect'].y0, d['rect'].x0) for d in page.get_drawings()   # rules across the Q column = Q-cell boundaries
                         if d['rect'].height < 2 and d['rect'].x0 < QX - 10 and d['rect'].x1 > QX - 15 and d['rect'].width > 20)
        qrules = [ry for ry, _ in qrules_]
        cuts, comm_floor = [], {}
        for k, l in enumerate(labels):
            y_ = l['y0'] - 4
            prev = labels[k - 1]['y1'] if k else top
            above = [ry for ry in qrules if prev + 1 < ry < l['y0'] - 1]
            if MATHS and COMM.match(l['text']):
                tight = [ry for ry, rx in qrules_ if l['y0'] - 9 < ry < l['y0'] and rx < l['x0'] - 1]
                if tight:              # maths: a 'Communication' row printed 6.5 pt under its full-width rule: the lift
                    comm_floor[id(l)] = max(tight) + 0.5   # climbed the column stubs above the text and the rules of the
                    #   merged cell above (2018 MJ 63 q4 'Justification', 9(b) A1 went into the communication row: marks 35
                    #   of 40; also approved 2019 ON 61 5(c)(ii); M3 reasons, pattern 242) -> never above that rule
            if above and y_ - max(above) > 4:
                y_ = max(above) + 1
            cuts.append((y_, l))
        if MATHS:
            cuts = _lift(page, cuts, QX - 2, top)
            cuts = [(max(c[0], comm_floor[id(c[1])]),) + tuple(c[1:]) if c[1] is not None and id(c[1]) in comm_floor
                    and c[0] < comm_floor[id(c[1])] - 1 else c for c in cuts]
        if current and (not cuts or cuts[0][0] > top + 4):
            cuts.insert(0, (top, None))          # continuation of the previous label
        headers = [l['y0'] for l in lines if (re.match(r'Question\b', l['text']) and l['x0'] < 130)
                   or (MATHS and re.match(r'(MODELLING|INVESTIGATION)\b|(Modelling|Investigation):', l['text'].strip()))
                   or (MATHS and re.fullmatch(r"(Modelling|Investigation)(\s+[A-Z0-9][\w']*)*\s*", l['text'].strip()))]
        #   ('Modelling DELIVERIES BY SCOOTER', 'Modelling Waste Plastic', a bare 'Modelling': 2024-2025 titles, M1)
        #                                                  part B heading ('MODELLING ...' 2021, 'Modelling: ...' 2025; round 28)
        for i, (y, lab) in enumerate(cuts):
            y_end = cuts[i + 1][0] if i + 1 < len(cuts) else bottom
            y_end = min([y_end] + [h - 3 for h in headers if h > y + 6 and (lab is None or h > lab['y0'])])
            # a new table starts mid-page (a header ABOVE the label never ends its row: the lifted first row of a page
            # reached over the table header and lost its content, round 28 2025 MJ 61 q1(a))
            if lab is not None and MATHS and COMM.match(lab['text']):
                current = {'label': 'C', 'path': ('C',), 'segments': [], 'text': '', 'marks_codes': [], 'also': []}
                rows.append(current)
            elif lab is not None:
                text = label_text(lab['text'])
                if (NONUM.match(text) or (MATHS and NONUM4.match(text))) and current:
                    text = str(current['path'][0]) + text
                sub4 = SUB4.match(text) if MATHS else None   # '4(b)(iii)(a)': a fourth level, part of 4(b)(iii) (2021 FM 42)
                if sub4:
                    text = sub4.group(1)
                m = LABEL.match(text)
                path = (int(m.group(1)),) + tuple(g.strip('()') for g in m.groups()[1:3] if g)
                extra = [x for x in m.group(4).split(',') if x]        # ',(ii),(iii)'
                if (MATHS and not m.group(2) and m.group(3) and m.group(3) not in ('(i)',) and current
                        and len(current['path']) == 3 and current['path'][0] == path[0] and isinstance(current['path'][1], str)):
                    path = (path[0], current['path'][1], path[1])   # maths: '1(ii)' printed after 1(b)(i) = 1(b)(ii)
                    #                                                 (2018 ON 42 q1; M3 reasons, pattern 244)
                if m.group(5) and current and current['path'] == path:
                    pass                                               # numbered item: same row continues
                else:
                    label = str(path[0]) + ''.join(f'({x})' for x in path[1:]) + (sub4.group(2) if sub4 else '')
                    current = {'label': label, 'path': path, 'segments': [], 'text': '', 'marks_codes': [],
                               'also': [path[:-1] + (x.strip('()'),) for x in extra]}
                    rows.append(current)
            body = [l for l in lines if y - 1 <= l['y0'] < y_end - 1 and l['x0'] >= QX and l['x0'] < CX]
            codes = [l['text'] for l in lines if y - 1 <= l['y0'] < y_end - 1 and CX <= l['x0'] < PX and re.fullmatch(r'\(?[ABCM]\d\)?|\d|\[\d\]', l['text'])]
            ink = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines if y - 1 <= l['y0'] < y_end - 1]
            if not ink:
                continue
            # pictures in the answer cell count too (2023 MJ 33 q8: the symbol-matching picture under the
            # column headings was cut off at the last text line)
            rot = page.rotation_matrix                # image boxes are unrotated; text is as displayed (landscape pages)
            pics = [r for r in ((fitz.Rect(i['bbox']).quad * rot).rect for i in page.get_image_info())
                    if y - 1 <= r.y0 < y_end - 1 and r.x0 >= QX - 2 and r.x1 <= CX + 2 and r.width >= 12 and r.height >= 12]
            # ... but not a picture of the next row (2016 MJ 41 q10: the diode starts above the next label)
            ink_y1 = max(r.y1 for r in ink)
            pics = [r for r in pics if not any(ink_y1 - 1 <= ry <= r.y0 + 1 for ry in hrules)]
            drawn = []
            if MATHS:                                 # vector drawings in the row count too (a Venn diagram / sketch
                for d_ in page.get_drawings():        # below the last text line was cut off, round 28: 2019 ON 42 q8)
                    r_ = d_['rect']
                    if not (y - 1 <= r_.y0 < y_end - 1 and r_.y1 <= y_end + 1 and r_.x0 >= QX - 2):
                        continue
                    if (r_.height < 1.6 and r_.width > 0.45 * (x1 - x0)) or r_.width < 1.6 or r_.width > 0.9 * (x1 - x0):
                        continue                      # table rules (row / column lines), the page box
                    if d_.get('fill') and not d_.get('color') and r_.width > 0.3 * (x1 - x0):
                        continue                      # a shaded cell background
                    drawn.append(r_)
            seg_bottom = min(y_end, max([r.y1 for r in ink] + [r.y1 for r in pics] + [r.y1 for r in drawn]) + 6)
            current['segments'].append({'page': pno + 1, 'bbox': [x0, round(y, 1), x1, round(seg_bottom, 1)]})
            current['text'] = (current['text'] + '\n' + '\n'.join(l['text'] for l in body)).strip()
            current['marks_codes'] += codes
    return rows


SUB4 = re.compile(r'^(\d{1,2}\([a-z]\)\([ivx]+\))(\([a-z]\))$')     # maths: 4(b)(iii)(a)
COMM = re.compile(r'^Communication(?::|\s+seen)')     # maths investigation papers: communication marks (ERROR_PATTERNS 67)


def _lift(page, cuts, x_min, top=None):
    """Maths: a row starts 4 pt above its label, but a numerator ('144' over '233'), a rotated table label ('All pos') or a
    table's top band can be printed higher (round 28): while a word or drawing crosses a row's top cut, the cut moves up
    above it (never above the previous label's line). cuts: [(y, label line or None, ...)] -> same list, y lifted."""
    W = page.rect.width
    ink = [fitz.Rect(w[:4]) for w in page.get_text('words') if w[0] >= x_min]
    ink += [fitz.Rect(im['bbox']) for im in page.get_image_info() if fitz.Rect(im['bbox']).x0 >= x_min]   # pasted tables
    drs_ = page.get_drawings()
    import collections as _co
    cover_ = _co.Counter()
    for d in drs_:
        if d['rect'].width < 1.6:
            cover_[round(d['rect'].x0)] += d['rect'].height
    main_x = [x for x, h in cover_.items() if h > 0.3 * page.rect.height]
    for d in drs_:
        r = d['rect']
        if r.width < 1.6 and any(abs(r.x0 - x) < 2.5 for x in main_x):
            continue                                  # a piece of a main column rule (drawn row by row, or in 6 pt pieces:
            #                                           the cut climbed up them, 2021 FM 52 q4(c)(ii))
        if r.x0 < x_min or (r.height < 1.6 and r.width > 0.45 * W) or (r.width < 1.6 and r.height > 0.35 * page.rect.height) \
                or r.width > 0.8 * W:
            continue                                  # the page table's own rules (an inner table's border counts:
            #                                           2021 FM 52 q3(b), its top row printed above the label)
        ink.append(fitz.Rect(r.x0, r.y0, r.x1, max(r.y1, r.y0 + 0.3)))
    out = []
    for i, c in enumerate(cuts):
        y, lab = c[0], c[1]
        if lab is None or (i == 0 and top is None):
            out.append(c); continue
        prev = cuts[i - 1][1] if i else None
        floor = (prev['y1'] + 1) if prev else (cuts[i - 1][0] + 2 if i else top + 1)   # first row of a page: the table top (not the header: its rule came in)
        for _ in range(6):
            cross = [r.y0 for r in ink if r.y0 < y - 0.5 and r.y1 > y + 1 and r.y0 > floor and r.y1 < lab['y1'] + 30]
            if not cross:
                break
            y = min(cross) - 2
        out.append((y,) + tuple(c[1:]))
    return out


def _maths(doc):
    m = re.search(r'/(\d{4})/\d{4}-[A-Z]{2}/', (doc.name or '').replace('\\', '/'))
    return bool(m) and m.group(1) != '0625'


def _maths_rules(page):
    """2014 maths mark schemes: a ruled table without a header row, Q | Answer | Mark | Notes. x of the long column rules."""
    import collections
    c = collections.Counter()
    for d in page.get_drawings():
        r = d['rect']
        if r.width < 2 and r.height > 5:
            c[round(r.x0)] += r.height
    if not c:
        return None
    top = max(c.values())
    xs = sorted(x for x, h in c.items() if h >= 0.75 * top and h > 60)     # the table's own rules (not a header box, inner tables)
    return xs if len(xs) == 5 else None


NOTE_RE = re.compile(r'Throughout the (modelling|investigation)\b', re.I)


def section_notes(doc, rows):
    """Maths (2026 MJ paper 6): a section-wide note printed once ('Throughout the modelling allow 4% as ...') is cut out of
    the row it fell in and put at the top of the first row of EVERY question after it (Dhruv, M1: top of every modelling
    question). rows: in print order; changed in place."""
    notes = []
    for pno, page in enumerate(doc):
        for l in _lines(page):
            if NOTE_RE.match(l['text'].strip()) and l['x0'] < 160:
                hr = sorted(d['rect'].y0 for d in page.get_drawings()
                            if d['rect'].height < 2 and d['rect'].width > 0.5 * page.rect.width and d['rect'].y0 > l['y1'] + 2)
                txt = [m for m in _lines(page) if m['y0'] >= l['y0'] - 1 and (not hr or m['y1'] <= hr[0] + 1)]
                y1 = hr[0] if hr else max(m['y1'] for m in txt) + 3
                notes.append((pno, l['y0'] - 4, y1))
    for pno, y0, y1 in notes:
        xs = [s_['bbox'] for r in rows for s_ in r['segments'] if s_['page'] == pno + 1]
        if not xs:
            continue
        x0, x1 = min(b[0] for b in xs), max(b[2] for b in xs)
        for r in rows:                                   # cut the note out of the row it fell in
            keep = []
            for s_ in r['segments']:
                b = list(s_['bbox'])
                if s_['page'] == pno + 1 and b[1] < y1 and b[3] > y0:
                    if b[1] < y0 - 3:
                        b[3] = min(b[3], y0)
                    elif b[3] > y1 + 3:
                        b[1] = max(b[1], y1)
                    else:
                        continue
                keep.append({**s_, 'bbox': b})
            r['segments'] = keep
        seen = set()
        for r in rows:
            if not r['segments'] or not isinstance(r['path'][0], int):
                continue
            s0 = r['segments'][0]
            if (s0['page'], s0['bbox'][1]) < (pno + 1, y0) or r['path'][0] in seen:
                continue
            seen.add(r['path'][0])
            r['segments'] = [{'page': pno + 1, 'bbox': [x0, y0, x1, y1], 'note': True}] + r['segments']
    return rows


def fold_communication(rows):
    """A 'Communication' row (label 'C') owns the rows printed under it that name earlier questions (its criteria):
    they are not mark-scheme rows of those questions. Returns (rows, communication rows)."""
    out, comms, last = [], [], ()
    RN = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
    def key(p):
        q = p[0] if isinstance(p[0], int) else 0
        let = ord(p[1]) if len(p) > 1 else 0
        rom = RN.index(p[2]) + 1 if len(p) > 2 and p[2] in RN else 0
        return (q, let, rom)
    cur = None
    for r in rows:
        if r['path'][0] == 'C':
            cur = dict(r, criteria=[]); comms.append(cur); continue
        if cur is not None and key(r['path']) <= key(last):
            cur['criteria'].append({'label': r['label'], 'text': r['text']})
            cur['segments'] += r['segments']
            continue
        cur = None
        out.append(r); last = r['path']
    return out, comms


def is_column_format(doc):
    """2015-16 mark schemes: portrait pages, labels in columns (1 / (a) / (i)), no 'Question' table."""
    for page in doc:
        t = page.get_text()
        if 'Question' in t and re.search(r'\b[Aa]nswers?\b', t) and 'Mark' in t:    # 'Answer', 'Expected answer'
            return False
    return True


OLD_Q, OLD_L, OLD_R = (30, 58), (60, 80), (82, 100)
ROMANS = {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x'}


def _label_columns(doc):
    """x ranges of the number / letter / roman label columns: they moved between years (2005 tables sit
    20 pt further right than 2015). Taken from where '(a)' and '(i)' tokens are printed most often."""
    import collections
    let, rom, num = collections.Counter(), collections.Counter(), collections.Counter()
    for page in doc:
        for x0, y0, x1, y1, w, *_ in page.get_text('words'):
            if x0 > 200:
                continue
            if re.fullmatch(r'\([a-h]\)', w) and w != '(i)':
                let[round(x0 / 4)] += 1
            elif re.fullmatch(r'\((?:i|ii|iii|iv)\)', w):
                rom[round(x0 / 4)] += 1
            elif re.fullmatch(r'\d{1,2}\.?', w):
                num[round(x0 / 4)] += 1
    if not let:
        return OLD_Q, OLD_L, OLD_R
    lx = let.most_common(1)[0][0] * 4
    if abs(lx - 66) < 8:                      # the 2015-16 layout: keep the tuned ranges
        return OLD_Q, OLD_L, OLD_R
    nx = max([k * 4 for k, n in num.items() if k * 4 < lx - 4] or [lx - 20], key=lambda x: num[round(x / 4)])
    rx = rom.most_common(1)[0][0] * 4 if rom else lx + 16
    return (nx - 8, lx - 4), (lx - 6, lx + 14), (rx - 6, rx + 14)


def structured_rows_columns(doc):
    """Rows for the old column layout: label tokens start rows; a row runs down to the next label."""
    cols = _label_columns(doc)
    OLD_Q, OLD_L, OLD_R = cols
    if int((re.search(r'/((?:19|20)\d\d)-', doc.name or '') or [0, '9999'])[1]) < 2013 and cols != (globals()['OLD_Q'], globals()['OLD_L'], globals()['OLD_R']):
        pre09_l = OLD_R[1]                               # pre-2009: a letter (not i/v/x) may sit in the roman column (2005 ON 03 q11)
    else:
        pre09_l = None
    CODE_X = 480 if cols == (globals()['OLD_Q'], globals()['OLD_L'], globals()['OLD_R']) else 420   # 2005: codes at 470
    rows, current, cur = [], None, [0, None, None]
    MATHS, mr, qoff = _maths(doc), None, 0
    for pno, page in enumerate(doc):
        lines = _lines(page)
        words = page.get_text('words')
        if MATHS:                   # a broken text layer prints words as overlapping pieces ('(i' + 'ii)' = '(ii)', '1F' + 'FT'
            fixed = []              # = '1FT', 2014 MJ 62 p4: (f)(ii), (g)(ii) and a 1FT mark were lost - round 30). Normal text
            for w_ in sorted(words, key=lambda q_: q_[0]):          # never overlaps the word before it.
                pr = next((o for o in reversed(fixed) if abs(o[1] - w_[1]) < 2.5 and o[0] < w_[0] < o[2] - 1.0), None)
                if pr is not None:
                    a_, b_ = pr[4], w_[4]
                    k_ = max((n for n in range(1, min(len(a_), len(b_)) + 1) if a_[-n:] == b_[:n]), default=0)
                    if k_:
                        fixed[fixed.index(pr)] = (pr[0], pr[1], max(pr[2], w_[2]), max(pr[3], w_[3]), a_ + b_[k_:]) + tuple(pr[5:])
                        continue
                fixed.append(w_)
            words = fixed
        mr = (_maths_rules(page) or (mr if pno else None)) if MATHS else None   # 2014 maths: marks between the 3rd and 4th rule
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
            if OLD_Q[0] <= x0 <= OLD_Q[1] and re.fullmatch(r'\d{1,2}\.?', w):
                toks.append((y0, 'q', int(w.rstrip('.'))))   # 2011 MJ 52/61 print '1.' for the question number
            elif OLD_Q[0] <= x0 <= OLD_L[1] and m:
                toks.append((y0, 'q', int(m.group(1))))
                toks.append((y0 + 0.01, 'l', (m.group(2), m.group(3))))
            elif OLD_Q[0] <= x0 <= OLD_L[1] and re.fullmatch(r'(\d{1,2})\(([a-p])\)', w):      # '10(a)' printed as one word
                mm = re.fullmatch(r'(\d{1,2})\(([a-p])\)', w)
                toks.append((y0, 'q', int(mm.group(1))))
                toks.append((y0 + 0.01, 'l', mm.group(2)))
            elif OLD_L[0] <= x0 <= OLD_L[1] and m2 and m2.group(2) not in ROMANS and m2.group(2) > m2.group(1):
                toks.append((y0, 'l', (m2.group(1), m2.group(2))))
            elif 44 <= x0 <= (pre09_l if pre09_l and w[1:-1] not in ROMANS else OLD_L[1]) and re.fullmatch(r'\([a-p]\)', w):
                toks.append((y0, 'l', w[1:-1]))
            elif OLD_L[0] <= x0 <= OLD_L[1] and re.fullmatch(r'\((?:ii|iii|iv|vi|vii)\)', w):
                toks.append((y0, 'r', w[1:-1]))                          # a roman part printed in the letter column
            elif OLD_R[0] <= x0 <= OLD_R[1] and re.fullmatch(r'\([ivx]+\)', w):
                toks.append((y0, 'r', w[1:-1]))
        if MATHS:
            toks += [(l['y0'], 'c', None) for l in lines if l['x0'] < 160 and COMM.match(l['text']) and top <= l['y0'] <= bottom]
            toks += [(l['y0'] - 0.01, 'b', None) for l in lines if l['x0'] < 60 and l['text'].strip() == 'B' and top <= l['y0'] <= bottom]
        order = {'q': 0, 'l': 1, 'r': 2, 'c': 0, 'b': -1}
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
            if kind == 'c':
                starts.append((y, ('C',), []))
                continue
            if kind == 'b':                       # 2014 paper 6: part B numbers from 1 again (the paper's are ours, continued)
                qoff = cur[0]
                continue
            if kind == 'q':
                val = val + qoff
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
        if re.search(r'/(?:200\d|201[012])-', doc.name or '') or _maths(doc):   # (maths too: 2014 MJ 21 q5(b), round 28)
            # a fraction's numerators ('1/u' printed as a fraction, 2012 ON 63 q4(b), round 26) stand above the
            # label's line and reach into it: the row starts above them, not between them and their fraction
            cuts = [(min([y - 4] + [w[1] - 1 for w in words if y - 10 < w[1] < y - 4 and w[3] > y + 1]), p, a)
                    for (y, p, a) in [(y_, p_, a_) for y_, p_, a_ in starts]]
        if _maths(doc):
            labs = {}
            for l in lines:
                for (yy, p_, a_) in cuts:
                    if p_ is not None and abs(l['y0'] - (yy + 4)) < 0.6 and l['x0'] < 100:
                        labs.setdefault(yy, l)
            tmp = [(yy, labs.get(yy, {'y0': yy + 4, 'y1': yy + 14}) if p_ is not None else None, p_, a_) for yy, p_, a_ in cuts]
            cuts = [(t_[0], t_[2], t_[3]) for t_ in _lift(page, tmp, 90)]
        if current and (not cuts or cuts[0][0] > top + 4):
            cuts.insert(0, (top, None, []))
        for i, (y, path, also) in enumerate(cuts):
            y_end = cuts[i + 1][0] if i + 1 < len(cuts) else bottom
            if path == ('C',):
                current = {'label': 'C', 'path': path, 'segments': [], 'text': '', 'marks_codes': [], 'also': []}
                rows.append(current)
            elif path is not None:
                label = str(path[0]) + ''.join(f'({x})' for x in path[1:])
                current = {'label': label, 'path': path, 'segments': [], 'text': '', 'marks_codes': [], 'also': also}
                rows.append(current)
            if current is None:
                continue
            band = [l for l in lines if y - 1 <= l['y0'] < y_end - 1]
            if not band:
                continue
            body = [l for l in band if 100 <= l['x0'] < 480]
            if mr:                                # 2014 maths: the Mark column (numbers, '2FT'); notes beside it are not marks
                codes = [w[4] for w in {(round(w[0]), round(w[1]), w[4]): w for w in words}.values()   # text printed twice (2014 MJ 62 p4)
                         if y - 1 <= w[1] < y_end - 1 and mr[2] - 2 <= w[0] < mr[3] and re.fullmatch(r'\d{1,2}(?:FT|ft)?|C\d|[ABM]\d', w[4])]
            else:
                codes = [l['text'] for l in band if l['x0'] >= CODE_X and re.fullmatch(r'\(?[ABCM]\d\)?|\d|\[\d\]', l['text'])]
            drawn = []
            if _maths(doc):                           # vector drawings in the row count too (2014 MJ 31 q10: the Venn
                for d_ in page.get_drawings():        # diagram's lower half was cut off at the last text line, round 28)
                    r_ = d_['rect']
                    if not (y - 1 <= r_.y0 < y_end - 1 and r_.y1 <= y_end + 1 and r_.x0 >= 90):
                        continue
                    if (r_.height < 1.6 and r_.width > 0.45 * page.rect.width) or r_.width < 1.6 or r_.width > 0.8 * page.rect.width:
                        continue
                    drawn.append(r_)
            seg_bottom = min(y_end, max([l['y1'] for l in band] + [r.y1 for r in drawn]) + 6)
            current['segments'].append({'page': pno + 1, 'bbox': [36.0, round(y, 1), page.rect.width - 36.0, round(seg_bottom, 1)]})
            current['text'] = (current['text'] + '\n' + '\n'.join(l['text'] for l in body)).strip()
            current['marks_codes'] += codes
    return rows
