"""EXPERIMENT (not part of the pipeline): can a page be rebuilt from layout data + figure SVGs only?

    python3 pipeline/experiments/layout_rebuild.py 2024-MJ/42 [--pages 2-6] [--out out/layout_test]

For every page of the question paper and the mark scheme it stores
    layout.json   text spans (text, x, baseline, width, size, family, bold/italic, colour), vector lines/boxes
                  (as SVG path data), raster images (as files) and figure boxes
    figure SVGs   only the captioned / MCQ figure crops the bank already has (copied)
then rebuilds each page as SVG from those files alone, renders it with Chromium, and compares it with the
original page (missing / extra ink within 1.5 pt). Writes compare_<doc>_p<n>.png (original | rebuilt | diff).
"""
import glob, gzip, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pymupdf as fitz
import numpy as np
from PIL import Image
import paths
from run import cleaned

FAMILY = [('symbol', 'DejaVu Sans'), ('times', 'Liberation Serif'), ('serif', 'Liberation Serif'),
          ('courier', 'Liberation Mono'), ('mono', 'Liberation Mono')]


SYMBOL = dict(zip(
    'ABGDEFHIJKLMNOPQRSTUVWXYZabgdefhijklmnopqrstuvwxyz',
    'ΑΒΓΔΕΦΗΙϑΚΛΜΝΟΠΘΡΣΤΥςΩΞΨΖαβγδεφηιϕκλμνοπθρστυϖωξψζ'))
SYMBOL.update({'G': 'Γ', 'C': 'Χ', 'c': 'χ', 'g': 'γ'})
SYMBOL_HI = {0xB0: '°', 0xB1: '±', 0xB4: '×', 0xB8: '÷', 0xB9: '≠', 0xBA: '≡', 0xBB: '≈', 0xA3: '≤', 0xB3: '≥',
             0xAE: '→', 0xAC: '←', 0xAD: '↑', 0xAF: '↓', 0xAB: '↔', 0xD6: '√', 0xB5: '∝', 0xA5: '∞', 0x2D: '−',
             0xD7: '·', 0xA2: '′', 0xB2: '″', 0xE5: '∑', 0xF2: '∫', 0xB6: '∂', 0x27: '∋', 0x60: '‾', 0xBC: '…'}


def unpua(ch):
    """Symbol-font characters arrive as private-use codes (U+F0xx): map them to real Unicode."""
    o = ord(ch)
    if 0xF020 <= o <= 0xF0FF:
        o -= 0xF000
        if o in SYMBOL_HI:
            return SYMBOL_HI[o]
        c = chr(o)
        return SYMBOL.get(c, c)
    return ch


def family(font):
    f = font.lower()
    for k, v in FAMILY:
        if k in f:
            return v
    return 'Liberation Sans'          # Arial, Helvetica, Verdana, Calibri, AllAndNone (Cambridge's hidden subset)


def hexcol(c):
    if c is None:
        return None
    if isinstance(c, int):
        return '#%06x' % c
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in c[:3])


def inside(r, boxes, tol=1.5):
    return any(r.x0 >= b.x0 - tol and r.y0 >= b.y0 - tol and r.x1 <= b.x1 + tol and r.y1 <= b.y1 + tol for b in boxes)


def path_d(items):
    d = []
    cur = None
    for it in items:
        k = it[0]
        if k == 'l':
            a, b = it[1], it[2]
            if cur is None or abs(cur.x - a.x) > .01 or abs(cur.y - a.y) > .01:
                d.append(f'M{a.x:.2f} {a.y:.2f}')
            d.append(f'L{b.x:.2f} {b.y:.2f}'); cur = b
        elif k == 'c':
            a, c1, c2, b = it[1:5]
            if cur is None or abs(cur.x - a.x) > .01 or abs(cur.y - a.y) > .01:
                d.append(f'M{a.x:.2f} {a.y:.2f}')
            d.append(f'C{c1.x:.2f} {c1.y:.2f} {c2.x:.2f} {c2.y:.2f} {b.x:.2f} {b.y:.2f}'); cur = b
        elif k == 're':
            r = it[1]
            d.append(f'M{r.x0:.2f} {r.y0:.2f}H{r.x1:.2f}V{r.y1:.2f}H{r.x0:.2f}Z'); cur = None
        elif k == 'qu':
            q = it[1]
            d.append(f'M{q.ul.x:.2f} {q.ul.y:.2f}L{q.ur.x:.2f} {q.ur.y:.2f}L{q.lr.x:.2f} {q.lr.y:.2f}L{q.ll.x:.2f} {q.ll.y:.2f}Z'); cur = None
    return ''.join(d)


def span_len(chars, d):
    """Length of the text along its writing direction (horizontal or rotated lines)."""
    ox, oy = chars[0]['origin']
    ends = []
    for c in (chars[0], chars[-1]):
        x0, y0, x1, y1 = c['bbox']
        ends += [(x - ox) * d[0] + (y - oy) * d[1] for x in (x0, x1) for y in (y0, y1)]
    return max(ends)


def extract_page(page, fig_boxes, img_dir, tag):
    W, H = page.mediabox.width, page.mediabox.height          # content coordinates (unrotated)
    out = {'w': round(page.rect.width, 2), 'h': round(page.rect.height, 2), 'text': [], 'paths': [], 'images': [], 'figures': []}
    if page.rotation:
        m = page.rotation_matrix
        out['rot'] = [round(v, 3) for v in (m.a, m.b, m.c, m.d, m.e, m.f)]
    # text: one record per span, trimmed to its first/last printed character
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            if abs(l['dir'][1]) > 0.01:
                vert = True
            else:
                vert = False
            for s in l['spans']:
                runs, cur = [], []
                for c in s['chars']:
                    if c['c'].strip():
                        cur.append(c)
                    elif cur:
                        runs.append(cur); cur = []
                if cur:
                    runs.append(cur)
                font = s['font']
                bold = bool(s['flags'] & 16) or 'bold' in font.lower()
                italic = bool(s['flags'] & 2) or 'italic' in font.lower() or 'oblique' in font.lower()
                col = hexcol(s['color'])
                for chars in runs:                 # one record per word: spacing between words stays exact
                    r = fitz.Rect(chars[0]['bbox'][0], s['bbox'][1], chars[-1]['bbox'][2], s['bbox'][3])
                    if vert:
                        r = fitz.Rect(s['bbox'])
                    if inside(r, fig_boxes) or r.y1 < 0 or r.y0 > H or r.x1 < 0 or r.x0 > W:
                        continue
                    rec = {'t': ''.join(unpua(c['c']) for c in chars), 'x': round(chars[0]['origin'][0], 2),
                           'y': round(chars[0]['origin'][1], 2), 'w': round(span_len(chars, l['dir']), 2),
                           's': round(s['size'], 2), 'f': family(font)}
                    if bold: rec['b'] = 1
                    if italic: rec['i'] = 1
                    if col != '#000000': rec['c'] = col
                    if vert: rec['dir'] = [round(v, 3) for v in l['dir']]
                    out['text'].append(rec)
    # vector drawings outside the figures
    for dr in page.get_drawings():
        r = dr['rect']
        if inside(r, fig_boxes):
            continue
        fill, stroke = hexcol(dr.get('fill')), hexcol(dr.get('color'))
        if dr.get('fill_opacity') == 0: fill = None
        if dr.get('stroke_opacity') == 0: stroke = None
        if fill is None and stroke is None:
            continue
        rec = {'d': path_d(dr['items'])}
        if not rec['d']:
            continue
        if fill: rec['fill'] = fill
        if dr.get('even_odd'): rec['eo'] = 1
        if stroke and dr['type'] in ('s', 'fs'):
            rec['stroke'] = stroke; rec['sw'] = round(dr.get('width') or 1, 2)
            if dr.get('dashes') and dr['dashes'] not in ('[] 0', '[ ] 0'):
                m = re.match(r'\[([^\]]*)\]', dr['dashes'])
                if m and m.group(1).strip():
                    rec['dash'] = m.group(1).strip()
            if dr.get('lineCap'): rec['cap'] = max(dr['lineCap']) if isinstance(dr['lineCap'], (list, tuple)) else dr['lineCap']
        if dr['type'] == 'f':
            rec.pop('stroke', None)
        out['paths'].append(rec)
    # raster images (logos etc.)
    for k, info in enumerate(page.get_image_info(xrefs=True)):
        r = fitz.Rect(info['bbox'])
        if inside(r, fig_boxes) or not info.get('xref'):
            continue
        pix = fitz.Pixmap(page.parent, info['xref'])
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        name = f'{tag}_img{k}.png'
        pix.save(os.path.join(img_dir, name))
        out['images'].append({'file': name, 'bbox': [round(v, 2) for v in r]})
    return out


def page_svg(lay, fig_dir_rel):
    W, H = lay['w'], lay['h']
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>']
    if lay.get('rot'):
        o.append('<g transform="matrix(%s)">' % ' '.join(map(str, lay['rot'])))
    for p in lay['paths']:
        a = [f'd="{p["d"]}"', f'fill="{p.get("fill", "none")}"']
        if p.get('eo'): a.append('fill-rule="evenodd"')
        if p.get('stroke'):
            a += [f'stroke="{p["stroke"]}"', f'stroke-width="{p["sw"]}"']
            if p.get('dash'): a.append(f'stroke-dasharray="{p["dash"]}"')
            cap = {1: 'round', 2: 'square'}.get(p.get('cap'))
            if cap: a.append(f'stroke-linecap="{cap}"')
        o.append(f'<path {" ".join(a)}/>')
    for im in lay['images']:
        x0, y0, x1, y1 = im['bbox']
        o.append(f'<image href="{im["file"]}" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" preserveAspectRatio="none"/>')
    for f in lay['figures']:
        x0, y0, x1, y1 = f['bbox']
        o.append(f'<image href="{fig_dir_rel}/{f["file"]}" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>')
    for t in lay['text']:
        esc = t['t'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        a = [f'x="{t["x"]}"', f'y="{t["y"]}"', f'font-family="{t["f"]}"', f'font-size="{t["s"]}"']
        if t.get('b'): a.append('font-weight="bold"')
        if t.get('i'): a.append('font-style="italic"')
        if t.get('c'): a.append(f'fill="{t["c"]}"')
        if len(t['t']) > 1 and t['w'] > 0:
            a.append(f'textLength="{t["w"]}" lengthAdjust="spacingAndGlyphs"')
        if t.get('dir'):
            import math
            ang = math.degrees(math.atan2(t['dir'][1], t['dir'][0]))
            a.append(f'transform="rotate({ang:.1f} {t["x"]} {t["y"]})"')
        o.append(f'<text {" ".join(a)} xml:space="preserve">{esc}</text>')
    if lay.get('rot'):
        o.append('</g>')
    o.append('</svg>')
    return '\n'.join(o)


def ink(a):
    return a < 160


def compare(orig_png, rebuilt_png, out_png):
    a = np.asarray(Image.open(orig_png).convert('L'), dtype=np.int16)
    b = np.asarray(Image.open(rebuilt_png).convert('L').resize((a.shape[1], a.shape[0])), dtype=np.int16)
    A, B = ink(a), ink(b)
    def dil(m, r=3):
        out = m.copy()
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
        return out
    missing = A & ~dil(B)
    extra = B & ~dil(A)
    vis = np.full(a.shape + (3,), 255, np.uint8)
    vis[A] = (170, 170, 170)
    vis[missing] = (220, 0, 0)
    vis[extra] = (0, 90, 220)
    trio = np.concatenate([np.stack([a] * 3, -1).astype(np.uint8), np.stack([b] * 3, -1).astype(np.uint8), vis], 1)
    Image.fromarray(trio).save(out_png, optimize=True)
    return int(A.sum()), int(missing.sum()), int(extra.sum())


SHOT = r"""
const { chromium } = require('playwright');
(async () => {
  const jobs = JSON.parse(require('fs').readFileSync(process.argv[2]));
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 2 });
  for (const [svg, png, w, h] of jobs) {
    await p.setViewportSize({ width: Math.ceil(w), height: Math.ceil(h) });
    await p.goto('file://' + svg); await p.waitForTimeout(150);
    await p.screenshot({ path: png, clip: { x: 0, y: 0, width: w, height: h } });
  }
  await b.close();
})();
"""


def flat(src):
    """Bake page rotation in (mark schemes are rotated landscape pages), so all coordinates agree."""
    if not any(p.rotation for p in src):
        return src
    out = fitz.open()
    for i, p in enumerate(src):
        np_ = out.new_page(width=p.rect.width, height=p.rect.height)
        np_.show_pdf_page(np_.rect, src, i, rotate=-p.rotation)
    return out


def main():
    a = sys.argv[1:]
    sel = a[0]                                 # e.g. 2024-MJ/42
    out = 'out/layout_test'
    if '--out' in a:
        out = a[a.index('--out') + 1]
    sess, pv = sel.split('/')
    out = os.path.join(paths.ROOT, out, sel.replace('/', '_'))
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'figures')); os.makedirs(os.path.join(out, 'render'))
    qp = os.path.join(paths.ROOT, 'raw', '0625', sess, f'qp_{pv}.pdf')
    ms = os.path.join(paths.ROOT, 'raw', '0625', sess, f'ms_{pv}.pdf')
    pdir = glob.glob(os.path.join(paths.ROOT, 'bank', '*', '*', sess, f'p{pv}'))[0]
    figs = {}
    for qf in glob.glob(os.path.join(pdir, 'q*', '*.json')):
        q = json.load(open(qf))
        for f in q.get('figures', []):
            src = os.path.join(paths.ROOT, f['svg']['file'])
            shutil.copy(src, os.path.join(out, 'figures'))
            figs.setdefault(f['page'], []).append({'file': os.path.basename(src), 'bbox': f['bbox']})
    layout, jobs, sizes = {}, [], {'layout_json': 0, 'images': 0}
    for kind, path in (('qp', cleaned(qp)), ('ms', ms)):
        doc = fitz.open(path)
        for i in range(1, len(doc)):                      # page 1 = cover
            fb = figs.get(i + 1, []) if kind == 'qp' else []
            lay = extract_page(doc[i], [fitz.Rect(f['bbox']) for f in fb], out, f'{kind}{i + 1}')
            lay['figures'] = fb
            layout[f'{kind}_p{i + 1}'] = lay
            svg = os.path.join(out, f'{kind}_p{i + 1}.svg')
            open(svg, 'w').write(page_svg(lay, 'figures'))
            orig = os.path.join(out, 'render', f'{kind}_p{i + 1}_orig.png')
            doc[i].get_pixmap(matrix=fitz.Matrix(2, 2), colorspace=fitz.csGRAY).save(orig)
            jobs.append([svg, os.path.join(out, 'render', f'{kind}_p{i + 1}_rebuilt.png'), lay['w'], lay['h']])
    js = json.dumps(layout, ensure_ascii=False, separators=(',', ':'))
    open(os.path.join(out, 'layout.json'), 'w').write(js)
    sizes['layout_json'] = len(js.encode()); sizes['layout_json_gz'] = len(gzip.compress(js.encode()))
    sizes['images'] = sum(os.path.getsize(f) for f in glob.glob(os.path.join(out, '*.png')))
    sizes['figures'] = sum(os.path.getsize(f) for f in glob.glob(os.path.join(out, 'figures', '*.svg')))
    sizes['figures_gz'] = sum(len(gzip.compress(open(f, 'rb').read())) for f in glob.glob(os.path.join(out, 'figures', '*.svg')))
    cur = [f for f in glob.glob(os.path.join(pdir, 'q*', '*', '*.svg'))]
    sizes['current_svgs'] = sum(os.path.getsize(f) for f in cur); sizes['current_svg_files'] = len(cur)
    sizes['current_svgs_gz'] = sum(len(gzip.compress(open(f, 'rb').read())) for f in cur)
    jf = os.path.join(out, 'jobs.json'); json.dump(jobs, open(jf, 'w'))
    sf = os.path.join(out, 'shot.js'); open(sf, 'w').write(SHOT)
    subprocess.run(['node', sf, jf], check=True, cwd=paths.ROOT)
    report = []
    for svg, png, w, h in jobs:
        key = os.path.basename(svg)[:-4]
        orig = os.path.join(out, 'render', f'{key}_orig.png')
        inkpx, miss, extra = compare(orig, png, os.path.join(out, f'compare_{key}.png'))
        report.append({'page': key, 'ink_px': inkpx, 'missing_px': miss, 'extra_px': extra,
                       'missing_pct': round(100 * miss / max(inkpx, 1), 2), 'extra_pct': round(100 * extra / max(inkpx, 1), 2)})
    json.dump({'sizes': sizes, 'pages': report}, open(os.path.join(out, 'report.json'), 'w'), indent=1)
    print(json.dumps(sizes))
    for r in report:
        print(f"{r['page']:8s} ink {r['ink_px']:7d}  missing {r['missing_pct']:5.2f}%  extra {r['extra_pct']:5.2f}%")


if __name__ == '__main__':
    main()
