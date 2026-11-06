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
    if len(nw) != 3:
        return None
    ms0 = info['new_edges'][len(nw) - 2]
    tpl = next((dict(t) for v in rows for t in v['text'] if t.get('f')), {'s': 11.0, 'f': 'sans'})
    for k in ('i', 'c', 'role', 'u', 'dir'):
        tpl.pop(k, None)
    a = dict(tpl, t='Total', b=1, w=29.3, y=14.0); a['x'] = round(ms0 - 8 - a['w'], 2)
    num = str(marks)
    b = dict(tpl, t=num, b=1, w=round(6.1 * len(num), 2), y=14.0); b['x'] = round(ms0 + (nw[-1] - b['w']) / 2, 2)
    return {'src': rows[-1]['src'], 'w': W, 'h': 20.0, 'text': [a, b], 'lines': [_rect(ms0 - 0.3, 0, ms0 + 0.3, 20.0)],
            'figs': [], 'glyphs': [], 'own_total': True}


LABEL_RE = re.compile(r'^(\d{1,2})$|^\(([a-h])\)$|^\(([ivx]{1,4})\)$')
MARK_RE = re.compile(r'^\(?(?:[ABCMP]\d{1,2}|B\d|\d)\)?$|^\[\d{1,2}\]$')


def _old_rows(units, q, L=44.0, M=W - 44.0):
    """Old portrait mark schemes (up to 2016 FM: no table, 'n (a) answer ... B1'): put them in OUR table, like every
    other year (Dhruv 2026-11-06: 'we want each ms in our guideline layout, consistency in all ms').
    One row per question part; label 'n(a)(i)' in the Q column, answer at the normal size in the Answer column
    (re-wrapped when too wide), marks right-aligned in the Marks column; the printed '[Total: n]' goes (ours is drawn)."""
    A = M - L - 10
    qn = str(int(q['id'].rsplit('_q', 1)[1]))
    state = {'l': None, 'r': None}
    rows = []
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
        def lead_labels(lw):                          # bold 'n', '(a)', '(i)' at the start of a line
            out_ = []
            for t in lw:
                if t.get('b') and LABEL_RE.match(t['t']) and t['x'] < 0.3 * u['w']:
                    out_.append(t)
                else:
                    break
            return out_
        all_labs = {id(t) for lw in lines.values() for t in lead_labels(lw)}
        body = [t for t in ws if id(t) not in all_labs and not (t['x'] > 0.82 * u['w'] and MARK_RE.match(t['t']))]
        ax0 = min([t['x'] for t in body]) if body else 56.0
        # split the unit at lines that start with a part label
        segs = []
        for y, lw in lines.items():
            labs = lead_labels(lw)
            if labs or not segs:
                segs.append({'y0': y, 'labs': labs, 'lines': []})
            segs[-1]['lines'].append(lw)
        for sg in segs:
            for t in sg['labs']:
                m_ = LABEL_RE.match(t['t'])
                if m_.group(2):
                    state['l'], state['r'] = m_.group(2), None
                elif m_.group(3):
                    state['r'] = m_.group(3)
            label = qn + (f"({state['l']})" if state['l'] else '') + (f"({state['r']})" if state['r'] else '')
            tpl = dict(next((t for lw in sg['lines'] for t in lw if not t.get('b')), sg['lines'][0][0]))
            for k in ('i', 'c', 'role', 'u', 'dir'):
                tpl.pop(k, None)
            v = {'src': u['src'], 'w': W, 'h': 0.0, 'text': [], 'lines': [], 'figs': [], 'glyphs': [], 'old_portrait': True}
            top = max(sg['lines'][0], key=lambda t: t.get('s', 11))['y'] - 14.0
            extra = 0.0; cur_y = None
            for lw in sg['lines']:
                body_l = [t for t in lw if t not in sg['labs'] and not (t['x'] > 0.82 * u['w'] and MARK_RE.match(t['t']))]
                marks_l = [t for t in lw if t['x'] > 0.82 * u['w'] and MARK_RE.match(t['t'])]
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
                    for t in marks_l:
                        n = dict(t, b=1); n['x'] = round(W - 6 - (c_ - a_) + (t['x'] - a_), 2); n['y'] = round(max(lw, key=lambda t: t.get('s', 11))['y'] - top, 2)
                        v['text'].append(n)                   # marks in bold, like the later years
            # drawings and pictures of the unit (fraction bars, symbols) move with the answer text of the first segment
            if sg is segs[0]:
                for l in u['lines']:
                    bb = MP._bbox(l['d'])
                    if bb is None or (min(bb[2] - bb[0], bb[3] - bb[1]) <= 1.0 and (bb[2] - bb[0] > 0.8 * u['w'] or bb[3] - bb[1] > 0.8 * u['h'])):
                        continue                      # the old frame of the row: ours instead
                    v['lines'].append({**l, 'd': _map_path(l['d'], lambda x: L + 5 + (x - ax0), lambda y: y - top)})
                for k_ in ('figs', 'images', 'glyphs'):
                    for f in u.get(k_) or []:
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
    ink_y = [t['y'] for t in u['text'] if not any(abs(t['y'] - y) < 2.5 for y in tot_y)] + [f['y'] + f.get('h', 0) for k_ in ('figs', 'images', 'glyphs') for f in u.get(k_) or []]
    hy = collections.defaultdict(float)
    for r in rr:
        if r[3] - r[1] < 1.3 and r[2] - r[0] > 1.3:
            hy[round(r[1])] += r[2] - r[0]
    for y in sorted(hy):                               # an empty band under a full-width rule (2017 MJ 32 q11): not part of the row
        if hy[y] > 0.9 * u['w'] and 4 < y < h - 4 and ink_y and max(ink_y) < y:
            h = float(y); break
    full = sorted(x for x, c in cov.items() if c >= 0.6 * h and 20 < x < u['w'] - 8)
    cx_ = [t['x'] + t['w'] / 2 for t in u['text']]
    while len(full) >= 2 and not any(c > full[-1] for c in cx_):
        full.pop()                                    # the table's own right border (2016 MJ 43: 9 pt inside the cut)
    left = [x for x, c in cov.items() if x <= 20 and c >= 0.6 * h]
    if len(full) == 1 and left and any(c > full[0] for c in cx_):
        full = [max(left)] + full                     # a continuation row with an empty question column (2020 MJ 31 q11, page 2)
    outer = [x for x in cov if x <= 20 or x >= u['w'] - 8 or (full and x > full[-1] + 2)]
    outer = [x for x in outer if x not in full]
    if len(full) >= 2:                                # the paper's grand total in a grey cell under the last question (2016 ON 43 q11)
        e2_ = full[-1]
        ink2 = [t['y'] for t in u['text'] if not any(abs(t['y'] - y) < 2.5 for y in tot_y)
                and not (t['x'] + t['w'] / 2 > e2_ and re.fullmatch(r'\d+', t['t']))] + \
               [f['y'] + f.get('h', 0) for k_ in ('figs', 'images', 'glyphs') for f in u.get(k_) or []]
        for y in sorted(hy):
            if hy[y] > 0.6 * u['w'] and 4 < y < h - 4 and ink2 and max(ink2) < y:
                h = float(y); break
    if first:
        nw = [w for w in first['new_w'] if w >= 20]
        L = first['new_edges'][0]; M = first['new_edges'][len(nw) - 2]
    else:
        L, M = 44.0, W - 44.0
    has_marks = True
    if len(full) >= 2:
        e1, e2 = full[0], full[-1]                    # label | answer ... answer | marks
    elif first and u['text'] and not u.get('figs') and not u.get('images') and not u.get('glyphs') and len({round(t['y']) for t in u['text']}) == 1:
        return _heading_row(u, L)                     # a heading row across answer and marks ('8  Hydroelectric', 2017 ON 41)
    else:
        return None
    return _cell_layout(u, h, e1, e2, L, M, has_marks, outer, rr, cov)


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


def _reflow_table(TT, LL, PP, vx, A):
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
    mins = [max([t['w'] for (i, j), ws in cells.items() if j == jj for t in ws] + [10]) + 10 for jj in range(len(cols))]
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
        a, c = cols[j]; x0 = nx[j] + 4; x1 = nx[j + 1] - 4
        anch = sorted({round(t['y']) for t in ws if t.get('s', 11) >= 9})
        def key(t):                                    # sub/superscripts (R₁, cm³) stay on their line
            if t.get('s', 11) >= 9 or not anch:
                return round(t['y'])
            a_ = min(anch, key=lambda a: abs(a - t['y']))
            return a_ if abs(a_ - t['y']) <= 7 else round(t['y'])
        lines_ = {}
        for t in sorted(ws, key=lambda t: (key(t), t['x'])):
            lines_.setdefault(key(t), []).append(t)
        lines_ = dict(sorted(lines_.items()))
        first = min(t['y'] for t in ws) - ys[i]
        lh = max(t.get('s', 10) for t in ws) * 1.2
        y = first; out = []
        centred = all(abs((min(t['x'] for t in lw) + max(t['x'] + t['w'] for t in lw)) / 2 - (a + c) / 2) < 4 for lw in lines_.values())
        for k, lw in enumerate(lines_.values()):
            if k:
                y += lh
            cur, row_ = x0, []
            prev = None
            for t in lw:
                gap = 0 if prev is None else min(max(t['x'] - (prev['x'] + prev['w']), 2.0), 6.0)
                if row_ and cur + gap + t['w'] > x1:
                    out.append(row_); row_ = []; y += lh; cur = x0; gap = 0
                n = dict(t, _sx=t['x']); n['x'] = cur + gap; n['y'] = y + (t['y'] - max(lw, key=lambda o: o.get('s', 11))['y'])
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


def _cell_layout(u, h, e1, e2, L, M, has_marks, outer, rr, cov=()):
    """Dhruv 2026-11-05 (round 13): rows drawn cell-wise keep the NORMAL font size; the row grows instead.
    The answer cell is laid out band by band (bands = its sub-rows): an inner table gets narrower columns to fit its
    content; a text-only band that is too wide is re-wrapped; only a band with fractions/drawings that still does not
    fit is shrunk (just that band)."""
    T_ = 0.6
    A = M - L - 10                                    # room in our answer column
    v = {'src': u['src'], 'w': W, 'h': 0, 'text': [], 'lines': [], 'figs': [], 'glyphs': [], 'cell_scaled': 1.0}
    cy = lambda t: t['y'] - 0.35 * t.get('s', 10)
    ans_t = [t for t in u['text'] if e1 < t['x'] + t['w'] / 2 < e2 and t['y'] < h - 1]
    lab_t = [t for t in u['text'] if t['x'] + t['w'] / 2 < e1 and t['y'] < h - 1]
    mrk_t = [t for t in u['text'] if t['x'] + t['w'] / 2 > e2 and t['y'] < h - 1]
    ans_l = []
    for l in u['lines']:
        if (l.get('fill') or '').lower() in ('#ffffff', '#fff') and not l.get('stroke') or (l.get('stroke') or '').lower() in ('#ffffff', '#fff'):
            continue                                  # white paint (a hidden line, 2022 MJ 41 q9): nothing to draw
        b = MP._bbox(l['d'])
        if b is None:
            bb = [MP._bbox(sub) for sub in re.findall(r'M[^M]+', l['d'])]
            b = None if any(x is None for x in bb) or not bb else (min(x[0] for x in bb), min(x[1] for x in bb), max(x[2] for x in bb), max(x[3] for x in bb))
        if b is None:                                 # a curve (brace, arc): keep it, place it by its first point
            pts = [float(x) for x in MP.NUM.findall(l['d'])[:2]]
            if len(pts) == 2 and e1 < pts[0] < e2 and pts[1] < h:
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
    seps = MP._cluster([(b[1] + b[3]) / 2 for l, b in ans_l if b[3] - b[1] < 1.3 and b[2] - b[0] >= 0.85 * (e2 - e1)])
    sep_m = {y: any(r[3] - r[1] < 1.3 and abs((r[1] + r[3]) / 2 - y) < 1.5 and r[2] > e2 + 5 for r in rr) for y in seps}
    ans_l = [(l, b) for l, b in ans_l if not (b[3] - b[1] < 1.3 and b[2] - b[0] >= 0.85 * (e2 - e1))]
    pics = [(key, f) for key in ('figs', 'images', 'glyphs') for f in (u.get(key) or [])]
    bounds = [0.0] + seps + [h]
    lines_m = {}
    for t in mrk_t:
        lines_m.setdefault(round(t['y']), []).append(t)
    lines_l = {}
    for t in lab_t:
        lines_l.setdefault(round(t['y']), []).append(t)
    span = lambda ws: (min(w['x'] for w in ws), max(w['x'] + w['w'] for w in ws))
    cum, sep_new, kmin, end_full = 0.0, [], 1.0, None
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
                for t in ws:
                    byl.setdefault(round(t['y']), []).append(t)
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
        R = max([tx(t) + t['w'] for t in TT] + [fxc(b[2]) for l, b in LL] + [fxc(f['x']) + f.get('w', 0) for k_, f in PP] + [e1b])
        need = R - e1b
        if need > A + 0.5:                            # blank space left of the content (an indented table, 2020 FM 32 q6): use it first
            lead = min([tx(t) for t in TT] + [fxc(b[0]) for l, b in LL] + [fxc(f['x']) for k_, f in PP] + [R]) - e1b
            sh = min(need - A, max(0.0, lead - 6))
            e1b += sh; need -= sh
        X = lambda x: L + 5 + (x - e1b)
        decor = [(l, b) for l, b in LL]
        under = {}
        for l, b in decor:                            # underlines: they move with their word
            o = next((t for t in TT if 0.3 <= b[1] - t['y'] <= 5 and b[0] < t['x'] + t['w'] and b[2] > t['x'] and b[3] - b[1] < 1.3), None)
            under[id(l)] = o
        pure = not PP and not cols and all(under[id(l)] is not None for l, b in decor)
        kb, moves, extra = 1.0, {}, 0.0
        if (need > A + 0.5 or spanning) and pure and TT:   # re-wrap the text lines of this band (wide gaps closed up)
            # a fraction (numerator / bar / denominator) belongs to the text line it sits in (2022 FM 32 q11 '... OR 240×48/590')
            line_of = {id(t): round(t['y']) for t in TT}
            for l, b in decor:
                num = [t for t in TT if 0.3 <= b[1] - t['y'] <= 5 and b[0] - 1 <= t['x'] + t['w'] / 2 <= b[2] + 1]
                den = [t for t in TT if 0 < t['y'] - b[3] <= 13 and b[0] - 1 <= t['x'] + t['w'] / 2 <= b[2] + 1]
                if num and den:
                    yn, yd = min(t['y'] for t in num), max(t['y'] for t in den)
                    host = [t for t in TT if yn + 1 < t['y'] < yd - 1 and t not in num + den]
                    if host:
                        hy = round(min(host, key=lambda t: abs(t['y'] - (b[1] + 3)))['y'])
                        for t in num + den:
                            line_of[id(t)] = hy
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
        elif need > A + 0.5 and cols and not spanning and all(vx[0] - 3 <= t['x'] + t['w'] / 2 <= vx[-1] + 3 for t in TT):
            full_ = abs(vx[0] - (e1b + 0.5)) < 0.01 and abs(vx[-1] - (e2 - 0.5)) < 0.01
            rf = _reflow_table(TT, LL, PP, vx, (M - L + 4) if full_ else A)
            if rf is not None:                        # the table at the normal size, text wrapped inside its cells
                texts_, lines_, pics_, tw_, ymap_ = rf
                ox = L if full_ else L + 5 + (A - tw_) / 2   # a table filling the cell meets our column rules (round 16)
                ytab = min([b[1] for l, b in LL if b[2] - b[0] < 1.3] + [b0])
                oy = cum if full_ else cum + max(0.0, ytab - b0)   # a full-cell table starts on the row line (round 17)
                for n in texts_:
                    n['x'] = round(n['x'] + ox, 2); n['y'] = round(n['y'] + oy, 2); v['text'].append(n)
                for l in lines_:
                    v['lines'].append({**l, 'd': _map_path(l['d'], lambda x: x + ox, lambda y: y + oy)})
                for k_, g in pics_:
                    g['x'] = round(g['x'] + ox, 2); g['y'] = round(g['y'] + oy, 2); v.setdefault(k_, []).append(g)
                Ymap = lambda y: oy + ymap_(y)
                if has_marks:                         # the marks column's own sub-row lines, at the table's new row heights
                    for y_m in MP._cluster([(r[1] + r[3]) / 2 for r in rr if r[3] - r[1] < 1.3 and r[0] >= e2 - 2 and r[2] - r[0] > 5
                                            and b0 + 2 < (r[1] + r[3]) / 2 < b1 - 2 and (r[1] + r[3]) / 2 < h - 2]):
                        v['lines'].append(_rect(M, Ymap(y_m) - 0.25, W, Ymap(y_m) + 0.25))
                for y_, ws in lines_m.items():
                    if not inb(y_ - 3):
                        continue
                    a_, c_ = span(ws)
                    for t in ws:
                        n = dict(t); n['x'] = round(W - 6 - (c_ - a_) + (t['x'] - a_), 2); n['y'] = round(Ymap(t['y']), 2)
                        v['text'].append(n)
                for y_, ws in lines_l.items():
                    if not inb(y_ - 3):
                        continue
                    a_, c_ = span(ws)
                    for t in ws:
                        n = dict(t); n['x'] = round((L - (c_ - a_)) / 2 + (t['x'] - a_), 2); n['y'] = round(cum + (t['y'] - b0), 2)
                        v['text'].append(n)
                tb = max([MP._bbox(l['d'])[3] for l in v['lines'][-len(lines_):] if MP._bbox(l['d'])] + [oy]) if lines_ else oy
                cum = max([tb + (0 if full_ else 6)] + [n['y'] + 5 for n in v['text']])   # a full-cell table ends on the row line
                if full_ and cum > tb + 0.5:              # its column lines run on to the row line
                    for l in list(v['lines'][-len(lines_):]):
                        bb_ = MP._bbox(l['d'])
                        if bb_ and bb_[2] - bb_[0] < 1.3 and abs(bb_[3] - tb) < 0.6:
                            v['lines'].append(_rect(bb_[0], tb, bb_[2], cum))
                if i < len(bounds) - 2:
                    sep_new.append((cum, sep_m.get(bounds[i + 1], False)))
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
            sx0 = min([t['x'] for t in TT] + [b[0] for l, b in LL] + [f['x'] for k_, f in PP])
            sx1 = max([t['x'] + t['w'] for t in TT] + [b[2] for l, b in LL] + [f['x'] + f.get('w', 0) for k_, f in PP])
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
            n['x'] = round(L + 5 + (tx(t) - e1b) * kb + dx + cxs, 2); n['y'] = round(fy(t['y'], dy), 2)
            if kb < 1:
                n['s'] = round(t['s'] * kb, 2); n['w'] = round(t['w'] * kb, 2)
            v['text'].append(n)
        lbot = 0.0
        for l, b in LL:
            o = under.get(id(l)); dx, dy = moves.get(id(o), (0.0, 0.0)) if o is not None else (0.0, 0.0)
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
            for y_m in MP._cluster([(r[1] + r[3]) / 2 for r in rr if r[3] - r[1] < 1.3 and r[0] >= e2 - 2 and r[2] - r[0] > 5
                                    and b0 + 2 < (r[1] + r[3]) / 2 < b1 - 2 and (r[1] + r[3]) / 2 < h - 2]):
                v['lines'].append(_rect(M, fy(y_m) - 0.25, W, fy(y_m) + 0.25))
        for y_, ws in lines_m.items():                # marks: right-aligned in our marks column, at the band's top offset
            if spanning or not inb(y_ - 3):
                continue
            a_, c_ = span(ws)
            for t in ws:
                n = dict(t); n['x'] = round(W - 6 - (c_ - a_) + (t['x'] - a_), 2); n['y'] = round(cum + (t['y'] - b0), 2)
                v['text'].append(n)
        for y_, ws in lines_l.items():                # question label: centred in our label column
            if spanning or not inb(y_ - 3):
                continue
            a_, c_ = span(ws)
            for t in ws:
                n = dict(t); n['x'] = round((L - (c_ - a_)) / 2 + (t['x'] - a_), 2); n['y'] = round(cum + (t['y'] - b0), 2)
                v['text'].append(n)
        bot = [n['y'] + 5 for n in v['text']]
        cum = max([(b1 - b0) * kb + extra + cum] + [y for y in bot] + ([lbot + 6] if cols else []))   # room under an inner table's edge
        if i < len(bounds) - 2:
            sep_new.append((cum, sep_m.get(bounds[i + 1], False)))
    v['h'] = round(cum if end_full is not None and abs(end_full - cum) < 0.01 else cum + 2, 2)
    v['cell_scaled'] = round(kmin, 3)
    for y, into_m in sep_new:
        if y >= cum - 0.5:
            continue                                  # the bands below were dropped: the row's own bottom border is enough
        v['lines'].append(_rect(L, y, W if into_m else M, y + T_ * 0.8))
    v['lines'].append(_rect(L - 0.3, 0, L + 0.3, v['h']))
    if has_marks:
        v['lines'].append(_rect(M - 0.3, 0, M + 0.3, v['h']))
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
    uniq = [(r, _tighten(_under_images(_dedupe(_unshrink(u))))) for r, u in uniq]
    units = [u for _, u in uniq]
    if all(u['w'] <= W + 2 for u in units):          # the old portrait era: our table too (no printed one to follow)
        first = {'edges': [], 'new_edges': [44.0, W - 44.0], 'new_w': [44.0, W - 88.0, 44.0], 'default': True}
        out = _old_rows(units, q)
        modes = {'old': len(out)}
        hdr = _header_unit({'src': units[0]['src'], 'text': []}, first)
        total_row = _own_total(q['marks'], first, out) if q.get('marks') else None
        out = [hdr] + out + ([total_row] if total_row else [])
        for i, v in enumerate(out[1:], 1):
            _drop_slivers(v)
            nxt = out[i + 1] if i + 1 < len(out) else None
            _frame(v, bottom_from=44.0 if nxt is not None and nxt.get('cont') else 0.0)
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
    out = fixed
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
    ws = sorted(hdr['text'], key=lambda t: t['x'])
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
