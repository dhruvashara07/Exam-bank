"""Portrait mark scheme of one question with OUR consistent frame (decided with Dhruv 2026-11-03).

    build(q, store) -> {'w': 523, 'h': ..., 'rows': [unit, ...], 'problems': [...], 'modes': {...}}

- header row once at the top (Q | Answer | Marks), grey;
- rows re-wrapped by ms_portrait (column widths from the content of the whole question);
- full black frame: left and right border and a line under every row;
- 'Total: n' is its own last row (label "Total" in the answer column, number under Marks).
Units are the same layout units as everywhere else (draw with store.unit_svg).
"""
import collections
import os, json, copy, re
import ms_portrait as MP

W = 523.0
FRAME = '#000000'


def _rect(x0, y0, x1, y1, fill=FRAME):
    return {'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}L{x0:.2f} {y1:.2f}Z', 'fill': fill}


def _frame(v, top=False, t=0.6, bottom_from=0.0):
    h = v['h']
    v['lines'] += [_rect(0, 0, t, h), _rect(W - t, 0, W, h), _rect(bottom_from, h - t, W, h)]
    if top:
        v['lines'].append(_rect(0, 0, W, t))


def _shift_path(d, dx):
    """Move an absolute M/L/H/V/C/Z path by dx (x only)."""
    out = []
    for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
        n = [float(x) for x in MP.NUM.findall(args)]
        if cmd in 'MLCSQT':
            n = [v + dx if i % 2 == 0 else v for i, v in enumerate(n)]
        elif cmd == 'H':
            n = [v + dx for v in n]
        out.append(cmd + ' '.join(f'{v:.2f}' for v in n))
    return ''.join(out)


def _scale_path(d, k):
    out = []
    for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
        n = [float(x) * k for x in MP.NUM.findall(args)]
        out.append(cmd + ' '.join(f'{v:.2f}' for v in n))
    return ''.join(out)


def _unshrink(u):
    """A landscape mark scheme printed shrunk onto portrait paper (2019 ON 42: 8 pt text): scale the row back up to the
    usual 11 pt so it is laid out like every other year (otherwise it would be kept as printed, tiny and without our frame)."""
    ss = sorted(t['s'] for t in u['text'] if t.get('s'))
    if not ss:
        return u
    med = ss[len(ss) // 2]
    if med >= 9.5 or u['w'] < 400:
        return u
    k = 11.0 / med
    v = copy.deepcopy(u)
    for t in v['text']:
        for key in ('x', 'y', 'w', 's'):
            if key in t:
                t[key] = round(t[key] * k, 2)
    for f in v.get('figs', []) + (v.get('images') or []) + (v.get('glyphs') or []):
        for key in ('x', 'y', 'w', 'h'):
            if key in f:
                f[key] = round(f[key] * k, 2)
        if 'k' in f or f in v.get('figs', []):
            f['k'] = round(f.get('k', 1) * k, 4)
    v['lines'] = [{**l, 'd': _scale_path(l['d'], k)} for l in v['lines']]
    v['w'] = round(u['w'] * k, 2); v['h'] = round(u['h'] * k, 2)
    return v


def _dedupe(u):
    """Some mark schemes draw each cell's text in clipped pieces that repeat a letter where they overlap
    ('ci' + 'ircuit', '1' + '0(a)'): join overlapping pieces on one baseline and drop the repeated letters."""
    ws = sorted(u['text'], key=lambda t: (round(t['y'], 1), t['x']))
    out = []
    for t in ws:
        p = out[-1] if out else None
        if p and abs(p['y'] - t['y']) < 0.6 and p.get('s') == t.get('s') and t['x'] < p['x'] + p['w'] - 0.8 and t['x'] > p['x']:
            if t['x'] + t['w'] <= p['x'] + p['w'] + 0.6 and t['t'] in p['t']:
                continue                              # a repeated piece printed inside the word ('acceptable' + 'a')
            over = max([m for m in range(1, len(t['t']) + 1) if p['t'].endswith(t['t'][:m])] + [0])
            rest = t['t'][over:]
            p = dict(p); p['t'] = p['t'] + rest; p['w'] = round(max(p['x'] + p['w'], t['x'] + t['w']) - p['x'], 2)
            out[-1] = p
            continue
        if p and abs(p['y'] - t['y']) < 0.6 and p.get('s') == t.get('s') and abs(t['x'] - (p['x'] + p['w'])) < 0.4 \
                and not p['t'][-1:] in ',;' and t['t'][:1].isalnum() and p['t'][-1:].isalnum() \
                and p.get('b') == t.get('b') and p.get('i') == t.get('i'):
            p = dict(p); p['t'] = p['t'] + t['t']; p['w'] = round(t['x'] + t['w'] - p['x'], 2)
            out[-1] = p                               # a word split into touching pieces ('a' + 'rrows')
            continue
        out.append(dict(t))
    if len(out) == len(u['text']):
        return u
    v = dict(u); v['text'] = out
    return v


def _under_images(u):
    """Words lying inside a small picture of the same label (2022 ON 41 q7, 2022 MJ 41 q9: the labels are printed as
    pictures with a hidden text copy underneath): the picture shows them, the copy would print them a second time."""
    ims = [im for im in (u.get('images') or []) if im.get('w', 0) * im.get('h', 0) < 4000]
    if not ims:
        return u
    inside = lambda t: any(im['x'] - 1 <= t['x'] and t['x'] + t['w'] <= im['x'] + im['w'] + 1
                           and im['y'] - 1 <= t['y'] - 0.7 * t.get('s', 10) and t['y'] <= im['y'] + im['h'] + 1 for im in ims)
    keep = [t for t in u['text'] if not inside(t)]
    if len(keep) == len(u['text']):
        return u
    return dict(u, text=keep)


TICK_GLYPH = re.compile(r'_(2713|2714|221a|f0fc|fc)_', re.I)


def _tidy_boxes(v):
    """Dhruv, round 19 (2024 ON 31 q7(c)): tick boxes look tidy - the tick sits in the exact centre of its box, and the
    words that label the box start a small space after it, on the box's middle line."""
    boxes = []
    for l in v.get('lines', []):
        b = MP._bbox(l['d'])
        if (b and l.get('stroke') and 8 <= b[2] - b[0] <= 26 and 8 <= b[3] - b[1] <= 26
                and abs((b[2] - b[0]) - (b[3] - b[1])) <= 4):
            boxes.append(b)
    if not boxes:
        return
    keep = []
    for g in v.get('glyphs') or []:
        b = None
        if TICK_GLYPH.search(g.get('file', '')):
            cx, cy = g['x'] + g['w'] / 2, g['y'] + g['h'] / 2
            b = next((b for b in boxes if b[0] - 4 <= cx <= b[2] + 4 and b[1] - 4 <= cy <= b[3] + 4), None)
        if b is None:
            keep.append(g); continue
        # the tick picture also caught bits of its box: drawn as a real tick character instead
        import store_text as ST
        sz = round(min(b[3] - b[1], b[2] - b[0]) * 0.75, 2)
        tw = ST._width('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '✓', sz) or sz * 0.78
        v['text'].append({'t': '✓', 'x': round((b[0] + b[2]) / 2 - tw / 2, 2), 'y': round((b[1] + b[3]) / 2 + 0.36 * sz, 2),
                          'w': round(tw, 2), 's': sz, 'f': 'symbol'})
    if v.get('glyphs'):
        v['glyphs'] = keep
    for t in v['text']:                               # ticks drawn as text
        if t['t'].strip() in ('✓', '✔', '√'):
            b = next((b for b in boxes if b[0] - 4 <= t['x'] + t['w'] / 2 <= b[2] + 4 and b[1] - 4 <= t['y'] - 0.35 * t['s'] <= b[3] + 4), None)
            if b is not None:
                t['x'] = round((b[0] + b[2]) / 2 - t['w'] / 2, 2); t['y'] = round((b[1] + b[3]) / 2 + 0.35 * t['s'], 2)
    for b in boxes:                                   # the label beside the box
        line = [t for t in v['text'] if b[2] - 3 <= t['x'] <= b[2] + 20 and b[1] - 2 <= t['y'] <= b[3] + 6]
        if not line:
            continue
        y0 = line[0]['y']
        words = sorted([t for t in v['text'] if abs(t['y'] - y0) < 1.5 and t['x'] >= b[2] - 3], key=lambda t: t['x'])
        dx = b[2] + 5 - words[0]['x']
        ny = round((b[1] + b[3]) / 2 + 0.35 * max(t['s'] for t in words), 2)
        for t in words:
            t['x'] = round(t['x'] + dx, 2); t['y'] = ny


def _full_edges(u):
    rr = MP._rules(u)
    if not rr:
        return None
    vs = [r for r in rr[0] if r[2] - r[0] < 1.3 and r[3] - r[1] > 1.5]
    cov = collections.defaultdict(float)
    xs = MP._cluster([(r[0] + r[2]) / 2 for r in vs])
    for r in vs:
        cov[min(xs, key=lambda e: abs(e - (r[0] + r[2]) / 2))] += r[3] - r[1]
    return sorted(x for x in xs if cov[x] >= 0.7 * u['h'] and x > 20)


def _common_columns(uniq):
    """A row whose printed table lost a column rule (an empty Marks cell drawn without its left line, 2024 MJ 43 q10(c))
    would be laid out with fewer columns: Q column a different width, no Marks column. It gets the missing rule back
    when the other rows of the question all have it and no word crosses it."""
    eds = [_full_edges(u) for _, u in uniq]
    common = collections.Counter(tuple(round(x) for x in e) for e in eds if e)
    if not common:
        return uniq
    std, n = common.most_common(1)[0]
    if n < 2:
        return uniq
    out = []
    for (r, u), e in zip(uniq, eds):
        if e and len(e) < len(std) and all(any(abs(x - s_) < 2 for s_ in std) for x in e):
            miss = [s_ for s_ in std if not any(abs(x - s_) < 2 for x in e)]
            if miss and not any(t['x'] < m_ < t['x'] + t['w'] for m_ in miss for t in u['text']):
                u = dict(u); u['w'] = max(u['w'], max(o_['w'] for _, o_ in uniq))   # (the cut stopped at the lost rule)
                u['lines'] = list(u['lines']) + [
                    {'d': f'M{m_ - 0.24:.2f} 0.00L{m_ + 0.24:.2f} 0.00L{m_ + 0.24:.2f} {u["h"]:.2f}L{m_ - 0.24:.2f} {u["h"]:.2f}Z',
                     'fill': '#000000'} for m_ in miss]
        out.append((r, u))
    return out


def _bottom_rule(u):
    """A row cut a few pt below its own bottom rule (2024 ON 31 q7(c): the cut ends 2.5 pt under it) would get our frame line
    too: two lines. The row ends on that rule when nothing is printed below it."""
    h = u['h']
    segs = collections.defaultdict(float)
    for l in u['lines']:
        b = MP._bbox(l['d'])
        if b is not None and b[3] - b[1] < 1.3 and h - 6 <= b[1] < h - 1.5:
            segs[round(b[1], 1)] += b[2] - b[0]
    ys_ = [y for y, wsum in segs.items() if wsum >= 0.85 * u['w']]
    if not ys_:
        return u
    y = max(ys_)
    below = [t for t in u['text'] if t['y'] - 0.7 * t.get('s', 10) > y] + \
            [f for k_ in ('figs', 'images', 'glyphs') for f in u.get(k_) or [] if f['y'] + f.get('h', 0) > y + 1]
    if below:
        return u
    v = dict(u); v['h'] = round(y + 0.5, 2); v['lines'] = _clip_lines(u['lines'], v['h'])
    return v


def _tighten(u):
    """Cut a row unit down to its table: some years print the table narrower than the cut (2016 ON: empty margins
    left and right of the borders). Without this the margins become empty 'columns'."""
    rr = MP._rules(u)
    if not rr or not u['text']:
        return u
    h = u['h']
    vs = [r for r in rr[0] if r[2] - r[0] < 1.3 and r[3] - r[1] > 1.5]
    cov = {}
    for x in MP._cluster([(r[0] + r[2]) / 2 for r in vs]):
        cov[x] = sum(r[3] - r[1] for r in vs if abs((r[0] + r[2]) / 2 - x) < 1.5)
    full = [x for x, c in cov.items() if c >= 0.7 * h]
    tmin = min(t['x'] for t in u['text']); tmax = max(t['x'] + t['w'] for t in u['text'])
    for f in u.get('figs', []) + (u.get('images') or []):
        tmin = min(tmin, f['x'])
    left = max([x for x in full if x < tmin - 1] + [None], key=lambda v: -1e9 if v is None else v)
    right = min([x for x in full if x > tmax + 1] + [None], key=lambda v: 1e9 if v is None else v)
    if left is None or left < 4:
        left = 0.0
    if right is None or u['w'] - right < 4:
        right = u['w']
    if left == 0.0 and right == u['w']:
        return u
    v = copy.deepcopy(u)
    dx = -left + 0.5 if left else 0.0
    for t in v['text']:
        t['x'] = round(t['x'] + dx, 2)
    for f in v.get('figs', []) + (v.get('images') or []) + (v.get('glyphs') or []):
        f['x'] = round(f['x'] + dx, 2)
    keep = []
    for l in v['lines']:
        b = MP._bbox(l['d'])
        if b is not None and (b[2] < left - 1 or b[0] > right + 1):
            continue                                  # outside the table
        keep.append({**l, 'd': _shift_path(l['d'], dx)})
    v['lines'] = keep
    v['w'] = round(right - left + 1.0, 2)
    return v


def _clip_lines(lines, h):
    """Drop rules that lie below h, cut those that cross it (the row is now shorter)."""
    out = []
    for l in lines:
        b = MP._bbox(l['d'])
        if b is not None and b[3] - b[1] < 3 and b[1] > h - 3.5:    # horizontal rule at/after the new bottom: our frame replaces it
            continue
        if b is None or b[3] <= h + 0.3:
            out.append(l); continue
        if b[1] >= h - 0.6:
            continue
        if b[2] - b[0] < 3 and not l.get('stroke'):          # vertical rule: shorten
            out.append({**l, 'd': f'M{b[0]:.2f} {b[1]:.2f}L{b[2]:.2f} {b[1]:.2f}L{b[2]:.2f} {h:.2f}L{b[0]:.2f} {h:.2f}Z'})
    return out


def _drop_slivers(v):
    """Vertical rules close to the right edge (the printed table's own border, a few pt inside ours): our frame replaces them."""
    keep = []
    for l in v['lines']:
        b = MP._bbox(l['d'])
        if b and b[2] - b[0] < 3 and (0.8 < b[0] < 20 or W - 20 < b[0] < W - 0.8):
            continue
        if b and b[3] - b[1] < 1.3 and b[2] - b[0] > 40 and W - 8 < b[2] < W - 0.7 and MP._bbox(l['d']) and re.fullmatch(r'M[^M]*Z?', l['d'].strip()):
            l = {**l, 'd': _rect(b[0], b[1], W, b[3])['d']}   # a row line that stops a few pt short of the frame (2023 ON 51 q4)
        keep.append(l)
    v['lines'] = keep


def _split_total(v, info):
    """Take 'Total:' and its number out of the row, if they are the last line; returns (row, total_row or None)."""
    ws = v['text']
    tot = [t for t in ws if re.fullmatch(r'Total:?', t['t'])]
    if len(tot) != 1 or info.get('mode') != 'wrap' or len([w for w in info['new_w'] if w >= 20]) != 3:
        return v, None
    T = tot[0]
    line = [t for t in ws if abs(t['y'] - T['y']) < 2.5]
    below = [t for t in ws if t['y'] > T['y'] + 2.5]
    nums = [t for t in line if t is not T and t['x'] > T['x'] and re.fullmatch(r'[\d.,]+', t['t'])]
    if below or len(nums) != 1:
        return v, None
    N = nums[0]
    lh = max(T.get('s', 11) * 1.25, 14.0)
    others = [t for t in ws if t not in (T, N)]
    v2 = copy.deepcopy(v) if others else None
    if v2 is not None:
        v2['text'] = [t for t in v2['text'] if not (abs(t['y'] - T['y']) < 2.5 and (t['t'] == T['t'] or t['t'] == N['t']))]
    cut = min(T['y'] - 3.0, max(t['y'] for t in others) + 7.0) if others else 0
    if v2 is not None:
        v2['h'] = round(cut + 1.0, 2) if cut + 1.0 < v['h'] else v['h']
    # rules that lie below the cut belong to the removed line
    if v2 is not None:
        v2['lines'] = _clip_lines(v2['lines'], v2['h'])
    nw = [w for w in info['new_w'] if w >= 20]; ne = info['new_edges'][:len(nw) - 1]
    ms0 = ne[-1]                                      # start of the marks column
    row = {'src': v['src'], 'w': W, 'h': 20.0, 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    a = dict(T); a['t'] = 'Total'; a['x'] = round(ms0 - 8 - a['w'] * 0.95, 2); a['y'] = 14.0
    b = dict(N); b['x'] = round(ms0 + (nw[-1] - b['w']) / 2, 2); b['y'] = 14.0
    row['text'] = [a, b]
    row['lines'].append(_rect(ms0 - 0.3, 0, ms0 + 0.3, 20.0))
    return v2, row


def _own_total(marks, info, rows):
    nw = [w for w in info['new_w'] if w >= 20]
    if len(nw) not in (3, 4):                         # Q | Answer | Marks (| Guidance, 2026 MJ): the total in the Marks column
        return None
    ms0 = info['new_edges'][1]
    tpl = next((dict(t) for v in rows for t in v['text'] if t.get('f')), {'s': 11.0, 'f': 'sans'})
    for k in ('i', 'c', 'role', 'u', 'dir'):
        tpl.pop(k, None)
    a = dict(tpl, t='Total', b=1, w=29.3, y=14.0); a['x'] = round(ms0 - 8 - a['w'], 2)
    num = str(marks)
    b = dict(tpl, t=num, b=1, w=round(6.1 * len(num), 2), y=14.0); b['x'] = round(ms0 + (nw[-1] - b['w']) / 2, 2)
    b['x'] = round(ms0 + (nw[2] - b['w']) / 2, 2)
    lines = [_rect(ms0 - 0.3, 0, ms0 + 0.3, 20.0)] + ([_rect(ms0 + nw[2] - 0.3, 0, ms0 + nw[2] + 0.3, 20.0)] if len(nw) == 4 else [])
    return {'src': rows[-1]['src'], 'w': W, 'h': 20.0, 'text': [a, b], 'lines': lines,
            'figs': [], 'glyphs': [], 'own_total': True}


LABEL_RE = re.compile(r'^(\d{1,2})$|^\(([a-hj-p])\)$|^\(([ivx]{1,4})\)$')   # (practical papers run to (n))
COMBO_RE = re.compile(r'^(\((?:[a-hj-p]|[ivx]{1,4})\)){2,4}$')   # one answer for several parts: '(iii)(iv)(v)', '(a)(i)(ii)', '(b)(c)'
MARK_RE = re.compile(r'^\(?(?:[ABCMP]\d{1,2}|B\d|\d)\)?$|^\[\d{1,2}\]$')
# marks-column pieces: codes, '[1]' (also printed as '[ ]' + '1', 2014 ON 63), 'max.' ('max. B2', 2015 MJ 23), '+' ('B1 + B1')
MARKISH = lambda x: bool(MARK_RE.match(x) or re.fullmatch(r'[\[\]\s]+|max\.?|\+', x))


def _old_rows(units, q, L=44.0, M=W - 44.0):
    """Old portrait mark schemes (up to 2016 FM: no table, 'n (a) answer ... B1'): put them in OUR table, like every
    other year (Dhruv 2026-11-06: 'we want each ms in our guideline layout, consistency in all ms').
    One row per question part; label 'n(a)(i)' in the Q column, answer at the normal size in the Answer column
    (re-wrapped when too wide), marks right-aligned in the Marks column; the printed '[Total: n]' goes (ours is drawn)."""
    A = M - L - 10
    qn = str(int(q['id'].rsplit('_q', 1)[1]))
    # a brace running from one printed part into the next ('(d)(i) ... } both B1 (ii)', 2014 ON 21 q10): one unit, so one row
    def tall_braces(u):
        out_ = []
        for l in u['lines']:
            pts_ = [float(x_) for x_ in MP.NUM.findall(l['d'])]
            if len(pts_) >= 4:
                b_ = (min(pts_[0::2]), min(pts_[1::2]), max(pts_[0::2]), max(pts_[1::2]))
                if b_[2] - b_[0] < 14 and b_[0] > 0.1 * u['w']:
                    out_.append(b_)
        return out_
    merged = []
    for u in units:
        prev = merged[-1] if merged else None
        if (prev is not None and prev['src']['page'] == u['src']['page'] and abs(prev['src']['box'][3] - u['src']['box'][1]) < 1
                and abs(prev['src']['box'][0] - u['src']['box'][0]) < 1
                and any(b_[3] - b_[1] > 20 and b_[3] >= prev['h'] - 2 for b_ in tall_braces(prev))
                and any(b_[1] <= 2 for b_ in tall_braces(u))):
            dy_ = prev['h']
            m_ = dict(prev); m_['h'] = round(prev['h'] + u['h'], 2)
            m_['src'] = dict(prev['src'], box=[prev['src']['box'][0], prev['src']['box'][1], prev['src']['box'][2], u['src']['box'][3]])
            m_['text'] = prev['text'] + [dict(t, y=t['y'] + dy_) for t in u['text']]
            m_['lines'] = prev['lines'] + [{**l, 'd': _map_path(l['d'], lambda x: x, lambda y, dy_=dy_: y + dy_)} for l in u['lines']]
            for k_ in ('figs', 'images', 'glyphs'):
                if prev.get(k_) or u.get(k_):
                    m_[k_] = list(prev.get(k_) or []) + [dict(f, y=f['y'] + dy_) for f in u.get(k_) or []]
            merged[-1] = m_
        else:
            merged.append(u)
    units = merged
    state = {'l': None, 'r': None}
    rows = []
    used = set()
    qparts = {p.get('path') for p in q.get('parts', [])}
    for u in units:
        ws = [t for t in u['text'] if t.get('s', 10) >= 5]
        # the printed total '[Total: 5]'
        drop = set()
        for t in ws:
            if re.fullmatch(r'\[?Total:?', t['t']):
                drop.add(id(t))
                for o in ws:
                    if abs(o['y'] - t['y']) < 2.5 and o['x'] > t['x'] and re.fullmatch(r'[\d\]\[]+', o['t']):
                        drop.add(id(o))
        ws = [t for t in ws if id(t) not in drop]
        if not ws:
            continue
        # lines by baseline; small raised/lowered pieces (cm³, ½mv², ¹³¹₅₄Xe) join the nearest normal line
        anch = sorted({round(t['y']) for t in ws if t.get('s', 11) >= 9})
        def key(t):
            y = round(t['y'])
            if t.get('s', 11) >= 9 or not anch:
                return y
            return min(anch, key=lambda a: abs(a - t['y'])) if min(abs(a - t['y']) for a in anch) <= 7 else y
        lines = collections.OrderedDict()
        for t in sorted(ws, key=lambda t: (key(t), t['x'])):
            lines.setdefault(key(t), []).append(t)
        lines = collections.OrderedDict(sorted(lines.items()))
        cand = lambda t: ((LABEL_RE.match(t['t']) or COMBO_RE.match(t['t'])) and t['x'] < 0.3 * u['w']
                          and (not t['t'].isdigit() or t['t'] == qn))   # an answer '92' is not a label (2013 MJ 23 q12)
        plain = [t for lw in lines.values() for t in lw if not cand(t) and not (t['x'] > 0.82 * u['w'] and MARKISH(t['t']))]
        indent = min([t['x'] for t in plain] + [u['w']])
        def lead_labels(lw):                          # 'n', '(a)', '(i)' at the start of a line: bold, or left of the answer text
            out_ = []                                 # (2013 MJ 51: labels printed in a plain font)
            for t in lw:
                if cand(t) and (t.get('b') or t['x'] + t['w'] <= indent + 1 or (out_ == [] and t['x'] < indent - 8 and COMBO_RE.match(t['t']))):
                    out_.append(t)
                else:
                    break
            return out_
        all_labs = {id(t) for lw in lines.values() for t in lead_labels(lw)}
        body = [t for t in ws if id(t) not in all_labs and not (t['x'] > 0.82 * u['w'] and MARKISH(t['t']))]
        ax0 = min([t['x'] for t in body]) if body else 56.0
        # split the unit at lines that start with a part label
        segs = []
        pieces_ = []
        for l in u['lines']:
            pts_ = [float(x_) for x_ in MP.NUM.findall(l['d'])]
            if len(pts_) >= 4:
                bb_ = (min(pts_[0::2]), min(pts_[1::2]), max(pts_[0::2]), max(pts_[1::2]))
                if bb_[2] - bb_[0] < 14 and bb_[0] > 0.1 * u['w'] and bb_[3] - bb_[1] > 4:
                    pieces_.append(bb_)
        pieces_.sort(key=lambda b_: b_[1])
        braces = []
        for b_ in pieces_:                            # a brace drawn in pieces (top, middle, bottom): one brace
            if braces and b_[1] <= braces[-1][3] + 3 and b_[0] < braces[-1][2] + 2 and b_[2] > braces[-1][0] - 2:
                c_ = braces[-1]; braces[-1] = (min(c_[0], b_[0]), c_[1], max(c_[2], b_[2]), max(c_[3], b_[3]))
            else:
                braces.append(b_)
        braces = [b_ for b_ in braces if b_[3] - b_[1] > 20]
        for y, lw in lines.items():
            labs = lead_labels(lw)
            # parts joined by one brace share one answer and one mark ('(d)(i) ... } both B1 (ii)', 2014 ON 21 q10): one row
            joined = labs and segs and any(b_[1] < y - 9 and y - 4 < b_[3] and b_[1] < segs[-1]['y0'] + 4 for b_ in braces)
            if joined:
                segs[-1].setdefault('more', []).extend(labs)
                lw = [t for t in lw if t not in labs]
            elif labs or not segs:
                segs.append({'y0': y, 'labs': labs, 'lines': []})
            segs[-1]['lines'].append(lw)
        for sg in segs:
            extra_lab = ''
            for t in sg['labs']:
                pieces = re.findall(r'\(([a-hj-p]|[ivx]{1,4})\)', t['t']) or [t['t']]
                for k_, pc in enumerate(pieces):
                    roman = re.fullmatch(r'[ivx]{1,4}', pc) and not (pc in ('i', 'v', 'x') and state['r'] is None and k_ == 0
                                                                         and not any(re.fullmatch(r'[a-h]', o) for o in pieces[:k_]) and False)
                    if pc.isdigit():
                        continue
                    if pc == 'i' and state['l'] == 'h' and k_ == 0:
                        state['l'], state['r'] = 'i', None    # '(i)' after '(h)' is the letter i
                        continue
                    if re.fullmatch(r'[a-hj-p]', pc):
                        if extra_lab or (k_ and re.fullmatch(r'[a-hj-p]', pieces[k_ - 1])):
                            extra_lab += f'({pc})'           # '(b)(c)': one answer for both
                        else:
                            state['l'], state['r'] = pc, None
                    elif roman:
                        if state['r'] is not None and k_ and re.fullmatch(r'[ivx]{1,4}', pieces[k_ - 1]):
                            extra_lab += f'({pc})'           # '(iii)(iv)(v)'
                        else:
                            state['r'] = pc
            for t in sg.get('more', []):                # labels joined into this row by a brace: '(d)(i)(ii)'
                extra_lab += ''.join(f'({pc})' for pc in re.findall(r'\(([a-hj-p]|[ivx]{1,4})\)', t['t']))
            label = qn + (f"({state['l']})" if state['l'] else '') + (f"({state['r']})" if state['r'] else '') + extra_lab
            base_lab = qn + (f"({state['l']})" if state['l'] else '') + (f"({state['r']})" if state['r'] else '')
            if sg['labs'] and state['l'] and state['r'] and not extra_lab and (base_lab in used or base_lab not in qparts):
                # Cambridge left out the letter ('(a)(ii)' then '(i)' meaning (b)(i), 2013 ON 31 q11): the next letter whose
                # part exists in the question paper
                for k in range(1, 4):
                    l2 = chr(ord(state['l']) + k)
                    lab2 = f"{qn}({l2})({state['r']})"
                    if lab2 in qparts and lab2 not in used:
                        state['l'], label = l2, lab2
                        break
            if sg['labs']:
                used.add(label)
            tpl = dict(next((t for lw in sg['lines'] for t in lw if not t.get('b')), sg['lines'][0][0]))
            for k in ('i', 'c', 'role', 'u', 'dir'):
                tpl.pop(k, None)
            v = {'src': u['src'], 'w': W, 'h': 0.0, 'text': [], 'lines': [], 'figs': [], 'glyphs': [], 'old_portrait': True}
            top = max(sg['lines'][0], key=lambda t: t.get('s', 11))['y'] - 14.0
            extra = 0.0; cur_y = None
            for lw in sg['lines']:
                body_l = [t for t in lw if t not in sg['labs'] and not (t['x'] > 0.82 * u['w'] and MARKISH(t['t']))]
                marks_l = [t for t in lw if t['x'] > 0.82 * u['w'] and MARKISH(t['t'])]
                ly = max(lw, key=lambda t: t.get('s', 11))['y']
                y = ly - top + extra
                dx = 0.0; start = None
                for t in body_l:
                    n = dict(t); x = L + 5 + (t['x'] - ax0) + dx
                    if start is None:
                        start = x
                    if x + t['w'] > L + 5 + A and x > start + 1:
                        dx = start - (L + 5 + (t['x'] - ax0)); extra += t.get('s', 11) * 1.25; y += t.get('s', 11) * 1.25
                        x = start
                    n['x'] = round(x, 2); n['y'] = round(y + (t['y'] - ly), 2); v['text'].append(n)
                if marks_l:
                    a_ = min(t['x'] for t in marks_l); c_ = max(t['x'] + t['w'] for t in marks_l)
                    pos = {id(t): t['x'] - a_ for t in marks_l}
                    stack = [t for t in marks_l if re.fullmatch(r'max\.?', t['t'])]
                    if stack and c_ - a_ > (W - M) - 8:       # 'max. B2': 'max.' on the line above its code
                        for t in stack:
                            n = dict(t, b=0); n['x'] = round(W - 6 - t['w'], 2)
                            n['y'] = round(max(lw, key=lambda t: t.get('s', 11))['y'] - top - 0.9 * t.get('s', 11), 2)
                            v['text'].append(n)
                        marks_l = [t for t in marks_l if t not in stack]
                        a_ = min(t['x'] for t in marks_l); c_ = max(t['x'] + t['w'] for t in marks_l)
                        pos = {id(t): t['x'] - a_ for t in marks_l}
                    if c_ - a_ > (W - M) - 10:                # 'B1   [4]' wider than our Marks column: gaps closed up
                        xx = 0.0; pos = {}
                        for t in sorted(marks_l, key=lambda t: t['x']):
                            br = re.fullmatch(r'[\[\]\s]+', t['t'])
                            pos[id(t)] = xx; xx += t['w'] + (0.5 if br else 3.0)
                        c_ = a_ + xx - 3.0
                    for t in marks_l:
                        n = dict(t, b=1 if re.fullmatch(r'\(?[ABCMP]\d{1,2}\)?', t['t']) else 0)   # only mark codes bold
                        n['x'] = round(W - 6 - (c_ - a_) + pos[id(t)], 2); n['y'] = round(max(lw, key=lambda t: t.get('s', 11))['y'] - top, 2)
                        v['text'].append(n)                   # mark codes in bold, like the later years
            # drawings and pictures (underlines, braces, fraction bars, symbols) go with the segment they are printed in
            si = segs.index(sg)
            lo_ = -1e9 if si == 0 else sg['y0'] - 12
            hi_ = 1e9 if si == len(segs) - 1 else segs[si + 1]['y0'] - 12
            def mine(y0_, y1_):
                c_ = (y0_ + y1_) / 2
                return lo_ <= c_ < hi_
            for l in u['lines']:
                pts_ = [float(x_) for x_ in MP.NUM.findall(l['d'])]
                bb = MP._bbox(l['d']) or ((min(pts_[0::2]), min(pts_[1::2]), max(pts_[0::2]), max(pts_[1::2])) if len(pts_) >= 4 else None)
                if bb is None or (min(bb[2] - bb[0], bb[3] - bb[1]) <= 1.0 and (bb[2] - bb[0] > 0.8 * u['w'] or bb[3] - bb[1] > 0.8 * u['h'])):
                    continue                          # the old frame of the row: ours instead
                if not mine(bb[1], bb[3]):
                    continue
                v['lines'].append({**l, 'd': _map_path(l['d'], lambda x: L + 5 + (x - ax0), lambda y: y - top)})
            for k_ in ('figs', 'images', 'glyphs'):
                for f in u.get(k_) or []:
                    if not mine(f['y'], f['y'] + f.get('h', 0)):
                        continue
                    g = dict(f); g['x'] = round(L + 5 + (f['x'] - ax0), 2); g['y'] = round(f['y'] - top, 2)
                    v.setdefault(k_, []).append(g)
            cw = sum(3.7 if c in '()' else 2.4 if c == 'i' else 5.5 if c in 'vx' else 6.1 for c in label)
            lab = dict(tpl, t=label, b=0, s=11.0, w=round(cw, 2))
            lab['x'] = round((L - lab['w']) / 2, 2); lab['y'] = 14.0
            v['text'].append(lab)
            bot = [t['y'] + 6 for t in v['text']] + [f['y'] + f.get('h', 0) + 4 for k_ in ('figs', 'images', 'glyphs') for f in v.get(k_) or []]
            v['h'] = round(max(bot + [20.0]), 2)
            v['lines'] += [_rect(L - 0.3, 0, L + 0.3, v['h']), _rect(M - 0.3, 0, M + 0.3, v['h'])]
            rows.append(v)
    # one part printed in several units ('(c)' continued): no new label for a row that repeats the previous label
    for a_, b_ in zip(rows, rows[1:]):
        la = [t for t in a_['text'] if t.get('s') == 11.0 and t['x'] < L and t['y'] == 14.0]
        lb = [t for t in b_['text'] if t.get('s') == 11.0 and t['x'] < L and t['y'] == 14.0]
        if la and lb and la[0]['t'] == lb[0]['t']:
            b_['text'] = [t for t in b_['text'] if t is not lb[0]]
            b_['cont'] = True
    return rows


def _cell_fallback(u, first):
    """A row the re-wrap cannot handle (inner table, drawn symbol, fraction bars ...): keep OUR columns and sizes.
    Question label and marks stay 11 pt in our columns; only the answer cell's content is scaled to fit the Answer
    column (inner tables, diodes and fractions keep their drawing). Dhruv 2026-11-05: rows must look like the others."""
    rr = []                                           # thin rules only: other drawings (arrowheads, circles) stay as content
    for l in u['lines']:
        if l.get('fill', '#000000').lower() == '#ffffff' and 'stroke' not in l:
            continue
        for sub in re.findall(r'M[^M]+', l['d']):
            bb = MP._bbox(sub)
            if bb is not None and bb[3] > 0.6 and min(bb[2] - bb[0], bb[3] - bb[1]) <= 1.3:
                rr.append(bb)
    vs = [r for r in rr if r[2] - r[0] < 1.3 and r[3] - r[1] > 1.5]
    cov = {}
    for x in MP._cluster([(r[0] + r[2]) / 2 for r in vs]):
        cov[x] = sum(r[3] - r[1] for r in vs if abs((r[0] + r[2]) / 2 - x) < 1.5)
    h = u['h']
    tot_y = [t['y'] for t in u['text'] if re.fullmatch(r'Total:?', t['t'])]
    draw_y = []                                       # drawings count as content too (2023 MJ 33 q8: symbol boxes and matching lines)
    for l in u['lines']:
        bb_ = MP._bbox(l['d'])
        if bb_ is None:
            pts_ = [float(x) for x in MP.NUM.findall(l['d'])]
            bb_ = (min(pts_[0::2]), min(pts_[1::2]), max(pts_[0::2]), max(pts_[1::2])) if len(pts_) >= 4 else None
        if bb_ is not None and not (bb_[3] - bb_[1] < 1.3 and bb_[2] - bb_[0] > 0.5 * u['w']) and not (bb_[2] - bb_[0] < 1.3 and bb_[3] - bb_[1] > 0.5 * u['h']):
            draw_y.append(bb_[3])
    ink_y = [t['y'] for t in u['text'] if not any(abs(t['y'] - y) < 2.5 for y in tot_y)] + [f['y'] + f.get('h', 0) for k_ in ('figs', 'images', 'glyphs') for f in u.get(k_) or []] + draw_y
    hy = collections.defaultdict(float)
    for r in rr:
        if r[3] - r[1] < 1.3 and r[2] - r[0] > 1.3:
            hy[round(r[1])] += r[2] - r[0]
    for y in sorted(hy):                               # an empty band under a full-width rule (2017 MJ 32 q11): not part of the row
        if hy[y] > 0.9 * u['w'] and 4 < y < h - 4 and ink_y and max(ink_y) < y:
            h = float(y); break
    full = sorted(x for x, c in cov.items() if c >= 0.6 * h and 20 < x < u['w'] - 8)
    cx_ = [t['x'] + t['w'] / 2 for t in u['text']]
    four = bool(first) and len([w for w in first['new_w'] if w >= 20]) == 4
    while len(full) >= (4 if four else 2) and not any(c > full[-1] for c in cx_):
        full.pop()                                    # the table's own right border (2016 MJ 43: 9 pt inside the cut)
                                                      # (not the Guidance rule of an empty Guidance cell, 2026 MJ 41 q8)
    left = [x for x, c in cov.items() if x <= 20 and c >= 0.6 * h]
    if len(full) == 1 and left and any(c > full[0] for c in cx_):
        full = [max(left)] + full                     # a continuation row with an empty question column (2020 MJ 31 q11, page 2)
    outer = [x for x in cov if x <= 20 or x >= u['w'] - 8 or (full and x > full[-1] + 2)]
    outer = [x for x in outer if x not in full]
    if len(full) >= 2:                                # the paper's grand total in a grey cell under the last question (2016 ON 43 q11)
        e2_ = full[-1]
        ink2 = [t['y'] for t in u['text'] if not any(abs(t['y'] - y) < 2.5 for y in tot_y)
                and not (t['x'] + t['w'] / 2 > e2_ and re.fullmatch(r'\d+', t['t']))] + \
               [f['y'] + f.get('h', 0) for k_ in ('figs', 'images', 'glyphs') for f in u.get(k_) or []] + draw_y
        for y in sorted(hy):
            if hy[y] > 0.6 * u['w'] and 4 < y < h - 4 and ink2 and max(ink2) < y:
                h = float(y); break
    guide = None
    if first:
        nw = [w for w in first['new_w'] if w >= 20]
        L = first['new_edges'][0]; M = first['new_edges'][1 if len(nw) == 4 else len(nw) - 2]
        if len(nw) == 4 and len(full) >= 3:           # Q | Answer | Marks | Guidance (2026 MJ)
            xr = max([x for x in outer if x > full[-1]] + [u['w']])
            guide = {'G': first['new_edges'][2], 'e3': full[-1], 'xr': xr}
            full = full[:-1]
    else:
        L, M = 44.0, W - 44.0
    has_marks = True
    if len(full) >= 2:
        e1, e2 = full[0], full[-1]                    # label | answer ... answer | marks
    elif first and u['text'] and not u.get('figs') and not u.get('images') and not u.get('glyphs') and len({round(t['y']) for t in u['text']}) == 1:
        return _heading_row(u, L)                     # a heading row across answer and marks ('8  Hydroelectric', 2017 ON 41)
    else:
        return None
    return _cell_layout(u, h, e1, e2, L, M, has_marks, outer, rr, cov, guide=guide)


def _heading_row(u, L):
    ws = sorted(u['text'], key=lambda t: t['x'])
    lab = ws[0] if re.fullmatch(r'\d{1,2}(\([a-z]+\))*(\([ivx]+\))*', ws[0]['t']) else None
    rest = [t for t in ws if t is not lab]
    v = {'src': u['src'], 'w': W, 'h': 20.0, 'text': [], 'lines': [_rect(L - 0.3, 0, L + 0.3, 20.0)], 'figs': [], 'glyphs': [], 'heading': True}
    if lab is not None:
        n = dict(lab); n['x'] = round((L - lab['w']) / 2, 2); n['y'] = 14.0; v['text'].append(n)
    if rest:
        x0 = rest[0]['x']
        for t in rest:
            n = dict(t); n['x'] = round(L + 5 + (t['x'] - x0), 2); n['y'] = 14.0; v['text'].append(n)
    return v


def _map_path(d, fx, fy):
    out = []
    for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
        n = [float(x) for x in MP.NUM.findall(args)]
        if cmd in 'MLCSQT':
            n = [fx(a) if i % 2 == 0 else fy(a) for i, a in enumerate(n)]
        elif cmd == 'H':
            n = [fx(a) for a in n]
        elif cmd == 'V':
            n = [fy(a) for a in n]
        out.append(cmd + ' '.join(f'{a:.2f}' for a in n))
    return ''.join(out)


def _reflow_table(TT, LL, PP, vx, A, mins_in=None, rec=None, pad=10):
    """An inner table too wide for our Answer column even with narrow columns (side-by-side 'OR' alternatives,
    2019 ON 43 q9): keep the normal font size and wrap each cell's text inside its column; rows grow taller.
    Returns (texts, lines, pics, width, ymap) in table coordinates (x from 0, y = mapped source y)."""
    cw_ = lambda x: next((c - a for a, c in zip(vx, vx[1:]) if a - 1 <= x <= c + 1), 1e9)
    hz = [b for l, b in LL if b[3] - b[1] < 1.3 and b[0] < vx[-1] - 2 and b[2] > vx[0] + 2
          and b[2] - b[0] >= 0.6 * cw_((b[0] + b[2]) / 2)]        # (an underline is not a row rule: 2019 ON 41 q6 'joined')
    vt = [b for l, b in LL if b[2] - b[0] < 1.3 and b[3] - b[1] >= 4 and vx[0] - 2 <= (b[0] + b[2]) / 2 <= vx[-1] + 2]
    ytop = min([b[1] for b in vt] + [b[1] for b in hz]); ybot = max([b[3] for b in vt] + [b[3] for b in hz])
    ys = MP._cluster([(b[1] + b[3]) / 2 for b in hz if ytop - 1 <= b[1] <= ybot + 1])
    ys = sorted(set([round(ytop, 2)] + [y for y in ys if ytop + 2 < y < ybot - 2] + [round(ybot, 2)]))
    cols = list(zip(vx, vx[1:]))
    colof = lambda x: next((j for j, (a, c) in enumerate(cols) if a - 1 <= x <= c + 1), None)
    rowof = lambda y: next((i for i, (a, c) in enumerate(zip(ys, ys[1:])) if a - 1 <= y <= c + 1), None)
    cells = {}
    for t in TT:
        j = colof(t['x'] + t['w'] / 2); i = rowof(t['y'] - 0.35 * t.get('s', 10))
        if j is None or i is None:
            return None
        cells.setdefault((i, j), []).append(t)
    old = [c - a for a, c in cols]
    mins = [max([t['w'] for (i, j), ws in cells.items() if j == jj for t in ws] + [10]) + pad for jj in range(len(cols))]
    if rec is not None:
        rec.append(mins)
    if mins_in is not None:                            # the same table design in other sub-rows: same column widths (round 18)
        mins = [max(a, b) for a, b in zip(mins, mins_in)]
    avail = A - 4
    f = avail / sum(old)
    new = [max(m, w * f) for m, w in zip(mins, old)]
    over = sum(new) - avail
    if over > 0:
        flex = [n - m for n, m in zip(new, mins)]
        if sum(flex) < over:
            return None
        new = [n - over * fl / sum(flex) for n, fl in zip(new, flex)]
    nx = [0.0]
    for w in new:
        nx.append(nx[-1] + w)
    # reflow every cell; row heights from the tallest cell
    placed, need_h = [], {}
    for (i, j), ws in cells.items():
        a, c = cols[j]; x0 = nx[j] + pad / 2.5; x1 = nx[j + 1] - pad / 2.5
        anch = []
        for y0 in sorted(t['y'] for t in ws if t.get('s', 11) >= 9):   # baselines within 3 pt are one line (big brackets)
            if not anch or y0 - anch[-1] > 3:
                anch.append(round(y0))
        def key(t):                                    # sub/superscripts (R₁, cm³) stay on their line
            if not anch:
                return round(t['y'])
            a_ = min(anch, key=lambda a: abs(a - t['y']))
            return a_ if abs(a_ - t['y']) <= (3.5 if t.get('s', 11) >= 9 else 7) else round(t['y'])
        lines_ = {}
        for t in sorted(ws, key=lambda t: (key(t), t['x'])):
            lines_.setdefault(key(t), []).append(t)
        lines_ = dict(sorted(lines_.items()))
        # a line that ran to the cell's right edge was wrapped by the printer: it goes on in the next line (2024 MJ 43 q10
        # '... intact / pipe as well cracked'); a line starting 'OR' / 'AND' / a bullet is a new line
        mer = []
        base_of, joined = {}, set()
        for lw in lines_.values():
            b_ = max(lw, key=lambda o: o.get('s', 11))['y']
            for t in lw:
                base_of[id(t)] = b_
        for k_, lw in lines_.items():
            body_ = [t for t in lw if t.get('s', 11) >= 9] or lw
            w0 = min(body_, key=lambda t: t['x'])
            if (mer and max(t['x'] + t['w'] for t in mer[-1][1]) + 3 + w0['w'] >= c - 4 and min(t['x'] for t in body_) <= a + 12
                    and not re.match(r'(OR|AND|or|and)$|[•▪–-]$', min(body_, key=lambda t: t['x'])['t'].strip())):
                joined.add(id(min(body_, key=lambda t: t['x'])))
                mer[-1] = (mer[-1][0], mer[-1][1] + list(lw))
                continue
            mer.append((k_, list(lw)))
        lines_ = dict(mer)
        first = min(t['y'] for t in ws) - ys[i]
        lh = max(t.get('s', 10) for t in ws) * 1.2
        y = first; out = []
        centred = all(abs((min(t['x'] for t in lw) + max(t['x'] + t['w'] for t in lw)) / 2 - (a + c) / 2) < 4 for lw in lines_.values()) \
            and any(min(t['x'] for t in lw) - a > 8 for lw in lines_.values())   # (a line filling its cell is not centred: 2022 ON 42 q2)
        for k, lw in enumerate(lines_.values()):
            if k:
                y += lh
            cur, row_ = x0, []
            prev = None
            for t in lw:
                gap = 0 if prev is None else (3.0 if id(t) in joined else min(max(t['x'] - (prev['x'] + prev['w']), 2.0), 6.0))
                if row_ and cur + gap + t['w'] > x1:
                    out.append(row_); row_ = []; y += lh; cur = x0; gap = 0
                n = dict(t, _sx=t['x']); n['x'] = cur + gap; n['y'] = y + (t['y'] - base_of.get(id(t), t['y']))
                row_.append(n); cur = n['x'] + t['w']; prev = t
            out.append(row_)
        for row_ in out:
            if centred and row_:
                w_ = row_[-1]['x'] + row_[-1]['w'] - row_[0]['x']; sh = (x0 + x1) / 2 - w_ / 2 - row_[0]['x']
                for n in row_:
                    n['x'] += sh
            placed += [(i, n) for n in row_]
        need_h[i] = max(need_h.get(i, 0), y + 5)
    heights = [max(need_h.get(i, 0), 14.0) for i in range(len(ys) - 1)]
    Y = [0.0]
    for hgt in heights:
        Y.append(Y[-1] + hgt)
    def ymap(y):
        if y <= ys[0]:
            return y - ys[0]
        for i, (a, c) in enumerate(zip(ys, ys[1:])):
            if y <= c:
                return Y[i] + (y - a) / max(c - a, 1) * (Y[i + 1] - Y[i])
        return Y[-1] + (y - ys[-1])
    texts = [dict(n, y=round(Y[i] + n['y'], 2), x=round(n['x'], 2)) for i, n in placed]
    unders = []                                       # underlines ('joined', 'and') move with their word
    src_of = {}
    for (i, n), m in zip(placed, texts):
        src_of[(n['t'], n.get('_sx'))] = m
    for l, b in LL:
        if b[3] - b[1] < 1.3 and not any(b is h for h in hz) and b[2] - b[0] > 1:
            o = next((t for t in TT if 0.3 <= b[1] - t['y'] <= 5 and b[0] < t['x'] + t['w'] and b[2] > t['x']), None)
            m = src_of.get((o['t'], o['x'])) if o is not None else None
            if m is not None:
                unders.append(_rect(m['x'] + (b[0] - o['x']), m['y'] + (b[1] - o['y']), m['x'] + (b[2] - o['x']), m['y'] + (b[1] - o['y']) + max(b[3] - b[1], 0.5)))
    lines = []
    for k, y in enumerate(ys):                        # row rules where the source drew them (per column)
        for j, (a, c) in enumerate(cols):
            mid = (a + c) / 2
            if any(abs((b[1] + b[3]) / 2 - y) < 1.5 and b[0] <= mid <= b[2] for b in hz):
                lines.append(_rect(nx[j], Y[k] - 0.25, nx[j + 1], Y[k] + 0.25))
    for k in (0, len(ys) - 1):                        # the table's top/bottom edge lost with the row's own border (2023 FM 42 q1)
        y = ys[k]
        if not any(abs((b[1] + b[3]) / 2 - y) < 1.5 for b in hz) and any(b[1] - 1 <= y <= b[3] + 1 for b in vt):
            lines.append(_rect(nx[0], Y[k] - 0.25, nx[-1], Y[k] + 0.25))
    for j, x in enumerate(vx):                        # column rules where the source drew them (per row)
        for i, (a, c) in enumerate(zip(ys, ys[1:])):
            mid = (a + c) / 2
            if any(abs((b[0] + b[2]) / 2 - x) < 1.5 and b[1] <= mid <= b[3] for b in vt):
                lines.append(_rect(nx[j] - 0.25, Y[i], nx[j] + 0.25, Y[i + 1]))
    pics = []
    for k_, f_ in PP:
        j = colof(f_['x']); i = rowof(f_['y'])
        if j is None or i is None:
            return None
        g = dict(f_); g['x'] = round(nx[j] + (f_['x'] - cols[j][0]) * new[j] / old[j], 2); g['y'] = round(ymap(f_['y']), 2)
        pics.append((k_, g))
    for m in texts:
        m.pop('_sx', None)
    return texts, lines + unders, pics, nx[-1], ymap


def _guide_band(v, gd_t, inb, b0, band0, guide):
    """The Guidance column of one cell (2026 MJ; MS rules 13). Paragraphs are re-wrapped to our Guidance column and start
    level with the Answer line they stood beside in the print (guide['anchors']: printed y -> our y). Fractions stay stacked
    on their line. Pictures: pictures that touch count as ONE picture; a picture keeps its printed size, shrunk only to fit
    the column and never below 60 %; a picture that would have to shrink more goes to its own full-width line under the
    row (guide['wide']). Nothing overlaps. Returns the bottom of the column's content."""
    ws = [t for t in gd_t if inb(t['y'] - 0.35 * t.get('s', 10))]
    G, e3, xr = guide['G'], guide['e3'], guide['xr']
    nw = W - G
    pics = guide.get('pics') or []
    if not ws and not pics:
        return band0
    by_line = {}
    for sy, ny in guide.get('anchors') or [(b0, band0)]:
        k_ = round(sy)                                 # one anchor per printed line: the line's first (left-most) word
        if k_ not in by_line or ny < by_line[k_][1]:
            by_line[k_] = (sy, ny)
    anchors = sorted(by_line.values())
    def ymap(y):                                       # our y for a printed y: from the last Answer line at or above it
        a_ = [p_ for p_ in anchors if p_[0] <= y + 1]
        sy, ny = a_[-1] if a_ else anchors[0]
        return ny + (y - sy)
    # fractions: numerator + denominator over a bar move as one piece on their host line
    ws = [dict(t) for t in ws]
    for k, (l, bb) in enumerate(guide.get('lines') or []):
        if bb[3] - bb[1] > 1.3 or bb[2] - bb[0] > 90:
            continue
        num = [t for t in ws if 0.3 <= bb[1] - t['y'] <= 5 and bb[0] - 1 <= t['x'] + t['w'] / 2 <= bb[2] + 1]
        den = [t for t in ws if 0 < t['y'] - bb[3] <= 13 and bb[0] - 1 <= t['x'] + t['w'] / 2 <= bb[2] + 1]
        host = [t for t in ws if num and den and min(o['y'] for o in num) + 1 < t['y'] < max(o['y'] for o in den) - 1
                and t not in num + den]
        if num and den and host:
            hy = min(host, key=lambda t: abs(t['y'] - (bb[1] + 3)))['y']
            for t in num + den:
                t['_stack'] = k; t['_hy'] = hy
    s_ = max([t.get('s', 10) for t in ws] + [10])
    pitch = round(s_ * 1.18, 2)
    items = []
    for p in MP._paragraphs(MP._groups(ws), xr, e3, guidance=True):
        y0 = min(w['y'] - 0.8 * w.get('s', 10) for ln in p['lines'] for g in ln for w in g['ws'])
        items.append((y0, 'p', p))
    rows = []
    for k_, f in sorted(pics, key=lambda kf: kf[1]['y']):
        if rows and f['y'] < max(g['y'] + (g.get('h') or 0) for _, g in rows[-1]) - 2:
            rows[-1].append((k_, f))
        else:
            rows.append([(k_, f)])
    for r in rows:
        items.append((min(f['y'] for _, f in r), 'r', r))
    items.sort(key=lambda it: it[0])
    bot, moved, prev = band0, [], None
    for y_src, kind, it in items:
        y = max(ymap(y_src), bot + (2 if kind == 'r' else 0))
        if prev is not None and prev[0] == 'r':      # text printed right under a picture follows it (the picture may be smaller)
            y = bot + max(2.0, min(y_src - prev[1], 6.0))
        if kind == 'r':
            it = sorted(it, key=lambda kf: kf[1]['x'])
            tw = (max(f['x'] + (f.get('w') or 0) for _, f in it) - min(f['x'] for _, f in it))   # touching = one picture
            k = min(1.0, (nw - 6) / tw) if tw else 1.0
            if k < 0.6:
                guide.setdefault('wide', []).append(it)      # too small in the column: a line of its own under the row
                continue
            x_base = min(f['x'] for _, f in it)
            x = G + 3 + max(0.0, (nw - 6 - tw * k) / 2)
            hmax = 0.0
            for k_, f in it:
                g = dict(f); g['x'] = round(x + (f['x'] - x_base) * k, 2); g['y'] = round(y + (f['y'] - y_src) * k, 2)
                if 'w' in g: g['w'] = round(g['w'] * k, 2)
                if 'h' in g: g['h'] = round(g['h'] * k, 2)
                if k_ == 'figs': g['k'] = round(f.get('k', 1) * k, 4)
                v.setdefault(k_, []).append(g)
                hmax = max(hmax, (g['y'] - y) + (g.get('h') or 0))
            bot = y + hmax + 2
            prev = ('r', max(f['y'] + (f.get('h') or 0) for _, f in it))
        else:
            prev = ('p', 0)
            rel = {'lines': [[dict(g, x=g['x'] - e3) for g in ln] for ln in it['lines']]}
            wl = MP._wrap(rel, nw - 2)
            g0 = it['lines'][0][0]; m0 = g0['ws'][0]
            base = y + 0.8 * m0.get('s', 10) if 'ref_y' not in g0 else y + 0.8 * s_
            first_ref = g0.get('ref_y', m0['y'])
            for j, ln in enumerate(wl):
                stacked = any('ref_y' in g for g, gx in ln)
                if stacked:
                    base += 0.45 * s_                  # room for a fraction's numerator
                for g, gx in ln:
                    m = g['ws'][0]; ref = g.get('ref_y', m['y'])
                    for w in g['ws']:
                        n = dict(w); n['x'] = round(G + gx + (w['x'] - m['x']), 2)
                        n['y'] = round(base + j * pitch + (w['y'] - ref), 2)
                        for k2 in ('_stack', '_hy'):
                            n.pop(k2, None)
                        v['text'].append(n); bot = max(bot, n['y'] + 4); moved.append((w, n))
                if stacked:
                    base += 0.45 * s_                  # ... and for its denominator
    for l, bb in guide.get('lines') or []:            # each drawing moves with the word it touches (or the nearest one)
        if not moved:
            break
        def dist(w):
            dx_ = max(w['x'] - bb[2], bb[0] - (w['x'] + w['w']), 0)
            dy_ = max((w['y'] - 0.8 * w.get('s', 10)) - bb[3], bb[1] - (w['y'] + 0.25 * w.get('s', 10)), 0)
            return dx_ + 2 * dy_
        w, n = min(moved, key=lambda wn: dist(wn[0]))
        if dist(w) > 12:
            continue
        ddx, ddy = n['x'] - w['x'], n['y'] - w['y']
        v['lines'].append({**l, 'd': _map_path(l['d'], lambda x: x + ddx, lambda y: y + ddy)})
    return bot + 1


def _cell_layout(u, h, e1, e2, L, M, has_marks, outer, rr, cov=(), force=None, guide=None):
    """Dhruv 2026-11-05 (round 13): rows drawn cell-wise keep the NORMAL font size; the row grows instead.
    The answer cell is laid out band by band (bands = its sub-rows): an inner table gets narrower columns to fit its
    content; a text-only band that is too wide is re-wrapped; only a band with fractions/drawings that still does not
    fit is shrunk (just that band)."""
    T_ = 0.6
    WR = guide['G'] if guide else W               # right end of OUR marks column (Guidance follows, 2026 MJ)
    e3 = guide['e3'] if guide else 1e9
    A = M - L - 10                                    # room in our answer column
    v = {'src': u['src'], 'w': W, 'h': 0, 'text': [], 'lines': [], 'figs': [], 'glyphs': [], 'cell_scaled': 1.0}
    cy = lambda t: t['y'] - 0.35 * t.get('s', 10)
    ans_t = [t for t in u['text'] if e1 < t['x'] + t['w'] / 2 < e2 and t['y'] < h - 1]
    lab_t = [t for t in u['text'] if t['x'] + t['w'] / 2 < e1 and t['y'] < h - 1]
    mrk_t = [t for t in u['text'] if e2 < t['x'] + t['w'] / 2 < e3 and t['y'] < h - 1]
    gd_t = [t for t in u['text'] if t['x'] + t['w'] / 2 > e3 and t['y'] < h - 1]
    ans_l = []
    for l in u['lines']:
        if (l.get('fill') or '').lower() in ('#ffffff', '#fff') and not l.get('stroke') or (l.get('stroke') or '').lower() in ('#ffffff', '#fff'):
            continue                                  # white paint (a hidden line, 2022 MJ 41 q9): nothing to draw
        b = MP._bbox(l['d'])
        if b is None:
            bb = [MP._bbox(sub) for sub in re.findall(r'M[^M]+', l['d'])]
            b = None if any(x is None for x in bb) or not bb else (min(x[0] for x in bb), min(x[1] for x in bb), max(x[2] for x in bb), max(x[3] for x in bb))
        if b is None:                                 # a curve (brace, arc): keep it, place it by its first point
            allp = [float(x) for x in MP.NUM.findall(l['d'])]
            pts = allp[:2]
            if len(pts) == 2 and e1 < pts[0] < e2 and pts[1] < h:
                cb = (min(allp[0::2]), min(allp[1::2]), max(allp[0::2]), max(allp[1::2]))
                if cb[3] - cb[1] > 20 and cb[2] - cb[0] < 14:   # a tall brace: its whole box (it is stretched to its lines)
                    ans_l.append((l, cb)); continue
                ans_l.append((l, (pts[0], pts[1], pts[0], pts[1]))); continue
            continue
        if b[2] - b[0] < 1.3 and any(abs((b[0] + b[2]) / 2 - e) < 2 for e in [e1, e2] + outer):
            continue                                  # a column rule: ours are drawn instead
        if b[0] < e1 - 2 or b[2] > e2 + 2 or b[1] >= h - 1.5:
            continue
        if b[3] - b[1] < 1.3 and (b[1] <= 3.5 or b[3] >= h - 1.5) and b[2] - b[0] >= 0.85 * (e2 - e1):
            continue                                  # the row's own top/bottom border: ours instead (an inner table's own edge stays)
        if b[1] < -0.5 and b[3] <= 3.2:
            continue                                  # a strip of the header row above (grey, 2020 MJ 31 q11)
        ans_l.append((l, b))
    # a sub-row rule runs across the whole answer cell; an inner table's own edge stops short of it (2023 FM 42 q1)
    is_sep = lambda b: b[3] - b[1] < 1.3 and b[0] <= e1 + 4 and b[2] >= e2 - 4
    seps = MP._cluster([(b[1] + b[3]) / 2 for l, b in ans_l if is_sep(b)])
    sep_m = {y: any(r[3] - r[1] < 1.3 and abs((r[1] + r[3]) / 2 - y) < 1.5 and r[2] > e2 + 5 for r in rr) for y in seps}
    sep_g = {y: any(r[3] - r[1] < 1.3 and abs((r[1] + r[3]) / 2 - y) < 1.5 and r[2] > e3 + 5 for r in rr) for y in seps}
    gstate = {'start': None, 'y0': 0.0, 'bot': 0.0}   # a Guidance cell spanning several Answer sub-rows (no rule across it)
    def g_open(i, band0, b0):
        if not guide:
            return
        guide.setdefault('anchors', []).append((b0 - 0.01, band0))   # (the band's top; its lines' own anchors come first)
        if gstate['start'] is not None:
            return
        j = i
        while j < len(seps) and not sep_g.get(seps[j], True):
            j += 1                                    # bands i..j share one Guidance cell
        gstate.update(start=i, end=j, band0=band0, lo_y=b0)
    def g_close(i, cum):
        if not guide or gstate['start'] is None or i < gstate['end']:
            return cum
        lo, hi = bounds[gstate['start']], bounds[gstate['end'] + 1]
        last = gstate['end'] + 1 == len(bounds) - 1
        inb_g = lambda y: lo <= y < hi or (last and y >= hi)
        guide['pics'] = [(k_, f) for k_, f in gpics if inb_g(f['y'] + f.get('h', 0) / 2)]
        guide['lines'] = [(l, bb) for l, bb in glines if inb_g((bb[1] + bb[3]) / 2)]
        g_ = dict(guide); g_['anchors'] = [a for a in guide['anchors'] if a[0] >= gstate['lo_y'] - 1]
        bot = _guide_band(v, gd_t, inb_g, lo, gstate['band0'], g_)
        if g_.get('wide'):
            guide.setdefault('wide', []).extend(g_['wide'])
        gstate['start'] = None
        return max(cum, bot)
    ans_l = [(l, b) for l, b in ans_l if not is_sep(b)]
    pics = [(key, f) for key in ('figs', 'images', 'glyphs') for f in (u.get(key) or []) if f['x'] < e3]
    gpics = [(key, f) for key in ('figs', 'images', 'glyphs') for f in (u.get(key) or []) if f['x'] >= e3 - 2]
    glines = []                                        # drawings in the Guidance cell (root signs, fraction bars): move with their word
    if guide:
        for l in u['lines']:
            if (l.get('fill') or '').lower() in ('#ffffff', '#fff') and not l.get('stroke'):
                continue
            pts = [float(x) for x in MP.NUM.findall(l['d'])]
            if len(pts) < 4:
                continue
            bb = (min(pts[0::2]), min(pts[1::2]), max(pts[0::2]), max(pts[1::2]))
            if bb[0] < e3 + 1 or bb[1] >= h - 1.5 or (bb[3] - bb[1] < 1.3 and bb[2] - bb[0] > 0.8 * (u['w'] - e3)):
                continue                              # outside, or a rule of the cell
            if bb[2] - bb[0] < 1.3 and bb[3] - bb[1] > 0.6 * h:
                continue
            if any(f['x'] - 2 <= bb[0] and bb[2] <= f['x'] + (f.get('w') or 0) + 2 and f['y'] - 4 <= bb[1]
                   and bb[3] <= f['y'] + (f.get('h') or 0) + 2 for _, f in gpics):
                continue                              # drawn over a picture: part of the picture
            glines.append((l, bb))
    bounds = [0.0] + seps + [h]
    lines_m = {}
    for t in mrk_t:
        lines_m.setdefault(round(t['y']), []).append(t)
    lines_l = {}
    for t in lab_t:
        lines_l.setdefault(round(t['y']), []).append(t)
    span = lambda ws: (min(w['x'] for w in ws), max(w['x'] + w['w'] for w in ws))
    cum, sep_new, kmin, end_full = 0.0, [], 1.0, None
    tabs = {}                                          # inner-table design (its column rules) -> [mins per band], reflowed?
    for i in range(len(bounds) - 1):
        b0, b1 = bounds[i], bounds[i + 1]
        inb = lambda y: b0 <= y < b1 or (i == len(bounds) - 2 and y >= b1)
        cut_ = sum(min(r[3], b1) - max(r[1], b0) for r in rr if r[2] - r[0] < 1.3 and abs((r[0] + r[2]) / 2 - e1) < 2 and r[3] > b0 and r[1] < b1)
        spanning = cut_ < 0.4 * (b1 - b0)            # a band across all columns ('Additional graph notes', 2020 ON 51 q4)
        if spanning and not any(sum(min(r[3], b1) - max(r[1], b0) for r in rr if r[2] - r[0] < 1.3 and abs((r[0] + r[2]) / 2 - x_) < 2
                                    and r[3] > b0 and r[1] < b1) >= 0.4 * (b1 - b0) for x_ in cov):
            continue                                  # text under the table, outside every cell ('Additional graph notes' below
                                                      # the table, 2020 ON 51 q4): general notes, not this question's answer
        if spanning:
            TT = [t for t in u['text'] if inb(cy(t)) and t['y'] < h - 1]
            e1b = min([t['x'] for t in TT] + [e1]) - 0.5
        else:
            TT = [t for t in ans_t if inb(cy(t))]
            e1b = e1
        LL = [(l, b) for l, b in ans_l if inb((b[1] + b[3]) / 2)]
        PP = [(k_, f) for k_, f in pics if inb(f['y'] + f.get('h', 0) / 2)]
        # an inner table: narrower columns, just wide enough for their content
        vx = MP._cluster([(b[0] + b[2]) / 2 for l, b in LL if b[2] - b[0] < 1.3 and b[3] - b[1] >= 6])
        if vx and not spanning and any(t['x'] + t['w'] / 2 < vx[0] for t in TT) and any(t['x'] + t['w'] / 2 > vx[-1] for t in TT):
            vx = [e1b + 0.5] + vx + [e2 - 0.5]          # columns filling the answer cell ('A ... | or | ... B', 2019 ON 43 q9, 41 q6)
        cols, chunk = [], {}
        if len(vx) >= 2:
            needs = []
            for a_, c_ in zip(vx, vx[1:]):
                ws = [t for t in TT if a_ < t['x'] + t['w'] / 2 < c_]
                byl = {}
                big = sorted({round(t['y']) for t in ws if t.get('s', 11) >= 9})
                for t in ws:                          # a sub/superscript belongs to its line ('a²', 2024 MJ 42 q1)
                    k_ = round(t['y'])
                    if t.get('s', 11) < 9 and big:
                        a_k = min(big, key=lambda b_: abs(b_ - t['y']))
                        if abs(a_k - t['y']) <= 7:
                            k_ = a_k
                    byl.setdefault(k_, []).append(t)
                wmax = 0.0
                for g in byl.values():                # a cell's line ('(output of AND)') moves as one piece
                    ga, gb = min(t['x'] for t in g), max(t['x'] + t['w'] for t in g)
                    for t in g:
                        chunk[id(t)] = (ga, gb)
                    wmax = max(wmax, gb - ga)
                needs.append((a_, c_, wmax + 12))
            tw_old = vx[-1] - vx[0]
            room = A - (vx[0] - e1b) - max(0.0, max([t['x'] + t['w'] for t in TT] + [vx[-1]]) - vx[-1]) - 4
            f = 1.0
            if tw_old > room:                         # shrink the columns only as much as needed, never below their content
                lo, hi = 0.0, 1.0
                for _ in range(30):
                    m_ = (lo + hi) / 2
                    if sum(max(nd, (c_ - a_) * m_) for a_, c_, nd in needs) > room: hi = m_
                    else: lo = m_
                f = lo
            cols = [(a_, c_, min(c_ - a_, max(nd, (c_ - a_) * f))) for a_, c_, nd in needs]
        def fxc(x, cols=cols):
            if not cols or x <= cols[0][0]:
                return x
            na = cols[0][0]
            for a_, c_, nwid in cols:
                if x <= c_:
                    return na + (x - a_) * nwid / (c_ - a_)
                na += nwid
            return x - (cols[-1][1] - na)
        def tx(t, cols=cols):                         # a table cell's text keeps its alignment inside the narrower column
            c = t['x'] + t['w'] / 2
            ga, gb = chunk.get(id(t), (t['x'], t['x'] + t['w']))
            gc = (ga + gb) / 2
            for j, (a_, c_, nwid) in enumerate(cols):
                if a_ < c < c_:
                    na = fxc(a_); nc = fxc(gc)
                    nx = max(na + 3, min(nc - (gb - ga) / 2, na + nwid - (gb - ga) - 3))
                    return nx + (t['x'] - ga)
            return fxc(t['x'])
        vys = [b for l, b in LL if b[2] - b[0] < 1.3 and b[3] - b[1] >= 6]
        tab_y0 = min([b[1] for b in vys] + [1e9]); tab_y1 = max([b[3] for b in vys] + [-1e9])
        tab_rows = lambda t: tab_y0 - 2 <= t['y'] - 0.35 * t.get('s', 10) <= tab_y1 + 2
        note = lambda t: bool(cols) and not tab_rows(t)   # a note above/below an inner table ('1 mark for each correct response')
        R = max([tx(t) + t['w'] for t in TT] + [fxc(b[2]) for l, b in LL] + [fxc(f['x']) + f.get('w', 0) for k_, f in PP] + [e1b])
        need = R - e1b
        e1b0 = e1b
        if need > A + 0.5:                            # blank space left of the content (an indented table, 2020 FM 32 q6): use it first
            lead = min([tx(t) for t in TT if not note(t)] + [fxc(b[0]) for l, b in LL] + [fxc(f['x']) for k_, f in PP] + [R]) - e1b
            sh = min(need - A, max(0.0, lead - 6))
            e1b += sh; need -= sh
        X = lambda x: L + 5 + (x - e1b)
        decor = [(l, b) for l, b in LL]
        under = {}
        for l, b in decor:                            # underlines: they move with their word
            o = next((t for t in TT if 0.3 <= b[1] - t['y'] <= 5 and b[0] < t['x'] + t['w'] and b[2] > t['x'] and b[3] - b[1] < 1.3), None)
            under[id(l)] = o
        is_brace = lambda b: b[3] - b[1] > 20 and b[2] - b[0] < 14   # a tall bracket beside a list (2026 MJ 32 q3(b))
        pure = not PP and not cols and all(under[id(l)] is not None or is_brace(b) for l, b in decor)
        kb, moves, extra = 1.0, {}, 0.0
        tkey = tuple(round(x) for x in vx) if cols else None
        if tkey and not spanning:                      # remember each band's table needs (same design in several sub-rows)
            rm = []
            _reflow_table([t for t in TT if tab_rows(t)], LL, PP, vx, A, rec=rm)
            if rm:
                tabs.setdefault(tkey, [[], False])[0].append(rm[0])
        if (need > A + 0.5 or spanning) and pure and TT:   # re-wrap the text lines of this band (wide gaps closed up)
            # a fraction (numerator / bar / denominator) belongs to the text line it sits in (2022 FM 32 q11 '... OR 240×48/590')
            line_of = {}
            ref_y = []                                  # baselines within 1.5 pt are one line ('ρ=' 0.8 pt off its brackets, 2026 MJ 41 q2)
            for t in sorted((t for t in TT if t.get('s', 11) >= 8), key=lambda t: t['y']):
                if ref_y and t['y'] - ref_y[-1][0] <= 1.5:
                    line_of[id(t)] = ref_y[-1][1]
                else:
                    ref_y.append((t['y'], round(t['y']))); line_of[id(t)] = round(t['y'])
            for t in TT:                                # a sub/superscript ('×10ᴺ') goes with the line it sits on
                if id(t) not in line_of:
                    near = min(ref_y, key=lambda r: abs(r[0] - t['y'])) if ref_y else None
                    line_of[id(t)] = near[1] if near and abs(near[0] - t['y']) <= 7 else round(t['y'])
            for l, b in decor:
                num = [t for t in TT if 0.3 <= b[1] - t['y'] <= 5 and b[0] - 1 <= t['x'] + t['w'] / 2 <= b[2] + 1]
                den = [t for t in TT if 0 < t['y'] - b[3] <= 13 and b[0] - 1 <= t['x'] + t['w'] / 2 <= b[2] + 1]
                if num and den:
                    yn, yd = min(t['y'] for t in num), max(t['y'] for t in den)
                    host = [t for t in TT if yn + 1 < t['y'] < yd - 1 and t not in num + den]
                    if host:
                        hy = line_of[id(min(host, key=lambda t: abs(t['y'] - (b[1] + 3))))]
                        for t in num + den:
                            line_of[id(t)] = hy
            for t in TT:                                # a sub/superscript follows the word it is attached to ('2.8×10ᴺ')
                if t.get('s', 11) < 8:
                    base = [o for o in TT if o.get('s', 11) >= 8 and abs(o['y'] - t['y']) <= 7
                            and t['x'] - 3 <= o['x'] + o['w'] <= t['x'] + 1]
                    if base:
                        line_of[id(t)] = line_of[id(max(base, key=lambda o: o['x'] + o['w']))]
            rows_ = collections.OrderedDict()
            for t in sorted(TT, key=lambda t: (line_of[id(t)], t['x'])):
                rows_.setdefault(line_of[id(t)], []).append(t)
            rows_ = collections.OrderedDict(sorted(rows_.items()))
            for y_, ws in rows_.items():
                # pieces stacked over each other (a fraction) move as one token
                toks = []
                for t in sorted(ws, key=lambda t: t['x']):
                    if toks and t['x'] < max(o['x'] + o['w'] for o in toks[-1]) - 0.5 and abs(t['y'] - toks[-1][0]['y']) > 2:
                        toks[-1].append(t)
                    elif toks and t['x'] - max(o['x'] + o['w'] for o in toks[-1]) < 2.0:
                        toks[-1].append(t)                 # no space between them ('2.8×10ᴺ'): never split
                    else:
                        toks.append([t])
                tx0 = lambda tk: min(o['x'] for o in tk); tw_ = lambda tk: max(o['x'] + o['w'] for o in tk) - tx0(tk)
                span_y = max(t['y'] for t in ws) - min(t['y'] for t in ws)
                start = X(tx0(toks[0])); dx = 0.0; lh = max(t.get('s', 10) for t in ws) * 1.25 + span_y; prev = None; hang = None
                for tk in toks:
                    if prev is not None:
                        gap = (X(tx0(tk)) + dx) - (X(tx0(prev)) + moves[id(prev[0])][0] + tw_(prev))
                        if gap > 12 and (spanning or X(tx0(tk)) + dx + tw_(tk) > L + 5 + A):
                            dx -= gap - 3.5                # a wide gap (justified or column text): one space
                        elif gap > 12 and hang is None and not spanning:
                            hang = X(tx0(tk)) + dx         # 'MP2   Correct circuit ...': wrapped lines hang under 'Correct'
                    if X(tx0(tk)) + dx + tw_(tk) > L + 5 + A and X(tx0(tk)) + dx > start + 1:
                        dx = (hang if hang is not None and hang < L + 5 + A / 2 else start) - X(tx0(tk)); extra += lh
                    for t in tk:
                        moves[id(t)] = (dx, extra)
                    prev = tk
                # following lines move down by the extra lines so far (applied via moves of later words)
            for t in TT:
                if id(t) not in moves:
                    moves[id(t)] = (0.0, 0.0)
        elif (need > A + 0.5 or (force and tkey in force)) and cols and not spanning and all(vx[0] - 3 <= t['x'] + t['w'] / 2 <= vx[-1] + 3 or not tab_rows(t) for t in TT):
            full_ = abs(vx[0] - (e1b + 0.5)) < 0.01 and abs(vx[-1] - (e2 - 0.5)) < 0.01
            TT_out = [t for t in TT if not tab_rows(t)]   # a note under/over the table ('1 mark for each correct column')
            rf = _reflow_table([t for t in TT if tab_rows(t)], LL, PP, vx, (M - L + 4) if full_ else A,
                               mins_in=(force or {}).get(tkey))
            tight = False
            if rf is None and not full_:              # Dhruv, round 20: normal font size always - before any shrinking, the table
                rf = _reflow_table([t for t in TT if tab_rows(t)], LL, PP, vx, M - L + 2,   # may use the whole Answer cell with
                                   mins_in=(force or {}).get(tkey), pad=6)                 # slimmer cell padding (2026 MJ 43 q5)
                tight = rf is not None
            if rf is not None:
                tabs.setdefault(tkey, [[], False])[1] = True
            if rf is not None:                        # the table at the normal size, text wrapped inside its cells
                texts_, lines_, pics_, tw_, ymap_ = rf
                ox = L if full_ else (L + max(1.0, (M - L - tw_) / 2) if tight else L + 5 + (A - tw_) / 2)   # a table filling the cell meets our column rules (round 16)
                ytab = min([b[1] for l, b in LL if b[2] - b[0] < 1.3 and b[3] - b[1] >= 4] or [b0])   # the table's top
                oy = cum if full_ else cum + max(0.0, ytab - b0)   # a full-cell table starts on the row line (round 17)
                for n in texts_:
                    n['x'] = round(n['x'] + ox, 2); n['y'] = round(n['y'] + oy, 2); v['text'].append(n)
                for l in lines_:
                    v['lines'].append({**l, 'd': _map_path(l['d'], lambda x: x + ox, lambda y: y + oy)})
                for k_, g in pics_:
                    g['x'] = round(g['x'] + ox, 2); g['y'] = round(g['y'] + oy, 2); v.setdefault(k_, []).append(g)
                Ymap = lambda y: oy + ymap_(y)
                if has_marks:                         # the marks column's own sub-row lines, at the table's new row heights
                    for y_m in MP._cluster([(r[1] + r[3]) / 2 for r in rr if r[3] - r[1] < 1.3 and r[0] >= e2 - 2 and r[2] <= e3 + 2 and r[2] - r[0] > 5
                                            and b0 + 2 < (r[1] + r[3]) / 2 < b1 - 2 and (r[1] + r[3]) / 2 < h - 2]):
                        v['lines'].append(_rect(M, Ymap(y_m) - 0.25, WR, Ymap(y_m) + 0.25))
                for y_, ws in lines_m.items():
                    if not inb(y_ - 3):
                        continue
                    a_, c_ = span(ws)
                    for t in ws:
                        n = dict(t); n['x'] = round(WR - 6 - (c_ - a_) + (t['x'] - a_), 2)
                        n['y'] = round(cum + (t['y'] - b0) if t['y'] - 0.7 * t.get('s', 10) < ytab + 2 else Ymap(t['y']), 2)   # level with the label
                        v['text'].append(n)
                for y_, ws in lines_l.items():
                    if not inb(y_ - 3):
                        continue
                    a_, c_ = span(ws)
                    for t in ws:
                        n = dict(t); n['x'] = round((L - (c_ - a_)) / 2 + (t['x'] - a_), 2); n['y'] = round(cum + (t['y'] - b0), 2)
                        v['text'].append(n)
                tb = max([MP._bbox(l['d'])[3] for l in v['lines'][-len(lines_):] if MP._bbox(l['d'])] + [oy]) if lines_ else oy
                for t in TT_out:                      # notes keep their place above/below the table, left-aligned
                    n = dict(t); n['x'] = round(L + 5 + (t['x'] - e1b), 2)
                    n['y'] = round(cum + (t['y'] - b0) if t['y'] < tab_y0 else tb + (t['y'] - tab_y1), 2)
                    v['text'].append(n)
                g_open(i, cum, b0)
                cum = max([tb + (0 if full_ else 6)] + [n['y'] + 5 for n in v['text'] if n['x'] < WR])   # a full-cell table ends on the row line
                cum = g_close(i, cum)
                if full_ and cum > tb + 0.5:              # its column lines run on to the row line
                    for l in list(v['lines'][-len(lines_):]):
                        bb_ = MP._bbox(l['d'])
                        if bb_ and bb_[2] - bb_[0] < 1.3 and abs(bb_[3] - tb) < 0.6:
                            v['lines'].append(_rect(bb_[0], tb, bb_[2], cum))
                if i < len(bounds) - 2:
                    sep_new.append((cum, (sep_m.get(bounds[i + 1], False), sep_g.get(bounds[i + 1], False)) if guide else sep_m.get(bounds[i + 1], False)))
                elif full_:
                    end_full = cum                    # the row ends on the table's last line (no 2 pt gap under it)
                continue
            kb = A / need
        elif need > A + 0.5:
            kb = A / need
        kmin = min(kmin, kb)
        cxs = 0.0
        if (cols or PP) and not spanning and (TT or PP):
            # Dhruv, rounds 15-16: 'horizontal responsiveness' - a table or drawing keeps its ORIGINAL alignment in the answer
            # cell (centred stays centred, left stays left, right stays right), only fitted to our portrait column
            sx0 = min([t['x'] for t in TT if not note(t)] + [b[0] for l, b in LL] + [f['x'] for k_, f in PP])
            sx1 = max([t['x'] + t['w'] for t in TT if not note(t)] + [b[2] for l, b in LL] + [f['x'] + f.get('w', 0) for k_, f in PP])
            ml, mr = sx0 - e1, e2 - sx1
            nx0 = L + 5 + (fxc(sx0) - e1b) * kb; nx1 = L + 5 + (fxc(sx1) - e1b) * kb; bw = nx1 - nx0
            if abs(ml - mr) <= 0.25 * max(ml + mr, 1) + 6:
                cxs = (L + 5 + (A - bw) / 2) - nx0
            elif mr < ml:
                cxs = (L + 5 + A - bw - min(mr, 6)) - nx0
            cxs = max(L + 5 - nx0, min(cxs, L + 5 + A - nx1))
        def fy(y, dy=0.0):
            return cum + (y - b0) * kb + dy
        for t in TT:
            n = dict(t); dx, dy = moves.get(id(t), (0.0, 0.0))
            n['x'] = round(L + 5 + (tx(t) - e1b) * kb + dx + cxs, 2) if not note(t) else round(L + 5 + (t['x'] - e1b0) * kb + dx, 2)
            n['y'] = round(fy(t['y'], dy), 2)
            if kb < 1:
                n['s'] = round(t['s'] * kb, 2); n['w'] = round(t['w'] * kb, 2)
            v['text'].append(n)
            if guide and t.get('s', 11) >= 8:          # Guidance lines up with the Answer line it stood beside
                guide.setdefault('anchors', []).append((t['y'] - 0.8 * t['s'], n['y'] - 0.8 * n['s']))
        lbot = 0.0
        for l, b in LL:
            o = under.get(id(l)); dx, dy = moves.get(id(o), (0.0, 0.0)) if o is not None else (0.0, 0.0)
            if o is None and moves and not is_brace(b) and b[2] - b[0] < 40:
                # a drawn sign (root sign, bracket piece) moves with the word that follows it ('(v =)√{2×2.5/0.18}', 2026 MJ 41 q1)
                nxt = [t for t in TT if t['x'] >= b[0] - 1.5 and t['y'] - t.get('s', 10) - 4 <= b[3] and t['y'] + 4 >= b[1]]
                if nxt:
                    dx, dy = moves.get(id(min(nxt, key=lambda t: t['x'])), (0.0, 0.0))
            if o is None and moves and is_brace(b):      # a bracket stays beside its (re-wrapped) lines and spans them
                beside = [t for t in TT if b[1] - 3 <= t['y'] - 0.35 * t.get('s', 10) <= b[3] + 3 and t['x'] < b[0]]
                if beside:
                    def nyt(t):
                        return fy(t['y'], moves.get(id(t), (0, 0))[1])
                    top_t = min(beside, key=lambda t: t['y']); bot_t = max(beside, key=lambda t: t['y'])
                    ny0 = nyt(top_t) - (top_t['y'] - b[1]); ny1 = nyt(bot_t) + (b[3] - bot_t['y'])
                    nr = max(L + 5 + (tx(t) - e1b) + moves.get(id(t), (0, 0))[0] + t['w'] for t in beside)
                    sy = (ny1 - ny0) / max(b[3] - b[1], 1)
                    d_ = _map_path(l['d'], lambda x: nr + 4 + (x - b[0]), lambda y: ny0 + (y - b[1]) * sy)
                    v['lines'].append({**l, 'd': d_})
                    lbot = max(lbot, ny1)
                    continue
            if o is not None and cols and not note(o):   # an underline moves with its word (2024 MJ 42 q1 'vectors')
                d_ = _map_path(l['d'], lambda x, o=o: L + 5 + (tx(o) + (x - o['x']) - e1b) * kb + dx + cxs, lambda y: fy(y, dy))
            else:
                d_ = _map_path(l['d'], lambda x: L + 5 + (fxc(x) - e1b) * kb + dx + cxs, lambda y: fy(y, dy))
            v['lines'].append({**l, 'd': d_})
            bb_ = MP._bbox(d_)
            if bb_ is not None:
                lbot = max(lbot, bb_[3])
        if cols:                                      # the table's bottom edge was the row's own border: draw it (round 15)
            vb = max(b[3] for l, b in LL if b[2] - b[0] < 1.3 and b[3] - b[1] >= 6)
            has_bottom = any(b[3] - b[1] < 1.3 and abs(b[1] - vb) < 2 and b[0] <= vx[0] + 2 and b[2] >= vx[-1] - 2 for l, b in LL)
            if not has_bottom:
                x0_ = L + 5 + (fxc(vx[0]) - e1b) * kb + cxs; x1_ = L + 5 + (fxc(vx[-1]) - e1b) * kb + cxs
                v['lines'].append(_rect(x0_ - 0.25, fy(vb) - 0.5, x1_ + 0.25, fy(vb)))
                lbot = max(lbot, fy(vb))
        for k_, f in PP:
            g = dict(f); g['x'] = round(L + 5 + (fxc(f['x']) - e1b) * kb + cxs, 2); g['y'] = round(fy(f['y']), 2)
            if kb < 1:
                if 'w' in g: g['w'] = round(g['w'] * kb, 2)
                if 'h' in g: g['h'] = round(g['h'] * kb, 2)
                if k_ == 'figs': g['k'] = round(f.get('k', 1) * kb, 4)
            v.setdefault(k_, []).append(g)
        if has_marks and not spanning:               # the marks column's own sub-row lines (2021 ON 32 q6(a))
            for y_m in MP._cluster([(r[1] + r[3]) / 2 for r in rr if r[3] - r[1] < 1.3 and r[0] >= e2 - 2 and r[2] <= e3 + 2 and r[2] - r[0] > 5
                                    and b0 + 2 < (r[1] + r[3]) / 2 < b1 - 2 and (r[1] + r[3]) / 2 < h - 2]):
                v['lines'].append(_rect(M, fy(y_m) - 0.25, WR, fy(y_m) + 0.25))
        for y_, ws in lines_m.items():                # marks: right-aligned in our marks column, at the band's top offset
            if spanning or not inb(y_ - 3):
                continue
            a_, c_ = span(ws)
            for t in ws:
                n = dict(t); n['x'] = round(WR - 6 - (c_ - a_) + (t['x'] - a_), 2); n['y'] = round(cum + (t['y'] - b0), 2)
                v['text'].append(n)
        for y_, ws in lines_l.items():                # question label: centred in our label column
            if spanning or not inb(y_ - 3):
                continue
            a_, c_ = span(ws)
            for t in ws:
                n = dict(t); n['x'] = round((L - (c_ - a_)) / 2 + (t['x'] - a_), 2); n['y'] = round(cum + (t['y'] - b0), 2)
                v['text'].append(n)
        bot = [n['y'] + 5 for n in v['text'] if n['x'] < WR]
        g_open(i, cum, b0)
        cum = max([(b1 - b0) * kb + extra + cum] + [y for y in bot] + ([lbot + 6] if cols else []))   # room under an inner table's edge
        cum = g_close(i, cum)
        if i < len(bounds) - 2:
            sep_new.append((cum, (sep_m.get(bounds[i + 1], False), sep_g.get(bounds[i + 1], False)) if guide else sep_m.get(bounds[i + 1], False)))
    if force is None:
        # Dhruv, round 18 (2023 FM 42 q1): the same inner table in several sub-rows keeps ONE design - if one of them has
        # to be re-wrapped, all of them are, with the same column widths (the widest each column needs)
        f_ = {k: [max(c) for c in zip(*ms_)] for k, (ms_, rfl) in tabs.items() if rfl and len(ms_) >= 2}
        if f_:
            return _cell_layout(u, h, e1, e2, L, M, has_marks, outer, rr, cov, force=f_, guide=guide)
    wide_y = None
    if guide and guide.get('wide'):                   # Guidance pictures too wide for the column: a full-width line under the row
        wide_y = cum + 2
        y_ = wide_y + 4
        for it in guide['wide']:
            tw = max(f['x'] + (f.get('w') or 0) for _, f in it) - min(f['x'] for _, f in it)
            k = min(1.0, (W - L - 10) / tw) if tw else 1.0
            x_base, y_base = min(f['x'] for _, f in it), min(f['y'] for _, f in it)
            x0_ = L + max(5.0, (W - L - tw * k) / 2)
            hmax = 0.0
            for k_, f in it:
                g = dict(f); g['x'] = round(x0_ + (f['x'] - x_base) * k, 2); g['y'] = round(y_ + (f['y'] - y_base) * k, 2)
                if 'w' in g: g['w'] = round(g['w'] * k, 2)
                if 'h' in g: g['h'] = round(g['h'] * k, 2)
                if k_ == 'figs': g['k'] = round(f.get('k', 1) * k, 4)
                v.setdefault(k_, []).append(g)
                hmax = max(hmax, (g['y'] - y_) + (g.get('h') or 0))
            y_ += hmax + 4
        v['lines'].append(_rect(L, wide_y, W, wide_y + T_ * 0.8))
        cum = y_ + 2
        end_full = None
    v['h'] = round(cum if end_full is not None and abs(end_full - cum) < 0.01 else cum + 2, 2)
    v['cell_scaled'] = round(kmin, 3)
    for y, into_m in sep_new:
        if y >= cum - 0.5:
            continue                                  # the bands below were dropped: the row's own bottom border is enough
        if guide:                                     # Marks: into the marks column; Guidance: only where its own rule is
            into_m, into_g = into_m
            v['lines'].append(_rect(L, y, (W if into_g else WR) if into_m else M, y + T_ * 0.8))
            continue
        v['lines'].append(_rect(L, y, W if into_m else M, y + T_ * 0.8))
    v['lines'].append(_rect(L - 0.3, 0, L + 0.3, v['h']))
    if has_marks:
        v['lines'].append(_rect(M - 0.3, 0, M + 0.3, wide_y if wide_y else v['h']))
    if guide:
        v['lines'].append(_rect(WR - 0.3, 0, WR + 0.3, wide_y if wide_y else v['h']))
    return v


def build(q, store):
    sizes = {f['id']: tuple(f['size_pt']) for f in q.get('figures', [])}
    rows = [(r, u) for p in q['parts'] for r in p['ms'] for u in r['layout']]
    seen, uniq = set(), []
    for r, u in rows:                                 # one mark-scheme row can belong to several parts: once
        k = (u['src']['page'], tuple(u['src']['box']))
        if k not in seen:
            seen.add(k); uniq.append((r, u))
    if not uniq:
        return None
    uniq.sort(key=lambda ru: (ru[1]['src']['page'], ru[1]['src']['box'][1]))   # the mark scheme's own order (2017 ON 41 q8: 8 Hydroelectric (a)(b)(c), 8 Tidal flow (a)(b)(c) ...)
    uniq = [(r, _tighten(_under_images(_dedupe(_unshrink(_bottom_rule(u)))))) for r, u in uniq]
    uniq = _common_columns(uniq)
    units = [u for _, u in uniq]
    if all(u['w'] <= W + 2 for u in units):          # the old portrait era: our table too (no printed one to follow)
        first = {'edges': [], 'new_edges': [44.0, W - 44.0], 'new_w': [44.0, W - 88.0, 44.0], 'default': True}
        out = _old_rows(units, q)
        labw = max([t['w'] for v in out for t in v['text'] if t.get('s') == 11.0 and t['x'] < 44 and t['y'] == 14.0] + [0])
        if labw + 8 > 44:                             # a long label ('1(a)(i)(ii)', '3(a)(iii)(iv)(v)'): a wider Q column
            Lq_ = float(int(labw + 9))
            first = {'edges': [], 'new_edges': [Lq_, W - 44.0], 'new_w': [Lq_, W - 44.0 - Lq_, 44.0], 'default': True}
            out = _old_rows(units, q, L=Lq_)
        modes = {'old': len(out)}
        hdr = _header_unit({'src': units[0]['src'], 'text': []}, first)
        total_row = _own_total(q['marks'], first, out) if q.get('marks') else None
        out = [hdr] + out + ([total_row] if total_row else [])
        for i, v in enumerate(out[1:], 1):
            _drop_slivers(v)
            _tidy_boxes(v)
            nxt = out[i + 1] if i + 1 < len(out) else None
            _frame(v, bottom_from=first['new_edges'][0] if nxt is not None and nxt.get('cont') else 0.0)
        return {'w': W, 'h': round(sum(v['h'] for v in out), 2), 'rows': out, 'problems': [], 'modes': modes,
                'printed_total': None, 'info': {k: first[k] for k in ('edges', 'new_edges', 'new_w')}, 'has_header': True}
    widths = MP.column_widths(units)
    out, modes, problems, first = [], {}, [], None
    total_row = None
    hdr_p = os.path.join(store, 'ms_header.json')
    ncol = lambda info: len([w for w in info['new_w'] if w >= 20])
    expected = None
    if os.path.exists(hdr_p):                         # the printed header says how many columns the table has
        names_ = [n for t in json.load(open(hdr_p))['text']
                  for pat, n in NAMES if re.search(pat, t['t'].strip().lower())]
        expected = len(names_) if len(names_) >= 3 else None   # Question | Answer | Marks (| Guidance)
    for i, (r, u) in enumerate(uniq):
        v, info = MP.portrait_unit(u, widths=widths, sizes=sizes)
        if info['mode'] == 'wrap' and expected and ncol(info) > expected:
            # an inner table's lines read as extra columns (2021 FM 32 q11 carbon-12/14 table): drawn cell-wise instead
            v, info = MP._scaled(u, W, 'inner table read as columns') if hasattr(MP, '_scaled') else (u, {'mode': 'scale'})
            info = dict(info, mode='scale')
        modes[info['mode']] = modes.get(info['mode'], 0) + 1
        if info['mode'] == 'wrap':
            first = first or info
            problems += [(r['label'], p) for p in MP.check(u, v)]
        if total_row is None and info['mode'] == 'wrap' and any(re.fullmatch(r'Total:?', t['t']) for t in v['text']):
            v, total_row = _split_total(v, info)      # the printed Total can sit in any row (rows follow the parts' order)
        if v is not None:
            out.append((v, info, u))
    if first is None:                                 # no row could be re-wrapped: our default columns (Q 44 | Answer | Marks 44)
        first = {'edges': [], 'new_edges': [44.0, W - 44.0], 'new_w': [44.0, W - 88.0, 44.0], 'default': True}
    fixed = []
    for v, info, u in out:
        if info['mode'] == 'scale':
            c = _cell_fallback(u, first)
            if c is not None:
                v = c; modes['scale'] -= 1; modes['cell'] = modes.get('cell', 0) + 1
        if total_row is None and info['mode'] != 'wrap':   # a printed 'Total: n' inside a fallback row: take it out, ours instead
            tw = [t for t in v['text'] if re.fullmatch(r'Total:?', t['t'])]
            if len(tw) == 1:
                T = tw[0]
                same = [t for t in v['text'] if abs(t['y'] - T['y']) < 2.5 and t['x'] > T['x'] and re.fullmatch(r'[\d.,]+', t['t'])]
                v = dict(v); v['text'] = [t for t in v['text'] if t is not T and t not in same[:1]]
                total_row = _own_total(q['marks'], first, [v]) if q.get('marks') else None
                if not v['text'] and not v.get('figs') and not v.get('images') and not v.get('glyphs'):
                    continue                          # the row held only the printed total
        fixed.append(v)
    out = []
    for v in fixed:                                   # the PAPER's total ('[Total: 80]' under the last question, 2016 MJ 43): not ours
        pt = [t for t in v['text'] if re.fullmatch(r'\[Total:?', t['t'])]
        if pt:
            drop = {id(t) for T in pt for t in v['text'] if abs(t['y'] - T['y']) < 2.5 and t['x'] >= T['x'] - 1 and re.fullmatch(r'\[Total:?|\d+\]', t['t'])}
            v = dict(v); v['text'] = [t for t in v['text'] if id(t) not in drop]
            ty = min(T['y'] - 0.8 * T.get('s', 10) for T in pt)
            above = [t['y'] + 3 for t in v['text'] if t['y'] < ty] + [f['y'] + f.get('h', 0) for k_ in ('figs', 'images', 'glyphs') for f in v.get(k_) or []]
            if above:                                 # its own strip of the row goes too: the row ends on the rule above it
                rl_ = [b[1] for b in (MP._bbox(l['d']) for l in v['lines']) if b and b[3] - b[1] < 1.5 and b[2] - b[0] > 0.5 * v['w']
                       and max(above) - 1 <= b[1] <= ty]
                if rl_:
                    v['h'] = round(min(rl_) + 0.6, 2); v['lines'] = _clip_lines(v['lines'], v['h'])
            if not any(t['t'].strip() for t in v['text']) and not v.get('figs') and not v.get('images') and not v.get('glyphs'):
                continue
        out.append(v)
    if first and os.path.exists(hdr_p):
        out.insert(0, _header_unit(json.load(open(hdr_p)), first))
    def printed_total(v):                             # 'Total: 6' on its own (not 'Total p.d. = ...' inside an answer)
        for t in v['text']:
            if re.fullmatch(r'Total:?', t['t']):
                after = sorted((o for o in v['text'] if abs(o['y'] - t['y']) < 2.5 and o['x'] > t['x']), key=lambda o: o['x'])
                if len(after) == 1 and re.fullmatch(r'\d+', after[0]['t']):
                    return True
        return False
    if total_row is None and first and q.get('marks') and not any(printed_total(v) for v in out):
        total_row = _own_total(q['marks'], first, out)      # the mark scheme prints no total (e.g. 2016 MJ 43): add ours
    printed_total = None
    if total_row and q.get('marks') and total_row['text'][1]['t'] != str(q['marks']):
        printed_total = total_row['text'][1]['t']     # Cambridge misprint (2016 ON 43 q04 prints 5 for 7 marks): show the question's marks
        total_row['text'][1]['t'] = str(q['marks'])
        total_row['text'][1]['w'] = round(6.1 * len(str(q['marks'])), 2)
    if total_row:
        out.append(total_row)
    Lq = first['new_edges'][0] if first else 44.0
    def continues(v, prev):                           # the same cell carried over to the next page (2020 MJ 31 q11): one Q cell
        return ('src' in v and 'src' in prev and v['src']['page'] != prev['src']['page'] and v['text']
                and not v.get('heading') and not any(t['x'] + t['w'] / 2 < Lq for t in v['text']))
    for i, v in enumerate(out):
        _drop_slivers(v)
        _tidy_boxes(v)
        if not (i == 0 and first and os.path.exists(hdr_p)):
            nxt = out[i + 1] if i + 1 < len(out) else None
            cont = nxt is not None and continues(nxt, v)
            if cont:                                  # the row's own bottom rule stops at the Q column too
                keep = []
                for l in v['lines']:
                    bb = MP._bbox(l['d'])
                    if bb is not None and bb[3] - bb[1] < 1.5 and bb[1] >= v['h'] - 2.5 and bb[0] < Lq - 1 and bb[2] > Lq:
                        keep.append({**l, 'd': f'M{Lq:.2f} {bb[1]:.2f}L{bb[2]:.2f} {bb[1]:.2f}L{bb[2]:.2f} {bb[3]:.2f}L{Lq:.2f} {bb[3]:.2f}Z'})
                    elif bb is not None and bb[3] - bb[1] < 1.5 and bb[1] >= v['h'] - 2.5 and bb[2] <= Lq + 1:
                        continue
                    else:
                        keep.append(l)
                v['lines'] = keep
            _frame(v, top=(i == 0), bottom_from=Lq if cont else 0.0)

    return {'w': W, 'h': round(sum(v['h'] for v in out), 2), 'rows': out, 'problems': problems, 'modes': modes,
            'printed_total': printed_total,
            'info': {k: first[k] for k in ('edges', 'new_edges', 'new_w')} if first else None,
            'has_header': bool(first and os.path.exists(hdr_p))}


NAMES = [(r'^(question|q)$', 'Q'), (r'answer', 'Answer'), (r'^marks?$', 'Marks'), (r'guidance|notes?|additional', 'Guidance')]


def _header_unit(hdr, info):
    """Our own header row: the same short names in every year (Q | Answer | Marks | Guidance), centred in the
    columns of the rows below. Only the ORDER of the printed header words is used, not their positions."""
    nw = list(info['new_w']); starts = [0.0] + list(info['new_edges'])
    real = [i for i, w in enumerate(nw) if w >= 20]
    top_y = min([t['y'] for t in hdr['text']] or [0])   # the header line only (2026 MJ 62: an examiner note printed under it)
    ws = sorted((t for t in hdr['text'] if t['y'] <= top_y + 3), key=lambda t: t['x'])
    phrases = []
    for t in ws:
        if phrases and t['x'] - (phrases[-1][-1]['x'] + phrases[-1][-1]['w']) < 12:
            phrases[-1].append(t)
        else:
            phrases.append([t])
    def norm(ph):
        txt = ' '.join(t['t'] for t in ph).strip()
        return next((n for pat, n in NAMES if re.search(pat, txt.lower())), txt)
    names = [norm(p) for p in phrases]
    if len(names) != len(real):
        names = ['Q', 'Answer', 'Marks'] if len(real) == 3 else (names + [''] * len(real))[:len(real)]
    tpl = dict(ws[0]) if ws else {'s': 11.0, 'f': 'sans'}
    for k in ('i', 'c', 'role', 'u', 'dir'):
        tpl.pop(k, None)
    H = 22.0
    v = {'src': hdr['src'], 'w': W, 'h': H, 'text': [], 'lines': [_rect(0, 0, W, H, '#f2f2f2')], 'figs': [], 'glyphs': []}
    for k, (c, name) in enumerate(zip(real, names)):
        x0 = starts[c]
        x1 = W if k == len(real) - 1 else starts[c] + nw[c]
        if k < len(real) - 1:
            v['lines'].append(_rect(x1 - 0.3, 0, x1 + 0.3, H))
        t = dict(tpl, t=name, b=1, s=11.0, y=15.0)
        t['w'] = round(len(name) * 6.4, 2)
        t['x'] = round(x0 + (x1 - x0 - t['w']) / 2, 2)
        v['text'].append(t)
    _frame(v, top=True)
    return v


def attach_header(rec, store):
    """The header file is written after the questions: put the header row on top of rec['ms_p'] when it was missing."""
    mp = rec.get('ms_p')
    hdr_p = os.path.join(store, 'ms_header.json')
    if not mp or mp.get('has_header') or not mp.get('info') or not os.path.exists(hdr_p):
        return False
    v = _header_unit(json.load(open(hdr_p)), mp['info'])
    mp['rows'].insert(0, v); mp['h'] = round(mp['h'] + v['h'], 2); mp['has_header'] = True
    return True
