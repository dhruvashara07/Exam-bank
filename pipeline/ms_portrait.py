"""Portrait version of a landscape mark-scheme row (2016 MJ onwards: tables 726 pt wide) at the question-paper width.

    portrait_unit(u, W=523.0) -> (unit', info)
        unit' has the same schema as a stored layout unit (text, lines, figs, w, h) so store.unit_svg draws it as is.
        info = {'mode': 'wrap' | 'scale' | 'same', 'why': ..., 'extra_lines': n}

How: the row's table is recognised from its rules (vertical edges that run the whole row, thin horizontal rules between
marking points). The question-label column and short-content columns (marks) keep their width; the wide text columns
(answer, guidance) are narrowed to fit, and their text is re-wrapped at the same font size: sub/superscripts stay glued
to their word, gaps inside a line are kept (equations stay as printed), bullets get a hanging indent. Every line keeps its
original vertical position; a line that wraps pushes the lines (and marks) below it down. Rules are redrawn for the new
size. Rows that cannot be re-wrapped (picture / drawn symbol / table inside a cell / unknown rules) are scaled to fit.
Portrait-era rows (w <= W + 2) are returned unchanged.
"""
import re, copy, statistics, collections

NUM = re.compile(r'-?\d+\.?\d*')
BULLET = re.compile(r'^(•|·|–|-|▪|\([a-zA-Z0-9]{1,4}\)|[a-zA-Z0-9]{1,2}[.)])$')
PITCH = 13.2          # default line pitch of 11 pt mark-scheme text


def _bbox(d):
    """bbox of an absolute path made of M L H V Z; None if it has curves or relative commands."""
    xs, ys, cx, cy = [], [], 0.0, 0.0
    for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
        n = [float(x) for x in NUM.findall(args)]
        if cmd in 'ML' and n and len(n) % 2 == 0:
            for i in range(0, len(n), 2):
                cx, cy = n[i], n[i + 1]; xs.append(cx); ys.append(cy)
        elif cmd == 'H' and n:
            for x in n:
                cx = x; xs.append(cx); ys.append(cy)
        elif cmd == 'V' and n:
            for y in n:
                cy = y; xs.append(cx); ys.append(cy)
        elif cmd != 'Z':
            return None
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _rules(u):
    """([(x0,y0,x1,y1)] thin rectangles, fill) or None if something else is drawn (dashes, boxes, curves)."""
    out, fills = [], collections.Counter()
    for l in u['lines']:
        if 'dash' in l:
            return None
        for sub in re.findall(r'M[^M]+', l['d']):
            bb = _bbox(sub)
            if bb is None or min(bb[2] - bb[0], bb[3] - bb[1]) > 1.3 or l.get('fill', '#000000').lower() == '#ffffff':
                return None
            out.append(bb)
            fills[l.get('fill', '#000000')] += 1
    return out, (fills.most_common(1)[0][0] if fills else '#000000')


def _cluster(vals, tol=1.5):
    out = []
    for v in sorted(vals):
        if out and v - out[-1][-1] <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(c) / len(c) for c in out]


def _scale_unit(u, W):
    k = W / u['w']
    v = copy.deepcopy(u)
    v['w'], v['h'] = round(W, 2), round(u['h'] * k, 2)
    for t in v['text']:
        for key in ('x', 'y', 'w', 's'):
            t[key] = round(t[key] * k, 2)
    for l in v['lines']:
        parts = re.split(r'(-?\d+\.?\d*)', l['d'])
        l['d'] = ''.join(f'{float(p) * k:.2f}' if NUM.fullmatch(p) else p for p in parts)
    for key in ('figs', 'images', 'glyphs'):
        for f in v.get(key, []):
            f['x'] = round(f['x'] * k, 2); f['y'] = round(f['y'] * k, 2)
            if 'w' in f:
                f['w'] = round(f['w'] * k, 2); f['h'] = round(f['h'] * k, 2)
            else:
                f['k'] = round(k * f.get('k', 1), 4)
    return v


def _groups(words):
    """words of one cell -> lines of groups; a group = a word with its sub/superscripts."""
    if not words:
        return []
    ref = max(w['s'] for w in words)
    main = [w for w in words if w['s'] >= 0.85 * ref or w.get('dir')]
    subs = [w for w in words if w not in main]
    G = [{'ws': [w], 'x': w['x'], 'w': w['w'], 'y': w['y']} for w in sorted(main, key=lambda w: (w['y'], w['x']))]
    for s in subs:
        best = None
        for g in G:
            m = g['ws'][0]
            if m['y'] - 11 <= s['y'] <= m['y'] + 8 and m['x'] - 1 <= s['x'] <= m['x'] + m['w'] + 4:
                if best is None or abs(g['y'] - s['y']) < abs(best['y'] - s['y']):
                    best = g
        if best is None:
            G.append({'ws': [s], 'x': s['x'], 'w': s['w'], 'y': s['y']})
        else:
            best['ws'].append(s)
            best['w'] = max(best['w'], s['x'] + s['w'] - best['x'])
    lines = []
    for g in sorted(G, key=lambda g: (g['y'], g['x'])):
        if lines and abs(lines[-1][0]['y'] - g['y']) < 3.5:
            lines[-1].append(g)
        else:
            lines.append([g])
    for ln in lines:
        ln.sort(key=lambda g: g['x'])
    return lines


def _paragraphs(lines, x1):
    """join soft-wrapped lines (a line that runs up to the right edge continues on the next); bullets start a paragraph."""
    paras = []
    for ln in lines:
        if paras and paras[-1]['soft'] and not BULLET.match(ln[0]['ws'][0]['t']):
            paras[-1]['lines'].append(ln)
        else:
            paras.append({'lines': [ln], 'soft': False})
        paras[-1]['soft'] = ln[-1]['x'] + ln[-1]['w'] >= x1 - 45
    return paras


def _wrap(par, x1):
    """-> lines, each [(group, x)] ; x relative to the column's left edge. First line starts at the original x,
    continuation lines at the original continuation x (or a hanging indent after a bullet)."""
    flat = []
    first_x = par['lines'][0][0]['x']
    cont_x = par['lines'][1][0]['x'] if len(par['lines']) > 1 else None
    for ln in par['lines']:
        prevend = None
        for g in ln:
            flat.append((g, None if prevend is None else max(g['x'] - prevend, 0)))
            prevend = g['x'] + g['w']
    if cont_x is None:
        cont_x = par['lines'][0][1]['x'] if len(par['lines'][0]) > 1 and BULLET.match(par['lines'][0][0]['ws'][0]['t']) else first_x
    out, cur, x = [], [], first_x
    for g, gap in flat:
        sp = 0 if not cur else (3.0 if gap is None else gap)
        if cur and x + sp + g['w'] > x1 - 3:
            out.append(cur)
            cur, x, sp = [], cont_x, 0
        cur.append((g, x + sp))
        x = x + sp + g['w']
    if cur:
        out.append(cur)
    return out


def _scaled(u, W, why):
    return _scale_unit(u, W), {'mode': 'scale', 'why': why, 'extra_lines': 0}


def portrait_unit(u, W=523.0):
    if u['w'] <= W + 2:
        return u, {'mode': 'same', 'why': 'portrait era', 'extra_lines': 0}
    if u.get('figs') or u.get('images') or u.get('glyphs'):
        return _scaled(u, W, 'picture or drawn symbol in the row')
    rr = _rules(u)
    if not rr:
        return _scaled(u, W, 'unknown rules')
    rl, rfill = rr
    h, Wo = u['h'], u['w']
    # vertical edges = thin vertical rules that together cover most of the row height
    vs = [r for r in rl if r[2] - r[0] < 1.3 and r[3] - r[1] > 1.5]
    xs = _cluster([(r[0] + r[2]) / 2 for r in vs])
    cov = collections.defaultdict(float)
    for r in vs:
        cov[min(xs, key=lambda e: abs(e - (r[0] + r[2]) / 2))] += r[3] - r[1]
    edges = sorted(x for x in xs if cov[x] >= 0.7 * h and x > 20)
    outer = [x for x in xs if cov[x] >= 0.7 * h and x <= 20]          # a left border of the whole table
    if any(0.7 * h > cov[x] > 8 for x in xs):
        return _scaled(u, W, 'table inside a cell')
    if not edges:
        return _scaled(u, W, 'columns not recognised')
    ncol = len(edges) + 1
    def col_of(x): return sum(1 for e in edges if e <= x + 0.5)
    def cx0(c): return 0 if c == 0 else edges[c - 1]
    old_w = [edges[0]] + [edges[i] - edges[i - 1] for i in range(1, len(edges))] + [Wo - edges[-1]]
    # horizontal rules that span a whole column are table rules; shorter ones are underlines / fraction bars
    colspan = [(0.0, edges[0])] + [(edges[i - 1], edges[i]) for i in range(1, len(edges))] + [(edges[-1], Wo)]
    def spans_col(r):
        return any(min(r[2], c1) - max(r[0], c0) >= 0.85 * (c1 - c0) and r[2] - r[0] >= 20 for c0, c1 in colspan)
    cand = [r for r in rl if r[3] - r[1] < 1.3 and r[2] - r[0] >= 1.3]
    ygroups = collections.defaultdict(list)                      # rules at one height: together they may cross the table
    for r in cand:
        ygroups[round((r[1] + r[3]) / 2 / 1.5)].append(r)
    def crosses(r):
        g = ygroups[round((r[1] + r[3]) / 2 / 1.5)]
        covered = sum(max(0, min(q[2], Wo) - max(q[0], edges[0])) for q in g)
        return covered >= 0.85 * (Wo - edges[0])
    hs = [r for r in cand if r[2] - r[0] > 20 and (spans_col(r) or crosses(r))]
    decor = [r for r in cand if r not in hs]
    seps = _cluster([(r[1] + r[3]) / 2 for r in hs if r[0] > edges[0] - 1 and 4 < (r[1] + r[3]) / 2 < h - 4])
    bounds = [0.0] + seps + [h]
    nb = len(bounds) - 1
    cells = collections.defaultdict(list)
    for t in u['text']:
        b = next((i for i in range(nb) if bounds[i] <= t['y'] < bounds[i + 1]), nb - 1)
        cells[(b, col_of(t['x']))].append(t)
    # fixed columns: the label column and columns whose text is only short tokens (marks)
    def short(c):
        ws = [t for (b, cc), v in cells.items() if cc == c for t in v]
        return bool(ws) and all(len(t['t']) <= 6 for t in ws) and len({round(t['y']) for t in ws}) >= len(ws) * 0.5
    fixed = [c == 0 or old_w[c] <= 75 or (old_w[c] <= 120 and short(c)) for c in range(ncol)]
    flex = sum(w for w, f in zip(old_w, fixed) if not f)
    if flex <= 0:
        return _scaled(u, W, 'columns not recognised')
    k = (W - sum(w for w, f in zip(old_w, fixed) if f)) / flex
    if k < 0.3:
        return _scaled(u, W, 'columns too narrow')
    new_w = [w if f else w * k for w, f in zip(old_w, fixed)]
    new_edges = [sum(new_w[:i + 1]) for i in range(ncol - 1)]
    def nx_start(c): return 0 if c == 0 else new_edges[c - 1]
    # line pitch of this row
    ps = []
    for ws in cells.values():
        ys = sorted({round(w['y']) for w in ws if w['s'] >= 9})
        ps += [y2 - y1 for y1, y2 in zip(ys, ys[1:]) if 11 <= y2 - y1 <= 17]
    pitch = statistics.median(ps) if ps else PITCH
    # re-wrap the flexible columns: paragraphs per (band, column); 'cum' = extra lines added above a paragraph
    paras_of, band_extra = {}, [0] * nb
    for (b, c), ws in cells.items():
        if fixed[c]:
            continue
        out, cum = [], 0
        for p in _paragraphs(_groups(ws), cx0(c) + old_w[c]):
            rel = {'lines': [[dict(g, x=g['x'] - cx0(c)) for g in ln] for ln in p['lines']]}
            last = rel['lines'][0][-1]
            if len(rel['lines']) == 1 and rel['lines'][0][0]['x'] > 0.5 * old_w[c] and last['x'] + last['w'] >= old_w[c] - 25:
                wl = [[(g, g['x'] - (old_w[c] - new_w[c])) for g in rel['lines'][0]]]        # right-aligned ('Total:') stays right-aligned
            else:
                wl = _wrap(rel, new_w[c])
            extra = len(wl) - len(p['lines'])
            out.append({'y': p['lines'][0][0]['y'], 'lines': wl, 'cum': cum, 'extra': extra})
            cum += extra
        paras_of[(b, c)] = out
        band_extra[b] = max(band_extra[b], cum)
    shift, acc = [0.0] * nb, 0.0
    for b in range(nb):
        shift[b] = acc
        acc += band_extra[b] * pitch
    v = {'src': u['src'], 'w': round(W, 2), 'h': round(h + acc, 2), 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    ref = {}                                      # per band the flexible column with most paragraphs: marks follow its lines
    for (b, c), ps_ in paras_of.items():
        if b not in ref or len(ps_) > len(paras_of[(b, ref[b])]):
            ref[b] = c
    def cum_above(b, y):
        before = [p for p in paras_of.get((b, ref.get(b)), []) if p['y'] < y - 2.5]
        return before[-1]['cum'] + before[-1]['extra'] if before else 0
    moved = []
    for (b, c), ws in cells.items():
        if fixed[c]:
            for t in ws:
                nt = dict(t)
                nt['x'] = round(t['x'] - cx0(c) + nx_start(c), 2)
                nt['y'] = round(t['y'] + shift[b] + pitch * cum_above(b, t['y']), 2)
                v['text'].append(nt); moved.append((t, nt))
    for (b, c), ps_ in paras_of.items():
        for p in ps_:
            for j, ln in enumerate(p['lines']):
                for g, gx in ln:
                    m = g['ws'][0]
                    for w in g['ws']:
                        nt = dict(w)
                        nt['x'] = round(nx_start(c) + gx + (w['x'] - m['x']), 2)
                        nt['y'] = round(p['y'] + (j + p['cum']) * pitch + (w['y'] - m['y']) + shift[b], 2)
                        v['text'].append(nt); moved.append((w, nt))
    # rules, redrawn at the new size
    T = 0.48
    def rect(x0, y0, x1, y1):
        return {'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}L{x0:.2f} {y1:.2f}Z', 'fill': rfill}
    bnew = [b0 + shift[i] for i, b0 in enumerate(bounds[:-1])] + [v['h']]
    left = min([r[0] for r in hs] + [edges[0]])
    xr = W - (Wo - max([r[2] for r in hs] + [edges[-1]]))          # the table's right end (rules stop at the right border)
    for i in range(nb):
        y0 = 0 if i == 0 else bnew[i] + T
        for e in new_edges + outer:
            v['lines'].append(rect(e - T / 2, y0, e + T / 2, bnew[i + 1]))
    for i in range(1, nb):
        full = any(r[0] < edges[0] - 5 and abs((r[1] + r[3]) / 2 - bounds[i]) < 2 for r in hs)
        v['lines'].append(rect(left if full else new_edges[0], bnew[i], xr, bnew[i] + T))
    v['lines'].append(rect(left, v['h'] - T, xr, v['h']))
    segs = collections.defaultdict(list)                       # new line (rounded y) -> [x0, x1, y, rect-thickness]
    for r in decor:
        under = [(o, n) for o, n in moved if o['s'] >= 5 and r[0] - 1.5 <= o['x'] + 0.2 * o['w'] and o['x'] + 0.8 * o['w'] <= r[2] + 1.5
                 and 0.5 <= r[1] - o['y'] <= 4.5]
        below = [o for o, n in moved if r[0] <= o['x'] + o['w'] / 2 <= r[2] and 0 < o['y'] - r[3] < 9 and o['y'] - 0.75 * o['s'] < r[3] + 1.5 and o['s'] >= 5]
        if not under or below:
            return _scaled(u, W, 'fraction bar or unknown mark')
        for o, n in under:
            segs[round(n['y'] - o['y'] + r[1], 1) if False else (round(n['y'] / 2), round(r[3] - r[1], 2), round(r[1] - o['y'], 2))].append([n['x'], n['x'] + o['w'], n['y'] + (r[1] - o['y']), r[3] - r[1]])
    for sg in segs.values():
        sg.sort()
        cur = sg[0][:]
        for a in sg[1:]:
            if a[0] - cur[1] <= 6 and abs(a[2] - cur[2]) < 1:
                cur[1] = max(cur[1], a[1])
            else:
                v['lines'].append(rect(cur[0], cur[2], cur[1], cur[2] + cur[3])); cur = a[:]
        v['lines'].append(rect(cur[0], cur[2], cur[1], cur[2] + cur[3]))
    return v, {'mode': 'wrap', 'why': '', 'extra_lines': int(sum(band_extra)), 'cols': ncol, 'bands': nb}


def check(u, v):
    """all words of u present in v, none past the right edge."""
    problems = []
    if sorted(t['t'] for t in u['text']) != sorted(t['t'] for t in v['text']):
        problems.append('words differ')
    over = [t['t'] for t in v['text'] if t['x'] + t['w'] > v['w'] + 0.5]
    if over:
        problems.append('overflow: ' + ' '.join(over[:4]))
    return problems
