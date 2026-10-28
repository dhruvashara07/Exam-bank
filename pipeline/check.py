"""Everything Claude needs to check papers before approving them (used by the daily check).

    python3 pipeline/check.py                    # all pending papers
    python3 pipeline/check.py 0625_2025MJ_41     # specific papers
Prints a report per paper (marks vs cover, flagged items, uncovered ink) and writes contact sheets to
out/check/<paper>/sheet_NN.jpg: each row = original page with the cut boxes | rebuilt question | figures.
Look at every sheet before approving.
"""
import json, os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import paths
from approve import pending, all_papers
from coverage import check_paper
import review_assets as ra

OUT = os.path.join(paths.ROOT, 'out', 'check')
COLS = (560, 560, 340)
MAX_H = 2600


def fit(im, w):
    if im is None:
        return Image.new('RGB', (w, 20), 'white')
    return im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS) if im.width > w else im


def sheets(paper, qids):
    d = os.path.join(OUT, paper)
    items = ra.render_items(os.path.join(d, 'items'), [(q, 'check') for q in qids], {})
    rows = []
    for it in items:
        cells = [fit(Image.open(os.path.join(d, 'items', it['images'][k])) if k in it['images'] else None, w)
                 for k, w in zip(('orig', 'q', 'figs'), COLS)]
        h = max(c.height for c in cells) + 24
        row = Image.new('RGB', (sum(COLS) + 20, h), (235, 235, 235))
        x = 0
        for c, w in zip(cells, COLS):
            row.paste(c, (x, 22)); x += w + 10
        from PIL import ImageDraw
        ImageDraw.Draw(row).text((4, 4), f"{it['id']}  {it['type']}  {it['marks']} marks  answer={it.get('answer')}", fill=(0, 0, 0))
        rows.append(row)
    out, cur, n = [], [], 0
    for r in rows + [None]:
        if r is None or (cur and sum(x.height for x in cur) + r.height > MAX_H):
            if cur:
                n += 1
                sheet = Image.new('RGB', (cur[0].width, sum(x.height for x in cur) + 4 * len(cur)), (120, 0, 0))
                y = 0
                for x in cur:
                    sheet.paste(x, (0, y)); y += x.height + 4
                p = os.path.join(d, f'sheet_{n:02d}.jpg'); sheet.save(p, quality=80); out.append(p)
            cur = []
        if r is not None:
            cur.append(r)
    return out


if __name__ == '__main__':
    papers = sys.argv[1:] or pending()
    files = all_papers()
    if not papers:
        print('nothing pending'); sys.exit(0)
    queue = json.load(open(os.path.join(paths.ROOT, 'review', 'queue.json')))
    for p in papers:
        meta = json.load(open(files[p]))
        print(f"\n== {p}  ({meta['paper_code']} {meta['season']} {meta['year']}, {meta['paper_type']})")
        print(f"   questions {meta['questions']}, marks {meta['marks_found']}/{meta['total_marks']}"
              f"{'' if meta['checks']['marks_match_total'] else '   <-- MISMATCH'}, mark scheme: {meta.get('mark_scheme', 'ok')}")
        for x in queue:
            if x['id'].startswith(p):
                print(f"   flagged {x['id']}: {'; '.join(x['reasons'])}")
        n, probs = check_paper(files[p])
        print(f"   coverage: {n} pages, {len(probs)} with uncovered ink {probs[:5] if probs else ''}")
        for s in sheets(p, meta['question_ids']):
            print('   sheet', os.path.relpath(s, paths.ROOT))
