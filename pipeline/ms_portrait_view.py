"""Picture of a question's mark scheme: landscape original (left) vs portrait version (right).
    python3 pipeline/ms_portrait_view.py <question id> <out path without extension>   -> .png (+ .html)
"""
import sys,os,json,glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store as S, ms_portrait as MP, store_view as V
def render(qid,out):
    q,store=S.load(qid); base='file://'+store
    L,R=[],[]; yl=yr=6; infos=[]; probs=[]
    for p in q['parts']:
        for r in p['ms']:
            for u in r['layout']:
                v,info=MP.portrait_unit(u)
                infos.append(info); pr=MP.check(u,v) if info['mode']=='wrap' else []
                if pr: probs.append((r['label'],pr))
                L.append(S.unit_svg(u,base,0,yl,doc='ms')); yl+=u['h']
                R.append(S.unit_svg(v,base,0,yr,doc='ms')); yr+=v['h']
    h=max(yl,yr)+6
    svl=f'<svg xmlns="http://www.w3.org/2000/svg" width="730" height="{h}" viewBox="0 0 730 {h}">'+''.join(L)+'</svg>'
    svr=f'<svg xmlns="http://www.w3.org/2000/svg" width="530" height="{h}" viewBox="0 0 530 {h}">'+''.join(R)+'</svg>'
    html='<body style="margin:0;background:#ddd;display:flex;gap:14px;padding:8px;align-items:flex-start">'+''.join(f'<div style="background:#fff;width:{w}px">{s}</div>' for w,s in ((730,svl),(530,svr)))
    open(out+'.html','w').write(html)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':600},device_scale_factor=1.5); pg.goto('file://'+out+'.html'); pg.wait_for_timeout(400); pg.screenshot(path=out+'.png',full_page=True); b.close()
    return infos,probs
if __name__=='__main__':
    infos,probs=render(sys.argv[1],sys.argv[2])
    import collections; print(collections.Counter(i['mode'] for i in infos),'problems',probs[:5])
