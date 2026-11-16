"""Side-by-side sheets for Claude's own look (PLAYBOOK 2e, round 28): for each question, OUR mark-scheme table (left)
next to the PRINTED rows it was made from (right), and our question layout next to the printed page part.

    python3 pipeline/ms_compare.py out_prefix <qid> ...      # writes out_prefix_<n>.png, 4 questions per sheet

Every round item and every question with an automatic-check hit is looked at this way before a round is published:
the content checks cannot see a stretched font, a fraction touching a rule or a cut picture; this sheet can.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json

import fitz
from PIL import Image, ImageDraw

import paths
import review_assets as ra
import store

ROOT = paths.ROOT


def printed_rows(rec, dpi=72):
    """The printed mark-scheme rows of the question, stacked (one crop per row unit)."""
    syl, ses, pv = rec['id'].split('_')[0], rec['id'].split('_')[1], rec['id'].split('_')[2]
    fp = os.path.join(ROOT, 'raw', syl, ses[:4] + '-' + ses[4:], f'ms_{pv}.pdf')
    if not os.path.exists(fp):
        return None
    doc = fitz.open(fp)
    seen, ims = set(), []
    for p in rec['parts']:
        for r in p.get('ms', []):
            for u in r['layout']:
                k = (u['src']['page'], tuple(u['src']['box']))
                if k in seen:
                    continue
                seen.add(k)
                pix = doc[u['src']['page'] - 1].get_pixmap(dpi=dpi, clip=fitz.Rect(u['src']['box']))
                ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    if not ims:
        return None
    W = max(i.width for i in ims)
    out = Image.new('RGB', (W, sum(i.height + 4 for i in ims)), (235, 235, 235))
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height + 4
    return out


def pair(qid, width=900, dpi=72):
    ses = qid.split('_')[1]
    rec = json.load(open(os.path.join(paths.store_dir(qid.rsplit('_', 1)[0]), qid.rsplit('_', 1)[1] + '.json')))
    if 'parts' not in rec and rec.get('same_as'):    # stored once for the session (store.py dupes)
        qid = rec['same_as'][0] if isinstance(rec['same_as'], list) else rec['same_as']
        rec = json.load(open(os.path.join(paths.store_dir(qid.rsplit('_', 1)[0]), qid.rsplit('_', 1)[1] + '.json')))
    sv = store.review_svgs(qid, '/tmp/rtmp')
    ours = ra.svg_img(sv['ms'], dpi) if sv.get('ms') else None
    pr = printed_rows(rec, dpi)
    parts = [x for x in (ours, pr) if x is not None]
    if not parts:
        return None
    k = (width / 2 - 6) / max(p.width for p in parts)
    parts = [p.resize((int(p.width * k), int(p.height * k))) for p in parts]
    H = max(p.height for p in parts) + 16
    c = Image.new('RGB', (width, H), 'white')
    x = 0
    for p in parts:
        c.paste(p, (x, 16))
        x += int(width / 2)
    ImageDraw.Draw(c).text((2, 2), qid + '   ours | printed', fill=(200, 0, 0))
    return c


def fig_sheet(out, items):
    """Each diagram crop (red) drawn on its printed page, 3 per row: items 'qid:diagram1'."""
    ims = []
    for it in items:
        qid, suf = it.split(':')
        pid = qid.rsplit('_', 1)[0]
        rec = json.load(open(os.path.join(paths.store_dir(pid), qid.rsplit('_', 1)[1] + '.json')))
        fs = [f for f in rec.get('figures', []) if f['id'].endswith(suf)]
        if not fs:
            continue
        src = fs[0]['source']
        syl, ses, pv = qid.split('_')[0], qid.split('_')[1], qid.split('_')[2]
        doc = fitz.open(os.path.join(ROOT, 'raw', syl, ses[:4] + '-' + ses[4:], f'qp_{pv}.pdf'))
        pg = doc[src['page'] - 1]
        b = fitz.Rect(src['box'])
        clip = (b + (-40, -40, 40, 40)) & pg.rect
        pix = pg.get_pixmap(dpi=90, clip=clip)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        k = 90 / 72
        d = ImageDraw.Draw(im)
        d.rectangle([(b.x0 - clip.x0) * k, (b.y0 - clip.y0) * k, (b.x1 - clip.x0) * k, (b.y1 - clip.y0) * k], outline=(255, 0, 0), width=2)
        d.text((3, 3), it, fill=(0, 0, 255))
        ims.append(im)
    for n in range(0, len(ims), 6):
        g = ims[n:n + 6]
        W, H = max(i.width for i in g), max(i.height for i in g)
        sheet = Image.new('RGB', (3 * W, ((len(g) + 2) // 3) * H), 'white')
        for i, im in enumerate(g):
            sheet.paste(im, ((i % 3) * W, (i // 3) * H))
        sheet.thumbnail((1800, 2400))
        sheet.save(f'{out}_{n // 6}.png')
        print(f'{out}_{n // 6}.png', sheet.size)


if __name__ == '__main__':
    if sys.argv[1] == '--figs':
        fig_sheet(sys.argv[2], sys.argv[3:])
        sys.exit()
    ZOOM = sys.argv[1] == '--zoom'      # one question per image at 2x: for a doubtful detail (thin rules, shading)
    if ZOOM:
        for q in sys.argv[3:]:
            im = pair(q, 1800, 144)
            im.save(f'{sys.argv[2]}_{q}.png'); print(f'{sys.argv[2]}_{q}.png', im.size)
        sys.exit()
    out, ids = sys.argv[1], sys.argv[2:]
    ims = [i for i in (pair(q) for q in ids) if i is not None]
    for n in range(0, len(ims), 4):
        group = ims[n:n + 4]
        g = Image.new('RGB', (900, sum(i.height + 6 for i in group)), (180, 180, 180))
        y = 0
        for i in group:
            g.paste(i, (0, y))
            y += i.height + 6
        g.save(f'{out}_{n // 4}.png')
        print(f'{out}_{n // 4}.png', g.size)
