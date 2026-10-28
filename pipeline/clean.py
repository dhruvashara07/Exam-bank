"""Remove the PapaCambridge watermark layer from 2026 PDFs.

PapaCambridge wraps each original page as:
  q [ q <watermark tiles: gs /gRLs0, FormXob.pcm> Q ] <original content> Q
  q <outline watermark + footer: gs /gRLs0-0> Q
We delete every q..Q group that directly sets a /gRLs0* graphics state, plus the
final top-level group that carries the outline watermark and footer text.
Files without the watermark are copied unchanged.
"""
import re, sys, pathlib, pikepdf

MARK = '/gRLs0'

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
    doc.save(path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


def clean(src, dst):
    pdf = pikepdf.open(src)
    n = sum(clean_page(pdf, p) for p in pdf.pages)
    pdf.save(dst)
    if '/qp_' in src.replace('\\', '/'):
        strip_corner_marks(dst)
    return n

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    print(clean(src, dst), 'pages cleaned')
