"""EXPERIMENT v2: the proposed question store (one JSON per question), duplicates, homework sheets, checks.

    python3 pipeline/experiments/qstore.py build <paper ids...>       # -> out/store/<paper>/qNN.json, figures/, glyphs/
    python3 pipeline/experiments/qstore.py dupes <session>             # e.g. 2016-MJ: mark identical questions across variants
    python3 pipeline/experiments/qstore.py verify <paper ids...>       # every unit redrawn vs. the original page region
    python3 pipeline/experiments/qstore.py sheet out.pdf <selections>  # homework PDF + mark scheme
        selection = <question id>[:<part>[,<part>]]   e.g. 0625_2024MJ_42_q02:b-ii

Question JSON (schema 3, see SCHEMA below): print layout per part ("layout" units) + mark scheme per part
("ms" rows, each with its own layout unit) + figures with true-size labels. Room for later phases under "meta"
(topics, keywords, solutions) without changing anything else.
"""
import glob, gzip, hashlib, json, math, os, re, shutil, subprocess, sys, collections

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
import pymupdf as fitz
import numpy as np
from PIL import Image
import paths
from run import cleaned
from layout_rebuild import family, unpua, hexcol, span_len, odd
from units import glyph_styles, char_styles, tp, drawing_d, nodes, scale_note

OUT = os.path.join(paths.ROOT, 'out', 'store')
PT2MM = 25.4 / 72
FAM = {'Liberation Sans': 'sans', 'Liberation Serif': 'serif', 'Liberation Mono': 'mono', 'DejaVu Sans': 'symbol'}
CSS_FAM = {'sans': 'Liberation Sans, Arial, Helvetica, sans-serif', 'serif': 'Liberation Serif, Times New Roman, serif',
           'mono': 'Liberation Mono, Courier New, monospace', 'symbol': 'DejaVu Sans, sans-serif'}

SCHEMA = {
    'question': 'schema, id, paper{syllabus,session,code,paper,variant}, number, type, marks, answer, same_as, '
                'parts[], figures[], meta{topics,keywords,difficulty,solution}',
    'part': 'path "2(b)(i)", label "(i)", parent "2(b)", marks, text (plain, for search), layout[unit], ms[row], meta{}',
    'ms row': 'label "2(b)(i)", marks, codes ["B1",...], text, layout[unit]',
    'unit': 'src{doc qp|ms, page, box[x0,y0,x1,y1] pt}, w, h, text[word], lines[path], figs[{id,x,y}], glyphs[{file,x,y,w,h}]',
    'word': 't text, x, y (baseline), w (width), s (size), f (sans|serif|mono|symbol), b/i (1 = bold/italic), '
            'c (colour if not black), dir (writing direction if rotated), role (qnum|total|mslabel)',
    'figure': 'id, file, kind (vector|raster), caption, size_pt[w,h], size_mm[w,h], measure (bool), scale_note, '
              'source{page, box}',
}


# ---------------------------------------------------------------- one exact piece of a page
def unit(doc, pno, clip, figs, cstyle, store, docname):
    page = doc[pno]
    m = page.rotation_matrix
    ox, oy = clip.x0, clip.y0
    boxes = [fitz.Rect(f['source']['box']) for f in figs]
    def in_fig(r):
        return any(r.x0 >= b.x0 - 1.5 and r.y0 >= b.y0 - 1.5 and r.x1 <= b.x1 + 1.5 and r.y1 <= b.y1 + 1.5 for b in boxes)
    def in_fig_c(r):                       # text: its centre inside a figure = printed in the figure
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        return any(b.x0 - 1 <= cx <= b.x1 + 1 and b.y0 - 1 <= cy <= b.y1 + 1 for b in boxes)
    def inside(r):
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        return clip.x0 <= cx <= clip.x1 and clip.y0 <= cy <= clip.y1
    u = {'src': {'doc': docname, 'page': pno + 1, 'box': [round(v, 2) for v in clip]},
         'w': round(clip.width, 2), 'h': round(clip.height, 2), 'text': [], 'lines': [], 'figs': [], 'glyphs': []}
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            dx, dy = l['dir'][0] * m.a + l['dir'][1] * m.c, l['dir'][0] * m.b + l['dir'][1] * m.d
            for s in l['spans']:
                font = s['font']
                if any(odd(c['c'], font) for c in s['chars']):
                    # a symbol we cannot write as a character (dingbat ✓ ✗, unknown code): keep its drawn shape
                    for c in s['chars']:
                        if not c['c'].strip() and ord(c['c'][0]) >= 32:
                            continue
                        q = fitz.Rect(c['bbox']).quad * m
                        r = q.rect
                        if r.is_empty or not inside(r) or in_fig(r):
                            continue
                        key = f"g_{re.sub('[^A-Za-z0-9]', '', font)[:24]}_{ord(c['c'][0]):x}_{round(s['size'] * 10)}_{page.rotation}"
                        gfile = os.path.join(store, 'glyphs', key + '.svg')
                        if not os.path.exists(gfile):
                            from render import region_svg
                            open(gfile, 'w').write(region_svg(doc, pno, [r.x0 - .5, r.y0 - .5, r.x1 + .5, r.y1 + .5]))
                        u['glyphs'].append({'file': key + '.svg', 'x': round(r.x0 - .5 - ox, 2), 'y': round(r.y0 - .5 - oy, 2),
                                            'w': round(r.width + 1, 2), 'h': round(r.height + 1, 2)})
                    continue
                runs, cur = [], []
                for c in s['chars']:
                    if c['c'].strip():
                        cur.append(c)
                    elif cur:
                        runs.append(cur); cur = []
                if cur:
                    runs.append(cur)
                bold = bool(s['flags'] & 16) or 'bold' in font.lower()
                italic = bool(s['flags'] & 2) or 'italic' in font.lower() or 'oblique' in font.lower()
                col = hexcol(s['color'])
                if len(s['chars']) > 1 and abs(dy) < 0.01 and any(
                        b2['origin'][0] < a2['origin'][0] - 0.1 for a2, b2 in zip(s['chars'], s['chars'][1:]) if a2['c'].strip() and b2['c'].strip()):
                    # letters placed right-to-left: mirrored / reversed lettering in a diagram -> keep as drawn
                    r = (fitz.Rect(s['bbox']).quad * m).rect
                    if inside(r) and not in_fig_c(r):
                        name = f"txt_{docname}{pno + 1}_{int(r.x0)}_{int(r.y0)}.svg"
                        from render import region_svg
                        open(os.path.join(store, 'glyphs', name), 'w').write(region_svg(doc, pno, [r.x0 - .5, r.y0 - .5, r.x1 + .5, r.y1 + .5]))
                        u['glyphs'].append({'file': name, 'x': round(r.x0 - .5 - ox, 2), 'y': round(r.y0 - .5 - oy, 2),
                                            'w': round(r.width + 1, 2), 'h': round(r.height + 1, 2)})
                    continue
                for chars in runs:
                    corners = [tp(m, x, y) for c in (chars[0], chars[-1]) for x in (c['bbox'][0], c['bbox'][2]) for y in (c['bbox'][1], c['bbox'][3])]
                    r = fitz.Rect(min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners), max(p[1] for p in corners))
                    if not inside(r) or in_fig_c(r):
                        continue
                    x, y = tp(m, *chars[0]['origin'])
                    w = {'t': ''.join(unpua(c['c']) for c in chars), 'x': round(x - ox, 2), 'y': round(y - oy, 2),
                         'w': round(span_len(chars, l['dir']), 2), 's': round(s['size'], 2), 'f': FAM[family(font)]}
                    st = collections.Counter(cstyle.get((round(c['origin'][0], 1), round(c['origin'][1], 1)), 'r')
                                             for c in chars if c['c'].isalnum()) or collections.Counter('r')
                    st = st.most_common(1)[0][0]
                    if bold or 'b' in st: w['b'] = 1
                    if italic or 'i' in st: w['i'] = 1
                    if col != '#000000': w['c'] = col
                    if abs(dy) > 0.01: w['dir'] = [round(dx, 3), round(dy, 3)]
                    u['text'].append(w)
    stack = []
    for dr in page.get_drawings(extended=True):
        lvl = dr.get('level', 0)
        while stack and stack[-1][0] >= lvl:
            stack.pop()
        if dr['type'] == 'clip':
            sc = dr.get('scissor')
            if sc is not None:
                stack.append((lvl, (fitz.Rect(sc).quad * m).rect))
            continue
        if dr['type'] == 'group':
            continue
        scissor = None
        for _, sc in stack:
            scissor = sc if scissor is None else scissor & sc
        r = (dr['rect'].quad * m).rect
        if scissor is not None:
            if (r & scissor).is_empty and r.width > .01 and r.height > .01:
                continue
        tol = 2.0 if docname == 'ms' else 1.2         # mark-scheme rows end up to 1.5 pt above their table rule
        cl = clip + (-tol, -tol, tol, tol)
        if not (r.intersects(cl) or (r.width < .01 and clip.x0 <= r.x0 <= clip.x1 and r.y1 > clip.y0 and r.y0 < clip.y1)
                or (r.height < .01 and clip.y0 <= r.y0 <= clip.y1 and r.x1 > clip.x0 and r.x0 < clip.x1)):
            continue
        if in_fig(r):
            continue
        fill, stroke = hexcol(dr.get('fill')), hexcol(dr.get('color'))
        # faint background watermark (2026 mark schemes tile a 5 % logo pattern over every page): not content
        if (dr.get('fill_opacity') if dr.get('fill_opacity') is not None else 1) < 0.3: fill = None
        if (dr.get('stroke_opacity') if dr.get('stroke_opacity') is not None else 1) < 0.3: stroke = None
        if dr['type'] == 'f': stroke = None
        if dr['type'] == 's': fill = None
        if fill is None and stroke is None:
            continue
        cbox = clip + (-tol, -tol, tol, tol)
        if scissor is not None:
            cbox = cbox & (scissor + (-.5, -.5, .5, .5))
            if cbox.is_empty:
                continue
        d = drawing_d(dr, m, cbox, ox, oy)   # table rules on the piece's edge belong to it; clipped like the PDF
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
        u['lines'].append(rec)
    # pictures that are not part of a figure crop (a photo or sketch inside a mark-scheme cell): 300 dpi PNG
    for k, info in enumerate(page.get_image_info()):
        r = (fitz.Rect(info['bbox']).quad * m).rect & clip
        if r.is_empty or r.width < 8 or r.height < 8 or not inside(r) or in_fig(r):
            continue
        name = f"img_{docname}{pno + 1}_{int(r.x0)}_{int(r.y0)}.png"
        page.get_pixmap(clip=r, dpi=300).save(os.path.join(store, 'figures', name))
        u.setdefault('images', []).append({'file': name, 'x': round(r.x0 - ox, 2), 'y': round(r.y0 - oy, 2),
                                            'w': round(r.width, 2), 'h': round(r.height, 2)})
    for f in figs:
        b = fitz.Rect(f['source']['box'])
        if inside(b):
            u['figs'].append({'id': f['id'], 'x': round(b.x0 - ox, 2), 'y': round(b.y0 - oy, 2)})
    # roles the sheet builder uses
    for i, t in enumerate(u['text']):
        if docname == 'qp' and re.fullmatch(r'\d{1,2}', t['t']) and t['x'] + ox < 60 and t.get('b'):
            t['role'] = 'qnum'
        if t['t'].startswith('[Total') or (i and u['text'][i - 1].get('role') == 'total' and re.fullmatch(r'\d+\]', t['t'])):
            t['role'] = 'total'
        if docname == 'ms' and t['x'] < 70 and re.match(r'^\d{1,2}(\(|$)', t['t']):
            t['role'] = 'mslabel'
    if not u['glyphs']:
        del u['glyphs']
    return u


# ---------------------------------------------------------------- figures
def save_figure(f, q, meta, qdoc, store):
    b = fitz.Rect(f['bbox'])
    pg = qdoc[f['page'] - 1]
    # raster figure (photo, shaded drawing): any image under it -> 300 dpi PNG of the region (an SVG of a
    # soft-masked image loses parts of its shading in browsers)
    imgs = [fitz.Rect(i['bbox']) for i in pg.get_image_info() if (fitz.Rect(i['bbox']) & b).get_area() > 0.2 * b.get_area()]
    text_all = ' '.join(n.get('text', '') for n in nodes(q))
    fignum = re.search(r'(?:Fig\.|Table)\s*[\d.]+', f.get('caption') or '')
    measure = bool(fignum and re.search(r'(measure|ruler|protractor)[^.]{0,80}' + re.escape(fignum.group(0)) + r'|'
                                        + re.escape(fignum.group(0)) + r'[^.]{0,40}measure', text_all, re.I))
    label = {'id': f['id'], 'kind': 'raster' if imgs else 'vector', 'caption': f.get('caption'),
             'size_pt': [round(b.width, 2), round(b.height, 2)], 'size_mm': [round(b.width * PT2MM, 2), round(b.height * PT2MM, 2)],
             'measure': measure, 'scale_note': scale_note(pg, b),
             'source': {'paper': meta['paper_code'], 'session': f"{meta['session']} {meta['year']}", 'page': f['page'], 'box': [round(v, 2) for v in b]}}
    if imgs:
        name = f['id'] + '.png'
        pg.get_pixmap(clip=b, dpi=300).save(os.path.join(store, 'figures', name))
    else:
        name = f['id'] + '.svg'
        svg = open(os.path.join(paths.ROOT, f['svg']['file'])).read()
        attrs = (f' data-id="{f["id"]}" data-width-mm="{label["size_mm"][0]}" data-height-mm="{label["size_mm"][1]}"'
                 f' data-measure="{str(measure).lower()}" data-source="{label["source"]["paper"]} {label["source"]["session"]} p{f["page"]}"')
        svg = re.sub(r'<svg ', '<svg' + attrs + ' ', svg, count=1)
        svg = re.sub(r'(<svg[^>]*>)', r'\1' + f'<title>{f["id"]}</title><desc>{json.dumps(label)}</desc>', svg, count=1)
        open(os.path.join(store, 'figures', name), 'w').write(svg)
    label['file'] = name
    return label


# ---------------------------------------------------------------- build a paper
def plain(units):
    return ' '.join(w['t'] for u in units for w in u['text'] if w.get('role') not in ('qnum', 'total'))


def build(pid):
    pj = [p for p in paths.paper_files() if paths.paper_id(json.load(open(p))) == pid][0]
    meta = json.load(open(pj))
    raw = os.path.join(paths.ROOT, 'raw', meta['syllabus'], f"{meta['year']}-{meta['session']}")
    pv = meta['paper_code'].split('/')[1]
    qdoc = fitz.open(cleaned(os.path.join(raw, f'qp_{pv}.pdf')))
    mdoc = fitz.open(os.path.join(raw, f'ms_{pv}.pdf'))
    store = os.path.join(OUT, pid)
    shutil.rmtree(store, ignore_errors=True)
    for d in ('figures', 'glyphs'):
        os.makedirs(os.path.join(store, d))
    qstyle, mstyle = glyph_styles(qdoc, range(1, len(qdoc))), glyph_styles(mdoc, range(1, len(mdoc)))
    cst = {}
    def styles(doc, name, pno, gs):
        if (name, pno) not in cst:
            cst[(name, pno)] = char_styles(doc, pno, gs)
        return cst[(name, pno)]
    for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
        q = json.load(open(qf))
        figs = [save_figure(f, q, meta, qdoc, store) for f in q.get('figures', [])]
        rec = {'schema': 3, 'id': q['id'],
               'paper': {'syllabus': meta['syllabus'], 'session': f"{meta['year']}-{meta['session']}", 'code': meta['paper_code'],
                         'paper': meta['paper'], 'variant': meta['variant']},
               'number': q['number'], 'type': 'mcq' if meta.get('is_mcq') else 'structured', 'marks': q['marks'],
               'answer': q.get('answer'), 'same_as': [], 'parts': [], 'figures': figs,
               'meta': {'topics': [], 'keywords': [], 'difficulty': None, 'solution': None}}
        for n in nodes(q):
            path = n.get('path') or str(q['number'])
            lay = []
            for s in n.get('segments', []):
                pno = s['page'] - 1
                lay.append(unit(qdoc, pno, fitz.Rect(s['bbox']), [f for f in figs if f['source']['page'] == s['page']],
                                styles(qdoc, 'qp', pno, qstyle), store, 'qp'))
            ms = []
            for r in n.get('mark_scheme', []):
                ms.append({'label': r['label'], 'codes': r.get('codes', []),
                           'marks': sum(int(re.findall(r'\d+', c)[-1]) for c in r.get('codes', []) if re.findall(r'\d+', c)),
                           'text': r.get('text', ''),
                           'layout': [unit(mdoc, s['page'] - 1, fitz.Rect(s['bbox']), [], styles(mdoc, 'ms', s['page'] - 1, mstyle), store, 'ms')
                                      for s in r['segments']]})
            parent = re.sub(r'\([^()]*\)$', '', path) if '(' in path else None
            rec['parts'].append({'path': path, 'label': n.get('label'), 'parent': parent, 'marks': n['marks'],
                                 'text': plain(lay), 'layout': lay, 'ms': ms, 'meta': {}})
        json.dump(rec, open(os.path.join(store, f"q{q['number']:02d}.json"), 'w'), ensure_ascii=False, separators=(',', ':'))
    # the mark-scheme table header row (Question | Answer | Marks), stored once per paper
    for pno in range(1, len(mdoc)):
        rm = mdoc[pno].rotation_matrix                 # mark-scheme pages are rotated: words in visible coordinates
        words = [tuple(fitz.Rect(w[:4]).quad.__mul__(rm).rect) + (w[4],) for w in mdoc[pno].get_text('words')]
        hw = [w for w in words if w[4] in ('Answer', 'Question')]
        rows = [fitz.Rect(s['bbox']) for qf in glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))
                for n in nodes(json.load(open(qf))) for r in n.get('mark_scheme', []) for s in r['segments'] if s['page'] == pno + 1]
        if len(hw) >= 2 and rows:
            first = min(rows, key=lambda r: r.y0)
            top = min(w[1] for w in hw) - 5
            if top < first.y0:
                hdr = unit(mdoc, pno, fitz.Rect(first.x0, top, first.x1, first.y0), [], styles(mdoc, 'ms', pno, mstyle), store, 'ms')
                json.dump(hdr, open(os.path.join(store, 'ms_header.json'), 'w'), separators=(',', ':'))
                break
    size = lambda pat: sum(os.path.getsize(f) for f in glob.glob(os.path.join(store, pat)))
    js = b''.join(open(f, 'rb').read() for f in glob.glob(os.path.join(store, 'q*.json')))
    print(f'{pid}: {len(glob.glob(os.path.join(store, "q*.json")))} question files {size("q*.json") // 1024} KB '
          f'({len(gzip.compress(js)) // 1024} KB gz), figures {len(os.listdir(os.path.join(store, "figures")))} '
          f'{size("figures/*") // 1024} KB, glyphs {len(os.listdir(os.path.join(store, "glyphs")))}')


# ---------------------------------------------------------------- duplicates (same question in two variants)
def signature(q):
    words = re.sub(r'\s+', ' ', ' '.join(p['text'] for p in q['parts'])).strip().lower()
    figs = sorted(tuple(round(v) for v in f['size_pt']) for f in q['figures'])
    ms = re.sub(r'\s+', ' ', ' '.join(r['text'] for p in q['parts'] for r in p['ms'])).strip().lower()
    return hashlib.sha1(json.dumps([words, figs, q['marks'], q.get('answer')]).encode()).hexdigest()[:16], \
        hashlib.sha1(ms.encode()).hexdigest()[:16]


def dupes(session):
    """Cambridge prints the same question in several variants of one session (e.g. 2016 May/June 32 = 33).
    Same words, same figure sizes, same marks and same mark-scheme text = the same question: the first
    (lowest id) keeps the content, the others become stubs that point to it (store once, list everywhere).
    When only the question matches but the mark scheme differs, both keep their content and say so."""
    files = sorted(glob.glob(os.path.join(OUT, f'0625_{session.replace("-", "")}_*', 'q*.json')))
    by = collections.defaultdict(list)
    for f in files:
        q = json.load(open(f))
        if q.get('stub'):
            q, _ = load(q['same_as'][0])
        sig, ms = signature(q)
        by[sig].append((q['id'], ms, f))
    groups = [v for v in by.values() if len(v) > 1]
    for g in groups:
        g.sort()
        canon = g[0][0]
        same_ms = len({x[1] for x in g}) == 1
        for qid, msig, f in g:
            q = json.load(open(f))
            q['same_as'] = [i for i, _, _ in g if i != qid]
            if qid != canon and msig == g[0][1]:
                stub = {k: q[k] for k in ('schema', 'id', 'paper', 'number', 'type', 'marks', 'answer')}
                stub.update({'stub': True, 'same_as': [canon], 'meta': q['meta']})
                json.dump(stub, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
                for fg in q.get('figures', []):          # its figures live with the canonical copy
                    fp = os.path.join(os.path.dirname(f), 'figures', fg['file'])
                    if os.path.exists(fp):
                        os.remove(fp)
            else:
                json.dump(q, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
        print('same question:', ' = '.join(x[0] for x in g), '(stored once)' if same_ms else '(mark schemes differ: both kept)')
    print(f'{session}: {len(files)} questions, {len(groups)} duplicate groups')


# ---------------------------------------------------------------- drawing units
def unit_svg(u, base, dx=0, dy=0, renumber=None, drop_total=False, figs=None):
    o = [f'<g transform="translate({dx:.2f} {dy:.2f})">']
    for p in u['lines']:
        a = [f'd="{p["d"]}"', f'fill="{p.get("fill", "none")}"']
        if p.get('eo'): a.append('fill-rule="evenodd"')
        if p.get('stroke'):
            a += [f'stroke="{p["stroke"]}"', f'stroke-width="{p["sw"]}"']
            if p.get('dash'): a.append(f'stroke-dasharray="{p["dash"]}"')
        o.append(f'<path {" ".join(a)}/>')
    for im in u.get('images', []):
        o.append(f'<image href="{base}/figures/{im["file"]}" x="{im["x"]}" y="{im["y"]}" width="{im["w"]}" height="{im["h"]}" preserveAspectRatio="none"/>')
    for g in u.get('glyphs', []):
        o.append(f'<image href="{base}/glyphs/{g["file"]}" x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" preserveAspectRatio="none"/>')
    for f in u['figs']:
        fl = figs[f['id']]
        o.append(f'<image href="{base}/figures/{fl["file"]}" x="{f["x"]}" y="{f["y"]}" width="{fl["size_pt"][0]}" '
                 f'height="{fl["size_pt"][1]}" preserveAspectRatio="none"/>')
    for t in u['text']:
        if drop_total and t.get('role') == 'total':
            continue
        txt = t['t']
        if renumber and t.get('role') == 'qnum':
            txt = renumber
        if renumber and t.get('role') == 'mslabel':
            txt = re.sub(r'^\d+', renumber, t['t'])
        esc = txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        a = [f'x="{t["x"]}"', f'y="{t["y"]}"', f'font-family="{CSS_FAM[t["f"]]}"', f'font-size="{t["s"]}"']
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


def load(qid):
    pid = '_'.join(qid.split('_')[:3])
    f = os.path.join(OUT, pid, f"q{int(qid.split('_q')[1]):02d}.json")
    if not os.path.exists(f):
        build(pid)
    return json.load(open(f)), os.path.join(OUT, pid)


def chosen(q, sel):
    """Selected parts, plus the lead text of their question and parent parts, in print order."""
    if not sel:
        return q['parts']
    want = [f"{q['number']}" + ''.join(f'({x})' for x in s.split('-')) for s in sel]
    keep = [p for p in q['parts'] if any(p['path'] == w or w.startswith(p['path'] + '(') or p['path'].startswith(w + '(') for w in want)]
    return keep


SHOT = """const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(600);
  await p.pdf({ path: process.argv[3], preferCSSPageSize: true, printBackground: true }); await b.close(); })();"""


def sheet(out_pdf, selections, title='Homework'):
    """Questions in exam layout: every piece at its original position across the page (Cambridge margins)
    and original size, stacked down the page with page breaks only between pieces; original question numbers
    (numbering is a later feature); then the mark-scheme rows of exactly those parts, as printed."""
    W, H = 595.28, 841.89
    TOP, BOT = 52, 790                    # Cambridge pages: content from ~57 pt to ~790 pt
    qpages, cur, y = [], [], TOP + 26     # first page leaves room for the title
    mpages, mcur, my = [], [], 50
    total = 0
    last_hdr = [None]
    out_dir = os.path.dirname(os.path.abspath(out_pdf))
    def flush_q():
        nonlocal cur, y
        qpages.append(cur); cur = []; y = TOP
    for n, sel in enumerate(selections, 1):
        qid, _, ps = sel.partition(':')
        q, store = load(qid)
        if q.get('stub'):                     # a duplicate stored once: use the canonical copy
            q, store = load(q['same_as'][0])
        base = os.path.relpath(store, out_dir)
        figs = {f['id']: f for f in q['figures']}
        parts = chosen(q, [s for s in ps.split(',') if s])
        leaves = [p for p in parts if not any(o['path'].startswith(p['path'] + '(') for o in parts)]
        marks = q['marks'] if not ps else sum(p['marks'] for p in leaves)
        total += marks
        has_num = any(t.get('role') == 'qnum' for p in parts for u in p['layout'] for t in u['text'])
        first = True
        src = f"{q['paper']['code']} {q['paper']['session']} Q{q['number']}" + (f" {ps}" if ps else '')
        for p in parts:
            for u in p['layout']:
                if y + u['h'] > BOT:
                    flush_q()
                ox = u['src']['box'][0]
                cur.append(unit_svg(u, base, ox, y, drop_total=bool(ps), figs=figs))
                if first:
                    if not has_num and u['text']:   # stem not selected: print the question's own number where Cambridge does
                        t0 = min(u['text'], key=lambda t: (round(t['y']), t['x']))
                        cur.append(f'<text x="49.6" y="{y + t0["y"]:.2f}" font-family="{CSS_FAM["sans"]}" font-size="{t0["s"]}" font-weight="bold">{q["number"]}</text>')
                    cur.append(f'<text x="570" y="{y - 2:.1f}" font-family="{CSS_FAM["sans"]}" font-size="6" fill="#999" text-anchor="end">{src}</text>')
                first = False
                y += u['h']
        if ps:
            if y + 16 > BOT:
                flush_q()
            cur.append(f'<text x="546" y="{y + 11:.1f}" font-family="{CSS_FAM["sans"]}" font-size="11" text-anchor="end">[Total: {marks}]</text>')
            y += 16
        y += 14
        # mark scheme: the rows as printed (original labels), header row at the top of each page
        if q.get('answer'):
            if my + 20 > 560:
                mpages.append(mcur); mcur = []; my = 50
            mcur.append(f'<text x="58" y="{my + 14:.1f}" font-family="{CSS_FAM["sans"]}" font-size="11">{q["paper"]["code"]} {q["paper"]["session"]} '
                        f'Question {q["number"]}:  <tspan font-weight="bold">{q["answer"]}</tspan></text>')
            my += 20
            continue
        hpath = os.path.join(store, 'ms_header.json')
        hdr = json.load(open(hpath)) if os.path.exists(hpath) else None
        for p in parts:
            for r in p['ms']:
                for u in r['layout']:
                    if my + u['h'] + (hdr['h'] + 8 if hdr and last_hdr[0] != store else 0) > 560:
                        mpages.append(mcur); mcur = []; my = 50
                    if hdr and (not mcur or last_hdr[0] != store):   # each paper's rows under its own header row
                        if mcur:
                            my += 8
                        mcur.append(unit_svg(hdr, base, hdr['src']['box'][0], my)); my += hdr['h']; last_hdr[0] = store
                    mcur.append(unit_svg(u, base, u['src']['box'][0], my))
                    my += u['h']
    qpages.append(cur)
    if mcur:
        mpages.append(mcur)
    css = ('@page{size:A4;margin:0}@page land{size:A4 landscape;margin:0}body{margin:0}'
           '.p{width:210mm;height:297mm;break-after:page;overflow:hidden}.l{page:land;width:297mm;height:210mm;break-after:page;overflow:hidden}'
           '.p:last-child,.l:last-child{break-after:auto}')
    html = [f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>']
    np_ = len(qpages)
    for i, pg in enumerate(qpages, 1):
        head = (f'<text x="297.6" y="{TOP + 8}" font-family="{CSS_FAM["sans"]}" font-size="13" font-weight="bold" text-anchor="middle">{title}</text>'
                if i == 1 else '')
        html.append(f'<div class="p"><svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 {W} {H}">{head}'
                    + '\n'.join(pg) + f'<text x="297.6" y="815" font-family="{CSS_FAM["sans"]}" font-size="9" text-anchor="middle">{i}</text></svg></div>')
    for i, pg in enumerate(mpages, 1):
        html.append(f'<div class="l"><svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 {H} {W}">'
                    f'<text x="421" y="32" font-family="{CSS_FAM["sans"]}" font-size="12" font-weight="bold" text-anchor="middle">{title}: mark scheme   (total {total} marks)</text>'
                    + '\n'.join(pg) + f'<text x="421" y="580" font-family="{CSS_FAM["sans"]}" font-size="9" text-anchor="middle">{np_ + i}</text></svg></div>')
    html.append('</body></html>')
    hp = out_pdf[:-4] + '.html'
    open(hp, 'w').write('\n'.join(html))
    js = os.path.join(OUT, '_print.js')
    open(js, 'w').write(SHOT)
    subprocess.run(['node', js, os.path.abspath(hp), os.path.abspath(out_pdf)], check=True, cwd=paths.ROOT)
    print(f'{out_pdf}: {len(qpages)} question pages + {len(mpages)} mark-scheme pages, {total} marks')


# ---------------------------------------------------------------- verification: every unit vs. the original
VSHOT = r"""const { chromium } = require('playwright');
(async () => { const jobs = JSON.parse(require('fs').readFileSync(process.argv[2]));
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 3 });
  for (const [svg, png, w, h] of jobs) { await p.setViewportSize({ width: Math.ceil(w), height: Math.ceil(h) });
    await p.goto('file://' + svg); await p.waitForTimeout(60); await p.screenshot({ path: png, clip: { x: 0, y: 0, width: w, height: h } }); }
  await b.close(); })();"""


def verify(pids, show=12):
    """Redraw every unit on its own (Chromium) and compare with the same region of the original page
    (MuPDF, 216 dpi): 'missing' = printed ink with nothing drawn within 1 pt, 'extra' the reverse."""
    rows = []
    for pid in pids:
        store = os.path.join(OUT, pid)
        if not os.path.isdir(store):
            build(pid)
        pj = [p for p in paths.paper_files() if paths.paper_id(json.load(open(p))) == pid][0]
        meta = json.load(open(pj))
        raw = os.path.join(paths.ROOT, 'raw', meta['syllabus'], f"{meta['year']}-{meta['session']}")
        pv = meta['paper_code'].split('/')[1]
        docs = {'qp': fitz.open(cleaned(os.path.join(raw, f'qp_{pv}.pdf'))), 'ms': fitz.open(os.path.join(raw, f'ms_{pv}.pdf'))}
        vdir = os.path.join(store, '_verify'); os.makedirs(vdir, exist_ok=True)
        jobs, meta_rows = [], []
        for qf in sorted(glob.glob(os.path.join(store, 'q*.json'))):
            q = json.load(open(qf))
            if q.get('stub'):
                continue
            figs = {f['id']: f for f in q['figures']}
            us = [(p['path'], u) for p in q['parts'] for u in p['layout']] + [(r['label'] + ' ms', u) for p in q['parts'] for r in p['ms'] for u in r['layout']]
            for k, (name, u) in enumerate(us):
                key = f"{q['id']}_{k}"
                svg = os.path.join(vdir, key + '.svg')
                M = 3                              # margin, so rules on the piece's edge are inside both renders
                open(svg, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{u["w"] + 2 * M}" height="{u["h"] + 2 * M}" viewBox="{-M} {-M} {u["w"] + 2 * M} {u["h"] + 2 * M}">'
                                     f'<rect width="100%" height="100%" fill="#fff"/>' + unit_svg(u, '..', figs=figs) + '</svg>')
                jobs.append([svg, svg[:-4] + '.png', u['w'] + 2 * M, u['h'] + 2 * M])
                meta_rows.append((pid, q['id'], name, u, svg[:-4] + '.png'))
        jf = os.path.join(vdir, 'jobs.json'); json.dump(jobs, open(jf, 'w'))
        sf = os.path.join(OUT, '_vshot.js'); open(sf, 'w').write(VSHOT)
        subprocess.run(['node', sf, jf], check=True, cwd=paths.ROOT)
        for pid_, qid, name, u, png in meta_rows:
            doc = docs[u['src']['doc']]
            page = doc[u['src']['page'] - 1]
            clip = fitz.Rect(u['src']['box']) + (-3, -3, 3, 3)
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip, colorspace=fitz.csGRAY)   # clip in visible coords
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w)
            b = np.asarray(Image.open(png).convert('L'))          # same scale and origin: pad/crop, never resize
            bb = np.full((pix.h, pix.w), 255, np.uint8)
            hh, ww = min(pix.h, b.shape[0]), min(pix.w, b.shape[1])
            bb[:hh, :ww] = b[:hh, :ww]
            b = bb
            k = 2 * 3                                  # keep the piece plus 1 pt around it (3 pt margin rendered, 3x zoom)
            a, b = a[k:-k or None, k:-k or None], b[k:-k or None, k:-k or None]
            A, B = a < 140, b < 140
            def dil(mk, r=3):
                o = mk.copy()
                for dy_ in range(-r, r + 1):
                    for dx_ in range(-r, r + 1):
                        o |= np.roll(np.roll(mk, dy_, 0), dx_, 1)
                return o
            # the two renderers round sizes differently (up to ~1 px): align the rebuild by the best small shift
            best = None
            for sy in range(-4, 5):
                for sx in range(-4, 5):
                    Bs = np.roll(np.roll(B, sy, 0), sx, 1)
                    sc = int((A ^ Bs).sum())
                    if best is None or sc < best[0]:
                        best = (sc, sy, sx)
            B = np.roll(np.roll(B, best[1], 0), best[2], 1); b = np.roll(np.roll(b, best[1], 0), best[2], 1)
            ink = int(A.sum())
            def opening(mk):                   # drops differences thinner than 3 px (= 1 pt): hairline rules
                er = mk.copy()                 # rendered on different pixel grids, not missing content
                for dy_ in (-1, 0, 1):
                    for dx_ in (-1, 0, 1):
                        er &= np.roll(np.roll(mk, dy_, 0), dx_, 1)
                return dil(er, 1)
            miss, extra = int(opening(A & ~dil(B)).sum()), int(opening(B & ~dil(A)).sum())
            rows.append({'paper': pid_, 'q': qid, 'unit': name, 'ink': ink, 'missing': round(100 * miss / max(ink, 1), 2),
                         'extra': round(100 * extra / max(ink, 1), 2), 'png': png,
                         'orig': (a, b, A, B), 'shift': best[1:]})
    bad = sorted(rows, key=lambda r: -(r['missing'] + r['extra']))
    print(f'{len(rows)} units checked; worse than 1%: {sum(1 for r in rows if r["missing"] > 1 or r["extra"] > 1)}; '
          f'worse than 0.3%: {sum(1 for r in rows if r["missing"] > .3 or r["extra"] > .3)}')
    for r in bad[:show]:
        print(f"  {r['q']:22s} {r['unit']:14s} ink {r['ink']:6d}  missing {r['missing']:5.2f}%  extra {r['extra']:5.2f}%")
    # side-by-side images of the worst ones
    for i, r in enumerate(bad[:show]):
        a, b, A, B = r['orig']
        vis = np.full(a.shape + (3,), 255, np.uint8); vis[A] = (180, 180, 180)
        def dil(mk, rr=3):
            o = mk.copy()
            for dy_ in range(-rr, rr + 1):
                for dx_ in range(-rr, rr + 1):
                    o |= np.roll(np.roll(mk, dy_, 0), dx_, 1)
            return o
        vis[A & ~dil(B)] = (220, 0, 0); vis[B & ~dil(A)] = (0, 90, 220)
        trio = np.concatenate([np.stack([a] * 3, -1), np.stack([b] * 3, -1), vis], 1).astype(np.uint8)
        Image.fromarray(trio).save(os.path.join(OUT, f'_worst_{i:02d}.png'))
    json.dump([{k: v for k, v in r.items() if k not in ('orig',)} for r in rows], open(os.path.join(OUT, '_verify.json'), 'w'), indent=0)
    return rows


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'build':
        for pid in a[1:]:
            build(pid)
    elif a[0] == 'dupes':
        dupes(a[1])
    elif a[0] == 'verify':
        verify(a[1:])
    elif a[0] == 'sheet':
        sheet(a[1], a[2:])
