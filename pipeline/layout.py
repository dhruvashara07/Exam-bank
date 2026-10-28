"""Page geometry helpers: content area, ink boxes, and label tokens.

All coordinates are PDF points with the origin at the top-left (PyMuPDF convention).
"""
import re
import pymupdf as fitz

CONTENT_X0, CONTENT_X1 = 30.0, 570.0      # outside this: margin strips (corner marks are filtered by shape)
QNUM_X = (44.0, 56.0)                     # question numbers
LETTER_X = (64.0, 80.0)                   # (a) (b) ...
ROMAN_X = (84.0, 104.0)                   # (i) (ii) ...
ROMAN = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
LETTERS = 'abcdefghjklmnop'

# Symbol-font characters that arrive as private-use code points
SYMBOL_MAP = {0xf0ae: '→', 0xf0ac: '←', 0xf0ad: '↑', 0xf0af: '↓', 0xf0b0: '°', 0xf0b1: '±', 0xf0b4: '×',
              0xf0b8: '÷', 0xf0a3: '≤', 0xf0b3: '≥', 0xf0bb: '≈', 0xf0b9: '≠', 0xf0d6: '√', 0xf0b5: '∝',
              0xf0a5: '∞', 0xf02d: '−', 0xf02b: '+', 0xf03d: '=', 0xf061: 'α', 0xf062: 'β', 0xf067: 'γ',
              0xf064: 'δ', 0xf065: 'ε', 0xf071: 'θ', 0xf06c: 'λ', 0xf06d: 'μ', 0xf070: 'π', 0xf072: 'ρ',
              0xf073: 'σ', 0xf077: 'ω', 0xf057: 'Ω', 0xf044: 'Δ', 0xf046: 'Φ', 0xf053: 'Σ', 0xf0d7: '·',
              0xf0a2: '′', 0xf0c5: '⊕', 0xf0de: '⇒', 0xf0db: '⇔'}


def norm(text):
    return ''.join(SYMBOL_MAP.get(ord(c), c) for c in text)


def page_bounds(page):
    """Return (top, bottom) of the question content area on a page."""
    top, bottom = 50.0, page.rect.height - 40
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            t = ''.join(s['text'] for s in l['spans']).strip()
            y0, y1 = l['bbox'][1], l['bbox'][3]
            if y0 > 700 and ('©' in t or 'UCLES' in t or 'Turn over' in t or re.search(r'\d{4}/\d\d/[A-Z]/[A-Z]/\d\d', t)):
                bottom = min(bottom, y0 + 1.0)
            if y1 < 56 and re.fullmatch(r'\d{1,2}', t):          # page number
                top = max(top, y1 + 4)
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
            if y0 < top - 2 or y1 > bottom + 2 or x1 < CONTENT_X0 or x0 > CONTENT_X1:
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
            elif ROMAN_X[0] <= x0 <= ROMAN_X[1] and v in ROMAN:
                toks.append({'kind': 'r', 'val': v, 'x0': x0, 'y0': y0, 'y1': y1})
    toks.sort(key=lambda t: (round(t['y0']), t['x0']))
    return toks
