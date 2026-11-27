"""Chemistry hint (ERROR_PATTERNS 295): the numbers in our MS Marks column should add up to the question's marks.
A mismatch is a HINT, not a fault: Guidance rows, 'max N' and OR alternatives give false hits (C0: 10 of 56 papers' questions,
all matching the print). It found the empty 2005 Marks column in C0.

    python3 pipeline/ms_marksum.py <paper ids>
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

def msum(rec):
    """Sum of the whole numbers in the Marks column of our laid-out MS (header 'Marks' bounds; Total row skipped)."""
    mp=rec.get('ms_p') or {}; rows=mp.get('rows',[])
    if not rows: return None
    hdr=None
    for v in rows:
        for t in v.get('text',[]):
            if t['t']=='Marks' and t.get('b'): hdr=v;break
        if hdr: break
    if not hdr: return None
    mx=next(t for t in hdr['text'] if t['t']=='Marks')
    # column bounds: vertical rules of header
    xs=[]
    for l in hdr.get('lines',[]):
        m=re.findall(r'[\d.]+',l['d'])
        if len(m)>=8:
            a=list(map(float,m)); x0,x1=min(a[0::2]),max(a[0::2])
            if x1-x0<2: xs.append((x0+x1)/2)
    cx=mx['x']+mx['w']/2
    lo=max([x for x in xs if x<cx],default=mx['x']-10); hi=min([x for x in xs if x>cx],default=mx['x']+mx['w']+10)
    s=0
    for v in rows:
        if v is hdr: continue
        tx=v.get('text',[])
        if any(re.match(r'(?i)total',t['t']) for t in tx if t['x']<lo): continue
        for t in tx:
            c=t['x']+t['w']/2
            if lo<c<hi and re.fullmatch(r'\d{1,2}',t['t']): s+=int(t['t'])
    return s


def hits(pid):
    out = []
    for f in sorted(glob.glob(os.path.join(paths.store_dir(pid), 'q*.json'))):
        r = json.load(open(f))
        if r.get('stub') or r.get('answer'):
            continue
        s = msum(r)
        if s is not None and s != r.get('marks'):
            out.append({'id': r['id'], 'kind': 'ms_marksum',
                        'detail': f"Marks column adds up to {s}, question has {r.get('marks')} (hint: Guidance / max / OR rows give false hits)"})
    return out


if __name__ == '__main__':
    for pid in sys.argv[1:]:
        for h in hits(pid):
            print(h['id'], h['detail'])
