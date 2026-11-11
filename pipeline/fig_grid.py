"""Original page around a figure crop, crop box in red: python3 pipeline/fig_grid.py out.png <qid>:<fig id suffix> ..."""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf as f, PIL.Image as I, PIL.ImageDraw as D
from run import cleaned
tiles = []
for a in sys.argv[2:]:
    qid, suf = a.split(':')
    q = json.load(open(glob.glob(f'bank/**/{qid}.json', recursive=True)[0]))
    g = [x for x in q['figures'] if x['id'].endswith(suf)][0]; b = g['bbox']
    ses = q['id'].split('_')[1]; ses = ses[:4] + '-' + ses[4:]; pv = q['id'].split('_')[2]
    p = f.open(cleaned(f'raw/0625/{ses}/qp_{pv}.pdf'))[g['page'] - 1]
    clip = f.Rect(max(0, b[0] - 30), max(0, b[1] - 40), min(p.rect.width, b[2] + 30), min(p.rect.height, b[3] + 15))
    pm = p.get_pixmap(dpi=50, clip=clip); im = I.frombytes('RGB', (pm.width, pm.height), pm.samples); s = 50 / 72
    D.Draw(im).rectangle([(b[0] - clip.x0) * s, (b[1] - clip.y0) * s, (b[2] - clip.x0) * s, (b[3] - clip.y0) * s], outline=(255, 0, 0), width=2)
    tiles.append(im)
cols = 3; W = max(t.width for t in tiles)
rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
out = I.new('RGB', (W * cols + 20, sum(max(t.height for t in r) + 6 for r in rows)), 'white'); y = 0
for r in rows:
    for k, t in enumerate(r): out.paste(t, (k * (W + 6), y))
    y += max(t.height for t in r) + 6
out.save(sys.argv[1]); print(out.size)
