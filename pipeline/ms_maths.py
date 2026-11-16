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
ANSWER_SHARE = 0.6        # Answer : Partial Marks = 60 : 40 of the room left by Q and Marks (MS_TABLE_RULES 24, round 29)
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
            xs[-1][2].append((b[1], b[3]))
        else:
            xs.append([x, 0, [(b[1], b[3])]])
    for e in xs:                # covered height = the UNION of the pieces (a graph's grid line drawn 3 times over itself
        tot, end = 0.0, -1e9    # out-measured the table's rules: 2014 MJ 43 q9, round 30)
        for a, b_ in sorted(e[2]):
            if b_ > end:
                tot += b_ - max(a, end); end = b_
        e[1] = tot
    xs = [(x, c) for x, c, _ in xs]
    inner = [x for x, c in xs if c > 0.6 * u['h'] and 20 < x < u['w'] - 20]
    if len(inner) not in (2, 3) and xs:                  # a grid drawn in the answer (2014 MJ 22 q2) has tall lines too:
        top = max(c for _, c in xs)                      # the table's own rules run the full height
        inner = [x for x, c in xs if c > 0.97 * top and 20 < x < u['w'] - 20]
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
        d_ = t.get('dir') or [1.0, 0.0]
        if abs(d_[0]) < 0.3 and d_[1] < 0:            # rotated, read upwards: the word runs UP from (x, y) and its glyphs
            its.append(_Item('t', t, t['x'] - 0.78 * s, t['y'] - t['w'], t['x'] + 0.22 * s, t['y']))   # stand left
            continue                                  # (round 30: boxed as level text '3 neg' fell out of its table, 2021 FM 52 q3)
        if abs(d_[0]) < 0.3 and d_[1] > 0:            # rotated, read downwards
            its.append(_Item('t', t, t['x'] - 0.22 * s, t['y'], t['x'] + 0.78 * s, t['y'] + t['w']))
            continue
        its.append(_Item('t', t, t['x'], t['y'] - 0.78 * s, t['x'] + t['w'], t['y'] + 0.22 * s))
    for k in ('glyphs', 'images'):
        for g in u.get(k) or []:
            its.append(_Item(k, g, g['x'], g['y'], g['x'] + g['w'], g['y'] + g['h']))
    for f in u.get('figs') or []:
        its.append(_Item('figs', f, f['x'], f['y'], f['x'] + f.get('w', 0), f['y'] + f.get('h', 0)))
    shaded = any(l.get('fill', '').lower() not in ('', '#ffffff', '#000000', '#231f20') for l in u.get('lines', []))
    vb = [b for b in (_bbox(l['d']) for l in u.get('lines', [])) if b and b[2] - b[0] < 1.3 and b[3] - b[1] > 8]
    def grid_v(b):          # one of >= 3 thin verticals with the same span, away from the column rules: a table's own
        return (sum(abs(o[1] - b[1]) < 2 and abs(o[3] - b[3]) < 2 for o in vb) >= 3     # (round 30, 2014 MJ 62 q3)
                and not any(abs((b[0] + b[2]) / 2 - e) < 2.5 for e in edges + [0.5, u['w'] - 0.5])
                and len(edges) >= 2 and edges[0] < (b[0] + b[2]) / 2 < edges[1])               # inside the Answer column
    # a rule printed as many short pieces (2014 MJ 62 page 4: 12 pt dashes): each piece is judged by the whole run
    hz = sorted((b, id(l)) for l, b in ((l, _bbox(l['d'])) for l in u.get('lines', []))
                if b and b[3] - b[1] < 1.3 and b[2] - b[0] >= 4)   # dashes of a rule (12 pt), never a curve's tiny steps
    span = {}
    run = []
    def close(run):
        for b, k in run:
            span[k] = (min(r[0][0] for r in run), max(r[0][2] for r in run))
    for b, k in sorted(hz, key=lambda t: ((t[0][1] + t[0][3]) / 2, t[0][0])):
        if run and abs((run[-1][0][1] + run[-1][0][3]) / 2 - (b[1] + b[3]) / 2) < 0.4 and b[0] - max(r[0][2] for r in run) < 1.5:
            run.append((b, k))
        else:
            if run:
                close(run)
            run = [(b, k)]
    if run:
        close(run)
    hb = [b for b in (_bbox(l['d']) for l in u.get('lines', [])) if b and b[3] - b[1] < 1.6 and b[2] - b[0] > 40]
    def axis_v(b):          # the y-axis of a sketch: a horizontal axis starts at it inside its height, away from the
        x = (b[0] + b[2]) / 2   # column rules (round 30, 2025 MJ 61 q5(a)(v): taken for a column rule)
        return (b[3] - b[1] < 0.9 * u['h'] and not any(abs(x - e) < 4 for e in edges + [0.5, u['w'] - 0.5])
                and len(edges) >= 2 and edges[0] < x < edges[1]                     # only in the Answer column
                and any(h[0] - 3 <= x <= h[2] + 3 and b[1] + 5 < (h[1] + h[3]) / 2 <= b[3] + 1 for h in hb))
    for l in u.get('lines', []):
        if l.get('fill', '').lower() == '#ffffff' and 'stroke' not in l and not shaded:
            continue                                    # (a white box over grey 'un-shades' a cell: kept, round 28 2019 ON 51 q1)
        b0 = _bbox(l['d'])
        if not b0:
            continue
        b = (span[id(l)][0], b0[1], span[id(l)][1], b0[3]) if id(l) in span else b0
        if b[2] - b[0] < 1.3 and not grid_v(b) and not axis_v(b) and (b[3] - b[1] > 0.5 * u['h'] or any(abs((b[0] + b[2]) / 2 - e) < 2.5 for e in edges + [0.5, u['w'] - 0.5])
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
        if b[3] - b[1] < 1.6 and len(edges) >= 2 and edges[1] < (b[0] + b[2]) / 2 < (edges[2] if len(edges) >= 3 else u['w']):
            continue                                    # the Marks column holds no drawing: a short line there is the
            #                                             printed total's underline (round 29, 2014 MJ 11 q4(b), q12(c))
        subs = re.findall(r'M[^M]+', l['d'])
        sb = [_bbox(x) for x in subs]
        if len(subs) > 1 and all(x and x[3] - x[1] < 1.6 for x in sb) and \
                all(b_[0] - a_[2] > 2 for a_, b_ in zip(sorted(sb), sorted(sb)[1:])):
            for x, d_ in zip(sb, subs):                 # several fraction bars drawn as ONE path: one item each, so a long
                its.append(_Item('lines', dict(l, d=d_), x[0], x[1], x[2], x[3]))   # step can wrap between them (2014 MJ 21 q8)
            continue
        its.append(_Item('lines', l, b0[0], b0[1], b0[2], b0[3]))
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
    # a printed line group joined by one tall sign that is wider than our column is laid out line by line again
    # (scaling it shrank whole paragraphs: 2014 MJ 42 q1(e), round 30 - Dhruv: 'take the extra space, never shrink')
    split_ = []
    for ln in lines:
        ts_ = [i for i in ln['its'] if i.kind == 't']
        base_ = sorted({round(i.ref['y'], 0) for i in ts_ if i.ref.get('s', 11) >= 9})
        bands = []
        for y_ in base_:
            if bands and y_ - bands[-1][-1] < 6:
                bands[-1].append(y_)
            else:
                bands.append([y_])
        # two printed lines stay together only when a drawing joins them: a fraction bar between them, a root sign or
        # bracket reaching into both (2025 MJ 21 q15); a superscript alone never joins (2014 MJ 42 q1(d) overlapped)
        if len(bands) >= 2:
            dr_ = [i for i in ln['its'] if i.kind != 't']
            merged = [bands[0]]
            for b_ in bands[1:]:
                ya, yb = sum(merged[-1]) / len(merged[-1]), sum(b_) / len(b_)
                ta = [i for i in ts_ if i.ref.get('s', 11) >= 9 and min(abs(round(i.ref['y'], 0) - y_) for y_ in merged[-1]) < 0.6]
                tb_ = [i for i in ts_ if i.ref.get('s', 11) >= 9 and min(abs(round(i.ref['y'], 0) - y_) for y_ in b_) < 0.6]
                stacked = any(b.x0 > left + 8 and min(a.x1, b.x1) - max(a.x0, b.x0) > 0.5 * min(a.x1 - a.x0, b.x1 - b.x0)
                              for a in ta for b in tb_) and yb - ya < 18 and tb_ and min(b.x0 for b in tb_) > left + 8
                # (a denominator stands indented UNDER its numerator; a new printed line starts at the cell's left -
                #  round 30: splitting broke fractions in 2025 MJ 22 q15, 2021 FM 42 q9, 2019 ON 31 q8)
                if stacked or any((i.y1 - i.y0 < 1.6 and ya - 4 < i.y0 < yb - 1) or (i.y0 < ya - 2 and i.y1 > yb - 6) for i in dr_):
                    merged[-1] = merged[-1] + b_
                else:
                    merged.append(b_)
            bands = merged
        span_ = max(i.x1 for i in ln['its']) - min(i.x0 for i in ln['its'])
        if len(bands) >= 2 and span_ > width + 0.5:
            ys = [sum(b_) / len(b_) for b_ in bands]
            grp = {k_: [] for k_ in range(len(ys))}
            for it in ln['its']:
                yc = it.ref['y'] if it.kind == 't' else (it.y0 + it.y1) / 2 + 3
                grp[min(range(len(ys)), key=lambda k_: (0 if min(bands[k_]) - 12 <= yc <= max(bands[k_]) + 4 else 1,
                                                        abs(ys[k_] - yc)))].append(it)
            for k_ in range(len(ys)):
                if grp[k_]:
                    split_.append({'its': grp[k_], 'y0': min(i.y0 for i in grp[k_]), 'y1': max(i.y1 for i in grp[k_])})
        else:
            split_.append(ln)
    lines = split_
    lead = max(1.5, min(left - c0, PAD + 2))
    out, extra = [], 0.0
    # a paragraph printed over several lines (the printed column was wider than ours) is re-flowed as one: its lines are
    # joined when they hold only text, start at the same indent and the line before ran to the cell's right side (round 27,
    # 2014 MJ 62 q2(b): 'previous / numerator.' broken lines)
    def plain(ln):
        return all(i.kind == 't' for i in ln['its'])
    def open_end(ln):           # a printed line that stops mid-step ('... ÷ their', '... ='): the next line goes on with it
        last = max((i for i in ln['its'] if i.kind == 't'), key=lambda i: i.x1, default=None)   # (round 30, Dhruv: write a
        t_ = last.ref.get('t', '').strip() if last else ''                                   # step whole, not broken)
        return bool(re.search(r'[÷×+\-–=(]$', t_)) or t_ in ('their', 'of', 'for', 'and', 'or', 'by', 'to', 'the')
    k = 0
    while k < len(lines) - 1 and align != 'right':
        a, b = lines[k], lines[k + 1]
        lh_ = a['y1'] - a['y0']
        ax0, ax1 = min(i.x0 for i in a['its']), max(i.x1 for i in a['its'])
        bx0 = min(i.x0 for i in b['its'])
        first_b = min(b['its'], key=lambda i: i.x0).ref.get('t', '') if plain(b) else ''
        if plain(a) and plain(b) and abs(ax0 - bx0) < 3 and b['y0'] - a['y1'] < 0.6 * lh_ and ax1 > c1 - 0.3 * (c1 - c0) \
                and (ax1 - ax0) > width * 0.6 and (re.match(r'[a-z]', first_b) or open_end(a)) and not re.match(r'(or|and)$', first_b):
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
            tl_ = [i for i in first['its'] if i.kind == 't' and i.ref.get('s', 11) >= 9]
            lh_t = (max(i.y1 for i in tl_) - min(i.y0 for i in tl_)) if tl_ else lh
            pitch = max(pitch, lh_t + LGAP)      # (a superscript on the next printed line made the pitch smaller than a
            #                                      line: re-flowed rows overlapped, 2014 MJ 42 q1(d), round 30)
            x, row = 0.0, 0
            fy0_ = min(i.y0 for i in tl_) if tl_ else first['y0']
            for j, part in enumerate(ln['parts']):
                for ch in _chunks(part['its']):
                    w_ = ch['x1'] - ch['x0']
                    sp_ = 0.0 if x == 0 else 0.25 * 11.0
                    if x and x + sp_ + w_ > width + 0.5:
                        row += 1; x, sp_ = 0.0, 0.0
                    dx = n0 + lead + x + sp_ - ch['x0']
                    ptl = [i for i in part['its'] if i.kind == 't' and i.ref.get('s', 11) >= 9]
                    py0_ = min(i.y0 for i in ptl) if ptl else part['y0']      # the text top, not a superscript's
                    dy = extra + push(first['y0']) + (fy0_ + row * pitch) - py0_
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
        if multi and span_all > width + 0.5:           # too wide for one block: pieces that overlap in x stay together
            xc = []                                    # (a fraction, a root), the line wraps between them - never shrinks
            for it in sorted(ln['its'], key=lambda i: i.x0):   # (round 30, 2014 MJ 21 q8(b)(ii), 2025 MJ 22 q21(b))
                if xc and it.x0 < xc[-1]['x1'] - 0.3:
                    xc[-1]['its'].append(it); xc[-1]['x1'] = max(xc[-1]['x1'], it.x1)
                else:
                    xc.append({'its': [it], 'x0': it.x0, 'x1': it.x1})
            chunks = xc
        elif multi:                                    # two printed lines joined by a tall sign (a root over brackets, 2025 MJ
            chunks = [{'its': list(ln['its']), 'x0': chunks[0]['x0'], 'x1': chunks[-1]['x1']}]   # 21 q15): one block,
            #                                             never wrapped piece by piece (they were drawn on top of each other)
        if any(ch['x1'] - ch['x0'] > width + 0.5 for ch in chunks):    # one piece wider than the column: split it where
            nc = []                                                     # nothing overlaps in x (never shrink, round 30)
            for ch in chunks:
                if ch['x1'] - ch['x0'] <= width + 0.5:
                    nc.append(ch); continue
                for it in sorted(ch['its'], key=lambda i: i.x0):
                    if nc and nc[-1].get('_s') and it.x0 < nc[-1]['x1'] - 0.3:
                        nc[-1]['its'].append(it); nc[-1]['x1'] = max(nc[-1]['x1'], it.x1)
                    else:
                        nc.append({'its': [it], 'x0': it.x0, 'x1': it.x1, '_s': True})
                if nc and nc[-1].get('_s'):
                    nc[-1]['_s'] = False
            chunks = nc
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
    A = ANSWER_SHARE * (W - QW - MW) if ncols == 4 else W - QW - MW   # (Dhruv, round 29: Answer wider than Partial Marks)
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
        if by[c] and not (c == 3 and ncols == 3) and not ((_picture_cell(by[c]) or _has_table(by[c]) or u['src']['page'] in CTX.get('broken', ()))
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
        if by[c] and u['src']['page'] not in CTX.get('broken', ()) and _has_table(by[c]):
            # a table: everything inside its rules is one rigid block of its own lines, shading and text; text above / below
            # it is laid out as usual (round 29: tables as lines + text, never a picture; dotted rows split the old cluster)
            rl = [i for i in by[c] if i.kind == 'lines' and ((i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 8) or (i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 15)
                                                             or i.ref.get('fill', '').lower() not in ('', '#000000', '#ffffff', '#231f20'))]
            vl_ = [i for i in rl if i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 8]
            if len(vl_) >= 3:       # the grid = its verticals and the rules / shading between them; a fraction bar higher up
                gy0, gy1 = min(i.y0 for i in vl_) - 2, max(i.y1 for i in vl_) + 2   # in the cell is no table rule (round 30:
                gx0, gx1 = min(i.x0 for i in vl_) - 2, max(i.x1 for i in vl_) + 2   # sentences above 2025 MJ 62 q4(b)'s table)
                rl = [i for i in rl if (gy0 - 10 <= (i.y0 + i.y1) / 2 <= gy1 + 10 and i.x0 >= gx0 - 3 and i.x1 <= gx1 + 3)
                      or (gy0 <= (i.y0 + i.y1) / 2 <= gy1 and i.x1 > gx0 and i.x0 < gx1) or
                      (gy0 - 40 < (i.y0 + i.y1) / 2 < gy1 + 40 and i.x0 >= gx0 - 3 and i.x1 <= gx1 + 3
                       and i.x1 - i.x0 > 0.8 * (gx1 - gx0))]   # a full-width rule of a row without column rules
            tx0, ty0 = min(i.x0 for i in rl) - 1, min(i.y0 for i in rl) - 1
            tx1, ty1 = max(i.x1 for i in rl) + 1, max(i.y1 for i in rl) + 1
            blk = [i for i in by[c] if tx0 <= (i.x0 + i.x1) / 2 <= tx1 and ty0 <= (i.y0 + i.y1) / 2 <= ty1]
            blk += [i for i in by[c] if i not in blk and i.kind == 't' and (i.ref.get('dir') or [1, 0])[0] < 0.3
                    and ty0 - 3 <= (i.y0 + i.y1) / 2 <= ty1 + 3 and tx0 - 30 <= i.x0 and i.x1 <= tx0 + 2]
            # (rotated row labels beside the table ('1 neg') belong to it: round 30, 2021 FM 52 q3)
            for _ in range(3):      # an unruled row printed right against the table, inside its width ('3 + 4 + 5 + 6 = 18'
                yb0, yb1 = min(i.y0 for i in blk), max(i.y1 for i in blk)   # above, '-3 + -4 ... = -18' below: 52 q3(b))
                add = [i for i in by[c] if i not in blk and i.kind == 't' and tx0 - 2 <= i.x0 and i.x1 <= tx1 + 2
                       and (yb0 - 16 < i.y1 <= yb0 + 1 or yb1 - 1 <= i.y0 < yb1 + 16)]
                if not add:
                    break
                rowy = {round(i.ref['y']) for i in add}
                colx = {round(i.x0) for i in blk if i.kind == 't'}
                if any(re.fullmatch(r'[A-Za-z]{4,}[.,]?', i.ref.get('t', '')) for i in add) or any(len([i for i in add if round(i.ref['y']) == y_]) < 3 or
                       sum(1 for i in add if round(i.ref['y']) == y_ and any(abs(i.x0 - cx) <= 3 for cx in colx)) < 3
                       for y_ in rowy):     # (its cells line up with the table's columns: sentences above a small
                    #                          table were pulled in and drawn over the text, 2025 MJ 62 q4(b), round 30)
                    break           # only whole table-like rows (several cells), never a sentence under it
                blk += add
            rest = [i for i in by[c] if i not in blk]
            shift, tb = push_for(c)(ty0), None
            if rest:
                placed, tb, _ = _cell(rest, cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1], push=push_for(c))
                for it, dx, dy, k, x0 in placed:
                    _emit(v, it, dx, dy, k, x0)
                ab = [p_ for p_ in placed if p_[0].y1 <= ty0 + 1]
                shift = max([shift] + [p_[2] for p_ in ab])
            bx0, bx1 = min(i.x0 for i in blk), max(i.x1 for i in blk)
            by0_, by1_ = min(i.y0 for i in blk), max(i.y1 for i in blk)
            if rest:                # the table starts under the text above it as WE placed it (re-flowed text can end
                ab_b = [p_[0].ref['y'] + 0.25 * p_[0].ref.get('s', 11) + p_[2] for p_ in placed if (p_[0].y0 + p_[0].y1) / 2 < ty0 and p_[0].kind == 't']   # lower than
                if ab_b:            # printed: its last line ran into the table's top rule, 2025 MJ 62 q4(b), round 31)
                    shift = max(shift, max(ab_b) + 2.5 - by0_)
            room = ours[c][1] - ours[c][0] - 2 * PAD
            k_ = min(1.0, room / max(1.0, bx1 - bx0))
            thin = lambda i: i.kind == 'lines' and min(i.x1 - i.x0, i.y1 - i.y0) < 1.6
            blk = [i for i in blk if not thin(i)] + [i for i in blk if thin(i)]   # rules over the shading (round 30)
            _emit_block(v, blk, bx0, by0_, ours[c][0] + PAD, by0_ + shift, k_)
            bottoms.append(max(by0_ + shift + (by1_ - by0_) * k_ + 3.0, tb or 0))
            continue
        if (_picture_cell(by[c]) or u['src']['page'] in CTX.get('broken', ())) and by[c] and CTX.get('pdf'):   # a diagram / shaded sketch in the cell: its printed picture (pattern 78)
            tbx =[(t.x0 - 1.5, t.y0 - 1.5, t.x1 + 1.5, t.y1 + 1.5) for t in by[c] if t.kind == 't']
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
            head = [t_ for t_ in by[c] if t_.kind == 't' and (
                        (t_.y0 < py0 + 3 and t_.y1 > py0 - 0.5 and any(i.y0 < t_.y1 for i in pasted)) or
                        any(i.x0 - 2 <= t_.x0 and t_.x1 <= i.x1 + 2 and i.y0 - 0.5 < t_.y1 and t_.y0 < i.y0 + 0.3 * (i.y1 - i.y0)
                            for i in pasted) or
                        (t_ not in inpic and t_.x0 < px1 and t_.x1 > px0 and t_.y1 > py0 and t_.y0 < py0 + 0.3 * (py1 - py0)) or
                        (t_.y1 <= py0 + 3 and len(' '.join(o.ref['t'] for o in by[c] if o.kind == 't'
                                                         and abs(o.ref['y'] - t_.ref['y']) < 2)) > 8))]
            # (and a heading of OUR text over the top of a DRAWN graph: drawn twice, 2019 ON 41 q11, 43 q3, round 30)
            #   (also a heading INSIDE the top of a pasted graph: 'Correct sketch'
            #                                       drawn twice, 2021 FM 62 q9(d)(ii), round 29)   # a text line a pasted picture lies over (never a drawn box,
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
            drawn_ = (not broken_pg and not any(i.kind in ('images', 'figs') for i in inpic)
                      and not _clash([i for i in inpic if i.kind == 't'])
                      and not any(i.kind == 'lines' and (i.ref.get('fill') or '').lower() not in ('', '#000000', '#ffffff', '#231f20')
                                  and (i.x1 - i.x0) * (i.y1 - i.y0) > 30 for i in inpic))
            # (shaded areas stay the printed picture: their transparency is not in our line data - 2014 MJ 52 q1 turned dark)
            if drawn_ and not _is_table(inpic):          # a graph / sketch the PDF draws as lines: drawn again by us as sharp
                bx0, by0 = min(i.x0 for i in inpic), min(i.y0 for i in inpic)   # lines, a little darker (Dhruv, round 30:
                bx1, by1 = max(i.x1 for i in inpic), max(i.y1 for i in inpic)   # 'faint diagrams - redraw + darken')
                room = ours[c][1] - ours[c][0] - 2 * PAD
                k_ = max(0.6, min(1.0, room / max(1.0, bx1 - bx0)))
                x_at = ours[c][0] + PAD + (max(0.0, bx0 - cells_src[c][0] - PAD) if k_ == 1.0 else 0.0)
                x_at = min(x_at, ours[c][1] - PAD - (bx1 - bx0) * k_)
                n0_ = len(v['lines'])
                inpic = _chain(inpic)
                _emit_block(v, inpic, bx0, by0, x_at, by0 + shift, k_, table=False)
                area_ = {}              # colours that fill an AREA (shading drawn in thin strips, 2014 MJ 52 q1) keep their tone
                for i in inpic:
                    if i.kind == 'lines' and i.ref.get('fill'):
                        area_[i.ref['fill'].lower()] = area_.get(i.ref['fill'].lower(), 0) + (i.x1 - i.x0) * (i.y1 - i.y0)
                keep_ = {c_ for c_, a_ in area_.items() if a_ > 150}
                grid_ = sum(1 for l_ in v['lines'][n0_:] if (l_.get('stroke') or '').lower() in ('#c0c0c0', '#bfbfbf', '#d9d9d9', '#a6a6a6', '#808080'))
                nb = [b_ for b_ in (_bbox(l_['d']) for l_ in v['lines'][n0_:] if l_.get('stroke')) if b_]
                fx0, fy0 = min(b_[0] for b_ in nb) if nb else 0, min(b_[1] for b_ in nb) if nb else 0
                fx1, fy1 = max(b_[2] for b_ in nb) if nb else 0, max(b_[3] for b_ in nb) if nb else 0
                for l_ in v['lines'][n0_:]:
                    b_ = _bbox(l_['d'])
                    if grid_ >= 6 and l_.get('stroke') and b_ and (
                            (b_[2] - b_[0] < 0.5 and min(abs(b_[0] - fx0), abs(b_[0] - fx1)) < 0.8 and b_[3] - b_[1] > 0.8 * (fy1 - fy0)) or
                            (b_[3] - b_[1] < 0.5 and min(abs(b_[1] - fy0), abs(b_[1] - fy1)) < 0.8 and b_[2] - b_[0] > 0.8 * (fx1 - fx0))):
                        l_['stroke'] = '#b0b0b0'; l_['sw'] = 0.25     # the chart's frame stays light like its grid (Dhruv,
                        continue                                        # round 31: black box next to the y-axis, 2019 ON 41 q11)
                    if (l_.get('fill') or '').lower() not in keep_:
                        _darken(l_)
                bottoms.append(max(by0 + shift + (by1 - by0) * k_ + 3.0, tb or 0))
                continue
            if not broken_pg and _is_table(inpic):       # a table: its own lines + text, one rigid block (round 29)
                bx0, by0 = min(i.x0 for i in inpic), min(i.y0 for i in inpic)
                bx1, by1 = max(i.x1 for i in inpic), max(i.y1 for i in inpic)
                room = ours[c][1] - ours[c][0] - 2 * PAD
                k_ = min(1.0, room / max(1.0, bx1 - bx0))
                _emit_block(v, inpic, bx0, by0, ours[c][0] + PAD, by0 + shift, k_)
                bottoms.append(max(by0 + shift + (by1 - by0) * k_ + 3.0, tb or 0))
                continue
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
             and (i.x1 - i.x0) > 30 and (i.y1 - i.y0) > 30 and not _root_sign(i)]
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


from PIL import Image


def _erase_bands(im):
    """Whiten runs of >= 10 rows (or columns) in which >= 85 % of the pixels are one light tone (200-254): the tinted
    band of a pasted screenshot. Thin grid lines (1-3 px) and curves stay."""
    import numpy as np
    a = np.array(im)
    g = a[:, :, :3].astype(int).mean(axis=2)
    for _ in range(3):              # a light background tone covering >= 10 % of the picture (a screenshot's grey paper)
        light = np.round(g[(g >= 200) & (g <= 254)])
        if not light.size:
            break
        v, n = np.unique(light, return_counts=True)
        if n.max() < 0.10 * g.size:
            break
        t = v[n.argmax()]
        edge = np.concatenate([g[:3].ravel(), g[-3:].ravel(), g[:, :3].ravel(), g[:, -3:].ravel()])
        if (np.abs(edge - t) <= 3).mean() < 0.3:
            break               # a tone that does not reach the picture's edges is SHADING, not paper (2025 MJ 11 q16)
        a[np.abs(g - t) <= 3, :3] = 255
        g = a[:, :, :3].astype(int).mean(axis=2)
    for axis in (0, 1):
        G = g if axis == 0 else g.T
        uni = []
        for row in G:
            q = np.round(row / 4)
            v, n = np.unique(q, return_counts=True)
            j = n.argmax()
            uni.append(v[j] * 4 if (n[j] >= 0.85 * len(row) and 200 <= v[j] * 4 <= 254) else None)
        i = 0
        while i < len(uni):
            if uni[i] is None:
                i += 1
                continue
            j = i
            while j < len(uni) and uni[j] is not None and abs(uni[j] - uni[i]) <= 8:
                j += 1
            if j - i >= 10:
                for r in range(i, j):
                    line = G[r]
                    m = np.abs(line - uni[r]) <= 6
                    if axis == 0:
                        a[r, m, :3] = 255
                    else:
                        a[m, r, :3] = 255
                g = a[:, :, :3].astype(int).mean(axis=2)
                G = g if axis == 0 else g.T
            i = j
    im.paste(Image.fromarray(a))


def _chain(items):
    """Join a curve printed as hundreds of tiny strokes (end of one = start of the next) into one polyline: drawn one by
    one they showed as a dashed line (2025 MJ 42 q11, round 30)."""
    segs, rest = [], []
    for i in items:
        m = re.fullmatch(r'M(-?[\d.]+) (-?[\d.]+)L(-?[\d.]+) (-?[\d.]+)', (i.ref.get('d') or '').strip()) if i.kind == 'lines' else None
        if m and i.ref.get('stroke') and i.x1 - i.x0 < 3 and i.y1 - i.y0 < 3:
            segs.append((i, [float(g) for g in m.groups()]))
        else:
            rest.append(i)
    if len(segs) < 20:
        return items
    out, cur = [], None
    for i, (a, b, c, d) in segs:
        if cur and cur['ref']['stroke'] == i.ref['stroke'] and abs(cur['end'][0] - a) < 0.06 and abs(cur['end'][1] - b) < 0.06:
            cur['pts'].append((c, d)); cur['end'] = (c, d)
        else:
            cur = {'ref': i.ref, 'pts': [(a, b), (c, d)], 'end': (c, d)}
            out.append(cur)
    for p in out:
        xs, ys = [q[0] for q in p['pts']], [q[1] for q in p['pts']]
        d = 'M%.2f %.2f' % p['pts'][0] + ''.join('L%.2f %.2f' % q for q in p['pts'][1:])
        rest.append(_Item('lines', dict(p['ref'], d=d), min(xs), min(ys), max(xs), max(ys)))
    return rest


def _clash(ts):
    """Words printed over each other (a broken text layer)."""
    ts = [i for i in ts if i.x1 - i.x0 > 2]
    return sum(1 for k, a in enumerate(ts) for b in ts[k + 1:]
               if abs(a.ref['y'] - b.ref['y']) < 3.0 and min(a.x1, b.x1) - max(a.x0, b.x0) > 0.4 * min(a.x1 - a.x0, b.x1 - b.x0)) >= 2


def _dark_hex(h, f=0.62):
    h = h.lstrip('#')
    if len(h) != 6:
        return '#' + h
    r, g, b = (int(h[k:k + 2], 16) for k in (0, 2, 4))
    if min(r, g, b) > 250:
        return '#' + h
    return '#%02x%02x%02x' % tuple(int(c * f) for c in (r, g, b))


def _darken(l):
    """A thin line / stroke of a redrawn graph: darker colour, at least 0.6 pt (faint grey grids and pale curves were
    hard to see, round 30). Filled areas (shading) keep their tone."""
    b = _bbox(l['d'])
    thin = b and min(b[2] - b[0], b[3] - b[1]) < 2.0
    if l.get('stroke'):
        h_ = l['stroke'].lstrip('#')
        ch_ = [int(h_[k:k + 2], 16) for k in (0, 2, 4)] if len(h_) == 6 else [0, 0, 0]
        light = min(ch_) >= 0x90 and max(ch_) - min(ch_) < 24      # light GREY = grid; a coloured line is a curve
        if light:               # a light grid stays light, just visible (round 30: grids turned black)
            l['stroke'] = _dark_hex(l['stroke'], 0.85)
            l['sw'] = max(l.get('sw', 0.3), 0.25)
        else:
            l['stroke'] = _dark_hex(l['stroke'])
            l['sw'] = max(l.get('sw', 0.5), 0.6)
    if l.get('fill') and thin:
        l['fill'] = _dark_hex(l['fill'])


def _root_sign(i):
    """A drawn root sign (any size): a horizontal bar along the TOP of the path covering most of its width, the rest
    slanted strokes below-left of it. A tall nested root (sqrt of a fraction, 33 pt) passed as a sketch and the cell
    became a cut picture (round 30, 2025 MJ 21 q15)."""
    pts = [(float(a), float(b)) for a, b in re.findall(r'[ML]\s*(-?[\d.]+)[ ,](-?[\d.]+)', i.ref.get('d', ''))]
    if len(pts) < 4 or 'C' in i.ref.get('d', ''):
        return False
    top = [p for p in pts if p[1] <= i.y0 + 1.0]
    bar = (max(p[0] for p in top) - min(p[0] for p in top)) if top else 0
    return bar > 0.55 * (i.x1 - i.x0) and min(p[0] for p in top) > i.x0 + 2 and max(p[0] for p in top) >= i.x1 - 1


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
    runs = []                   # rules printed as dashes (2014 MJ 62 p4) are judged as whole runs (round 30)
    for b_ in sorted((x for x in (_bbox(l['d']) for l in u.get('lines', [])) if x), key=lambda q: (round(q[1], 0), q[0])):
        if b_[3] - b_[1] >= 1.6:
            continue
        if runs and abs(runs[-1][1] - b_[1]) < 0.5 and b_[0] - runs[-1][2] < 2.0:
            runs[-1] = (runs[-1][0], runs[-1][1], max(runs[-1][2], b_[2]), max(runs[-1][3], b_[3]))
        else:
            runs.append(tuple(b_))
    vr = []
    for b_ in sorted((x for x in (_bbox(l['d']) for l in u.get('lines', [])) if x), key=lambda q: (round(q[0], 0), q[1])):
        if b_[2] - b_[0] >= 1.6:
            continue
        if vr and abs(vr[-1][0] - b_[0]) < 0.5 and b_[1] - vr[-1][3] < 2.0:
            vr[-1] = (vr[-1][0], vr[-1][1], max(vr[-1][2], b_[2]), max(vr[-1][3], b_[3]))
        else:
            vr.append(tuple(b_))
    for b_ in vr:               # a column rule inside the picture's sides: the picture stops before it
        if b_[3] - b_[1] > 0.6 * u['h'] and x0 < (b_[0] + b_[2]) / 2 < x1 and \
                min(abs((b_[0] + b_[2]) / 2 - src[0]), abs((b_[0] + b_[2]) / 2 - src[1])) < 5:   # (an axis is no rule)
            if (b_[0] + b_[2]) / 2 > (x0 + x1) / 2:
                x1 = b_[0] - 0.4
            else:
                x0 = b_[2] + 0.4
    for b_ in runs:                                      # never over the printed table's own row rules (a full-width line
        l = None                                         # under a Venn picture, round 29 2021 FM 32 q9)
        if b_ and b_[3] - b_[1] < 1.6 and (b_[2] - b_[0] > 0.8 * u['w'] or
                                           (b_[0] <= src[0] + 3 and b_[2] >= src[1] - 3)):   # (or the cell's own rule)
            if y0 < b_[1] < y1 and b_[1] > (y0 + y1) / 2:
                y1 = b_[1] - 0.4
            elif y0 < b_[3] < y1 and b_[3] < (y0 + y1) / 2:
                y0 = b_[3] + 0.4
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
    thr = 245
    if any(i.kind in ('images', 'figs') for i in items):
        thr = 252                   # a pasted graph's grid is drawn in 246-252 (2014 MJ 31 q15): keep it
        _erase_bands(im)            # a pasted screenshot's light grey BAND (>= 10 px of one tone) is paper (2021 FM 32 q9);
        # its light grids and pale curves are not (a global 229 cut erased them: 2014 MJ 31 q15, round 30)
    im.putdata([(a, b_, c, 0 if a > thr and b_ > thr and c > thr else 255) for a, b_, c, _ in im.getdata()])   # near-white
    if thr == 252:                  # pasted: a light SMOOTH area (gradient shadow) is paper; a light thin line is not
        A = np.array(im); G = A[:, :, :3].astype(int).mean(axis=2)
        P = np.pad(G, 2, mode='edge'); hi = lo = G.copy()
        for dy in range(5):
            for dx in range(5):
                S = P[dy:dy + G.shape[0], dx:dx + G.shape[1]]; hi = np.maximum(hi, S); lo = np.minimum(lo, S)
        A[(G >= 238) & (hi - lo <= 4), 3] = 0
        im = Image.fromarray(A)
    # (232 erased light grey graph grids, round 28 - 245 kept: the grey band of 2021 FM 32 q9 is printed so)
    if True:                        # raise contrast of what stays (faint screenshots, Dhruv round 30): ink x 2.4
        A0 = np.array(im).astype(int)
        G0 = A0[:, :, :3].mean(axis=2)
        ink = (A0[:, :, 3] > 0) & (G0 < 245)
        er = ink.copy()                 # thick ink (shaded regions, filled shapes) keeps its tone; only thin lines and
        for dy_ in range(-3, 4):        # curves get darker (round 30: a grey Venn shading turned black, 2014 MJ 31 q10)
            for dx_ in range(-3, 4):
                er &= np.roll(np.roll(ink, dy_, 0), dx_, 1)
        thick = er.copy()
        for dy_ in range(-3, 4):
            for dx_ in range(-3, 4):
                thick |= np.roll(np.roll(er, dy_, 0), dx_, 1)
        op = ink & ~thick
        for ch in range(3):
            c_ = A0[:, :, ch]
            c_[op] = np.clip(255 - (255 - c_[op]) * 2.4, 0, 255)
        im = Image.fromarray(A0.astype('uint8'))
    import numpy as _np
    arr = _np.array(im)
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


def _is_table(items):
    """A ruled / shaded table of text (no curve, no pasted picture): kept as its own lines, shading and text (Dhruv,
    round 29: 'it can be done using lines and box and text, no need of image', as in physics)."""
    if any(i.kind in ('images', 'figs') for i in items):
        return False
    if sum(1 for i in items if i.kind == 'lines' and i.x1 - i.x0 < 3 and i.y1 - i.y0 < 3 and i.ref.get('stroke')) > 40:
        return False        # a curve drawn as many tiny strokes: a graph on a grid, not a table (2025 MJ 42 q11, round 30)
    for i in items:         # a coloured line or a polyline of many points is a curve: a graph, not a table (2014 MJ 42 q2)
        st = (i.ref.get('stroke') or '').lstrip('#') if i.kind == 'lines' else ''
        if len(st) == 6:
            ch = [int(st[k:k + 2], 16) for k in (0, 2, 4)]
            if max(ch) - min(ch) > 40:
                return False
        if i.kind == 'lines' and (i.ref.get('d') or '').count('L') > 6 and i.x1 - i.x0 > 5 and i.y1 - i.y0 > 5:
            return False
    ln = [i for i in items if i.kind == 'lines']
    if any('C' in i.ref.get('d', '') and (i.x1 - i.x0) > 6 and (i.y1 - i.y0) > 6 for i in ln):
        return False                                     # a curve: a graph or Venn diagram
    if any(_slanted(i.ref.get('d', '')) and (i.x1 - i.x0) > 20 and (i.y1 - i.y0) > 20 for i in ln):
        return False                                     # a long slanted line: a sketch
    gv = [i for i in ln if i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 8]
    gh = [i for i in ln if i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 15]
    shaded = [i for i in ln if i.ref.get('fill', '').lower() not in ('', '#000000', '#ffffff', '#231f20')]
    ts = [i for i in items if i.kind == 't']
    return len(ts) >= 3 and ((len(gv) >= 2 and len(gh) >= 2) or bool(shaded))


def _has_table(items):
    """The cell holds a ruled table (>= 3 vertical and >= 3 horizontal rule pieces, text inside)."""
    ln = [i for i in items if i.kind == 'lines']
    gv = [i for i in ln if i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 8]
    gh = [i for i in ln if i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 15]
    if not (len(gv) >= 3 and len(gh) >= 3 and _is_table(items)):
        return False
    x0, x1 = min(i.x0 for i in gv + gh), max(i.x1 for i in gv + gh)
    import collections
    rows = collections.defaultdict(float)             # rule length per height: a table's row rules run most of its width
    for i in gh:                                      # (boxes around numbers, 2019 ON 51 q1(a)(ii), are no table)
        rows[round(i.y0)] += i.x1 - i.x0
    return sum(1 for w in rows.values() if w > 0.6 * (x1 - x0)) >= 2


def _emit_block(v, items, ox, oy, nx, ny, k, table=True):
    """Place items as one rigid block: (ox, oy) -> (nx, ny), scaled k both ways (a table is never wrapped)."""
    from ms_layout import _map_path
    hr = [i for i in items if i.kind == 'lines' and i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 20] if table else []
    # (border clean-up only for tables: a curve drawn as tiny segments lost them, 2025 MJ 42 q11(a) round 30)
    drop = set()                # a rule printed double (two lines < 2.5 pt apart, same run): one line (Dhruv, round 30:
    for a in hr:                # 'why double edge at top of the table', 2021 FM 52 q4)
        for b in hr:
            if a is not b and id(a) not in drop and 0 < b.y0 - a.y0 < 2.5 and abs(a.x0 - b.x0) < 3 and abs(a.x1 - b.x1) < 3:
                drop.add(id(b))
    items = [i for i in items if id(i) not in drop]
    # a Word 'double' border prints tiny corner pieces and leaves a gap between the top rule and the column rules: the
    # pieces go and the column rules reach up to the rule (2021 FM 52 q4, round 30: 'why double edge at top')
    hr = [i for i in items if i.kind == 'lines' and i.y1 - i.y0 < 1.6 and i.x1 - i.x0 > 20]
    out_ = []
    for i in items:
        if i.kind == 'lines' and i.x1 - i.x0 < 2 and i.y1 - i.y0 < 2 and any(abs(i.y0 - h.y1) < 2.2 or abs(i.y0 - h.y0) < 2.2 for h in hr):
            continue
        if i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 5 and not i.ref.get('stroke'):
            top = [h for h in hr if 0 < i.y0 - h.y1 < 2.2 and h.x0 - 1 <= i.x0 <= h.x1 + 1]
            if top:
                y0n = top[0].y0
                i = _Item('lines', dict(i.ref, d=f'M{i.x0:.2f} {y0n:.2f}H{i.x1:.2f}V{i.y1:.2f}H{i.x0:.2f}Z'), i.x0, y0n, i.x1, i.y1)
        out_.append(i)
    items = out_
    fx = lambda x: nx + (x - ox) * k
    fy = lambda y: ny + (y - oy) * k
    for it in items:
        if it.kind == 't':
            t = dict(it.ref)
            t['x'] = round(fx(t['x']), 2); t['y'] = round(fy(t['y']), 2)
            t['s'] = round(t.get('s', 11) * k, 2); t['w'] = round(t['w'] * k, 2)
            v['text'].append(t)
        elif it.kind == 'lines':
            l = dict(it.ref)
            l['d'] = _map_path(l['d'], fx, fy)
            if 'sw' in l:
                l['sw'] = round(l['sw'] * k, 2)
            v['lines'].append(l)
        else:
            g = dict(it.ref)
            g['x'] = round(fx(g['x']), 2); g['y'] = round(fy(g['y']), 2)
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
