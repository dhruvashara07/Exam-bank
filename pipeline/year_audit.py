"""Full automatic audit of some sessions (Dhruv's plan 2026-11-05): every signal we have, per question, in one list.

    python3 pipeline/year_audit.py 2016-MJ 2016-ON ...      -> out/audit/<sessions>.json + a short summary

Signals (with what rounds 5-10 taught us about how often each one is a real problem):
  figure   crop cuts ink or a text line (checks.py)                          ~80% real -> Claude fixes / looks at every one
  ms       mark scheme: row shrunk / no own Total / Total != marks / header / foreign rows / >1 Total   ~90% real
  msmiss   'no mark scheme for (x)' / 'row has no matching part'                Dhruv: no worry if not in the PDF
  differs  stored copy differs from the page (store.py verify)                 ~11% real -> Claude looks, clears most
  options  options split into pictures                                          ~10% real -> Claude looks at every set
  piece    a cut problem (furniture inside, sliver, mark at top)                always looked at
"""
import json, os, re, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import review_round as RR


def audit(sessions):
    out = collections.defaultdict(list)
    for s in sessions:
        sid = s.replace('-', '')
        for f in sorted(glob.glob(os.path.join(paths.CHECKS, f'0625_{sid}_*.json'))):
            d = json.load(open(f))
            for p in d.get('problems', []) + d.get('flags', []):
                k = p['kind']
                if k == 'text':
                    continue
                if k == 'flag' and re.search(r'no mark scheme for|has no matching part', p['detail']):
                    k = 'msmiss'
                out[p['id']].append((k, p['detail']))
        for f in sorted(glob.glob(os.path.join(paths.STORE_CHECKS, f'0625_{sid}_*.json'))):
            for d in json.load(open(f)).get('differ', []):
                out[d['q']].append(('differs', f"{d['unit']}: {d['missing']}% missing, {d['extra']}% extra"))
        for qf in sorted(glob.glob(f'store/cambridge-igcse/0625-physics/{s}/p*/q*.json')):
            q = json.load(open(qf))
            if q.get('stub'):
                continue
            for r in RR.risk_reasons(q['id']):
                k = 'options' if 'options split' in r else 'table' if 'table kept' in r else 'ms'
                out[q['id']].append((k, r))
    return out


if __name__ == '__main__':
    ss = sys.argv[1:]
    res = audit(ss)
    os.makedirs(os.path.join(paths.ROOT, 'out', 'audit'), exist_ok=True)
    p = os.path.join(paths.ROOT, 'out', 'audit', '_'.join(ss) + '.json')
    json.dump(res, open(p, 'w'), indent=0)
    c = collections.Counter(k for v in res.values() for k, _ in v)
    print(f'{len(res)} questions with a signal: {dict(c)} -> {p}')
