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
import os
import re

W = 523.0
QW, MW = 44.0, 44.0
PAD = 5.0
ANSWER_SHARE = 0.6        # Answer : Partial Marks = 60 : 40 of the room left by Q and Marks (MS_TABLE_RULES 24, round 29)
FIVE_SHARES = (0.4, 0.3, 0.3)   # 2026 MJ: Q | Answer | Marks | Partial Marks | Guidance - Answer : Partial : Guidance of the room
                                # left by Q and Marks (Dhruv, M1 2026-11-16, MS_TABLE_RULES 31)
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
    ok = (2, 3, 4) if CTX.get('five') else (2, 3)        # 4 inner rules only in a scheme with a Guidance column (M1)
    inner = [x for x, c in xs if c > 0.6 * u['h'] and 20 < x < u['w'] - 20]
    if len(inner) not in ok and xs:                  # a grid drawn in the answer (2014 MJ 22 q2) has tall lines too:
        top = max(c for _, c in xs)                      # the table's own rules run the full height
        inner = [x for x, c in xs if c > 0.97 * top and 20 < x < u['w'] - 20]
    return inner if len(inner) in ok else None


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
        #  (a large equation-font letter ('m' at 16 pt in 'm²') reached into the next line and joined it: words of that
        #   line moved to another paragraph, 2021 ON 63 q1(c), M2 reasons - its descent counts as normal text's)
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
        if run and abs((run[-1][0][1] + run[-1][0][3]) / 2 - (b[1] + b[3]) / 2) < 0.4 and b[0] - max(r[0][2] for r in run) < 1.5 \
                and b[2] >= min(r[0][0] for r in run) - 1.5:    # (never a piece far LEFT of the run: two fraction bars 0.06 pt
            #   apart in height in Answer and Partial Marks became one 'rule' over the Marks column and were dropped, M1)
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
    vlong_in = [q_ for q_ in (_bbox(l_['d']) for l_ in u.get('lines', [])) if q_ and q_[2] - q_[0] < 1.3 and q_[3] - q_[1] > 6
                and not any(abs((q_[0] + q_[2]) / 2 - e) < 2.5 for e in edges + [0.5, u['w'] - 0.5])]
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
        one_end_tbl = b[3] - b[1] < 1.3 and not (any(b[0] - 3 <= e <= b[0] + 3 for e in edges + [0, u['w']])
                                                 and any(b[2] - 3 <= e <= b[2] + 3 for e in edges + [0, u['w']])) \
            and sum(1 for q_ in vlong_in if b[0] + 3 < q_[0] < b[2] - 3 and q_[1] - 1 <= b[1] <= q_[3] + 1) >= 2
        #   (a table printed flush with the cell's left border: its rules start at the edge, end inside the column and
        #    its own column rules cross them - table rules, not sub-row rules; 2023 FM 62 q1/q2 fell apart, M2)
        if not one_end_tbl and b[3] - b[1] < 1.3 and b[2] - b[0] > 30 and any(b[0] - 3 <= e <= b[0] + 3 or b[2] - 3 <= e <= b[2] + 3 for e in edges + [0, u['w']]):
            if 3.0 < b[1] < u['h'] - 3.0 and b[0] > edges[0] - 3:
                CTX.setdefault('subrules', []).append((b[0], (b[1] + b[3]) / 2, b[2]))   # redrawn by layout_row (round 32)
            continue                                    # a row / sub-row rule running between column rules
        if b[3] - b[1] < 1.3 and b[2] - b[0] > 0.8 * u['w']:
            continue
        if b[3] - b[1] > 0.9 * u['h'] and b[2] - b[0] > 0.9 * u['w']:
            continue                                    # a background box
        inner_ = b[3] - b[1] < 1.6 and b[2] - b[0] > 20 and not any(abs(b[0] - e) < 3 or abs(b[2] - e) < 3 for e in edges + [0, u['w']]) \
            and sum(1 for l2 in u.get('lines', []) if (lambda q: q and q[2] - q[0] < 1.3 and b[0] - 1 <= q[0] <= b[2] + 1
                                                       and q[1] <= b[3] + 1 and q[3] > b[1] + 6)(_bbox(l2['d']))) >= 2
        #   (a table printed at the very top of its row: its top edge lies inside the column, its column rules hang under
        #    it - the table's own edge, not the row's rule; without it the table lost its top and kept stubs, 2022 FM 52 q4)
        if not inner_ and ((b[3] - b[1] < 3.0 and (b[1] < 3.0 or b[3] > u['h'] - 3.0) and b[2] - b[0] > 20) or b[3] <= 3.0 or b[1] >= u['h'] - 3.0):   # the row's own top / bottom rule, or the edge of the header's shading poking in (2019 ON 63 q6, round 28)
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
    import collections as _c_
    _sz = _c_.Counter(round(i.ref.get('s', 11), 1) for i in items if i.kind == 't')
    base = max([s_ for s_, n_ in _sz.items() if n_ >= 0.2 * sum(_sz.values())] or [11])
    #  (the cell's normal size, not its largest letter: one 16 pt equation-font 'm' made every 11 pt line 'small raised
    #   text' that joined the line above - 'give a' moved paragraphs, 2021 ON 63 q1(c), M2 reasons)
    def small(b):
        ts = [i for i in b['its'] if i.kind == 't']
        return ts and all(i.ref.get('s', 11) < 0.85 * base for i in ts)
    k = 0
    while k < len(rows) - 1:
        a, b = rows[k], rows[k + 1]
        op = a.get('open')          # under a fraction bar: only a band that lies within the bar's width (its denominator)
        under = bool(op) and all(op[0] - 2 <= i.x0 and i.x1 <= op[1] + 2 for i in b['its'])
        # a tall bracket printed as glyph pieces (top / extender / bottom) is one stack: its top piece's line and the line
        # of its lower pieces are one printed line (the pieces' boxes do not overlap; pattern 240: '(x / -3)' torn apart,
        # 2023 MJ 32 q8(c), 2026 MJ 11 q18(b), 2026 MJ 22 q6)
        brk_ = any(i.kind == 't' and i.ref.get('t') in '⎛⎜⎞⎟⎡⎢⎤⎥' and abs(i.y1 - a['y1']) < 3 and any(
            j.kind == 't' and j.ref.get('t') in '⎜⎝⎟⎠⎢⎣⎥⎦' and abs(j.x0 - i.x0) < 1.5 and 0 <= j.y0 - i.y1 < 3
            for j in b['its']) for i in a['its'])
        if (drawn(a) or drawn(b) or small(a) or under or brk_) and b['y0'] - a['y1'] < 4.0:
            # a band that took a drawing-only band at its bottom (a fraction bar under the numerator) also takes the band
            # right under it (the denominator) - M1 2026 MJ 42 q9: '2(3)' fell out of its fraction and moved down
            a['open'] = drawn(b) and not drawn(a) and (min(i.x0 for i in b['its']), max(i.x1 for i in b['its']))
            a['its'] += b['its']; a['y1'] = max(a['y1'], b['y1']); del rows[k + 1]
            continue
        k += 1
    return rows


def _brk_join(ch, it):
    """A tall bracket made of glyph pieces never ends a wrap piece on its own: an opening bracket takes what follows it,
    a closing bracket joins what is before it (pattern 240: 'Allow ... = (' and '4 / -3)' on two lines, 2026 MJ 22 q6)."""
    if it.x0 - ch['x1'] >= 2 * GAP:          # bracket glyphs sit a little apart from their contents (1.9 pt)
        return False
    if it.kind == 't' and it.ref.get('t') in '⎞⎟⎠⎤⎥⎦':
        return True
    last_ = max(ch['its'], key=lambda i: i.x1)
    return last_.kind == 't' and last_.ref.get('t') in '⎛⎜⎝⎡⎢⎣'


def _chunks(its):
    """Unbreakable pieces of one line: ink closer than a word space, or stacked (x-overlapping) pieces."""
    out = []
    for it in sorted(its, key=lambda i: i.x0):
        if out and (it.x0 - out[-1]['x1'] < GAP or _brk_join(out[-1], it)):
            out[-1]['its'].append(it); out[-1]['x1'] = max(out[-1]['x1'], it.x1)
        else:
            out.append({'its': [it], 'x0': it.x0, 'x1': it.x1})
    return out


def _rootish(i):
    d = i.ref.get('d', '')
    return i.y1 - i.y0 < 30 and i.x1 - i.x0 < 400 and ('L' in d or 'l' in d) and not i.ref.get('fill') == '#ffffff' and \
        _slanted(d)


def _cell(items, c0, c1, n0, n1, align='left', push=None, growth=None):
    """Lay the items of one printed cell [c0, c1] into our column [n0, n1]. Returns (placed pieces, bottom y, top y)."""
    if not items:
        return [], None, None
    push = push or (lambda y: 0.0)
    # a white box behind the printed text (the cell's own background) wider than our column is no ink: kept, it made the
    # text's piece 'too wide' and shrank the marks / partial marks to 70-88 % (2020 MJ 31 q11(a)(i) '2', round 37)
    items = [i for i in items if not (i.kind == 'lines' and (i.ref.get('fill') or '').lower() == '#ffffff'
                                      and not i.ref.get('stroke') and i.x1 - i.x0 > (n1 - n0) - 2 * PAD)] or items
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
                ov_ = lambda a, b: min(a.x1, b.x1) - max(a.x0, b.x0) > 0.5 * min(a.x1 - a.x0, b.x1 - b.x0)
                stacked = any(b.x0 > left + 8 and ov_(a, b) for a in ta for b in tb_) and yb - ya < 18 and tb_ \
                    and min(b.x0 for b in tb_) > left + 8
                # a vector / bracket glyph pair (top piece above its extender or bottom piece) is one stack even when the
                # printed line starts at the cell's left ('B1 for translation of (-5 / y) or (x / -3)': the second vector
                # was torn apart when the line wrapped; 2023 MJ 32 q8, 2025 ON 22 q10, 2026 MJ 11 q18 / 22 q4 / 22 q6, pattern 240)
                if not stacked and yb - ya < 18:
                    stk_ = [i for i in ts_ if i.ref.get('t') in BRK_]
                    for g_ in stk_:         # a bracket column spans the bands it sits beside: its glyphs lie between them
                        col_ = [h for h in stk_ if abs(h.ref['x'] - g_.ref['x']) < 1.5]
                        lo_, hi_ = min(h.ref['y'] for h in col_), max(h.ref['y'] for h in col_)
                        if lo_ - 4 <= ya <= hi_ + 1 and lo_ - 4 <= yb <= hi_ + 1 and hi_ > lo_:
                            stacked = True; break
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
    def plain(ln):              # text, fraction bars and root signs (a step with fractions re-flows too: round 32, 2014 MJ
        return all(i.kind == 't' or (i.kind == 'lines' and (i.y1 - i.y0 < 1.6 or _rootish(i))) for i in ln['its'])   # 41 q11)
    def open_end(ln):           # a printed line that stops mid-step ('... ÷ their', '... ='): the next line goes on with it
        ln = ln['parts'][-1] if ln.get('parts') else ln   # the LAST printed line of a joined paragraph (its widest line
        #   ended in 'or' / 'and': every later line was joined, 'B1 for ...' / 'FT ...' too: M2 reasons, 2022 FM 62 q8)
        last = max((i for i in ln['its'] if i.kind == 't'), key=lambda i: i.x1, default=None)   # (round 30, Dhruv: write a
        t_ = last.ref.get('t', '').strip() if last else ''                                   # step whole, not broken)
        return bool(re.search(r'[÷×+\-–=(]$', t_)) or t_ in ('their', 'of', 'for', 'and', 'or', 'by', 'to', 'the')
    def last_t(ln):             # the text at the end of the LAST printed line of (a joined) line
        ln = ln['parts'][-1] if ln.get('parts') else ln
        last = max((i for i in ln['its'] if i.kind == 't'), key=lambda i: i.x1, default=None)
        return last.ref.get('t', '').strip() if last else ''
    def list_line(a, b):        # a list of formulas ('... seen in working:' / 'sin a = v/T oe' / 'cos a = h/T oe') stays one
        bt = ' '.join(i.ref.get('t', '') for i in b['its'] if i.kind == 't')   # per line (2018 ON 63 q6(d)(i), round 37)
        return last_t(a).endswith(':') or (re.search(r'\boe$', last_t(a)) is not None and '=' in bt)
    k = 0
    while k < len(lines) - 1 and align != 'right':
        a, b = lines[k], lines[k + 1]
        lh_ = a['y1'] - a['y0']
        ax0, ax1 = min(i.x0 for i in a['its']), max(i.x1 for i in a['its'])
        bx0 = min(i.x0 for i in b['its'])
        first_b = min(b['its'], key=lambda i: i.x0).ref.get('t', '') if plain(b) else ''
        if plain(a) and plain(b) and abs(ax0 - bx0) < 3 and b['y0'] - a['y1'] < 0.6 * lh_ and ax1 > c1 - 0.3 * (c1 - c0) \
                and (ax1 - ax0) > width * 0.6 and (re.match(r'[a-z]', first_b) or open_end(a)) and not re.match(r'(or|and)$', first_b) \
                and not re.match(r'(\(?[ABCM]\d|SC\d|FT|If|OR|AND|Method)\b', first_b) and not list_line(a, b) \
                and not any(a['y1'] - 1 < sy < b['y0'] + 1 and sx0 - 3 <= ax0 <= sx1 for sx0, sy, sx1 in CTX.get('subrules', [])):
            # (never across a printed sub-row rule: '... or better' + next sub-row '32.8 km/h', 2024 FM 62 q9(c), M1 check)
            # (only a line that goes on with a sentence: '[x =] 1.13 ...' or 'or ...' is a new answer line, round 28)
            a.setdefault('parts', [dict(a, its=list(a['its']))]).append(b)
            a['its'] = a['its'] + b['its']; a['y1'] = b['y1']
            del lines[k + 1]
            continue
        k += 1
    prev = None                 # (placed bottom, printed bottom) of the line above in this cell
    for ln in lines:
        if prev is not None:    # a line never moves above the line before it plus their printed gap: growth of OTHER
            n_ = len(out)       # columns and this cell's own wraps must add up, not overlap (M1 2026 MJ 12 q13)
            need = prev[0] + max(0.0, ln["y0"] - prev[1]) - (ln["y0"] + extra + push(ln["y0"]))
            if need > 0.01:
                extra += need
                if growth is not None:
                    growth.append((ln['y0'], need))
        n_ = len(out)
        if not ln.get('parts') and align != 'right' and plain(ln) and any(i.kind == 'lines' for i in ln['its']) \
                and max(i.x1 for i in ln['its']) - min(i.x0 for i in ln['its']) > width + 0.5 \
                and len({round(i.ref['y']) for i in ln['its'] if i.kind == 't' and i.ref.get('s', 11) >= 9}) <= 3:
            ln['parts'] = [dict(ln, its=list(ln['its']))]   # one wide step with fractions: wrapped like a re-flow, each
            #                                                row as tall as its own pieces (round 32: 'of x' far below)
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
            import collections as _cl
            def base_(part):            # the part's text baseline: the y most of its words sit on
                c_ = _cl.Counter(round(i.ref['y'], 1) for i in part['its'] if i.kind == 't' and i.ref.get('s', 11) >= 9)
                return c_.most_common(1)[0][0] if c_ else part['y1']
            tall_ = any(i.kind == 'lines' for p_ in ln['parts'] for i in p_['its']) and len(tl_) > 0
            if tall_:                   # a step with fractions (round 32, 2014 MJ 41 q11): rows aligned on the baseline,
                up_ = max(base_(p_) - p_['y0'] for p_ in ln['parts'])        # each row as tall as the tallest piece
                dn_ = max(p_['y1'] - base_(p_) for p_ in ln['parts'])
                pitch = up_ + dn_ + LGAP
                fb_ = base_(first)
            if tall_:                   # rows first, then each row as tall as ITS pieces (a short 'line CB' row is not
                rows_ = [[]]            # given the fraction's height: round 32, 2024 ON 32 q1)
                xx_ = 0.0
                for part in ln['parts']:
                    bp_ = base_(part)
                    for ch in _chunks(part['its']):
                        w_ = ch['x1'] - ch['x0']; sp_ = 0.0 if xx_ == 0 else 0.25 * 11.0
                        if w_ > width + 0.5:     # one unbreakable piece (a fraction with a long numerator) wider than
                            ch = dict(ch, _k=max(0.6, width / w_)); w_ *= ch['_k']   # the column: scaled to fit (rule 30,
                            #                                            >= 60 %), never clipped (M2 reasons, 2021 MJ 22 q13)
                        if xx_ and xx_ + sp_ + w_ > width + 0.5:
                            rows_.append([]); xx_, sp_ = 0.0, 0.0
                        rows_[-1].append((ch, xx_ + sp_, bp_)); xx_ += sp_ + w_
                yb_ = fb_
                for r_i, rw in enumerate(rows_):
                    ups = max(bp_ - min(i.y0 for i in ch['its']) for ch, _, bp_ in rw)
                    dns = max(max(i.y1 for i in ch['its']) - bp_ for ch, _, bp_ in rw)
                    if r_i:
                        yb_ += prev_dn + LGAP + ups
                    prev_dn = dns
                    for ch, xo, bp_ in rw:
                        dx = n0 + lead + xo - ch['x0']
                        dy = extra + push(first['y0']) + yb_ - bp_
                        for it in ch['its']:
                            out.append((it, dx, dy, ch.get('_k', 1.0), ch['x0']))
                g_ = (yb_ + prev_dn) - ln['y1']
                extra += g_
                if growth is not None and abs(g_) > 0.01:
                    growth.append((ln['y1'], g_))
                if len(out) > n_:
                    prev = (max(it.y1 + dy_ for it, dx_, dy_, k_, x_ in out[n_:]), ln['y1'])
                continue
            for j, part in enumerate(ln['parts']):
                for ch in _chunks(part['its']):
                    w_ = ch['x1'] - ch['x0']
                    k_ch = max(0.6, width / w_) if w_ > width + 0.5 else 1.0   # (as above: scaled, never clipped)
                    w_ *= k_ch
                    sp_ = 0.0 if x == 0 else 0.25 * 11.0
                    if x and x + sp_ + w_ > width + 0.5:
                        row += 1; x, sp_ = 0.0, 0.0
                    dx = n0 + lead + x + sp_ - ch['x0']
                    ptl = [i for i in part['its'] if i.kind == 't' and i.ref.get('s', 11) >= 9]
                    py0_ = min(i.y0 for i in ptl) if ptl else part['y0']      # the text top, not a superscript's
                    dy = extra + push(first['y0']) + (fy0_ + row * pitch) - py0_
                    for it in ch['its']:
                        out.append((it, dx, dy, k_ch, ch['x0']))
                    x += sp_ + w_
            g_ = (first['y0'] + row * pitch + lh) - ln['y1']
            extra += g_
            if growth is not None and abs(g_) > 0.01:
                growth.append((ln['y1'], g_))
            if len(out) > n_:
                prev = (max(it.y1 + dy_ for it, dx_, dy_, k_, x_ in out[n_:]), ln['y1'])
            continue
        chunks = _chunks(ln['its'])
        rel0 = chunks[0]['x0'] - left                  # this printed line's indent in its cell
        span_all = chunks[-1]['x1'] - chunks[0]['x0']
        lead_ts = [i for i in ln['its'] if i.kind == 't' and i.x0 - chunks[0]['x0'] < 3]
        multi = len({round(i.ref['y'] / (0.9 * i.ref.get('s', 11))) for i in lead_ts}) >= 2 and len(lead_ts) >= 2
        if multi and span_all > width + 0.5:           # too wide for one block: pieces that overlap in x stay together
            xc = []                                    # (a fraction, a root), the line wraps between them - never shrinks
            for it in sorted(ln['its'], key=lambda i: i.x0):   # (round 30, 2014 MJ 21 q8(b)(ii), 2025 MJ 22 q21(b))
                if xc and (it.x0 < xc[-1]['x1'] - 0.3 or _brk_join(xc[-1], it)):
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
                    if nc and nc[-1].get('_s') and (it.x0 < nc[-1]['x1'] - 0.3 or _brk_join(nc[-1], it)):
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
        if len(out) > n_:
            prev = (max(it.y1 + dy_ for it, dx_, dy_, k_, x_ in out[n_:]), ln['y1'])
    bottom = max(it.y1 for it in items) + extra + push(1e9)
    if out:                     # never above the last placed line: a line pushed by ANOTHER column's growth and then wrapped
        bottom = max(bottom, max(it.y1 + dy for it, dx, dy, k, x0 in out))   # itself ran past the row (M1 2026 MJ 12 q3)
    return out, bottom, min(i.y0 for i in items)


_FONTS = {('serif', 0): 'tiro', ('serif', 1): 'tibo', ('sans', 0): 'helv', ('sans', 1): 'hebo'}


def text_width(t, fam, s, bold=False):
    """Width of a text in the font the page draws it with (Times / Helvetica metrics = the review and site fonts)."""
    import fitz
    return round(fitz.get_text_length(t, fontname=_FONTS.get((fam if fam in ('serif', 'sans') else 'serif', int(bool(bold))), 'tiro'),
                                      fontsize=s), 2)


TOP = 4.0          # free space above the highest ink of a row (round 28: fractions touched the row's top rule)
BRK_ = set('⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦')
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
            if sum(1 for i in l['its'] if i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 > 5) >= 2:
                tall = False            # a table row (cell rules): the table is one rigid block, no margins per row (M1:
                #                         2024 ON 62 q1(b) - 11 rows x margins opened a big gap under the table)
            if prev is None:
                need = TOP + (MARGIN if tall else 0.0) - l['y0']
                if need > 0:
                    ps.append((-1e9, need))
            else:
                ptall = (prev['y1'] - prev['y0']) > 1.45 * base and not prev.get('_tbl')
                need = LGAP + (MARGIN if tall or ptall else 0.0) - (l['y0'] - prev['y1'])
                if need > 0:
                    ps.append((l['y0'] - 0.01, need))
            l['_tbl'] = not tall and (l['y1'] - l['y0']) > 1.45 * base
            prev = l
        if prev is not None and (prev['y1'] - prev['y0']) > 1.45 * base and not prev.get('_tbl'):
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
    merged = False
    is_note = bool(re.match(r'Throughout the (modelling|investigation)\b', ' '.join(
        t['t'] for t in sorted(u.get('text', []), key=lambda t: (round(t['y']), t['x'])) if t['t'].strip())[:40].strip(), re.I))
    # a section-wide note (Dhruv M1: top of every modelling question): ONE cell over the whole table, no label, no rules
    if hint and edges and len(edges) == len(hint) and abs(u['w'] - hint[1]) < 2 and abs(edges[0] - hint[0][0]) > 8 \
            and any(abs(a_ - b_) < 2.5 for a_, b_ in zip(edges[1:], hint[0][1:])):
        edges = list(hint[0])   # a table flush with the Answer column (shaded cells, no printed Q|Answer rule) put its own
        #                         first rule in place of the column rule: the table fell into the Q column (2023 FM 62 q1, M2)
    if hint and (not edges or len(edges) != len(hint)) and abs(u['w'] - hint[1]) < 2:
        own = edges
        edges = list(hint[0])                            # a graph / grid in the row hides its column rules: same table
        vx = [((bb[0] + bb[2]) / 2, bb[3] - bb[1]) for bb in (_bbox(l['d']) for l in u.get('lines', [])) if bb and bb[2] - bb[0] < 1.3]
        merged = not own and len(edges) >= 2 and all(sum(h for x, h in vx if abs(x - e) < 2.5) < 0.2 * u['h'] for e in edges[1:]) \
            and any(abs(x - edges[0]) < 2.5 and h > 0.5 * u['h'] for x, h in vx)
        # a note row printed across Answer, Marks and Partial Marks (no column rules after the Q column, 2024 MJ 42 q10
        # 'For all parts accept ...'): ONE cell over all of them, never cut into our columns (M1)
    if not edges:
        return None
    if len(edges) == 2:
        edges = edges + [u['w'] - 0.5]                   # no Partial Marks column printed
    if ncols == 5 and len(edges) == 3:
        edges = edges + [u['w'] - 0.5]                   # no Guidance column printed in this row
    cells_src = [(0.0, edges[0])] + [(edges[k], edges[k + 1]) for k in range(len(edges) - 1)] + [(edges[-1], u['w'])]
    A = ANSWER_SHARE * (W - QW - MW) if ncols == 4 else W - QW - MW   # (Dhruv, round 29: Answer wider than Partial Marks)
    ours = [(0.0, QW), (QW, QW + A), (QW + A, QW + A + MW), (QW + A + MW, W)]
    if ncols == 5:
        F = W - QW - MW
        A, P5 = FIVE_SHARES[0] * F, FIVE_SHARES[1] * F
        ours = [(0.0, QW), (QW, QW + A), (QW + A, QW + A + MW), (QW + A + MW, QW + A + MW + P5), (QW + A + MW + P5, W)]
    CTX['subrules'] = []
    its = _items(u, edges[:4] if ncols == 5 else edges[:3])
    vlong = [i for i in its if i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 >= 8]
    its = [i for i in its if not (i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 < 8 and i.y0 < 1.5 and any(
        abs(i.x0 - l.x0) < 1.2 and abs(l.y0 - i.y1) < 1.5 for l in vlong))]
    # (a column rule split at the row's top edge: its stub stayed above the table it belongs to, 2014 MJ 31 q5, round 32)
    if not any(i.kind != 'lines' and not (i.kind == 't' and re.fullmatch(r'[.\s…_|\-]+', i.ref['t'])) for i in its):
        return 'empty'                                   # only rules left (the end of a table on a page): no row
    by = [[] for _ in cells_src]
    for it in its:
        cx = (it.x0 + it.x1) / 2
        c = next((k for k, e in enumerate(edges) if cx < e), len(edges))
        by[c].append(it)
    CS = (1, 2, 3, 4) if ncols == 5 else (1, 2, 3)
    if is_note:
        for c in range(len(by)):
            if c != 1:
                by[1] += by[c]; by[c] = []
        cells_src[1] = (0.0, u['w'])
        ours[1] = (0.0, W)
        merged = True
        first_unit = False
    note = None                 # a note band printed across the whole table INSIDE a row ('In parts (a)(ii)(b) and (a)(ii)(c),
    if not merged and ncols >= 4 and len(edges) >= 3:   # marks can only be ...', 2024 MJ 41 q2, M1): no column rules there
        vx_ = [((bb[0] + bb[2]) / 2, bb[1], bb[3]) for bb in (_bbox(l['d']) for l in u.get('lines', [])) if bb and bb[2] - bb[0] < 1.3]
        def cov_(e, y):
            return any(abs(x - e) < 2.5 and y0 - 1 <= y <= y1 + 1 for x, y0, y1 in vx_)
        run_, best_ = None, None
        for yy in [k_ * 0.5 for k_ in range(int(u['h'] * 2))]:
            free_ = not cov_(edges[1], yy) and not cov_(edges[2], yy)
            if free_ and run_ is None:
                run_ = yy
            if (not free_ or yy + 0.5 >= u['h']) and run_ is not None:
                if yy - run_ > 8 and (best_ is None or yy - run_ > best_[1] - best_[0]):
                    best_ = (run_, yy)
                run_ = None
        if best_ and 2 < best_[0] and best_[1] < u['h'] - 2 and any(cov_(edges[1], y) for y in (best_[0] - 2, best_[1] + 2)):
            nt_ = [it for c in range(len(by)) for it in by[c] if best_[0] < (it.y0 + it.y1) / 2 < best_[1]]
            txt_ = ' '.join(it.ref['t'] for it in sorted(nt_, key=lambda i: (i.y0, i.x0)) if it.kind == 't').strip()
            if re.match(r'(MODELLING|INVESTIGATION|Modelling|Investigation)\b', txt_):
                nt_ = []                # the NEXT section's title row (pattern 112) is never a note of this row
            if any(it.kind == 't' for it in nt_):
                rules_ = [it for c in range(len(by)) for it in by[c] if it.kind == 'lines' and it.y1 - it.y0 < 1.6
                          and it.x1 - it.x0 > 0.25 * u['w'] and (best_[0] - 6 <= it.y0 <= best_[0] + 2 or best_[1] - 2 <= it.y0 <= best_[1] + 6)]
                nt_ = nt_ + rules_      # (the printed rules above / under the band: ours replace them - no double edge, round 32)
                for c in range(len(by)):
                    by[c] = [it for it in by[c] if it not in nt_]
                nt_ = [it for it in nt_ if it not in rules_]
                qfree_ = not cov_(edges[0], (best_[0] + best_[1]) / 2)
                by.append(nt_)
                cells_src.append((0.0 if qfree_ else edges[0], u['w']))
                ours.append((0.0 if qfree_ else QW, W))
                CS = CS + (len(by) - 1,)
                note = (len(by) - 1, qfree_, best_[0] < 8, best_[1] > u['h'] - 8)   # (band at the row's top / bottom:
                #   the row's own border is the band's edge - ours would double it, round 32 2024 MJ 41 q2)
    if merged:
        for c in range(2, len(by)):
            by[1] += by[c]; by[c] = []
        cells_src[1] = (edges[0], u['w'])
        ours[1] = (QW, W)
    v = {'src': u['src'], 'w': W, 'h': 0.0, 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    bottoms = []
    placed_all = []                                      # (source y0, our y0, source y1, our y1) of every placed text piece
    CTX['pic_spans'] = []                                # source y ranges of pictures / rigid blocks in this row
    push0 = _pushes(list(by), 11.0 if base else max([i.ref.get('s', 11) for i in its if i.kind == 't'] or [11]))
    # rows grow in step: a line that wraps in one column moves the lines below it in EVERY column (round 28, 2025 MJ 61 q4:
    # the '1' mark stayed beside the wrong line). Pass 1 measures each column's growth by printed height.
    grows = {}
    for c in CS:
        if by[c] and not (c == 3 and ncols == 3) and not ((_picture_cell(by[c]) or _has_table(by[c]) or _brk(u, label, c))
                                                          and CTX.get('pdf')):
            g = []
            _cell(by[c] + (by[3] if c == 1 and ncols == 3 else []), cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1],
                  align='right' if c == 2 else 'left', push=push0, growth=g)
            grows[c] = g
    def G(c, y):
        return sum(a for yy, a in grows.get(c, []) if yy < y)
    def anchored(c, y):         # this printed line lines up with another column (a line of it starts at the same height)
        neg = [yy for yy, a in grows.get(c, []) if a < 0 and yy < y]     # or a sub-row rule lies between it and the
        return any(abs(i.y0 - y) < 3 for k in CS if k != c and k < len(by) for i in by[k] if i.kind == 't') or \
            any(min(neg) - 1 <= sy <= y + 1 for sx0, sy, sx1 in CTX.get('subrules', []))   # re-flow above it
    def push_for(c):            # a column's growth is matched by the others; space a re-flow SAVED (negative growth) is
        def p_(y):              # kept only where the line must line up - otherwise the next line moves up (no blank line
            if G(c, y) < 0 and not anchored(c, y):                # under a re-flowed sentence: Dhruv round 37, 2018 ON 63 q6)
                return push0(y)   # (a wrap in the Partial Marks column beside it is no reason to stay down)
            return push0(y) + max([G(k, y) for k in grows] + [0.0]) - G(c, y)
        return p_
    push = push_for(0)
    top_pad = min([i.y0 for i in its] + [u['h']])
    for c in CS:
        if c == 3 and ncols == 3:
            by[1] += by[3]; continue
        if by[c] and not _brk(u, label, c) and _has_table(by[c]):
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
            for _ in range(4):      # a column rule printed in pieces: the short pieces at its ends (a 5.6 pt stub above the first
                #                     strip of shading) are part of it - left out they were drawn as loose ticks above the
                #                     table (2023 FM 62 q1(a), round 34, pattern 235)
                add_ = [i for i in by[c] if i not in rl and i.kind == 'lines' and i.x1 - i.x0 < 1.6 and 0.4 < i.y1 - i.y0 <= 8
                        and any(j.kind == 'lines' and j.x1 - j.x0 < 1.6 and abs((i.x0 + i.x1) / 2 - (j.x0 + j.x1) / 2) < 0.8
                                and (abs(i.y1 - j.y0) < 1.0 or abs(i.y0 - j.y1) < 1.0) for j in rl)]
                if not add_:
                    break
                rl = rl + add_
            tx0, ty0 = min(i.x0 for i in rl) - 1, min(i.y0 for i in rl) - 1
            tx1, ty1 = max(i.x1 for i in rl) + 1, max(i.y1 for i in rl) + 1
            blk = [i for i in by[c] if tx0 <= (i.x0 + i.x1) / 2 <= tx1 and ty0 <= (i.y0 + i.y1) / 2 <= ty1]
            blk += [i for i in by[c] if i not in blk and i.kind == 't' and (i.ref.get('dir') or [1, 0])[0] < 0.3
                    and ty0 - 3 <= (i.y0 + i.y1) / 2 <= ty1 + 3 and tx0 - 30 <= i.x0 and i.x1 <= tx0 + 2]
            # (rotated row labels beside the table ('1 neg') belong to it: round 30, 2021 FM 52 q3)
            blk += [i for i in by[c] if i not in blk and i.kind in ('t', 'lines') and ty0 <= (i.y0 + i.y1) / 2 <= ty1
                    and i.x1 <= tx0 + 2 and not (i.kind == 'lines' and i.y1 - i.y0 > ty1 - ty0 + 4)]
            # (the first column of a table whose cells are fills - its row names 'Pattern number, n' sit left of the
            #  grid's first rule - goes with the table, never laid out as loose text over it: 2022 FM 62 q1, M2 pass 2)
            for _ in range(3):      # an unruled row printed right against the table, inside its width ('3 + 4 + 5 + 6 = 18'
                yb0, yb1 = min(i.y0 for i in blk), max(i.y1 for i in blk)   # above, '-3 + -4 ... = -18' below: 52 q3(b))
                add = [i for i in by[c] if i not in blk and i.kind == 't' and tx0 - 2 <= i.x0 and i.x1 <= tx1 + 2
                       and (yb0 - 16 < i.y1 <= yb0 + 1 or yb1 - 1 <= i.y0 < yb1 + 16)]
                if not add:
                    break
                rowy = {round(i.ref['y']) for i in add}
                if any(i not in blk and i not in add and i.kind == 't' and round(i.ref['y']) in rowy for i in by[c]):
                    break           # a printed line running on past the table is a sentence, not a table row: its tail
                    #                 was laid out alone at the cell's left ('x = 22 and y ...', 2022 MJ 61 q3, M2)
                colx = {round(i.x0) for i in blk if i.kind == 't'}
                if any(re.fullmatch(r'[A-Za-z]{4,}[.,]?', i.ref.get('t', '')) for i in add) or any(len([i for i in add if round(i.ref['y']) == y_]) < 3 or
                       sum(1 for i in add if round(i.ref['y']) == y_ and any(abs(i.x0 - cx) <= 3 for cx in colx)) < 3
                       for y_ in rowy):     # (its cells line up with the table's columns: sentences above a small
                    #                          table were pulled in and drawn over the text, 2025 MJ 62 q4(b), round 30)
                    break           # only whole table-like rows (several cells), never a sentence under it
                blk += add
            rest = [i for i in by[c] if i not in blk]
            shift, tb = push_for(c)(ty0), None
            placed = []
            if rest:
                placed, tb, _ = _cell(rest, cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1], push=push_for(c))
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
            bel = [p_ for p_ in placed if p_[0].y0 >= by1_ - 1]
            e_ = 0.0
            if bel:                 # text under the table starts under it as WE placed it (the table moved down with the
                f_b = min(bel, key=lambda p_: p_[0].y0)     # text above it: 2024 ON 63 q6, a rule ran through 'or', M1 check)
                e_ = max(0.0, by0_ + shift + (by1_ - by0_) * k_ + (f_b[0].y0 - by1_) - (f_b[0].y0 + f_b[2]))
            for it, dx, dy, k, x0 in placed:
                dy_ = dy + (e_ if it.y0 >= by1_ - 1 else 0.0)
                _emit(v, it, dx, dy_, k, x0)
                if it.kind == 't':          # (text around a table counts for sub-row rules and alignment, M1 check)
                    placed_all.append((it.y0, it.y0 + dy_, it.y1, it.y1 + dy_, c))
            if tb is not None and bel:
                tb += e_
            thin = lambda i: i.kind == 'lines' and min(i.x1 - i.x0, i.y1 - i.y0) < 1.6
            blk = [i for i in blk if not thin(i)] + [i for i in blk if thin(i)]   # rules over the shading (round 30)
            _emit_block(v, blk, bx0, by0_, ours[c][0] + PAD, by0_ + shift, k_)
            placed_all.append((by0_, by0_ + shift, by1_, by0_ + shift + (by1_ - by0_) * k_, c))   # the table counts too
            bottoms.append(max(by0_ + shift + (by1_ - by0_) * k_ + 3.0, tb or 0))
            continue
        _gs = __import__('ms_graphs').spec(CTX.get('qid'), label)
        _forced = bool(_gs and _gs.get('vector') and c == _gs.get('col', 1) and any(i.kind != 't' for i in by[c]))
        #   (a spec'd faint sketch is a picture even when its few thin lines don't look like one: 2020 ON 43 8(a)(iii))
        if (_forced or _picture_cell(by[c]) or _brk(u, label, c)) and by[c] and CTX.get('pdf'):   # a diagram / shaded sketch in the cell: its printed picture (pattern 78)
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
            BR_ = set('⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎫⎬⎭')     # pieces of a tall bracket are text of the line under, never picture
            inpic = [i for i in by[c] if px0 - 14 <= (i.x0 + i.x1) / 2 <= px1 + 14 and py0 - 12 <= (i.y0 + i.y1) / 2 <= py1 + 12
                     and not (i.kind == 't' and len(i.ref['t']) > 6 and not (py0 - 2 <= (i.y0 + i.y1) / 2 <= py1 + 2))
                     and not (i.kind == 't' and i.ref['t'] and set(i.ref['t']) <= BR_ and not (py0 - 2 <= (i.y0 + i.y1) / 2 <= py1 + 2))]
            long_out = [i for i in by[c] if i.kind == 't' and i not in inpic and len(i.ref['t']) > 6
                        and px0 - 14 <= (i.x0 + i.x1) / 2 <= px1 + 14 and py0 - 12 <= (i.y0 + i.y1) / 2 <= py1 + 12]
            br_out = [i for i in by[c] if i.kind == 't' and i not in inpic and i.ref['t'] and set(i.ref['t']) <= BR_]
            long_out += br_out                           # (2026 MJ 63 q9: the top of '((100/50)^2 - 1)' drawn twice)
            if br_out:                                   # and everything printed on the bracket's lines (its exponent '2')
                b0_, b1_ = min(i.y0 for i in br_out) - 4, max(i.y1 for i in br_out)
                inpic = [i for i in inpic if not (i.kind == 't' and b0_ <= (i.y0 + i.y1) / 2 <= b1_)]
            if long_out:                                 # a text line under / over the drawing goes WHOLE to our text, never
                inpic = [i for i in inpic if not (i.kind == 't' and any(abs(i.ref['y'] - o.ref['y']) < 2 for o in long_out))]
                #   half into the picture ('Correct sketch passing through (3, -5)' drawn twice, 2025 ON 63 q1, M1)
            # (short labels just outside the drawing go with it; words of the text around it do not - round 28, 2025 MJ 61
            # q1: the lines under a table went into its picture and everything shrank)
            if _brk(u, label, c):
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
            def _words(t_):                              # letters of the whole printed line of t_: a heading is words,
                return sum(ch.isalpha() for o in by[c] if o.kind == 't' and abs(o.ref['y'] - t_.ref['y']) < 2
                           for ch in o.ref['t'])          # never a diagram label 'Q', 'S', '65' (2026 MJ 21 q13, M1)
            head = [t_ for t_ in by[c] if t_.kind == 't' and (
                        (_words(t_) >= 4 and t_.y0 < py0 + 3 and t_.y1 > py0 - 0.5 and any(i.y0 < t_.y1 for i in pasted)) or
                        (_words(t_) >= 4 and any(i.x0 - 2 <= t_.x0 and t_.x1 <= i.x1 + 2 and i.y0 - 0.5 < t_.y1
                                                 and t_.y0 < i.y0 + 0.3 * (i.y1 - i.y0) for i in pasted)) or
                        (_words(t_) >= 4 and t_ not in inpic and t_.x0 < px1 and t_.x1 > px0 and t_.y1 > py0
                         and t_.y0 < py0 + 0.3 * (py1 - py0)) or
                        (t_.y1 <= py0 + 3 and len(' '.join(o.ref['t'] for o in by[c] if o.kind == 't'
                                                         and abs(o.ref['y'] - t_.ref['y']) < 2)) > 8))]
            head = [t_ for t_ in head if not any(
                i.kind == 'lines' and i.x1 - i.x0 > 40 and i.y1 - i.y0 > 30 and i.x0 < t_.x0 - 1 and t_.x1 + 1 < i.x1
                and i.y0 < t_.y0 - 1 and t_.y1 + 1 < i.y1 for i in dr)]
            #   (a label INSIDE a drawn frame - 'Sandwich' / 'Fruit' in a Venn box - is never a heading: the box's top was
            #    cut and the labels moved out, 2023 ON 12 q20, M2 reasons)
            # (and a heading of OUR text over the top of a DRAWN graph: drawn twice, 2019 ON 41 q11, 43 q3, round 30)
            #   (also a heading INSIDE the top of a pasted graph: 'Correct sketch'
            #                                       drawn twice, 2021 FM 62 q9(d)(ii), round 29)   # a text line a pasted picture lies over (never a drawn box,
            head_moved = any(len(t_.ref['t']) > 3 for t_ in head)
            if head_moved:                                   # 2021 FM 42 q9) ('Correct diagram' half hidden, 2021 FM 32 q9):
                line = [t_ for t_ in by[c] if t_.kind == 't' and any(abs(t_.ref['y'] - h_.ref['y']) < 2 for h_ in head)]
                if line:                                 # (a raised power on the heading line goes with it: 'k²', M1)
                    ly0_, ly1_ = min(t_.y0 for t_ in line), max(t_.y1 for t_ in line)
                    line += [t_ for t_ in by[c] if t_.kind == 't' and t_ not in line and t_.y0 >= ly0_ - 4 and t_.y1 <= ly1_ + 0.5
                             and t_.ref.get('s', 11) < 0.85 * max(o.ref.get('s', 11) for o in line)]
                py0 = max([min([py0] + [i.y0 - 1.0 for i in inpic if i not in line and i.y0 > max(t_.y1 for t_ in line)])]
                          + [t_.y1 + 0.5 for t_ in line])   # the picture starts under it, the WHOLE line is our text
                #   (from the picture's own first ink: a numerator above a pasted bracket was cut, 2024 ON 41 q5, M1)
                for t_ in line:                              # (round 28: only its first word was kept)
                    if t_ in inpic:
                        inpic.remove(t_)
                    if t_ not in rest:
                        rest.append(t_)
            shift, tb = 0.0, None
            snap_ = {k_: len(v.get(k_, [])) for k_ in ('text', 'lines', 'glyphs', 'images', 'figs')}
            if rest:                                     # text around the picture ('Correct diagram') laid out as text
                above = [i for i in rest if i.y1 <= py0 + 1]
                placed, tb, _ = _cell(rest, cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1], push=push_for(c))
                for it, dx, dy, k, x0 in placed:
                    _emit(v, it, dx, dy, k, x0)
                if above:
                    pl_ab = [p_ for p_ in placed if p_[0] in above]
                    shift = max([p_[2] for p_ in pl_ab] + [0.0])
            shift = max(shift, push(py0))                # (the heading's placement already holds the push)
            broken_pg = _brk(u, label, c)
            import ms_graphs
            gsp_ = ms_graphs.spec(CTX.get('qid'), label)
            gsp_ = gsp_ if gsp_ and c in {a_.get('col', 1) for a_ in [gsp_] + gsp_.get('alts', [])} and (gsp_.get('vector') or any(i.kind in ('images', 'figs') for i in inpic)) else None
            #   ('vector': a drawn graph that lost its points / is too faint is drawn again too; 'col': 3 = Partial Marks,
            #    Dhruv round 37: 2020 ON 62 6(a), 2020 ON 43 8(a)(iii))
            drawn_ = gsp_ is None and (not broken_pg and not any(i.kind in ('images', 'figs') for i in inpic)
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
            import ms_graphs
            gsp = gsp_
            if gsp:                                     # a screenshot graph: drawn again from the question's function
                if 'alts' in gsp:                       # several screenshots under one label (2021 MJ 41 11(b): graphical
                    n_ = CTX.setdefault('alt_n', {})    # method (1) and (2)): the k-th picture of the label takes alts[k] (RD2)
                    al_ = [a_ for a_ in gsp['alts'] if a_.get('col', 1) == c] or gsp['alts']   # (an alt may sit in the
                    k_ = n_.get((label, c), 0); n_[(label, c)] = k_ + 1                       #  Partial Marks column)
                    gsp = dict(al_[min(k_, len(al_) - 1)])
                K_ = u.get('_K', 1.0)                   # (Dhruv round 32, ms_graphs.SPECS)
                im_ = [i for i in inpic if i.kind in ('images', 'figs')]
                if im_ and max(i.y1 for i in im_) < py1 - 4:   # (RD2) the drawing replaces the SCREENSHOT only: a formula
                    py1 = max(i.y1 for i in im_)               # under it (its bar / root lines joined the picture's cluster)
                    #  stays text - 2024 ON 61 2(d) lost '-0.5 ± √(0.5² - 4×1.5×-737)' under the redrawn graph
                gw = min(ours[c][1] - ours[c][0] - 2 * PAD, max(gsp.get('w', 230.0), (px1 - px0)))
                gh = max(gsp.get('h', 110.0), (py1 - py0))
                gL, gT = ms_graphs.draw(gsp, gw, gh)
                yb_ = [b_[3] for b_ in (_bbox(l_['d']) for l_ in gL) if b_] + [t_['y'] + 0.3 * t_.get('s', 9) for t_ in gT]
                if yb_ and max(yb_) + 2 < gh:           # (Dhruv round 39) the cell is as tall as the DRAWING: a drawing
                    gh = max(yb_) + 2                   # smaller than the printed picture left empty space under it
                ox_, oy_ = ours[c][0] + PAD, py0 + shift
                if gh > (py1 - py0) + 0.5:              # the drawing is taller than the printed picture: what is under
                    CTX.setdefault('pic_grow', []).append(  # it in the row moves down (Dhruv round 38, 2021 MJ 63 7(d):
                        (oy_ + (py1 - py0), gh - (py1 - py0), len(v['lines']), len(v['text'])))   # graph over the next sub-row)
                from ms_layout import _map_path
                for l_ in gL:
                    l2 = dict(l_, _g=1); l2['d'] = _map_path(l_['d'], lambda x: x + ox_, lambda y: y + oy_); v['lines'].append(l2)
                for t_ in gT:
                    t2 = dict(t_, x=round(t_['x'] + ox_, 2), y=round(t_['y'] + oy_, 2), f=fam or 'serif', _g=1); v['text'].append(t2)
                CTX.setdefault('pic_spans', []).append((py0, py1))
                bottoms.append(max(oy_ + gh + 3.0, tb or 0))
                CTX.setdefault('pic_bots', []).append(bottoms[-1])   # (already below the grown picture: never moved again)
                lp_out = [i for i in inpic if i.kind in ('t', 'lines', 'glyphs') and not (py0 - 1 <= (i.y0 + i.y1) / 2 <= py1 + 1)]
                if lp_out:
                    pl_, bt_, _ = _cell(lp_out, cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1], push=push_for(c))
                    nt0_, nl0_ = len(v['text']), len(v['lines'])
                    for it, dx, dy, k, x0 in pl_:
                        dd_ = dy + max(0.0, (oy_ + gh + 3.0) - (py1 + dy))
                        _emit(v, it, dx + 0, dd_, k, x0)
                        bottoms.append(it.y1 + dd_ + 3.0)       # the row grows with the text under a redrawn graph
                    for e_ in v['text'][nt0_:] + v['lines'][nl0_:]:
                        e_['_g'] = 1                            # (placed under the drawing already: not moved again)
                continue
            CTX['pic_text_out'] = [i for i in by[c] if i.kind == 't' and i not in inpic]
            bot = _cell_picture(v, u, inpic, cells_src[c], ours[c], (px0, py0, px1, py1) if head_moved and not broken_pg else None,
                                shift)          # (top clamped only under a moved heading: a rotated 'All' above a table
            #                                     was cut, 2021 FM 52 q3)
            #                     (broken page: from the cell's first ink - the formula over the graph was cut, 2014 MJ 62 q6)
            if bot is not None:
                bottoms.append(max(bot, tb or 0))
                lp_ = CTX.pop('last_pic', None)        # text the crop left out (under a sub-row rule: the formula
                out_ = [i for i in inpic if i.kind in ('t', 'lines', 'images', 'glyphs') and lp_ and not (lp_[0] - 1 <= (i.y0 + i.y1) / 2 <= lp_[1] + 1)]
                if out_:                               # row under a sketch, 2024 ON 61 q2(d), M1) is laid out as text
                    pl_, bt_, _ = _cell(out_, cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1], push=push_for(c))
                    for it, dx, dy, k, x0 in pl_:
                        _emit(v, it, dx, dy, k, x0)
                    if bt_ is not None:
                        bottoms.append(bt_)
                continue
            for k_, n_ in snap_.items():                 # no picture after all: the text placed around it goes, the whole
                if k_ in v:                              # cell is laid out once below (2026 MJ 21 q7: drawn twice, M1)
                    del v[k_][n_:]
        placed, bot, _ = _cell(by[c], cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1],
                               align='right' if c == 2 else 'left', push=push_for(c))
        for it, dx, dy, k, x0 in placed:
            _emit(v, it, dx, dy, k, x0)
            placed_all.append((it.y0, it.y0 + dy, it.y1, it.y1 + dy, c))
        if note and c == note[0] and placed:
            note = note[:2] + (min(it.y0 + dy for it, dx, dy, k, x0 in placed) - 4, max(it.y1 + dy for it, dx, dy, k, x0 in placed) + 4) + note[2:4]
        if bot is not None:
            bottoms.append(bot)
    for thr_, ext_, nl_, nt_ in CTX.pop('pic_grow', []):     # (the drawing's own pieces come after nl_ / nt_ and stay)
        from ms_layout import _map_path
        dl_ = len(v['lines']); dt_ = len(v['text'])
        for k_, t_ in enumerate(v['text']):
            if not t_.get('_g') and t_['y'] - 0.75 * t_.get('s', 11) >= thr_ - 0.5:
                t_['y'] = round(t_['y'] + ext_, 2)
        for k_, l_ in enumerate(v['lines']):
            bb = _bbox(l_['d'])
            if bb and bb[1] >= thr_ - 0.5 and not l_.get('_g'):
                l_['d'] = _map_path(l_['d'], lambda x: x, lambda y: y + ext_)
        for k_ in ('images', 'figs', 'glyphs'):
            for g_ in v.get(k_, []):
                if isinstance(g_, dict) and g_.get('y', -1) >= thr_ - 0.5:
                    g_['y'] = round(g_['y'] + ext_, 2)
        placed_all = [(a0, b0 + ext_, a1, b1 + ext_, k0) if b0 >= thr_ - 0.5 else (a0, b0, a1, b1, k0)
                      for a0, b0, a1, b1, k0 in placed_all]
        own_ = CTX.get('pic_bots', [])           # (Dhruv round 39: the drawing's own bottom moved down by its own growth
        bottoms[:] = [b_ + ext_ if b_ > thr_ + 0.5 and b_ not in own_ else b_ for b_ in bottoms]   # = empty space under it)
    CTX.pop('pic_bots', None)
    for l_ in v['lines']:
        l_.pop('_g', None)
    for t_ in v['text']:
        t_.pop('_g', None)
    # Q column: our full label on the first printed line (continued rows show none)
    # sub-row rules (maths, Dhruv round 32: 'line between A1 and M1', 'lines align with their answer'): each printed
    # rule inside the row is drawn again over the columns it crosses, between the lines placed above and under it
    subr = CTX.pop('subrules', []); pic_spans = CTX.pop('pic_spans', [])
    for sx0, sy, sx1 in sorted(set(subr), key=lambda t: t[1]):
        if any(a_ - 1 < sy < b_ + 1 for a_, b_ in pic_spans) or not placed_all:
            continue
        under = [p_ for p_ in placed_all if p_[0] > sy]
        above = [p_ for p_ in placed_all if p_[2] < sy]
        if not under:
            continue
        # every column starts its first line under the rule at the same height (Dhruv round 32, 2026 MJ 62 q6: a mark
        # '1' sat beside the table above its '18' when the table grew; 2026 MJ 63 q6(b)). A column whose first line under
        # the rule is higher than the others moves down - only its lines from there on, and placed_all with them.
        nxt = min([r_[1] for r_ in subr if r_[1] > sy + 1] + [1e9])
        firsts = {}                 # column -> (our top, our top - printed top) of its first line under the rule
        for p_ in under:
            if p_[0] < nxt and p_[1] < firsts.get(p_[4], (1e9, 0))[0]:
                firsts[p_[4]] = (p_[1], p_[1] - p_[0])
        def fits():                 # the rule as placed would run through no line
            if not above:
                return True
            f1 = min(under, key=lambda p_: p_[0])
            y1_ = min(max(f1[1] - (f1[0] - sy), max(p_[3] for p_ in above) + 1.5), f1[1] - 1.0)
            return not any(p_[1] < y1_ for p_ in under) and not any(p_[3] > y1_ for p_ in above)
        if len(firsts) >= 2 and not fits():     # only where the rule would otherwise be dropped (2025 MJ 43 q14: the
            from ms_layout import _map_path     # alignment everywhere moved good rows apart)
            tgt = max(o_ for f0, o_ in firsts.values())   # (offsets, not tops: a cell printed lower - centred - stays lower)
            for c_, (f0, o_) in firsts.items():
                d_ = tgt - o_
                if not (0.8 < d_ < 200) or not (1 <= c_ < len(ours)):
                    continue
                x0_, x1_ = ours[c_][0] - 1, ours[c_][1] + 1
                for t_ in v['text']:
                    if x0_ <= t_['x'] < x1_ and t_['y'] - 0.75 * t_.get('s', 11) >= f0 - 0.5:
                        t_['y'] = round(t_['y'] + d_, 2)
                for l_ in v['lines']:
                    bb = _bbox(l_['d'])
                    if bb and x0_ <= bb[0] and bb[2] <= x1_ and bb[1] >= f0 - 0.5:
                        l_['d'] = _map_path(l_['d'], lambda x: x, lambda y: y + d_)
                for k_ in ('images', 'figs', 'glyphs'):
                    for g_ in v.get(k_, []):
                        if isinstance(g_, dict) and x0_ <= g_.get('x', -1) < x1_ and g_.get('y', -1) >= f0 - 0.5:
                            g_['y'] = round(g_['y'] + d_, 2)
                placed_all = [(a0, b0 + d_, a1, b1 + d_, k0) if k0 == c_ and b0 >= f0 - 0.5 else (a0, b0, a1, b1, k0)
                              for a0, b0, a1, b1, k0 in placed_all]
                bottoms.append(max([b1 for a0, b0, a1, b1, k0 in placed_all if k0 == c_] + [0]))
            under = [p_ for p_ in placed_all if p_[0] > sy]
            above = [p_ for p_ in placed_all if p_[2] < sy]
        if not above:               # only a rigid block above (a table: its text is not in placed_all) - its bottom
            top_u = min(p_[1] for p_ in under)      # in our row (2026 MJ 62 q6: 'OR' table, then '18 | 1')
            bt = [t_['y'] + 0.3 * t_.get('s', 11) for t_ in v['text'] if t_['y'] < top_u - 1]
            bt += [b_[3] for b_ in (_bbox(l_['d']) for l_ in v['lines']) if b_ and b_[3] < top_u - 1 and b_[1] > 0.5]
            if not bt:
                continue
            above = [(sy - 1, max(bt), sy - 1, max(bt), -1)]
        f_ = min(under, key=lambda p_: p_[0])
        y_ = max(f_[1] - (f_[0] - sy), max(p_[3] for p_ in above) + 1.5)
        y_ = min(y_, f_[1] - 1.0)
        if any(p_[3] > y_ for p_ in above) and not any(p_[1] < max(q_[3] for q_ in above) - 30 for p_ in under):
            # a column above the rule grew more than the others (a guidance cell wraps to more lines than printed): the
            # whole row under the rule moves down so the rule fits - rows grow in step (2026 MJ 63 q6(b), M1 check)
            from ms_layout import _map_path
            T = min(p_[1] for p_ in under) - 0.5
            need = max(p_[3] for p_ in above) + 3.0 - min(p_[1] for p_ in under)
            for t_ in v['text']:
                if t_['y'] - 0.75 * t_.get('s', 11) > T:
                    t_['y'] = round(t_['y'] + need, 2)
            for l_ in v['lines']:
                b_ = _bbox(l_['d'])
                if b_ and b_[1] > T:
                    l_['d'] = _map_path(l_['d'], lambda x: x, lambda y: y + need)
            for k_ in ('figs', 'glyphs', 'images'):
                for g_ in v.get(k_, []):
                    if isinstance(g_, dict) and g_.get('y', -1) > T:
                        g_['y'] = round(g_['y'] + need, 2)
            placed_all = [(a0, b0 + need, a1, b1 + need, c0_) if b0 > T else (a0, b0, a1, b1, c0_) for a0, b0, a1, b1, c0_ in placed_all]
            bottoms = [b0 + need if b0 > T else b0 for b0 in bottoms]
            under = [p_ for p_ in placed_all if p_[0] > sy]
            f_ = min(under, key=lambda p_: p_[0])
            y_ = max(f_[1] - (f_[0] - sy), max(p_[3] for p_ in above) + 1.5)
            y_ = min(y_, f_[1] - 1.0)
        if any(p_[1] < y_ for p_ in under) or any(p_[3] > y_ for p_ in above) or any(
                a_ - 1 < sy < b_ + 1 for a_, b_ in pic_spans):
            continue                # the columns are not aligned at this rule: no rule rather than one through content
        def col_x(x):                                  # a printed x on a column edge -> our edge
            cand = [(abs(x - e), o) for e, o in zip([edges[0]] + list(edges[1:]) + [u['w']], [ours[1][0]] + [ours[c_][0] for c_ in range(2, len(ours))] + [W])]
            return min(cand)[1] if min(cand)[0] < 6.5 else None
        xa, xb = col_x(sx0), col_x(sx1)
        if xa is None or xb is None or xb - xa < 10:
            continue
        if any(xa - 1 < t_['x'] + t_.get('w', 0) and t_['x'] < xb + 1 and t_['y'] - 0.72 * t_.get('s', 11) < y_ < t_['y'] + 0.2 * t_.get('s', 11)
               for t_ in v['text'] if t_.get('t', '').strip()):
            continue                # never a rule through a word: text laid out under a cell picture is not in placed_all
            #                         ('[on third roll] corner ...' struck through, 2021 MJ 51 q7 / 62 q3, M2 reasons)
        v['lines'].append({'d': f'M{xa:.2f} {y_ - 0.3:.2f}H{xb:.2f}V{y_ + 0.3:.2f}H{xa:.2f}Z', 'fill': '#000000'})
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
    if ncols == 5:
        xs = [QW, QW + A, QW + A + MW, QW + A + MW + P5]
    elif ncols == 4:
        xs = [QW, QW + A, QW + A + MW]
    else:
        xs = [QW, QW + A]
    segs_ = [(0.0, v['h'])]
    if note and len(note) == 6:                     # column rules stop at the note band; a rule above and under it
        segs_ = [(0.0, note[2]), (note[3], v['h'])]
        for yy, edge_ in ((note[2], note[4]), (note[3], note[5])):
            if edge_:
                continue
            v['lines'].append({'d': f'M{0 if note[1] else QW:.2f} {yy - 0.3:.2f}L{W:.2f} {yy - 0.3:.2f}L{W:.2f} {yy + 0.3:.2f}'
                                    f'L{0 if note[1] else QW:.2f} {yy + 0.3:.2f}Z', 'fill': '#000000'})
    for x in ([] if is_note else [QW] if merged else xs):
        for ya_, yb_ in (segs_ if not (note and len(note) == 6 and x == QW and not note[1]) else [(0.0, v['h'])]):
            v['lines'].append({'d': f'M{x - 0.3:.2f} {ya_:.2f}L{x + 0.3:.2f} {ya_:.2f}L{x + 0.3:.2f} {yb_:.2f}L{x - 0.3:.2f} {yb_:.2f}Z', 'fill': '#000000'})
    if fam:                                          # one font for question and mark scheme (Dhruv, round 27)
        for t in v['text']:
            if t.get('f') in ('serif', 'sans'):
                t['f'] = fam
        _ops_font(v, fam)            # signs in the paper's font: the 'symbol' face (DejaVu) draws '>' far wider than
                #                         its printed width, it ran into the '9' (2026 MJ 21 q10(c), Dhruv round 33)
    if is_note:
        v['note'] = True
    v['info'] = {'edges': edges, 'new_edges': xs, 'new_w': [QW, A, MW] + ([A] if ncols == 4 else [P5, W - xs[-1]] if ncols == 5 else [])}
    _sub_chain(v)
    return v


OPS_SERIF = set('<>=≤≥≠+−×÷±→*∞°√,.()[]')


def _ops_font(v, fam):
    """signs in the 'symbol' face -> the paper's font, centred in their printed width (pattern 203)"""
    if not fam or not isinstance(v, dict):
        return
    for t in v.get('text', []):
        if t.get('f') == 'symbol' and t['t'] and all(ch in OPS_SERIF for ch in t['t']):
            t['f'] = fam
            if len(t['t']) == 1 and t['t'] not in ',.()[]':
                nat = _serif_w(t['t'], t.get('s', 11))
                if nat and nat < t['w']:
                    t['x'] = round(t['x'] + (t['w'] - nat) / 2, 2); t['w'] = round(nat, 2)
_SW = {}


def _serif_w(ch, size):
    """advance width of a character in Liberation Serif (the face the pages draw with)"""
    if not _SW:
        import glob
        from fontTools.ttLib import TTFont
        f = (glob.glob('/usr/share/fonts/**/LiberationSerif-Regular.ttf', recursive=True) or [None])[0]
        if not f:
            _SW['_'] = None
            return None
        tt = TTFont(f); _SW['_'] = (tt.getBestCmap(), tt['hmtx'].metrics, tt['head'].unitsPerEm)
    if not _SW.get('_'):
        return None
    cm, hm, upm = _SW['_']
    g = cm.get(ord(ch))
    return hm[g][0] / upm * size if g else None


def _sub_chain(v):
    """'y₂ − y₁' printed as one subscript chain (the '− y' at subscript size: 2024 ON 32 q1(f), Dhruv round 33 'shrunk'):
    the sign and the second letter go back to the letter's size and line; the digits stay subscripts. What follows on
    the same line, and a fraction bar under / over the chain, move right by the extra width."""
    from ms_layout import _map_path
    tt = v['text']
    for b in sorted([t for t in tt if t.get('s', 11) > 9.5 and len(t['t']) == 1 and t['t'].isalpha()], key=lambda t: t['x']):
        near = lambda t, x0: [u for u in tt if -1.0 <= u['x'] - x0 < 2.5 and u is not t]
        d1 = [u for u in near(b, b['x'] + b['w']) if u.get('s', 11) < 8 and u['t'].isdigit() and 0.5 < u['y'] - b['y'] < 5]
        if not d1:
            continue
        d1 = d1[0]
        op = [u for u in near(d1, d1['x'] + d1['w']) if u['t'] in ('−', '+', '-') and u.get('s', 11) < 8 and abs(u['y'] - d1['y']) < 1]
        if not op:
            continue
        op = op[0]
        l2 = [u for u in near(op, op['x'] + op['w']) if u['t'].isalpha() and len(u['t']) == 1 and u.get('s', 11) < 8 and abs(u['y'] - op['y']) < 1]
        if not l2:
            continue
        l2 = l2[0]
        d2 = [u for u in near(l2, l2['x'] + l2['w']) if u['t'].isdigit() and u.get('s', 11) < l2.get('s', 11)]
        x_end0 = max(u['x'] + u['w'] for u in [l2] + d2)
        S = b['s']; k_ = S / op['s']
        x = d1['x'] + d1['w'] + 0.8
        op.update(s=S, y=b['y'], w=round(op['w'] * k_, 2), x=round(x, 2), f=b.get('f', op.get('f'))); x += op['w'] + 0.8
        l2.update(s=S, y=b['y'], w=round(l2['w'] * k_, 2), x=round(x, 2)); x += l2['w']
        for u in d2:
            u.update(s=round(0.64 * S, 2), y=round(d1['y'], 2), w=round(u['w'] * 0.64 * S / max(u['s'], 1), 2), x=round(x, 2)); x += u['w']
        dx = x - x_end0
        if dx <= 0.2:
            continue
        rest_ = [u for u in tt if u['x'] >= x_end0 - 0.3 and u not in (op, l2) and u not in d2 and abs(u['y'] - b['y']) < 12]
        bars = [bb for bb in (_bbox(l_['d']) for l_ in v['lines']) if bb and bb[3] - bb[1] < 1.6 and bb[0] < b['x'] + 1
                and bb[2] >= x_end0 - 3 and abs((bb[1] + bb[3]) / 2 - b['y']) < 14]
        right = max([x] + [bb[2] + dx for bb in bars])
        sh = max(0.0, right + 3.0 - min([u['x'] for u in rest_] + [1e9]))   # what follows moves only if it would touch
        for u in rest_:
            u['x'] = round(u['x'] + sh, 2)
        for l_ in v['lines']:
            bb = _bbox(l_['d'])
            if not bb:
                continue
            if bb[3] - bb[1] < 1.6 and bb[0] < b['x'] + 1 and bb[2] >= x_end0 - 3 and abs((bb[1] + bb[3]) / 2 - b['y']) < 14:
                l_['d'] = _map_path(l_['d'], lambda X, a=bb[0], c=bb[2]: X if X <= a + 0.5 else X + dx, lambda Y: Y)
            elif bb[0] >= x_end0 - 0.3 and abs((bb[1] + bb[3]) / 2 - b['y']) < 12 and sh:
                l_['d'] = _map_path(l_['d'], lambda X: X + sh, lambda Y: Y)


CTX = {}


PRINTED_CELLS = {   # cells whose PDF text layer is broken (doubled characters, a root sign with no drawing): shown as their
    ('0607_2018ON_61_q07', '7(a)', 1), ('0607_2018ON_61_q07', '7(b)(i)', 1),   # printed picture (Dhruv round 37)
}


def _brk(u, label, c):
    return u['src']['page'] in CTX.get('broken', ()) or (CTX.get('qid'), label, c) in PRINTED_CELLS


def _inline_pic(i, items):
    """A symbol pasted as a tiny picture inside a text line ('≠' in 2025 FM 62 q5(b)(ii)): one more piece of that line,
    never a reason to make the cell a picture (that drew the line twice, round 32)."""
    if i.y1 - i.y0 > 24 or i.x1 - i.x0 > 90:
        return False
    return sum(1 for t in items if t.kind == 't' and t.y0 < i.y1 - 2 and t.y1 > i.y0 + 2 and 0 <= min(abs(t.x0 - i.x1), abs(i.x0 - t.x1)) < 20) >= 2


def _picture_cell(items):
    """A cell whose content is a drawing (Venn diagram, sketch, shaded region, picture) rather than text + fraction bars,
    or whose text layer is broken (words drawn over each other, 2014 MJ 62 p4)."""
    if any(i.kind == 'figs' or (i.kind == 'images' and not _inline_pic(i, items)) for i in items):
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
    if a.ndim < 3 or min(a.shape[:2]) < 1:
        return im               # an empty crop (2026 MJ 21 q13, M1): nothing to clean
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
    below_ = [i.y0 for i in CTX.pop('pic_text_out', []) if i.y0 > (y0 + y1) / 2 and i.x0 < x1 and i.x1 > x0]
    if below_ and min(below_) - 0.6 < y1:   # never into a text line laid out as our text under the picture (its top half
        y1 = min(below_) - 0.6              # came out twice: 2026 MJ 63 q9, Dhruv round 33)
    b = u['src']['box']
    CTX['last_pic'] = (y0, y1)
    CTX.setdefault('pic_spans', []).append((y0, y1))
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
    fills = [i for i in ln if (i.ref.get('fill') or '').lower() not in ('', '#000000', '#231f20') and i.y1 - i.y0 > 3 and i.x1 - i.x0 > 10]
    if not (len(gv) >= 3 and (len(gh) >= 3 or len(fills) >= 4) and _is_table(items)):
        return False        # (rows drawn as cell fills, not rules: 2023 FM 62 q1(a), M2)
    x0, x1 = min(i.x0 for i in gv + gh), max(i.x1 for i in gv + gh)
    import collections
    pcs = collections.defaultdict(list)               # rule length per height: a table's row rules run most of its width.
    for i in gh:                                      # Only pieces that TOUCH (<= 1.5 pt) are one rule: four boxes around numbers
        pcs[round(i.y0)].append((i.x0, i.x1))         # with 11-16 pt between them are no table row (2019 ON 51 q1(a)(ii), pattern 234)
    rows = collections.defaultdict(float)
    for y_, sp in pcs.items():
        a_ = b_ = None
        for p0, p1 in sorted(sp):
            if a_ is not None and p0 <= b_ + 1.5:
                b_ = max(b_, p1)
            else:
                if a_ is not None:
                    rows[y_] = max(rows[y_], b_ - a_)
                a_, b_ = p0, p1
        rows[y_] = max(rows[y_], b_ - a_)
    if sum(1 for w in rows.values() if w > 0.6 * (x1 - x0)) >= 2:
        return True
    # a Word table whose rows are drawn as cell fills (grey / white) with short rule pieces: the fills' edges are its row
    # lines (2023 FM 62 q1(a) was taken for a 'shaded picture' and fell apart, M2 reasons)
    for i in ln:
        f_ = (i.ref.get('fill') or '').lower()
        if f_ and f_ not in ('#000000', '#231f20') and i.y1 - i.y0 > 3 and i.x1 - i.x0 > 10:
            rows[round(i.y0)] += i.x1 - i.x0; rows[round(i.y1)] += i.x1 - i.x0
    if sum(1 for w in rows.values() if w > 0.6 * (x1 - x0)) >= 2:
        return True
    cols_ = collections.defaultdict(list)             # ... or >= 4 column rules (pieces joined) over most of the grid's
    for i in gv:                                      # height: a grid of columns, never a few boxes around numbers
        cols_[round((i.x0 + i.x1) / 2)].append((i.y0, i.y1))
    gy0, gy1 = min(i.y0 for i in gv), max(i.y1 for i in gv)
    def cov(sp):
        tot, end = 0.0, -1e9
        for a_, b_ in sorted(sp):
            if b_ > end:
                tot += b_ - max(a_, end); end = b_
        return tot
    merged_, last_ = [], None
    for x_ in sorted(cols_):
        if last_ is not None and x_ - last_ <= 2:
            merged_[-1] += cols_[x_]
        else:
            merged_.append(list(cols_[x_]))
        last_ = x_
    return len(fills) >= 4 and sum(1 for sp in merged_ if cov(sp) > 0.6 * (gy1 - gy0)) >= 4
    #   (only with cell fills: boxes around numbers in rows ('2 x 5 x [2] x [5]', 2019 ON 51 q1) are no table, M2 pass 2)


def _curvy(i):
    d = i.ref.get('d', '')
    return 'C' in d or _slanted(d) or bool(i.ref.get('dash'))


def _clean_table(items):
    """A table is redrawn 'similar but proper' (Dhruv, round 32): its rule pieces snap to one grid of column x's and
    row y's, pieces of one rule join into one line (no double edge, no step at a shaded cell), shading fills snap to the
    grid cells, and a missing outer edge is added when the column rules show it (2025 MJ 61 q2, 2014 MJ 31 q5)."""
    thin_h = [i for i in items if i.kind == 'lines' and i.y1 - i.y0 < 1.6 and i.x1 - i.x0 >= 3 and not _curvy(i)]
    thin_v = [i for i in items if i.kind == 'lines' and i.x1 - i.x0 < 1.6 and i.y1 - i.y0 >= 3 and not _curvy(i)]
    fl_ = [i for i in items if i.kind == 'lines' and (i.ref.get('fill') or '').lower() not in ('', '#000000', '#231f20')
           and i.y1 - i.y0 > 3 and i.x1 - i.x0 > 10]
    if len(thin_h) < 2 and len(fl_) >= 4 and len(thin_v) >= 2:
        # a table whose rows are only cell fills (no printed row rules, 2022 FM 62 q1(a)(ii)): its row lines are the fills'
        # edges and its outer edges are drawn too ('similar but proper', MS_TABLE_RULES 32)
        ts_ = [i for i in items if i.kind == 't']
        gx0 = min([i.x0 for i in fl_ + thin_v] + [t.x0 - 4 for t in ts_])
        gx1 = max(i.x1 for i in fl_ + thin_v)
        fm_ = [i for i in fl_ if not any(o is not i and o.x0 <= i.x0 + 0.5 and o.x1 >= i.x1 - 0.5 and o.y0 <= i.y0 + 0.5 and o.y1 >= i.y1 - 0.5
                                         and (o.y1 - o.y0) > (i.y1 - i.y0) + 1 for o in fl_)]
        #   (a cell shaded in strips - a top strip, a middle one, a bottom one, and the whole cell on top of them: only the
        #    whole cell's edges are row lines, not every strip's: 2023 FM 62 q1(a), round 34, pattern 235)
        ys_ = sorted({round(i.y0, 1) for i in fm_} | {round(i.y1, 1) for i in fm_})
        cl_ = []
        for y_ in ys_:
            if cl_ and y_ - cl_[-1][-1] <= 3.5:
                cl_[-1].append(y_)
            else:
                cl_.append([y_])
        for c_ in cl_:
            y_ = sum(c_) / len(c_)
            thin_h.append(_Item('lines', {'d': f'M{gx0:.2f} {y_ - 0.3:.2f}H{gx1:.2f}V{y_ + 0.3:.2f}H{gx0:.2f}Z', 'fill': '#000000'},
                                gx0, y_ - 0.3, gx1, y_ + 0.3))
        y0_, y1_ = min(i.y0 for i in fl_ + thin_v), max(i.y1 for i in fl_ + thin_v)     # (the header row above the first shaded
        #                                                                        row has its outer edges too)
        thin_v.append(_Item('lines', {'d': f'M{gx0 - 0.3:.2f} {y0_:.2f}H{gx0 + 0.3:.2f}V{y1_:.2f}H{gx0 - 0.3:.2f}Z', 'fill': '#000000'},
                            gx0 - 0.3, y0_, gx0 + 0.3, y1_))
        items = items + thin_h[-len(cl_):] + [thin_v[-1]]
        if gx1 - max((i.x0 + i.x1) / 2 for i in thin_v[:-1]) > 3:      # the right outer edge too (printed against the column rule
            thin_v.append(_Item('lines', {'d': f'M{gx1 - 0.3:.2f} {y0_:.2f}H{gx1 + 0.3:.2f}V{y1_:.2f}H{gx1 - 0.3:.2f}Z', 'fill': '#000000'},
                                gx1 - 0.3, y0_, gx1 + 0.3, y1_))       # and lost with it: 2023 FM 62 q1(a), round 34)
            items = items + [thin_v[-1]]
    if len(thin_h) < 2 or len(thin_v) < 2:
        return items
    def clusters(vals, tol=1.6):
        out = []
        for v_ in sorted(vals):
            if out and v_ - out[-1][-1] <= tol:
                out[-1].append(v_)
            else:
                out.append([v_])
        return [sum(c) / len(c) for c in out]
    xs = clusters([(i.x0 + i.x1) / 2 for i in thin_v])
    ys = clusters([(i.y0 + i.y1) / 2 for i in thin_h])
    if len(xs) < 2 or len(ys) < 2:
        return items
    snap = lambda v_, grid, tol=2.6: min(grid, key=lambda g: abs(g - v_)) if min(abs(g - v_) for g in grid) <= tol else v_
    def runs(segs):
        segs = sorted(segs); out = []
        for a_, b_ in segs:
            if out and a_ <= out[-1][1] + 0.8:
                out[-1][1] = max(out[-1][1], b_)
            else:
                out.append([a_, b_])
        return out
    H = {}
    for i in thin_h:
        y_ = snap((i.y0 + i.y1) / 2, ys); H.setdefault(round(y_, 2), []).append((snap(i.x0, xs), snap(i.x1, xs)))
    V = {}
    for i in thin_v:
        x_ = snap((i.x0 + i.x1) / 2, xs); V.setdefault(round(x_, 2), []).append((snap(i.y0, ys), snap(i.y1, ys)))
    x0, x1, y0, y1 = xs[0], xs[-1], ys[0], ys[-1]
    full_ = any(b_ - a_ >= 0.6 * (x1 - x0) for segs_ in H.values() for a_, b_ in runs(segs_))   # a real table has a row rule across
    #   (boxes around numbers - four separate boxes in a row: their outer verticals are no table edges, so no bottom /
    #    top rule is drawn through the 'x' signs between them: 2019 ON 51 q1(a)(ii), round 34, pattern 234)
    ends = [(min(a_ for a_, b_ in V.get(round(xx, 2), [(1e9, 0)])), max(b_ for a_, b_ in V.get(round(xx, 2), [(0, -1e9)]))) for xx in (x0, x1)]
    if full_ and abs(ends[0][0] - ends[1][0]) < 1.5 and ends[0][0] < y0 - 3:       # both outer column rules start above the first
        y0 = (ends[0][0] + ends[1][0]) / 2; ys = [y0] + ys                # row rule: the table's top edge was not printed
    if full_ and abs(ends[0][1] - ends[1][1]) < 1.5 and ends[0][1] > y1 + 3:       # in this unit (2014 MJ 31 q5) - draw it
        y1 = (ends[0][1] + ends[1][1]) / 2; ys = ys + [y1]
    for yy in ((y0, y1) if full_ else ()):                # a missing outer edge (top / bottom) where both outer columns reach it
        if not any(a_ <= x0 + 1 and b_ >= x1 - 1 for a_, b_ in runs(H.get(round(yy, 2), []))):
            if all(any(a_ <= yy + 1 and b_ >= yy - 1 for a_, b_ in V.get(round(xx, 2), [])) for xx in (x0, x1)):
                H.setdefault(round(yy, 2), []).append((x0, x1))
    nearg = lambda i: any(abs((i.x0 + i.x1) / 2 - g) < 1.6 for g in xs) or any(abs((i.y0 + i.y1) / 2 - g) < 1.6 for g in ys)
    keep = [i for i in items if not (i in thin_h or i in thin_v) and not (
        i.kind == 'lines' and i.x1 - i.x0 < 3.5 and i.y1 - i.y0 < 3.5 and not i.ref.get('stroke') and nearg(i))]
    # (tiny rule stubs at a grid line - corner pieces, a step where shading meets a rule - go: 2025 MJ 61 q2)
    fills = []
    for i in keep:
        if i.kind == 'lines' and i.ref.get('fill') and not i.ref.get('stroke') and i.x1 - i.x0 >= 3 and i.y1 - i.y0 >= 3:
            a_, b_, c_, d_ = snap(i.x0, xs), snap(i.y0, ys), snap(i.x1, xs), snap(i.y1, ys)
            fills.append(_Item('lines', dict(i.ref, d=f'M{a_:.2f} {b_:.2f}H{c_:.2f}V{d_:.2f}H{a_:.2f}Z'), a_, b_, c_, d_))
        else:
            fills.append(i)
    col = '#000000'
    rules = []
    for yy, segs in H.items():
        for a_, b_ in runs(segs):
            rules.append(_Item('lines', {'d': f'M{a_ - 0.3:.2f} {yy - 0.3:.2f}H{b_ + 0.3:.2f}V{yy + 0.3:.2f}H{a_ - 0.3:.2f}Z', 'fill': col},
                               a_ - 0.3, yy - 0.3, b_ + 0.3, yy + 0.3))
    for xx, segs in V.items():
        for a_, b_ in runs(segs):
            rules.append(_Item('lines', {'d': f'M{xx - 0.3:.2f} {a_ - 0.3:.2f}H{xx + 0.3:.2f}V{b_ + 0.3:.2f}H{xx - 0.3:.2f}Z', 'fill': col},
                               xx - 0.3, a_ - 0.3, xx + 0.3, b_ + 0.3))
    return fills + rules                                  # (shading first, rules over it)


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
    if items:
        CTX.setdefault('pic_spans', []).append((min(i.y0 for i in items), max(i.y1 for i in items)))
    items = _clean_table(out_) if table else out_
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


_PB = {}


def _paper_base(qid):
    """The most used text size of the whole printed mark scheme (characters counted), or None."""
    try:
        import paths, collections, pymupdf
        f = paths.raw_pdfs(qid)[1]
        if f not in _PB:
            c = collections.Counter()
            for pg in pymupdf.open(f):
                for b_ in pg.get_text('dict')['blocks']:
                    for l_ in b_.get('lines', []):
                        for s_ in l_['spans']:
                            if s_['text'].strip():
                                c[round(s_['size'] * 2) / 2] += len(s_['text'].strip())
            _PB[f] = c.most_common(1)[0][0] if c else None
        return _PB[f]
    except Exception:
        return None


def build(q, uniq, store, hdr_unit, own_total, frame):
    """All rows of one maths question -> ms_p dict, or None to let the general path try."""
    import os
    CTX.clear()
    CTX['qid'] = q.get('id')
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
    pb = _paper_base(q['id'])                         # ... but a question that is mostly a small printed table (8 pt) has
    if pb and base < 0.9 * pb:                        # a small median: the whole scheme came out at 15 pt (2023 MJ 53 q6,
        base = pb                                     # 2023 FM 52 q1/q2, M2 reasons) -> the paper's normal size decides
    uniq = [(r, _scaled_unit(u, 11.0 / base)) for r, u in uniq]
    pages = collections.defaultdict(int)             # a page whose text layer is broken (words drawn over each other):
    for _, u in uniq:                                # every cell on it is kept as its printed picture (2014 MJ 62 p4)
        ts = [t for t in u.get('text', []) if t.get('t', '').strip() and t['w'] > 2]
        pages[u['src']['page']] += sum(1 for k, a in enumerate(ts) for b in ts[k + 1:] if a['t'] != b['t']
                                       and abs(a['y'] - b['y']) < 3 and min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x']) > 0.5 * min(a['w'], b['w']))
    CTX['broken'] = {p for p, n in pages.items() if n >= 6}
    try:                                             # 2026 MJ: a Guidance column (5 columns; Dhruv M1: shown as 5 columns)
        CTX['five'] = 'Guidance' in open(os.path.join(store, 'ms_header.json')).read()
    except Exception:
        CTX['five'] = False
    cols = [(columns(u), u['w']) for _, u in uniq]
    ncols = 5 if CTX['five'] and any(len(c or []) == 4 for c, _ in cols) else 4 if any(len(c or []) == 3 for c, _ in cols) else 3
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
        _ops_font(v, fam)
        if not v.get('note'):
            seen_lab.add(r['label'])
        out.append(v)
    if not out:
        return None
    info = next((v['info'] for v in out if not v.get('note')), out[0]['info'])
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

