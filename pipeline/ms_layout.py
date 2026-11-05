"""Portrait mark scheme of one question with OUR consistent frame (decided with Dhruv 2026-11-03).

    build(q, store) -> {'w': 523, 'h': ..., 'rows': [unit, ...], 'problems': [...], 'modes': {...}}

- header row once at the top (Q | Answer | Marks), grey;
- rows re-wrapped by ms_portrait (column widths from the content of the whole question);
- full black frame: left and right border and a line under every row;
- 'Total: n' is its own last row (label "Total" in the answer column, number under Marks).
Units are the same layout units as everywhere else (draw with store.unit_svg).
"""
import os, json, copy, re
import ms_portrait as MP

W = 523.0
FRAME = '#000000'


def _rect(x0, y0, x1, y1, fill=FRAME):
    return {'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}L{x0:.2f} {y1:.2f}Z', 'fill': fill}


def _frame(v, top=False, t=0.6):
    h = v['h']
    v['lines'] += [_rect(0, 0, t, h), _rect(W - t, 0, W, h), _rect(0, h - t, W, h)]
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
    uniq = [(r, _tighten(u)) for r, u in uniq]
    units = [u for _, u in uniq]
    widths = MP.column_widths(units)
    out, modes, problems, first = [], {}, [], None
    total_row = None
    for i, (r, u) in enumerate(uniq):
        v, info = MP.portrait_unit(u, widths=widths, sizes=sizes)
        modes[info['mode']] = modes.get(info['mode'], 0) + 1
        if info['mode'] == 'wrap':
            first = first or info
            problems += [(r['label'], p) for p in MP.check(u, v)]
        if i == len(uniq) - 1:
            v, total_row = _split_total(v, info) if info['mode'] == 'wrap' else (v, None)
        if v is not None:
            out.append(v)
    hdr_p = os.path.join(store, 'ms_header.json')
    if first and os.path.exists(hdr_p):
        out.insert(0, _header_unit(json.load(open(hdr_p)), first))
    if total_row is None and first and q.get('marks') and not any(re.match(r'Total', t['t']) for v in out for t in v['text']):
        total_row = _own_total(q['marks'], first, out)      # the mark scheme prints no total (e.g. 2016 MJ 43): add ours
    if total_row:
        out.append(total_row)
    for i, v in enumerate(out):
        _drop_slivers(v)
        if not (i == 0 and first and os.path.exists(hdr_p)):
            _frame(v, top=(i == 0))

    return {'w': W, 'h': round(sum(v['h'] for v in out), 2), 'rows': out, 'problems': problems, 'modes': modes,
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
