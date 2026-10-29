"""Check that everything printed on every question page lies inside some extracted segment.

Works on the rendered page (what a student sees), so invisible geometry, curve control points and
line spacing never raise false alarms. Prints pages with printed ink left outside all segments.

    python3 pipeline/coverage.py                       # all papers
    python3 pipeline/coverage.py 0625_2025MJ_41 ...    # some papers
"""
import glob, json, os, sys, collections
import numpy as np
import pymupdf as fitz
sys.path.insert(0, os.path.dirname(__file__))
from run import cleaned
import paths
from layout import page_bounds, dark_mask, ZOOM
from extract import is_blank_page, end_of_paper, is_erratum_page

MIN_PIXELS = 6          # at 144 dpi: a few specks are not content


def segs_of(node):
    out = list(node.get('segments', []))
    for k in node.get('parts', []):
        out += segs_of(k)
    return out


def lost_ink(page, segs, top, bottom):
    """(pixel count, bbox in pt) of printed ink between top and bottom outside all segments, or None."""
    mask = dark_mask(page).copy()
    H = mask.shape[0]
    mask[:max(0, int(top * ZOOM))] = False
    mask[min(H, int(bottom * ZOOM) + 1):] = False
    for s in segs:
        x0, y0, x1, y1 = s
        mask[max(0, int((y0 - 1) * ZOOM)):int((y1 + 1) * ZOOM) + 1, max(0, int((x0 - 1) * ZOOM)):int((x1 + 1) * ZOOM) + 1] = False
    n = int(mask.sum())
    if n < MIN_PIXELS:
        return None
    ys, xs = np.nonzero(mask)
    return n, [round(xs.min() / ZOOM), round(ys.min() / ZOOM), round((xs.max() + 1) / ZOOM), round((ys.max() + 1) / ZOOM)]


def paper_problems(pj):
    """Yields (paper id, doc, page no, pixel count, bbox, segment rects) for every page with lost ink."""
    d = os.path.dirname(pj); meta = json.load(open(pj))
    doc = fitz.open(cleaned(paths.raw_pdfs(meta['question_ids'][0])[0]))
    by_page = collections.defaultdict(list)
    for qf in glob.glob(os.path.join(d, 'q*', '*.json')):
        for s in segs_of(json.load(open(qf))):
            by_page[s['page']].append(s['bbox'])
    last = max(by_page) if by_page else 0
    for pno in range(2, len(doc) + 1):
        page = doc[pno - 1]
        if is_blank_page(page) or is_erratum_page(page):
            continue
        top, bottom = page_bounds(page)
        if pno >= last:
            bottom = end_of_paper(page, top, bottom)
        hit = lost_ink(page, by_page[pno], top, bottom)
        if hit:
            yield paths.paper_id(meta), doc, pno, hit[0], hit[1], by_page[pno]


def check_paper(pj):
    """(pages checked, [(where, pixels, bbox)]) for one paper.json."""
    meta = json.load(open(pj))
    doc = fitz.open(cleaned(paths.raw_pdfs(meta['question_ids'][0])[0]))
    pages = sum(1 for p in range(1, len(doc)) if not is_blank_page(doc[p]) and not is_erratum_page(doc[p]))
    probs = [(f"{meta['paper_code']} {meta['year']}-{meta['session']} p{pno}", n, bbox)
             for _, _, pno, n, bbox, _ in paper_problems(pj)]
    return pages, probs


if __name__ == '__main__':
    want = sys.argv[1:]
    total_pages, problems = 0, []
    for pj in paths.paper_files():
        if want and paths.paper_id(json.load(open(pj))) not in want:
            continue
        n, p = check_paper(pj)
        total_pages += n; problems += p
    print('pages checked', total_pages, 'pages with uncovered ink', len(problems))
    for p in problems[:60]:
        print(' ', p)
