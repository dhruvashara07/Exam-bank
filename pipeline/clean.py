"""Remove the PapaCambridge watermark layer from 2026 PDFs.

PapaCambridge wraps each original page as:
  q [ q <watermark tiles: gs /gRLs0, FormXob.pcm> Q ] <original content> Q
  q <outline watermark + footer: gs /gRLs0-0> Q
We delete every q..Q group that directly sets a /gRLs0* graphics state, plus the
final top-level group that carries the outline watermark and footer text.
Files without the watermark are copied unchanged.
"""
import sys, pathlib, pikepdf

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
    if not drop:
        return False
    kept = [ops[i] for i in range(len(ops)) if i not in drop]
    page.Contents = pdf.make_stream(pikepdf.unparse_content_stream(kept))
    return True

def clean(src, dst):
    pdf = pikepdf.open(src)
    n = sum(clean_page(pdf, p) for p in pdf.pages)
    pdf.save(dst)
    return n

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    print(clean(src, dst), 'pages cleaned')
