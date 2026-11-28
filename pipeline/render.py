"""Cut page regions into standalone vector SVGs (text converted to outlines so no fonts are needed).

Content outside the region is deleted (not just hidden) with redactions, so each SVG holds
only what it shows.
"""
import re
import pymupdf as fitz
import subjects


def _subtract(r, holes):
    """Rectangle r minus the rectangles in holes, as a list of rectangles."""
    pieces = [fitz.Rect(r)]
    for h in holes:
        nxt = []
        for p in pieces:
            i = p & h
            if i.is_empty:
                nxt.append(p); continue
            for q in (fitz.Rect(p.x0, p.y0, p.x1, i.y0), fitz.Rect(p.x0, i.y1, p.x1, p.y1),
                      fitz.Rect(p.x0, i.y0, i.x0, i.y1), fitz.Rect(i.x1, i.y0, p.x1, i.y1)):
                if q.width > 0.01 and q.height > 0.01:
                    nxt.append(q)
        pieces = nxt
    return pieces


def _isolated_page(src_doc, page_index, clip):
    tmp = fitz.open()
    tmp.insert_pdf(src_doc, from_page=page_index, to_page=page_index)
    page = tmp[0]
    W, H = page.rect.width, page.rect.height
    outside = [fitz.Rect(-50, -50, W + 50, clip.y0 - 0.5), fitz.Rect(-50, clip.y1 + 0.5, W + 50, H + 50),
               fitz.Rect(-50, clip.y0, clip.x0 - 0.5, clip.y1), fitz.Rect(clip.x1 + 0.5, clip.y0, W + 50, clip.y1)]
    outside = [r for r in outside if not r.is_empty]
    # a large letter printed inside the region has a font box reaching outside it (a 76 pt 'R' in a diagram):
    # redaction would delete it, so the text pass leaves holes for letters whose printed body is inside
    keep = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                for c in sp['chars']:
                    bb = fitz.Rect(c['bbox'])
                    if c['c'].strip() and not clip.contains(bb) and (bb & clip).get_area() > 0.5 * bb.get_area():
                        keep.append(bb)
    for r in outside:
        page.add_redact_annot(r, fill=False)
    chem_ = subjects.is_chem(subjects.path_syl(src_doc.name) or '')
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS if chem_ else fitz.PDF_REDACT_IMAGE_REMOVE,   # chemistry: atom letters
                          # are tiny images taller than the letter (6 x 42 pt): removing every image that reaches outside the cut
                          # dropped them from the structure pictures (2021 FM 42, C2b 352) - only the pixels outside are blanked
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=fitz.PDF_REDACT_TEXT_NONE if keep else fitz.PDF_REDACT_TEXT_REMOVE)
    if keep:
        for r in outside:
            for q in _subtract(r, keep):
                page.add_redact_annot(q, fill=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_REMOVE)
    return tmp


def region_pdf(src_doc, page_index, bbox):
    """A one-page PDF containing only the clipped region at its original size."""
    clip = fitz.Rect(bbox)
    tmp = _isolated_page(src_doc, page_index, clip)
    out = fitz.open()
    page = out.new_page(width=clip.width, height=clip.height)
    page.show_pdf_page(page.rect, tmp, 0, clip=clip)
    return out


def fix_cmyk_images(svg):
    """A CMYK picture (a JPEG 2000 in the Cambridge PDF, Adobe-inverted) is written by MuPDF as a CMYK JPEG that browsers
    show black (2003 MJ 02 q7 Fig 7.3, the sunken ship). Re-encoded as inverted-CMYK -> RGB PNG; other pictures are untouched."""
    import base64, io
    from PIL import Image, ImageChops

    def fix(m):
        try:
            im = Image.open(io.BytesIO(base64.b64decode(re.sub(r'\s', '', m.group(2)))))
            if im.mode != 'CMYK':
                return m.group(0)
            buf = io.BytesIO()
            ImageChops.invert(im).convert('RGB').save(buf, 'PNG', optimize=True)
            return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        except Exception:
            return m.group(0)
    return re.sub(r'data:image/(jpeg|jpg);base64,\s*([A-Za-z0-9+/=\s]+)', fix, svg)


def region_svg(src_doc, page_index, bbox):
    doc = region_pdf(src_doc, page_index, bbox)
    svg = doc[0].get_svg_image(text_as_path=True)
    if subjects.maths_path(src_doc.name) or subjects.is_chem(subjects.path_syl(src_doc.name) or ''):   # (chemistry: 'leastreactive', 355)
        svg = _respace(svg, src_doc[page_index], fitz.Rect(bbox))
    if subjects.is_chem(subjects.path_syl(src_doc.name) or ''):
        return minify(fix_cmyk_images(svg), exact_matrix=True)
    return minify(fix_cmyk_images(svg))


def _respace(svg, page, clip):
    """MuPDF's redaction (the isolation above) rewrites text runs and drops the width of spaces: a label inside a
    figure came out 'Reflectioninleftdiagonal' (2024 FM 62 q3(b), Dhruv round 33). Every glyph goes back to the x
    of the same character on the original page (same baseline, never left of where it is). Maths only."""
    orig = {}
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                for c in sp['chars']:
                    if c['c'].strip():
                        x, y = c['origin'][0] - clip.x0, c['origin'][1] - clip.y0
                        orig.setdefault(c['c'], []).append([x, y, False])
    uses = list(re.finditer(r'(<use data-text="([^"]*)"[^>]*?transform="matrix\()([^)]*)(\)")', svg))
    if not uses or not orig:
        return svg
    rep = {}
    order = sorted(range(len(uses)), key=lambda k: (round(float(uses[k].group(3).split(',')[5]), 1),
                                                   float(uses[k].group(3).split(',')[4])))
    for k in order:
        m = uses[k]; ch = m.group(2); v = [float(t) for t in m.group(3).split(',')]
        if abs(v[1]) > 1e-6 or abs(v[2]) > 1e-6:
            continue                                # rotated text: left as it is
        cand = [o for o in orig.get(ch, []) if not o[2] and abs(o[1] - v[5]) < 0.8 and -0.3 <= o[0] - v[4] < 60]
        if not cand:
            continue
        o = min(cand, key=lambda o: o[0]); o[2] = True
        if o[0] - v[4] > 0.3:
            v[4] = o[0]
            rep[k] = m.group(1) + ','.join(f'{t:.3f}' for t in v) + m.group(4)
    if not rep:
        return svg
    out, last = [], 0
    for k, m in enumerate(uses):
        if k in rep:
            out.append(svg[last:m.start()]); out.append(rep[k]); last = m.end()
    out.append(svg[last:])
    return ''.join(out)


USE_LIMIT = 900        # Cloudinary rejects SVGs with 1000+ <use> elements ("Resource is invalid")


def minify(svg, exact_matrix=False):
    svg = re.sub(r'>\s+<', '><', svg)
    if exact_matrix:              # chemistry (C2a r47, ERROR_PATTERNS 350): a path drawn at scale .04398 on coordinates ~16000
        keep = {}                 # moved 16 pt when its matrix was cut to .043 - matrices keep 6 significant digits
        def _m(m):
            k = f'@@M{len(keep)}@@'
            keep[k] = 'matrix(' + ','.join(f'{float(v):.6g}' for v in m.group(1).split(',')) + ')'
            return k
        svg = re.sub(r'matrix\(([^)]*)\)', _m, svg)
    svg = re.sub(r'(-?\d*\.\d{3})\d+', r'\1', svg)   # 3 decimals: well below print resolution
    if exact_matrix:
        svg = re.sub(r'@@M\d+@@', lambda m: keep[m.group(0)], svg)
    return limit_uses(svg)


def limit_uses(svg):
    """Text-as-path SVGs draw every letter as <use href="#glyph">. Drop uses of empty glyphs (spaces);
    if still too many for Cloudinary, write each glyph's path inline instead (same picture, bigger file)."""
    glyphs = dict(re.findall(r'<path id="([^"]+)" d="([^"]*)"/>', svg))
    empty = {k for k, d in glyphs.items() if not d.strip()}
    use_re = re.compile(r'<use ([^>]*?)xlink:href="#([^"]+)"([^>]*)/>')
    if empty:
        svg = use_re.sub(lambda m: '' if m.group(2) in empty else m.group(0), svg)
    if svg.count('<use') < USE_LIMIT:
        return svg

    def inline(m):
        d = glyphs.get(m.group(2))
        if d is None:
            return m.group(0)
        return f'<path {m.group(1)}{m.group(3).strip()} d="{d}"/>'.replace('  ', ' ')
    return use_re.sub(inline, svg)
