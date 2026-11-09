"""Remove the PapaCambridge watermark layer from 2026 PDFs.

PapaCambridge wraps each original page as:
  q [ q <watermark tiles: gs /gRLs0, FormXob.pcm> Q ] <original content> Q
  q <outline watermark + footer: gs /gRLs0-0> Q
We delete every q..Q group that directly sets a /gRLs0* graphics state, plus the
final top-level group that carries the outline watermark and footer text.
Files without the watermark are copied unchanged.
"""
import os, re, sys, pathlib, pikepdf

MARK = '/gRLs0'


def is_barcode_span(sp):
    """Barcodes printed as text. Judged by content, never by font name (2025+ papers use one font,
    'AllAndNone', for everything): the '* 0019654991002 *' number, a wide strip of glyphs with no
    letters or digits (1D barcode), or a run of unusual symbols (2D code)."""
    t = sp['text']
    if re.fullmatch(r'\*\s*[\d ]{8,}\s*\*', t.strip()):
        return True
    x0, y0, x1, y1 = sp['bbox']
    ctrl = sum(1 for c in t if ord(c) < 32)
    if ctrl >= 3 and all(ord(c) < 32 or c in ', ' for c in t) and (x1 - x0) > 60:
        return True                                   # 1D barcode: ',\x01\x01\t...,'
    odd = sum(1 for c in t if 0xA0 <= ord(c) < 0x250)
    return len(t) >= 8 and ' ' not in t and odd >= 0.6 * len(t)   # 2D code

def clean_page(pdf, page):
    ops = list(pikepdf.parse_content_stream(page))
    stack, groups = [], []          # groups: (start, end, depth, direct_ops)
    direct = {}
    for i, (operands, op) in enumerate(ops):
        o = str(op)
        if o == 'q':
            stack.append(i); direct[i] = []
        elif o == 'Q' and stack:
            s = stack.pop(); groups.append((s, i, len(stack), direct.pop(s)))
        elif stack:
            direct[stack[-1]].append((operands, o))
    drop = set()
    top = [g for g in groups if g[2] == 0]
    for s, e, depth, d in groups:
        if any(o == 'gs' and str(a[0]).startswith(MARK) for a, o in d):
            drop.update(range(s, e + 1))
    for s, e, depth, d in top:            # outline watermark + footer group
        inner = range(s, e + 1)
        if any(str(ops[k][1]) == 'gs' and str(ops[k][0][0]).startswith(MARK + '-0') for k in inner):
            drop.update(inner)
    # Cambridge page furniture (corner marks, margin strips, barcode) sits in form XObjects /R0../R9;
    # the question content itself is /R or inline, so those calls can go.
    for i, (operands, op) in enumerate(ops):
        if str(op) == 'Do' and re.fullmatch(r'/R\d', str(operands[0])):
            drop.add(i)
    if not drop:
        return False
    kept = [ops[i] for i in range(len(ops)) if i not in drop]
    page.Contents = pdf.make_stream(pikepdf.unparse_content_stream(kept))
    return True

def strip_corner_marks(path):
    """Delete the crop/corner marks in the four page corners (question papers only)."""
    import pymupdf as fitz
    doc = fitz.open(path)
    for page in doc:
        W, H = page.rect.width, page.rect.height
        if W > H:
            continue
        for r in (fitz.Rect(0, 0, 40.5, 52), fitz.Rect(555.5, 0, W, 52),
                  fitz.Rect(0, H - 52, 40.5, H), fitz.Rect(555.5, H - 52, W, H)):
            page.add_redact_annot(r, fill=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                              text=fitz.PDF_REDACT_TEXT_NONE)
        # barcodes printed as text: a barcode font (e.g. 'AllAndNone') and the '* 0019654991002 *' number
        hits = []
        for b in page.get_text('dict')['blocks']:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                for sp in l['spans']:
                    if is_barcode_span(sp):
                        hits.append(fitz.Rect(sp['bbox']))
        if hits:
            for r in hits:
                page.add_redact_annot(r, fill=False)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_REMOVE)
    doc.save(path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


def strip_stamp_images(path):
    """A download site's stamp (older PDFs: a 'www.PapaCambridge.com' banner in the top corner and a strip
    along the bottom) is a picture placed at the same spot on (nearly) every page: not part of the paper.
    Pictures that repeat at one position on 60 % or more of the pages (at least 3) are removed there."""
    import pymupdf as fitz, collections
    doc = fitz.open(path)
    if len(doc) < 3:
        return 0
    seen = collections.Counter()
    for page in doc:
        for b in {tuple(round(v) for v in i['bbox']) for i in page.get_image_info()}:
            seen[b] += 1
    stamps = [fitz.Rect(b) for b, n in seen.items() if n >= max(3, 0.6 * len(doc))]
    if not stamps:
        return 0
    for page in doc:
        hit = False
        for i in page.get_image_info():
            r = fitz.Rect(i['bbox'])
            if any(abs(r.x0 - s.x0) < 1.5 and abs(r.y0 - s.y0) < 1.5 and abs(r.x1 - s.x1) < 1.5 and abs(r.y1 - s.y1) < 1.5 for s in stamps):
                page.add_redact_annot(r, fill=False); hit = True
        if hit:
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_NONE)
    doc.save(path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    return len(stamps)


def strip_examiner_rule_drawn(path):
    """2002-2004 papers: the rule of the 'For Examiner's Use' column is not a vector path (no rule for
    strip_examiner_column to find) but a thin line in the page's drawing: it would sit inside every piece. Found by
    rendering the right-hand strip: a very thin vertical ink run over most of the page height, on pages that carry the
    heading. Painted white; returns the number of pages changed."""
    import numpy as np
    import pymupdf as fitz
    doc = fitz.open(path)
    n = 0
    for page in doc:
        W, H = page.rect.width, page.rect.height
        if W > H or not any(w[4].startswith('Examiner') and w[0] > 0.85 * W and w[1] < 75 for w in page.get_text('words')):
            continue
        if any(d['rect'].width < 1.5 and d['rect'].height > 0.6 * H for d in page.get_drawings()):
            continue                       # a vector rule: strip_examiner_column removes it
        clip = fitz.Rect(0.8 * W, 0, 0.97 * W, H)
        pm = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=clip, colorspace=fitz.csGRAY)
        ink = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width) < 200
        cols = np.nonzero(ink.sum(axis=0) > 0.6 * pm.height)[0]
        if not len(cols) or cols.max() - cols.min() > 8:     # more than 2 pt wide: not a hairline rule
            continue
        xa, xb = clip.x0 + cols.min() / 4 - 0.5, clip.x0 + (cols.max() + 1) / 4 + 0.5
        page.draw_rect(fitz.Rect(xa, 0, xb, H), color=None, fill=(1, 1, 1), overlay=True)
        n += 1
    if n:
        doc.save(path + '.tmp')
        doc.close()
        os.replace(path + '.tmp', path)
    else:
        doc.close()
    return n


def strip_examiner_column(path):
    """Older question papers (2013 and before) have a 'For Examiner's Use' column: a thin vertical rule
    near the page edge running down most of the page, headed by 'For / Examiner's / Use'. It is page
    furniture, not part of any question (figure crops took the rule as drawing ink). Removed only where
    both the long rule and the heading next to it are found; returns the number of pages changed."""
    import pymupdf as fitz
    doc = fitz.open(path)
    n = 0
    for page in doc:
        W, H = page.rect.width, page.rect.height
        rules = [d['rect'] for d in page.get_drawings()
                 if d['rect'].width < 1.5 and d['rect'].height > 0.6 * H
                 and (d['rect'].x0 > 0.8 * W or d['rect'].x1 < 0.2 * W)]
        words = page.get_text('words')
        hits = []
        # 2002-2004 papers: the heading 'For / Examiner's / Use' stays at the top right with no long rule beside it
        corner = [w for w in words if w[0] > 0.85 * W and w[1] < 75 and w[4].replace('’', "'") in ('For', "Examiner's", 'Use')]
        if not rules and any(w[4].startswith('Examiner') for w in corner):
            hits += [('text', fitz.Rect(w[:4])) for w in corner]
        for r in rules:
            near = [w for w in words if w[1] < r.y0 + 40 and w[3] > r.y0 - 15
                    and min(abs(w[0] - r.x0), abs(w[2] - r.x0)) < 45]
            head = [w for w in near if w[4].replace('’', "'") in ('For', "Examiner's", 'Use', "Examiners'")]
            if not any(w[4].startswith('Examiner') for w in head):
                continue
            hits.append(('rule', fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)))
            hits += [('text', fitz.Rect(w[:4])) for w in head]
        if not hits:
            continue
        # two passes so the rule's strip never removes text and the heading's boxes never remove line art
        for want, graphics, text in (('text', fitz.PDF_REDACT_LINE_ART_NONE, fitz.PDF_REDACT_TEXT_REMOVE),
                                     ('rule', fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED, fitz.PDF_REDACT_TEXT_NONE)):
            for kind, r in hits:
                if kind == want:
                    page.add_redact_annot(r, fill=False)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=graphics, text=text)
        n += 1
    if n:
        doc.save(path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    return n


def unrotate(path):
    """Pages stored with /Rotate (many mark schemes before 2020 are landscape this way): bake the
    rotation into the content so text runs left-to-right in page coordinates. Looks identical."""
    import pymupdf as fitz
    doc = fitz.open(path)
    if not any(p.rotation for p in doc):
        return
    for p in doc:
        if p.rotation:
            p.remove_rotation()
    doc.save(path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


A4 = (595.28, 841.89)


def to_a4(pdf, page):
    """A few question papers were published at another page size (0625/23 May/June 2017 is A3,
    0625/51 Oct/Nov 2020 is 612x859). The layout rules work in A4 points, so scale such a page to A4:
    the drawing is unchanged, only its coordinates."""
    x0, y0, x1, y1 = [float(v) for v in page.mediabox]
    w, h = x1 - x0, y1 - y0
    if abs(w - A4[0]) < 3 and abs(h - A4[1]) < 3:
        return False
    s = min(A4[0] / w, A4[1] / h)
    page.contents_coalesce()
    page.contents_add(pdf.make_stream(f'q {s:.6f} 0 0 {s:.6f} {-x0 * s:.4f} {-y0 * s:.4f} cm\n'.encode()), prepend=True)
    page.contents_add(pdf.make_stream(b'\nQ'), prepend=False)
    page.obj.MediaBox = pikepdf.Array([0, 0, A4[0], A4[1]])
    for k in ('/CropBox', '/TrimBox', '/BleedBox', '/ArtBox'):
        if k in page.obj:
            del page.obj[k]
    return True


def drop_answer_booklet(path):
    """Nov 2002 practical test: the PDF holds the question paper and the Answer Booklet (cover 'ANSWER BOOKLET ...
    FOR EXAMINER'S USE', then ruled pages). The booklet is not part of the paper: leave its pages out of the cleaned copy."""
    import pymupdf as fitz
    d = fitz.open(path)
    for i in range(1, len(d)):
        t = d[i].get_text().upper()
        if 'ANSWER BOOKLET' in t and 'FOR EXAMINER' in t:
            d.delete_pages(i, len(d) - 1)
            d.save(path + '.tmp')
            d.close()
            os.replace(path + '.tmp', path)
            return
    d.close()


def clean(src, dst):
    pdf = pikepdf.open(src)
    n = sum(clean_page(pdf, p) for p in pdf.pages)
    if '/qp_' in src.replace('\\', '/'):
        for p in pdf.pages:
            if not p.obj.get('/Rotate'):
                to_a4(pdf, p)
    pdf.save(dst)
    unrotate(dst)
    strip_stamp_images(dst)
    if '/qp_' in src.replace('\\', '/'):
        strip_corner_marks(dst)
        strip_examiner_rule_drawn(dst)
        strip_examiner_column(dst)
        drop_answer_booklet(dst)
    return n

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    print(clean(src, dst), 'pages cleaned')
