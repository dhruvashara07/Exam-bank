"""Maths: recompute ms_p (ms_layout/ms_maths only) for sessions, list questions whose rows change; --write stores them.
   python3 pipeline/ms_rebuild.py 2024-MJ 2025-ON [--write]   (minutes; never run.py for a layout-only fix)"""
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ms_layout as ML
write = '--write' in sys.argv
for ses in [a for a in sys.argv[1:] if not a.startswith('--')]:
    for qf in sorted(glob.glob(f'store/cambridge-igcse/0607*/{ses}/p*/q*.json')):
        rec = json.load(open(qf))
        if not rec.get('ms_p') or rec.get('stub'):
            continue
        store = os.path.dirname(qf)
        try:
            mp = ML.build(rec, store)
        except Exception as e:
            print('ERR', qf, e); continue
        if not mp:
            print('NONE', qf); continue
        new = {'w': mp['w'], 'h': mp['h'], 'rows': mp['rows'], 'modes': mp['modes'], 'info': mp['info'], 'has_header': mp['has_header'],
               'printed_total': mp.get('printed_total'), 'problems': [list(x) for x in mp['problems']]}
        old = rec['ms_p']
        if json.dumps(new['rows'], sort_keys=True) != json.dumps(old['rows'], sort_keys=True):
            print('CHANGED', qf, old.get('h'), new['h'])
            if write:
                rec['ms_p'] = new; json.dump(rec, open(qf, 'w'), ensure_ascii=False, separators=(',', ':'))
