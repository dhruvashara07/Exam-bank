"""Picture of a question's mark scheme in portrait (one table, header once at the top); with --both also the landscape original.
    python3 pipeline/ms_portrait_view.py <question id> <out path without extension> [--both]   -> .png (+ .html)
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store as S, ms_portrait as MP

def render(qid, out, both=False):
    q, store = S.load(qid); base = 'file://' + store
    sizes = {f['id']: tuple(f['size_pt']) for f in q['figures']}
    figs = {f['id']: f for f in q['figures']}
    rows = [(r, u) for p in q['parts'] for r in p['ms'] for u in r['layout']]
    units = [u for r, u in rows]
    widths = MP.column_widths(units)
    L, R, infos, probs, first_info = [], [], [], [], None
    yl = yr = 6
    res = []
    for r, u in rows:
        v, info = MP.portrait_unit(u, widths=widths, sizes=sizes)
        res.append((u, v, info))
        if info['mode'] == 'wrap' and first_info is None:
            first_info = info
    try:
        hdr = json.load(open(os.path.join(store, 'ms_header.json')))
    except Exception:
        hdr = None
    if hdr and first_info:
        hv = MP.portrait_header(hdr, first_info)
        R.append(S.unit_svg(hv, base, 0, yr, doc='ms')); yr += hv['h']
    for u, v, info in res:
        infos.append(info)
        pr = MP.check(u, v) if info['mode'] == 'wrap' else []
        if pr: probs.append((u['src']['page'], pr))
        L.append(S.unit_svg(u, base, 0, yl, doc='ms', figs=figs)); yl += u['h']
        R.append(S.unit_svg(v, base, 0, yr, doc='ms', figs=figs)); yr += v['h']
    h = max(yl, yr) + 6
    svl = f'<svg xmlns="http://www.w3.org/2000/svg" width="730" height="{h}" viewBox="0 0 730 {h}">' + ''.join(L) + '</svg>'
    svr = f'<svg xmlns="http://www.w3.org/2000/svg" width="530" height="{h}" viewBox="0 0 530 {h}">' + ''.join(R) + '</svg>'
    panels = ((730, svl), (530, svr)) if both else ((530, svr),)
    html = '<body style="margin:0;background:#ddd;display:flex;gap:14px;padding:8px;align-items:flex-start">' + ''.join(
        f'<div style="background:#fff;width:{w}px">{sv}</div>' for w, sv in panels)
    open(out + '.html', 'w').write(html)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1300 if both else 560, 'height': 600}, device_scale_factor=1.5)
        pg.goto('file://' + os.path.abspath(out + '.html')); pg.wait_for_timeout(400)
        pg.screenshot(path=out + '.png', full_page=True); b.close()
    return infos, probs, widths

if __name__ == '__main__':
    infos, probs, widths = render(sys.argv[1], sys.argv[2], '--both' in sys.argv)
    print(collections.Counter(i['mode'] for i in infos), 'widths', {k: round(v) for k, v in widths.items()}, 'problems', probs[:4])
