"""Pictures of stored questions in the two v5 views (examples for approval; later the review page):

    python3 pipeline/store_view.py <out_dir> <question id>[:<part>[,<part>]] ...
        -> <id>_bank.png   question-bank view: working space and full dotted answer lines removed, gaps closed,
                           question number = N (here the position in the list), Fig/Table numbered N.k
           <id>_print.png  print view: the full Cambridge layout (same numbers)
    selection = <id>[:<part>[,<part>]]   e.g. 0625_2014MJ_53_q01:b-ii   (stems of the parts are printed too)
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import store as S
import renumber as RN

GREY = '#8a8a8a'


def question_svg(qid, view, number=None, sel=None, ms=False, relabel=False):
    """(svg text, width pt, height pt) of one question (or the selected parts) stacked as one continuous page."""
    q, store = S.load(qid)
    if q.get('stub'):
        q, store = S.load(q['same_as'][0])
    figs = {f['id']: f for f in q['figures']}
    parts = S.chosen(q, sel or [])
    plan = RN.make_plan(q, parts, number or q['number'], relabel_parts=relabel)
    base = 'file://' + store
    X0 = 20.0                                         # Cambridge's left margin is 30 pt: show it at 10
    y = 6.0
    o = []
    src = f"{q['paper']['code']} {q['paper']['session']} Q{q['number']}" + (f" {','.join(sel)}" if sel else '')
    o.append(f'<text x="10" y="{y + 8}" font-family="{S.CSS_FAM["sans"]}" font-size="7.5" fill="{GREY}">{src}</text>')
    o.append(f'<text x="560" y="{y + 8}" font-family="{S.CSS_FAM["sans"]}" font-size="7.5" fill="{GREY}" text-anchor="end">'
             f'{view} view</text>')
    y += 14
    first = True
    for p in parts:
        for ui, u in enumerate(p['layout']):
            h = S.view_height(u, view)
            o.append(S.unit_svg(u, base, u['src']['box'][0] - X0, y, drop_total=bool(sel), figs=figs, view=view, plan=plan,
                                meta={'path': p['path'], 'first': ui == 0}))
            y += h
    if ms:
        y += 10
        o.append(f'<line x1="10" x2="560" y1="{y}" y2="{y}" stroke="#bbb" stroke-width=".6"/>')
        o.append(f'<text x="10" y="{y + 12}" font-family="{S.CSS_FAM["sans"]}" font-size="9" font-weight="bold" fill="{GREY}">Mark scheme</text>')
        y += 18
        if q.get('answer'):
            o.append(f'<text x="10" y="{y + 10}" font-family="{S.CSS_FAM["sans"]}" font-size="11">Answer: <tspan font-weight="bold">{q["answer"]}</tspan></text>')
            y += 18
        done = set()
        for p in parts:
            for r in p['ms']:
                for u in r['layout']:
                    if (u['src']['page'], tuple(u['src']['box'])) in done:
                        continue
                    done.add((u['src']['page'], tuple(u['src']['box'])))
                    o.append(S.unit_svg(u, base, u['src']['box'][0] - X0, y, plan=plan, doc='ms'))
                    y += u['h']
    if plan['flags']:
        o.append(f'<text x="10" y="{y + 12}" font-family="{S.CSS_FAM["sans"]}" font-size="7.5" fill="#b00">'
                 f'numbering flags: {"; ".join(sorted({f"{a} {b}" for a, b in plan["flags"]}))}</text>')
        y += 16
    y += 8
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="570" height="{y:.1f}" viewBox="0 0 570 {y:.1f}">' + '\n'.join(o) + '</svg>', 570, y


def shot(svgs, out_png, width=900, scale=2):
    """svgs: list of svg strings placed side by side; one PNG (Chromium, as a browser shows it)."""
    from playwright.sync_api import sync_playwright
    html = ['<!doctype html><body style="margin:0;background:#e9e9e9;display:flex;gap:16px;padding:12px;align-items:flex-start">']
    for s in svgs:
        sv = s.replace('<svg ', '<svg style="width:100%;height:auto;display:block" ', 1)
        html.append('<div style="background:#fff;box-shadow:0 0 4px #999;width:%dpx">%s</div>' % (width // len(svgs) - 20, sv))
    tmp = out_png[:-4] + '.html'
    open(tmp, 'w').write('\n'.join(html))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': width, 'height': 600}, device_scale_factor=scale)
        pg.goto('file://' + os.path.abspath(tmp))
        pg.wait_for_timeout(500)
        pg.screenshot(path=out_png, full_page=True)
        b.close()
    os.remove(tmp)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, spec in enumerate(sys.argv[2:], 1):
        qid, _, ps = spec.partition(':')
        sel = [s for s in ps.split(',') if s]
        name = qid + (('_' + ps.replace(',', '+')) if ps else '')
        bank, _, _ = question_svg(qid, 'bank', n, sel, ms=True)
        prt, _, _ = question_svg(qid, 'print', n, sel, ms=True)
        shot([bank, prt], os.path.join(out, name + '_bank_vs_print.png'), width=1500)
        print(name, 'ok')
