"""Maths mark-scheme rows in OUR table: Q | Answer | Marks | Partial Marks (MS_TABLE_RULES 24, Dhruv M0).

Why not the physics re-wrap: maths rows are full of fractions, column vectors and brackets; the physics re-wrap sends
such rows to a fallback. Here every printed cell is laid out on its own:
- the cell's content is split into printed LINES by vertical overlap (a fraction's numerator, bar and denominator,
  a tall bracket and its stacked numbers overlap their line, so they are part of it);
- a line is split into CHUNKS at real word gaps; a chunk (a word, a whole fraction, a bracketed vector) never breaks;
- chunks keep their printed size and spacing; a line wider than our column wraps at a chunk gap onto a new line;
- the row grows to hold its tallest cell (Dhruv: "if a fraction changes the height, adjust to the content").
Q shows the row's full label; Marks are right-aligned; Answer and Partial Marks have the same width.
Columns come from the printed column rules of the row (3 inner rules = 4 columns, 2 = 3 columns).
"""
import re

W = 523.0
QW, MW = 44.0, 44.0
PAD = 5.0
GAP = 1.9                     # a gap wider than this between ink pieces is a word space (a place to wrap)
NUM = re.compile(r'-?\d+(?:\.\d+)?')


def _bbox(d):
    v = [float(x) for x in NUM.findall(d)]
    if len(v) < 2:
        return None
    toks = re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d)
    xs, ys, cmd, i, cx, cy = [], [], None, 0, 0.0, 0.0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t.upper(); i += 1; continue
        if cmd == 'H':
            cx = float(t); i += 1
        elif cmd == 'V':
            cy = float(t); i += 1
        elif cmd == 'C':
            if i + 5 >= len(toks): break
            xs += [float(toks[i]), float(toks[i + 2])]; ys += [float(toks[i + 1]), float(toks[i + 3])]
            cx, cy = float(toks[i + 4]), float(toks[i + 5]); i += 6
        else:
            if i + 1 >= len(toks): break
            cx, cy = float(t), float(toks[i + 1]); i += 2
        xs.append(cx); ys.append(cy)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _shift(d, dx, dy):
    out = []
    for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
        n = [float(x) for x in NUM.findall(args)]
        c = cmd.upper()
        if c in 'MLCSQT':
            n = [a + (dx if k % 2 == 0 else dy) for k, a in enumerate(n)]
        elif c == 'H':
            n = [a + dx for a in n]
        elif c == 'V':
            n = [a + dy for a in n]
        out.append(cmd + ' '.join(f'{a:.2f}' for a in n))
    return ''.join(out)


def columns(u):
    """x of the printed inner column rules of a row unit (2 or 3 of them), or None."""
    vs = []
    for l in u.get('lines', []):
        for sub in re.findall(r'M[^M]+', l['d']):
            b = _bbox(sub)
            if b and b[2] - b[0] < 1.3 and b[3] - b[1] > 1.0:
                vs.append(b)
    xs = []
    for b in sorted(vs, key=lambda b: b[0]):
        x = (b[0] + b[2]) / 2
        if xs and abs(xs[-1][0] - x) < 1.6:
            xs[-1][1] += b[3] - b[1]
        else:
            xs.append([x, b[3] - b[1]])
    inner = [x for x, c in xs if c > 0.6 * u['h'] and 20 < x < u['w'] - 20]
    return inner if len(inner) in (2, 3) else None


class _Item:
    __slots__ = ('kind', 'ref', 'x0', 'x1', 'y0', 'y1')

    def __init__(self, kind, ref, x0, y0, x1, y1):
        self.kind, self.ref, self.x0, self.y0, self.x1, self.y1 = kind, ref, x0, y0, x1, y1


def _items(u, edges):
    """Every piece of ink of the row with its box, minus the table's own rules."""
    its = []
    seen_t = []
    for t in u.get('text', []):
        if not t.get('t', '').strip():
            continue
        if any(o['t'] == t['t'] and abs(o['x'] - t['x']) < 1.2 and abs(o['y'] - t['y']) < 1.2 for o in seen_t):
            continue                                    # text printed twice (2014 MJ 62 p4)
        seen_t.append(t)
        s = t.get('s', 11)
        its.append(_Item('t', t, t['x'], t['y'] - 0.78 * s, t['x'] + t['w'], t['y'] + 0.22 * s))
    for k in ('glyphs', 'images'):
        for g in u.get(k) or []:
            its.append(_Item(k, g, g['x'], g['y'], g['x'] + g['w'], g['y'] + g['h']))
    for f in u.get('figs') or []:
        its.append(_Item('figs', f, f['x'], f['y'], f['x'] + f.get('w', 0), f['y'] + f.get('h', 0)))
    shaded = any(l.get('fill', '').lower() not in ('', '#ffffff', '#000000', '#231f20') for l in u.get('lines', []))
    for l in u.get('lines', []):
        if l.get('fill', '').lower() == '#ffffff' and 'stroke' not in l and not shaded:
            continue                                    # (a white box over grey 'un-shades' a cell: kept, round 28 2019 ON 51 q1)
        b = _bbox(l['d'])
        if not b:
            continue
        if b[2] - b[0] < 1.3 and (b[3] - b[1] > 0.5 * u['h'] or any(abs((b[0] + b[2]) / 2 - e) < 2.5 for e in edges + [0.5, u['w'] - 0.5])
                                  or (b[0] + b[2]) / 2 < 20 or (b[0] + b[2]) / 2 > u['w'] - 20):
            continue                                    # a column rule / border (or a piece of one)
        if b[3] - b[1] < 1.3 and b[2] - b[0] > 30 and any(b[0] - 3 <= e <= b[0] + 3 or b[2] - 3 <= e <= b[2] + 3 for e in edges + [0, u['w']]):
            continue                                    # a row / sub-row rule running between column rules
        if b[3] - b[1] < 1.3 and b[2] - b[0] > 0.8 * u['w']:
            continue
        if b[3] - b[1] > 0.9 * u['h'] and b[2] - b[0] > 0.9 * u['w']:
            continue                                    # a background box
        if (b[3] - b[1] < 3.0 and (b[1] < 3.0 or b[3] > u['h'] - 3.0) and b[2] - b[0] > 20) or b[3] <= 3.0 or b[1] >= u['h'] - 3.0:   # the row's own top / bottom rule, or the edge of the header's shading poking in (2019 ON 63 q6, round 28)
            continue                                    # a piece of the row's own top / bottom rule (round 27 stray lines)
        if b[3] - b[1] < 1.3 and b[2] - b[0] > 25 and len(edges) >= 2 and b[0] >= edges[1] - 1 and not any(
                t.get('t', '').strip() and t['x'] < b[2] and t['x'] + t['w'] > b[0] and 0 <= b[1] - t['y'] < 9
                for t in u.get('text', [])):
            continue                                    # a long line with nothing written over it: a cell rule
        its.append(_Item('lines', l, b[0], b[1], b[2], b[3]))
    return its


def _lines_of(items):
    """Printed lines: items whose vertical extents overlap (fractions and brackets join their line). A band holding
    only drawings (a fraction bar, a vector arrow) joins the bands right above and below it (numerator / letters),
    and so does a band of small raised text (powers) - round 27, ERROR_PATTERNS 77."""
    rows = []
    for it in sorted(items, key=lambda i: i.y0):
        h = it.y1 - it.y0
        if rows and it.y0 < rows[-1]['y1'] - min(1.0, 0.3 * h):
            rows[-1]['its'].append(it); rows[-1]['y1'] = max(rows[-1]['y1'], it.y1)
        else:
            rows.append({'its': [it], 'y0': it.y0, 'y1': it.y1})
    def drawn(b):
        return all(i.kind == 'lines' for i in b['its'])
    base = max([i.ref.get('s', 11) for i in items if i.kind == 't'] or [11])
    def small(b):
        ts = [i for i in b['its'] if i.kind == 't']
        return ts and all(i.ref.get('s', 11) < 0.85 * base for i in ts)
    k = 0
    while k < len(rows) - 1:
        a, b = rows[k], rows[k + 1]
        if (drawn(a) or drawn(b) or small(a)) and b['y0'] - a['y1'] < 4.0:
            a['its'] += b['its']; a['y1'] = max(a['y1'], b['y1']); del rows[k + 1]
            continue
        k += 1
    return rows


def _chunks(its):
    """Unbreakable pieces of one line: ink closer than a word space, or stacked (x-overlapping) pieces."""
    out = []
    for it in sorted(its, key=lambda i: i.x0):
        if out and it.x0 - out[-1]['x1'] < GAP:
            out[-1]['its'].append(it); out[-1]['x1'] = max(out[-1]['x1'], it.x1)
        else:
            out.append({'its': [it], 'x0': it.x0, 'x1': it.x1})
    return out


def _cell(items, c0, c1, n0, n1, align='left', push=None, growth=None):
    """Lay the items of one printed cell [c0, c1] into our column [n0, n1]. Returns (placed pieces, bottom y, top y)."""
    if not items:
        return [], None, None
    push = push or (lambda y: 0.0)
    lines = _lines_of(items)
    width = n1 - n0 - 2 * PAD
    left = min(i.x0 for i in items)
    lead = max(1.5, min(left - c0, PAD + 2))
    out, extra = [], 0.0
    # a paragraph printed over several lines (the printed column was wider than ours) is re-flowed as one: its lines are
    # joined when they hold only text, start at the same indent and the line before ran to the cell's right side (round 27,
    # 2014 MJ 62 q2(b): 'previous / numerator.' broken lines)
    def plain(ln):
        return all(i.kind == 't' for i in ln['its'])
    k = 0
    while k < len(lines) - 1 and align != 'right':
        a, b = lines[k], lines[k + 1]
        lh_ = a['y1'] - a['y0']
        ax0, ax1 = min(i.x0 for i in a['its']), max(i.x1 for i in a['its'])
        bx0 = min(i.x0 for i in b['its'])
        first_b = min(b['its'], key=lambda i: i.x0).ref.get('t', '') if plain(b) else ''
        if plain(a) and plain(b) and abs(ax0 - bx0) < 3 and b['y0'] - a['y1'] < 0.6 * lh_ and ax1 > c1 - 0.3 * (c1 - c0) \
                and (ax1 - ax0) > width * 0.6 and re.match(r'[a-z]', first_b) and not re.match(r'(or|and)$', first_b):
            # (only a line that goes on with a sentence: '[x =] 1.13 ...' or 'or ...' is a new answer line, round 28)
            a.setdefault('parts', [dict(a, its=list(a['its']))]).append(b)
            a['its'] = a['its'] + b['its']; a['y1'] = b['y1']
            del lines[k + 1]
            continue
        k += 1
    for ln in lines:
        if ln.get('parts'):                            # re-flow: chunks one after the other, a space between words
            first = ln['parts'][0]
            lh = first['y1'] - first['y0']
            pitch = (ln['parts'][1]['y0'] - first['y0']) if len(ln['parts']) > 1 else lh + 2.0
            x, row = 0.0, 0
            for j, part in enumerate(ln['parts']):
                for ch in _chunks(part['its']):
                    w_ = ch['x1'] - ch['x0']
                    sp_ = 0.0 if x == 0 else 0.25 * 11.0
                    if x and x + sp_ + w_ > width + 0.5:
                        row += 1; x, sp_ = 0.0, 0.0
                    dx = n0 + lead + x + sp_ - ch['x0']
                    dy = extra + push(first['y0']) + (first['y0'] + row * pitch) - part['y0']
                    for it in ch['its']:
                        out.append((it, dx, dy, 1.0, ch['x0']))
                    x += sp_ + w_
            g_ = (first['y0'] + row * pitch + lh) - ln['y1']
            extra += g_
            if growth is not None and abs(g_) > 0.01:
                growth.append((ln['y1'], g_))
            continue
        chunks = _chunks(ln['its'])
        rel0 = chunks[0]['x0'] - left                  # this printed line's indent in its cell
        span_all = chunks[-1]['x1'] - chunks[0]['x0']
        lead_ts = [i for i in ln['its'] if i.kind == 't' and i.x0 - chunks[0]['x0'] < 3]
        multi = len({round(i.ref['y'] / (0.9 * i.ref.get('s', 11))) for i in lead_ts}) >= 2 and len(lead_ts) >= 2
        if multi:                                      # two printed lines joined by a tall sign (a root over brackets, 2025 MJ
            chunks = [{'its': list(ln['its']), 'x0': chunks[0]['x0'], 'x1': chunks[-1]['x1']}]   # 21 q15): one block,
            #                                             never wrapped piece by piece (they were drawn on top of each other)
        first_shift = 0.0
        if span_all <= width + 0.5 and chunks[-1]['x1'] - left > width + 0.5:
            first_shift = min(rel0, chunks[-1]['x1'] - left - width)   # a line hanging right ('+ 8[corners]', 2021 FM 62 q4)
            #                                             moves left to end at our column edge instead of wrapping
        vis = [{'chs': [], 'shift': first_shift}]
        for ch in chunks:
            cur = vis[-1]
            if cur['chs'] and (ch['x1'] - left - cur['shift']) > width + 0.5:
                vis.append({'chs': [], 'shift': (ch['x0'] - left) - rel0})   # wrapped: starts at the line's indent
                cur = vis[-1]
            cur['chs'].append(ch)
        lh = ln['y1'] - ln['y0']
        for k, r in enumerate(vis):
            dy = extra + push(ln['y0']) + k * (lh + 2.0)
            span = r['chs'][-1]['x1'] - r['chs'][0]['x0']
            sc = width / span if span > width + 0.5 else 1.0        # one unbreakable piece wider than the column
            if align == 'right':
                dx = n1 - PAD - r['chs'][-1]['x1']
            else:
                dx = n0 + lead - left - r['shift']
                if sc != 1.0:
                    dx = n0 + lead - r['chs'][0]['x0']
            for ch in r['chs']:
                for it in ch['its']:
                    out.append((it, dx, dy, sc, r['chs'][0]['x0']))
        extra += (len(vis) - 1) * (lh + 2.0)
        if growth is not None and len(vis) > 1:
            growth.append((ln['y1'], (len(vis) - 1) * (lh + 2.0)))
    bottom = max(it.y1 for it in items) + extra + push(1e9)
    return out, bottom, min(i.y0 for i in items)


_FONTS = {('serif', 0): 'tiro', ('serif', 1): 'tibo', ('sans', 0): 'helv', ('sans', 1): 'hebo'}


def text_width(t, fam, s, bold=False):
    """Width of a text in the font the page draws it with (Times / Helvetica metrics = the review and site fonts)."""
    import fitz
    return round(fitz.get_text_length(t, fontname=_FONTS.get((fam if fam in ('serif', 'sans') else 'serif', int(bool(bold))), 'tiro'),
                                      fontsize=s), 2)


TOP = 4.0          # free space above the highest ink of a row (round 28: fractions touched the row's top rule)
MARGIN = 3.0       # extra space above and below a line holding stacked maths (fraction, vector, root)
LGAP = 1.5         # least free space between two printed lines of one cell


def _pushes(cols, base):
    """Vertical space to add, as a function of the printed y: lines with stacked maths get MARGIN above and below,
    the first line TOP below the row's top. The pushes of all columns are joined (the larger one wins at each height),
    so a line keeps its printed height against the same line in the other columns (round 28, Dhruv: 'margin around
    the fraction, the whole line vertically centred')."""
    per = []
    for its in cols:
        ln = _lines_of(its) if its else []
        ps, prev = [], None
        for l in ln:
            tall = (l['y1'] - l['y0']) > 1.45 * base
            if prev is None:
                need = TOP + (MARGIN if tall else 0.0) - l['y0']
                if need > 0:
                    ps.append((-1e9, need))
            else:
                ptall = (prev['y1'] - prev['y0']) > 1.45 * base
                need = LGAP + (MARGIN if tall or ptall else 0.0) - (l['y0'] - prev['y1'])
                if need > 0:
                    ps.append((l['y0'] - 0.01, need))
            prev = l
        if prev is not None and (prev['y1'] - prev['y0']) > 1.45 * base:
            ps.append((prev['y0'] + 0.01, MARGIN))      # space under a tall last line (counted in the row's height)
        per.append(ps)
    marks = sorted({y for ps in per for y, _ in ps})
    def push(y):
        return max([sum(p for yy, p in ps if yy < y) for ps in per] + [0.0])
    return push


def _scaled_unit(u, K):
    """The whole printed row at K times its size (so its normal text is 11 pt, MS_TABLE_RULES 25)."""
    if abs(K - 1) < 0.04:
        return dict(u, _K=1.0)
    v = dict(u, w=round(u['w'] * K, 2), h=round(u['h'] * K, 2), _K=K)
    v['text'] = [dict(t, x=round(t['x'] * K, 2), y=round(t['y'] * K, 2), w=round(t['w'] * K, 2), s=round(t.get('s', 11) * K, 2))
                 for t in u.get('text', [])]
    def sp(d):
        out = []
        for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
            n = [float(x) * K for x in NUM.findall(args)]
            out.append(cmd + ' '.join(f'{a:.2f}' for a in n))
        return ''.join(out)
    v['lines'] = [dict(l, d=sp(l['d']), **({'sw': round(l['sw'] * K, 2)} if 'sw' in l else {})) for l in u.get('lines', [])]
    for k in ('glyphs', 'images'):
        if u.get(k):
            v[k] = [dict(g, x=round(g['x'] * K, 2), y=round(g['y'] * K, 2), w=round(g['w'] * K, 2), h=round(g['h'] * K, 2)) for g in u[k]]
    if u.get('figs'):
        v['figs'] = [dict(f, x=round(f['x'] * K, 2), y=round(f['y'] * K, 2), k=round(f.get('k', 1) * K, 4)) for f in u['figs']]
    return v


def layout_row(u, label, ncols, first_unit=True, hint=None, QW=QW, fam=None, base=None):
    """One printed row unit -> our row unit, or None when its columns cannot be read."""
    if base:
        K = 11.0 / base
        u = _scaled_unit(u, K)
        if hint:
            hint = ([x * K for x in hint[0]], hint[1] * K)
    edges = columns(u)
    if hint and (not edges or len(edges) != len(hint)) and abs(u['w'] - hint[1]) < 2:
        edges = list(hint[0])                            # a graph / grid in the row hides its column rules: same table
    if not edges:
        return None
    if len(edges) == 2:
        edges = edges + [u['w'] - 0.5]                   # no Partial Marks column printed
    cells_src = [(0.0, edges[0]), (edges[0], edges[1]), (edges[1], edges[2]), (edges[2], u['w'])]
    A = (W - QW - MW) / 2 if ncols == 4 else W - QW - MW
    ours = [(0.0, QW), (QW, QW + A), (QW + A, QW + A + MW), (QW + A + MW, W)]
    its = _items(u, edges[:3])
    if not any(i.kind != 'lines' and not (i.kind == 't' and re.fullmatch(r'[.\s…_|\-]+', i.ref['t'])) for i in its):
        return 'empty'                                   # only rules left (the end of a table on a page): no row
    by = [[], [], [], []]
    for it in its:
        cx = (it.x0 + it.x1) / 2
        c = 0 if cx < edges[0] else 1 if cx < edges[1] else 2 if cx < edges[2] else 3
        by[c].append(it)
    v = {'src': u['src'], 'w': W, 'h': 0.0, 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    bottoms = []
    push0 = _pushes([by[0], by[1], by[2], by[3]], 11.0 if base else max([i.ref.get('s', 11) for i in its if i.kind == 't'] or [11]))
    # rows grow in step: a line that wraps in one column moves the lines below it in EVERY column (round 28, 2025 MJ 61 q4:
    # the '1' mark stayed beside the wrong line). Pass 1 measures each column's growth by printed height.
    grows = {}
    for c in (1, 2, 3):
        if by[c] and not (c == 3 and ncols == 3) and not ((_picture_cell(by[c]) or u['src']['page'] in CTX.get('broken', ()))
                                                          and CTX.get('pdf')):
            g = []
            _cell(by[c] + (by[3] if c == 1 and ncols == 3 else []), cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1],
                  align='right' if c == 2 else 'left', push=push0, growth=g)
            grows[c] = g
    def G(c, y):
        return sum(a for yy, a in grows.get(c, []) if yy < y)
    def push_for(c):
        return lambda y: push0(y) + max([G(k, y) for k in grows] + [0.0]) - G(c, y)
    push = push_for(0)
    top_pad = min([i.y0 for i in its] + [u['h']])
    for c in (1, 2, 3):
        if c == 3 and ncols == 3:
            by[1] += by[3]; continue
        if (_picture_cell(by[c]) or u['src']['page'] in CTX.get('broken', ())) and by[c] and CTX.get('pdf'):   # a diagram / shaded sketch in the cell: its printed picture (pattern 78)
            tbx = [(t.x0 - 1.5, t.y0 - 1.5, t.x1 + 1.5, t.y1 + 1.5) for t in by[c] if t.kind == 't']
            dr = [i for i in by[c] if i.kind != 't' and not (i.kind == 'lines' and i.y1 - i.y0 < 1.6 and i.x1 - i.x0 < 80)
                  and not (i.kind == 'lines' and max(i.x1 - i.x0, i.y1 - i.y0) < 40 and any(
                      i.x0 < b[2] and i.x1 > b[0] and i.y0 < b[3] and i.y1 > b[1] for b in tbx))] or by[c]
            # (a root sign / bar on a text line below a table is text, not the drawing: 2025 MJ 61 q1, round 28)
            groups_ = []                                 # drawings in clusters (6 pt apart): the picture is the main ones,
            for i in sorted(dr, key=lambda i: (i.y0, i.x0)):   # small marks standing apart (a bracket or sign in the
                box_ = [i.x0 - 6, i.y0 - 6, i.x1 + 6, i.y1 + 6]  # notes under a table) stay with the text
                hit = [g for g in groups_ if g['b'][0] < box_[2] and g['b'][2] > box_[0] and g['b'][1] < box_[3] and g['b'][3] > box_[1]]
                g = {'its': [i], 'b': box_}
                for h in hit:
                    g['its'] += h['its']; groups_.remove(h)
                    g['b'] = [min(g['b'][0], h['b'][0]), min(g['b'][1], h['b'][1]), max(g['b'][2], h['b'][2]), max(g['b'][3], h['b'][3])]
                groups_.append(g)
            if len(groups_) > 1:
                big = max((g['b'][2] - g['b'][0]) * (g['b'][3] - g['b'][1]) for g in groups_)
                dr = [i for g in groups_ if (g['b'][2] - g['b'][0]) * (g['b'][3] - g['b'][1]) >= 0.3 * big for i in g['its']]
            px0, py0 = min(i.x0 for i in dr), min(i.y0 for i in dr)
            px1, py1 = max(i.x1 for i in dr), max(i.y1 for i in dr)
            inpic = [i for i in by[c] if px0 - 14 <= (i.x0 + i.x1) / 2 <= px1 + 14 and py0 - 12 <= (i.y0 + i.y1) / 2 <= py1 + 12
                     and not (i.kind == 't' and len(i.ref['t']) > 6 and not (py0 - 2 <= (i.y0 + i.y1) / 2 <= py1 + 2))]
            # (short labels just outside the drawing go with it; words of the text around it do not - round 28, 2025 MJ 61
            # q1: the lines under a table went into its picture and everything shrank)
            if u['src']['page'] in CTX.get('broken', ()):
                inpic = list(by[c])                      # broken text layer: the whole cell is its printed picture
            grow = True                                  # text on the same line as the drawing belongs to the picture
            while grow:
                grow = False
                for t_ in [i for i in by[c] if i not in inpic and i.kind == 't']:
                    if any(o.kind != 't' and min(o.y1, t_.y1) - max(o.y0, t_.y0) > 0.5 * (t_.y1 - t_.y0) for o in inpic) \
                            and not (t_.y0 < py0 + 3 and len(t_.ref['t']) > 3 and t_.y1 <= py0 + 0.6 * (t_.y1 - t_.y0) + 3):
                        inpic.append(t_); grow = True
            rest = [i for i in by[c] if i not in inpic]
            pasted = [i for i in dr if i.kind in ('images', 'figs')]
            head = [t_ for t_ in by[c] if t_.kind == 't' and t_.y0 < py0 + 3 and t_.y1 > py0 - 0.5
                    and any(i.y0 < t_.y1 for i in pasted)]   # a text line a pasted picture lies over (never a drawn box,
            head_moved = any(len(t_.ref['t']) > 3 for t_ in head)
            if head_moved:                                   # 2021 FM 42 q9) ('Correct diagram' half hidden, 2021 FM 32 q9):
                line = [t_ for t_ in by[c] if t_.kind == 't' and any(abs(t_.ref['y'] - h_.ref['y']) < 2 for h_ in head)]
                py0 = max([py0] + [t_.y1 + 0.5 for t_ in line])   # the picture starts under it, the WHOLE line is our text
                for t_ in line:                              # (round 28: only its first word was kept)
                    if t_ in inpic:
                        inpic.remove(t_)
                    if t_ not in rest:
                        rest.append(t_)
            shift, tb = 0.0, None
            if rest:                                     # text around the picture ('Correct diagram') laid out as text
                above = [i for i in rest if i.y1 <= py0 + 1]
                placed, tb, _ = _cell(rest, cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1], push=push_for(c))
                for it, dx, dy, k, x0 in placed:
                    _emit(v, it, dx, dy, k, x0)
                if above:
                    pl_ab = [p_ for p_ in placed if p_[0] in above]
                    shift = max([p_[2] for p_ in pl_ab] + [0.0])
            shift = max(shift, push(py0))                # (the heading's placement already holds the push)
            broken_pg = u['src']['page'] in CTX.get('broken', ())
            bot = _cell_picture(v, u, inpic, cells_src[c], ours[c], (px0, py0, px1, py1) if head_moved and not broken_pg else None,
                                shift)          # (top clamped only under a moved heading: a rotated 'All' above a table
            #                                     was cut, 2021 FM 52 q3)
            #                     (broken page: from the cell's first ink - the formula over the graph was cut, 2014 MJ 62 q6)
            if bot is not None:
                bottoms.append(max(bot, tb or 0))
                continue
        placed, bot, _ = _cell(by[c], cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1],
                               align='right' if c == 2 else 'left', push=push_for(c))
        for it, dx, dy, k, x0 in placed:
            _emit(v, it, dx, dy, k, x0)
        if bot is not None:
            bottoms.append(bot)
    # Q column: our full label on the first printed line (continued rows show none)
    lab_items = sorted(by[0], key=lambda i: i.y0)
    s0 = next((i.ref.get('s', 11) for i in lab_items if i.kind == 't'), 11.0)
    if first_unit and label:
        y0 = min([i.ref['y'] for i in lab_items if i.kind == 't'] or
                 [i.ref['y'] for c in (1, 2) for i in by[c] if i.kind == 't'] or [top_pad + 0.78 * s0])
        f = next((i.ref.get('f') for i in lab_items if i.kind == 't'), 'serif')
        s0 = 11.0
        tw = text_width(label, fam or f, s0)               # the real width: a guessed one stretched the label (round 28)
        v['text'].append({'t': label, 'x': round(max(2.0, (QW - tw) / 2), 2), 'y': round(y0 + push(y0 - 0.5), 2), 'w': tw,
                          's': s0, 'f': f})            # Q labels in normal weight (Dhruv, round 28)
    bottom_pad = max(3.0, min(8.0, u['h'] - max([i.y1 for i in its] + [0])))
    lab_bot = max([i.y1 for i in by[0]] + [0]) + push(1e9)
    v['h'] = round(max([b + bottom_pad for b in bottoms] + [lab_bot + bottom_pad, 18.0]), 2) if bottoms else u['h']
    if ncols == 4:
        xs = [QW, QW + A, QW + A + MW]
    else:
        xs = [QW, QW + A]
    for x in xs:
        v['lines'].append({'d': f'M{x - 0.3:.2f} 0.00L{x + 0.3:.2f} 0.00L{x + 0.3:.2f} {v["h"]:.2f}L{x - 0.3:.2f} {v["h"]:.2f}Z', 'fill': '#000000'})
    if fam:                                          # one font for question and mark scheme (Dhruv, round 27)
        for t in v['text']:
            if t.get('f') in ('serif', 'sans'):
                t['f'] = fam
    v['info'] = {'edges': edges, 'new_edges': xs, 'new_w': [QW, A, MW] + ([A] if ncols == 4 else [])}
    return v


CTX = {}


def _picture_cell(items):
    """A cell whose content is a drawing (Venn diagram, sketch, shaded region, picture) rather than text + fraction bars,
    or whose text layer is broken (words drawn over each other, 2014 MJ 62 p4)."""
    if any(i.kind in ('images', 'figs') for i in items):
        return True
    ts = [i for i in items if i.kind == 't' and i.x1 - i.x0 > 2]
    clash = sum(1 for k, a in enumerate(ts) for b in ts[k + 1:]
                if abs(a.ref['y'] - b.ref['y']) < 3.0 and min(a.x1, b.x1) - max(a.x0, b.x0) > 0.4 * min(a.x1 - a.x0, b.x1 - b.x0))
    if clash >= 2:
        return True
    # curves / slanted strokes bigger than a root sign (Venn circles, sketches, arrows of a mapping) or a large shaded
    # area; ruled inner tables (straight rules only) stay text (MS_TABLE_RULES 9)
    curvy = [i for i in items if i.kind == 'lines' and ('C' in i.ref.get('d', '') or _slanted(i.ref.get('d', '')))
             and (i.x1 - i.x0) > 30 and (i.y1 - i.y0) > 30]
    shaded = [i for i in items if i.kind == 'lines' and i.ref.get('fill') and i.ref.get('fill', '').lower() not in ('#000000', '#ffffff', '#231f20')]
    shaded = shaded if sum((i.x1 - i.x0) * (i.y1 - i.y0) for i in shaded) > 400 else []   # shading drawn in thin strips
    #                                                                     counts together (2019 ON 51 q1(b)(ii), round 28)
    # a graph / grid drawn with straight lines: long rules both ways (root signs and brackets are short strokes: a cell full
    # of square roots was taken for a graph, round 28 2025 MJ 61 q4)
    gv = [i for i in items if i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 20]
    gh = [i for i in items if i.kind == 'lines' and i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 40]
    # axes: a long vertical line crossing a long horizontal one - every graph has them, root signs and brackets never
    # (round 28: graphs drawn from short straight pieces with dashed grids were laid out as faint loose lines, 2014 MJ 42 q2)
    av = [i for i in items if i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 30]
    ah = [i for i in items if i.kind == 'lines' and i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 40]
    axes = any(h.x0 - 1 <= v.x0 <= h.x1 + 1 and v.y0 - 1 <= h.y0 <= v.y1 + 1 for v in av for h in ah)
    # a drawing made of many short pieces (a graph traced in 20 pt segments, 2014 MJ 42 q2): pieces that touch no text
    # (root signs and fraction bars always sit on their text)
    tb = [(t.x0 - 1.5, t.y0 - 1.5, t.x1 + 1.5, t.y1 + 1.5) for t in ts]
    free = [i for i in items if i.kind == 'lines' and not (i.y1 - i.y0 < 1.6 and i.x1 - i.x0 < 60)
            and max(i.x1 - i.x0, i.y1 - i.y0) > 3
            and not any(i.x0 < b[2] and i.x1 > b[0] and i.y0 < b[3] and i.y1 > b[1] for b in tb)]
    slant = [i for i in free if i.x1 - i.x0 > 1.6 and i.y1 - i.y0 > 1.6 and max(i.x1 - i.x0, i.y1 - i.y0) > 8]
    #        (the tick of a root sign is 2.7 x 5 pt and stands beside its text; curve pieces are longer)
    def spread(lst):
        return lst and (max(i.x1 for i in lst) - min(i.x0 for i in lst)) > 60 and (max(i.y1 for i in lst) - min(i.y0 for i in lst)) > 30
    pieces = (len(free) >= 20 and spread(free)) or (len(slant) >= 5 and spread(slant))   # (a curve over a grid, 2014 MJ 43 q6)
    return bool(curvy) or bool(shaded) or (len(gv) >= 3 and len(gh) >= 3) or axes or pieces


def _slanted(d):
    pts = [(float(a), float(b)) for a, b in re.findall(r'[ML]\s*(-?[\d.]+)[ ,](-?[\d.]+)', d)]
    return any(abs(p[0] - q[0]) > 1 and abs(p[1] - q[1]) > 1 for p, q in zip(pts, pts[1:]))


def _cell_picture(v, u, items, src, ours, region=None, shift=0.0):
    """Render the cell's printed region from the PDF as one picture (white transparent), placed at the cell's top, shrunk
    to the column (never below 60 %; MS_TABLE_RULES 13). Returns the bottom y."""
    import os, fitz
    from PIL import Image
    K = u.get('_K', 1.0)
    x0, x1 = max(src[0] + 1.0, min(i.x0 for i in items) - 1.5), min(src[1] - 1.0, max(i.x1 for i in items) + 1.5)
    y0 = max(0.5, min(i.y0 for i in items) - 1.5); y1 = min(u['h'] - 0.5, max(i.y1 for i in items) + 1.5)
    if region:
        y0 = max(y0, region[1])                          # not over a text line kept as our text
    b = u['src']['box']
    r = fitz.Rect(b[0] + x0 / K, b[1] + y0 / K, b[0] + x1 / K, b[1] + y1 / K)
    doc = CTX.setdefault('doc', fitz.open(CTX['pdf']))
    # grow sideways to whole ink inside the cell: words that are no text items (a rotated 'All' left of 'pos', 2021 FM 52
    # q3) were cut at the picture's left edge (round 28)
    import numpy as np
    lo, hi = b[0] + (src[0] + 1.0) / K, b[0] + (src[1] - 1.0) / K
    pg_ = doc[u['src']['page'] - 1]
    for _ in range(12):
        grown = False
        for side in ('l', 'r'):
            xa = r.x0 - 1.5 if side == 'l' else r.x1 + 0.2
            if (side == 'l' and r.x0 - 2.5 < lo) or (side == 'r' and r.x1 + 2.5 > hi):
                continue
            bp = pg_.get_pixmap(clip=fitz.Rect(xa, r.y0, xa + 1.3, r.y1), dpi=150, colorspace=fitz.csGRAY)
            a = np.frombuffer(bp.samples, np.uint8)
            if a.size and (a < 160).sum() >= 2:
                if side == 'l':
                    r.x0 -= 2.5
                else:
                    r.x1 += 2.5
                grown = True
        if not grown:
            break
    pix = doc[u['src']['page'] - 1].get_pixmap(clip=r, dpi=220)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
    im.putdata([(a, b_, c, 0 if a > 245 and b_ > 245 and c > 245 else 255) for a, b_, c, _ in im.getdata()])   # near-white
    # (232 erased light grey graph grids, round 28 - 245 kept: the grey band of 2021 FM 32 q9 is printed so)
    box = im.getbbox()
    if not box:
        return None
    im = im.crop(box)
    name = f"msimg_{u['src']['page']}_{int(r.x0)}_{int(r.y0)}.png"
    im.save(os.path.join(CTX['store'], 'figures', name))
    w, h = im.width / 220 * 72 * K, im.height / 220 * 72 * K
    room = ours[1] - ours[0] - 2 * PAD
    k = min(1.0, room / w) if w else 1.0
    k = max(k, 0.6)
    x = ours[0] + PAD + max(0.0, (x0 + box[0] / 220 * 72 * K - src[0] - PAD)) if k == 1.0 else ours[0] + PAD
    x = min(x, ours[1] - PAD - w * k)
    y = y0 + shift + box[1] / 220 * 72 * K
    v.setdefault('images', []).append({'file': name, 'x': round(x, 2), 'y': round(y, 2), 'w': round(w * k, 2), 'h': round(h * k, 2),
                                       'src': [u['src']['page'], round(r.x0 + box[0] / 220 * 72, 2), round(r.y0 + box[1] / 220 * 72, 2),
                                               round(r.x0 + box[2] / 220 * 72, 2), round(r.y0 + box[3] / 220 * 72, 2)]})
    return y + h * k


def _emit(v, it, dx, dy, k, x0):
    if it.kind == 't':
        t = dict(it.ref)
        if k != 1.0:
            t['x'] = round(x0 + dx + (t['x'] - x0) * k, 2); t['s'] = round(t.get('s', 11) * k, 2); t['w'] = round(t['w'] * k, 2)
        else:
            t['x'] = round(t['x'] + dx, 2)
        t['y'] = round(t['y'] + dy, 2)
        v['text'].append(t)
    elif it.kind == 'lines':
        l = dict(it.ref)
        if k != 1.0:
            from ms_layout import _map_path
            l['d'] = _map_path(l['d'], lambda x: x0 + dx + (x - x0) * k, lambda y: y + dy)
        else:
            l['d'] = _shift(l['d'], dx, dy)
        v['lines'].append(l)
    else:
        g = dict(it.ref)
        g['x'] = round(x0 + dx + (g['x'] - x0) * k, 2); g['y'] = round(g['y'] + dy, 2)
        if 'w' in g: g['w'] = round(g['w'] * k, 2)
        if 'h' in g: g['h'] = round(g['h'] * k, 2)
        if it.kind == 'figs': g['k'] = round(g.get('k', 1) * k, 4)
        v.setdefault(it.kind, []).append(g)


def build(q, uniq, store, hdr_unit, own_total, frame):
    """All rows of one maths question -> ms_p dict, or None to let the general path try."""
    import os
    CTX.clear()
    try:
        import paths
        from run import cleaned
        pp = q['paper']; ses = pp['session']; pv = pp['code'].split('/')[1]
        raw = os.path.join(paths.ROOT, 'raw', pp['syllabus'], ses, f'ms_{pv}.pdf')
        if os.path.exists(raw):
            CTX.update(pdf=cleaned(raw), store=store)
    except Exception:
        pass
    import collections
    fc = collections.Counter(t.get('f') for p in q.get('parts', []) for un in p.get('layout', []) for t in un.get('text', [])
                             if t.get('f') in ('serif', 'sans'))
    fam = fc.most_common(1)[0][0] if fc else None
    sz = sorted(t.get('s', 11) for _, u in uniq for t in u.get('text', []) if t.get('t', '').strip() and t.get('s', 11) >= 7)
    base = sz[len(sz) // 2] if sz else 11.0             # the scheme's normal text size -> ours is 11 pt
    uniq = [(r, _scaled_unit(u, 11.0 / base)) for r, u in uniq]
    pages = collections.defaultdict(int)             # a page whose text layer is broken (words drawn over each other):
    for _, u in uniq:                                # every cell on it is kept as its printed picture (2014 MJ 62 p4)
        ts = [t for t in u.get('text', []) if t.get('t', '').strip() and t['w'] > 2]
        pages[u['src']['page']] += sum(1 for k, a in enumerate(ts) for b in ts[k + 1:] if a['t'] != b['t']
                                       and abs(a['y'] - b['y']) < 3 and min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x']) > 0.5 * min(a['w'], b['w']))
    CTX['broken'] = {p for p, n in pages.items() if n >= 6}
    cols = [(columns(u), u['w']) for _, u in uniq]
    ncols = 4 if any(len(c or []) == 3 for c, _ in cols) else 3
    good = [(c, w) for c, w in cols if c and len(c) == ncols - 1]
    hint = max(good, key=lambda cw: sum(1 for c2, w2 in good if c2 == cw[0])) if good else None
    qw = max([QW] + [round(text_width(r['label'], fam, 11.0) + 10) for r, _ in uniq])   # long labels ('11(d)(iii)'): wider Q
    out, seen_lab = [], set()
    for r, u in uniq:
        if u['h'] < 4:
            continue
        v = layout_row(u, r['label'], ncols, first_unit=r['label'] not in seen_lab, hint=hint, QW=qw, fam=fam)
        if v == 'empty':
            continue
        if v is None:
            return None
        seen_lab.add(r['label'])
        out.append(v)
    if not out:
        return None
    info = out[0]['info']
    for v in out:
        v.pop('info', None)
        frame(v)
    first = {'edges': info['edges'], 'new_edges': info['new_edges'], 'new_w': info['new_w']}
    rows = ([hdr_unit(first, ncols, fam)] if hdr_unit else []) + out
    if hdr_unit:                                     # header words: real bold widths, centred in their column
        ne = [0.0] + list(first['new_edges']) + [W]
        for t in rows[0]['text']:
            cx = t['x'] + t['w'] / 2
            k = next((j for j in range(len(ne) - 1) if ne[j] <= cx < ne[j + 1]), None)
            t['w'] = text_width(t['t'], fam, t.get('s', 11.0), True)
            if k is not None:
                t['x'] = round((ne[k] + ne[k + 1] - t['w']) / 2, 2)
    tot = own_total(q.get('marks'), first, out) if q.get('marks') else None
    if tot:
        for t in tot['text']:                        # the total row in our normal size (its template can be a tiny axis label)
            t.update(s=11.0, b=1, w=text_width(t['t'], fam, 11.0, True), **({'f': fam} if fam else {}))
            t.pop('i', None)
        tw = tot['text']
        if len(tw) == 2:
            tw[0]['x'] = round(first['new_edges'][1] - 6 - tw[0]['w'], 2)
            tw[1]['x'] = round(first['new_edges'][2] - 6 - tw[1]['w'], 2) if len(first['new_edges']) > 2 else tw[1]['x']
        frame(tot)
        rows.append(tot)
    if hdr_unit:
        rows[0]['lines'] += []
    return {'w': W, 'h': round(sum(v['h'] for v in rows), 2), 'rows': rows, 'problems': [], 'modes': {'maths': len(out)},
            'info': first, 'has_header': bool(hdr_unit), 'printed_total': None}
