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
    if total_row:
        out.append(total_row)
    for i, v in enumerate(out):
        _drop_slivers(v)
        if not (i == 0 and first and os.path.exists(hdr_p)):
            _frame(v, top=(i == 0))

    return {'w': W, 'h': round(sum(v['h'] for v in out), 2), 'rows': out, 'problems': problems, 'modes': modes,
            'info': {k: first[k] for k in ('edges', 'new_edges', 'new_w')} if first else None,
            'has_header': bool(first and os.path.exists(hdr_p))}


def _header_unit(hdr, info):
    v = MP.portrait_header(hdr, info)
    for t in v['text']:
        if t['t'] == 'Mark':
            t['t'] = 'Marks'; t['w'] = round(t['w'] * 1.22, 2); t['x'] = round(t['x'] - 3, 2)
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
