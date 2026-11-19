"""Mark-scheme sweep over OUR tables (ms_p) - ERROR_PATTERNS 11-13: python3 pipeline/ms_sweep.py 2005-MJ 2005-ON ..."""
import sys, re, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store, subjects
SYL = subjects.current(); SLUG = subjects.subject(SYL)['slug']
bad = []
for ses in sys.argv[1:]:
    for f in sorted(glob.glob(f'store/cambridge-igcse/{SLUG}/{ses}/p*/q*.json')):
        if subjects.mcq_dir(SYL, f.split('/')[4][1:]):
            continue                   # multiple choice: no table
        a = f.split('/'); qid = SYL + '_' + a[3].replace('-', '') + '_' + a[4][1:] + '_' + os.path.basename(f)[:-5]
        sq, _ = store.load(qid)
        if sq.get('stub'):
            continue                   # the same question as another variant (same_as): checked there
        mp = sq.get('ms_p')
        if not mp:
            bad.append((qid, 'no table (scan?)')); continue
        e = (mp.get('info') or {}).get('new_edges') or []
        maths = not subjects.is_physics(SYL) and len(e) >= 3   # maths: Q | Answer | Marks | Partial Marks: the Marks
        #   column is new_edges[1]..[2]; 'M1 for ...' in Partial Marks is no code in the answer (M2 reasons, 2026-11-19)
        for v in mp['rows'][1:-1]:
            for t in v['text']:
                if maths:
                    if re.fullmatch(r'\(?[ABCM]\d,?\)?', t['t']) and e[0] < t['x'] < e[1] - 2:
                        bad.append((qid, 'code in answer', t['t']))
                    if re.fullmatch(r'\[\d{1,2}\]', t['t']) and e[1] - 2 <= t['x'] < e[2]:
                        bad.append((qid, 'bracket in marks', t['t']))
                    if t['t'] in ('TOTAL',) or re.fullmatch(r'\[(Total|TOTAL):?', t['t']):
                        bad.append((qid, t['t']))
                    continue
                if t['t'] in ('TOTAL',) or re.fullmatch(r'\[(Total|TOTAL):?', t['t']) or t['t'] in ('along-',):
                    bad.append((qid, t['t']))
                if re.fullmatch(r'\(?[ABCM]\d,?\)?', t['t']) and t['x'] < 470:
                    bad.append((qid, 'code in answer', t['t']))
                if re.fullmatch(r'\[\d{1,2}\]', t['t']) and t['x'] > 470:
                    bad.append((qid, 'bracket in marks', t['t']))
for b in bad:
    print(*b)
print(len(bad), 'hits')
