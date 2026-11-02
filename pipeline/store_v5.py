"""Store format v5 (docs/V5_SPEC.md): captions as text, numbering tags, answer bands.

Used by store.py while a paper is built:
    caption_rects(pg, bbox, caption)          caption line(s) of a figure/table inside its cut box (visible coordinates)
    drawing_box(pg, bbox, cap)                the figure's drawing WITHOUT its caption line (or the old box + a flag)
    tag_unit(u, ...)                          roles on words: caption / figref / partlabel / partref (numbering)
    answer_bands(u, fig_sizes)                y ranges the question-bank view removes (working space, full dotted lines)

Word roles (all optional, a word without role is plain text):
    qnum      the question number                     (already in v4)
    caption   the number word of a caption            ref {kind: fig|table, q, n}   "Fig. 3.1" -> q 3, n 1
    figref    the number word of a reference in text  ref {kind, q, n[, other]}     other: refers to another question
    partlabel a printed part label "(b)", "(ii)"      path "3(b)(ii)" (the part the label names)
    partref   a reference to a part in text "(a)(ii)" path "3(a)(ii)"
    mslabel   mark-scheme row label                   (already in v4)
"""
import re
import pymupdf as fitz

KEYWORD = re.compile(r'^(Fig\.?|Figs\.?|Figure|Figures|Table|Tables)$')
FUSED = re.compile(r'^(Fig\.?|Figs\.?|Figure|Figures|Table|Tables)(\d+\.\d+)([.,;:)]*)$')
NUMBER = re.compile(r'^(\d+)\.(\d+)([.,;:)]*)$')
DOTS = re.compile(r'^[.…]{5,}(\[\s*\d+\s*\])?$')          # dots, maybe glued to the mark '[1]'
MARKTOK = re.compile(r'^\[\s*\d+\s*\]$')
LABEL = re.compile(r'^\(([a-z]{1,3}|[ivx]{1,5}|\d)\)$')
PARTREF = re.compile(r'^(\([a-z]{1,2}\))?(\((?:i{1,3}|iv|v|vi{1,3}|ix|x)\))?([.,;:]*)$')


# ---------------------------------------------------------------- captions (page side)
def _vis_words(pg):
    m = pg.rotation_matrix
    out = []
    for w in pg.get_text('words'):
        r = (fitz.Rect(w[:4]).quad * m).rect
        out.append((r.x0, r.y0, r.x1, r.y1, w[4], w[5], w[6]))
    return out


def caption_prefix(caption):
    m = re.match(r'^(Fig\.?|Figure|Table)\s*(\d+)(?:\.(\d+))?', caption or '')
    if not m:
        return None
    kind = 'table' if m.group(1) == 'Table' else 'fig'
    return kind, int(m.group(2)), int(m.group(3) or 0)


def caption_rects(pg, bbox, caption):
    """Rectangles (visible coordinates) of the caption line of this figure inside bbox: 'Fig. 1.1' plus the
    words that follow on the same line ('(not to scale)'). Side-by-side captions on one text line are told
    apart by their number. Returns the one nearest the edge the caption belongs to, or None."""
    want = caption_prefix(caption)
    if not want:
        return None
    b = fitz.Rect(bbox) + (-1, -1, 1, 1)
    ws = [w for w in _vis_words(pg) if b.contains(fitz.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))]
    ws.sort(key=lambda w: (round((w[1] + w[3]) / 2 / 2), w[0]))
    found = []
    for i, w in enumerate(ws):
        kind = num = None
        fused = FUSED.match(w[4])
        if fused:
            kw, nn, rest, last = fused.group(1), fused.group(2), fused.group(3), i
        elif KEYWORD.match(w[4]) and i + 1 < len(ws) and NUMBER.match(ws[i + 1][4]) \
                and abs((ws[i + 1][1] + ws[i + 1][3]) / 2 - (w[1] + w[3]) / 2) < 3 and ws[i + 1][0] - w[2] < 8:
            kw, nn, rest, last = w[4], NUMBER.match(ws[i + 1][4]).group(0), '', i + 1
        else:
            continue
        mm = re.match(r'(\d+)\.(\d+)', nn)
        if not mm:
            continue
        kind = 'table' if kw.startswith('Table') else 'fig'
        if (kind, int(mm.group(1)), int(mm.group(2))) != want:
            continue
        rect = fitz.Rect(w[:4]) | fitz.Rect(ws[last][:4])
        j = last + 1                                   # words that follow on the same line: '(not to scale)'
        while j < len(ws) and abs((ws[j][1] + ws[j][3]) / 2 - (w[1] + w[3]) / 2) < 3 and ws[j][0] - rect.x1 < 12 \
                and not KEYWORD.match(ws[j][4]) and not FUSED.match(ws[j][4]):
            rect |= fitz.Rect(ws[j][:4]); j += 1
        found.append(rect)
    if not found:
        return None
    bb = fitz.Rect(bbox)
    if want[0] == 'table':
        return min(found, key=lambda r: r.y0)
    return max(found, key=lambda r: r.y0) if bb.height else found[0]


def without_caption(pg, cap):
    """A one-page copy of pg with the caption's words removed (lines, pictures and other text stay)."""
    d = fitz.open()
    d.insert_pdf(pg.parent, from_page=pg.number, to_page=pg.number)
    p = d[0]
    p.add_redact_annot(cap + (-0.3, -0.3, 0.3, 0.3), fill=False)
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    return p


def drawing_box(pg, bbox, cap):
    """The figure crop without its caption: (box, ok). ok=False: something else is printed in the caption's
    row/below it (ink or text), so the caption stays inside the figure (flagged by the caller)."""
    b = fitz.Rect(bbox)
    if cap is None:
        return b, True
    H = b.height
    m = pg.rotation_matrix
    def other_ink(y_lo, y_hi):
        """Something that is not the caption and is printed in the rows y_lo..y_hi of the crop?"""
        for w in _vis_words(pg):
            r = fitz.Rect(w[:4])
            if b.intersects(r) and r.y1 > y_lo and r.y0 < y_hi and not cap.intersects(r + (-.5, -.5, .5, .5)) \
                    and not (KEYWORD.match(w[4]) or FUSED.match(w[4]) or NUMBER.match(w[4])):
                return True                                   # (a neighbour's 'Fig. 1.2' on the same row is fine)
        for dr in pg.get_drawings():
            r = (dr['rect'].quad * m).rect
            if b.intersects(r) and r.y1 > y_lo and r.y0 < y_hi and not (r.x0 >= cap.x0 - 2 and r.x1 <= cap.x1 + 2):
                return True
        return False
    if cap.y0 > b.y0 + 0.5 * H:                          # caption under the drawing
        if other_ink(cap.y0 - 0.2, cap.y1 + 4):
            return b, False
        return fitz.Rect(b.x0, b.y0, b.x1, max(b.y0 + 4, cap.y0 - 0.8)), True
    if cap.y1 < b.y0 + 0.4 * H:                          # caption above
        if other_ink(cap.y0 - 4, cap.y1 + 0.2):
            return b, False
        return fitz.Rect(b.x0, min(b.y1 - 4, cap.y1 + 0.8), b.x1, b.y1), True
    return b, False


# ---------------------------------------------------------------- numbering tags (layout side)
def _centre(t, ox, oy):
    return t['x'] + ox + t['w'] / 2, t['y'] + oy - t['s'] * 0.3


def _split_trailing(txt):
    m = re.match(r'^(.*?)([.,;:)]*)$', txt)
    return m.group(1), m.group(2)


def tag_unit(u, ox, oy, qnum, captions, path, docname, first_unit, ms_label=None):
    """Tag roles on the words of one unit.
    captions: [{'rect': Rect page coords, 'kind', 'q', 'n'}]   the caption lines of this question's figures/tables
    path: the part's path ('3(b)(ii)'); first_unit: this unit is where the part starts (its label is printed here)"""
    ws = u['text']
    # captions first: a number word inside a caption rect
    for t in ws:
        cx, cy = _centre(t, ox, oy)
        for c in captions:
            if (c['rect'] + (-1, -1, 1, 1)).contains(fitz.Point(cx, cy)) and NUMBER.match(t['t']) or \
               (c['rect'] + (-1, -1, 1, 1)).contains(fitz.Point(cx, cy)) and FUSED.match(t['t']):
                t['role'] = 'caption'
                t['ref'] = {'kind': c['kind'], 'q': c['q'], 'n': c['n']}
                break
    # references in running text: 'Fig. 3.1', 'Figs. 1.1 and 1.2', 'Table 2.1'
    i = 0
    while i < len(ws):
        t = ws[i]
        kw = None
        if KEYWORD.match(t['t']):
            kw = t['t']
        elif FUSED.match(t['t']):
            kw = FUSED.match(t['t']).group(1)
        if kw:
            kind = 'table' if kw.startswith('Table') else 'fig'
            j = i
            if FUSED.match(t['t']):
                cand = [t]
            else:
                cand = []
                j = i + 1
                plural = t['t'].lower().startswith(('figs', 'figures', 'tables'))
                k = j                                          # numbers after the keyword: 'Figs. 1.1 and 1.2'
                while k < len(ws) and k < i + 8:
                    w = ws[k]
                    if NUMBER.match(w['t']) and abs(w['y'] - t['y']) <= 3:
                        cand.append(w); k += 1
                        if not plural:
                            break
                    elif plural and cand and w['t'] in ('and', ',', 'to', '&', 'or') and abs(w['y'] - t['y']) <= 3:
                        k += 1
                    else:
                        break
            for w in cand:
                if w.get('role') == 'caption':
                    continue
                mm = re.match(r'.*?(\d+)\.(\d+)', w['t'])
                if not mm:
                    continue
                q = int(mm.group(1))
                w['role'] = 'figref'
                w['ref'] = {'kind': kind, 'q': q, 'n': int(mm.group(2))}
                if q != qnum:
                    w['ref']['other'] = True
            i = max(i + 1, j)
            continue
        i += 1
    # part labels: bold '(b)' '(ii)' leading the first printed line of a part (and its ancestors' labels)
    comps = re.findall(r'\([^()]*\)', path)
    if docname == 'qp' and first_unit and comps:
        top = min((t for t in ws if t.get('role') != 'qnum' and t['s'] >= 9), key=lambda t: (round(t['y']), t['x']), default=None)
        if top is not None:
            line = sorted([t for t in ws if abs(t['y'] - top['y']) < 2.5 and t.get('b') and LABEL.match(t['t']) and t['x'] < 130],
                          key=lambda t: t['x'])
            lead = []
            for t in line:                       # consecutive label words from the left: '(d)' '(i)'
                if lead and t['x'] - (lead[-1]['x'] + lead[-1]['w']) > 40:
                    break
                lead.append(t)
            n = min(len(lead), len(comps))
            if n:
                use = lead[:n]
                names = comps[len(comps) - n:]
                for t, nm in zip(use, names):
                    if t['t'] != nm:                      # the printed label must be the path's own label
                        continue
                    k = comps.index(nm)
                    t['role'] = 'partlabel'
                    t['path'] = str(qnum) + ''.join(comps[:k + 1])
    # mark-scheme row label '4(b)(ii)': its left-column words '(b)' '(ii)' (and the number) follow the part's new label
    if docname == 'ms' and ms_label:
        cs = re.findall(r'\([^()]*\)', ms_label)
        k = 0
        for t in sorted([t for t in ws if t['x'] < 150 and not t.get('role')], key=lambda t: (round(t['y']), t['x'])):
            if k < len(cs) and t['t'] == cs[k]:
                t['role'] = 'partlabel'
                t['path'] = str(qnum) + ''.join(cs[:k + 1])
                k += 1
    # references to parts in text: '(a)(ii)', '(b)(i)', '(c)'; a bare '(iv)' follows the letter before it
    if docname == 'qp':
        letter = re.match(r'\d+(\([a-z]{1,2}\))?', path).group(1) if path else None
        for t in ws:
            if t.get('role') or t['x'] <= 110:
                continue
            m = re.fullmatch(r'(\([a-z]{1,2}\))?(\((?:i{1,3}|iv|v|vi{1,3}|ix|x)\))?([.,;:]?)', t['t'])
            if not m or not (m.group(1) or m.group(2)):
                continue
            if m.group(1):
                letter = m.group(1)
            t['role'] = 'partref'
            t['path'] = str(qnum) + (m.group(1) or letter or '') + (m.group(2) or '')
    return u


# ---------------------------------------------------------------- answer bands
def path_bbox(d):
    toks = re.findall(r'[MLHVCZ]|-?\d+(?:\.\d+)?', d)
    xs, ys = [], []
    i, cmd, cx, cy = 0, None, 0.0, 0.0
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCZ' and len(t) == 1 and t.isalpha():
            cmd = t; i += 1
            if cmd == 'Z':
                continue
            continue
        if cmd in ('M', 'L') and i + 1 < len(toks):
            cx, cy = float(toks[i]), float(toks[i + 1]); xs.append(cx); ys.append(cy); i += 2
        elif cmd == 'H':
            cx = float(toks[i]); xs.append(cx); i += 1
        elif cmd == 'V':
            cy = float(toks[i]); ys.append(cy); i += 1
        elif cmd == 'C' and i + 5 < len(toks):
            for k in range(0, 6, 2):
                xs.append(float(toks[i + k])); ys.append(float(toks[i + k + 1]))
            i += 6
        else:
            i += 1
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def _rows(words):
    """Words grouped into text rows by baseline (sub/superscripts join the row of their neighbours)."""
    rows = []
    for w in sorted(words, key=lambda w: (w['y'], w['x'])):
        for r in rows:
            if abs(r['y'] - w['y']) <= 3.5 and (w['s'] >= 8.5 or r['words']) and abs(r['y'] - w['y']) <= (3.5 if w['s'] < 9 else 2.2):
                r['words'].append(w); break
        else:
            rows.append({'y': w['y'], 'words': [w]})
    for r in rows:
        r['top'] = min(w['y'] - w['s'] * 0.85 for w in r['words'])
        r['bot'] = max(w['y'] + w['s'] * 0.25 for w in r['words'])
        r['x0'] = min(w['x'] for w in r['words']); r['x1'] = max(w['x'] + w['w'] for w in r['words'])
    return rows


WORK_GAP = 28.0        # a blank vertical gap longer than this (pt) is working space
KEEP_GAP = 9.0         # what stays of such a gap in the question-bank view


def _rows(words):
    """Words grouped into text rows by baseline; sub/superscripts join the nearest row."""
    rows = []
    for w in sorted((w for w in words if w['s'] >= 8.5), key=lambda w: (w['y'], w['x'])):
        for r in rows:
            if abs(r['y'] - w['y']) <= 2.2:
                r['words'].append(w); break
        else:
            rows.append({'y': w['y'], 'words': [w]})
    for w in words:
        if w['s'] < 8.5:
            near = min(rows, key=lambda r: abs(r['y'] - w['y']), default=None)
            if near is not None and abs(near['y'] - w['y']) <= 6:
                near['words'].append(w)
            else:
                rows.append({'y': w['y'], 'words': [w]})
    for r in rows:
        r['top'] = min(w['y'] - w['s'] * 0.85 for w in r['words'])
        r['bot'] = max(w['y'] + w['s'] * 0.25 for w in r['words'])
    return rows


def answer_bands(u, fig_sizes):
    """Bands (y ranges in unit coordinates) the question-bank view removes: full dotted answer lines and blank
    working space. Kept as they are: dots inside a sentence, 'm = ..... g' lines, tables to complete, grids to
    draw on, answer boxes. Sets w['hide'] = 1 on the dots (and prefix) of a full answer line whose row must
    stay because it carries the mark '[2]'."""
    if u.get('exact') or not u['text']:
        return []
    wide = max(u['w'] - 80.0, 100.0)
    kept, hidden = [], []
    for r in _rows([w for w in u['text'] if not w.get('dir')]):
        ws = sorted(r['words'], key=lambda w: w['x'])
        dots = [w for w in ws if DOTS.match(w['t'])]
        marks = [w for w in ws if MARKTOK.match(w['t']) or w.get('role') == 'total' or w['t'].startswith('[Total')
                 or (DOTS.match(w['t']) and w['t'].endswith(']'))]
        rest = [w for w in ws if w not in dots and w not in marks]
        prefix_ok = all((not w.get('b')) and len(w['t']) <= 4 and re.fullmatch(r'\(?[0-9a-z]{1,3}[.)]?', w['t']) for w in rest)
        if dots and sum(w['w'] for w in dots) >= 0.30 * wide and prefix_ok:     # a full answer line
            if marks:                                      # the mark stays: hide only the dots and the prefix
                for w in dots + rest:
                    w['hide'] = 1
                kept.append((r['top'], r['bot']))
            else:
                hidden.append((r['top'], r['bot']))
        else:
            kept.append((r['top'], r['bot']))
    for l in u['lines']:
        bb = path_bbox(l['d'])
        if not bb:
            continue
        x0, y0, x1, y1 = bb
        if l.get('dash') and (y1 - y0) < 1.5 and (x1 - x0) >= 0.30 * wide:    # a long dotted drawn line = answer line
            hidden.append((y0 - 3, y1 + 3))
        else:
            kept.append((y0, y1))
    for f in u['figs']:
        sz = fig_sizes.get(f['id'])
        if sz:
            kept.append((f['y'], f['y'] + sz[1]))
    for im in u.get('images', []) + u.get('glyphs', []):
        kept.append((im['y'], im['y'] + im['h']))
    if not kept:
        return [{'y0': 0.0, 'y1': round(u['h'], 1), 'kind': 'dots'}] if hidden else []
    kept.sort()
    bands, lo = [], None
    for idx in range(len(kept) + 1):
        hi = kept[idx][0] if idx < len(kept) else u['h']
        start = 0.0 if lo is None else lo
        inside = [h for h in hidden if h[0] >= start - 2 and h[1] <= hi + 2]
        gap = hi - start
        if inside and (lo is None or gap > KEEP_GAP + 4):
            y0 = start if lo is None else start + KEEP_GAP
            bands.append({'y0': round(y0, 1), 'y1': round(hi, 1), 'kind': 'dots'})
        elif lo is not None and gap > WORK_GAP:
            bands.append({'y0': round(start + KEEP_GAP, 1), 'y1': round(hi, 1), 'kind': 'work'})
        if idx < len(kept):
            lo = kept[idx][1] if lo is None else max(lo, kept[idx][1])
    return bands
