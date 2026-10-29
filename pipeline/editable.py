"""Editable version of every question: ordered content blocks per question / part.

The exact SVG pieces stay the master for printing. This adds, on every node that has segments,
    node['content'] = [ {type: 'text', html, text}            paragraph (b, i, sub, sup, LaTeX \\(\\frac..\\))
                        {type: 'list', items: [html]}          bullet points
                        {type: 'figure', id, caption}          diagram/table picture (SVG in figures/)
                        {type: 'table', rows: [[cell]], caption}
                        {type: 'answer', kind, lines, prefix, unit, height_pt}
                        {type: 'marks', value} ]
so a website can show, search and edit the wording, and rebuild a clean (non-exact) layout.

    python3 pipeline/editable.py                 # add/refresh content for every question in bank/
    python3 pipeline/editable.py 0625_2025MJ_41  # some papers
"""
import html as htmlmod, json, os, re, statistics, sys
import pymupdf as fitz

sys.path.insert(0, os.path.dirname(__file__))
import paths
from layout import norm, dark_mask, ZOOM, CONTENT_X0, CONTENT_X1

DOTS = re.compile(r'\.{8,}|…{3,}')
MARK = re.compile(r'\[\s*(\d{1,2})\s*\]')
TOTAL = re.compile(r'\[\s*Total\s*:\s*\d+\s*\]')
LABEL = re.compile(r'^\s*(\d{1,2}\s+)?(\([a-z]{1,4}\)\s*){0,3}')
BULLET = '•'
PUA = re.compile('[\ue000-\uf8ff]')


# ---------------------------------------------------------------------------------------------------
def spans_in(page, rect):
    """Text pieces whose centre lies inside rect: dicts with text, bbox, size, origin, bold, italic.
    Normal PDFs: one piece per span (font name tells bold/italic). Merged-font PDFs ('AllAndNone',
    2025+): one piece per word, bold decided from the printed stroke width (see stroke_bold)."""
    out = []
    gap_after = set()                 # word groups followed by a (thin) space in the PDF
    for b in page.get_text('rawdict', clip=rect)['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            if abs(l['dir'][1]) > 0.1:
                continue                                  # rotated labels belong to figures
            for s in l['spans']:
                font = s['font']
                merged = font.startswith('AllAndNone')
                base = {'size': s['size'], 'oy': s['origin'][1], 'font': font, 'merged_font': merged,
                        'bold': bool(s['flags'] & 16) or 'Bold' in font or 'Black' in font,
                        'italic': bool(s['flags'] & 2) or 'Italic' in font or 'Oblique' in font}
                groups, cur = [], []
                for c in s['chars']:
                    if merged and c['c'].isspace():
                        if cur:
                            groups.append(cur); cur = []
                        if groups:
                            gap_after.add(id(groups[-1]))
                    else:
                        cur.append(c)
                if cur:
                    groups.append(cur)
                for g in groups:
                    t = PUA.sub('', norm(''.join(c['c'] for c in g)))     # bracket/brace pieces of symbol fonts
                    if not t.strip():
                        continue
                    r = fitz.Rect(g[0]['bbox'])
                    for c in g:
                        r |= fitz.Rect(c['bbox'])
                    cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
                    if not (rect.x0 <= cx <= rect.x1 and rect.y0 <= cy <= rect.y1):
                        continue
                    out.append({**base, 'text': t, 'bbox': r, 'space_after': id(g) in gap_after})
    return out


def stroke_width(mask, r):
    import numpy as np
    a = mask[int(r.y0 * ZOOM):int(r.y1 * ZOOM) + 1, int(r.x0 * ZOOM):int(r.x1 * ZOOM) + 1]
    runs = []
    for row in a:
        x = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
        runs += list(x[1::2] - x[0::2])
    return float(np.mean(runs)) if runs else 0.0


def density_bold(page, spans):
    """Merged fonts hide bold: words whose printed strokes are clearly wider than the page's typical
    stroke are bold (regular Arial 11 pt ~3.2 px at 144 dpi, bold ~4.5 px). Words of 1-2 characters
    are unreliable and follow their neighbours."""
    mask = dark_mask(page)
    ws = [s for s in spans if s['merged_font']]
    for s in ws:
        s['_sw'] = stroke_width(mask, s['bbox'])
    ref = [s['_sw'] for s in ws if sum(ch.isalpha() for ch in s['text']) >= 3 and s['size'] >= 9]
    if len(ref) < 5:
        return
    med = statistics.median(ref)
    for s in ws:
        s['bold'] = sum(ch.isalpha() for ch in s['text']) >= 3 and s['_sw'] > 1.22 * med
    ws.sort(key=lambda s: (round(s['oy']), s['bbox'].x0))
    for i, s in enumerate(ws):
        if sum(ch.isalpha() for ch in s['text']) < 3:
            nb = [o for o in ws[max(0, i - 1):i + 2] if o is not s and abs(o['oy'] - s['oy']) < 2]
            s['bold'] = bool(nb) and all(o['bold'] for o in nb)


def fraction_tokens(page, rect, spans, figure_rects):
    """Stacked fractions (a short horizontal bar with text right above and below) -> one inline token
    \\(\\frac{num}{den}\\); the numerator/denominator spans are consumed."""
    toks, used = [], set()
    for d in page.get_drawings():
        r = d['rect']
        if not (r.height < 1.6 and 4 < r.width < 170 and rect.contains(r)):
            continue
        if any(f.intersects(r) for f in figure_rects):
            continue
        y = (r.y0 + r.y1) / 2                       # baselines: numerator just above the bar, denominator below
        num = [i for i, s in enumerate(spans) if i not in used and 0.3 <= y - s['oy'] < 9
               and s['bbox'].x0 >= r.x0 - 3 and s['bbox'].x1 <= r.x1 + 3]
        den = [i for i, s in enumerate(spans) if i not in used and 3 <= s['oy'] - y < 14
               and s['bbox'].x0 >= r.x0 - 3 and s['bbox'].x1 <= r.x1 + 3]
        if not num or not den:
            continue
        def tex(ids):
            ss = sorted((spans[i] for i in ids), key=lambda s: s['bbox'].x0)
            return html_to_tex(tok_html([(inline(s, spans), s['text'], s['bbox'].x0, s['bbox'].x1) for s in ss]))
        used.update(num); used.update(den)
        toks.append({'html': f'\\(\\frac{{{tex(num)}}}{{{tex(den)}}}\\)', 'text': f'({plain(num, spans)})/({plain(den, spans)})',
                     'bbox': fitz.Rect(r.x0, r.y0 - 6, r.x1, r.y1 + 6), 'oy': y + 2.7, 'size': 11})
    return toks, used


def html_to_tex(h):
    """Inline HTML of a numerator/denominator -> LaTeX: words in \\text{}, sub/sup as _{} ^{}."""
    h = htmlmod.unescape(re.sub(r'</?(b|i)>', '', h))
    h = re.sub(r'<sub>(.*?)</sub>', lambda m: '_{' + m.group(1) + '}', h)
    h = re.sub(r'<sup>(.*?)</sup>', lambda m: '^{' + m.group(1) + '}', h)
    # runs of words (2+ letters, with spaces between) become text; single letters stay maths variables;
    # sin/cos/tan are maths functions
    def word(m):
        w = m.group(0)
        return '\\' + w + ' ' if w in ('sin', 'cos', 'tan', 'log', 'ln') else '\\text{' + w + '}'
    h = re.sub(r'[A-Za-z]{2,}(?:\s+[A-Za-z]{2,})*', word, h)
    h = h.replace('%', '\\%').replace('×', '\\times ').replace('÷', '\\div ')
    return re.sub(r'\s+', ' ', h).strip()


def plain(ids, spans):
    return ''.join(spans[i]['text'] for i in sorted(ids, key=lambda i: spans[i]['bbox'].x0)).strip()


def inline(s, spans):
    """HTML for one span: sub/superscript by size and baseline, bold, italic."""
    t = htmlmod.escape(s['text'])
    if s.get('script') == 'sup':
        t = f'<sup>{t}</sup>'
    elif s.get('script') == 'sub':
        t = f'<sub>{t}</sub>'
    if s['italic']:
        t = f'<i>{t}</i>'
    if s['bold']:
        t = f'<b>{t}</b>'
    return t


def mark_scripts(spans):
    """Small spans next to normal ones: above the baseline -> sup, below -> sub."""
    sizes = [s['size'] for s in spans if len(s['text'].strip()) > 1]
    main = statistics.median(sizes) if sizes else 11
    for s in spans:
        if s['size'] < 0.85 * main:
            near = [o for o in spans if o is not s and o['size'] >= 0.95 * main
                    and abs(o['bbox'].y0 - s['bbox'].y0) < main and (abs(o['bbox'].x1 - s['bbox'].x0) < 3 or abs(s['bbox'].x1 - o['bbox'].x0) < 3)]
            if near:
                base = near[0]['oy']
                s['script'] = 'sup' if s['oy'] < base - 0.5 else ('sub' if s['oy'] > base + 0.5 else None)
    return main


def cell_lines(r, spans):
    """HTML lines of the text inside one table cell (from our spans, so sub/sup/italic survive)."""
    inside = [s for s in spans if r.x0 - 1 <= (s['bbox'].x0 + s['bbox'].x1) / 2 <= r.x1 + 1
              and r.y0 - 1 <= (s['bbox'].y0 + s['bbox'].y1) / 2 <= r.y1 + 1]
    lines = []
    for s in sorted(inside, key=lambda s: (s['oy'], s['bbox'].x0)):
        L = next((L for L in lines if abs(L[0] - s['oy']) < (6 if s.get('script') else 2.2)), None)
        if L is None:
            lines.append([s['oy'], [s]])
        else:
            L[1].append(s)
    out = []
    for oy, ss in lines:
        ss.sort(key=lambda s: s['bbox'].x0)
        out.append(tok_html([(inline(s, spans), s['text'], s['bbox'].x0, s['bbox'].x1) for s in ss]))
    return [x for x in out if x]


def table_rows(t, spans):
    """Rows of a ruled table as HTML cells. Cambridge often rules only the columns, so one ruled row
    holds several printed rows: split it when every filled cell has the same number of lines."""
    rows = []
    for row in t.rows:
        cells = [cell_lines(fitz.Rect(c), spans) if c else [] for c in row.cells]
        n = {len(c) for c in cells if c}
        if len(n) == 1 and (k := n.pop()) > 1:
            for i in range(k):
                rows.append([c[i] if c else '' for c in cells])
        else:
            rows.append([' '.join(c) for c in cells])
    return rows


# ---------------------------------------------------------------------------------------------------
def build_segment(page, bbox, figures, tables_out):
    """Blocks for one segment (page strip)."""
    rect = fitz.Rect(bbox)
    fig_rects = [fitz.Rect(f['bbox']) for f in figures]
    spans = spans_in(page, rect)
    if any(s['merged_font'] for s in spans):
        density_bold(page, spans)
    mark_scripts(spans)
    # tables drawn with ruled lines (not those already inside a figure picture's own text)
    table_rects = []
    try:
        for t in page.find_tables(clip=rect, use_layout=False).tables:
            tr = fitz.Rect(t.bbox)
            if tr.height < 15 or tr.width < 60:
                continue
            rows = table_rows(t, spans)
            cells = [c for r in rows for c in r if c]
            if len(cells) < 3 or len(rows) < 2 or max(len(r) for r in rows) < 2:
                continue
            if any(DOTS.search(c) or MARK.search(c) or TOTAL.search(c) for c in cells):
                continue                                   # answer lines read as a table
            if any(re.fullmatch(r'\((?:[a-h]|[ivx]+)\)', c) for c in cells):
                continue                                   # a part label column, not a real table
            if any((tr & f).get_area() > 0.6 * tr.get_area() for f in fig_rects):
                continue                                   # labels inside a diagram, not a table
            table_rects.append(tr)
            tables_out.append({'type': 'table', 'rows': rows, 'y': tr.y0, 'bbox': tr})
    except Exception:
        pass
    keep = [s for s in spans if not any(f.contains(s['bbox']) or (f & s['bbox']).get_area() > 0.6 * s['bbox'].get_area() for f in fig_rects + table_rects)]
    fr, used = fraction_tokens(page, rect, keep, fig_rects + table_rects)
    toks = [{'html': inline(s, keep), 'text': s['text'], 'bbox': s['bbox'], 'oy': s['oy'],
             'size': s['size'], 'script': s.get('script'), 'space_after': s.get('space_after')} for i, s in enumerate(keep) if i not in used] + fr
    # lines by baseline; sub/superscripts join the line of the character they sit next to
    main = [t for t in toks if not t.get('script')]
    scripts = [t for t in toks if t.get('script')]
    main.sort(key=lambda t: (t['oy'], t['bbox'].x0))
    lines = []
    for t in main:
        for L in lines:
            if abs(L['oy'] - t['oy']) < 2.2:
                L['toks'].append(t); break
        else:
            lines.append({'oy': t['oy'], 'toks': [t]})
    for t in scripts:
        best = min(lines, key=lambda L: min(abs(o['bbox'].x1 - t['bbox'].x0) + abs(L['oy'] - t['oy']) for o in L['toks']), default=None)
        if best is not None and abs(best['oy'] - t['oy']) < 9:
            best['toks'].append(t)
        else:
            lines.append({'oy': t['oy'], 'toks': [t]})
    out_lines = []
    for L in lines:
        L['toks'].sort(key=lambda t: t['bbox'].x0)
        h, txt, prev, prev_sp = '', '', None, False
        for t in L['toks']:
            gap = (t['bbox'].x0 - prev.x1) if prev else 0
            if prev and (gap > 1.0 or (prev_sp and gap > 0.4)) and not h.endswith(' ') and not t['html'].startswith(' ') and not t.get('script'):
                h += ' '; txt += ' '
            h += t['html']; txt += t['text']; prev = t['bbox']; prev_sp = t.get('space_after')
        x0 = min(t['bbox'].x0 for t in L['toks']); y0 = min(t['bbox'].y0 for t in L['toks']); y1 = max(t['bbox'].y1 for t in L['toks'])
        h = re.sub(r'\s+', ' ', h)
        out_lines.append({'html': h.strip(), 'text': re.sub(r'\s+', ' ', txt).strip(), 'x0': x0, 'y0': y0, 'y1': y1,
                          'toks': [(t['html'], t['text'], t['bbox'].x0, t['bbox'].x1) for t in L['toks']]})
    out_lines.sort(key=lambda l: l['y0'])
    return out_lines


def strip_html_label(h, t):
    """Remove the leading question/part label ('4', '(a)', '(ii)') from a line (html and text)."""
    m = LABEL.match(t)
    if not m or not m.group(0).strip():
        return h, t
    lab = m.group(0)
    t2 = t[len(lab):]
    # remove the same characters from the html, skipping tags
    out, i, n = [], 0, len(lab.rstrip())
    k = 0
    while i < len(h) and k < n:
        if h[i] == '<':
            j = h.index('>', i) + 1; out.append(h[i:j]); i = j; continue
        if h[i] == '&':
            j = h.index(';', i) + 1; i = j; k += 1; continue
        i += 1; k += 1
    rest = ''.join(out) + h[i:]
    rest = re.sub(r'^(\s|<b>\s*</b>|<i>\s*</i>)+', '', rest)
    rest = re.sub(r'<(b|i|sub|sup)>\s*</\1>', '', rest)
    return rest.strip(), t2.strip()


def option_starts(line, expect):
    """Indexes of tokens that start MCQ options on this line ('A', 'B', ... in order, standing alone and
    first on the line or after a clear gap), with the letters they start."""
    out, toks = [], line['toks']
    for i, (h, t, x0, x1) in enumerate(toks):
        if t.strip() == expect and (i == 0 or x0 - toks[i - 1][3] > 4):
            nxt = toks[i + 1][2] if i + 1 < len(toks) else None
            if nxt is None or nxt - x1 > 3:
                out.append((i, expect)); expect = chr(ord(expect) + 1)
                if expect > 'D':
                    break
    return out


def tok_html(toks):
    h, prev = '', None
    for th, tt, x0, x1 in toks:
        if prev is not None and x0 - prev > 1.0 and not h.endswith(' ') and not th.startswith(' '):
            h += ' '
        h += th; prev = x1
    h = re.sub(r'\s+(</(?:b|i|sub|sup)>)', r'\1 ', h)
    return re.sub(r'\s+', ' ', h).strip()


def to_blocks(lines, figures, tables, seg, mcq=False):
    """Paragraphs, bullet lists, answer space and marks from the ordered lines of one segment."""
    blocks, para = [], None
    captions = {f.get('caption') for f in figures if f.get('caption')}
    opts, expect, opt_x = None, 'A', None
    items = [('line', l['y0'], l) for l in lines] + [('figure', f['bbox'][1], f) for f in figures] + \
            [('table', t['y'], t) for t in tables]
    items.sort(key=lambda x: x[1])
    answer = {'type': 'answer', 'kind': (seg.get('answer_space') or {}).get('kind', 'none')}
    marks = 0
    prev_line = None
    for kind, _, it in items:
        if kind == 'figure':
            para = None
            blocks.append({'type': 'figure', 'id': it['id'], 'caption': it.get('caption')}); continue
        if kind == 'table':
            para = None
            blocks.append({'type': 'table', 'rows': it['rows']}); continue
        l = it
        t, h = l['text'], l['html']
        if t.strip() in captions:                           # the figure block carries its caption
            continue
        if mcq and expect <= 'D':
            st = option_starts(l, expect)
            if st and (st[0][1] != 'A' or st[0][0] == 0):
                if opts is None:
                    opts = {'type': 'options', 'options': []}
                    blocks.append(opts); para = None
                if st[0][0] > 0 and opts['options']:          # text before the first label continues an option
                    opts['options'][-1]['html'] += ' ' + tok_html(l['toks'][:st[0][0]])
                for j, (i, letter) in enumerate(st):
                    end = st[j + 1][0] if j + 1 < len(st) else len(l['toks'])
                    opts['options'].append({'label': letter, 'html': tok_html(l['toks'][i + 1:end])})
                    opt_x = l['toks'][i + 1][2] if i + 1 < end else opt_x
                expect = chr(ord(st[-1][1]) + 1)
                prev_line = l; continue
        if opts is not None and opt_x is not None and l['x0'] >= opt_x - 2 and not DOTS.search(t) and not MARK.fullmatch(t.strip()):
            opts['options'][-1]['html'] += ' ' + h          # an option running onto a second line
            prev_line = l; continue
        for m in MARK.findall(t):
            marks += int(m)
        if TOTAL.search(t):
            t = TOTAL.sub('', t); h = TOTAL.sub('', h)
        if DOTS.search(t):                                   # answer line / dotted lines
            pre = DOTS.split(t)[0].strip()
            post = MARK.sub('', DOTS.split(t)[-1]).strip()
            if pre.startswith(BULLET) or len(pre) > 25 or len(post) > 12:
                # a sentence with a gap to fill ('Room temperature has decreased by ...... .'): keep the words
                t = DOTS.sub('……', t); h = DOTS.sub('……', h)
            elif pre or post:
                blocks.append({k: v for k, v in {'type': 'answer', 'kind': 'answer_line', 'prefix': pre or None,
                                                 'unit': post or None}.items() if v is not None})
                para = None; continue
            else:
                answer['lines'] = answer.get('lines', 0) + 1
                if answer['kind'] in ('none', 'space'):
                    answer['kind'] = 'lines'
                para = None; continue
        t = MARK.sub('', t).strip(); h = MARK.sub('', h).strip()
        if not t:
            continue
        h, t = strip_html_label(h, t)
        if not t:
            continue
        if t.startswith(BULLET):
            ht = re.sub(r'^(<[^>]+>)*\s*•\s*', r'\1', h)
            if blocks and blocks[-1]['type'] == 'list':
                blocks[-1]['items'].append(ht.strip())
            else:
                blocks.append({'type': 'list', 'items': [ht.strip()]})
            para = blocks[-1]; prev_line = l; continue
        joinable = (para is not None and prev_line is not None and para['type'] == 'text'
                    and l['y0'] - prev_line['y1'] < 0.9 * (l['y1'] - l['y0']) and abs(l['x0'] - para['_x0']) < 30)
        if para is not None and para['type'] == 'list' and prev_line is not None and l['y0'] - prev_line['y1'] < 6 and l['x0'] > prev_line['x0'] + 5:
            para['items'][-1] += ' ' + h; prev_line = l; continue
        if joinable:
            para['html'] += ' ' + h; para['text'] += ' ' + t
        else:
            para = {'type': 'text', 'html': h, 'text': t, '_x0': l['x0']}
            blocks.append(para)
        prev_line = l
    for b in blocks:
        b.pop('_x0', None)
    ans = seg.get('answer_space') or {}
    if answer['kind'] in ('none', 'space') and ans.get('working_gap_pt', 0) > 40:
        answer.update({'kind': 'space', 'height_pt': ans.get('working_gap_pt')})
    if answer['kind'] in ('lines', 'space'):         # answer lines with a label were added where they stand
        blocks.append({k: v for k, v in answer.items() if v is not None})
    if marks:
        blocks.append({'type': 'marks', 'value': marks})
    return blocks


def build_node(doc, node, q):
    blocks = []
    figs_all = q.get('figures', [])
    for s in node.get('segments', []):
        page = doc[s['page'] - 1]
        r = fitz.Rect(s['bbox'])
        figs = [f for f in figs_all if f['page'] == s['page'] and fitz.Rect(f['bbox']).intersects(r)
                and (fitz.Rect(f['bbox']) & r).get_area() > 0.5 * fitz.Rect(f['bbox']).get_area()]
        tables = []
        lines = build_segment(page, s['bbox'], figs, tables)
        # a figure that is only a picture of a table found as real rows: keep the editable table
        figs = [f for f in figs if not any((fitz.Rect(f['bbox']) & t['bbox']).get_area() > 0.7 * fitz.Rect(f['bbox']).get_area()
                                           for t in tables)]
        for t in tables:
            t.pop('bbox', None)
        blocks += to_blocks(lines, figs, tables, s, mcq=q.get('type') == 'mcq')
    if q.get('type') == 'mcq' or node.get('parts'):          # no answer space in MCQs or above sub-parts
        blocks = [b for b in blocks if not (b['type'] == 'answer' and (q.get('type') == 'mcq' or b['kind'] == 'space'))]
    if blocks:
        node['content'] = blocks
    for k in node.get('parts', []):
        build_node(doc, k, q)


def build(doc, q):
    build_node(doc, q, q)
    if q.get('type') == 'mcq':
        q['content'] = [b for b in q.get('content', []) if b['type'] != 'marks']
        for b in q['content']:
            if b['type'] == 'options' and (not any(re.sub(r'<[^>]+>', '', o['html']).strip() for o in b['options'])
                                           or [o['label'] for o in b['options']] != list('ABCD')[:len(b['options'])]):
                b['in_figure'] = True                      # options A-D are drawings / labels in the diagram
                b['options'] = [{'label': x, 'html': ''} for x in 'ABCD']
            if b['type'] == 'table' and [re.sub(r'<[^>]+>', '', r[0]).strip() for r in b['rows'] if r][-4:] == list('ABCD'):
                b['options'] = True                        # an options table: one row per answer A-D
    if q.get('type') == 'mcq' and not any(b['type'] == 'options' or b.get('options') for b in q['content']) \
            and (q.get('options') or q.get('figures') or q.get('has_diagram')):
        b = {'type': 'options', 'options': [{'label': o['label'], 'html': htmlmod.escape(o['text'])} for o in q.get('options') or []]}
        if not any(o['text'].strip() for o in q.get('options') or []) or \
                [o['label'] for o in q.get('options') or []] != list('ABCD')[:len(q.get('options') or [])]:
            b = {'type': 'options', 'in_figure': True, 'options': [{'label': x, 'html': ''} for x in 'ABCD']}
        q['content'].append(b)
    return q


def node_html(node, depth=0):
    """Simple HTML preview of the editable layer (review page, website fallback)."""
    out = []
    lab = node.get('label')
    if lab:
        out.append(f'<div class="lab">({lab})</div>')
    for b in node.get('content', []):
        t = b['type']
        if t == 'text':
            out.append(f"<p>{b['html']}</p>")
        elif t == 'list':
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in b['items']) + '</ul>')
        elif t == 'figure':
            out.append(f"<div class=\"fig\" data-id=\"{b['id']}\">[figure {htmlmod.escape(b.get('caption') or '')}]</div>")
        elif t == 'table':
            out.append('<table>' + ''.join('<tr>' + ''.join(f'<td>{htmlmod.escape(c)}</td>' for c in r) + '</tr>' for r in b['rows']) + '</table>')
        elif t == 'answer':
            if b['kind'] == 'answer_line':
                out.append(f"<div class=\"ans\">{htmlmod.escape(b.get('prefix') or '')} ............ {htmlmod.escape(b.get('unit') or '')}</div>")
            elif b['kind'] == 'lines':
                out.append('<div class="ans">' + '<br>'.join(['.' * 60] * b.get('lines', 1)) + '</div>')
            elif b['kind'] == 'space':
                out.append(f"<div class=\"ans space\" style=\"height:{int(b.get('height_pt', 40))}px\"></div>")
        elif t == 'marks':
            out.append(f"<div class=\"marks\">[{b['value']}]</div>")
        elif t == 'options':
            out.append('<ol class="opts">' + ''.join(f"<li><b>{o['label']}</b> {o['html']}</li>" for o in b['options']) + '</ol>')
    for k in node.get('parts', []):
        out.append(f'<div class="part d{depth + 1}">' + node_html(k, depth + 1) + '</div>')
    return '\n'.join(out)


if __name__ == '__main__':
    from run import cleaned
    want = sys.argv[1:]
    files = paths.question_files()
    by_paper = {}
    for f in files:
        pid = '_'.join(os.path.basename(f).split('_')[:3])
        if not want or pid in want:
            by_paper.setdefault(pid, []).append(f)
    n = 0
    for pid, fs in sorted(by_paper.items()):
        doc = fitz.open(cleaned(paths.raw_pdfs(pid + '_q01')[0]))
        for f in fs:
            q = json.load(open(f))
            build(doc, q)
            with open(f, 'w') as fh:
                json.dump(q, fh, ensure_ascii=False, indent=1)
            n += 1
    print(n, 'questions updated with editable content')
