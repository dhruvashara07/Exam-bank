"""Contact sheet of coverage problems: each tile = the page area around printed ink that no segment
contains (red box), with the segments in green.

    python3 pipeline/coverage_sheet.py OUT.png [paper ids...]
"""
import json, os, sys
import pymupdf as fitz
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import paths
from coverage import paper_problems

if __name__ == '__main__':
    out, want = sys.argv[1], sys.argv[2:]
    tiles = []
    for pj in paths.paper_files():
        if want and paths.paper_id(json.load(open(pj))) not in want:
            continue
        for pid, doc, pno, n, bb, segs in paper_problems(pj):
            page = doc[pno - 1]
            clip = fitz.Rect(0, max(0, bb[1] - 40), page.rect.width, min(page.rect.height, bb[3] + 40))
            z = 0.9
            pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip)
            im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            dr = ImageDraw.Draw(im)
            for s in segs:
                dr.rectangle([(s[0] - clip.x0) * z, (s[1] - clip.y0) * z, (s[2] - clip.x0) * z, (s[3] - clip.y0) * z], outline=(0, 160, 0))
            dr.rectangle([(bb[0] - clip.x0) * z - 2, (bb[1] - clip.y0) * z - 2, (bb[2] - clip.x0) * z + 2, (bb[3] - clip.y0) * z + 2],
                         outline=(255, 0, 0), width=2)
            dr.text((4, 2), f'{pid} p{pno} ({n}px)', fill=(200, 0, 0))
            im.thumbnail((540, 300))
            tiles.append(im)
    W = 1090; x = y = rowh = 0; placed = []
    for t in tiles:
        if x + t.width > W:
            x, y = 0, y + rowh + 6; rowh = 0
        placed.append((t, x, y)); x += t.width + 6; rowh = max(rowh, t.height)
    sheet = Image.new('RGB', (W, max(1, y + rowh + 4)), (90, 90, 90))
    for t, x, y in placed:
        sheet.paste(t, (x, y))
    sheet.save(out)
    print(len(tiles), 'tiles')
