"""Papers of one session as run.py selectors:  python3 pipeline/session_papers.py 2021-MJ  ->  2021-MJ/11 2021-MJ/12 ..."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = json.load(open(os.path.join(ROOT, 'raw', 'manifest.json')))
ses = sys.argv[1]
print(' '.join(sorted({f"{r.split('/')[1]}/{re.sub(r'^qp_|[.]pdf$', '', r.split('/')[2])}"
                       for r in m if r.split('/')[1] == ses and r.split('/')[2].startswith('qp_')})))
