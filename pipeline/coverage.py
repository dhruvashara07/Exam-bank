"""Check that every piece of ink on every question page lies inside some extracted segment.

Prints pages where ink is left uncovered (content the pipeline would lose).
"""
import glob, json, os, sys, collections
import pymupdf as fitz
sys.path.insert(0, os.path.dirname(__file__))
from run import cleaned, ROOT
import paths
from layout import page_bounds, ink_boxes
from extract import is_blank_page, end_of_paper

def segs_of(node):
    out = list(node.get('segments', []))
    for k in node.get('parts', []):
        out += segs_of(k)
    return out

problems = []
total_pages = 0
for pj in paths.paper_files():
    d = os.path.dirname(pj); meta = json.load(open(pj)); folder = f"{meta['year']}-{meta['session']}"
    doc = fitz.open(cleaned(paths.raw_pdfs(meta['question_ids'][0])[0]))
    by_page = collections.defaultdict(list)
    for qf in glob.glob(os.path.join(d, 'q*', '*.json')):
        for s in segs_of(json.load(open(qf))):
            by_page[s['page']].append(fitz.Rect(s['bbox']))
    last = max(by_page) if by_page else 0
    for pno in range(2, len(doc) + 1):
        page = doc[pno - 1]
        if is_blank_page(page):
            continue
        total_pages += 1
        top, bottom = page_bounds(page)
        if pno >= last:
            bottom = end_of_paper(page, top, bottom)
        lost = [r for r in ink_boxes(page, top, bottom)
                if r.height * r.width > 2 and not any((s + (-1, -1, 1, 1)).contains(r) for s in by_page[pno])]
        if lost:
            u = lost[0] | lost[-1]
            problems.append((f"{meta['paper_code']} {folder} p{pno}", len(lost), [round(v) for v in u]))
print('pages checked', total_pages, 'pages with uncovered ink', len(problems))
for p in problems[:40]:
    print(' ', p)
