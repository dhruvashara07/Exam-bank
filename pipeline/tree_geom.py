"""Branch geometry of the probability tree(s) printed in a question paper, for ms_graphs tree specs (Dhruv round 40:
an MS tree has the same structure and angles as the question's tree).

    python3 pipeline/tree_geom.py raw/0607/2019-ON/qp_31.pdf
prints (x0, x1, x2, x3, rise1, rise2, off, page): first branches from x0 to x1 rising rise1, second branches from x2 to x3
rising rise2, each second tree moved off further out than the end of its first branch. Paste the first 7 into
SPECS[...]['tree']['geom'] (ms_graphs.TREE_GEOM)."""
import sys
import pymupdf
def segs(page):
    out=[]
    for d in page.get_drawings():
        for it in d['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if a.x>b.x: a,b=b,a
                if b.x-a.x>15 and abs(b.y-a.y)>3: out.append((a.x,a.y,b.x,b.y))
    return out
def trees(page):
    S=segs(page); res=[]
    near=lambda p,q: abs(p[0]-q[0])<2.5 and abs(p[1]-q[1])<2.5
    for s in S:
        for t in S:
            if s is t or not near(s[:2],t[:2]) or not (s[3]<s[1] and t[3]>t[1]): continue
            # second level from each end: pairs starting right of end, same y
            sec=[]
            for e in ((s[2],s[3]),(t[2],t[3])):
                c=[u for u in S if u[0]>e[0]+5 and abs(u[1]-e[1])<45 and u[0]-e[0]<200]
                up=[u for u in c if u[3]<u[1]]; dn=[u for u in c if u[3]>u[1]]
                if up and dn: sec.append((min(up,key=lambda u:u[0]),min(dn,key=lambda u:u[0])))
            if len(sec)==2:
                u=sec[0][0]; v=sec[1][0]
                off=((t[3]-s[3]) and ((s[3]-u[1]) + (v[1]-t[3]))/2)
                res.append((round(s[0],1),round(s[2],1),round(u[0],1),round(u[2],1),round(s[1]-s[3],1),round(u[1]-u[3],1),round(off,1),page.number))
    return res
if __name__=='__main__':
    for f in sys.argv[1:]:
        d=pymupdf.open(f)
        for p in d:
            for r in trees(p): print(f, r)
