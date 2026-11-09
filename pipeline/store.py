"""EXPERIMENT v2: the proposed question store (one JSON per question), duplicates, homework sheets, checks.

    python3 pipeline/store.py build <paper ids...>       # -> store/.../<session>/p<pv>/qNN.json, figures/, glyphs/
    python3 pipeline/store.py dupes <session>             # e.g. 2016-MJ: mark identical questions across variants
    python3 pipeline/store.py verify <paper ids...>       # every unit redrawn vs. the original page region
    python3 pipeline/store.py sheet out.pdf <selections>  # homework PDF + mark scheme
        selection = <question id>[:<part>[,<part>]]   e.g. 0625_2024MJ_42_q02:b-ii

Question JSON (schema 4, see SCHEMA below): print layout per part ("layout" units) + mark scheme per part
("ms" rows, each with its own layout unit) + figures with true-size labels. Ruled tables are layout text, not
figures. Multiple choice: `options` A-D (text, table cells, or one figure per option). Later phases (topics,
keywords, solutions) add their own fields; `schema` says which version a document follows.
"""
import glob, gzip, hashlib, json, math, os, re, shutil, subprocess, sys, collections

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
import pymupdf as fitz
import numpy as np
from PIL import Image
import paths
from run import cleaned
from store_text import family, unpua, hexcol, span_len, odd, symbol_family
from store_units import glyph_styles, char_styles, tp, drawing_d, nodes, scale_note
import store_options as OPT
import store_v5 as V5
import ms_layout as ML

OUT = os.path.join(paths.ROOT, 'out', 'store')          # scratch: verify renders, print helpers
PT2MM = 25.4 / 72
TICKS = {('wingdings', 0xFC): '✓', ('wingdings', 0xF0FC): '✓', ('wingdings', 0x2713): '✓', ('wingdings', 0x2714): '✓',
         ('zapf', 0x33): '✓', ('zapf', 0x34): '✓', ('zapf', 0x2713): '✓', ('zapf', 0x2714): '✓',
         ('wingdings', 0xFB): '✗', ('wingdings', 0xF0FB): '✗', ('wingdings', 0x2717): '✗', ('wingdings', 0x2718): '✗',
         ('zapf', 0x37): '✗', ('zapf', 0x38): '✗', ('zapf', 0x2717): '✗', ('zapf', 0x2718): '✗'}


def dingbat_family(font):
    f = font.lower()
    return 'wingdings' if 'wingding' in f else 'zapf' if ('zapf' in f or 'dingbat' in f) else None


def symbol_width(t, sz):
    from store_text import _width
    return _width('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', t, sz) or sz * 0.8


FAM = {'Liberation Sans': 'sans', 'Liberation Serif': 'serif', 'Liberation Mono': 'mono', 'DejaVu Sans': 'symbol'}
CSS_FAM = {'sans': 'Liberation Sans, Arial, Helvetica, sans-serif', 'serif': 'Liberation Serif, Times New Roman, serif',
           'mono': 'Liberation Mono, Courier New, monospace', 'symbol': 'DejaVu Sans, sans-serif'}

SCHEMA = {
    'question': 'schema, id, paper{syllabus,session,code,paper,variant}, number, type, marks, answer, same_as, '
                'parts[], figures[], options[] (mcq), option_columns[] (mcq options in a table)',
    'option': 'label A-D, text, cells[] (table row), figure (id of its own drawing)',
    'ms_scan': 'only when the mark scheme is a scan without text: its pages as pictures',
    'part': 'path "2(b)(i)", label "(i)", parent "2(b)", marks, text (plain, for search), layout[unit], ms[row]',
    'ms row': 'label "2(b)(i)", marks, codes ["B1",...], text, layout[unit]',
    'unit': 'src{doc qp|ms, page, box[x0,y0,x1,y1] pt}, w, h, text[word], lines[path], figs[{id,x,y}], glyphs[{file,x,y,w,h}], '
            'exact (rare: the piece kept as the exact page picture glyphs/<file>, its words still listed for search)',
    'word': 't text, x, y (baseline), w (width), s (size), f (sans|serif|mono|symbol), b/i (1 = bold/italic), '
            'c (colour if not black), dir (writing direction if rotated), hide (1: dots of an answer line, hidden in the '
            'question-bank view), role (qnum|total|mslabel|caption|figref|partlabel|partref; see store_v5.py) with ref {kind,q,n[,other]} / path',
    'unit.answer': 'bands [{y0,y1,kind dots|work}] removed in the question-bank view (working space, full dotted answer lines)',
    'table': 'id, caption, ref, page, box, rows[[cell text]]  (the table itself is text + rules in the layout)',
    'figure': 'id, file, kind (vector|raster), caption, size_pt[w,h], size_mm[w,h], measure (bool), scale_note, '
              'source{page, box}, caption_masked/caption_box (caption blanked in the file, drawn as layout text)',
}


# ---------------------------------------------------------------- one exact piece of a page
def unit(doc, pno, clip, figs, cstyle, store, docname, ctx=None):
    page = doc[pno]
    m = page.rotation_matrix
    ox, oy = clip.x0, clip.y0
    boxes = [fitz.Rect(f['source']['box']) for f in figs]
    capboxes = [fitz.Rect(f['caption_box']) for f in figs if f.get('caption_box') and f['source']['page'] == pno + 1]
    def in_fig(r):
        return any(r.x0 >= b.x0 - 1.5 and r.y0 >= b.y0 - 1.5 and r.x1 <= b.x1 + 1.5 and r.y1 <= b.y1 + 1.5 for b in boxes)
    def in_fig_c(r):                       # text: its centre inside a figure = printed in the figure
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        if any(c.x0 - 1 <= cx <= c.x1 + 1 and c.y0 - 1 <= cy <= c.y1 + 1 for c in capboxes):
            return False                    # the caption of a figure whose crop has it blanked: layout text
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
                        mark = TICKS.get((dingbat_family(font), ord(c['c'][0])))
                        if mark:                      # Dhruv, rounds 19-20: a tick/cross is drawn as a real ✓ / ✗, centred where it was
                            sz = round(s['size'], 2)
                            tw_ = symbol_width(mark, sz)
                            u['text'].append({'t': mark, 'x': round((r.x0 + r.x1) / 2 - tw_ / 2 - ox, 2),
                                              'y': round((r.y0 + r.y1) / 2 + 0.36 * sz - oy, 2), 'w': round(tw_, 2), 's': sz,
                                              'f': 'symbol', **({'c': hexcol(s['color'])} if hexcol(s['color']) != '#000000' else {})})
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
                        # a jump of the baseline inside one run is a new word (')' + denominator '1.8' of the fraction
                        # below, 2026 MJ 41 q7(b)(iii): one PDF run over two lines)
                        if cur and abs(c['origin'][1] - cur[-1]['origin'][1]) > 2.5 and abs(dy) < 0.01:
                            runs.append(cur); cur = []
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
                    c0 = fitz.Rect(chars[0]['bbox']).quad * m        # a word belongs where it starts: 'B1' whose '1'
                    if not inside(c0.rect) or in_fig_c(r):              # crosses the piece's right edge stays
                        continue
                    x, y = tp(m, *chars[0]['origin'])
                    w = {'t': ''.join(unpua(c['c']) for c in chars), 'x': round(x - ox, 2), 'y': round(y - oy, 2),
                         'w': round(span_len(chars, l['dir']), 2), 's': round(s['size'], 2), 'f': FAM[family(font)]}
                    if w['f'] == 'symbol':
                        w['f'], w['s'] = symbol_family(w['t'], w['s'], w['w'])
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
    rects_ = []
    for k, info in enumerate(page.get_image_info()):
        r = (fitz.Rect(info['bbox']).quad * m).rect & clip
        if r.is_empty or r.width < 8 or r.height < 8 or not inside(r) or in_fig(r):
            continue
        rects_.append(r)
    merged_ = True                                # pictures that touch side by side are ONE picture (Dhruv, round 20: 2026 MJ 31 q7(a)(ii))
    while merged_:
        merged_ = False
        for i_ in range(len(rects_)):
            for j_ in range(i_ + 1, len(rects_)):
                a_, b_ = rects_[i_], rects_[j_]
                if min(a_.width, b_.width) >= 50 and min(a_.height, b_.height) >= 40 and \
                        min(a_.y1, b_.y1) - max(a_.y0, b_.y0) > 0.6 * min(a_.height, b_.height) and \
                        max(a_.x0, b_.x0) - min(a_.x1, b_.x1) < 4:   # (not the small pieces of one drawing, 2025 ON 43 q7)
                    rects_[i_] = a_ | b_; del rects_[j_]; merged_ = True; break
            if merged_:
                break
    for r in rects_:
        if docname == 'ms':                   # a picture filling its table cell: keep it off the cell's rules (2016 MJ 41 q10)
            r = fitz.Rect(r.x0, r.y0 + (1.5 if r.y0 <= clip.y0 + 1 else 0), r.x1, r.y1 - (1.5 if r.y1 >= clip.y1 - 1 else 0))
        name = f"img_{docname}{pno + 1}_{int(r.x0)}_{int(r.y0)}.png"
        pix = page.get_pixmap(clip=r, dpi=300)
        if docname == 'ms':                   # white paper is transparent, so our lines stay visible around the picture
            from PIL import Image as _I
            im_ = _I.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
            px = [(rr, gg, bb, 0 if rr > 245 and gg > 245 and bb > 245 else 255) for rr, gg, bb, aa in im_.getdata()]
            im_.putdata(px); im_.save(os.path.join(store, 'figures', name))
        else:
            pix.save(os.path.join(store, 'figures', name))
        u.setdefault('images', []).append({'file': name, 'x': round(r.x0 - ox, 2), 'y': round(r.y0 - oy, 2),
                                            'w': round(r.width, 2), 'h': round(r.height, 2)})
    # shapes filled with a tiled picture (hatched circles = protons, 2019 ON 41 q9): the tiles cannot be placed, so each such
    # small filled shape is kept as a picture of itself (ring + hatching), drawn over its outline
    if any(i['bbox'][2] - i['bbox'][0] < 8 and i['bbox'][3] - i['bbox'][1] < 8 for i in page.get_image_info()):
        for dr in page.get_drawings():
            r = (fitz.Rect(dr['rect']).quad * m).rect
            if dr.get('type') in ('f', 'fs') and len(dr.get('items') or []) >= 40 and 5 < r.width < 40 and 5 < r.height < 40 \
                    and not (r & clip).is_empty and inside(r) and not in_fig(r):
                r = r + (-0.6, -0.6, 0.6, 0.6)
                name = f"img_{docname}{pno + 1}_{int(r.x0)}_{int(r.y0)}.png"
                page.get_pixmap(clip=r, dpi=300).save(os.path.join(store, 'figures', name))
                u.setdefault('images', []).append({'file': name, 'x': round(r.x0 - ox, 2), 'y': round(r.y0 - oy, 2),
                                                    'w': round(r.width, 2), 'h': round(r.height, 2)})
    # glyphs the text layer cannot read (colour-emoji ticks, 2025 FM 42 q6(a)(iv): Segoe UI Emoji maps them to a space,
    # so they were lost): every drawn glyph whose character reads as a space is kept as a picture of itself
    seen_ = set()
    for tr in page.get_texttrace():
        if not any(ch[0] == 32 and ch[1] > 3 for ch in tr['chars']) or 'emoji' not in tr['font'].lower() and 'symbol' not in tr['font'].lower():
            continue
        r = (fitz.Rect(tr['bbox']).quad * m).rect
        if r.width < 3 or r.height < 3 or (r & clip).is_empty or not inside(r) or in_fig(r):
            continue
        k_ = (round(r.x0), round(r.y0))
        if k_ in seen_:
            continue
        seen_.add(k_)
        r = r + (-0.5, -0.5, 0.5, 0.5)
        name = f"emo_{docname}{pno + 1}_{int(r.x0)}_{int(r.y0)}.png"
        pix = page.get_pixmap(clip=r, dpi=300)
        from PIL import Image as _I
        im_ = _I.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
        ink_ = [(rr, gg, bb) for rr, gg, bb, aa in im_.getdata() if not (rr > 200 and gg > 200 and bb > 200)]
        if ink_:
            ar, ag, ab = (sum(p_[i] for p_ in ink_) / len(ink_) for i in range(3))
            if ag > ar + 40 and ag > ab + 40:        # a green tick emoji (2025 FM 42 q6): drawn as a real ✓ in its colour (round 20)
                sz = round(min(r.height, 14.0), 2)
                tw_ = symbol_width('✔', sz)
                u['text'].append({'t': '✔', 'x': round((r.x0 + r.x1) / 2 - tw_ / 2 - ox, 2), 'y': round((r.y0 + r.y1) / 2 + 0.36 * sz - oy, 2),
                                  'w': round(tw_, 2), 's': sz, 'f': 'symbol', 'b': 1, 'c': '#%02x%02x%02x' % (int(ar), int(ag), int(ab))})
                continue
        im_.putdata([(rr, gg, bb, 0 if rr > 245 and gg > 245 and bb > 245 else 255) for rr, gg, bb, aa in im_.getdata()])
        im_.save(os.path.join(store, 'figures', name))
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
    ctx = ctx or {}
    caps = [c for c in ctx.get('captions', []) if c['page'] == pno + 1]
    V5.tag_unit(u, ox, oy, ctx.get('qnum', 0), caps, ctx.get('path', ''), docname, ctx.get('first', False), ctx.get('ms_label'))
    if docname == 'qp':
        bands = V5.answer_bands(u, {f['id']: f['size_pt'] for f in figs})
        if bands:
            u['answer'] = bands
    right = max([t['x'] + t['w'] for t in u['text'] if not t.get('dir')] + [u['w']])
    if right > u['w']:                     # text running past the cut's edge: widen the piece to hold it
        u['w'] = round(right + 1, 2)
    return u


# ---------------------------------------------------------------- figures
FOREIGN = []                                   # words of a neighbouring figure inside the last fit_crop box
SIBLINGS = []                                  # the other figures' boxes on the page (same question), set by build


def fit_crop(pg, b, max_grow=50.0):
    """Mend a figure crop that cuts through ink or a label (review rounds: 80% of 'crop cut' flags were real).
    1. a drawing crossing an edge is taken in (at most max_grow pt per side);
    2. short label lines half inside or just outside (axis label 'day of the month', a row of axis numbers,
       'liquid density = 3.1 g/cm3', 'diagram 1') are taken in, never a caption 'Fig. 1.1', a part '(a) ...' or a question line;
    3. last word: a question sentence half inside, or fully inside above/below the drawing, is cut off."""
    from checks import cut_edges
    from layout import page_bounds, visible_lines, tight_ink
    from extract import split_captions
    t, bt = page_bounds(pg)
    lines = [x for x in (tight_ink(pg, fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])) for l in split_captions(pg, visible_lines(pg, t, bt))) if x]
    ws = pg.get_text('words')
    words_of = lambda l: [w for w in ws if l.contains(fitz.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))]
    NUM_ = re.compile(r'[\d.,\u2212-]+')
    def numeric(lw):
        return bool(lw) and sum(1 for w in lw if NUM_.fullmatch(w[4])) >= 0.7 * len(lw)
    body_x0 = min([l.x0 for l in lines] + [pg.rect.width])
    REALW = re.compile(r"[A-Za-z][A-Za-z'\u2019-]{2,}[.,:;?]?")
    def sentence(lw, l=None):
        # a line of the question's text: real words, and it starts at the text column's left margin (2017 ON 33 q7:
        # 'direction of travel of the water wave' is a label inside the drawing; 'R O Y _ B _ V' is no sentence at all)
        real = [w for w in lw if REALW.fullmatch(w[4])]
        long_ = len(real) >= 5 or (len(real) >= 3 and lw and lw[-1][4][-1:] in '.?:')
        at_margin = l is None or l.x0 <= body_x0 + 25
        return (not numeric(lw) and long_ and at_margin) or (l is not None and (continues(l) or bulleted(l)))
    def bulleted(l):
        # a bullet-list item of the question ('•  metre ruler.', 2023 ON 51 q4): text, however short
        return any(w[4] in ('•', '\u2022') and abs((w[1] + w[3]) / 2 - (l.y0 + l.y1) / 2) < 4 and 0 < l.x0 - w[2] < 40
                   for w in pg.get_text('words'))
    def continues(l):
        # the last line of a wrapped question sentence ('pattern.', 'provided.': 2019 MJ 31 q11, 2019 ON 41 q9):
        # directly under a long text line that starts at or left of it
        for o in lines:
            if o is not l and o.y0 < l.y0 - 3 and l.y0 - o.y1 < 5 and o.x0 <= l.x0 + 3 and o.x1 > l.x0 + 20:
                ow = [w for w in words_of(o) if REALW.fullmatch(w[4])]
                if len(ow) >= 5 and not numeric(words_of(o)):
                    return True
        return False
    def bad_label(lw, l=None):
        txt = ' '.join(w[4] for w in lw)
        return (not lw or sentence(lw, None) or (l is not None and continues(l)) or re.match(r'(Fig|Table)\.?\s', txt + ' ') or re.search(r'\b(Fig|Table)\.', txt)
                or re.match(r'^\(?([a-h]|[ivx]{1,4})\)|^[•\u2022]', txt) or re.fullmatch(r'\[\d+\]|\d{1,2}', txt.strip())
                or re.search(r'\.{4,}|…|\[\d+\]', txt))             # an answer line '..........[1]'
    caps = [l for l in lines if re.match(r'(Fig|Table)\.?\s*\d', ' '.join(w[4] for w in words_of(l)))]
    b0 = fitz.Rect(b)
    drw = [d_['rect'] for d_ in pg.get_drawings()]
    def ok(nb):
        if nb.width - b0.width > 2 * max_grow or nb.height - b0.height > 2 * max_grow:
            return False
        return not any(c.y0 >= (b0.y0 + b0.y1) / 2 and nb.y1 > max(b0.y1, c.y1 + 1) and c.x0 < nb.x1 and c.x1 > nb.x0
                       and not any(r.y0 < c.y0 and r.y1 > c.y1 + 3 and (r.x1 < c.x0 - 2 or r.x0 > c.x1 + 2) and r.intersects(nb)
                                   and r.width < 0.9 * pg.rect.width for r in drw)
                       for c in caps)                    # never grow past the figure's caption (unless the drawing itself goes
                                                         # on beside and below it: 2021 ON 63 q1 magnified scale)
    for _ in range(3):
        changed = False
        if cut_edges(pg, b):
            for d in pg.get_drawings():
                r = d['rect']
                if r.width > 0.9 * pg.rect.width or not r.intersects(b) or b.contains(r):
                    continue
                nb = b | r
                if ok(nb):
                    b = nb; changed = True
        for l in lines:
            if b.contains(l):
                continue
            lw = words_of(l)
            ov = (l & b).get_area() / max(l.get_area(), 1)
            gap = max(l.y0 - b.y1, b.y0 - l.y1, l.x0 - b.x1, b.x0 - l.x1)
            near = ov > 0.15 or (ov == 0 and 0 <= gap < 14 and l.x0 >= b.x0 - 10 and l.x1 <= b.x1 + 10)
            half = ov > 0.15
            label_ok = (not sentence(lw, l)) if half else not bad_label(lw, l)
            if half and re.match(r'(Fig|Table)\.?\s*\d', ' '.join(w[4] for w in lw)):
                label_ok = False
            if near and label_ok and (len(lw) <= 4 or numeric(lw) or half):
                nb = b | l
                if ok(nb):
                    b = nb; changed = True
        if not changed:
            break
    def text_bar(r):                                   # a fraction bar inside a text row ('f = uv / (u + v)'): text, not drawing
        return r.height < 1.2 and any(l.y0 - 3 <= r.y0 <= l.y1 + 3 and r.x0 < l.x1 and r.x1 > l.x0 for l in lines)
    ink = [d['rect'] for d in pg.get_drawings() if d['rect'].intersects(b) and d['rect'].width < 0.9 * pg.rect.width and not text_bar(d['rect'])]
    top, bot = (min(r.y0 for r in ink), max(r.y1 for r in ink)) if ink else (b.y0, b.y1)
    for c in caps:                                     # nothing under the figure's caption ('Method 1' heading, 2020 MJ 53 q3)
        if c.y0 >= (b.y0 + b.y1) / 2 and c.x0 < b.x1 and c.x1 > b.x0 and c.y1 <= b.y1 + 1 and not any(
                r.y1 > c.y1 + 3 and r.intersects(b) and r.width < 0.9 * pg.rect.width for r in (d_['rect'] for d_ in pg.get_drawings())):
            # (only when no drawing goes on under the caption: 2021 ON 63 q1 has the magnified scale below 'Fig. 1.1')
            for l in lines:
                if l is not c and l.y0 >= c.y1 - 1 and l.intersects(b):
                    b.y1 = min(b.y1, max(c.y1 + 0.5, l.y0 - 0.5))
    for l in lines:                                    # the rest of a text row whose start lies outside the crop (2019 MJ 62 q4:
        if (l & b).get_area() < 0.15 * max(l.get_area(), 1):   # 'The equation is:' outside, 'f = uv/(u+v)' inside) is text too
            continue
        if not (l.y1 <= top + 1 or l.y0 >= bot - 1):
            continue
        row = any(not o.intersects(b) and min(o.y1, l.y1) - max(o.y0, l.y0) > 0.4 * min(o.height, l.height) and 0 <= b.x0 - o.x1 < 40
                  and len([w for w in words_of(o) if REALW.fullmatch(w[4])]) >= 2 for o in lines)
        if row:
            if (l.y0 + l.y1) / 2 < (top + bot) / 2:
                b.y0 = max(b.y0, l.y1 + 0.5)
            else:
                b.y1 = min(b.y1, l.y0 - 0.5)
    for l in sorted(lines, key=lambda l: l.y0):
        ov = (l & b).get_area() / max(l.get_area(), 1)
        if ov <= 0.15 or not sentence(words_of(l), l):
            continue
        if ov < 0.85 or l.y1 <= top + 1 or l.y0 >= bot - 1:
            if (l.y0 + l.y1) / 2 < (top + bot) / 2:
                b.y0 = max(b.y0, l.y1 + 0.5)
            else:
                b.y1 = min(b.y1, l.y0 - 0.5)
    # side-by-side figures (2022 FM 62 Fig. 2.2 | 2.3, 2022 ON 31 Fig. 7.1 | 7.2): when the crop reaches over the neighbour's
    # drawing, keep only the ink that belongs to OUR caption (ink grouped by touching pieces, each group to the nearest caption)
    below = [c for c in caps if b.y1 - 40 <= c.y0 <= b.y1 + 45 and c.x1 > b.x0 - 150 and c.x0 < b.x1 + 150]
    below = sorted(below, key=lambda c: c.x0)
    side = [o for o in SIBLINGS if (o & b0).get_area() > 0 and min(o.y1, b0.y1) - max(o.y0, b0.y0) > 0.5 * min(o.height, b0.height)
            and abs((o.x0 + o.x1) / 2 - (b0.x0 + b0.x1) / 2) > 60]    # a neighbour figure BESIDE ours whose box overlaps ours
    if side and len(below) >= 2 and any(abs((c2.x0 + c2.x1) / 2 - (c1.x0 + c1.x1) / 2) > 80 for c1, c2 in zip(below, below[1:])):
        own = min(below, key=lambda c: abs((c.x0 + c.x1) / 2 - (b.x0 + b.x1) / 2))
        items = [fitz.Rect(d_['rect']) for d_ in pg.get_drawings() if d_['rect'].intersects(b) and d_['rect'].width < 0.9 * pg.rect.width]
        items = [r for r in items if (r & b).get_area() > 0 or r.width < 1 or r.height < 1]
        n_draw = len(items)
        items += [fitz.Rect(w[:4]) for w in pg.get_text('words') if fitz.Rect(w[:4]).intersects(b)
                  and not any(fitz.Rect(w[:4]).intersects(c) for c in below)]
        par = list(range(len(items)))
        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]; a = par[a]
            return a
        for a_ in range(len(items)):
            ga = fitz.Rect(items[a_].x0 - 5, items[a_].y0 - 3, items[a_].x1 + 5, items[a_].y1 + 3)   # words of one label stay together
            for c_ in range(a_ + 1, len(items)):
                if ga.intersects(items[c_]):
                    par[find(a_)] = find(c_)
        groups = {}
        for k, r in enumerate(items):
            groups.setdefault(find(k), fitz.Rect(r)).include_rect(r)
        mine_roots = {k for k, g in groups.items() if min(below, key=lambda c: abs((c.x0 + c.x1) / 2 - (g.x0 + g.x1) / 2)) is own}
        mine = [groups[k] for k in mine_roots]
        others = [g for g in groups.values() if g not in mine]
        if mine and others:
            u = fitz.Rect(mine[0])
            for g in mine[1:]:
                u.include_rect(g)
            nb = fitz.Rect(max(b.x0, u.x0 - 2), b.y0, min(b.x1, u.x1 + 2), b.y1)
            if not any((g & nb).get_area() > 0.5 * max(g.get_area(), 1) for g in others) and nb.width > 0.3 * b.width:
                b = nb
                # the neighbour's label words that still reach into our crop ('beaker A with lid' over Fig. 2.2): blanked
                FOREIGN.extend(r for k, r in enumerate(items) if find(k) not in mine_roots and r.intersects(b)
                               and (k >= n_draw or (r & b).get_area() > 4 or (r.width < 1 or r.height < 1)))
    return b


def merge_contained(figs, qid, store, resave=None):
    """Two captioned figures printed side by side whose crops overlap (one inside the other, 2018 MJ 53 q1 Fig. 1.2 / 1.3),
    or that cannot be cut apart without the other's ink (2022 FM 62 Fig. 2.2 / 2.3, 'clash'):
    keep ONE picture (the larger crop) named after both, e.g. id ..._fig1-2+1-3, caption 'Fig. 1.2 and Fig. 1.3'."""
    out = list(figs)
    for big in sorted(figs, key=lambda f: -f['size_pt'][0] * f['size_pt'][1]):
        if big not in out or not big.get('caption'):
            continue
        B = fitz.Rect(big['source']['box'])
        inner = [f for f in out if f is not big and f.get('caption') and f['source']['page'] == big['source']['page']
                 and ((fitz.Rect(f['source']['box']) & B).get_area() > 0.8 * fitz.Rect(f['source']['box']).get_area()
                      or ((big.get('clash') or f.get('clash')) and (fitz.Rect(f['source']['box']) & B).get_area() > 0))]
        if not inner:
            continue
        group = sorted(inner + [big], key=lambda f: f['id'])
        nums = [g['id'].split('_fig')[-1] for g in group]
        new_id = f"{qid}_fig" + '+'.join(nums)
        ext = os.path.splitext(big['file'])[1]
        os.replace(os.path.join(store, 'figures', big['file']), os.path.join(store, 'figures', new_id + ext))
        for g in inner:
            try:
                os.remove(os.path.join(store, 'figures', g['file']))
            except OSError:
                pass
            out.remove(g)
        U = fitz.Rect(B)
        for g in inner:
            U |= fitz.Rect(g['source']['box'])
        cap = ' and '.join(g['caption'] for g in group)
        if resave and (U.x0 < B.x0 - 0.5 or U.y0 < B.y0 - 0.5 or U.x1 > B.x1 + 0.5 or U.y1 > B.y1 + 0.5):
            os.remove(os.path.join(store, 'figures', new_id + ext))   # one picture over both crops (labels of both)
            lab = resave({'id': new_id, 'page': big['source']['page'], 'bbox': list(U), 'caption': None})
            for k in ('kind', 'size_pt', 'size_mm', 'source', 'file', 'scale_note'):
                if k in lab:
                    big[k] = lab[k]
        big['merged'] = [g['id'] for g in group]
        big.pop('clash', None)
        big['id'] = new_id
        big['file'] = big['file'] if big['file'].startswith(new_id) else new_id + ext
        big['caption'] = cap
    return out


def save_figure(f, q, meta, qdoc, store):
    b = fitz.Rect(f['bbox'])
    pg = qdoc[f['page'] - 1]
    cap, cap_in, masked, clash = None, False, False, False
    if not f.get('mask'):
        FOREIGN.clear()
        nb = fit_crop(pg, b)
        if nb != b:
            f = dict(f, bbox=list(nb), svg=None); b = nb
        clash = bool(FOREIGN)                     # Dhruv, round 17: no clean cut without the neighbour's ink -> nothing is
                                                  # blanked; the two figures become ONE picture named after both (merge_contained)
    if f.get('mask'):                         # a printed option letter inside the drawing's box: blank it
        pg = V5.without_caption(pg, fitz.Rect(f['mask']))
        qdoc = pg.parent
        f = dict(f, svg=None)
        masked = True
    if f.get('caption'):                      # v5: the figure file holds the drawing only; the caption is layout text
        cap = V5.caption_rects(pg, b, f['caption'])
        if cap is not None:
            nb, ok = V5.drawing_box(pg, b, cap)
            if ok:
                f = dict(f, bbox=list(nb), svg=None)      # a fresh crop: the stored one still holds the caption
                b = nb
            else:                                        # drawing ink shares the caption's row: keep the box, blank only the
                pg = V5.without_caption(pg, cap)         # caption words (temporary copy of the page; graphics untouched)
                qdoc = pg.parent
                f = dict(f, svg=None)
                masked = True
    # raster figure (photo, shaded drawing): any image under it -> 300 dpi PNG of the region (an SVG of a
    # soft-masked image loses parts of its shading in browsers)
    imgs = [fitz.Rect(i['bbox']) for i in pg.get_image_info() if (fitz.Rect(i['bbox']) & b).get_area() > 0.2 * b.get_area()]
    text_all = ' '.join(n.get('text', '') for n in nodes(q))
    fignum = re.search(r'(?:Fig\.?|Table)\s*[\d.]+', f.get('caption') or '')
    measure = bool(fignum and re.search(r'(measure|ruler|protractor)[^.]{0,80}' + re.escape(fignum.group(0)) + r'|'
                                        + re.escape(fignum.group(0)) + r'[^.]{0,40}measure', text_all, re.I))
    pc = V5.caption_prefix(f.get('caption'))
    label = {'id': f['id'], 'kind': 'raster' if imgs else 'vector', 'caption': f.get('caption'),
             'size_pt': [round(b.width, 2), round(b.height, 2)], 'size_mm': [round(b.width * PT2MM, 2), round(b.height * PT2MM, 2)],
             'measure': measure, 'scale_note': scale_note(pg, b),
             'source': {'paper': meta['paper_code'], 'session': f"{meta['session']} {meta['year']}", 'page': f['page'], 'box': [round(v, 2) for v in b]}}
    if imgs:
        name = f['id'] + '.png'
        pg.get_pixmap(clip=b, dpi=300).save(os.path.join(store, 'figures', name))
    else:
        name = f['id'] + '.svg'
        if f.get('svg'):
            svg = open(os.path.join(paths.ROOT, f['svg']['file'])).read()
        else:                                   # an option drawing cut out of a multiple-choice figure
            from render import region_svg
            svg = region_svg(qdoc, (0 if masked else f['page'] - 1), list(b))
        attrs = (f' data-id="{f["id"]}" data-width-mm="{label["size_mm"][0]}" data-height-mm="{label["size_mm"][1]}"'
                 f' data-measure="{str(measure).lower()}" data-source="{label["source"]["paper"]} {label["source"]["session"]} p{f["page"]}"')
        svg = re.sub(r'<svg ', '<svg' + attrs + ' ', svg, count=1)
        svg = re.sub(r'(<svg[^>]*>)', r'\1' + f'<title>{f["id"]}</title><desc>{json.dumps(label)}</desc>', svg, count=1)
        open(os.path.join(store, 'figures', name), 'w').write(svg)
    label['file'] = name
    if clash:
        label['clash'] = True
    if pc:
        label['ref'] = {'kind': pc[0], 'q': pc[1], 'n': pc[2]}
    if (f.get('caption') or '').startswith('Table'):
        label['table_as_picture'] = OPT.table_picture_reason(pg, b) or 'table not recognised as text'
    if masked and cap is not None:
        label['caption_masked'] = True
        label['caption_box'] = [round(v, 2) for v in cap]
    if f.get('mask'):
        label['letter_masked'] = True             # option figure: the printed letter A-D was blanked
    if cap is not None:
        label['_cap'] = [round(v, 2) for v in cap]
    return label


# ---------------------------------------------------------------- build a paper
def row_marks(codes):
    """Marks of a mark-scheme row: its B1/M1/A1/C1 codes; a bare number (the part's total printed in the
    old marks column, or a 2017+ 'Marks' cell) only when there are no codes."""
    coded = [int(m.group(1)) for c in codes for m in [re.fullmatch(r'\(?[ABCM](\d)\)?', c.strip())] if m]
    if coded:
        return sum(coded)
    return sum(int(x) for c in codes for x in re.findall(r'\d+', c)[-1:])
def plain(units):
    return ' '.join(w['t'] for u in units for w in u['text'] if w.get('role') not in ('qnum', 'total'))


def build(pid):
    pj = [p for p in paths.paper_files() if paths.paper_id(json.load(open(p))) == pid][0]
    meta = json.load(open(pj))
    raw = os.path.join(paths.ROOT, 'raw', meta['syllabus'], f"{meta['year']}-{meta['session']}")
    pv = meta['paper_code'].split('/')[1]
    qdoc = fitz.open(cleaned(os.path.join(raw, f'qp_{pv}.pdf')))
    msp = os.path.join(raw, f'ms_{pv}.pdf')
    mdoc = fitz.open(cleaned(msp)) if os.path.exists(msp) else fitz.open()   # same cleaned copy the cut used
    store = paths.store_dir(pid)
    shutil.rmtree(store, ignore_errors=True)
    for d in ('figures', 'glyphs'):
        os.makedirs(os.path.join(store, d))
    qstyle, mstyle = glyph_styles(qdoc, range(1, len(qdoc))), glyph_styles(mdoc, range(1, len(mdoc)))
    scan = []
    if len(mdoc) and sum(len(pg.get_text().strip()) for pg in mdoc) < 50 * len(mdoc):
        os.makedirs(os.path.join(store, 'ms_pages'))         # no text layer: keep the pages as pictures
        for i, pg in enumerate(mdoc):
            pg.get_pixmap(dpi=150, colorspace=fitz.csGRAY).save(os.path.join(store, 'ms_pages', f'p{i + 1}.png'))
            scan.append(f'ms_pages/p{i + 1}.png')
    cst = {}
    def styles(doc, name, pno, gs):
        if (name, pno) not in cst:
            cst[(name, pno)] = char_styles(doc, pno, gs)
        return cst[(name, pno)]
    for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
        q = json.load(open(qf))
        figs, opts, cols = [], None, None
        captions, tables = [], []                   # v5: caption lines (layout words) and the tables' cells
        for f in q.get('figures', []):
            pg, b = qdoc[f['page'] - 1], fitz.Rect(f['bbox'])
            SIBLINGS[:] = [fitz.Rect(o['bbox']) for o in q.get('figures', []) if o is not f and o['page'] == f['page']]
            is_tab = (f.get('caption') or '').startswith('Table')
            g = OPT.grid(pg, b, table=is_tab)
            tt = None
            if not g and is_tab:                    # no closed grid: a borderless table is text too; a caption-only crop is no figure
                cr0 = V5.caption_rects(pg, b, f['caption'])
                tt = OPT.text_table(pg, b, cr0)
            if tt and not g:
                pc = V5.caption_prefix(f.get('caption'))
                if cr0 is not None and pc:
                    captions.append({'rect': cr0, 'kind': pc[0], 'q': pc[1], 'n': pc[2], 'page': f['page']})
                if tt == 'text' and pc:
                    tables.append({'id': f['id'], 'caption': f['caption'], 'ref': {'kind': pc[0], 'q': pc[1], 'n': pc[2]},
                                   'page': f['page'], 'box': [round(v, 2) for v in b], 'rows': None})
                continue
            if g:                                   # a ruled table: stays text + rules in the layout
                pc = V5.caption_prefix(f.get('caption'))
                if pc:
                    cr = V5.caption_rects(pg, b, f['caption'])
                    if cr is not None:
                        captions.append({'rect': cr, 'kind': pc[0], 'q': pc[1], 'n': pc[2], 'page': f['page']})
                    tables.append({'id': f['id'], 'caption': f['caption'], 'ref': {'kind': pc[0], 'q': pc[1], 'n': pc[2]},
                                   'page': f['page'], 'box': [round(v, 2) for v in g['rect']],
                                   'rows': [[c for c in r] for r in OPT.table_rows(pg, g)]})
                if meta.get('is_mcq') and opts is None:
                    t = OPT.table_options(OPT.table_rows(pg, g)) or OPT.table_options(OPT._row_lines(pg, g, None) or [])
                    if t:
                        cols, opts = t
                continue
            if meta.get('is_mcq') and opts is None:
                ti = OPT.table_inside(pg, b)
                if ti:                              # options table printed inside the drawing's crop
                    t = OPT.table_options(OPT.table_rows(pg, ti[0])) or OPT.table_options(OPT._row_lines(pg, ti[0], None) or [])
                    if t:
                        cols, opts = t
                        f = dict(f, bbox=list(ti[1]), svg=None)
                        figs.append(save_figure(f, q, meta, qdoc, store))
                        continue
            got = OPT.diagram_options(pg, b, with_labels=True) if meta.get('is_mcq') and opts is None else None
            regions, letters = got if got else (None, {})
            if regions:                             # four option drawings: one figure each, WITHOUT the printed letter A-D
                opts = []                           # (the site shows the letter; Dhruv 2026-11-05)
                for L, r in regions.items():
                    sub = {'id': f"{q['id']}_opt{L}", 'page': f['page'], 'bbox': list(r), 'caption': None,
                           'mask': list(letters[L]) if L in letters and (fitz.Rect(letters[L]) & r).get_area() > 0 else None}
                    figs.append(save_figure(sub, q, meta, qdoc, store))
                    opts.append({'label': L, 'figure': sub['id'], 'text': ''})
                continue
            figs.append(save_figure(f, q, meta, qdoc, store))
        SIBLINGS[:] = []
        figs = merge_contained(figs, q['id'], store, lambda f: save_figure(f, q, meta, qdoc, store))   # Fig. 1.2 printed inside Fig. 1.3's crop: one picture, both names (Dhruv)
        for lab in figs:                            # the caption line of each figure: layout words, tagged for renumbering
            cr = lab.pop('_cap', None)
            if cr is not None and lab.get('ref'):
                captions.append({'rect': fitz.Rect(cr), 'kind': lab['ref']['kind'], 'q': lab['ref']['q'], 'n': lab['ref']['n'],
                                 'page': lab['source']['page']})
        rec = {'schema': 5, 'id': q['id'],
               'paper': {'syllabus': meta['syllabus'], 'session': f"{meta['year']}-{meta['session']}", 'code': meta['paper_code'],
                         'paper': meta['paper'], 'variant': meta['variant']},
               'number': q['number'], 'type': 'mcq' if meta.get('is_mcq') else 'structured', 'marks': q['marks'],
               'answer': q.get('answer'), 'same_as': [], 'parts': [], 'figures': figs}
        for n in nodes(q):
            path = n.get('path') or str(q['number'])
            lay = []
            for k, s in enumerate(n.get('segments', [])):
                pno = s['page'] - 1
                lay.append(unit(qdoc, pno, fitz.Rect(s['bbox']), [f for f in figs if f['source']['page'] == s['page']],
                                styles(qdoc, 'qp', pno, qstyle), store, 'qp',
                                {'captions': captions, 'qnum': q['number'], 'path': path, 'first': k == 0}))
            ms = []
            for r in n.get('mark_scheme', []):
                ms.append({'label': r['label'], 'codes': r.get('codes', []),
                           'marks': row_marks(r.get('codes', [])),
                           'text': r.get('text', ''),
                           'layout': [unit(mdoc, s['page'] - 1, fitz.Rect(s['bbox']), [], styles(mdoc, 'ms', s['page'] - 1, mstyle), store, 'ms',
                                           {'qnum': q['number'], 'ms_label': r['label']})
                                      for s in r['segments']]})
            parent = re.sub(r'\([^()]*\)$', '', path) if '(' in path else None
            rec['parts'].append({'path': path, 'label': n.get('label'), 'parent': parent, 'marks': n['marks'],
                                 'text': plain(lay), 'layout': lay, 'ms': ms})
        if meta.get('is_mcq'):
            if opts is None:
                opts = OPT.text_options([u for p in rec['parts'] for u in p['layout']])
            if opts:
                rec['options'] = opts
                if cols:
                    rec['option_columns'] = cols
            else:                                    # letters printed on one drawing (points A-D on a diagram)
                rec['options'] = [{'label': L, 'text': ''} for L in OPT.LETTERS]
                rec['options_on_figure'] = True
                print(f"  {q['id']}: options A-D are marks on a figure", file=sys.stderr)
        if tables:
            rec['tables'] = tables
        if scan:
            rec['ms_scan'] = scan                 # the mark scheme exists only as scanned pages (Nov 2002)
        if not meta.get('is_mcq') and not scan:
            try:                                  # portrait mark scheme in our own frame (docs/MS_TABLE_RULES.md)
                mp = ML.build(rec, store)
                if mp:
                    rec['ms_p'] = {'w': mp['w'], 'h': mp['h'], 'rows': mp['rows'], 'modes': mp['modes'], 'info': mp['info'], 'has_header': mp['has_header'], 'printed_total': mp.get('printed_total'),
                                   'problems': [list(x) for x in mp['problems']]}
            except Exception as e:
                print(f"  {q['id']}: portrait mark scheme failed: {e}", file=sys.stderr)
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
    for qf in glob.glob(os.path.join(store, 'q*.json')):         # the header file exists only now: add the header row
        rec = json.load(open(qf))
        if rec.get('ms_p') and os.path.exists(os.path.join(store, 'ms_header.json')):
            try:                                  # built again now that the header is known: its column count decides
                mp = ML.build(rec, store)         # which rows are inner tables (2021 FM 32 q11)
                if mp:
                    rec['ms_p'] = {'w': mp['w'], 'h': mp['h'], 'rows': mp['rows'], 'modes': mp['modes'], 'info': mp['info'], 'has_header': mp['has_header'], 'printed_total': mp.get('printed_total'),
                                   'problems': [list(x) for x in mp['problems']]}
                    json.dump(rec, open(qf, 'w'), ensure_ascii=False, separators=(',', ':'))
                    continue
            except Exception as e:
                print(f"  {rec['id']}: portrait mark scheme failed: {e}", file=sys.stderr)
        if ML.attach_header(rec, store):
            json.dump(rec, open(qf, 'w'), ensure_ascii=False, separators=(',', ':'))
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
    files = sorted(glob.glob(os.path.join(paths.STORE, '*', '*', session, 'p*', 'q*.json')))
    by = collections.defaultdict(list)
    for f in files:
        q = json.load(open(f))
        own = q['id']
        if q.get('stub'):                        # already a stub: compare with the copy it points to
            if not q.get('same_as'):
                continue
            q, _ = load(q['same_as'][0])
        sig, ms = signature(q)
        by[sig].append((own, ms, f))
    groups = [v for v in by.values() if len(v) > 1]
    for g in groups:
        g.sort()
        canon = g[0][0]
        same_ms = len({x[1] for x in g}) == 1
        for qid, msig, f in g:
            q = json.load(open(f))
            if q.get('stub'):
                if qid != canon:
                    q['same_as'] = [canon]
                    json.dump(q, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
                    continue
                sys.exit(f'{qid}: canonical copy is a stub, rebuild the session')
            q['same_as'] = [i for i, _, _ in g if i != qid]
            if qid != canon and msig == g[0][1]:
                stub = {k: q[k] for k in ('schema', 'id', 'paper', 'number', 'type', 'marks', 'answer')}
                stub.update({'stub': True, 'same_as': [canon]})
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
def bands_of(u, view):
    """Answer bands removed in the question-bank view (none in the print view)."""
    return sorted(u.get('answer', []), key=lambda b: b['y0']) if view == 'bank' and not u.get('exact') else []


def _mark_w(txt, t):
    import renumber as RN
    return RN.text_w(txt, t)


def view_height(u, view='print'):
    return round(u['h'] - sum(b['y1'] - b['y0'] for b in bands_of(u, view)), 2)


def unit_svg(u, base, dx=0, dy=0, renumber=None, drop_total=False, figs=None, view='print', plan=None, doc='qp', meta=None):
    """One unit as SVG. view='bank': answer bands removed and the gaps closed (working space, full dotted lines).
    plan: a renumber.make_plan() result (new question number, Fig/Table numbers, part labels)."""
    if u.get('exact'):                     # kept as the exact picture of the printed piece
        return (f'<g transform="translate({dx:.2f} {dy:.2f})"><image href="{base}/glyphs/{u["exact"]}" x="0" y="0" '
                f'width="{u["src"]["box"][2] - u["src"]["box"][0]:.2f}" height="{u["h"]}" preserveAspectRatio="none"/></g>')
    if plan:
        import renumber as RN
        u = RN.apply_plan(u, plan, doc, meta)
    bands = bands_of(u, view)
    def shift(y):                          # how far content at y moves up: the bands above it
        return sum(b['y1'] - b['y0'] for b in bands if b['y1'] <= y + 0.01)
    def hidden(y0, y1=None):
        y1 = y0 if y1 is None else y1
        return any(b['y0'] - 0.01 <= y0 and y1 <= b['y1'] + 0.01 and b['y1'] > b['y0'] for b in bands)
    o = [f'<g transform="translate({dx:.2f} {dy:.2f})">']
    for p in u['lines']:
        bb = V5.path_bbox(p['d']) if bands else None
        if bb and hidden(bb[1], bb[3]):
            continue
        a = [f'd="{p["d"]}"', f'fill="{p.get("fill", "none")}"']
        if p.get('eo'): a.append('fill-rule="evenodd"')
        if p.get('stroke'):
            a += [f'stroke="{p["stroke"]}"', f'stroke-width="{p["sw"]}"']
            if p.get('dash'): a.append(f'stroke-dasharray="{p["dash"]}"')
        sh = shift(bb[1]) if bb else 0
        tr = f' transform="translate(0 {-sh:.2f})"' if sh else ''
        o.append(f'<path {" ".join(a)}{tr}/>')
    for im in u.get('images', []):
        o.append(f'<image href="{base}/figures/{im["file"]}" x="{im["x"]}" y="{im["y"] - shift(im["y"]):.2f}" width="{im["w"]}" height="{im["h"]}" preserveAspectRatio="none"/>')
    for g in u.get('glyphs', []):
        o.append(f'<image href="{base}/glyphs/{g["file"]}" x="{g["x"]}" y="{g["y"] - shift(g["y"]):.2f}" width="{g["w"]}" height="{g["h"]}" preserveAspectRatio="none"/>')
    for f in u['figs']:
        fl = figs[f['id']]
        o.append(f'<image href="{base}/figures/{fl["file"]}" x="{f["x"]}" y="{f["y"] - shift(f["y"]):.2f}" width="{fl["size_pt"][0] * f.get("k", 1):.2f}" '
                 f'height="{fl["size_pt"][1] * f.get("k", 1):.2f}" preserveAspectRatio="none"/>')
    for t in u['text']:
        if drop_total and t.get('role') == 'total':
            continue
        txt = t['t']
        if view == 'bank' and t.get('hide'):
            mk = re.search(r'\[\s*\d+\s*\]$', txt)
            if not mk:
                continue
            txt, t = mk.group(0), dict(t, x=round(t['x'] + t['w'] - _mark_w(mk.group(0), t), 2), w=0)   # keep only the mark
        elif view == 'bank' and hidden(t['y'] - t['s'] * 0.8, t['y'] + t['s'] * 0.2):
            continue
        if renumber and t.get('role') == 'qnum':
            txt = renumber
        if renumber and t.get('role') == 'mslabel':
            txt = re.sub(r'^\d+', renumber, t['t'])
        esc = txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        y = t['y'] - shift(t['y'])
        a = [f'x="{t["x"]}"', f'y="{y:.2f}"', f'font-family="{CSS_FAM[t["f"]]}"', f'font-size="{t["s"]}"']
        if t.get('b'): a.append('font-weight="bold"')
        if t.get('i'): a.append('font-style="italic"')
        if t.get('c'): a.append(f'fill="{t["c"]}"')
        if len(txt) > 1 and t['w'] > 0 and txt == t['t']:
            a.append(f'textLength="{t["w"]}" lengthAdjust="spacingAndGlyphs"')
        if t.get('dir'):
            a.append(f'transform="rotate({math.degrees(math.atan2(t["dir"][1], t["dir"][0])):.1f} {t["x"]} {y:.2f})"')
        o.append(f'<text {" ".join(a)}>{esc}</text>')
    o.append('</g>')
    return '\n'.join(o)


def load(qid):
    pid = '_'.join(qid.split('_')[:3])
    f = os.path.join(paths.store_dir(pid), f"q{int(qid.split('_q')[1]):02d}.json")
    if not os.path.exists(f):
        build(pid)
    return json.load(open(f)), paths.store_dir(pid)


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
        import renumber as RN
        plan = RN.make_plan(q, parts, n, relabel_parts=True)       # v5: questions 1..n, parts relabelled in print order
        has_num = any(t.get('role') == 'qnum' for p in parts for u in p['layout'] for t in u['text'])
        first = True
        src = f"{q['paper']['code']} {q['paper']['session']} Q{q['number']}" + (f" {ps}" if ps else '')
        for p in parts:
            for ui, u in enumerate(p['layout']):
                if y + u['h'] > BOT:
                    flush_q()
                ox = u['src']['box'][0]
                cur.append(unit_svg(u, base, ox, y, drop_total=bool(ps), figs=figs, plan=plan, meta={'path': p['path'], 'first': ui == 0}))
                if first:
                    if not has_num and u['text']:   # stem not selected: print the question's own number where Cambridge does
                        t0 = min(u['text'], key=lambda t: (round(t['y']), t['x']))
                        cur.append(f'<text x="49.6" y="{y + t0["y"]:.2f}" font-family="{CSS_FAM["sans"]}" font-size="{t0["s"]}" font-weight="bold">{n}</text>')
                    cur.append(f'<text x="570" y="{y - 2:.1f}" font-family="{CSS_FAM["sans"]}" font-size="6" fill="#999" text-anchor="end">{src}</text>')
                first = False
                y += u['h']
        if ps and marks > 0:
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
                        f'Question {n}:  <tspan font-weight="bold">{q["answer"]}</tspan></text>')
            my += 20
            continue
        hpath = os.path.join(store, 'ms_header.json')
        hdr = json.load(open(hpath)) if os.path.exists(hpath) else None
        done_rows = set()
        for p in parts:
            for r in p['ms']:
                for u in r['layout']:
                    key = (u['src']['page'], tuple(u['src']['box']))
                    if key in done_rows:               # one mark-scheme row can belong to several parts: print it once
                        continue
                    done_rows.add(key)
                    if my + u['h'] + (hdr['h'] + 8 if hdr and last_hdr[0] != store else 0) > 560:
                        mpages.append(mcur); mcur = []; my = 50
                    if hdr and (not mcur or last_hdr[0] != store):   # each paper's rows under its own header row
                        if mcur:
                            my += 8
                        mcur.append(unit_svg(hdr, base, hdr['src']['box'][0], my)); my += hdr['h']; last_hdr[0] = store
                    mcur.append(unit_svg(u, base, u['src']['box'][0], my, plan=plan, doc='ms'))
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
    os.makedirs(OUT, exist_ok=True)
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


_PW = {}


def shoot(jobs):
    """Render SVG files with Chromium at 3x (216 dpi): [svg, png, width, height]."""
    if 'page' not in _PW:
        from playwright.sync_api import sync_playwright
        _PW['pw'] = sync_playwright().start()
        _PW['b'] = _PW['pw'].chromium.launch()
        _PW['page'] = _PW['b'].new_page(device_scale_factor=3)
    pg = _PW['page']
    for svg, png, w, h in jobs:
        pg.set_viewport_size({'width': max(1, math.ceil(w)), 'height': max(1, math.ceil(h))})
        pg.goto('file://' + svg)
        pg.wait_for_timeout(30)
        pg.screenshot(path=png, clip={'x': 0, 'y': 0, 'width': w, 'height': h})


def patch(u, M, docs, store, key):
    """Self-repair: printed ink the layout data does not draw (pattern fills, shadings, unusual PDF
    constructs) is cut out of the page as small exact SVG patches placed over the piece. M = missing-ink
    mask in the verify frame (3 px per pt, origin 1 pt left/above the piece)."""
    import scipy.ndimage as ndi
    from render import region_svg
    lab, n = ndi.label(ndi.binary_dilation(M, iterations=6))
    box = fitz.Rect(u['src']['box'])
    doc = docs[u['src']['doc']]
    added = 0
    for i, sl in enumerate(ndi.find_objects(lab)):
        if sl is None or M[sl].sum() < 30:
            continue
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        r = fitz.Rect(box.x0 - 1 + x0 / 3 - 1, box.y0 - 1 + y0 / 3 - 1, box.x0 - 1 + x1 / 3 + 1, box.y0 - 1 + y1 / 3 + 1) & box
        if r.is_empty or r.width < 2 or r.height < 2:
            continue
        name = f'patch_{key}_{i}.svg'
        open(os.path.join(store, 'glyphs', name), 'w').write(region_svg(doc, u['src']['page'] - 1, list(r)))
        u.setdefault('glyphs', []).append({'file': name, 'x': round(r.x0 - box.x0, 2), 'y': round(r.y0 - box.y0, 2),
                                           'w': round(r.width, 2), 'h': round(r.height, 2), 'patch': 1})
        added += 1
    return added


def verify(pids, show=12, repair=True):
    """Redraw every unit on its own (Chromium) and compare with the same region of the original page
    (MuPDF, 216 dpi): 'missing' = printed ink with nothing drawn within 1 pt, 'extra' the reverse."""
    rows = []
    for pid in pids:
        store = paths.store_dir(pid)
        if not os.path.isdir(store):
            build(pid)
        pj = [p for p in paths.paper_files() if paths.paper_id(json.load(open(p))) == pid][0]
        meta = json.load(open(pj))
        raw = os.path.join(paths.ROOT, 'raw', meta['syllabus'], f"{meta['year']}-{meta['session']}")
        pv = meta['paper_code'].split('/')[1]
        docs = {'qp': fitz.open(cleaned(os.path.join(raw, f'qp_{pv}.pdf'))), 'ms': fitz.open(cleaned(os.path.join(raw, f'ms_{pv}.pdf'))) if os.path.exists(os.path.join(raw, f'ms_{pv}.pdf')) else None}
        vdir = os.path.join(OUT, '_verify', pid); shutil.rmtree(vdir, ignore_errors=True); os.makedirs(vdir)
        jobs, meta_rows = [], []
        qdocs = {}
        for qf in sorted(glob.glob(os.path.join(store, 'q*.json'))):
            q = json.load(open(qf))
            if q.get('stub'):
                continue
            qdocs[q['id']] = (qf, q)
            figs = {f['id']: f for f in q['figures']}
            us = [(p['path'], u) for p in q['parts'] for u in p['layout']] + [(r['label'] + ' ms', u) for p in q['parts'] for r in p['ms'] for u in r['layout']]
            for k, (name, u) in enumerate(us):
                key = f"{q['id']}_{k}"
                svg = os.path.join(vdir, key + '.svg')
                M = 3                              # margin, so rules on the piece's edge are inside both renders
                open(svg, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{u["w"] + 2 * M}" height="{u["h"] + 2 * M}" viewBox="{-M} {-M} {u["w"] + 2 * M} {u["h"] + 2 * M}">'
                                     f'<rect width="100%" height="100%" fill="#fff"/>' + unit_svg(u, 'file://' + store, figs=figs) + '</svg>')
                jobs.append([svg, svg[:-4] + '.png', u['w'] + 2 * M, u['h'] + 2 * M])
                meta_rows.append((pid, q['id'], name, u, svg[:-4] + '.png', key))
        shoot(jobs)
        patched = set()
        for pid_, qid, name, u, png, key in meta_rows:
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
            Mmask = opening(A & ~dil(B))
            Mmask[:9] = False; Mmask[-9:] = False     # 1 pt either side of the cut line: neighbouring rows' ascenders
            ink_edge = 0
            Emask = opening(B & ~dil(A)); Emask[:9] = False; Emask[-9:] = False
            miss, extra = int(Mmask.sum()), int(Emask.sum())
            if repair and extra > 0.03 * max(ink, 1) and not u.get('exact'):
                # the layout draws something the page does not show (a clip path it cannot follow): this
                # piece is kept as the exact picture of the page instead; its words stay for search
                from render import region_svg
                name = f'exact_{key}.svg'
                open(os.path.join(store, 'glyphs', name), 'w').write(region_svg(docs[u['src']['doc']], u['src']['page'] - 1, u['src']['box']))
                u['exact'] = name
                patched.add(qid)
            elif repair and miss > 0.01 * max(ink, 1) and not any(g.get('patch') for g in u.get('glyphs', [])):
                if patch(u, Mmask, docs, store, key):     # A (the page) was never shifted: page frame
                    patched.add(qid)
            rows.append({'paper': pid_, 'q': qid, 'unit': name, 'ink': ink, 'missing': round(100 * miss / max(ink, 1), 2),
                         'extra': round(100 * extra / max(ink, 1), 2), 'png': png,
                         'shift': best[1:]})
            if rows[-1]['missing'] + rows[-1]['extra'] > 0.3:     # keep pictures only of the ones worth showing
                rows[-1]['orig'] = (a, b, A, B)
        if patched:                        # save the repaired questions and check this paper again
            for qid in patched:
                qf, q = qdocs[qid]
                json.dump(q, open(qf, 'w'), ensure_ascii=False, separators=(',', ':'))
            rows[:] = [r for r in rows if r['paper'] != pid]
            rows += verify([pid], show=0, repair=False)
            continue
        os.makedirs(paths.STORE_CHECKS, exist_ok=True)
        mine = [r for r in rows if r['paper'] == pid]
        json.dump({'paper': pid, 'units': len(mine),
                   'differ': [{k: r[k] for k in ('q', 'unit', 'missing', 'extra')} for r in mine if r['missing'] > 1 or r['extra'] > 1],
                   'slight': sum(1 for r in mine if .3 < max(r['missing'], r['extra']) <= 1)},
                  open(os.path.join(paths.STORE_CHECKS, pid + '.json'), 'w'), indent=1)
        shutil.rmtree(vdir, ignore_errors=True)
    bad = sorted(rows, key=lambda r: -(r['missing'] + r['extra']))
    print(f'{len(rows)} units checked; worse than 1%: {sum(1 for r in rows if r["missing"] > 1 or r["extra"] > 1)}; '
          f'worse than 0.3%: {sum(1 for r in rows if r["missing"] > .3 or r["extra"] > .3)}')
    for r in bad[:show]:
        print(f"  {r['q']:22s} {r['unit']:14s} ink {r['ink']:6d}  missing {r['missing']:5.2f}%  extra {r['extra']:5.2f}%")
    # side-by-side images of the worst ones
    for i, r in enumerate([r for r in bad if 'orig' in r][:show]):
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


def ids(args):
    """Paper ids from '0625_2024MJ_12', '0625/2024-MJ/12', '2024-MJ/12', or 'ALL'."""
    allp = sorted(paths.paper_id(json.load(open(p))) for p in paths.paper_files())
    out = []
    for x in args:
        if x == 'ALL':
            return allp
        m = re.fullmatch(r'(?:(\d{4})/)?(\d{4})-(\w\w)/(\w+)', x)
        out.append(f"{m.group(1) or '0625'}_{m.group(2)}{m.group(3)}_{m.group(4)}" if m else x)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] in ('build', 'verify'):
        a = [a[0]] + ids(a[1:])
    if a[0] == 'build':
        for pid in a[1:]:
            build(pid)
    elif a[0] == 'dupes':
        dupes(a[1])
    elif a[0] == 'verify':
        verify(a[1:])
    elif a[0] == 'sheet':
        sheet(a[1], a[2:])


# ---------------------------------------------------------------- pictures for the review page
def stacked_svg(units, store, figs, path, gap=6):
    """Write one SVG with the units under each other (each at its own width), as stored = as students get it."""
    y, body = 0, []
    W = max([u['w'] for u in units] + [1])
    for u in units:
        body.append(unit_svg(u, 'file://' + store, 0, y, figs=figs)); y += u['h'] + gap
    H = max(y - gap, 1)
    open(path, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}" height="{H:.2f}" viewBox="0 0 {W:.2f} {H:.2f}">'
                          f'<rect width="100%" height="100%" fill="#fff"/>' + '\n'.join(body) + '</svg>')
    return path


def review_svgs(qid, tmp):
    """{'q': svg of the question, 'ms': svg of its mark-scheme rows, 'figs': [figure files]} from the store."""
    q, store = load(qid)
    if q.get('stub'):
        q, store = load(q['same_as'][0])
    figs = {f['id']: f for f in q['figures']}
    os.makedirs(tmp, exist_ok=True)
    out = {'q': stacked_svg([u for p in q['parts'] for u in p['layout']], store, figs, os.path.join(tmp, qid + '_q.svg'))}
    ms = q['ms_p']['rows'] if q.get('ms_p') else [u for p in q['parts'] for r in p['ms'] for u in r['layout']]
    if ms:
        out['ms'] = stacked_svg(ms, store, figs, os.path.join(tmp, qid + '_ms.svg'), gap=0 if q.get('ms_p') else 6)
    out['figs'] = [os.path.join(store, 'figures', f['file']) for f in q['figures']]
    out['fig_ids'] = [{'id': f['id'], 'caption': f.get('caption')} for f in q['figures']]   # what is stored (the review legend)
    out['options'] = q.get('options', [])
    return out
