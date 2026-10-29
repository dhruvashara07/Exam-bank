"""One image per paper: every question page with its cut boxes (colour per question, part label at the
right edge, orange = figure crops). This is what Claude looks at for the 'Claude checked' stage.

    python3 pipeline/overview.py [paper ids...]      -> out/overview/<paper id>.png  (all papers if none)
"""
import sys, json, glob, os, colorsys
sys.path.insert(0, 'pipeline')
import pymupdf as fitz, paths
from PIL import Image, ImageDraw, ImageFont
from run import cleaned
out_dir = os.path.join(paths.ROOT, 'out', 'overview'); os.makedirs(out_dir, exist_ok=True)
font = ImageFont.load_default()
index = {paths.paper_id(json.load(open(p))): p for p in paths.paper_files()}
for pid in (sys.argv[1:] or sorted(index)):
    pj = index[pid]
    meta = json.load(open(pj))
    doc = fitz.open(cleaned(paths.raw_pdfs(meta['question_ids'][0])[0]))
    boxes = {}
    for qf in sorted(glob.glob(os.path.join(os.path.dirname(pj), 'q*', '*.json'))):
        q = json.load(open(qf)); qi = q['number']
        def walk(n, lab):
            for s in n.get('segments', []):
                boxes.setdefault(s['page'], []).append((qi, lab, s['bbox'], 'seg'))
            for k in n.get('parts', []):
                walk(k, k.get('path') or lab)
        walk(q, str(qi))
        for f in q.get('figures', []):
            boxes.setdefault(f['page'], []).append((qi, '', f['bbox'], 'fig'))
    pages = sorted(boxes)
    z = 0.62; tiles = []
    for pno in pages:
        page = doc[pno - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(z, z))
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        d = ImageDraw.Draw(im)
        for qi, lab, bb, kind in boxes[pno]:
            r, g, b = colorsys.hsv_to_rgb((qi * 0.17) % 1, 0.9, 0.8)
            c = (int(r * 255), int(g * 255), int(b * 255))
            x0, y0, x1, y1 = [v * z for v in bb]
            if kind == 'fig':
                d.rectangle([x0, y0, x1, y1], outline=(240, 150, 0), width=1)
            else:
                d.rectangle([x0, y0, x1, y1], outline=c, width=2)
                d.text((x1 - 46, y0 + 2), lab[-12:], fill=c, font=font)
        d.text((4, 4), f'p{pno}', fill=(0, 0, 255), font=font)
        tiles.append(im)
    cols = 4; w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (w + 4), rows * (h + 4) + 18), (80, 80, 80))
    ImageDraw.Draw(sheet).text((4, 2), f"{pid}  {meta['paper_code']} {meta['year']}-{meta['session']}  marks {meta['marks_found']}/{meta['total_marks']}", fill=(255, 255, 0), font=font)
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * (w + 4), 18 + (i // cols) * (h + 4)))
    sheet.save(os.path.join(out_dir, pid + '.png'))
    print(pid, len(tiles), sheet.size)
