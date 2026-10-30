"""Page geometry helpers: content area, ink boxes, and label tokens.

All coordinates are PDF points with the origin at the top-left (PyMuPDF convention).
"""
import re
import pymupdf as fitz

CONTENT_X0, CONTENT_X1 = 30.0, 570.0      # outside this: margin strips (corner marks are filtered by shape)
QNUM_X = (44.0, 58.0)                     # question numbers
LETTER_X = (64.0, 80.0)                   # (a) (b) ...
ROMAN_X = (84.0, 104.0)                   # (i) (ii) ...
ROMAN = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
LETTERS = 'abcdefghijklmnop'           # (i) after (h) is a letter part; x position tells it from roman (i)

# Symbol-font characters that arrive as private-use code points
SYMBOL_MAP = {0xf0ae: '→', 0xf0ac: '←', 0xf0ad: '↑', 0xf0af: '↓', 0xf0b0: '°', 0xf0b1: '±', 0xf0b4: '×',
              0xf0b8: '÷', 0xf0a3: '≤', 0xf0b3: '≥', 0xf0bb: '≈', 0xf0b9: '≠', 0xf0d6: '√', 0xf0b5: '∝',
              0xf0a5: '∞', 0xf02d: '−', 0xf02b: '+', 0xf03d: '=', 0xf061: 'α', 0xf062: 'β', 0xf067: 'γ',
              0xf064: 'δ', 0xf065: 'ε', 0xf071: 'θ', 0xf06c: 'λ', 0xf06d: 'μ', 0xf070: 'π', 0xf072: 'ρ',
              0xf073: 'σ', 0xf077: 'ω', 0xf057: 'Ω', 0xf044: 'Δ', 0xf046: 'Φ', 0xf053: 'Σ', 0xf0d7: '·',
              0xf0a2: '′', 0xf0c5: '⊕', 0xf0de: '⇒', 0xf0db: '⇔'}


def norm(text):
    return ''.join(SYMBOL_MAP.get(ord(c), c) for c in text)


_BOUNDS = {}


def footer_ink_top(page, line):
    """Top of the printed glyphs of a footer line, measured on the rendered page (its text box starts
    higher than its ink, and the last answer line or a subscript can sit inside that box)."""
    import numpy as np
    sp = [s for s in line['spans'] if s['text'].strip()]
    base = max(s['origin'][1] for s in sp)
    clip = fitz.Rect(sp[0]['bbox'][0], line['bbox'][1] - 4, sp[-1]['bbox'][2], base)
    Z = 4.0
    pix = page.get_pixmap(matrix=fitz.Matrix(Z, Z), clip=clip, colorspace=fitz.csGRAY)
    a = (np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width) < 170).any(1)
    r = len(a) - 1
    while r > 0 and not a[r]:        # the baseline row itself can be blank
        r -= 1
    if not a[r]:
        return min(s['origin'][1] - 0.8 * s['size'] for s in sp)
    while r > 0 and a[r]:            # walk up from the baseline through the footer's own ink
        r -= 1
    top = clip.y0 + (r + 1) / Z
    if top < line['bbox'][1] - 0.5:  # ran into content touching the footer: estimate from the font size
        return max(line['bbox'][1] + 1.0, min(s['origin'][1] - 0.8 * s['size'] for s in sp) + 1.0)
    return top


def page_bounds(page):
    """Return (top, bottom) of the question content area on a page."""
    key = (page.parent.name, page.number)
    if key in _BOUNDS:
        return _BOUNDS[key]
    top, bottom = 50.0, page.rect.height - 40
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            t = ''.join(s['text'] for s in l['spans']).strip()
            y0, y1 = l['bbox'][1], l['bbox'][3]
            if y0 > 700 and ('©' in t or 'UCLES' in t or 'Turn over' in t or re.search(r'\d{4}/\d\d/[A-Z]/[A-Z]/\d\d', t)):
                bottom = min(bottom, footer_ink_top(page, l) - 1.0)
            if y0 > 560 and re.match(r'(Permission to reproduce|To avoid the issue of disclosure|Copyright Acknowledgements)', t):
                rules = [d['rect'].y0 for d in page.get_drawings()
                         if d['rect'].width > 300 and d['rect'].height < 2 and y0 - 30 < d['rect'].y0 < y0]
                bottom = min(bottom, min(rules) - 3.0 if rules else y0 - 6.0)   # copyright notice (and its rule) on the last page
            if y0 > 100 and 150 < l['bbox'][0] < 330 and re.fullmatch(
                    r'(Turn over( for (the next )?(question|page) ?\d*)?|Question \d+ (is|continues|begins|starts) on '
                    r'(the next (page|side)|the back page|page \d+)|Question continued on (the )?(next|following) (page|side))\.?', ' '.join(t.split())):
                bottom = min(bottom, y0 - 3.0)          # centred notice: 'Turn over', 'Question 10 is on the back page.'
            x0 = l['bbox'][0]
            if y0 < 58 and y1 < 72 and re.fullmatch(r'\d{1,2}', t) and 240 < x0 < 360:   # page number (lower when a barcode sits above it)
                top = max(top, y1 + 4)
    if len(_BOUNDS) > 4000:
        _BOUNDS.clear()
    _BOUNDS[key] = (top, bottom)
    return top, bottom


def visible_lines(page, top, bottom):
    """Horizontal text lines inside the content area, as dicts."""
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            if abs(l['dir'][1]) > 0.1:
                continue
            spans = [s for s in l['spans'] if s['text'].strip() and s['size'] > 6]
            if not spans:
                continue
            x0, y0, x1, y1 = l['bbox']
            base = min(s['origin'][1] for s in spans)          # main baseline (subscripts sit lower)
            if y0 < top - 2 or (y1 > bottom + 2 and base > bottom + 0.5) or x1 < CONTENT_X0 or x0 > CONTENT_X1:
                continue
            out.append({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1,
                        'text': norm(''.join(s['text'] for s in spans)).strip(),
                        'bold': any('Bold' in s['font'] or s['flags'] & 16 for s in spans)})
    out.sort(key=lambda d: (round(d['y0']), d['x0']))
    return out


def ink_boxes(page, top, bottom):
    """Bounding boxes of everything visible in the content area (text + vector drawings + images)."""
    boxes = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in visible_lines(page, top, bottom)]
    for d in page.get_drawings():
        r = d['rect']
        if r.y1 < top - 1 or r.y0 > bottom + 1 or r.x1 < CONTENT_X0 + 1 or r.x0 > CONTENT_X1 - 1:
            continue
        if r.width > 0.95 * page.rect.width and r.height > 0.95 * page.rect.height:
            continue                         # full-page clip/background
        if (r.width < 1.5 or r.height < 1.5) and (r.x0 < 40 or r.x1 > 556) and (r.y0 > bottom - 30 or r.y1 < top + 30):
            continue                         # crop/corner marks
        if d.get('fill') in ((1.0, 1.0, 1.0), (1, 1, 1)) and not d.get('color'):
            continue                         # white masks: invisible on paper
        parts = [r]
        if len(d['items']) > 1 and r.height > 30:      # one path object can hold lines from several questions
            parts = []
            for it in d['items']:
                pts = [x for x in it[1:] if isinstance(x, fitz.Point)]
                if it[0] == 're':
                    parts.append(fitz.Rect(it[1]))
                elif it[0] == 'qu':
                    parts.append(it[1].rect)
                elif pts:
                    xs = [p.x for p in pts]; ys = [p.y for p in pts]
                    parts.append(fitz.Rect(min(xs), min(ys), max(xs), max(ys)))
        for q in parts:
            if q.y1 < top - 1 or q.y0 > bottom + 1:
                continue
            boxes.append(fitz.Rect(max(q.x0, CONTENT_X0), max(q.y0, top), min(q.x1, CONTENT_X1), min(q.y1, bottom)))
    for img in page.get_image_info():
        r = fitz.Rect(img['bbox'])
        if r.y1 > top and r.y0 < bottom:
            boxes.append(r & fitz.Rect(CONTENT_X0, top, CONTENT_X1, bottom))
    return [b for b in boxes if not b.is_empty or b.width > 0 or b.height > 0]


def label_tokens(page, top, bottom):
    """Candidate structural labels on a page: ('q', n) / ('l', 'a') / ('r', 'ii'), with y and x."""
    toks = []
    for x0, y0, x1, y1, w, *_ in page.get_text('words'):
        if y0 < top - 2 or y1 > bottom + 2:
            continue
        if QNUM_X[0] <= x0 <= QNUM_X[1] and re.fullmatch(r'\d{1,2}', w):
            toks.append({'kind': 'q', 'val': int(w), 'x0': x0, 'y0': y0, 'y1': y1})
        m = re.fullmatch(r'[a-z]?\(([a-z]{1,4})\)', w)   # some PDFs carry a stray hidden char: 'i(i)'
        if m:
            v = m.group(1)
            if LETTER_X[0] <= x0 <= LETTER_X[1] and v in LETTERS:
                toks.append({'kind': 'l', 'val': v, 'x0': x0, 'y0': y0, 'y1': y1})
            elif QNUM_X[0] <= x0 <= QNUM_X[1] and v in LETTERS and v not in ROMAN and w.startswith('('):
                # a part label printed in the number column (a page that opens with '(e)' beside a figure);
                # boundaries() only takes it when it is the next letter of the current question
                toks.append({'kind': 'l', 'val': v, 'x0': x0, 'y0': y0, 'y1': y1, 'wide': True})
            elif ROMAN_X[0] <= x0 <= ROMAN_X[1] and v in ROMAN:
                toks.append({'kind': 'r', 'val': v, 'x0': x0, 'y0': y0, 'y1': y1})
    toks.sort(key=lambda t: (round(t['y0']), t['x0']))
    return toks


# --- what is actually printed: the rendered page -------------------------------------------------
ZOOM = 2.0                                 # 144 dpi: 0.5 pt per pixel row
_RASTER = {}


def dark_mask(page):
    """Boolean array (rows x cols) of printed ink at 144 dpi for the content columns, cached per page.
    Invisible geometry (pattern cells, white masks, clip paths) is not ink, by construction."""
    import numpy as np
    key = (page.parent.name, page.number)
    if key not in _RASTER:
        if len(_RASTER) > 64:
            _RASTER.clear()
        pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), colorspace=fitz.csGRAY)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        mask = img < 200
        x0, x1 = int(CONTENT_X0 * ZOOM), int(CONTENT_X1 * ZOOM)
        mask[:, :x0] = False
        mask[:, x1:] = False
        _RASTER[key] = mask
    return _RASTER[key]


def tight_ink(page, r, exclude=()):
    """Smallest rect (pt) around the printed ink inside r, ignoring the rects in `exclude` (text), or None.
    A drawing object's own box can be much bigger than what it prints (clip paths, invisible frames,
    curve control points), so figures are built from what is printed."""
    import numpy as np
    m = dark_mask(page)
    H, W = m.shape
    x0, y0 = max(int(r.x0 * ZOOM) - 1, 0), max(int(r.y0 * ZOOM) - 1, 0)
    x1, y1 = min(int(r.x1 * ZOOM) + 2, W), min(int(r.y1 * ZOOM) + 2, H)
    if x1 <= x0 or y1 <= y0:
        return None
    sub = m[y0:y1, x0:x1].copy()
    for t in exclude:
        tx0, ty0 = int(t.x0 * ZOOM) - x0, int(t.y0 * ZOOM) - y0
        tx1, ty1 = int(t.x1 * ZOOM) + 1 - x0, int(t.y1 * ZOOM) + 1 - y0
        if tx1 > 0 and ty1 > 0:
            sub[max(ty0, 0):max(ty1, 0), max(tx0, 0):max(tx1, 0)] = False
    ys, xs = np.nonzero(sub)
    if len(ys) == 0:
        return None
    return fitz.Rect((x0 + xs.min()) / ZOOM, (y0 + ys.min()) / ZOOM, (x0 + xs.max() + 1) / ZOOM, (y0 + ys.max() + 1) / ZOOM)


def grow_to_ink(page, r, limit, step=1.0, max_grow=80, exclude=()):
    """Grow r while printed ink runs across one of its edges (a line, curve or label that continues
    outside), staying inside `limit`. Fixes crops that end in the middle of a wire or an axis.
    Ink inside `exclude` (the question's sentences) never pulls the crop in."""
    m = dark_mask(page); H, W = m.shape; Z = ZOOM
    if exclude:
        m = m.copy()
        for e in exclude:
            m[max(0, int((e.y0 - 1) * Z)):max(0, int((e.y1 + 1) * Z) + 1), max(0, int((e.x0 - 1) * Z)):max(0, int((e.x1 + 1) * Z) + 1)] = False
    r = fitz.Rect(r)
    def crosses(edge):
        y0, y1 = max(0, int(r.y0 * Z)), min(H, int(r.y1 * Z) + 1)
        x0, x1 = max(0, int(r.x0 * Z)), min(W, int(r.x1 * Z) + 1)
        if edge == 'l':
            a, b = int((r.x0 - 1) * Z), int(r.x0 * Z)
            return 0 <= a < W and (m[y0:y1, a] & m[y0:y1, b]).any()
        if edge == 'r':
            a, b = int((r.x1 + 1) * Z), int(r.x1 * Z)
            return a < W and (m[y0:y1, a] & m[y0:y1, min(b, W - 1)]).any()
        if edge == 't':
            a, b = int((r.y0 - 1) * Z), int(r.y0 * Z)
            return 0 <= a < H and (m[a, x0:x1] & m[b, x0:x1]).any()
        a, b = int((r.y1 + 1) * Z), int(r.y1 * Z)
        return a < H and (m[a, x0:x1] & m[min(b, H - 1), x0:x1]).any()
    grown = 0
    changed = True
    while changed and grown < max_grow:
        changed = False
        if r.x0 - step >= limit.x0 and crosses('l'):
            r.x0 -= step; changed = True
        if r.x1 + step <= limit.x1 and crosses('r'):
            r.x1 += step; changed = True
        if r.y0 - step >= limit.y0 and crosses('t'):
            r.y0 -= step; changed = True
        if r.y1 + step <= limit.y1 and crosses('b'):
            r.y1 += step; changed = True
        grown += step
    return r


def row_ink(page):
    """Dark pixels per pixel row (index = y_pt * ZOOM)."""
    return dark_mask(page).sum(axis=1)


def ink_extent(page, y0, y1):
    """(top, bottom) in pt of printed ink between y0 and y1, or None if the strip is empty."""
    import numpy as np
    rows = row_ink(page)
    a, b = max(0, int(y0 * ZOOM)), min(len(rows), int(y1 * ZOOM) + 1)
    hit = np.nonzero(rows[a:b] > 0)[0]
    if not len(hit):
        return None
    return (a + hit[0]) / ZOOM, (a + hit[-1] + 1) / ZOOM
