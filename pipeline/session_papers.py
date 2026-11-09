"""Papers of one session as run.py selectors:  python3 pipeline/session_papers.py 2021-MJ  ->  2021-MJ/11 2021-MJ/12 ..."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = json.load(open(os.path.join(ROOT, 'raw', 'manifest.json')))
ses = sys.argv[1]
sel = {f"{r.split('/')[1]}/{re.sub(r'^qp_|[.]pdf$', '', r.split('/')[2])}"
       for r in m if r.split('/')[1] == ses and r.split('/')[2].startswith('qp_')}
# 2002-2009: the manifest holds both the original name (qp_3) and the renamed one (qp_03, old_papers.py):
# build the renamed one only, or every paper is built twice.
sel = {s for s in sel if not (re.search(r'/\d$', s) and re.sub(r'/(\d)$', r'/0\1', s) in sel)}
print(' '.join(sorted(sel)))
