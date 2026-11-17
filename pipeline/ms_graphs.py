"""Maths mark schemes: graphs printed as calculator SCREENSHOTS are drawn again from the function the question gives
(Dhruv, round 32: 'redraw in the same grid, black and white and clear, the function in the top right corner').

SPECS is data read from the question paper by eye (like ms.MS_RELABEL): the function(s) and the window the question's
own axes show. The drawing: a light grey grid, black axes with arrows and the question's labelled ticks, curves in
black (split where they jump: asymptotes), the function(s) written in the top right corner.
"""
import math

# (question id, mark-scheme row label) -> spec. 'f': [(python expression in x, label as printed)], 'x' / 'y': window,
# 'xt' / 'yt': labelled ticks (as on the question's axes), 'grid': grid step (x, y), 'ylab': y-axis letter.
SPECS = {
    ('0607_2024FM_42_q10', '10(b)(i)'): {'f': [('(3*x-2)/(5-2*x)', 'y = (3x − 2)/(5 − 2x)')], 'x': (-2, 6), 'y': (-10, 10),
                                         'xt': [-2, 2, 4, 6], 'yt': [-10, -5, 5, 10], 'grid': (1, 2.5)},
    ('0607_2024MJ_42_q03', '3(b)(i)'): {'f': [('2**x - 1/x', 'f(x) = 2ˣ − 1/x')], 'x': (-3, 3), 'y': (-5, 8),
                                        'xt': [-3, 3], 'yt': [-5, 8], 'grid': (1, 1)},
    ('0607_2024MJ_42_q03', '3(b)(iv)(a)'): {'f': [('2**x - 1/x', 'f(x) = 2ˣ − 1/x'), ('3 - x', 'g(x) = 3 − x')],
                                            'x': (-3, 3), 'y': (-5, 8), 'xt': [-3, 3], 'yt': [-5, 8], 'grid': (1, 1)},
    ('0607_2024MJ_43_q10', '10(f)'): {'f': [('math.sin(math.radians(3*(x+1)))', 'y = sin(3(x + 1))'),
                                            ('1 - 0.01*x', 'y = 1 − 0.01x')],
                                      'x': (0, 180), 'y': (-2, 2), 'xt': [180], 'yt': [-2, 2], 'grid': (30, 0.5)},
    ('0607_2024MJ_61_q13', '13(b)(iii)'): {'f': [('x - 1 + math.sqrt(1 - x)', 'G = x − 1 + √(1 − x)')], 'x': (0, 1),
                                           'y': (0, 0.5), 'xt': [1], 'yt': [0.5], 'grid': (0.1, 0.05), 'ylab': 'G'},
}


def spec(qid, label):
    return SPECS.get((qid, label))


def _num(v):
    return ('%g' % v).replace('-', '–')        # the MS prints an en dash for minus


def draw(sp, w, h, size=9.0):
    """-> (lines, texts) in a box w x h (pt), origin top left. lines: {'d', 'stroke', 'sw'}; texts: {'t', 'x', 'y', 'w', 's'}."""
    from ms_maths import text_width as tw0
    # text_width measures some Unicode signs (−, –) as ~0 and the label was squeezed; an estimate never below 0.5 em/char
    text_width = lambda t, f, s: max(tw0(t, f, s), 0.5 * s * len(t))
    L, T = [], []
    pl, pr, pt, pb = 22.0, 16.0, 8.0, 14.0                 # room for tick labels and arrows
    x0, x1 = sp['x']; y0, y1 = sp['y']
    W, H = max(20.0, w - pl - pr), max(20.0, h - pt - pb)
    X = lambda x: pl + (x - x0) / (x1 - x0) * W
    Y = lambda y: pt + (y1 - y) / (y1 - y0) * H
    gx, gy = sp.get('grid', (None, None))
    if gx:                                                 # light grey grid (the question's window)
        k = math.ceil(x0 / gx)
        while k * gx <= x1 + 1e-9:
            L.append({'d': f'M{X(k * gx):.2f} {Y(y1):.2f}V{Y(y0):.2f}', 'stroke': '#cfcfcf', 'sw': 0.4}); k += 1
        k = math.ceil(y0 / gy)
        while k * gy <= y1 + 1e-9:
            L.append({'d': f'M{X(x0):.2f} {Y(k * gy):.2f}H{X(x1):.2f}', 'stroke': '#cfcfcf', 'sw': 0.4}); k += 1
    ax_y = Y(0) if y0 <= 0 <= y1 else Y(y0)
    ax_x = X(0) if x0 <= 0 <= x1 else X(x0)
    L.append({'d': f'M{X(x0) - 3:.2f} {ax_y:.2f}H{X(x1) + 6:.2f}', 'stroke': '#000000', 'sw': 0.8})
    L.append({'d': f'M{X(x1) + 6:.2f} {ax_y:.2f}l-4 -1.8v3.6z', 'fill': '#000000'})
    L.append({'d': f'M{ax_x:.2f} {Y(y0) + 3:.2f}V{Y(y1) - 6:.2f}', 'stroke': '#000000', 'sw': 0.8})
    L.append({'d': f'M{ax_x:.2f} {Y(y1) - 6:.2f}l-1.8 4h3.6z', 'fill': '#000000'})
    for v in sp.get('xt', []):
        L.append({'d': f'M{X(v):.2f} {ax_y - 2:.2f}V{ax_y + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', size)
        T.append({'t': t, 'x': round(X(v) - tw / 2, 2), 'y': round(ax_y + 2 + size, 2), 'w': tw, 's': size})
    for v in sp.get('yt', []):
        L.append({'d': f'M{ax_x - 2:.2f} {Y(v):.2f}H{ax_x + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', size)
        T.append({'t': t, 'x': round(ax_x - 3 - tw, 2), 'y': round(Y(v) + size * 0.35, 2), 'w': tw, 's': size})
    T.append({'t': 'x', 'x': round(X(x1) + 8, 2), 'y': round(ax_y + size * 0.35, 2), 'w': size * 0.5, 's': size, 'i': 1})
    yl = sp.get('ylab', 'y')
    T.append({'t': yl, 'x': round(ax_x + 3, 2), 'y': round(Y(y1) - 2, 2), 'w': size * 0.6, 's': size, 'i': 1})
    dashes = [None, '3 2', '1 1.5']
    for n, (expr, lab) in enumerate(sp['f']):
        f = eval('lambda x: ' + expr, {'math': math})
        segs, cur, prev = [], [], None
        N = 600
        for i in range(N + 1):
            x = x0 + (x1 - x0) * i / N
            try:
                y = f(x)
                ok = isinstance(y, float) or isinstance(y, int)
                y = float(y)
                ok = ok and math.isfinite(y)
            except (ZeroDivisionError, ValueError, OverflowError):
                ok = False
            if ok and prev is not None and abs(y - prev) > 0.5 * (y1 - y0):
                ok_jump = False                               # a jump across the window: an asymptote, the curve breaks
            else:
                ok_jump = True
            if not ok or not ok_jump or not (y0 - 0.02 * (y1 - y0) <= y <= y1 + 0.02 * (y1 - y0)):
                if len(cur) > 1:
                    segs.append(cur)
                cur = [(X(x), Y(min(max(y, y0), y1)))] if ok and ok_jump is False and y0 <= y <= y1 else []
                prev = y if ok else None
                continue
            cur.append((X(x), Y(y))); prev = y
        if len(cur) > 1:
            segs.append(cur)
        for sg in segs:
            d = 'M' + 'L'.join(f'{a:.2f} {b:.2f}' for a, b in sg)
            ln = {'d': d, 'stroke': '#000000', 'sw': 1.0}
            if dashes[n % 3]:
                ln['dash'] = dashes[n % 3]
            L.append(ln)
    # the function(s) in the top right corner, in a white box (Dhruv: 'function written in the top right')
    ls = [lab for _, lab in sp['f']]
    bw = max(text_width(t, 'serif', size) for t in ls) + 6 + (14 if len(ls) > 1 else 0)
    bh = len(ls) * (size + 2) + 4
    bx, by = pl + W - bw, pt
    L.append({'d': f'M{bx:.2f} {by:.2f}H{bx + bw:.2f}V{by + bh:.2f}H{bx:.2f}Z', 'fill': '#ffffff', 'stroke': '#000000', 'sw': 0.5})
    for n, lab in enumerate(ls):
        yy = by + 2 + (n + 1) * (size + 2) - 2
        xx = bx + 3
        if len(ls) > 1:                                   # line sample, so the reader can tell the curves apart
            ln = {'d': f'M{xx:.2f} {yy - size * 0.3:.2f}h10', 'stroke': '#000000', 'sw': 1.0}
            if dashes[n % 3]:
                ln['dash'] = dashes[n % 3]
            L.append(ln); xx += 14
        T.append({'t': lab, 'x': round(xx, 2), 'y': round(yy, 2), 'w': text_width(lab, 'serif', size), 's': size})
    return L, T
