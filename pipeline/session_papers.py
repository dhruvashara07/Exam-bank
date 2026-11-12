"""Papers of one session as run.py selectors:
    python3 pipeline/session_papers.py 2021-MJ        ->  2021-MJ/11 2021-MJ/12 ...         (physics 0625)
    python3 pipeline/session_papers.py 0607/2021-MJ   ->  0607/2021-MJ/11 0607/2021-MJ/12 ...  (any other syllabus)"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = json.load(open(os.path.join(ROOT, 'raw', 'manifest.json')))
arg = sys.argv[1]
syl, ses = arg.split('/') if '/' in arg else ('0625', arg)
pre = '' if '/' not in arg else f'{syl}/'
sel = {f"{pre}{r.split('/')[1]}/{re.sub(r'^qp_|[.]pdf$', '', r.split('/')[2])}"
       for r in m if r.split('/')[0] == syl and r.split('/')[1] == ses and r.split('/')[2].startswith('qp_')}
# 2002-2009: the manifest holds both the original name (qp_3) and the renamed one (qp_03, old_papers.py):
# build the renamed one only, or every paper is built twice.
# 2008-2009: qp_3 holds 0625/31 and /32 together (split into qp_31, qp_32): skip the combined original too.
sel = {s for s in sel if not (re.search(r'/\d$', s) and any(o != s and re.fullmatch(re.escape(s[:-1]) + r'\d' + s[-1] + '|' + re.escape(s) + r'\d', o) for o in sel))}
print(' '.join(sorted(sel)))
