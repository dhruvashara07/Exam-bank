"""EXPERIMENT: per-part layout units and a homework-sheet composer.

    python3 pipeline/experiments/units.py build <paper ids...>          # -> out/units/<paper>/units.json + figures/
    python3 pipeline/experiments/units.py sheet out.pdf <selections...>   # homework PDF (questions, then mark scheme)
        selection = <question id>[:<part>[,<part>...]]   e.g. 0625_2024MJ_42_q02:b-ii  0625_2023MJ_63_q03

A unit = one exact piece of the paper (a part, a part's continuation on the next page, or one mark-scheme
row) stored as data: words (text, x, baseline, width, size, font family, bold/italic, colour), vector
lines/boxes (SVG path data, clipped to the piece) and figures (SVG files placed at their true size).
Coordinates are points (1/72 inch) relative to the piece's top-left, so a unit can be placed anywhere.

Figures keep their printed size exactly; each figure SVG gets a label (<title>/<desc> + data-* attributes):
id, source paper/page/box, size in mm, and whether the question asks to measure on it.
"""
import glob, gzip, json, math, os, re, shutil, subprocess, sys, collections

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
import pymupdf as fitz
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import paths
from run import cleaned
from layout_rebuild import family, unpua, hexcol, span_len

OUT = os.path.join(paths.ROOT, 'out', 'units')
PT2MM = 25.4 / 72
LIB = '/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf'
VARIANT = {'r': 'Regular', 'b': 'Bold', 'i': 'Italic', 'bi': 'BoldItalic'}


# ---------------------------------------------------------------- bold/italic for PDFs that hide font names
def glyph_styles(doc, pages):
    """2025+ Cambridge PDFs merge regular/bold/italic glyphs into one nameless font ('AllAndNone'), so
    text extraction says 'regular' for everything. Each style still has its own glyph id. For every glyph id
    measure stroke weight (ink per box) and slant on the rendered page; for a character drawn with several
    ids, the most used id is regular, a clearly heavier one is bold, a clearly slanted one italic. A character
    with a single id is compared with Liberation Sans regular/bold (weight) and an upright reference (slant)."""
    occ = collections.defaultdict(list)                  # (font, gid) -> [(page, char, bbox)]
    count = collections.Counter()
    for pno in pages:
        for sp in doc[pno].get_texttrace():
            if 'allandnone' not in sp['font'].lower():
                continue
            for c in sp['chars']:
                ch = chr(c[0])
                if not ch.isalnum():
                    continue
                count[(sp['font'], c[1], ch)] += 1
                if len(occ[(sp['font'], c[1])]) < 6:
                    occ[(sp['font'], c[1])].append((pno, ch, c[3]))
    if not occ:
        return {}
    Z = 8
    raster = {}
    def page_ink(pno):
        if pno not in raster:
            pix = doc[pno].get_pixmap(matrix=fitz.Matrix(Z, Z), colorspace=fitz.csGRAY)
            raster[pno] = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w) < 128
        return raster[pno]
    def measure(o):
        h = o.shape[0]
        ys, xs = np.nonzero(o)
        weight = o.sum() / max(1, h * h)          # ink relative to glyph height^2 (size-independent)
        rows = [(y, xs[ys == y].mean()) for y in range(h) if (ys == y).any()]
        if len(rows) > 3:
            yy = np.array([r[0] for r in rows]); xx = np.array([r[1] for r in rows])
            slant = -np.polyfit(yy, xx, 1)[0]      # x shift per pixel going up
        else:
            slant = 0.0
        return weight, slant
    feats = {}
    for key, lst in occ.items():
        ws, ss = [], []
        for pno, ch, bbox in lst:
            a = page_ink(pno)
            x0, y0, x1, y1 = [int(v * Z) for v in bbox]
            crop = a[max(0, y0 - 2):y1 + 2, max(0, x0 - 2):x1 + 2]
            ys, xs = np.nonzero(crop)
            if len(xs) < 20:
                continue
            o = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            w, sl = measure(o)
            ws.append(w); ss.append(sl)
        if ws:
            feats[key] = (lst[0][1], float(np.median(ws)), float(np.median(ss)))
    ref = {}
    def lib(ch, v):
        if (ch, v) not in ref:
            im = Image.new('L', (400, 400), 255)
            ImageDraw.Draw(im).text((50, 300), ch, font=ImageFont.truetype(LIB % VARIANT[v], 200), fill=0, anchor='ls')
            r = np.asarray(im) < 128
            ys, xs = np.nonzero(r)
            ref[(ch, v)] = measure(r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]) if len(xs) else (0, 0)
        return ref[(ch, v)]
    bychar = collections.defaultdict(list)
    for key, (ch, w, sl) in feats.items():
        bychar[(key[0], ch)].append((count[(key[0], key[1], ch)], key, w, sl))
    style = {}
    for (font, ch), lst in bychar.items():
        lst.sort(key=lambda t: -t[0])
        base_w, base_s = lst[0][2], lst[0][3]
        if len(lst) == 1:                         # only one shape: compare with the reference fonts
            rw, bw = lib(ch, 'r')[0], lib(ch, 'b')[0]
            base_w = rw if abs(lst[0][2] - rw) <= abs(lst[0][2] - bw) else lst[0][2] / max(bw / max(rw, 1e-6), 1e-6)
            base_s = lib(ch, 'r')[1]
        for n, key, w, sl in lst:
            b = w > base_w * 1.18
            i = sl - base_s > 0.12
            style[key] = 'bi' if (b and i) else 'b' if b else 'i' if i else 'r'
    return style


def char_styles(doc, pno, gstyle):
    """(x, y) of each character origin -> 'b' / 'i' / 'bi' for glyphs classified as non-regular."""
    out = {}
    if not gstyle:
        return out
    for sp in doc[pno].get_texttrace():
        for c in sp['chars']:
            st = gstyle.get((sp['font'], c[1]))
            if st and st != 'r':
                out[(round(c[2][0], 1), round(c[2][1], 1))] = st
    return out


# ---------------------------------------------------------------- geometry
def tp(m, x, y):
    p = fitz.Point(x, y) * m
    return p.x, p.y


def clip_seg(a, b, r):
    """Clip a straight segment to rect r (Liang-Barsky); None when outside."""
    x0, y0, x1, y1 = a[0], a[1], b[0], b[1]
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - r.x0), (dx, r.x1 - x0), (-dy, y0 - r.y0), (dy, r.y1 - y0)):
        if abs(p) < 1e-9:
            if q < 0:
                return None
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    if t0 > t1:
        return None
    return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)


def drawing_d(dr, m, clip, ox, oy):
    """SVG path data of a drawing in visible coordinates, clipped to `clip`, relative to (ox, oy).
    Straight lines and rectangles are clipped exactly; curves are kept when their box touches the clip."""
    out = []
    f = lambda x, y: f'{x - ox:.2f} {y - oy:.2f}'
    for it in dr['items']:
        k = it[0]
        if k == 'l':
            s = clip_seg(tp(m, it[1].x, it[1].y), tp(m, it[2].x, it[2].y), clip)
            if s and (abs(s[0][0] - s[1][0]) > .01 or abs(s[0][1] - s[1][1]) > .01):
                out.append(f'M{f(*s[0])}L{f(*s[1])}')
        elif k == 're':
            q = fitz.Rect(it[1]).quad * m
            r = q.rect & clip
            if not r.is_empty or (q.rect.width < .01 or q.rect.height < .01):
                r = fitz.Rect(max(q.rect.x0, clip.x0), max(q.rect.y0, clip.y0), min(q.rect.x1, clip.x1), min(q.rect.y1, clip.y1))
                if r.x1 >= r.x0 and r.y1 >= r.y0:
                    out.append(f'M{f(r.x0, r.y0)}H{r.x1 - ox:.2f}V{r.y1 - oy:.2f}H{r.x0 - ox:.2f}Z')
        elif k == 'qu':
            q = it[1] * m
            if q.rect.intersects(clip):
                out.append(f'M{f(q.ul.x, q.ul.y)}L{f(q.ur.x, q.ur.y)}L{f(q.lr.x, q.lr.y)}L{f(q.ll.x, q.ll.y)}Z')
        elif k == 'c':
            pts = [tp(m, p.x, p.y) for p in it[1:5]]
            box = fitz.Rect(min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
            if box.intersects(clip):
                out.append(f'M{f(*pts[0])}C{f(*pts[1])} {f(*pts[2])} {f(*pts[3])}')
    return ''.join(out)


# ---------------------------------------------------------------- one unit
def extract_unit(doc, pno, clip, figs, cstyle):
    """Everything printed inside `clip` (visible page coordinates) on page pno, relative to clip's corner."""
    page = doc[pno]
    m = page.rotation_matrix
    ox, oy = clip.x0, clip.y0
    fig_boxes = [fitz.Rect(f['bbox']) for f in figs]
    def in_fig(r):
        return any(r.x0 >= b.x0 - 1.5 and r.y0 >= b.y0 - 1.5 and r.x1 <= b.x1 + 1.5 and r.y1 <= b.y1 + 1.5 for b in fig_boxes)
    u = {'w': round(clip.width, 2), 'h': round(clip.height, 2), 'text': [], 'paths': [], 'figures': []}
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            dx, dy = l['dir'][0] * m.a + l['dir'][1] * m.c, l['dir'][0] * m.b + l['dir'][1] * m.d
            for s in l['spans']:
                runs, cur = [], []
                for c in s['chars']:
                    if c['c'].strip():
                        cur.append(c)
                    elif cur:
                        runs.append(cur); cur = []
                if cur:
                    runs.append(cur)
                font = s['font']
                bold = bool(s['flags'] & 16) or 'bold' in font.lower()
                italic = bool(s['flags'] & 2) or 'italic' in font.lower() or 'oblique' in font.lower()
                col = hexcol(s['color'])
                for chars in runs:
                    corners = [tp(m, x, y) for c in (chars[0], chars[-1]) for x in (c['bbox'][0], c['bbox'][2]) for y in (c['bbox'][1], c['bbox'][3])]
                    r = fitz.Rect(min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners), max(p[1] for p in corners))
                    cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
                    if not (clip.x0 <= cx <= clip.x1 and clip.y0 <= cy <= clip.y1) or in_fig(r):
                        continue
                    x, y = tp(m, *chars[0]['origin'])
                    rec = {'t': ''.join(unpua(c['c']) for c in chars), 'x': round(x - ox, 2), 'y': round(y - oy, 2),
                           'w': round(span_len(chars, l['dir']), 2), 's': round(s['size'], 2), 'f': family(font)}
                    st = collections.Counter(cstyle.get((round(c['origin'][0], 1), round(c['origin'][1], 1)), 'r')
                                             for c in chars if c['c'].isalnum()) or collections.Counter('r')
                    st = st.most_common(1)[0][0]
                    if bold or 'b' in st: rec['b'] = 1
                    if italic or 'i' in st: rec['i'] = 1
                    if col != '#000000': rec['c'] = col
                    if abs(dy) > 0.01: rec['dir'] = [round(dx, 3), round(dy, 3)]
                    u['text'].append(rec)
    for dr in page.get_drawings():
        q = dr['rect'].quad * m
        r = q.rect
        if not (r.intersects(clip) or (r.width < .01 and clip.x0 <= r.x0 <= clip.x1) or (r.height < .01 and clip.y0 <= r.y0 <= clip.y1)):
            continue
        if in_fig(r):
            continue
        fill, stroke = hexcol(dr.get('fill')), hexcol(dr.get('color'))
        if dr.get('fill_opacity') == 0: fill = None
        if dr.get('stroke_opacity') == 0: stroke = None
        if dr['type'] == 'f': stroke = None
        if dr['type'] == 's': fill = None
        if fill is None and stroke is None:
            continue
        d = drawing_d(dr, m, clip, ox, oy)
        if not d:
            continue
        rec = {'d': d}
        if fill: rec['fill'] = fill
        if dr.get('even_odd'): rec['eo'] = 1
        if stroke:
            rec['stroke'] = stroke; rec['sw'] = round(dr.get('width') or 1, 2)
            mm = re.match(r'\[([^\]]*)\]', dr.get('dashes') or '')
            if mm and mm.group(1).strip():
                rec['dash'] = mm.group(1).strip()
        u['paths'].append(rec)
    for f in figs:
        b = fitz.Rect(f['bbox'])
        cx, cy = (b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2
        if clip.x0 <= cx <= clip.x1 and clip.y0 <= cy <= clip.y1:
            u['figures'].append({'id': f['id'], 'file': f['file'], 'x': round(b.x0 - ox, 2), 'y': round(b.y0 - oy, 2),
                                 'w': round(b.width, 2), 'h': round(b.height, 2)})
    # tags the composer needs: the printed question number, '[Total: n]'
    for t in u['text']:
        if re.fullmatch(r'\d{1,2}', t['t']) and t['x'] < 30 and t.get('b'):
            t['role'] = 'qnum'
        if t['t'].startswith('[Total'):
            t['role'] = 'total'
    for i, t in enumerate(u['text']):
        if t['t'].startswith('[Total') or (i and u['text'][i - 1].get('role') == 'total' and re.fullmatch(r'\d+\]', t['t'])):
            t['role'] = 'total'
    return u


# ---------------------------------------------------------------- build all units of a paper
def nodes(n):
    yield n
    for k in n.get('parts', []):
        yield from nodes(k)


def scale_note(page, fig_rect):
    """Words printed with a figure that matter for measuring."""
    near = fitz.Rect(fig_rect.x0 - 40, fig_rect.y0 - 40, fig_rect.x1 + 40, fig_rect.y1 + 30)
    txt = ' '.join(l[4] for l in page.get_text('words') if fitz.Rect(l[:4]).intersects(near)).lower()
    for k in ('not to scale', 'full size', 'full-size', 'actual size', 'drawn to scale', 'scale:'):
        if k in txt:
            return k
    m = re.search(r'1 ?cm (?:represents|on fig[^ ]* represents) [^.]+', txt)
    return m.group(0) if m else None


def build(pid):
    pj = [p for p in paths.paper_files() if paths.paper_id(json.load(open(p))) == pid][0]
    meta = json.load(open(pj))
    qp_pdf, ms_pdf = paths.raw_pdfs(meta['question_ids'][0])[:2] if False else (None, None)
    raw = os.path.join(paths.ROOT, 'raw', meta['syllabus'], f"{meta['year']}-{meta['session']}")
    pv = meta['paper_code'].split('/')[1]
    qdoc = fitz.open(cleaned(os.path.join(raw, f'qp_{pv}.pdf')))
    mdoc = fitz.open(os.path.join(raw, f'ms_{pv}.pdf'))
    out = os.path.join(OUT, pid)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'figures'))
    qstyle = glyph_styles(qdoc, range(1, len(qdoc)))
    mstyle = glyph_styles(mdoc, range(1, len(mdoc)))
    cst_q, cst_m = {}, {}
    units = {'paper': pid, 'paper_code': meta['paper_code'], 'session': f"{meta['session']} {meta['year']}", 'questions': {}}
    for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
        q = json.load(open(qf))
        figs_by_page = collections.defaultdict(list)
        for f in q.get('figures', []):
            src = os.path.join(paths.ROOT, f['svg']['file'])
            dst = os.path.join(out, 'figures', os.path.basename(src))
            pg = qdoc[f['page'] - 1]
            b = fitz.Rect(f['bbox'])
            text_all = ' '.join(n.get('text', '') for n in nodes(q))
            fignum = re.search(r'(?:Fig\.|Table)\s*[\d.]+', f.get('caption') or '') or None
            measure = bool(fignum and re.search(r'(measure|ruler|protractor)[^.]{0,80}' + re.escape(fignum.group(0)) + r'|'
                                                + re.escape(fignum.group(0)) + r'[^.]{0,40}measure', text_all, re.I))
            label = {'id': f['id'], 'source': f"{meta['paper_code']} {meta['session']} {meta['year']} page {f['page']}",
                     'box_pt': [round(v, 2) for v in b], 'width_mm': round(b.width * PT2MM, 2),
                     'height_mm': round(b.height * PT2MM, 2), 'caption': f.get('caption'),
                     'scale_note': scale_note(pg, b), 'measure': measure,
                     'print_rule': 'print at exactly width_mm x height_mm' if measure else 'may scale on screen; print at true size'}
            svg = open(src).read()
            attrs = ''.join(f' data-{k.replace("_", "-")}="{v}"' for k, v in label.items() if v not in (None, False) and not isinstance(v, list))
            svg = re.sub(r'<svg ', f'<svg{attrs} data-box-pt="{label["box_pt"]}" ', svg, count=1)
            svg = re.sub(r'(<svg[^>]*>)', r'\1' + f'<title>{f["id"]}</title><desc>{json.dumps(label)}</desc>', svg, count=1)
            open(dst, 'w').write(svg)
            figs_by_page[f['page'] - 1].append({'id': f['id'], 'file': os.path.basename(src), 'bbox': f['bbox'], 'label': label})
        qrec = {'id': q['id'], 'number': q['number'], 'marks': q['marks'], 'type': q.get('type'), 'answer': q.get('answer'),
                'parts': [], 'figures': [g['label'] for v in figs_by_page.values() for g in v]}
        for n in nodes(q):
            path = n.get('path') or str(q['number'])
            pu = []
            for s in n.get('segments', []):
                pno = s['page'] - 1
                if pno not in cst_q:
                    cst_q[pno] = char_styles(qdoc, pno, qstyle)
                pu.append(extract_unit(qdoc, pno, fitz.Rect(s['bbox']), figs_by_page.get(pno, []), cst_q[pno]))
            mu = []
            for msr in n.get('mark_scheme', []):
                for s in msr['segments']:
                    pno = s['page'] - 1
                    if pno not in cst_m:
                        cst_m[pno] = char_styles(mdoc, pno, mstyle)
                    mu.append(extract_unit(mdoc, pno, fitz.Rect(s['bbox']), [], cst_m[pno]))
            qrec['parts'].append({'path': path, 'label': n.get('label'), 'marks': n['marks'], 'depth': path.count('('),
                                  'units': pu, 'ms_units': mu})
        units['questions'][q['id']] = qrec
    # mark-scheme table header (Question | Answer | Marks), taken from the first mark-scheme page that has one
    for pno in range(1, len(mdoc)):
        page = mdoc[pno]
        words = page.get_text('words')
        hdr = [w for w in words if w[4] == 'Answer']
        qw = [w for w in words if w[4] == 'Question']
        if hdr and qw:
            yb = max(hdr[0][3], qw[0][3])
            rows = sorted(s['bbox'][1] for qr in units['questions'].values() for p in qr['parts'] for _ in [0]
                          for mu in [0] if False)
            ms_rows = [fitz.Rect(s['bbox']) for qf in glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))
                       for n in nodes(json.load(open(qf))) for r in n.get('mark_scheme', []) for s in r['segments'] if s['page'] == pno + 1]
            if ms_rows:
                first = min(ms_rows, key=lambda r: r.y0)
                clip = fitz.Rect(first.x0, min(hdr[0][1], qw[0][1]) - 5, first.x1, first.y0)
                units['ms_header'] = extract_unit(mdoc, pno, clip, [], char_styles(mdoc, pno, mstyle))
                break
    js = json.dumps(units, ensure_ascii=False, separators=(',', ':'))
    open(os.path.join(out, 'units.json'), 'w').write(js)
    figsz = sum(os.path.getsize(f) for f in glob.glob(os.path.join(out, 'figures', '*.svg')))
    print(f'{pid}: units.json {len(js) // 1024} KB ({len(gzip.compress(js.encode())) // 1024} KB gz), '
          f'{len(glob.glob(os.path.join(out, "figures", "*.svg")))} figures {figsz // 1024} KB, '
          f'bold/italic glyphs found: {sum(v != "r" for v in qstyle.values())} qp / {sum(v != "r" for v in mstyle.values())} ms')
    return units


# ---------------------------------------------------------------- composer
def unit_svg(u, fig_href, renumber=None, drop_total=False, dx=0, dy=0):
    o = [f'<g transform="translate({dx:.2f} {dy:.2f})">']
    for p in u['paths']:
        a = [f'd="{p["d"]}"', f'fill="{p.get("fill", "none")}"']
        if p.get('eo'): a.append('fill-rule="evenodd"')
        if p.get('stroke'):
            a += [f'stroke="{p["stroke"]}"', f'stroke-width="{p["sw"]}"']
            if p.get('dash'): a.append(f'stroke-dasharray="{p["dash"]}"')
        o.append(f'<path {" ".join(a)}/>')
    for f in u['figures']:
        o.append(f'<image href="{fig_href}/{f["file"]}" x="{f["x"]}" y="{f["y"]}" width="{f["w"]}" height="{f["h"]}" '
                 f'preserveAspectRatio="none" data-figure="{f["id"]}"/>')
    for t in u['text']:
        if drop_total and t.get('role') == 'total':
            continue
        txt = renumber if (renumber and t.get('role') == 'qnum') else t['t']
        esc = txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        a = [f'x="{t["x"]}"', f'y="{t["y"]}"', f'font-family="{t["f"]}"', f'font-size="{t["s"]}"']
        if t.get('b'): a.append('font-weight="bold"')
        if t.get('i'): a.append('font-style="italic"')
        if t.get('c'): a.append(f'fill="{t["c"]}"')
        if len(txt) > 1 and t['w'] > 0 and txt == t['t']:
            a.append(f'textLength="{t["w"]}" lengthAdjust="spacingAndGlyphs"')
        if t.get('dir'):
            a.append(f'transform="rotate({math.degrees(math.atan2(t["dir"][1], t["dir"][0])):.1f} {t["x"]} {t["y"]})"')
        o.append(f'<text {" ".join(a)}>{esc}</text>')
    o.append('</g>')
    return '\n'.join(o)


def wanted_parts(q, sel):
    """Selected parts plus their ancestors' stems (a part needs its question's and parent's lead text)."""
    if not sel:
        return [p for p in q['parts']]
    keep = set()
    for s in sel:
        path = f"{q['number']}" + ''.join(f'({x})' for x in s.split('-'))
        for p in q['parts']:
            if p['path'] == path or path.startswith(p['path'] + '(') or p['path'].startswith(path + '(') or p['path'] == str(q['number']):
                keep.add(p['path'])
    return [p for p in q['parts'] if p['path'] in keep]


def sheet(out_pdf, selections, title='Homework'):
    W, H, TOP, BOT = 595.28, 841.89, 56, 800
    pages, cur, y = [], [], TOP
    ms_pages, mcur, my = [], [], 40
    def newpage():
        nonlocal cur, y
        pages.append(cur); cur = []; y = TOP
    total = 0
    header_done = {}
    for n, sel in enumerate(selections, 1):
        qid, _, partsel = sel.partition(':')
        pid = '_'.join(qid.split('_')[:3])
        upath = os.path.join(OUT, pid, 'units.json')
        if not os.path.exists(upath):
            build(pid)
        U = json.load(open(upath))
        q = U['questions'][qid]
        figdir = os.path.relpath(os.path.join(OUT, pid, 'figures'), os.path.dirname(os.path.abspath(out_pdf)))
        parts = wanted_parts(q, [s for s in partsel.split(',') if s])
        leaves = [p for p in parts if not any(o['path'].startswith(p['path'] + '(') for o in parts)]
        marks = q['marks'] if not partsel else sum(p['marks'] for p in leaves)
        total += marks
        src = f"{U['paper_code']} {U['session']} Q{q['number']}" + (f" {partsel}" if partsel else '')
        first = True
        has_num = any(t.get('role') == 'qnum' for p in parts for u in p['units'] for t in u['text'])
        for p in parts:
            for u in p['units']:
                if y + u['h'] > BOT:
                    newpage()
                cur.append(unit_svg(u, figdir, renumber=str(n), drop_total=bool(partsel), dx=0, dy=y - 0))
                if first and not has_num and u['text']:      # question stem not selected: print the number
                    t0 = min(u['text'], key=lambda t: (t['y'], t['x']))
                    cur.append(f'<text x="20" y="{y + t0["y"]:.2f}" font-family="Liberation Sans" font-size="{t0["s"]}" font-weight="bold">{n}</text>')
                if first:
                    cur.append(f'<text x="570" y="{y + 9:.1f}" font-family="Liberation Sans" font-size="6.5" fill="#888" text-anchor="end">{src}</text>')
                    first = False
                y += u['h'] + 4
        if partsel:
            if y + 18 > BOT:
                newpage()
            cur.append(f'<text x="546" y="{y + 10:.1f}" font-family="Liberation Sans" font-size="11" text-anchor="end">[Total: {marks}]</text>')
            y += 18
        y += 10
        # mark scheme
        if q.get('answer'):                       # multiple choice: the key
            if my + 22 > 555:
                ms_pages.append(mcur); mcur = []; my = 40
            mcur.append(f'<text x="50" y="{my + 14:.1f}" font-family="Liberation Sans" font-size="11"><tspan font-weight="bold">{n}</tspan>'
                        f'   answer: <tspan font-weight="bold">{q["answer"]}</tspan>   ({src})</text>')
            my += 22
            continue
        hdr = U.get('ms_header')
        for p in parts:
            for u in p['ms_units']:
                need = u['h'] + (hdr['h'] if (hdr and not mcur) else 0)
                if my + need > 555:
                    ms_pages.append(mcur); mcur = []; my = 40
                if hdr and not any('ms-header' in x for x in mcur):
                    mcur.append('<!--ms-header-->' + unit_svg(hdr, figdir, dx=58 - 0, dy=my)); my += hdr['h']
                mcur.append(unit_svg(u, figdir, renumber=None, dx=58, dy=my))
                mcur.append(f'<text x="50" y="{my + 12:.1f}" font-family="Liberation Sans" font-size="9" font-weight="bold" text-anchor="end">{n}</text>')
                my += u['h']
    pages.append(cur)
    if mcur:
        ms_pages.append(mcur)
    html = ['<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4;margin:0}body{margin:0}'
            '.p{width:210mm;height:297mm;page-break-after:always;overflow:hidden}.l{width:297mm;height:210mm;page-break-after:always;overflow:hidden}'
            '@page land{size:A4 landscape;margin:0}.l{page:land}</style></head><body>']
    for i, pg in enumerate(pages, 1):
        html.append(f'<div class="p"><svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 {W} {H}">'
                    + (f'<text x="297.6" y="40" font-family="Liberation Sans" font-size="12" font-weight="bold" text-anchor="middle">{title}</text>' if i == 1 else '')
                    + '\n'.join(pg) + f'<text x="297.6" y="815" font-family="Liberation Sans" font-size="8" text-anchor="middle">{i}</text></svg></div>')
    for i, pg in enumerate(ms_pages, 1):
        html.append(f'<div class="l"><svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 {H} {W}">'
                    f'<text x="421" y="28" font-family="Liberation Sans" font-size="11" font-weight="bold" text-anchor="middle">{title} — mark scheme (total {total})</text>'
                    + '\n'.join(pg) + '</svg></div>')
    html.append('</body></html>')
    hp = out_pdf[:-4] + '.html'
    open(hp, 'w').write('\n'.join(html))
    js = out_pdf[:-4] + '_print.js'
    open(js, 'w').write("""const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(500);
  await p.pdf({ path: process.argv[3], preferCSSPageSize: true, printBackground: true }); await b.close(); })();""")
    subprocess.run(['node', js, os.path.abspath(hp), os.path.abspath(out_pdf)], check=True, cwd=paths.ROOT)
    print(f'{out_pdf}: {len(pages)} question pages, {len(ms_pages)} mark-scheme pages, {total} marks')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'build':
        for pid in a[1:]:
            build(pid)
    elif a[0] == 'sheet':
        sheet(a[1], a[2:])
