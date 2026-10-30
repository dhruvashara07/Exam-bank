"""Split a cleaned Cambridge question paper into questions, parts and printable segments.

A *segment* is a horizontal strip of one page that belongs to exactly one label path,
for example question 4's stem, 4(a)'s stem, or 4(a)(ii). Printing the segments of a
question (or of a chosen part plus its parent stems) in order reproduces the original
layout, answer space included.
"""
import re
import pymupdf as fitz
from layout import page_bounds, visible_lines, ink_boxes, label_tokens, ROMAN, LETTERS, CONTENT_X0, CONTENT_X1, row_ink, ink_extent, ZOOM, tight_ink, grow_to_ink

PAD_TOP, PAD_BOTTOM = 4.0, 5.0
CAPTION = re.compile(r'^(Fig\.|Figure|Table)\s*\d+(\.\d+)?(\s*\(.*\))?$')
MARK = re.compile(r'\[\s*(\d{1,2})\s*\]')
TOTAL = re.compile(r'\[\s*Total\s*:\s*(\d{1,3})\s*\]')
DOTS = re.compile(r'\.{12,}')

SESSION_NAMES = {'FM': 'February-March', 'MJ': 'May-June', 'ON': 'October-November'}
PAPER_TYPES = {1: 'mcq_core', 2: 'mcq_extended', 3: 'theory_core', 4: 'theory_extended',
               5: 'practical_test', 6: 'alternative_to_practical'}


# Standard totals, used when the cover does not print one (covers before 2020).
STANDARD_TOTAL = {'mcq_core': 40, 'mcq_extended': 40, 'mcq': 40, 'theory_core': 80, 'theory_extended': 80,
                  'practical_test': 40, 'alternative_to_practical': 40}


def paper_type_from_cover(cover, paper):
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
    return PAPER_TYPES[paper]


def paper_meta(doc, syllabus, year, session, pv):
    cover = doc[0].get_text()
    m = re.search(r'total mark for this paper is (\d+)', cover)
    dur = re.search(r'\n\s*(\d+ hours?(?: \d+ minutes)?|\d+ minutes)\s*\n', cover)
    ptype = paper_type_from_cover(cover, int(pv[0]))
    return {
        'syllabus': syllabus, 'subject': 'Physics', 'board': 'CAIE', 'exam': 'IGCSE',
        'year': year, 'session': session, 'season': SESSION_NAMES[session],
        'paper': int(pv[0]), 'variant': int(pv[1]), 'paper_code': f'{syllabus}/{pv}',
        'paper_type': ptype, 'is_mcq': ptype.startswith('mcq'),
        'total_marks': int(m.group(1)) if m else STANDARD_TOTAL.get(ptype),
        'total_marks_source': 'cover' if m else 'standard',
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
    rest = [l for l in visible_lines(page, top, bottom) if not re.search(r'BLANK\s+PAGE', l['text'])]
    return len(rest) == 0


def boundaries(doc):
    """Walk pages in order and accept labels that continue the numbering sequence."""
    out, q, letter, roman = [], 0, None, None
    for pno in range(1, len(doc)):
        page = doc[pno]
        if is_blank_page(page) or is_erratum_page(page):
            continue
        top, bottom = page_bounds(page)
        for t in label_tokens(page, top, bottom):
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
    return min(cands, key=lambda c: (cost(c), abs(c - y)))


def raw_segments(doc, bnds):
    """Strips of pages between consecutive boundaries, continuing across page breaks."""
    segs = []
    pages = [p for p in range(1, len(doc)) if not is_blank_page(doc[p]) and not is_erratum_page(doc[p])]
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


def segment_text(doc, seg):
    page = doc[seg['page']]
    top, bottom = page_bounds(page)
    return [l for l in visible_lines(page, top, bottom) if seg['y0'] - 1 <= (l['y0'] + l['y1']) / 2 <= seg['y1'] + 1]


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


def find_figures(doc, seg, lines):
    """Captioned figures (Fig. 1.1 / Table 2.1) inside a segment: band from the prose above to the caption."""
    page = doc[seg['page']]
    top, bottom = page_bounds(page)
    figs = []
    caps = [l for l in lines if CAPTION.match(l['text'])]
    marks_text = [fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in lines
                  if MARK.fullmatch(l['text'].strip()) or TOTAL.fullmatch(l['text'].strip()) or DOTS.search(l['text'])]
    drawings = [r for r in ink_boxes(page, top, bottom) if seg['y0'] <= r.y0 and r.y1 <= seg['y1'] + 1
                and not any(abs(r.x0 - m.x0) < 1 and abs(r.y0 - m.y0) < 1 and abs(r.x1 - m.x1) < 1 for m in marks_text)]
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
    for cap in caps:
        is_table = cap['text'].startswith('Table')
        prose_above = [l for l in lines if l['y1'] <= cap['y0'] and not DOTS.search(l['text']) and (prose_like(l) or bullet_item(l) or (re.match(r'^(\d{1,2}|\([a-z]+\))\s', l['text']) and l['x0'] < 110)
                                                                    or (re.fullmatch(r'\([a-z]+\)', l['text'].strip()) and l['x0'] < 110)
                                                                    or re.fullmatch(r'Method \d', l['text'].strip())
                                                                    or (l['x0'] <= 76 and l['text'].rstrip().endswith('.'))
                                                                    or (l['text'].rstrip().endswith(('.', ':')) and l['x0'] < 130 and any(abs(l['x0'] - o['x0']) < 2 for o in long_lines if o is not l)))]
        for l in sorted(lines, key=lambda l: l['y0']):    # last line of a sentence ('Fig. 2.2.' after a long line)
            if l['y1'] <= cap['y0'] and l not in prose_above and re.search(r'[a-z]', l['text']) and \
                    l['text'].rstrip()[-1:] in '.:?' and any(0 < l['y0'] - p['y0'] < 1.6 * (l['y1'] - l['y0'])
                                                             and p['x0'] - 3 <= l['x0'] <= p['x0'] + 70 for p in prose_above):
                prose_above.append(l)
        rules = [r for r in drawings if not any(abs(r.x0 - t.x0) < 1 and abs(r.y0 - t.y0) < 1 for t in text_boxes)]
        grid_below = [r for r in rules if cap['y1'] - 1 <= r.y0 <= cap['y1'] + 12]
        grid_above = [r for r in rules if cap['y0'] - 30 <= r.y1 <= cap['y0'] + 1]
        if is_table and (grid_below or not grid_above):
            # table caption sits above the table (the usual case)
            prose_below = [l for l in lines if l['y0'] > cap['y1'] + 4 and len(l['text']) > 40
                           and not DOTS.search(l['text']) and not in_grid(l)]
            band = (cap['y0'] - 2, (min(l['y0'] for l in prose_below) - 4) if prose_below else seg['y1'])
        else:          # figure caption, or a table captioned underneath (table drawn just above, nothing below)
            band = ((max(l['y1'] for l in prose_above) + 2) if prose_above else seg['y0'], cap['y1'] + 2)
        strip = fitz.Rect(0, band[0] - 1, page.rect.width, band[1] + 1)
        grown = [fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1) for r in drawings]   # lines have zero height
        inside = [tight_ink(page, g & strip, marks_text) for g in grown
                  if g.y1 >= strip.y0 and g.y0 <= strip.y1 and not (g & strip).is_empty]
        inside = [r for r in inside if r is not None]       # what is printed, inside the band
        if not inside:
            continue
        x0 = min(r.x0 for r in inside); x1 = max(r.x1 for r in inside)
        y0 = min(r.y0 for r in inside); y1 = max(r.y1 for r in inside)
        g = grow_to_ink(page, fitz.Rect(x0, y0, x1, y1), fitz.Rect(CONTENT_X0, max(seg['y0'], band[0] - 1), CONTENT_X1, min(seg['y1'], band[1] + 1)),
                        exclude=[fitz.Rect(l['x0'], l['y0'], l['x1'], l['y1']) for l in prose_above])
        x0, y0, x1, y1 = g.x0, g.y0, g.x1, g.y1
        figs.append({'caption': cap['text'], 'page': seg['page'],
                     'bbox': [round(x0 - 3, 1), round(max(y0 - 3, seg['y0']), 1), round(x1 + 3, 1),
                              round(min(y1 + 3, seg['y1']), 1)]})    # a crop never reaches past its piece
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
        for f in find_figures(doc, s, lines):
            num = re.match(r'^(?:Fig\.|Figure|Table)\s*([\d.]+)', f['caption']).group(1).replace('.', '-')
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
            q['marks'] = sum_marks(q)
            if q['marks'] == 0 and not q.get('parts') and q.get('total_marks'):
                q['marks'] = q['total_marks']        # single-part question marked only by '[Total: n]'
            if 'total_marks' in q and q['total_marks'] != q['marks']:
                q['review']['reasons'].append(f"marks found {q['marks']} but [Total: {q['total_marks']}]")
        if len(q['segments']) == 0 and not q.get('parts'):
            q['review']['reasons'].append('no content found')
        q['review']['status'] = 'flagged' if q['review']['reasons'] else 'auto'
        out.append(q)
    return meta, out


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


def sum_marks(node):
    return node.get('marks', 0) + sum(sum_marks(k) for k in node.get('parts', []))
