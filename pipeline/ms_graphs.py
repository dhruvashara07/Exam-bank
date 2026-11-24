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
                                         'labels': [[('i', 'y'), ('t', ' = '), ('frac', '3x − 2', '5 − 2x')]],
                                         'xt': [-2, 2, 4, 6], 'yt': [-10, -5, 5, 10], 'grid': (1, 2.5)},
    ('0607_2024MJ_42_q03', '3(b)(i)'): {'f': [('2**x - 1/x', 'f(x) = 2ˣ − 1/x')], 'x': (-3, 3), 'y': (-5, 8),
                                        'labels': [[('t', 'f('), ('i', 'x'), ('t', ') = 2'), ('sup', 'x'), ('t', ' − '), ('frac', '1', 'x')]],
                                        'xt': [-3, 3], 'yt': [-5, 8], 'grid': (1, 1)},
    ('0607_2024MJ_42_q03', '3(b)(iv)(a)'): {'f': [('2**x - 1/x', 'f(x) = 2ˣ − 1/x'), ('3 - x', 'g(x) = 3 − x')],
                                            'x': (-3, 3), 'y': (-5, 8), 'xt': [-3, 3], 'yt': [-5, 8], 'grid': (1, 1),
                                            'labels': [[('t', 'f('), ('i', 'x'), ('t', ') = 2'), ('sup', 'x'), ('t', ' − '), ('frac', '1', 'x')],
                                                       [('t', 'g('), ('i', 'x'), ('t', ') = 3 − '), ('i', 'x')]]},
    ('0607_2024MJ_43_q10', '10(f)'): {'f': [('math.sin(math.radians(3*(x+1)))', 'y = sin(3(x + 1))'),
                                            ('1 - 0.01*x', 'y = 1 − 0.01x')],
                                      'x': (0, 180), 'y': (-2, 2), 'xt': [180], 'yt': [-2, 2], 'grid': (30, 0.5),
                                      'labels': [[('i', 'y'), ('t', ' = sin(3('), ('i', 'x'), ('t', ' + 1))')],
                                                 [('i', 'y'), ('t', ' = 1 − 0.01'), ('i', 'x')]]},
    ('0607_2024MJ_61_q13', '13(b)(iii)'): {'f': [('x - 1 + math.sqrt(1 - x)', 'G = x − 1 + √(1 − x)')], 'x': (0, 1),
                                           'y': (0, 0.5), 'xt': [1], 'yt': [0.5], 'grid': (0.1, 0.05), 'ylab': 'G',
                                           'labels': [[('i', 'G'), ('t', ' = '), ('i', 'x'), ('t', ' − 1 + √(1 − '), ('i', 'x'), ('t', ')')]]},
    ('0607_2023MJ_63_q12', '12(c)(iii)'): {'f': [('1.12*2**(-x) - 0.12', 'R = 1.12 × 2⁻ʰ − 0.12')], 'x': (0, 52), 'y': (-0.2, 1.0),
                                           'xt': [8, 16, 24, 32, 40, 48], 'yt': [-0.2, 0.2, 0.4, 0.6, 0.8, 1.0], 'grid': (4, 0.2),
                                           'ylab': 'R', 'xlab': 'h', 'xlow': True,      # (round 34: a blurred screenshot, redrawn from the model)
                                           'labels': [[('i', 'R'), ('t', ' = 1.12 × 2'), ('sup', '–h'), ('t', ' – 0.12')]]},
    ('0607_2020ON_62_q06', '6(a)'): {'f': [], 'label': False, 'vector': True, 'x': (9, 20), 'y': (900, 1100), 'grid': (1, 10),   # the 12
                                     'xt': list(range(9, 21)), 'yt': [950, 1000, 1050, 1100], 'xlab': 't', 'ylab': 'L',  # points
                                     'points': [(9, 960), (10, 959), (11, 960), (12, 960), (13, 960), (14, 959), (15, 960),  # of
                                                (16, 987), (17, 1014), (18, 1041), (19, 1068), (20, 1095)]},   # the question's table
    ('0607_2020ON_43_q08', '8(a)(iii)'): {'f': [('1.5**(-x)', ''), ('x**2', '')], 'label': False, 'dash': False, 'vector': True, 'col': 3,  # faint
                                          'x': (-2, 2), 'y': (0, 4), 'grid': (1, 1), 'xt': [-2, 2], 'yt': [4]},  # (round 37)
    ('0607_2018ON_61_q05', '5(b)(i)'): {'f': [('math.sqrt(x*x - 2.25)', '')], 'label': False, 'x': (-6, 6), 'y': (0, 6),
                                        'grid': (1, 1), 'xt': [-6, 6], 'yt': [6]},     # blurry screenshot (round 37)
    ('0607_2018ON_61_q06', '6(c)'): {'f': [('x*math.cos(math.radians(76))', ''), ('0.139*x', '')], 'label': False,
                                     'dash': False, 'x': (0, 6), 'y': (0, 2), 'grid': (0.5, 0.25),       # z = x cos 76,
                                     'xt': [1, 2, 3, 4, 5, 6], 'yt': [1, 2], 'xlab': 'x', 'ylab': 'z'},  # z = 0.139x (round 37)
    ('0607_2019ON_61_q05', '5(a)(ii)'): {'f': [('12 - 1.8*math.cos(math.radians(x))', 'y = 12 − 1.8 cos t°')],     # (round 35:
                                         'x': (0, 360), 'y': (0, 14), 'grid': (20, 2), 'ylab': 'y', 'xlab': 't',  # a blurred
                                         'xt': [60, 120, 180, 240, 300, 360], 'yt': [2, 4, 6, 8, 10, 12, 14],    # screenshot;
                                         'label': False},   # the question's model; no function label: the printed
                                                            # MS shows none (Dhruv round 36: a label only where the original has one)
    ('0607_2023MJ_32_q11', '11(a)'): {'w': 250.0, 'h': 200.0, 'tree': {         # (round 34: a blurred handwriting-style picture of the
        'first': [('0.80', ['wakes before', '7am']), ('0.20', ['does not', 'wake before', '7am'])],       # completed tree,
        'second': [[('0.92', ['gets to school', 'on time']), ('0.08', ['does not', 'get to school', 'on time'])],     # drawn again
                   [('0.23', ['gets to school', 'on time']), ('0.77', ['does not', 'get to school', 'on time'])]]}},   # like the question's)
}


def _draw_tree(sp, w, h, size=8.0):
    """A completed two-stage tree diagram drawn as lines and text like the question's own (probabilities on the branches)."""
    tr = sp['tree']
    L, T = [], []
    from ms_maths import text_width as tw0
    tw = lambda t: tw0(t, 'serif', size) or 0.5 * size * len(t)
    def txt(lines, x, yc, right=False):                       # a block of lines centred on yc, left edge at x
        lh = size * 1.15
        y0 = yc - (len(lines) - 1) * lh / 2 + size * 0.33
        for k, t in enumerate(lines):
            T.append({'t': t, 'x': round(x - (tw(t) if right else 0), 2), 'y': round(y0 + k * lh, 2), 'w': round(tw(t), 2), 's': size})
    def br(x0, y0, x1, y1, prob, upper):
        L.append({'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}', 'stroke': '#000000', 'sw': 0.8})
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if upper:
            T.append({'t': prob, 'x': round(mx - tw(prob) - 1, 2), 'y': round(my - 1.5, 2), 'w': round(tw(prob), 2), 's': size})
        else:
            T.append({'t': prob, 'x': round(mx - tw(prob) - 1, 2), 'y': round(my + size + 0.5, 2), 'w': round(tw(prob), 2), 's': size})
    rx, ry = 4.0, h / 2
    e1 = 0.24 * w
    f1 = 0.52 * w
    e2 = 0.66 * w
    for i, (prob, lines) in enumerate(tr['first']):
        yn = h * (0.26 if i == 0 else 0.74)
        br(rx, ry, e1, yn, prob, i == 0)
        txt(lines, e1 + 3, yn)
        for j, (p2, l2) in enumerate(tr['second'][i]):
            ye = yn + (-1 if j == 0 else 1) * 0.15 * h
            br(f1, yn, e2, ye, p2, j == 0)
            txt(l2, e2 + 3, ye)
    return L, T


def spec(qid, label):
    return SPECS.get((qid, label))


def _num(v):
    return ('%g' % v).replace('-', '–')        # the MS prints an en dash for minus


def draw(sp, w, h, size=9.0):
    """-> (lines, texts) in a box w x h (pt), origin top left. lines: {'d', 'stroke', 'sw'}; texts: {'t', 'x', 'y', 'w', 's'}."""
    if 'tree' in sp:
        return _draw_tree(sp, w, h, size)
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
        T.append({'t': t, 'x': round(X(v) - tw / 2, 2), 'y': round((Y(y0) + 1 + size) if sp.get('xlow') else (ax_y + 2 + size), 2),
                  'w': tw, 's': size})       # ('xlow': numbers under the window - a curve runs along the axis, 2023 MJ 63 q12)
    for v in sp.get('yt', []):
        L.append({'d': f'M{ax_x - 2:.2f} {Y(v):.2f}H{ax_x + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', size)
        T.append({'t': t, 'x': round(ax_x - 3 - tw, 2), 'y': round(Y(v) + size * 0.35, 2), 'w': tw, 's': size})
    T.append({'t': sp.get('xlab', 'x'), 'x': round(X(x1) + 8, 2), 'y': round(ax_y + size * 0.35, 2), 'w': size * 0.5, 's': size, 'i': 1})
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
            if dashes[n % 3] and sp.get('dash', True):      # ('dash': False - all curves solid, as printed)
                ln['dash'] = dashes[n % 3]
            L.append(ln)
    for px, py in sp.get('points', []):        # plotted points as crosses x (2020 ON 62 6(a): the crosses were lost)
        cx, cy, r_ = X(px), Y(py), 2.2
        L.append({'d': f'M{cx - r_:.2f} {cy - r_:.2f}L{cx + r_:.2f} {cy + r_:.2f}M{cx - r_:.2f} {cy + r_:.2f}L{cx + r_:.2f} {cy - r_:.2f}',
                  'stroke': '#000000', 'sw': 0.8})
    # the function label(s) (Dhruv round 33: only where the printed graph has one, small, never over the curves or the
    # axes, fractions as fractions): pieces ('t', text) / ('i', italic) / ('sup', text) / ('frac', num, den)
    if not sp.get('label', True):
        return L, T
    ls_ = sp.get('labels') or [[('t', lab)] for _, lab in sp['f']]
    ls = 7.0                                            # label size
    def piece_w(pc):
        if pc[0] == 'frac':
            return max(text_width(pc[1], 'serif', ls * 0.9), text_width(pc[2], 'serif', ls * 0.9)) + 1.5
        if pc[0] == 'sup':
            return text_width(pc[1], 'serif', ls * 0.7)
        return text_width(pc[1], 'serif', ls)
    def lab_h(lab):
        return ls * 2.3 if any(pc[0] == 'frac' for pc in lab) else ls * 1.35
    samp = len(sp['f']) > 1
    widths = [sum(piece_w(pc) for pc in lab) + (13 if samp else 0) for lab in ls_]
    bw, bh = max(widths) + 2, sum(lab_h(l_) for l_ in ls_) + 2
    pts = []                                            # every drawn curve point, the axes and the edges: kept clear
    for l_ in L:
        if l_.get('stroke') == '#000000':
            nums = [float(v) for v in __import__('re').findall(r'-?\d+\.?\d*', l_['d'])]
            pts += list(zip(nums[0::2], nums[1::2]))
    for t_ in T:                                        # tick numbers and axis letters are kept clear too
        for fx_ in (0, 0.5, 1):
            for fy_ in (0, 1):
                pts.append((t_['x'] + fx_ * t_['w'], t_['y'] - fy_ * t_['s'] * 0.75))
    def hits(bx_, by_):
        m = 2.5
        return sum(1 for a, b in pts if bx_ - m <= a <= bx_ + bw + m and by_ - m <= b <= by_ + bh + m)
    cands = []
    for fx in (0.98, 0.6, 0.3, 0.02):
        for fy in (0.02, 0.3, 0.6, 0.98):
            bx_ = pl + 3 + fx * (W - bw - 6); by_ = pt + 3 + fy * (H - bh - 6)
            cands.append((hits(bx_, by_), -fx, fy, bx_, by_))
    _, _, _, bx, by = min(cands)
    L.append({'d': f'M{bx:.2f} {by:.2f}H{bx + bw:.2f}V{by + bh:.2f}H{bx:.2f}Z', 'fill': '#ffffff'})   # no border
    yy = by + 1
    for n, lab in enumerate(ls_):
        h_ = lab_h(lab); base = yy + h_ / 2 + ls * 0.35; xx = bx + 1
        if samp:
            ln = {'d': f'M{xx:.2f} {base - ls * 0.3:.2f}h10', 'stroke': '#000000', 'sw': 1.0}
            if dashes[n % 3]:
                ln['dash'] = dashes[n % 3]
            L.append(ln); xx += 13
        for pc in lab:
            w_ = piece_w(pc)
            if pc[0] == 'frac':
                s2 = ls * 0.9
                for txt, yb in ((pc[1], base - ls * 0.62), (pc[2], base + ls * 0.78)):
                    tw = text_width(txt, 'serif', s2)
                    T.append({'t': txt, 'x': round(xx + (w_ - tw) / 2, 2), 'y': round(yb, 2), 'w': tw, 's': s2})
                L.append({'d': f'M{xx + 0.5:.2f} {base - ls * 0.3 - 0.25:.2f}H{xx + w_ - 0.5:.2f}V{base - ls * 0.3 + 0.25:.2f}'
                               f'H{xx + 0.5:.2f}Z', 'fill': '#000000'})
            elif pc[0] == 'sup':
                T.append({'t': pc[1], 'x': round(xx, 2), 'y': round(base - ls * 0.4, 2), 'w': w_, 's': ls * 0.7, 'i': 1})
            else:
                t_ = {'t': pc[1], 'x': round(xx, 2), 'y': round(base, 2), 'w': w_, 's': ls}
                if pc[0] == 'i':
                    t_['i'] = 1
                T.append(t_)
            xx += w_
        yy += h_
    return L, T
