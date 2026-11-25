"""Maths: recompute ms_p (ms_layout/ms_maths only) for sessions, list questions whose rows change; --write stores them.
   python3 pipeline/ms_rebuild.py 2024-MJ 2025-ON [--write]   (minutes; never run.py for a layout-only fix)
   python3 pipeline/ms_rebuild.py 0607_2024MJ_41_q02 ... [--write]  (seconds: try a fix on its target questions first)"""
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ms_layout as ML
write = '--write' in sys.argv
SYL = os.environ.get('SYL', '0607')                           # SYL=0620 for chemistry (default maths, unchanged)
only = [a for a in sys.argv[1:] if a.startswith(SYL + '_')]    # question ids: test a fix on its targets first (seconds)
sess = [a for a in sys.argv[1:] if not a.startswith('--') and not a.startswith(SYL + '_')]
files = []
for q in only:
    _, s_, p_, n_ = q.split('_')
    files += glob.glob(f'store/cambridge-igcse/{SYL}*/{s_[:4]}-{s_[4:]}/p{p_}/{n_}.json')
for ses in sess:
    files += sorted(glob.glob(f'store/cambridge-igcse/{SYL}*/{ses}/p*/q*.json'))
missing = sorted({os.path.join('raw', SYL, qf.split('/')[3], f"ms_{qf.split('/')[4][1:]}.pdf") for qf in files}
                 - {p for p in glob.glob(f'raw/{SYL}/*/ms_*.pdf')})
if missing:                    # without the printed PDF every picture cell silently falls back: the local rebuild then differs
    sys.exit('fetch the PDFs first (raw_store.py fetch ...): ' + ' '.join(missing[:6]))   # from the Action (ERROR_PATTERNS 211)
for _ in [0]:
    for qf in files:
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
if write:                                   # paper 5/6 task records carry the merged mark scheme (tasks.py)
    import tasks
    for d in sorted({os.path.dirname(f) for f in files}):
        tasks.build_paper(d)
