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
    for t in u.get('text', []):
        if not t.get('t', '').strip():
            continue
        s = t.get('s', 11)
        its.append(_Item('t', t, t['x'], t['y'] - 0.78 * s, t['x'] + t['w'], t['y'] + 0.22 * s))
    for k in ('glyphs', 'images'):
        for g in u.get(k) or []:
            its.append(_Item(k, g, g['x'], g['y'], g['x'] + g['w'], g['y'] + g['h']))
    for f in u.get('figs') or []:
        its.append(_Item('figs', f, f['x'], f['y'], f['x'] + f.get('w', 0), f['y'] + f.get('h', 0)))
    for l in u.get('lines', []):
        if l.get('fill', '').lower() == '#ffffff' and 'stroke' not in l:
            continue
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
        its.append(_Item('lines', l, b[0], b[1], b[2], b[3]))
    return its


def _lines_of(items):
    """Printed lines: items whose vertical extents overlap (fractions and brackets join their line)."""
    rows = []
    for it in sorted(items, key=lambda i: i.y0):
        h = it.y1 - it.y0
        if rows and it.y0 < rows[-1]['y1'] - min(1.0, 0.3 * h):
            rows[-1]['its'].append(it); rows[-1]['y1'] = max(rows[-1]['y1'], it.y1)
        else:
            rows.append({'its': [it], 'y0': it.y0, 'y1': it.y1})
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


def _cell(items, c0, c1, n0, n1, align='left'):
    """Lay the items of one printed cell [c0, c1] into our column [n0, n1]. Returns (placed pieces, bottom y, top y)."""
    if not items:
        return [], None, None
    lines = _lines_of(items)
    width = n1 - n0 - 2 * PAD
    left = min(i.x0 for i in items)
    lead = max(1.5, min(left - c0, PAD + 2))
    out, extra = [], 0.0
    for ln in lines:
        chunks = _chunks(ln['its'])
        rel0 = chunks[0]['x0'] - left                  # this printed line's indent in its cell
        vis = [{'chs': [], 'shift': 0.0}]
        for ch in chunks:
            cur = vis[-1]
            if cur['chs'] and (ch['x1'] - left - cur['shift']) > width + 0.5:
                vis.append({'chs': [], 'shift': (ch['x0'] - left) - rel0})   # wrapped: starts at the line's indent
                cur = vis[-1]
            cur['chs'].append(ch)
        lh = ln['y1'] - ln['y0']
        for k, r in enumerate(vis):
            dy = extra + k * (lh + 2.0)
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
    bottom = max(it.y1 for it in items) + extra
    return out, bottom, min(i.y0 for i in items)


def layout_row(u, label, ncols, first_unit=True, hint=None, QW=QW):
    """One printed row unit -> our row unit, or None when its columns cannot be read."""
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
    if not any(i.kind != 'lines' for i in its):
        return 'empty'                                   # only rules left (the end of a table on a page): no row
    by = [[], [], [], []]
    for it in its:
        cx = (it.x0 + it.x1) / 2
        c = 0 if cx < edges[0] else 1 if cx < edges[1] else 2 if cx < edges[2] else 3
        by[c].append(it)
    v = {'src': u['src'], 'w': W, 'h': 0.0, 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    bottoms = []
    top_pad = min([i.y0 for i in its] + [u['h']])
    for c in (1, 2, 3):
        if c == 3 and ncols == 3:
            by[1] += by[3]; continue
        placed, bot, _ = _cell(by[c], cells_src[c][0], cells_src[c][1], ours[c][0], ours[c][1],
                               align='right' if c == 2 else 'left')
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
        tw = round(0.5 * s0 * len(label) + 0.6, 2)
        v['text'].append({'t': label, 'x': round(max(2.0, (QW - tw) / 2), 2), 'y': round(y0, 2), 'w': tw, 's': s0, 'f': f})
    bottom_pad = max(3.0, min(8.0, u['h'] - max([i.y1 for i in its] + [0])))
    lab_bot = max([i.y1 for i in by[0]] + [0])
    v['h'] = round(max([b + bottom_pad for b in bottoms] + [lab_bot + bottom_pad, 18.0]), 2) if bottoms else u['h']
    if ncols == 4:
        xs = [QW, QW + A, QW + A + MW]
    else:
        xs = [QW, QW + A]
    for x in xs:
        v['lines'].append({'d': f'M{x - 0.3:.2f} 0.00L{x + 0.3:.2f} 0.00L{x + 0.3:.2f} {v["h"]:.2f}L{x - 0.3:.2f} {v["h"]:.2f}Z', 'fill': '#000000'})
    v['info'] = {'edges': edges, 'new_edges': xs, 'new_w': [QW, A, MW] + ([A] if ncols == 4 else [])}
    return v


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
    cols = [(columns(u), u['w']) for _, u in uniq]
    ncols = 4 if any(len(c or []) == 3 for c, _ in cols) else 3
    good = [(c, w) for c, w in cols if c and len(c) == ncols - 1]
    hint = max(good, key=lambda cw: sum(1 for c2, w2 in good if c2 == cw[0])) if good else None
    qw = max([QW] + [round(0.5 * 11 * len(r['label']) + 0.6 + 8) for r, _ in uniq])   # long labels ('11(d)(iii)'): wider Q
    out, seen_lab = [], set()
    for r, u in uniq:
        if u['h'] < 4:
            continue
        v = layout_row(u, r['label'], ncols, first_unit=r['label'] not in seen_lab, hint=hint, QW=qw)
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
    rows = ([hdr_unit(first, ncols)] if hdr_unit else []) + out
    tot = own_total(q.get('marks'), first, out) if q.get('marks') else None
    if tot:
        frame(tot)
        rows.append(tot)
    if hdr_unit:
        rows[0]['lines'] += []
    return {'w': W, 'h': round(sum(v['h'] for v in rows), 2), 'rows': rows, 'problems': [], 'modes': {'maths': len(out)},
            'info': first, 'has_header': bool(hdr_unit), 'printed_total': None}
