"""Tables and multiple-choice options for the question store.

A ruled table (a "figure" crop that is only a grid of straight rules with text in the cells) is stored as
layout text + lines, never as a picture.  A multiple-choice question gets an `options` list (A-D):
  - options in a table:   each row starting with A/B/C/D -> {label, cells[...], text}; the header -> `option_columns`
  - options as diagrams:  four separate drawings, each with its letter -> one figure file per option
  - options as text lines: "A  2.0 N" -> {label, text}
A diagram whose letters A-D mark points on ONE drawing (pins on a rod, levels in a tube) stays one figure.
"""
import collections, re
import pymupdf as fitz

LETTERS = ('A', 'B', 'C', 'D')
TICKS = {'\x16': '✓', '\x1a': '✗', '3': '✓', '4': '✓', '7': '✗', '8': '✗'}   # MonotypeSorts / ZapfDingbats
_WORDS = {}


def words(page):
    """Words as (x0, y0, x1, y1, text) with symbol-font codes turned into real characters (α, ✓, ✗)."""
    key = (page.parent.name, id(page.parent), page.number, page.rotation)
    if key in _WORDS:
        return _WORDS[key]
    from store_text import unpua
    out = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                ding = any(k in sp['font'].lower() for k in ('sorts', 'dingbat', 'wingding'))
                bold = bool(sp['flags'] & 16) or 'bold' in sp['font'].lower()
                cur = []
                for c in sp['chars'] + [None]:
                    if c is None or (not ding and not c['c'].strip()):
                        if cur:
                            r = fitz.Rect(cur[0]['bbox']) | fitz.Rect(cur[-1]['bbox'])
                            t = ''.join(TICKS.get(x['c'], '?') if ding else unpua(x['c']) for x in cur)
                            out.append((r.x0, r.y0, r.x1, r.y1, t, bold))
                        cur = []
                    elif ding:
                        if c['c'].strip() or ord(c['c']) < 32:
                            r = fitz.Rect(c['bbox'])
                            out.append((r.x0, r.y0, r.x1, r.y1, TICKS.get(c['c'], '?'), False))
                    else:
                        cur.append(c)
    _WORDS[key] = out
    return out


def labels(page, box, reach=30):
    """Option letters A-D near box: a lone capital with nothing printed right after it on its line
    (the stem's 'A student ...' has a word 3 pt later)."""
    ws = words(page)
    area = box + (-reach, -reach, reach, reach)
    out = {}
    for w in ws:
        if w[4] not in LETTERS or not area.contains(fitz.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)):
            continue
        nxt = [v for v in ws if v is not w and abs((v[1] + v[3]) / 2 - (w[1] + w[3]) / 2) < 2 and 0 <= v[0] - w[2] < 6]
        if nxt:
            continue
        out.setdefault(w[4], []).append((fitz.Rect(w[:4]), w[5]))
    if any(len(v) > 1 for v in out.values()):        # 'A' in an ammeter symbol too: keep the bold letters
        bold = {k: [r for r, b in v if b] for k, v in out.items()}
        if sorted(bold) == list(LETTERS) and all(len(v) == 1 for v in bold.values()):
            return bold
    return {k: [r for r, b in v] for k, v in out.items()}


def _segments(page, box, detail=False):
    """Straight axis-aligned rule segments inside box, and whether anything else (curves, slanted lines,
    filled shapes that are not thin rules) is drawn there. detail=True: the third value is a dict
    {'curve': n, 'slant': n, 'shade': n} instead of their sum."""
    hs, vs, other = [], [], 0
    cnt = {'curve': 0, 'slant': 0, 'shade': 0}
    for dr in page.get_drawings():
        r = dr['rect']
        if not (box + (-1, -1, 1, 1)).contains(fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)):
            continue
        if (dr.get('fill_opacity') or 1) < 0.3 and dr['type'] == 'f':
            continue
        for it in dr['items']:
            k = it[0]
            if k == 'l':
                a, b = it[1], it[2]
                if abs(a.y - b.y) < .3:
                    hs.append((min(a.x, b.x), max(a.x, b.x), a.y))
                elif abs(a.x - b.x) < .3:
                    vs.append((min(a.y, b.y), max(a.y, b.y), a.x))
                else:
                    other += 1; cnt['slant'] += 1
            elif k == 're':
                q = it[1]
                if q.height < 1.6:                       # thin filled rect = horizontal rule
                    hs.append((q.x0, q.x1, (q.y0 + q.y1) / 2))
                elif q.width < 1.6:
                    vs.append((q.y0, q.y1, (q.x0 + q.x1) / 2))
                elif dr.get('fill') is not None and dr.get('fill') not in ((1, 1, 1), [1, 1, 1]):
                    other += 1; cnt['shade'] += 1        # a shaded block: part of a drawing (or a shaded header cell)
                else:
                    hs += [(q.x0, q.x1, q.y0), (q.x0, q.x1, q.y1)]
                    vs += [(q.y0, q.y1, q.x0), (q.y0, q.y1, q.x1)]
            elif k == 'qu':
                q = it[1].rect
                hs += [(q.x0, q.x1, q.y0), (q.x0, q.x1, q.y1)]
                vs += [(q.y0, q.y1, q.x0), (q.y0, q.y1, q.x1)]
            else:
                other += 1; cnt['curve'] += 1
    return (hs, vs, cnt) if detail else (hs, vs, other)


def _merge(lines, tol=.8):
    """Join collinear touching pieces (tables are often drawn cell by cell)."""
    out = []
    for a0, a1, c in sorted(lines, key=lambda t: (round(t[2], 0), t[0])):
        if out and abs(out[-1][2] - c) < tol and a0 <= out[-1][1] + 1.5:
            p = out[-1]
            out[-1] = (p[0], max(p[1], a1), p[2])
        else:
            out.append((a0, a1, c))
    return out


def has_picture(page, box):
    return any(fitz.Rect(i['bbox']).intersects(box) and fitz.Rect(i['bbox']).width > 8 and fitz.Rect(i['bbox']).height > 8
               for i in page.get_image_info())


def grid(page, box, table=False):
    """The table grid inside box, or None: {'rows': [y...], 'cols': [x...], 'rect': Rect}.
    table=True (the crop is captioned 'Table n.n'): shaded cells and up to 3 slanted lines/curves (a split corner
    cell) are fine - the layout draws them; an embedded picture or a real drawing (more curves) makes it a figure."""
    hs, vs, other = _segments(page, box, detail=True)
    if table:
        if has_picture(page, box) or other['curve'] + other['slant'] > 3:
            return None
    elif sum(other.values()):
        return None
    hs, vs = _merge(hs), _merge(vs)
    if not hs or not vs:
        return None
    x0, x1 = min(h[0] for h in hs), max(h[1] for h in hs)
    y0, y1 = min(v[0] for v in vs), max(v[1] for v in vs)
    W, H = x1 - x0, y1 - y0
    if W < 40 or H < 20:
        return None
    full_h = sorted({round(h[2], 1) for h in hs if h[1] - h[0] >= 0.85 * W})
    full_v = sorted({round(v[2], 1) for v in vs if v[1] - v[0] >= 0.5 * H})
    rows = sorted({round(h[2], 1) for h in hs})
    if len(full_h) < 2 or len(full_v) < 2 or len(rows) > 30:   # 30+ rules = graph paper, not a table
        return None
    # a table is closed top and bottom; its top rule may start at the second column (an open top-left header cell)
    top_ok = abs(full_h[0] - y0) <= 2 or any(abs(h[2] - y0) <= 2 and h[1] - h[0] >= 0.4 * W for h in hs)
    if not top_ok or abs(full_h[-1] - y1) > 2:
        return None
    words_ = [w for w in words(page) if fitz.Rect(w[:4]).intersects(box)]
    inside = [w for w in words_ if x0 - 1 <= (w[0] + w[2]) / 2 <= x1 + 1 and y0 - 1 <= (w[1] + w[3]) / 2 <= y1 + 1]
    if len(inside) < 3:
        return None
    # text that is in the crop but outside the grid (a caption is fine, a labelled drawing is not)
    stray = [w for w in words_ if w not in inside and not re.match(r'(Fig|Table)', w[4])]
    if len(stray) > 6:
        return None
    cols = sorted({round(v[2], 1) for v in vs})
    return {'rows': rows, 'cols': cols, 'rect': fitz.Rect(x0, y0, x1, y1)}


def table_rows(page, g):
    """Cell texts row by row (rows between consecutive horizontal rules; cells between vertical rules)."""
    ws_ = words(page)
    ys, xs = g['rows'], g['cols']
    out = []
    for ya, yb in zip(ys, ys[1:]):
        if yb - ya < 4:
            continue
        cells = []
        for xa, xb in zip(xs, xs[1:]):
            ws = [w for w in ws_ if xa <= (w[0] + w[2]) / 2 <= xb and ya <= (w[1] + w[3]) / 2 <= yb]
            ws.sort(key=lambda w: (round(w[1] / 3), w[0]))
            cells.append(' '.join(w[4] for w in ws))
        # a row without its own rule (text lines inside one ruled row): split by text lines
        out.append(cells)
    # rows that hold several text lines A,B,C,D (rules only around the block): split them by line
    split = []
    for cells in out:
        if len(cells) and re.fullmatch(r'(?:[ABCD] ){1,3}[ABCD]', cells[0]):
            lines = _row_lines(page, g, cells)
            split += lines or [cells]
        else:
            split.append(cells)
    return split


def _row_lines(page, g, cells):
    ws_ = words(page)
    letters = [w for w in ws_ if w[4] in LETTERS and g['cols'][0] <= (w[0] + w[2]) / 2 <= g['cols'][1]
               and g['rect'].y0 <= w[1] <= g['rect'].y1]
    if len(letters) < 2:
        return None
    letters.sort(key=lambda w: w[1])
    out = []
    for i, l in enumerate(letters):
        ya = (letters[i - 1][3] + l[1]) / 2 if i else l[1] - 3
        yb = (l[3] + letters[i + 1][1]) / 2 if i + 1 < len(letters) else l[3] + 3
        row = []
        for xa, xb in zip(g['cols'], g['cols'][1:]):
            ws = sorted([w for w in ws_ if xa <= (w[0] + w[2]) / 2 <= xb and ya <= (w[1] + w[3]) / 2 <= yb], key=lambda w: w[0])
            row.append(' '.join(w[4] for w in ws))
        out.append(row)
    return out


def table_options(rows):
    """MCQ options from table rows: rows whose first cell is A-D. Returns (columns, options) or None."""
    opts = [r for r in rows if r and r[0] in LETTERS]
    if [r[0] for r in opts] != list(LETTERS):
        return None
    head = [r for r in rows if r and r[0] not in LETTERS]
    columns = head[0][1:] if head else []
    return columns, [{'label': r[0], 'cells': r[1:], 'text': ' | '.join(c for c in r[1:])} for r in opts]


def _components(page, box, gap=4.0):
    rects = []
    for dr in page.get_drawings():
        r = dr['rect']
        if dr['type'] == 'f' and dr.get('fill') in ((1, 1, 1), [1, 1, 1], (1.0, 1.0, 1.0)):
            continue                                  # white background box
        if r.width > .8 * box.width and r.height > .5 * box.height:
            continue                                  # a frame around everything
        # one PDF path often holds the lines of several drawings: use its pieces
        for it in dr['items']:
            pts = [p for p in it[1:] if isinstance(p, fitz.Point)]
            if it[0] == 're':
                ir = fitz.Rect(it[1])
            elif it[0] == 'qu':
                ir = it[1].rect
            elif pts:
                ir = fitz.Rect(min(p.x for p in pts), min(p.y for p in pts), max(p.x for p in pts), max(p.y for p in pts))
            else:
                continue
            if box.contains(fitz.Point((ir.x0 + ir.x1) / 2, (ir.y0 + ir.y1) / 2)):
                rects.append(ir)
    for b in page.get_image_info():
        r = fitz.Rect(b['bbox'])
        if box.contains(fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)):
            rects.append(r)
    comps = []
    for r in rects:
        g = r + (-gap, -gap, gap, gap)
        hit = [c for c in comps if c.intersects(g)]
        for c in hit:
            comps.remove(c)
            r = r | c
        comps.append(r)
    changed = True
    while changed:
        changed = False
        for i in range(len(comps)):
            for j in range(i + 1, len(comps)):
                if comps[i].intersects(comps[j] + (-gap, -gap, gap, gap)):
                    comps[i] = comps[i] | comps[j]; del comps[j]; changed = True; break
            if changed:
                break
    return comps


def _pieces(page, box, touching=False):
    """Rects of every drawn piece (line, curve, box, picture) whose centre is in box; a PDF path often holds
    the lines of several drawings, so paths are split into their pieces."""
    rects = []
    for dr in page.get_drawings():
        r = dr['rect']
        if dr['type'] == 'f' and dr.get('fill') in ((1, 1, 1), [1, 1, 1], (1.0, 1.0, 1.0)):
            continue                                  # white background box
        if r.width > .8 * box.width and r.height > .5 * box.height and len(dr['items']) <= 4:
            continue                                  # a frame around everything (one rectangle), not a path holding many lines
        for it in dr['items']:
            pts = [p for p in it[1:] if isinstance(p, fitz.Point)]
            if it[0] == 're':
                ir = fitz.Rect(it[1])
            elif it[0] == 'qu':
                ir = it[1].rect
            elif pts:
                ir = fitz.Rect(min(p.x for p in pts), min(p.y for p in pts), max(p.x for p in pts), max(p.y for p in pts))
            else:
                continue
            hw = max(0.4, (dr.get('width') or 0.5) / 2)       # a straight line has no area: give it its stroke width
            ir = ir + (-hw, -hw, hw, hw)
            if (box.intersects(ir) if touching else box.contains(fitz.Point((ir.x0 + ir.x1) / 2, (ir.y0 + ir.y1) / 2))):
                rects.append(ir)
    for b in page.get_image_info():
        r = fitz.Rect(b['bbox'])
        if box.contains(fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)) and r.width < .8 * box.width:
            rects.append(r)
    return rects


def diagram_options(page, box, with_labels=False):
    """with_labels=True -> (regions without the printed letters, {letter: Rect of the letter}).
    Four option drawings A-D side by side / in a grid -> {letter: Rect}, or None (one drawing).
    The crop is cut into the grid the letters are printed in; every drawn piece and word goes to the
    option whose cell holds its centre."""
    lab = labels(page, box)
    if sorted(lab) != list(LETTERS) or any(len(v) != 1 for v in lab.values()):
        return None
    lab = {k: v[0] for k, v in lab.items()}
    if not any(box.contains(r) for r in lab.values()) and not _one_row_or_col(lab):
        return None
    for r in lab.values():
        box = box | r
    cell = _cells(lab, box, page)
    if cell is None:
        return None
    regions = {k: fitz.Rect(lab[k]) for k in LETTERS}
    ink = {k: fitz.Rect() for k in LETTERS}           # the drawing alone (no letter): what the option figure shows
    filled = {k: 0 for k in LETTERS}
    items = []                                        # (option, rect) of every piece / phrase: for the clean-cut test
    safe = {}
    for k in LETTERS:                                 # a drawing touching the border it shares with another option = no clean cut
        R = fitz.Rect(cell.rect[k]); d = [-2.0, -2.0, 2.0, 2.0]
        for o in LETTERS:
            if o == k:
                continue
            O = cell.rect[o]
            ov_y = min(R.y1, O.y1) - max(R.y0, O.y0) > 1; ov_x = min(R.x1, O.x1) - max(R.x0, O.x0) > 1
            if ov_y and abs(O.x0 - R.x1) < 3: d[2] = -2.0
            if ov_y and abs(O.x1 - R.x0) < 3: d[0] = 2.0
            if ov_x and abs(O.y0 - R.y1) < 3: d[3] = -2.0
            if ov_x and abs(O.y1 - R.y0) < 3: d[1] = 2.0
        safe[k] = R + d
    def inside(r, k):
        return safe[k].contains(r)
    for r in _pieces(page, box):
        k = cell(fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
        if k:
            if not inside(r, k):
                return None                           # a drawing crosses into the next option: no clean cut (Dhruv 2026-11-05)
            regions[k] |= r; ink[k] |= r; filled[k] += 1; items.append((k, fitz.Rect(r)))
    ws = [w for w in words(page) if not (w[4] in LETTERS and any(fitz.Rect(w[:4]) == lab[k] for k in LETTERS))]
    phrase = {}                                   # "1.0 cm": a unit goes with its number (same line, small gap)
    for w in sorted(ws, key=lambda w: (round((w[1] + w[3]) / 2), w[0])):
        prev = [p for p in phrase if abs((p[1] + p[3]) / 2 - (w[1] + w[3]) / 2) < 2 and 0 <= w[0] - p[2] < 4]
        phrase[w] = phrase[prev[-1]] if prev else w
    members = {}
    for w in ws:
        members.setdefault(phrase[w], []).append(w)
    for head, mw in members.items():
        h = fitz.Rect(mw[0][:4])
        for w in mw[1:]:
            h |= fitz.Rect(w[:4])
        if mw[-1][4].endswith('?') or (len(mw) >= 5 and not any(safe[k].contains(h) for k in LETTERS)):
            continue                                  # a sentence of the question (not an option label)
        c = fitz.Point((h.x0 + h.x1) / 2, (h.y0 + h.y1) / 2)
        if not (box + (0, -12, 0, 12)).contains(c):
            continue
        k = cell(c)
        if k:
            if not inside(h, k):
                return None                           # a label crosses into the next option: keep one whole figure
            regions[k] |= h; ink[k] |= h; filled[k] += 1; items.append((k, h))
    def big_gap(rs, axis, limit=30.0):
        iv = sorted((r.x0, r.x1) if axis == 0 else (r.y0, r.y1) for r in rs)
        end = iv[0][1] if iv else 0
        for a, b in iv[1:]:
            if a - end > limit:
                return True
            end = max(end, b)
        return False
    for k in LETTERS:                                 # a piece far away from the rest of its option: the cell split is wrong
        rs = [r for o, r in items if o == k]
        if big_gap(rs, 0) or big_gap(rs, 1):
            return None
    for k in LETTERS:                                 # nothing of another option may show inside this option's crop
        R = ink[k] + (-1.5, -1.5, 1.5, 1.5)
        if any(o != k and (R & r).get_area() > 0 for o, r in items):
            return None
    if any(v == 0 for v in filled.values()):
        return None
    regions = {k: r + (-1.5, -1.5, 1.5, 1.5) for k, r in regions.items()}
    ks = list(LETTERS)
    for i in range(4):
        for j in range(i + 1, 4):
            if (regions[ks[i]] & regions[ks[j]]).get_area() > 0.15 * min(regions[ks[i]].get_area(), regions[ks[j]].get_area()):
                return None                   # the drawings interlock: one figure with labels on it
    areas = sorted(r.get_area() for r in regions.values())
    if areas[0] < 0.2 * areas[-1]:             # four options are drawings of about the same size
        return None
    crops = {k: (ink[k] + (-1.5, -1.5, 1.5, 1.5)) if not ink[k].is_empty else regions[k] for k in LETTERS}
    # final test: every drawn piece and label near the options is shown WHOLE in exactly one option picture
    # (nothing cut at a crop edge, nothing lost between pictures, nothing shown twice)
    others = [fitz.Rect(w[:4]) for w in ws if not any((fitz.Rect(w[:4]) & lab[k]).get_area() > 0 for k in LETTERS)]
    def _ph(mw):
        h = fitz.Rect(mw[0][:4])
        for w in mw[1:]:
            h |= fitz.Rect(w[:4])
        return h
    sentence = [fitz.Rect(w[:4]) for head, mw in members.items()
                if mw[-1][4].endswith('?') or (len(mw) >= 5 and not any(safe[k].contains(_ph(mw)) for k in LETTERS)) for w in mw]
    for r in _pieces(page, box, touching=True) + [o for o in others if box.intersects(o) and o not in sentence]:
        hit = [k for k in LETTERS if crops[k].intersects(r)]
        full = [k for k in hit if (crops[k] + (-1, -1, 1, 1)).contains(r)]
        if len(hit) > 1 or (hit and not full) or (not hit and (box + (-1, -1, 1, 1)).contains(r) and r.get_area() < 0.3 * box.get_area()):
            return None
    if with_labels:
        return crops, lab
    return regions


def _one_row_or_col(lab):
    ys = [r.y0 for r in lab.values()]
    xs = [r.x0 for r in lab.values()]
    return max(ys) - min(ys) < 3 or max(xs) - min(xs) < 3


def _cluster(vals, tol=12):
    out = []
    for v in sorted(vals):
        if out and v - out[-1][-1] < tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(c) / len(c) for c in out]


def _free_cut(lo, hi, spans, mid):
    """A coordinate between lo and hi that no span covers, as near to mid as possible (None if none)."""
    cov = sorted((max(a, lo), min(b, hi)) for a, b in spans if b > lo and a < hi)
    free, cur = [], lo
    for a, b in cov:
        if a > cur:
            free.append((cur, a))
        cur = max(cur, b)
    if cur < hi:
        free.append((cur, hi))
    free = [f for f in free if f[1] - f[0] >= 1.5]
    if not free:
        return None
    a, b = max(free, key=lambda f: (f[1] - f[0]) - 0.05 * abs((f[0] + f[1]) / 2 - mid))   # the widest white column (2026-11-05)
    return (a + b) / 2


def _cells(lab, box, page=None):
    """Which option a point belongs to: the page area is cut into the grid the letters are printed in.
    Columns split half-way between letter columns; rows split at the letter row when the letters sit
    above their drawings, just below the previous letter row when they sit underneath, else half-way."""
    cx = {k: (r.x0 + r.x1) / 2 for k, r in lab.items()}
    cy = {k: (r.y0 + r.y1) / 2 for k, r in lab.items()}
    xs, ys = _cluster(cx.values()), _cluster(cy.values())
    if len(xs) * len(ys) < 4 or len(xs) * len(ys) > 4 and not (len(xs) == 4 or len(ys) == 4):
        return None
    col = lambda x: min(range(len(xs)), key=lambda i: abs(xs[i] - x))
    row = lambda y: min(range(len(ys)), key=lambda i: abs(ys[i] - y))
    grid_ = {(row(cy[k]), col(cx[k])): k for k in LETTERS}
    if len(grid_) != 4:
        return None
    xb = [(a + b) / 2 for a, b in zip(xs, xs[1:])]
    if page is not None and len(xs) > 1:          # cut through white space between the drawings
        ink = _pieces(page, box) + [fitz.Rect(w[:4]) for w in words(page) if box.contains(fitz.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))
                                    and not any(fitz.Rect(w[:4]) == r for r in lab.values())]
        for i, (a, b) in enumerate(zip(xs, xs[1:])):
            c = _free_cut(a, b, [(r.x0, r.x1) for r in ink], (a + b) / 2)
            if c is not None:
                xb[i] = c
    if len(ys) == 1:
        yb = []
    elif len(xs) == 1:
        yb = [(a + b) / 2 for a, b in zip(ys, ys[1:])]
    else:
        top = ys[0] - box.y0 < 0.25 * (ys[1] - ys[0])        # first letter row at the top of the crop
        yb = [y - 6 for y in ys[1:]] if top else [y + 6 for y in ys[:-1]]
    def cell(p):
        c = sum(p.x > x for x in xb)
        r = sum(p.y > y for y in yb)
        return grid_.get((r, c))
    xe, ye = [box.x0 - 50] + xb + [box.x1 + 50], [box.y0 - 50] + yb + [box.y1 + 50]
    cell.rect = {k: fitz.Rect(xe[c], ye[r], xe[c + 1], ye[r + 1]) for (r, c), k in grid_.items()}
    return cell


SUP = str.maketrans('0123456789+-−n', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻ⁿ')
SUB = str.maketrans('0123456789+-−', '₀₁₂₃₄₅₆₇₈₉₊₋₋')


def _join(part, lab):
    """Words of one option as plain text: one line read left to right, small raised / lowered digits as
    superscript / subscript (1.5 × 10⁴ C); a fraction (lines above and below) read top to bottom."""
    s = lab['s']
    if all(abs(x['y'] - lab['y']) < 0.6 * s for x in part):
        out = ''
        for x in sorted(part, key=lambda x: x['x']):
            t = x['t']
            if x['s'] < 0.85 * s and x['y'] < lab['y'] - 1 and all(c in '0123456789+-−n' for c in t):
                out += t.translate(SUP); continue
            if x['s'] < 0.85 * s and x['y'] > lab['y'] + 1 and all(c in '0123456789+-−' for c in t):
                out += t.translate(SUB); continue
            out += (' ' if out else '') + t
        return out
    return ' '.join(x['t'] for x in sorted(part, key=lambda x: (round(x['y'] / 3), x['x'])))


def text_options(units):
    """Options printed as text: a lone A, B, C, D (the stem's "A student ..." has its next word 3 pt
    after the letter), then the option. An option's text is everything between its letter and the next
    letter: the rest of the line, or the lines of a fraction printed above and below it."""
    out = []
    for i, u in enumerate(units):
        ws = u['text']
        def lone(w):
            return not any(v is not w and abs(v['y'] - w['y']) < 2 and 0 <= v['x'] - (w['x'] + w['w']) < 6 for v in ws)
        lab = [w for w in ws if w['t'] in LETTERS and w.get('role') is None and lone(w)]
        by = {}
        for w in lab:
            by.setdefault(w['t'], []).append(w)
        if sorted(by) != list(LETTERS):
            continue
        if any(len(v) > 1 for v in by.values()):        # 'C' for coulomb, 'A' in the stem: pick the 4 letters
            import itertools                             # laid out as options are: a row, a column or a 2x2 grid,
            best = None                                  # in reading order, evenly spaced
            for combo in itertools.product(*(by[L] for L in LETTERS)):
                ys = _cluster([w['y'] for w in combo], 2)
                xs = _cluster([w['x'] for w in combo], 2)
                if len(ys) * len(xs) != 4 and not (len(ys) == 1 or len(xs) == 1):
                    continue
                order = sorted(combo, key=lambda w: (round(w['y']), w['x']))
                if [w['t'] for w in order] != list(LETTERS):
                    continue
                if len(ys) == 1:
                    gaps = [b['x'] - a['x'] for a, b in zip(combo, combo[1:])]
                elif len(xs) == 1:
                    gaps = [b['y'] - a['y'] for a, b in zip(combo, combo[1:])]
                else:
                    gaps = [0]
                score = max(gaps) - min(gaps)
                if best is None or score < best[0]:
                    best = (score, combo)
            if best is None:
                continue
            by = {w['t']: [w] for w in best[1]}
        seq = [by[L][0] for L in LETTERS]
        size = max(w['s'] for w in seq)
        for n, w in enumerate(seq):
            nxt = seq[n + 1] if n + 1 < 4 else None
            prv = seq[n - 1] if n else None
            same_row = nxt is not None and abs(nxt['y'] - w['y']) < 2
            x1 = nxt['x'] if same_row else 1e9
            top = w['y'] - 1.6 * size if not (prv and abs(prv['y'] - w['y']) < 2) else w['y'] - 1.6 * size
            bot = (nxt['y'] - 1.0 * size) if (nxt and not same_row) else w['y'] + 0.9 * size
            if prv and not (abs(prv['y'] - w['y']) < 2):
                top = max(top, prv['y'] + 0.4 * size)
            part = [x for x in ws if x is not w and x['x'] > w['x'] + w['w'] - .5 and x['x'] < x1
                    and top < x['y'] <= bot and x.get('role') is None]
            out.append({'label': w['t'], 'text': _join(part, w)})
        break
    if len(out) == 4 and all(o['text'] for o in out):
        return out
    return None


def table_inside(page, box):
    """A ruled table printed inside a figure crop together with a drawing (wave diagram above, options table
    below). Returns (table grid, the crop without the table) or None."""
    lab = labels(page, box, reach=0)
    if sorted(lab) != list(LETTERS) or any(len(v) != 1 for v in lab.values()):
        return None
    lab = {k: v[0] for k, v in lab.items()}
    if max(r.x0 for r in lab.values()) - min(r.x0 for r in lab.values()) > 3:
        return None                                   # option letters of a table are one column
    top, bot = min(r.y0 for r in lab.values()), max(r.y1 for r in lab.values())
    hs, vs, _ = _segments(page, box)
    hs = _merge(hs)
    near = [h for h in hs if top - 45 <= h[2] <= bot + 8 and h[1] - h[0] > 0.3 * box.width]
    if len(near) < 2:
        return None
    t = fitz.Rect(min(h[0] for h in near), min(h[2] for h in near), max(h[1] for h in near), max(h[2] for h in near))
    g = grid(page, t + (-1, -1, 1, 1))
    if not g:
        return None
    rest = fitz.Rect(box.x0, box.y0, box.x1, t.y0 - 2) if t.y0 - box.y0 > box.y1 - t.y1 else fitz.Rect(box.x0, t.y1 + 2, box.x1, box.y1)
    ink = [r for r in _pieces(page, rest)]
    if not ink:
        return None
    d = fitz.Rect(ink[0])
    for r in ink[1:]:
        d |= r
    for w in words(page):                      # labels of the drawing, not the question's sentence under it
        wr = fitz.Rect(w[:4])
        if rest.contains(fitz.Point((wr.x0 + wr.x1) / 2, (wr.y0 + wr.y1) / 2)) and wr.intersects(d + (-12, -12, 12, 12)):
            d |= wr
    return g, (d + (-2, -2, 2, 2)) & rest


def table_picture_reason(page, box):
    """Why a captioned table has to stay a picture (listed in the review), or None when it can be text."""
    hs, vs, o = _segments(page, box, detail=True)
    bits = []
    if has_picture(page, box):
        bits.append('a cell holds an embedded picture')
    if o['curve'] + o['slant'] > 3:
        bits.append(f"{o['curve'] + o['slant']} curves/slanted lines (a drawing or graph in the table)")
    return '; '.join(bits) or None


def text_table(page, box, cap):
    """A captioned table without a closed grid of rules (borderless / open table): words in columns, maybe a few
    rules. Returns 'caption-only' (the crop holds only its caption: no table here), 'text' (store it as layout text)
    or None (it holds a picture / drawing)."""
    if table_picture_reason(page, box):
        return None
    ws = [w for w in words(page) if fitz.Rect(w[:4]).intersects(box)]
    own = [w for w in ws if cap is not None and fitz.Rect(w[:4]).intersects(cap + (-.5, -.5, .5, .5))]
    rest = [w for w in ws if w not in own]
    hs, vs, _ = _segments(page, box)
    if len(rest) < 2 and not hs and not vs:
        return 'caption-only'
    return 'text' if len(rest) >= 2 else None
