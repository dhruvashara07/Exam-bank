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
BULLET = re.compile(r'^(•|·|–|-|▪|\([a-zA-Z0-9]{1,4}\)|[a-zA-Z0-9]{1,2}[.)])\s*$')   # ('• ' with its space: 2023 MJ 41 q7)
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
            if l.get('fill', '#000000').lower() == '#ffffff' and 'stroke' not in l:
                continue                                 # white cell background: the page is white anyway
            if bb is not None and (bb[3] <= 0.6 or (bb[1] < -0.5 and bb[3] <= 3.2)):   # (or a header strip of up to 3 pt, 2020 MJ 31 q11) the bottom edge of the header row above (grey fill cut by the box): not part of this row
                continue
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
    stacks = collections.defaultdict(list)            # fraction pieces (numerator + denominator) marked '_stack': ONE group
    for w in words:
        if w.get('_stack') is not None:
            stacks[w['_stack']].append(w)
    words = [w for w in words if w.get('_stack') is None]
    if not words and not stacks:
        return []
    ref = max([w['s'] for w in words] + [w['s'] for ws_ in stacks.values() for w in ws_])
    main = [w for w in words if w['s'] >= 0.85 * ref or w.get('dir')]
    subs = [w for w in words if w not in main]
    G = [{'ws': [w], 'x': w['x'], 'w': w['w'], 'y': w['y']} for w in sorted(main, key=lambda w: (w['y'], w['x']))]
    for ws_ in stacks.values():
        x0_ = min(w['x'] for w in ws_)
        G.append({'ws': sorted(ws_, key=lambda w: w['x']), 'x': x0_, 'w': max(w['x'] + w['w'] for w in ws_) - x0_,   # placed by its left-most piece
                  'y': ws_[0]['_hy'], 'ref_y': ws_[0]['_hy']})
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


KEYWORD = re.compile(r'(A|CON|TV|I|R|accept|allow|ignore|reject|do not|not|NOT|ecf|OR|AND|ORA|Note|NOTE)$')


def _paragraphs(lines, x1, x0=None, guidance=False):
    """join soft-wrapped lines (a line that runs up to the right edge continues on the next); bullets start a paragraph.
    Also a new paragraph (2026 MJ guidance column): after a blank line, and at a line starting with a bold marking keyword
    ('A ...', 'CON ...', 'accept ...', 'ignore ...') - each of those is its own instruction."""
    paras = []
    tol = 45 if x0 is None else min(45, 0.15 * (x1 - x0))
    for ln in lines:
        w0 = ln[0]['ws'][0]
        gap = paras and (w0['y'] - paras[-1]['lines'][-1][0]['ws'][0]['y']) > 1.6 * w0.get('s', 10)
        key = w0.get('b') and KEYWORD.match(w0['t'].strip())
        # a long line followed by one starting in lower case also continues (the printer wrapped early: 'after passing' /
        # 'through the lens', 2026 MJ 42 q6); short lines are list items and stay apart
        cont = (guidance and paras and x0 is not None and w0['t'][:1].islower() and not gap and not key   # Guidance only:
                # (Answer columns hold lists whose items start in lower case: 2018 ON 62 q3(e), 2016 ON 63 q4)
                and abs(ln[0]['x'] - paras[-1]['lines'][0][0]['x']) < 3
                and paras[-1]['end'] >= x1 - 0.3 * (x1 - x0))
        if paras and (paras[-1]['soft'] or cont) and not BULLET.match(w0['t']) and not gap and not key:
            paras[-1]['lines'].append(ln)
        else:
            paras.append({'lines': [ln], 'soft': False})
        paras[-1]['soft'] = ln[-1]['x'] + ln[-1]['w'] >= x1 - tol
        paras[-1]['end'] = ln[-1]['x'] + ln[-1]['w']
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
        l0 = par['lines'][0]
        if (cont_x == first_x and len(l0) > 1 and l0[1]['x'] - (l0[0]['x'] + l0[0]['w']) > 12
                and l0[1]['x'] - first_x < 0.4 * (x1 - first_x)):
            cont_x = l0[1]['x']                   # 'MP2   Measure ...': a wrapped line hangs under 'Measure' (2023 ON 51 q4)
    chains = []                                   # words with no real space between them ("30" + thin space + "s") never split
    for g, gap in flat:
        if chains and gap is not None and gap < 2.0:
            chains[-1].append((g, gap))
        else:
            chains.append([(g, gap)])
    out, cur, x = [], [], first_x
    for ch in chains:
        cw = sum(g['w'] for g, _ in ch) + sum(gp for _, gp in ch[1:])
        gap0 = ch[0][1]
        sp = 0 if not cur else (3.0 if gap0 is None else gap0)
        if cur and x + sp + cw > x1 - 3:
            out.append(cur)
            cur, x, sp = [], cont_x, 0
        xx = x + sp
        for i, (g, gp) in enumerate(ch):
            if i:
                xx += gp
            cur.append((g, xx))
            xx += g['w']
        x = xx
    if cur:
        out.append(cur)
    return out


def _scaled(u, W, why):
    return _scale_unit(u, W), {'mode': 'scale', 'why': why, 'extra_lines': 0}


def _line_w(ws):
    """width of the widest line of a cell."""
    out = []
    for y in sorted({round(t['y'] / 3) for t in ws}):
        ln = [t for t in ws if round(t['y'] / 3) == y and t['s'] >= 8]
        if ln:
            out.append(max(t['x'] + t['w'] for t in ln) - min(t['x'] for t in ln))
    return max(out) if out else 0.0


def _subcolumns(ws, x0, ow, nw, pitch):
    """Text set out in columns WITHOUT rules inside one cell (2019 FM 42 q11(b): 'gamma-emission | beta-emission' pairs):
    a plain re-wrap breaks the pairs apart. Found when a vertical strip of the cell is free of ink and at least 3 blocks
    (groups of lines between blank lines) have words on both sides of it. Each block becomes one paragraph; each side is
    wrapped in its own share of our column (alignment kept: centred stays centred)."""
    lines = _groups(ws)
    if len(lines) < 4:
        return None
    spans = [(g['x'], g['x'] + g['w']) for ln in lines for g in ln]
    best = None
    x = x0 + 0.25 * ow
    while x < x0 + 0.8 * ow:                         # the widest ink-free strip
        if not any(a - 2 < x < b + 2 for a, b in spans):
            a = x
            while x < x0 + 0.8 * ow and not any(a_ - 2 < x < b_ + 2 for a_, b_ in spans):
                x += 1
            if best is None or x - a > best[1] - best[0]:
                best = (a, x)
        x += 1
    if best is None or best[1] - best[0] < 12:
        return None
    S = (best[0] + best[1]) / 2
    blocks = []
    for ln in lines:
        if blocks and ln[0]['y'] - blocks[-1][-1][0]['y'] <= 1.6 * max(w['s'] for g in ln for w in g['ws']):
            blocks[-1].append(ln)
        else:
            blocks.append([ln])
    both = sum(1 for bl in blocks if any(g['x'] < S for ln in bl for g in ln) and any(g['x'] > S for ln in bl for g in ln))
    if both < 3:
        return None
    # a block's lines on one side can be printed half a line apart from the other side: blocks by the blank gaps only
    k = nw / ow
    sides = [(x0, S), (S, x0 + ow)]
    sinfo = []                                       # per side: centred? and the centre line (as printed)
    for a, c in sides:
        cs = []
        for ln in lines:
            gs = [g for g in ln if a <= g['x'] + g['w'] / 2 < c]
            if gs:
                cs.append((min(g['x'] for g in gs) + max(g['x'] + g['w'] for g in gs)) / 2)
        med = statistics.median(cs) if cs else (a + c) / 2
        sinfo.append((sum(abs(x_ - med) < 8 for x_ in cs) >= 0.7 * max(len(cs), 1), med))
    out, cum = [], 0
    for bl in blocks:
        rows = []
        for (a, c), (centred, med) in zip(sides, sinfo):
            gs = [g for ln in bl for g in ln if a <= g['x'] + g['w'] / 2 < c]
            if not gs:
                rows.append([]); continue
            na, width = (a - x0) * k + 3, (c - a) * k - 14
            mid = (med - a) * k - 3                   # the printed centre line, in our narrower side
            byl = {}
            for g in gs:
                byl.setdefault(round(g['y']), []).append(g)
            centred = centred and all(abs((min(g['x'] for g in l_) + max(g['x'] + g['w'] for g in l_)) / 2 - med) < 12
                                      for l_ in byl.values())   # ('Two of:' at the cell's left stays left)
            lead = 0.0 if centred else max(0.0, (min(g['x'] for g in gs) - a) * k)
            wl, cur, xx = [], [], lead
            for g in sorted(gs, key=lambda g: (round(g['y']), g['x'])):
                sp = 3.0 if cur else 0.0
                if cur and xx + sp + g['w'] > width:
                    wl.append(cur); cur, xx, sp = [], lead, 0.0
                cur.append([g, xx + sp]); xx += sp + g['w']
            if cur:
                wl.append(cur)
            for l_ in wl:
                lw_ = l_[-1][1] + l_[-1][0]['w'] - l_[0][1]
                sh = max(0.0, min(width - lw_, mid - lw_ / 2)) - l_[0][1] if centred else 0.0
                for e in l_:
                    e[1] = na + e[1] + sh
            rows.append(wl)
        n = max(len(r) for r in rows)
        wl = [[(g, gx) for r in rows if j < len(r) for g, gx in r[j]] for j in range(n)]
        y0 = min(g['y'] for ln in bl for g in ln)
        orig = round((max(g['y'] for ln in bl for g in ln) - y0) / pitch) + 1
        out.append({'y': y0, 'lines': wl, 'cum': cum, 'extra': n - orig})
        cum += n - orig
    return out, cum


def portrait_unit(u, W=523.0, widths=None, sizes=None, probe=False):
    """widths: {(ncol, column): width} for the fixed columns (see column_widths); sizes: {figure id: (w, h)};
    probe=True: only report the content width of the fixed columns -> (None, {'probe': {(ncol, c): width}, ...})."""
    if u['w'] <= W + 2:
        return u, {'mode': 'same', 'why': 'portrait era', 'extra_lines': 0}
    if u.get('glyphs'):
        return _scaled(u, W, 'drawn symbol in the row')
    pics = [dict(kind='image', x=i['x'], y=i['y'], w=i['w'], h=i['h'], ref=i) for i in u.get('images', [])]
    for f in u.get('figs', []):
        if not sizes or f['id'] not in sizes:
            return _scaled(u, W, 'picture of unknown size')
        pics.append(dict(kind='fig', x=f['x'], y=f['y'], w=sizes[f['id']][0], h=sizes[f['id']][1], ref=f))
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
    def crosses_col(y, c):                       # does the sub-row line at y run across column c?
        c0, c1 = colspan[c]
        cov_ = sum(max(0.0, min(r[2], c1) - max(r[0], c0)) for r in hs if abs((r[1] + r[3]) / 2 - y) < 1.5)
        return cov_ >= 0.85 * (c1 - c0)
    cross = {(i, c): crosses_col(bounds[i], c) for i in range(1, nb) for c in range(ncol)}
    cells = collections.defaultdict(list)
    for t in u['text']:
        b = next((i for i in range(nb) if bounds[i] <= t['y'] < bounds[i + 1]), nb - 1)
        c = col_of(t['x'])
        while b > 0 and c > 0 and old_w[c] >= 20 and not cross[(b, c)]:
            b -= 1                                # a cell spanning several sub-rows (2026 MJ Guidance): one paragraph
        cells[(b, c)].append(t)
    # fixed columns: the label column and columns whose text is only short tokens (marks)
    def short(c):
        ws = [t for (b, cc), v in cells.items() if cc == c for t in v]
        return bool(ws) and all(len(t['t']) <= 6 for t in ws) and len({round(t['y']) for t in ws}) >= len(ws) * 0.5
    fixed = [c == 0 or old_w[c] <= 75 or (old_w[c] <= 120 and short(c)) for c in range(ncol)]
    if probe:
        content = {(ncol, c): max([_line_w(ws) for (b, cc), ws in cells.items() if cc == c] or [0.0]) for c in range(ncol) if fixed[c]}
        return None, {'probe': content, 'ncol': ncol, 'old_w': old_w, 'fixed': fixed}
    fixed_w = [(widths or {}).get((ncol, c), old_w[c]) if fixed[c] else None for c in range(ncol)]
    flex = sum(w for w, f in zip(old_w, fixed) if not f)
    if flex <= 0:
        return _scaled(u, W, 'columns not recognised')
    k = (W - sum(w for w in fixed_w if w is not None)) / flex
    if k < 0.3:
        return _scaled(u, W, 'columns too narrow')
    new_w = [fw if fw is not None else w * k for fw, w in zip(fixed_w, old_w)]
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
        sc = _subcolumns(ws, cx0(c), old_w[c], new_w[c], pitch)
        if sc is not None:
            paras_of[(b, c)], cum_ = sc
            band_extra[b] = max(band_extra[b], cum_)
            continue
        out, cum = [], 0
        for p in _paragraphs(_groups(ws), cx0(c) + old_w[c], cx0(c), guidance=sum(not f for f in fixed) >= 2 and c == max(i for i in range(ncol) if not fixed[i])):
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
                lo = min([0.0] + [r[0] for r in rl if r[0] > -5]) if c == 0 else cx0(c)    # the label column starts at the table's left border (or the page edge)
                ow = (edges[0] - lo) if c == 0 else old_w[c]
                nw = (new_edges[0] - lo) if c == 0 else new_w[c]
                ns = lo if c == 0 else nx_start(c)
                # the words of one line move as ONE piece ('8 (a)(ii)' label 2019 MJ 32 q8, '2 × 1' marks 2016 ON 62 q5)
                grp = [o for o in ws if abs(o['y'] - t['y']) < 2]
                gx0 = min(o['x'] for o in grp); gw = max(o['x'] + o['w'] for o in grp) - gx0
                lg, rg = gx0 - lo, lo + ow - (gx0 + gw)                                 # gaps to the column's left / right edge
                if c != 0 and lg < rg - 3:
                    gx = ns + lg                                                          # left-aligned
                elif c != 0 and rg < lg - 3:
                    gx = ns + nw - rg - gw                                                # right-aligned (marks)
                else:
                    gx = ns + max(0.0, (nw - gw) / 2)                                     # centred (question label)
                nt['x'] = round(gx + (t['x'] - gx0), 2)
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
    # pictures keep their size (shrunk only if wider than their column); text must not sit beside them
    for pc in pics:
        c = col_of(pc['x'])
        if fixed[c]:
            return _scaled(u, W, 'picture in a narrow column')
        b = next((i for i in range(nb) if bounds[i] <= pc['y'] + 1 < bounds[i + 1]), nb - 1)
        if any(t['x'] < pc['x'] + pc['w'] and t['x'] + t['w'] > pc['x'] and t['y'] > pc['y'] - 2 and t['y'] - t['s'] < pc['y'] + pc['h']
               for (bb, cc), ws in cells.items() if cc == c for t in ws):
            return _scaled(u, W, 'picture with text beside it')
        rel = pc['x'] - cx0(c)
        room = new_w[c] - rel - 6
        kk = min(1.0, room / pc['w']) if room > 0 else 0
        if kk < 0.6:                              # (MS rules 13: never below 60 % - the cell layout gives it a line of its own)
            return _scaled(u, W, 'picture too wide')
        if any(o is not pc and col_of(o['x']) == c and o['y'] < pc['y'] + pc['h'] and o['y'] + o['h'] > pc['y']
               for o in pics):                    # pictures side by side are laid out together (one picture if they touch)
            return _scaled(u, W, 'pictures side by side')
        ny = pc['y'] + shift[b] + pitch * cum_above(b, pc['y'])
        if pc['kind'] == 'image':
            v.setdefault('images', []).append(dict(pc['ref'], x=round(nx_start(c) + rel, 2), y=round(ny, 2), w=round(pc['w'] * kk, 2), h=round(pc['h'] * kk, 2)))
        else:
            v['figs'].append(dict(pc['ref'], x=round(nx_start(c) + rel, 2), y=round(ny, 2), k=round(kk, 4)))
    # a word printed across the row's bottom line (Cambridge overflow, 'NOT -4' 2026 MJ 32 q9(b)(i)): the row grows to hold it
    low = max([n['y'] + 0.3 * n.get('s', 10) for n in v['text']] + [0])
    if low > v['h'] - 2:
        v['h'] = round(low + 4, 2)
    # rules, redrawn at the new size
    T = 0.48
    def rect(x0, y0, x1, y1):
        return {'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}L{x0:.2f} {y1:.2f}Z', 'fill': rfill}
    bnew = [b0 + shift[i] for i, b0 in enumerate(bounds[:-1])] + [v['h']]
    left = min([0.0] + [r[0] for r in hs if r[0] > -5])
    xr = min(W, W - (Wo - max([r[2] for r in hs] + [edges[-1]])))          # the table's right end (rules stop at the right border)
    for i in range(nb):
        y0 = 0 if i == 0 else bnew[i] + T
        for e in new_edges + outer:
            v['lines'].append(rect(e - T / 2, y0, e + T / 2, bnew[i + 1]))
    for i in range(1, nb):
        full = any(r[0] < edges[0] - 5 and abs((r[1] + r[3]) / 2 - bounds[i]) < 2 for r in hs)
        real = [c for c in range(ncol) if old_w[c] >= 20]
        if all(cross[(i, c)] for c in real[1:]):
            v['lines'].append(rect(left if full else new_edges[0], bnew[i], xr, bnew[i] + T))
            continue
        for c in real[(0 if full else 1):]:      # only across the columns it crosses in the print
            if c == 0 or cross[(i, c)]:
                x0_ = left if c == 0 else new_edges[c - 1]
                x1_ = xr if c == real[-1] else new_edges[c]
                v['lines'].append(rect(x0_, bnew[i], x1_, bnew[i] + T))
    v['lines'].append(rect(left, v['h'] - T, xr, v['h']))
    segs = collections.defaultdict(list)                       # new line (rounded y) -> [x0, x1, y, rect-thickness]
    for r in decor:
        under = [(o, n) for o, n in moved if o['s'] >= 5 and 0.5 <= r[1] - o['y'] <= max(4.5, 0.6 * o['s']) and (
                 (r[0] - 1.5 <= o['x'] + 0.2 * o['w'] and o['x'] + 0.8 * o['w'] <= r[2] + 1.5)
                 or (r[0] >= o['x'] - 2 and r[2] <= o['x'] + o['w'] + 2 and r[2] - r[0] > 4)   # part of one word ("evaporation/evaporated", '4.0')
                 or (r[2] - r[0] <= 5 and (abs(r[0] - o['x'] - o['w']) <= 2.5 or abs(r[2] - o['x']) <= 2.5
                                           or o['x'] - 1 <= r[0] and r[2] <= o['x'] + o['w'] + 1)))]   # the underline's bit under a space or ')'
        below = [o for o, n in moved if r[0] <= o['x'] + o['w'] / 2 <= r[2] and 0 < o['y'] - r[3] < 9 and o['y'] - 0.75 * o['s'] < r[3] + 1.5 and o['s'] >= 5]
        if not below:                                  # a denominator one line down, wholly under the bar (2019 ON 43 q5 '1700 / 1000')
            dn = [o for o, n in moved if o['s'] >= 5 and 0 < o['y'] - r[3] < 14 and r[0] - 2 <= o['x'] and o['x'] + o['w'] <= r[2] + 2]
            def chunk(seed):                           # the run of words on seed's baseline joined by normal word gaps
                same = sorted((o for o, n in moved if abs(o['y'] - seed['y']) < 1.5), key=lambda o: o['x'])
                i = same.index(seed); a = b_ = i
                while a > 0 and same[a]['x'] - (same[a - 1]['x'] + same[a - 1]['w']) < 6: a -= 1
                while b_ < len(same) - 1 and same[b_ + 1]['x'] - (same[b_]['x'] + same[b_]['w']) < 6: b_ += 1
                return same[a]['x'], same[b_]['x'] + same[b_]['w']
            inside = lambda ab: ab[0] >= r[0] - 3 and ab[1] <= r[2] + 3
            if dn and under and inside(chunk(dn[0])) and inside(chunk(under[0][0])):
                below = dn                                 # numerator and denominator both fit the bar: a fraction
        if below and any(re.fullmatch(r'[A-Za-z]{3,}', o['t']) and o['w'] >= 0.85 * (r[2] - r[0]) for o, n in under):
            below = []                                 # an underlined word ('area under graph'), not a fraction bar
        if not under or below:
            return _scaled(u, W, 'fraction bar or unknown mark')
        for o, n in under:
            a0 = max(0.0, r[0] - o['x']) if r[0] > o['x'] + 0.2 * o['w'] else 0.0
            a1 = min(o['w'], r[2] - o['x']) if r[2] < o['x'] + 0.8 * o['w'] else o['w']
            segs[(round(n['y'] / 2), round(r[3] - r[1], 2), round(r[1] - o['y'], 2))].append([n['x'] + a0, n['x'] + a1, n['y'] + (r[1] - o['y']), max(r[3] - r[1], 0.5)])  # a stroked zero-height line: give it ink
    for sg in segs.values():
        sg.sort()
        cur = sg[0][:]
        for a in sg[1:]:
            if a[0] - cur[1] <= 6 and abs(a[2] - cur[2]) < 1:
                cur[1] = max(cur[1], a[1])
            else:
                v['lines'].append(rect(cur[0], cur[2], cur[1], cur[2] + cur[3])); cur = a[:]
        v['lines'].append(rect(cur[0], cur[2], cur[1], cur[2] + cur[3]))
    return v, {'mode': 'wrap', 'why': '', 'extra_lines': int(sum(band_extra)), 'cols': ncol, 'bands': nb,
               'edges': edges, 'new_edges': new_edges, 'new_w': new_w, 'old_w': old_w}


def check(u, v):
    """all words of u present in v, none past the right edge."""
    problems = []
    if sorted(t['t'] for t in u['text']) != sorted(t['t'] for t in v['text']):
        problems.append('words differ')
    over = [t['t'] for t in v['text'] if t['x'] + t['w'] > v['w'] + 0.5]
    if over:
        problems.append('overflow: ' + ' '.join(over[:4]))
    return problems


MIN_LABEL, MIN_MARKS, PAD = 40.0, 40.0, 12.0


def column_widths(units, W=523.0):
    """Widths of the fixed columns (question label, marks ...) for ONE mark scheme: the widest content of any of its rows
    + 12 pt padding (label >= 40 pt, other fixed columns >= 34 pt). Columns without text keep their printed width."""
    need = collections.defaultdict(float)
    old = {}
    for u in units:
        if u['w'] <= W + 2:
            continue
        _, info = portrait_unit(u, W, probe=True)
        if not info.get('probe'):
            continue
        for key, wd in info['probe'].items():
            need[key] = max(need[key], wd)
            old[key] = info['old_w'][key[1]]
    out = {}
    for (ncol, c), wd in need.items():
        out[(ncol, c)] = old[(ncol, c)] if wd < 1 and old[(ncol, c)] < 20 else max(MIN_LABEL if c == 0 else MIN_MARKS, wd + PAD)
    return out


def portrait_header(hdr, info, W=523.0, short_q=True):
    """Header row (Question | Answer | Marks ...) drawn once at the top, in the same columns as the rows (info from portrait_unit)."""
    edges, new_edges, new_w = info['edges'], info['new_edges'], info['new_w']
    def col_of(x): return sum(1 for e in edges if e <= x + 0.5)
    nstart = lambda c: 0 if c == 0 else new_edges[c - 1]
    v = {'src': hdr['src'], 'w': round(W, 2), 'h': hdr['h'], 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    v['lines'].append({'d': f'M0 0L{W:.2f} 0L{W:.2f} {hdr["h"] - 0.5:.2f}L0 {hdr["h"] - 0.5:.2f}Z', 'fill': '#f2f2f2'})
    v['lines'].append({'d': f'M0 {hdr["h"] - 0.48:.2f}L{W:.2f} {hdr["h"] - 0.48:.2f}L{W:.2f} {hdr["h"]:.2f}L0 {hdr["h"]:.2f}Z', 'fill': '#000000'})
    bycol = collections.defaultdict(list)
    for t in sorted(hdr['text'], key=lambda t: t['x']):
        bycol[col_of(t['x'] + t['w'] / 2)].append(dict(t))
    for c, ws in bycol.items():
        if c >= len(new_w):
            continue
        for t in ws:
            if short_q and c == 0 and t['t'] == 'Question' and new_w[0] < t['w'] + 8:
                t['t'], t['w'] = 'Q', round(t['s'] * 0.78, 2)
        total = ws[-1]['x'] + ws[-1]['w'] - ws[0]['x']
        x0 = nstart(c) + (new_w[c] - total) / 2
        for t in ws:
            t['x'] = round(x0 + (t['x'] - ws[0]['x']), 2)
            v['text'].append(t)
    return v
