"""Make preview images and an item list for the phone review page.

For each review item:  orig.jpg  (source page(s) with detected segments boxed)
                       q.jpg     (rebuilt question from its SVG pieces)
                       ms.jpg    (mark scheme pieces, structured papers)
                       figs.jpg  (each cropped figure, stacked)
Usage: python3 pipeline/review_assets.py OUT_DIR [sample_per_paper_type]
"""
import json, os, sys, random, io
import pymupdf as fitz
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from run import cleaned, ROOT
import paths

COLORS = [(31, 95, 139), (200, 90, 20), (30, 140, 80), (150, 50, 160), (180, 40, 60), (90, 90, 90)]


_BROWSER = {}


def svg_img(path, dpi=96):
    """Rasterise an SVG with Chromium, i.e. exactly as a browser shows it.
    (MuPDF's SVG reader ignores stroke-dasharray, which made dashed lines look solid.)"""
    import re
    if 'page' not in _BROWSER:
        from playwright.sync_api import sync_playwright
        _BROWSER['pw'] = sync_playwright().start()
        _BROWSER['b'] = _BROWSER['pw'].chromium.launch()
    full = os.path.join(ROOT, path)
    head = open(full).read(600)
    w = float(re.search(r'width="([\d.]+)', head).group(1)); h = float(re.search(r'height="([\d.]+)', head).group(1))
    key = round(dpi)
    if _BROWSER.get('dpi') != key:
        if 'page' in _BROWSER:
            _BROWSER['page'].close()
        _BROWSER['page'] = _BROWSER['b'].new_page(device_scale_factor=dpi / 72)
        _BROWSER['dpi'] = key
    pg = _BROWSER['page']
    pg.set_viewport_size({'width': max(1, int(w + 0.999)), 'height': max(1, int(h + 0.999))})
    pg.goto('file://' + full)
    return Image.open(io.BytesIO(pg.screenshot())).convert('RGB')


def stack(imgs, sep=(225, 70, 70), gap=5):
    imgs = [i for i in imgs if i]
    if not imgs:
        return None
    W = max(i.width for i in imgs); H = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    m = Image.new('RGB', (W, H), sep); y = 0
    for i in imgs:
        m.paste(i, (0, y)); y += i.height + gap
    return m


def walk(node, path=''):
    """(label path, segment) pairs in print order."""
    out = [(path or 'stem', s) for s in node.get('segments', [])]
    for k in node.get('parts', []):
        out += walk(k, (path + '-' if path else '') + k['label'])
    return out


def ms_segs(node):
    res = []
    for m in node.get('mark_scheme', []):
        res += m['segments']
    for k in node.get('parts', []):
        res += ms_segs(k)
    return res


def outline(node, depth=0):
    rows = []
    for k in node.get('parts', []):
        sp = [s['answer_space']['kind'] for s in k.get('segments', [])]
        rows.append({'label': k.get('path', k['label']), 'marks': k.get('marks', 0), 'space': sp[-1] if sp else '',
                     'ms': bool(k.get('mark_scheme')), 'depth': depth})
        rows += outline(k, depth + 1)
    return rows


def original(q, qp_path, dpi=72):
    doc = fitz.open(cleaned(qp_path))
    segs = walk(q)
    pages = sorted({s['page'] for _, s in segs} | {f['page'] for f in q['figures']})
    labels = sorted({lab for lab, _ in segs})
    imgs = []
    for p in pages:
        pix = doc[p - 1].get_pixmap(dpi=dpi)
        im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
        dr = ImageDraw.Draw(im, 'RGBA'); k = dpi / 72
        for lab, s in segs:
            if s['page'] != p:
                continue
            c = COLORS[labels.index(lab) % len(COLORS)]
            x0, y0, x1, y1 = [v * k for v in s['bbox']]
            dr.rectangle([x0, y0, x1, y1], outline=c + (255,), width=2, fill=c + (18,))
            dr.text((x1 - 60, y0 + 2), lab, fill=c + (255,))
        for f in q['figures']:
            if f['page'] == p:
                x0, y0, x1, y1 = [v * k for v in f['bbox']]
                dr.rectangle([x0, y0, x1, y1], outline=(230, 160, 0, 255), width=2)
        imgs.append(im)
    return stack(imgs, sep=(60, 60, 60), gap=8)


def build(out_dir, per_type=6, seed=7):
    os.makedirs(out_dir, exist_ok=True)
    queue = json.load(open(os.path.join(ROOT, 'review', 'queue.json')))
    flagged = {x['id']: x['reasons'] for x in queue if '_q' in x['id']}
    byid = {os.path.basename(f)[:-5]: f for f in paths.question_files()}
    rnd = random.Random(seed)
    sample = []
    for ptype in '123456':
        pool = [i for i, f in byid.items() if i.split('_')[2][0] == ptype and i not in flagged]
        sample += rnd.sample(pool, per_type)
    items = [(i, 'flagged') for i in sorted(flagged)] + [(i, 'sample') for i in sorted(sample)]
    return render_items(out_dir, items, flagged, byid)


def render_items(out_dir, items, reasons, byid=None):
    """items: [(question id, group)]; reasons: {id: [text]} shown on the card."""
    os.makedirs(out_dir, exist_ok=True)
    byid = byid or {os.path.basename(f)[:-5]: f for f in paths.question_files()}
    flagged = reasons
    out = []
    for qid, group in items:
        q = json.load(open(byid[qid]))
        qp_path = paths.raw_pdfs(qid)[0]
        d = os.path.join(out_dir, qid); os.makedirs(d, exist_ok=True)
        imgs = {}
        def save(name, im, width=900):
            if im is None:
                return
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(os.path.join(d, name), quality=72, optimize=True)
            imgs[name.split('.')[0]] = f'{qid}/{name}'
        save('q.jpg', stack([svg_img(s['svg']['file']) for _, s in walk(q)]))
        save('orig.jpg', original(q, qp_path))
        if q['type'] != 'mcq':
            save('ms.jpg', stack([svg_img(s['svg']['file'], 72) for s in ms_segs(q)]), width=1000)
        if q['figures']:
            save('figs.jpg', stack([svg_img(f['svg']['file']) for f in q['figures']], sep=(230, 160, 0), gap=6))
        out.append({
            'id': qid, 'group': group, 'reasons': flagged.get(qid, []),
            'paper': q['paper_code'], 'session': f"{q['season']} {q['year']}", 'number': q['number'],
            'type': q['type'], 'marks': q['marks'], 'answer': q.get('answer'),
            'options': q.get('options', []), 'parts': outline(q),
            'figures': [{'id': f['id'], 'caption': f.get('caption')} for f in q['figures']],
            'images': imgs,
        })
        print(qid, group, list(imgs))
    json.dump(out, open(os.path.join(out_dir, 'items.json'), 'w'), ensure_ascii=False)
    return out


if __name__ == '__main__':
    build(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 6)
