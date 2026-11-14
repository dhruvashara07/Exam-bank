"""Split a cleaned Cambridge question paper into questions, parts and printable segments.

A *segment* is a horizontal strip of one page that belongs to exactly one label path,
for example question 4's stem, 4(a)'s stem, or 4(a)(ii). Printing the segments of a
question (or of a chosen part plus its parent stems) in order reproduces the original
layout, answer space included.
"""
import os, re
import subjects
import pymupdf as fitz
from layout import page_bounds, visible_lines, ink_boxes, label_tokens, ROMAN, LETTERS, CONTENT_X0, CONTENT_X1, row_ink, ink_extent, ZOOM, tight_ink, grow_to_ink

PAD_TOP, PAD_BOTTOM = 4.0, 5.0
TOTAL_SLIPS = {'0625_2007MJ_03_q11'}   # the paper prints [Total: 12] for q10 + q11 together (Dhruv, round 23)
CAPTION = re.compile(r'^(Fig\.?|Figure|Table)\s*\d+(\.\d+)?[a-d]?(\s*\(.*\))?$')   # 'Fig. 2.1a' (2006 ON 03 q2)   # 'Fig 4.1' (no full stop) too
MARK = re.compile(r'\[\s*(\d{1,2})\s*\]')
TOTAL = re.compile(r'\[\s*Total\s*:\s*(\d{1,3})\s*\]')
DOTS = re.compile(r'\.{12,}')

SESSION_NAMES = {'FM': 'February-March', 'MJ': 'May-June', 'ON': 'October-November'}
PAPER_TYPES = {1: 'mcq_core', 2: 'mcq_extended', 3: 'theory_core', 4: 'theory_extended',
               5: 'practical_test', 6: 'alternative_to_practical'}
# Before 2009 (0625/01 ... 0625/06, no variant) the cover prints only 'Paper 2': 1 = multiple choice (everyone),
# 2 = core theory, 3 = extended theory, 5 = practical test, 6 = alternative to practical.
OLD_PAPER_TYPES = {1: 'mcq', 2: 'theory_core', 3: 'theory_extended', 5: 'practical_test', 6: 'alternative_to_practical'}


# Standard totals, used when the cover does not print one (covers before 2020).
STANDARD_TOTAL = {'mcq_core': 40, 'mcq_extended': 40, 'mcq': 40, 'theory_core': 80, 'theory_extended': 80,
                  'practical_test': 40, 'alternative_to_practical': 40}


def paper_type_from_cover(cover, paper, old=False):
    """Read the paper type from the cover ('Paper 2 Core' in 2015 is theory, 'Paper 2 Multiple Choice
    (Extended)' from 2016 is MCQ); fall back to the current numbering."""
    m = re.search(r'Paper\s+\d\s+([^\n]+)', cover)
    title = (m.group(1) if m else '').lower()
    if 'multiple choice' in title:
        return 'mcq_extended' if 'extended' in title else ('mcq_core' if 'core' in title else 'mcq')
    if 'alternative to practical' in title:
        return 'alternative_to_practical'
    if 'practical' in title:
        return 'practical_test'
    if 'extended' in title:
        return 'theory_extended'
    if 'core' in title or 'theory' in title:
        return 'theory_core'
    return (OLD_PAPER_TYPES if old else PAPER_TYPES)[paper]


def paper_meta(doc, syllabus, year, session, pv):
    cover = doc[0].get_text()
    total = subjects.total_from_cover(cover, syllabus)
    dur = re.search(r'\n\s*(\d+ hours?(?: \d+ minutes)?|\d+ minutes)\s*\n', cover)
    old = pv[0] == '0'                     # before 2009 one paper per component: 0625/03 (no variant)
    paper, variant = (int(pv[1]), 0) if old else (int(pv[0]), int(pv[1]))
    if subjects.is_physics(syllabus):
        ptype = paper_type_from_cover(cover, paper, old)
    else:
        ptype = subjects.maths_paper_type(cover, paper)
    return {
        'syllabus': syllabus, 'subject': subjects.subject(syllabus)['subject'], 'board': 'CAIE', 'exam': 'IGCSE',
        'year': year, 'session': session, 'season': SESSION_NAMES[session],
        'paper': paper, 'variant': variant, 'paper_code': f'{syllabus}/{pv}',
        'paper_type': ptype, 'is_mcq': ptype.startswith('mcq'),
        'total_marks': total if total else STANDARD_TOTAL.get(ptype),
        'total_marks_source': 'cover' if total else ('standard' if ptype in STANDARD_TOTAL else 'sum'),
        'duration': dur.group(1) if dur else None,
        'pages': len(doc),
        'erratum': [{'page': i + 1, 'text': doc[i].get_text().strip()} for i in range(len(doc)) if is_erratum_page(doc[i])],
    }


def is_erratum_page(page):
    """An erratum notice Cambridge inserted into the paper (it is not a question page)."""
    return 'ERRATUM NOTICE' in page.get_text().upper()


def is_blank_page(page):
    t = page.get_text()
    if not re.search(r'BLANK\s+PAGE', t):
        return False
    top, bottom = page_bounds(page)
    rest = [l for l in visible_lines(page, top, bottom) if not re.search(r'BLANK\s+PAGE', l['text'])
            and not re.match(r'(Every reasonable effort|infringed\.|University of Cambridge|Permission to reproduce)', l['text'])]   # copyright note at the foot of a blank page
    return len(rest) == 0


def maths_doc(doc):
    """A maths paper (syllabus with maths text, 0607): its cleaned PDF path holds /<syllabus>/<year>-<session>/."""
    m = re.search(r'/(\d{4})/\d{4}-[A-Z]{2}/', (doc.name or '').replace('\\', '/'))
    return bool(m) and m.group(1) in subjects.SUBJECTS and subjects.SUBJECTS[m.group(1)]['maths_text']


FORMULA_TITLE = re.compile(r'^(Formula List|List of formulas|Formula list|FORMULA LIST)\s*$')


def is_formula_page(page):
    """Maths: page 2 'Formula List' / 'List of formulas' is no question; kept once per paper as paper.formula_list."""
    if page.number > 3 or not maths_doc(page.parent):
        return False
    top = [l for l in page.get_text().split('\n') if l.strip()][:8]
    return any(FORMULA_TITLE.match(l.strip()) for l in top)


def skipped_page(page):
    return is_blank_page(page) or is_erratum_page(page) or is_formula_page(page)


def boundaries(doc):
    """Walk pages in order and accept labels that continue the numbering sequence."""
    out, q, letter, roman = [], 0, None, None
    maths, pq = maths_doc(doc), None
    for pno in range(1, len(doc)):
        page = doc[pno]
        if skipped_page(page):
            continue
        top, bottom = page_bounds(page)
        # 2014 maths paper 6: part B numbers its questions from 1 again ('B  MODELLING', then '1'): they continue ours
        heads = [l['y0'] for l in visible_lines(page, top - 30, bottom) if maths and q
                 and re.match(r'^(B\s+)?MODELLING\b', l['text'].strip())]
        for t in label_tokens(page, top, bottom):
            if t['kind'] == 'q' and t['val'] == 1 and heads and t['y0'] > min(heads) and q >= 1:
                q, letter, roman, pq = q + 1, None, None, 1
                heads = []
                out.append({'page': pno, 'y': t['y0'], 'path': (q,)})
                continue
            if t['kind'] == 'q' and pq is not None and t['val'] == pq + 1:
                q, letter, roman, pq = q + 1, None, None, t['val']
                out.append({'page': pno, 'y': t['y0'], 'path': (q,)})
                continue
            if t['kind'] == 'q' and t['val'] == q + 1:
                q, letter, roman = q + 1, None, None
                out.append({'page': pno, 'y': t['y0'], 'path': (q,)})
            elif t['kind'] == 'l' and q and t['val'] == (LETTERS[LETTERS.index(letter) + 1] if letter else 'a'):
                letter, roman = t['val'], None
                out.append({'page': pno, 'y': t['y0'], 'path': (q, letter)})
            elif t['kind'] == 'r' and letter and t['val'] == (ROMAN[ROMAN.index(roman) + 1] if roman else 'i'):
                roman = t['val']
                out.append({'page': pno, 'y': t['y0'], 'path': (q, letter, roman)})
    return out


def end_of_paper(page, top, bottom):
    """Stop above the copyright/permissions box on the last page."""
    for l in visible_lines(page, top, bottom):
        if l['text'].startswith('Permission to reproduce') or 'Cambridge Assessment International Education is part of' in l['text']:
            return l['y0'] - 8
    return bottom


def best_cut(page, y, floor):
    """A cut line near y that crosses as little printed ink as possible (rendered pixels, so line
    spacing, tall glyphs and invisible geometry are all handled exactly). Candidates run from just
    above the label (y + PAD_TOP) up to 14 pt above the default cut; ties go to the one nearest y."""
    rows = row_ink(page)
    cands = [y + PAD_TOP - 0.5 - k * 0.5 for k in range(0, 29 + int(2 * PAD_TOP))]
    cands = [c for c in cands if c > floor] or [y]
    def cost(c):
        i = int(round(c * ZOOM))
        return int(rows[max(0, i - 1):i + 2].sum())
    c = min(cands, key=lambda c: (cost(c), abs(c - y)))
    return lift_over_thin_ink(page, c, floor)


def lift_over_thin_ink(page, c, floor):
    """A fraction's numerator and bar ('R = V/I', '1/u') are drawn ABOVE the text top of their own line
    and touch it, so the cleanest cut runs through them and leaves that ink in no piece at all
    (2011 MJ 51 p8, 2012 ON 63 p13). Move the cut up to the first white row above it, so a line keeps
    the ink that hangs over it; a white gap is never crossed, so the part above keeps its own ink.
    Pre-2013 only, so approved years keep their cuts."""
    if int((re.search(r'/((?:19|20)\d\d)-', page.parent.name or '') or [0, '9999'])[1]) >= 2013:
        return c
    rows = row_ink(page)
    i = int(round(c * ZOOM))
    if i <= 0 or i >= len(rows) or not rows[i - 1:i + 1].any():
        return c                                   # the cut is already in white: nothing hangs over
    j = i
    while j > 0 and rows[j - 1] and i - j < int(12 * ZOOM):
        j -= 1
    if rows[j - 1] if j > 0 else True:             # ink all the way up: not a hanging glyph, leave it
        return c
    up = (j - 0.5) / ZOOM
    return up if up > floor else c


def raw_segments(doc, bnds):
    """Strips of pages between consecutive boundaries, continuing across page breaks."""
    segs = []
    pages = [p for p in range(1, len(doc)) if not skipped_page(doc[p])]
    bounds = {p: page_bounds(doc[p]) for p in pages}
    cuts = []
    for i, b in enumerate(bnds):
        p = b['page']
        prev = [x['y'] for x in bnds[:i] if x['page'] == p]
        floor = (max(prev) + 2) if prev else bounds[p][0] - 6
        # a figure/table caption just above a label belongs to the figure above it: never cut above it
        caps = [l for l in visible_lines(doc[p], *bounds[p])
                if CAPTION.match(l['text']) and b['y'] - 24 < l['y0'] < b['y'] - 4 and l['x0'] > 100]
        if caps:                  # cut in the white row between the caption and the label line
            rows = row_ink(doc[p])
            lo, hi = max(c['y0'] for c in caps) + 6, b['y'] + 6
            cands = [lo + 0.5 * k for k in range(int((hi - lo) * 2) + 1)]
            cost = lambda c: int(rows[max(0, int(round(c * ZOOM)) - 1):int(round(c * ZOOM)) + 2].sum())
            cuts.append(min(cands, key=lambda c: (cost(c), -c)) if cands else best_cut(doc[p], b['y'] - PAD_TOP, floor))
            continue
        # a lone mark '[1]' of the part above printed level with the top of this label: cut below it
        mk = [l for l in visible_lines(doc[p], *bounds[p]) if MARK.fullmatch(l['text'].strip()) and l['x0'] > 400
              and b['y'] - 20 < l['y0'] < b['y'] - 1 and l['y1'] > b['y'] - 6]
        if mk:
            from layout import dark_mask
            m = dark_mask(doc[p]); Z = ZOOM
            a0, a1 = int((min(l['x0'] for l in mk) - 2) * Z), int((max(l['x1'] for l in mk) + 2) * Z)
            col = m[:, a0:a1].any(axis=1)
            other = m[:, :a0].any(axis=1) | m[:, a1:].any(axis=1)
            i = int(max(l['y0'] for l in mk) * Z)
            while i < len(col) and not col[i]:
                i += 1                        # top of the mark's ink
            while i < len(col) and col[i]:
                i += 1                        # first row below the mark's ink
            top_i = int((b['y'] - 2) * Z)
            if i < len(col) and i / Z < b['y'] + 10 and not other[min(top_i, i):i].any():
                cuts.append(i / Z)
            else:
                cuts.append(best_cut(doc[p], b['y'] - PAD_TOP, floor))
            continue
        cuts.append(best_cut(doc[p], b['y'] - PAD_TOP, floor))
    for i in range(1, len(bnds)):
        # '(b) (i)' on one line: one cut. A tall glyph on that line (a fraction 'h/x') can push the two
        # cuts apart and leave a sliver piece for '(b)' (a gap of 3 pt or less is dropped anyway)
        if bnds[i - 1]['page'] == bnds[i]['page'] and abs(bnds[i - 1]['y'] - bnds[i]['y']) < 1 \
                and (cuts[i] - cuts[i - 1] > 3 or
                     (cuts[i] > cuts[i - 1] and
                      int((re.search(r'/((?:19|20)\d\d)-', doc.name or '') or [0, '9999'])[1]) < 2013)):
            cuts[i] = cuts[i - 1]        # same line: one cut, the higher one (a 3 pt sliver would be
                                         # dropped and its ink lost - 2012 ON 63 p13 '(d) (i) ... 1/u')
    for i, b in enumerate(bnds):
        nxt = bnds[i + 1] if i + 1 < len(bnds) else None
        start_page = b['page']
        end_page = nxt['page'] if nxt else pages[-1]
        for p in [x for x in pages if start_page <= x <= end_page]:
            top, bottom = bounds[p]
            if not nxt:
                bottom = end_of_paper(doc[p], top, bottom)
            y0 = cuts[i] if p == start_page else top
            y1 = cuts[i + 1] if (nxt and p == end_page) else bottom
            if y1 - y0 > 3:
                segs.append({'path': b['path'], 'page': p, 'y0': y0, 'y1': y1,
                             'continued': p != start_page})
    return segs


def trim(doc, seg):
    """Shrink a strip to the ink it contains; drop strips with no ink."""
    page = doc[seg['page']]
    ext = ink_extent(page, seg['y0'], seg['y1'])        # printed ink only
    if not ext:
        return None
    ink_top, ink_bottom = ext
    seg = dict(seg)
    if seg['continued']:
        seg['y0'] = max(seg['y0'], ink_top - PAD_TOP)
    seg['y1'] = min(seg['y1'], ink_bottom + PAD_BOTTOM)
    seg['bbox'] = [CONTENT_X0, round(seg['y0'], 1), CONTENT_X1, round(seg['y1'], 1)]
    return seg


MULTI_CAPTION = re.compile(r'(?:Fig\.?|Figure|Table)\s*\d+(?:\.\d+)?')


def split_captions(page, lines):
    """Captions of side-by-side figures printed as ONE text line ('Fig. 1.1      Fig. 1.2'): one line per
    caption, each at its own place, so every caption closes its own figure."""
    out = []
    for l in lines:
        caps = MULTI_CAPTION.findall(l['text'])
        if len(caps) < 2 or MULTI_CAPTION.sub('', l['text']).strip():
            out.append(l); continue
        clip = fitz.Rect(l['x0'] - 1, l['y0'] - 1, l['x1'] + 1, l['y1'] + 1)
        parts, used = [], []
        for c in caps:
            hits = [r for r in page.search_for(c, clip=clip) if not any(abs(r.x0 - u.x0) < 1 for u in used)]
            if not hits:
                break
            r = min(hits, key=lambda r: r.x0); used.append(r)
            parts.append(dict(l, x0=r.x0, x1=r.x1, text=c, split=True))
        out += parts if len(parts) == len(caps) else [l]
    return out


def segment_text(doc, seg):
    page = doc[seg['page']]
    top, bottom = page_bounds(page)
    return split_captions(page, [l for l in visible_lines(page, top, bottom) if seg['y0'] - 1 <= (l['y0'] + l['y1']) / 2 <= seg['y1'] + 1])


def strip_label(text, path):
    """Remove leading '4', '(a)', '(ii)' labels from a line."""
    return re.sub(r'^(\d{1,2}\s+)?(\([a-z]{1,4}\)\s*){0,2}', '', text).strip()


def answer_space(lines, seg):
    dotted = [l for l in lines if DOTS.search(l['text'])]
    prompt = [l for l in lines if not DOTS.search(l['text']) and not MARK.fullmatch(l['text'])]
    gaps, prev = [], seg['y0']
    for l in sorted(lines, key=lambda d: d['y0']):
        gaps.append(l['y0'] - prev); prev = max(prev, l['y1'])
    answer_line = next((l['text'] for l in dotted if '=' in l['text']), None)
    kind = 'none'
    if answer_line:
        kind = 'answer_line'
    elif dotted:
        kind = 'lines'
    return {
        'kind': kind,
        'dotted_lines': len(dotted),
        'answer_line': re.sub(DOTS, '……', answer_line) if answer_line else None,
        'working_gap_pt': round(max(gaps), 1) if gaps else 0,
        'height_pt': round(seg['y1'] - seg['y0'], 1),
    }


def _beside_part(l, x0, x1, rules):
    """A text line that runs THROUGH a figure printed beside the question ('basket of' + '(b) Which form of energy ...'
    read as one line, 2012 MJ 22 q4, round 26): only its part right of the figure is question text, the left part is a
    label of the figure and must not be kept out of the crop."""
    if l['x0'] < x1 - 2 and l['x1'] > x1 + 20 and any(r.y0 < l['y1'] and l['y0'] < r.y1 and r.x0 >= x0 - 1 and r.x1 <= x1 + 1
                                                     for r in rules):
        return fitz.Rect(x1 + 2, l['y0'], l['x1'], l['y1'])
    return fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])



def _label_like(t, tb, box, text):
    """A text line that is part of a diagram: short, or a longer label touching the drawing ('gets up before 7 am');
    never a piece of a sentence printed on the same baseline, an answer line, a mark or a part label."""
    s = t['text'].strip()
    if DOTS.search(t['text']) or MARK.fullmatch(s) or re.match(r'^\(?[a-z]\)|^\([ivx]+\)', s):
        return False
    if re.fullmatch(r'NOT\s+TO|SCALE|NOT TO SCALE', s):
        return True
    if _sentence(t, text):
        return False                                 # a piece of a sentence ('Sketch the model for', round 27)
    if not (len(s) <= 22 or (len(s) <= 40 and not s.endswith('.') and tb.intersects(box + (-4, -2, 4, 2)))
            or re.fullmatch(r'(Diagram|Pattern|Shape|Figure)\s*\d+(\s+(Diagram|Pattern|Shape|Figure)\s*\d+)*', s)):
        return False
    return True


def _sentence(t, text):
    """True when the words on t's baseline read as a sentence (all pieces of that baseline together > 26 characters
    with at least 4 words, or ending with a full stop after a word), not as labels."""
    same = [o for o in text if abs(o['y0'] - t['y0']) < 2]
    whole = ' '.join(o['text'].strip() for o in sorted(same, key=lambda o: o['x0']))
    words = re.findall(r'[A-Za-z]{2,}', whole)
    if re.fullmatch(r'((Diagram|Pattern|Shape|Figure|Row|Column)\s*\d+\W*\s*)+', whole.strip()):
        return False
    if re.match(r'^\(?[a-z]\)|^\((i|ii|iii|iv|v|vi)\)|^\d{1,2}\s+\(?[a-z]\)', whole.strip()):
        return True                                  # the line of a part label: question text
    return (len(whole) > 26 and len(words) >= 4) or bool(re.search(r'\S{2,}[.?]\s*$', whole.strip())) and len(whole) > 6


def _grow_light(page, r, limit, exclude, Z=2.0):
    """Grow a crop while any non-white ink (light grey grid lines and dot grids too, which the dark mask ignores)
    crosses its edges; sentences never pull it."""
    import numpy as np
    pix = page.get_pixmap(matrix=fitz.Matrix(Z, Z), colorspace=fitz.csGRAY)
    m = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width) < 253
    m = m.copy()
    for e in exclude:
        m[max(0, int((e.y0 - 1) * Z)):int((e.y1 + 1) * Z) + 1, max(0, int((e.x0 - 1) * Z)):int((e.x1 + 1) * Z) + 1] = False
    H, W = m.shape
    r = fitz.Rect(r)
    for _ in range(300):
        x0, y0, x1, y1 = int(r.x0 * Z), int(r.y0 * Z), int(r.x1 * Z), int(r.y1 * Z)
        moved = False
        if r.x0 - 1 > limit.x0 and x0 - 2 >= 0 and m[y0:y1, x0 - 2].any():
            r.x0 -= 1; moved = True
        if r.x1 + 1 < limit.x1 and x1 + 2 < W and m[y0:y1, x1 + 2].any():
            r.x1 += 1; moved = True
        if r.y0 - 1 > limit.y0 and y0 - 2 >= 0 and m[y0 - 2, x0:x1].any():
            r.y0 -= 1; moved = True
        if r.y1 + 1 < limit.y1 and y1 + 2 < H and m[y1 + 2, x0:x1].any():
            r.y1 += 1; moved = True
        if not moved:
            break
    return r


def diagrams(doc, seg, lines, captioned):
    """Maths: drawings with no caption (a triangle 'NOT TO SCALE', axes, a grid to draw on, a stem-and-leaf box ...) inside
    a segment -> figure crops {'caption': None, 'page', 'bbox'}. Not figures: answer lines and dots, fraction bars and
    root signs inside a text line, ruled tables of text (kept as text + rules, store decision 4), the page furniture."""
    page = doc[seg['page']]
    top, bottom = page_bounds(page)
    y0s, y1s = max(seg['y0'], top), min(seg['y1'], bottom)
    taken = [fitz.Rect(f['bbox']) for f in captioned]
    text = [l for l in lines]
    tboxes = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in text]
    items = []
    for d in page.get_drawings():
        r = d['rect']
        if r.y1 < y0s - 1 or r.y0 > y1s + 1 or r.x1 < CONTENT_X0 + 2 or r.x0 > CONTENT_X1 - 2:
            continue
        if r.width > 0.95 * page.rect.width and r.height > 0.95 * page.rect.height:
            continue
        if d.get('fill') in ((1.0, 1.0, 1.0), (1, 1, 1)) and not d.get('color'):
            continue
        if r.height < 1.6 and r.width < 60 and any(t.y0 - 3 <= r.y0 <= t.y1 + 3 and t.x0 - 4 <= r.x0 and r.x1 <= t.x1 + 4 for t in tboxes):
            continue                                       # a fraction bar / overline inside a text line
        aligned = all((it[0] == 're') or (it[0] == 'l' and (abs(it[1].x - it[2].x) < 0.6 or abs(it[1].y - it[2].y) < 0.6))
                      for it in d['items'])
        rr = fitz.Rect(r); rr.aligned = aligned
        items.append(rr)
    for im in page.get_image_info():
        r = fitz.Rect(im['bbox'])
        if y0s - 1 <= r.y0 and r.y1 <= y1s + 1 and r.width > 8 and r.height > 8 and CONTENT_X0 - 2 <= r.x0:
            items.append(r)
    items = [r for r in items if not any(t.intersects(r) for t in taken)]
    # clusters: drawings closer than 10 pt are one diagram
    cl = []
    for r in sorted(items, key=lambda r: (r.y0, r.x0)):
        g = fitz.Rect(r) + (-10, -10, 10, 10)
        hit = [c for c in cl if c['g'].intersects(g)]
        if hit:
            base = hit[0]
            for c in hit[1:]:
                base['r'] |= c['r']; base['n'] += c['n']; base['rs'] += c['rs']; cl.remove(c)
            base['r'] |= r; base['n'] += 1; base['rs'].append(r)
            base['g'] = base['r'] + (-10, -10, 10, 10)
        else:
            cl.append({'r': fitz.Rect(r), 'g': g, 'n': 1, 'rs': [r]})
    out = []
    for c in cl:
        r = c['r']
        if r.width < 25 or r.height < 20:
            continue                                       # a root sign, a tick box, a short rule
        straight = [x for x in c['rs'] if x.width < 1.6 or x.height < 1.6]
        horiz = [x for x in straight if x.height < 1.6]
        if len(straight) == len(c['rs']) and len(horiz) == len(c['rs']):
            continue                                       # only horizontal lines: answer lines
        inside = [t for t in text if fitz.Rect(t['x0'], t['y0'], t['x1'], t['y1']).intersects(r)]
        if all(getattr(x, 'aligned', False) for x in c['rs']) and len(inside) >= 2 and \
                len({round(x.x0) for x in c['rs'] if x.width < 1.6}) <= 25 and len({round(x.y0) for x in c['rs'] if x.height < 1.6}) <= 25 and \
                all(len(t['text']) < 60 for t in inside):
            vert = [x for x in c['rs'] if x.width < 1.6 and x.height > 5]
            hz = [x for x in c['rs'] if x.height < 1.6 and x.width > 5]
            fills = [x for x in c['rs'] if x.width >= 1.6 and x.height >= 1.6]
            import collections as _c
            vc, hc = _c.Counter(), _c.Counter()
            for x in vert:
                vc[round(x.x0)] += x.height
            for x in hz:
                hc[round(x.y0)] += x.width
            full_v = sum(1 for h_ in vc.values() if h_ >= 0.8 * r.height)
            full_h = sum(1 for w_ in hc.values() if w_ >= 0.8 * r.width)
            if full_v >= 3 and full_h >= 2:
                continue                                   # a ruled table of text (column rules top to bottom): stays text + rules
        # labels touching the drawing (A, B, 68°, x, y, axis numbers) belong to it; sentences do not
        box = fitz.Rect(r)
        for _ in range(3):
            for t in text:
                tb = fitz.Rect(t['x0'], t['y0'], t['x1'], t['y1'])
                if re.search(r'NOT TO SCALE|^NOT\s+TO$|^SCALE$', t['text'].strip()) and tb.intersects(box + (-200, -30, 200, 30)):
                    box |= tb
                elif tb.intersects(box + (-14, -12, 14, 12)) and _label_like(t, tb, box, text):
                    box |= tb
        dl = [(''.join(sp['text'] for sp in l_['spans']).strip(), fitz.Rect(l_['bbox']))
              for b_ in page.get_text('dict')['blocks'] for l_ in b_.get('lines', [])]
        for _ in range(2):                              # axis titles printed sideways, tick labels and point names a little further out
            for lt, lb in dl:
                if lt and lb.intersects(box + (-26, -16, 26, 16)) and not lb.intersects(box) and len(lt) <= 22 and y0s - 1 <= lb.y0 \
                        and lb.y1 <= y1s + 1 and not DOTS.search(lt) and not MARK.fullmatch(lt) and not re.match(r'^\(?[a-z]\)|^\([ivx]+\)', lt) \
                        and not any(abs(ob.y0 - lb.y0) < 2 and len(ot) > 22 for ot, ob in dl):
                    box |= lb
        if any((box & tk).get_area() > 0.3 * box.get_area() for tk in taken):
            continue
        prose = [fitz.Rect(t['x0'], t['y0'], t['x1'], t['y1']) for t in text
                 if len(t['text'].strip()) > 22 or DOTS.search(t['text']) or _sentence(t, text)]
        box = grow_to_ink(page, box, fitz.Rect(CONTENT_X0 - 5, y0s, CONTENT_X1 + 5, y1s), max_grow=120, exclude=prose)
        box = _grow_light(page, box, fitz.Rect(CONTENT_X0 - 5, y0s, CONTENT_X1 + 5, y1s), prose)   # light grey grids too
        grown = fitz.Rect(box)
        for _ in range(2):                              # labels next to what the growing found (axis numbers beside an axis)
            for t in text:
                tb = fitz.Rect(t['x0'], t['y0'], t['x1'], t['y1'])
                if tb.intersects(box + (-14, -12, 14, 12)) and _label_like(t, tb, box, text):
                    box |= tb
            for lt, lb in dl:
                if lt and lb.intersects(box + (-26, -16, 26, 16)) and len(lt) <= 22 and y0s - 1 <= lb.y0 and lb.y1 <= y1s + 1 \
                        and not DOTS.search(lt) and not MARK.fullmatch(lt) and not re.match(r'^\(?[a-z]\)|^\([ivx]+\)', lt) \
                        and not any(abs(ob.y0 - lb.y0) < 2 and len(ot) > 22 for ot, ob in dl):
                    box |= lb
        if box != grown:
            box = _grow_light(page, box, fitz.Rect(CONTENT_X0 - 5, y0s, CONTENT_X1 + 5, y1s), prose)
        for t in text:                                  # a sentence touching the crop's top or bottom edge stays outside it
            tb = fitz.Rect(t['x0'], t['y0'], t['x1'], t['y1'])
            if not tb.intersects(box) or not (_sentence(t, text) or len(t['text'].strip()) > 22) or DOTS.search(t['text']):
                continue
            if tb.y0 <= box.y0 + 14 and tb.y1 < box.y0 + 0.5 * box.height:
                box.y0 = tb.y1 + 0.5
            elif tb.y1 >= box.y1 - 14 and tb.y0 > box.y0 + 0.5 * box.height:
                box.y1 = tb.y0 - 0.5
        for o in [o for o in out if fitz.Rect(o['bbox']).intersects(box)]:   # crops that overlap after taking labels: one
            box |= fitz.Rect(o['bbox']) + (3, 3, -3, -3)
            out.remove(o)
        out.append({'caption': None, 'page': seg['page'],
                    'bbox': [round(box.x0 - 4, 1), round(max(box.y0 - 1, seg['y0']), 1), round(box.x1 + 6, 1), round(min(box.y1 + 1.5, seg['y1']), 1)]})
    merged = True                                    # crops that touch or overlap are one diagram (round 27: '2 images')
    while merged:
        merged = False
        for a in out:
            for b in out:
                if a is not b and (fitz.Rect(a['bbox']) + (-3, -3, 3, 3)).intersects(fitz.Rect(b['bbox'])):
                    a['bbox'] = list(fitz.Rect(a['bbox']) | fitz.Rect(b['bbox'])); out.remove(b); merged = True
                    break
            if merged:
                break
    return out


def find_figures(doc, seg, lines):
    """Captioned figures (Fig. 1.1 / Table 2.1) inside a segment: band from the prose above to the caption."""
    page = doc[seg['page']]
    top, bottom = page_bounds(page)
    figs = []
    from layout import dark_mask
    mk = dark_mask(page)
    def inked(l):        # invisible text (an OCR layer: 'Fig. 12' in Courier, 2004 ON 02 q12) prints nothing and is no caption
        return bool(mk[int(l['y0'] * ZOOM):int(l['y1'] * ZOOM) + 1, int(l['x0'] * ZOOM):int(l['x1'] * ZOOM) + 1].any())
    caps = [l for l in lines if CAPTION.match(l['text']) and inked(l)]
    marks_text = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines
                  if MARK.fullmatch(l['text'].strip()) or TOTAL.fullmatch(l['text'].strip()) or DOTS.search(l['text'])]
    drawings = [r for r in ink_boxes(page, top, bottom) if seg['y0'] <= r.y0 and r.y1 <= seg['y1'] + 1
                and not any(abs(r.x0 - m.x0) < 1 and abs(r.y0 - m.y0) < 1 and abs(r.x1 - m.x1) < 1 for m in marks_text)]
    # side-by-side captions printed as one text line were split by segment_text: split their ink box too
    split = []
    for r in drawings:
        parts = [fitz.Rect(c['x0'], c['y0'], c['x1'], c['y1']) for c in caps
                 if abs(c['y0'] - r.y0) < 1.5 and r.x0 - 1 <= c['x0'] and c['x1'] <= r.x1 + 1]
        split += parts if len(parts) >= 2 else [r]
    drawings = split
    long_lines = [l for l in lines if len(l['text']) >= 25]
    para_x0 = [l['x0'] for l in lines if len(l['text']) >= 45]       # left edges of real paragraphs
    text_boxes = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines]
    frames = [r for r in drawings if r.width < 0.9 * page.rect.width and r.height > 18
              and not any(abs(r.x0 - t.x0) < 1 and abs(r.y0 - t.y0) < 1 for t in text_boxes)]
    vrules = [r for r in drawings if r.width <= 1.5 and r.height > 5]
    def in_grid(l):               # a cell of a ruled table: vertical rules on both sides at that height
        ym = (l['y0'] + l['y1']) / 2
        span = [r for r in vrules if r.y0 - 1 <= ym <= r.y1 + 1]
        return any(r.x0 <= l['x0'] + 1 for r in span) and any(r.x0 >= l['x1'] - 1 for r in span)
    def prose_like(l):            # a sentence of the question, not an axis title or label inside a figure
        if in_grid(l):
            return False
        if DOTS.search(l['text']):
            return False          # an answer line ('Vs = .........') can sit beside a figure
        lr = fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])
        if any(f.contains(lr) for f in frames):
            return False          # text printed inside a drawn box (a notice, a label) is part of the figure
        words = len(re.findall(r'[A-Za-z]{2,}', l['text']))
        return len(l['text']) >= 45 or (len(l['text']) >= 25 and words >= 4 and any(abs(l['x0'] - x) < 2.5 for x in para_x0))
    bullets = [l for l in lines if l['text'].lstrip().startswith('•')
               and not any(f.contains(fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])) for f in frames)]
    def bullet_item(l):           # '• metre ruler': a list item of the question, never part of a figure
        return l in bullets or any(abs(l['y0'] - b['y0']) < 2.5 and 0 < l['x0'] - b['x0'] < 40 for b in bullets)
    caps = [c for c in caps if not in_grid(c)]       # 'Fig. 5.2' written in a table cell is a reference, not a caption
    for cap in caps:
        is_table = cap['text'].startswith('Table')
        prose_above = [l for l in lines if l['y1'] <= cap['y0'] and not DOTS.search(l['text'])
                       and not re.fullmatch(r'[\s\d.,+—–−-]*(o?C|°C)?', l['text'].strip())    # a scale '−10 0 10 … 110 °C' is part of the figure
                       and (len(re.sub(r'\W', '', l['text'])) > 2 or re.match(r'\s*(\(?[a-z]+\)|\d{1,2})\s', l['text'] + ' '))   # 'C      D' labels (2007 MJ 05 Fig 3.1)
                       and (prose_like(l) or bullet_item(l) or (re.match(r'^(\d{1,2}|\([a-z]+\))\s', l['text']) and l['x0'] < 110)
                                                                    or (re.fullmatch(r'\([a-z]+\)', l['text'].strip()) and l['x0'] < 110)
                                                                    or re.fullmatch(r'Method \d', l['text'].strip())
                                                                    or (len(l['text'].split()) >= 4 and l['text'].rstrip().endswith('.')
                                                                        and any(abs(o['y0'] - l['y0']) < 3 and re.fullmatch(r'\[\d{1,2}\]', o['text'].strip()) for o in lines))   # 'Draw the best curve for these points.   [2]'
                                                                    or (l['x0'] <= 76 and l['text'].rstrip().endswith('.'))
                                                                    or (l['text'].rstrip().endswith(('.', ':')) and l['x0'] < 130 and any(abs(l['x0'] - o['x0']) < 2 for o in long_lines if o is not l)))]
        for l in sorted(lines, key=lambda l: l['y0']):    # last line of a sentence ('Fig. 2.2.' after a long line)
            if l['y1'] <= cap['y0'] and l not in prose_above and re.search(r'[a-z]', l['text']) and \
                    l['text'].rstrip()[-1:] in '.:?' and any(0 < l['y0'] - p['y0'] < 1.6 * (l['y1'] - l['y0'])
                                                             and p['x0'] - 3 <= l['x0'] <= p['x0'] + 70 for p in prose_above):
                prose_above.append(l)
        for l in lines:   # the denominator of an inline fraction at the end of a sentence ('ρ = m/VA'), hanging below it
            if l['y1'] <= cap['y0'] and l not in prose_above and 0 < len(l['text'].replace(' ', '')) <= 4 and \
                    re.search(r'[A-Za-z0-9]', l['text']) and any(
                        p['y0'] < l['y0'] < p['y1'] < l['y1'] and len(p['text']) >= 45
                        and p['x1'] - 15 <= l['x0'] <= p['x1'] + 2 and l['x1'] <= p['x1'] + 8 for p in prose_above):
                prose_above.append(l)
        rules = [r for r in drawings if not any(abs(r.x0 - t.x0) < 1 and abs(r.y0 - t.y0) < 1 for t in text_boxes)]
        grid_below = [r for r in rules if cap['y1'] - 1 <= r.y0 <= cap['y1'] + 18]   # 2010 MJ 52: table 15 pt under its caption
        grid_above = [r for r in rules if cap['y0'] - 30 <= r.y1 <= cap['y0'] + 1]
        if is_table and (grid_below or not grid_above):
            # table caption sits above the table (the usual case)
            prose_below = [l for l in lines if l['y0'] > cap['y1'] + 4 and len(l['text']) > 40
                           and not DOTS.search(l['text']) and not in_grid(l)]
            band = (cap['y0'] - 2, (min(l['y0'] for l in prose_below) - 4) if prose_below else seg['y1'])
        else:          # figure caption, or a table captioned underneath (table drawn just above, nothing below)
            band = ((max(l['y1'] for l in prose_above) + 2) if prose_above else seg['y0'], cap['y1'] + 2)
            # figures stacked with no sentence between them: each caption closes its own figure, so this
            # figure starts below the previous 'Fig.' caption (one caption = one figure, however many drawings)
            prev = [c['y1'] for c in caps if c is not cap and c['y1'] <= cap['y0'] and not c['text'].startswith('Table')]
            if prev and max(prev) + 2 > band[0]:
                band = (max(prev) + 2, band[1])
        # figures side by side, each with its own caption on the same row: one caption = one figure, so
        # split the row halfway between neighbouring captions (one caption under several drawings = one figure)
        cx = (cap['x0'] + cap['x1']) / 2
        row = sorted((c['x0'] + c['x1']) / 2 for c in caps if abs(c['y0'] - cap['y0']) < 4)
        k = row.index(cx) if cx in row else 0
        def gap(a, b):
            """Where to split two side-by-side figures whose captions are centred at a and b: among the empty
            columns between them, the one that leaves each caption best centred under its own drawing."""
            from layout import dark_mask
            mk = dark_mask(page)
            ya, yb = int(max(0, band[0]) * ZOOM), int(band[1] * ZOOM)
            colsum = mk[ya:yb].sum(axis=0)
            lo, hi = int(a * ZOOM), int(b * ZOOM)
            cols = colsum[lo:hi]
            if not len(cols):
                return (a + b) / 2
            m = cols.min()
            # never split inside a printed word: the gaps between letters of a label ('clamp') are empty
            # columns too, and a split there hands the label to the wrong figure
            words = [(l['x0'] * ZOOM, l['x1'] * ZOOM) for l in lines
                     if l['y1'] >= band[0] and l['y0'] <= band[1] and l is not cap and not CAPTION.match(l['text'])]
            def in_word(x):
                return any(w0 < x < w1 for w0, w1 in words)
            runs, start = [], None
            for i, v in enumerate(list(cols) + [m + 1]):
                if v == m and start is None:
                    start = i
                elif v != m and start is not None:
                    runs.append((start + i - 1) / 2); start = None
            runs = [r for r in runs if not in_word(lo + r)] or runs
            inked = [i for i, v in enumerate(colsum) if v]
            def score(c):
                x = lo + c
                left = [i for i in inked if int(CONTENT_X0 * ZOOM) <= i < x]
                right = [i for i in inked if x <= i < int(CONTENT_X1 * ZOOM)]
                if not left or not right:
                    return 1e9
                # only the ink between the neighbouring captions' outer limits counts (with a third figure
                # beside them, halfway to its caption: its ink must not pull this figure's centre)
                ia, ib = row.index(a), row.index(b)
                la = (row[ia - 1] + a) / 2 if ia > 0 else 2 * a - b
                rb = (b + row[ib + 1]) / 2 if ib + 1 < len(row) else 2 * b - a
                left_in = [i for i in left if i >= int(la * ZOOM)] or left
                right_in = [i for i in right if i <= int(rb * ZOOM)] or right
                lc = (left_in[0] + left_in[-1]) / 2
                rc = (right_in[0] + right_in[-1]) / 2
                return abs(lc - a * ZOOM) + abs(rc - b * ZOOM)
            best = min(runs, key=score)
            return (lo + best) / ZOOM
        xa = gap(row[k - 1], cx) if k > 0 else 0
        xb = gap(cx, row[k + 1]) if k + 1 < len(row) else page.rect.width
        strip = fitz.Rect(0, band[0] - 1, page.rect.width, band[1] + 1)
        grown = [fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1) for r in drawings]   # lines have zero height
        # a drawing belongs to the caption whose column holds its centre and is kept whole (side-by-side
        # figures may overlap a little; cutting a drawing in two would be worse)
        inside = [tight_ink(page, g & strip, marks_text) for g in grown
                  if g.y1 >= strip.y0 and g.y0 <= strip.y1 and not (g & strip).is_empty and xa <= (g.x0 + g.x1) / 2 <= xb]
        inside = [r for r in inside if r is not None]       # what is printed, inside the band
        if not inside:
            continue
        if xa > 0 or xb < page.rect.width:
            # side by side: also take drawings joined to this figure (a leader line reaching across the split)
            # and the labels at the end of those lines ('measuring cylinder' printed beside the next figure)
            for _ in range(3):
                more = [tight_ink(page, g & strip, marks_text) for g in grown
                        if not (g & strip).is_empty and not (xa <= (g.x0 + g.x1) / 2 <= xb)
                        and any((g + (-.5, -.5, .5, .5)).intersects(r) for r in inside)]
                more = [r for r in more if r is not None and not any(abs(r.x0 - o.x0) < .1 and abs(r.y0 - o.y0) < .1 for o in inside)]
                if not more:
                    break
                inside += more
            for l in lines:
                lr = fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1'])
                if band[0] <= lr.y0 and lr.y1 <= band[1] + 1 and l is not cap and not CAPTION.match(l['text']) \
                        and not (xa <= (lr.x0 + lr.x1) / 2 <= xb) and any((lr + (-3, -3, 3, 3)).intersects(r) and min(r.width, r.height) < 3 for r in inside):
                    inside.append(lr)
        x0 = min(r.x0 for r in inside); x1 = max(r.x1 for r in inside)
        y0 = min(r.y0 for r in inside); y1 = max(r.y1 for r in inside)
        top_lim = max(seg['y0'], band[0] - 1)
        mg = 80
        if prose_above and int((re.search(r'/((?:19|20)\d\d)-', doc.name or '') or [0, '9999'])[1]) < 2013 and \
                not any(l['x0'] < x1 - 2 and l['x1'] > x0 + 2 for l in prose_above if l['y1'] > band[0] - 30):
            top_lim = seg['y0']             # pre-2013: every sentence above sits BESIDE the figure (2008 MJ 02 Fig 4.1, text in a column;
                                            # 2012 MJ 22/23 q4 the cliff, round 26 - the crop had lost its top half)
            mg = 400                        # a tall figure beside a column of text: grow as far as its ink goes
        elif prose_above and int((re.search(r'/((?:19|20)\d\d)-', doc.name or '') or [0, '9999'])[1]) < 2009:     # pre-2009: a figure printed close under its sentence (thermometer
            top_lim = max(seg['y0'], max(l['y1'] for l in prose_above) - 2.5)   # 2006 MJ 06 q4) may reach into the line's descent
        if prose_above:      # the sentence that closes the band sits BESIDE the figure (bottles next to the question text): its top may rise past it
            last = max(prose_above, key=lambda l: l['y1'])
            if last['x1'] < x0 - 2 or last['x0'] > x1 + 2:
                top_lim = seg['y0']
        g = grow_to_ink(page, fitz.Rect(x0, y0, x1, y1), fitz.Rect(max(CONTENT_X0, min(xa, x0)), top_lim, min(CONTENT_X1, max(xb, x1)), min(seg['y1'], band[1] + 1)),
                        exclude=[_beside_part(l, x0, x1, rules) if mg > 80 else fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in prose_above]
                        + ([fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines if re.fullmatch(r'\d{1,2}', l['text'].strip()) and l['x0'] < 60]
                           if mg > 80 else []), max_grow=mg)    # the question number beside a tall figure (2008 MJ 02 q4) is not ink of it
        x0, y0, x1, y1 = g.x0, g.y0, g.x1, g.y1
        if mg > 80:                     # beside a column of text: a label the crop's edge runs through is taken whole
            for _ in range(2):          # ('basket of' half outside, 2012 MJ 22 q4, round 26 - its line was read together
                for r in drawings:      # with the question text beside the figure, so it was never inside the band)
                    if r.x0 < x1 and r.x1 > x0 and (r.x0 < x0 or r.x1 > x1) and r.y0 >= y0 - 1 and r.y1 <= y1 + 1 \
                            and r.x1 - r.x0 < 120 and r.x0 >= CONTENT_X0:
                        x0, x1 = min(x0, r.x0), max(x1, r.x1)
        for l in lines:                 # answer lines printed inside the figure ('nebula which contains .......')
            if DOTS.search(l['text']) and l['y0'] >= y0 - 2 and l['y1'] <= y1 + 2 and l['x0'] < x1 and l['x1'] > x0:
                x0, x1 = min(x0, l['x0']), max(x1, l['x1'])
        top_ = max(y0 - 3, seg['y0'])
        for l in lines:                 # a question number at the top-left corner of the crop (2008 MJ 02 Fig 4.1): stays out
            if re.fullmatch(r'\d{1,2}', l['text'].strip()) and l['x0'] < 60 and l['x1'] > x0 - 3 and l['y0'] < top_ < l['y1'] and l['y1'] <= y0 + 2:
                top_ = l['y1'] + 0.3
        figs.append({'caption': cap['text'], 'page': seg['page'],
                     'bbox': [round(x0 - 3, 1), round(top_, 1), round(x1 + 3, 1),
                              round(min(y1 + 3, seg['y1']), 1)]})    # a crop never reaches past its piece
        if cap.get('split'):
            figs[-1]['_row'] = round(cap['y0'])
    # captions split from one printed line: when the drawings are joined (a bench line under both, labels
    # printed between them) the crops run into each other; then each caption gets the whole row of figures
    # rather than a crop that cuts the neighbour (or a label) in two
    rows = {}
    for f in figs:
        if '_row' in f:
            rows.setdefault(f.pop('_row'), []).append(f)
    for row in rows.values():
        row.sort(key=lambda f: f['bbox'][0])
        if any(p['bbox'][2] - q['bbox'][0] > 12 for p, q in zip(row, row[1:])):
            u = [min(f['bbox'][0] for f in row), min(f['bbox'][1] for f in row),
                 max(f['bbox'][2] for f in row), max(f['bbox'][3] for f in row)]
            for f in row:
                f['bbox'] = list(u)
    return figs


def mcq_options(lines):
    """Options A-D: the last A<B<C<D run of bold letters; text is whatever follows on the same row."""
    cands = [l for l in lines if re.fullmatch(r'[ABCD]', l['text']) or
             (re.match(r'^[ABCD]\s', l['text']) and 64 <= l['x0'] <= 82)]
    cands.sort(key=lambda d: (round(d['y0']), d['x0']))
    chosen, want, limit = {}, 'DCBA', len(cands)
    for letter in want:
        idx = max((i for i in range(limit) if cands[i]['text'][0] == letter), default=None)
        if idx is None:
            break
        chosen[letter], limit = cands[idx], idx
    labels = list(chosen.values())
    opts = {}
    for letter, lab in chosen.items():
        if len(lab['text']) > 1:
            opts[letter] = lab['text'][1:].strip(); continue
        row_next = [o['x0'] for o in labels if abs(o['y0'] - lab['y0']) < 3 and o['x0'] > lab['x0']]
        limit_x = min(row_next) if row_next else 1e9
        same = [l for l in lines if abs(l['y0'] - lab['y0']) < 3.5 and lab['x1'] < l['x0'] < limit_x and l is not lab]
        opts[letter] = ' '.join(l['text'] for l in sorted(same, key=lambda d: d['x0'])).strip()
    return [{'label': k, 'text': opts[k]} for k in 'ABCD' if k in opts]


def node_for(tree, path):
    node = tree
    for depth in range(1, len(path)):
        label = path[depth]
        kids = node.setdefault('parts', [])
        found = next((k for k in kids if k['label'] == label), None)
        if not found:
            found = {'label': label, 'segments': [], 'text': '', 'marks': 0}
            kids.append(found)
        node = found
    return node


def extract(pdf_path, syllabus, year, session, pv):
    doc = fitz.open(pdf_path)
    meta = paper_meta(doc, syllabus, year, session, pv)
    bnds = boundaries(doc)
    segs = [s for s in (trim(doc, s) for s in raw_segments(doc, bnds)) if s]
    if subjects.subject(syllabus)['maths_text']:
        segs = maths_paper_parts(doc, bnds, segs, meta)
    sid = f"{syllabus}_{year}{session}_{pv}"
    questions = {}
    for s in segs:
        qn = s['path'][0]
        q = questions.setdefault(qn, {'id': f'{sid}_q{qn:02d}', 'number': qn, 'segments': [], 'text': '',
                                     'marks': 0, 'figures': [], 'review': {'reasons': []}})
        node = node_for(q, s['path'])
        lines = segment_text(doc, s)
        body = '\n'.join(strip_label(l['text'], s['path']) if i == 0 and not s['continued'] else l['text']
                         for i, l in enumerate(lines) if not CAPTION.match(l['text']))
        marks = sum(int(m) for l in lines for m in MARK.findall(l['text']) if not TOTAL.search(l['text']))
        total = [int(m) for l in lines for m in TOTAL.findall(l['text'])]
        if total:
            q['total_marks'] = total[-1]
        node['text'] = (node['text'] + '\n' + body).strip()
        node['marks'] += marks
        seg_rec = {'page': s['page'] + 1, 'bbox': s['bbox'], 'continued': s['continued'],
                   'answer_space': answer_space(lines, s)}
        node['segments'].append(seg_rec)
        found = find_figures(doc, s, lines)
        if subjects.subject(syllabus)['maths_text']:      # maths diagrams carry no 'Fig.' caption (ERROR_PATTERNS 68)
            for k, f in enumerate(diagrams(doc, s, lines, found), 1):
                near = [g for g in q['figures'] if g.get('kind') == 'diagram' and g['page'] == f['page'] + 1
                        and (fitz.Rect(g['bbox']) + (-3, -3, 3, 3)).intersects(fitz.Rect(f['bbox']))]
                if near:                                   # one drawing cut by a part boundary: one picture (round 27)
                    near[0]['bbox'] = [round(v, 1) for v in fitz.Rect(near[0]['bbox']) | fitz.Rect(f['bbox'])]
                    continue
                label = ''.join(str(x) for x in s['path'][1:])
                n_ = sum(1 for g in q['figures'] if g.get('kind') == 'diagram') + 1
                f.update(id=f"{q['id']}{label}_diagram{n_}", page=f['page'] + 1, alt='', kind='diagram',
                         part='(' + ')('.join(str(x) for x in s['path'][1:]) + ')' if len(s['path']) > 1 else '')
                q['figures'].append(f)
        for f in found:
            num = ''.join(re.match(r'^(?:Fig\.?|Figure|Table)\s*([\d.]+)([a-d]?)', f['caption']).groups()).replace('.', '-')   # 'Fig. 2.1a' -> 2-1a
            kind = 'table' if f['caption'].startswith('Table') else 'fig'
            label = ''.join(str(x) for x in s['path'][1:])
            f['id'] = f"{q['id']}{label}_{kind}{num}"
            f['page'] += 1
            f['part'] = '(' + ')('.join(str(x) for x in s['path'][1:]) + ')' if len(s['path']) > 1 else ''
            f['alt'] = ''
            q['figures'].append(f)
    out = []
    for qn in sorted(questions):
        q = questions[qn]
        if meta['is_mcq']:
            q['type'] = 'mcq'
            q['marks'] = 1
            q['options'] = mcq_options(segment_text_all(doc, q))
            if len(q['options']) < 4:
                q['review']['reasons'].append('options not found as text (likely in a table or diagrams)')
            q['has_diagram'] = bool(q['figures']) or has_drawings(doc, q)
        else:
            q['type'] = 'structured'
            if int(year) < 2013:
                block_marks(q)
            q['marks'] = sum_marks(q)
            if q['marks'] == 0 and not q.get('parts') and q.get('total_marks'):
                q['marks'] = q['total_marks']        # single-part question marked only by '[Total: n]'
            if 'total_marks' in q and q['total_marks'] != q['marks']:
                if q['id'] not in TOTAL_SLIPS:
                    q['review']['reasons'].append(f"marks found {q['marks']} but [Total: {q['total_marks']}]")
        if len(q['segments']) == 0 and not q.get('parts'):
            q['review']['reasons'].append('no content found')
        q['review']['status'] = 'flagged' if q['review']['reasons'] else 'auto'
        out.append(q)
    return meta, out


SECTION_HEAD = re.compile(r'^(?:Section\s+([AB])|([AB]))$')


def maths_paper_parts(doc, bnds, segs, meta):
    """Maths only (ERROR_PATTERNS 65-66). Text that belongs to no question:
    - the formula list (page 2) -> meta['formula_list'] = {page, bbox} (stored once per paper, exact print + LaTeX);
    - the introduction of an investigation / modelling section (page 2 before Q1; 'B  MODELLING' or 'Section B'
      heading before the first question of part B) -> meta['intros'] = [{section, before, segments}].
    Questions keep only their own text; each question of a section points to its intro (store)."""
    for p in range(1, min(4, len(doc))):
        if is_formula_page(doc[p]):
            top, bottom = page_bounds(doc[p])
            t = trim(doc, {'path': ('formula',), 'page': p, 'y0': top - 6, 'y1': bottom, 'continued': True})
            if t:
                meta['formula_list'] = {'page': p + 1, 'bbox': t['bbox']}
    if not bnds:
        return segs
    intros = []
    first = bnds[0]
    pre = []
    for p in range(1, first['page'] + 1):
        if skipped_page(doc[p]):
            continue
        top, bottom = page_bounds(doc[p])
        y1 = bottom
        if p == first['page']:
            fs = [s for s in segs if s['page'] == p and not s['continued']]
            y1 = min(s['y0'] for s in fs) if fs else first['y'] - PAD_TOP
        t = trim(doc, {'path': ('intro',), 'page': p, 'y0': top, 'y1': y1, 'continued': True})
        if t and t['y1'] - t['y0'] > 12:
            pre.append({'page': p + 1, 'bbox': t['bbox']})
    if pre:
        heads = [SECTION_HEAD.match(l['text'].strip()) for x in pre
                 for l in visible_lines(doc[x['page'] - 1], x['bbox'][1], x['bbox'][3])]
        heads = [h.group(1) or h.group(2) for h in heads if h]
        intros.append({'section': heads[0] if heads else None, 'before': 1, 'segments': pre})
    # a section heading inside a question's last piece: that piece ends at the heading
    out, cut_path = [], None
    for s in segs:
        if cut_path is not None and s['path'] == cut_path:
            intros[-1]['segments'].append({'page': s['page'] + 1, 'bbox': s['bbox']})
            continue
        cut_path = None
        page = doc[s['page']]
        head = None
        lines = visible_lines(page, s['y0'], s['y1'])
        for i, l in enumerate(lines):
            m = SECTION_HEAD.match(l['text'].strip())
            if not m:
                continue
            nxt = ' '.join(x['text'] for x in lines if abs(x['y0'] - l['y0']) < 3 and x is not l) + ' ' + \
                  ' '.join(x['text'] for x in lines[i + 1:i + 3])
            if m.group(1) or re.search(r'MODELLING|INVESTIGATION', nxt):
                head = l
                break
        if head is None or head['y0'] - s['y0'] < 2:
            if head is not None:          # the piece starts with the heading: all of it is intro
                intros.append({'section': (SECTION_HEAD.match(head['text'].strip()).group(1) or SECTION_HEAD.match(head['text'].strip()).group(2)),
                               'before': s['path'][0] + 1, 'segments': [{'page': s['page'] + 1, 'bbox': s['bbox']}]})
                cut_path = s['path']
                continue
            out.append(s)
            continue
        sec = SECTION_HEAD.match(head['text'].strip())
        above = trim(doc, dict(s, y1=head['y0'] - 3))
        below = trim(doc, dict(s, y0=head['y0'] - 3, continued=True))
        if above:
            out.append(above)
        intros.append({'section': sec.group(1) or sec.group(2), 'before': s['path'][0] + 1,
                       'segments': [{'page': s['page'] + 1, 'bbox': below['bbox']}] if below else []})
        cut_path = s['path']
    if intros:
        meta['intros'] = intros
    return out


def segment_text_all(doc, q):
    lines = []
    for s in q['segments']:
        seg = {'page': s['page'] - 1, 'y0': s['bbox'][1], 'y1': s['bbox'][3]}
        lines += segment_text(doc, seg)
    return lines


def has_drawings(doc, q):
    for s in q['segments']:
        page = doc[s['page'] - 1]
        top, bottom = page_bounds(page)
        text = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in visible_lines(page, top, bottom)]
        for r in ink_boxes(page, top, bottom):
            if r.y0 >= s['bbox'][1] and r.y1 <= s['bbox'][3] and not any(r.intersects(t) for t in text) and r.width * r.height > 40:
                return True
    return False


def block_marks(node):
    """Old papers print one bracket for a whole block of sub-parts, after the last one: '(a)(i) ... (ii) ... (iii) ...
    (iv) Calculate the density. [3]' - the 3 marks are for (a), not for (a)(iv) (Dhruv, round 26, 2011 ON 53 q1).
    When every sub-part but the last has no mark, the last one's marks go to the part itself (the total is unchanged)."""
    kids = node.get('parts', [])
    for k in kids:
        block_marks(k)
    if 'id' not in node and len(kids) >= 2 and all(not k.get('parts') for k in kids) \
            and all(not k.get('marks') for k in kids[:-1]) and kids[-1].get('marks'):
        node['marks'] = node.get('marks', 0) + kids[-1]['marks']
        kids[-1]['marks'] = 0


def sum_marks(node):
    return node.get('marks', 0) + sum(sum_marks(k) for k in node.get('parts', []))
