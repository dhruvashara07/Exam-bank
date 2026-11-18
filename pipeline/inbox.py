"""File PDFs dropped into inbox/ (any Cambridge-style name) into raw/ with the standard names.

    0625_s25_qp_41.pdf  ->  raw/0625/2025-MJ/qp_41.pdf      (m = Feb/Mar, s = May/Jun, w = Oct/Nov)
    0625_w25_ms_42.pdf  ->  raw/0625/2025-ON/ms_42.pdf
    0625_s25_er.pdf     ->  raw/0625/2025-MJ/er.pdf           (examiner report, kept for analysis)
    0620_s25_gt.pdf / _ci_52 / _ir_52 / _in_52 / _eq_5 -> gt.pdf / ci_52.pdf / ... (grade thresholds, confidential
    instructions, inserts: kept, never processed); old one-digit papers 0620_s04_qp_1 -> qp_1.pdf, combined mark
    schemes 0620_s03_ms_1+2+3 -> ms_1-2-3.pdf, 0620_s04_ms.pdf -> ms.pdf (chem upload 2026-11-18: 303 such files
    had been left in inbox/).
Files may sit in sub-folders of inbox/. Prints the papers to (re)process, one per line, e.g. '0625/2025-MJ/41'.
Unrecognised files stay in inbox/.
"""
import os, re, shutil, sys

sys.path.insert(0, os.path.dirname(__file__))
from paths import ROOT

SESSION = {'m': 'FM', 's': 'MJ', 'w': 'ON'}
NAME = re.compile(r'(\d{4})[_\- ]?([msw])(\d\d)[_\- ]?(qp|ms|er|gt|ci|ir|in|eq|confidential instructions)'
                  r'(?:[_\- ]?(\d{1,2}(?:\+\d{1,2})*))?(?=[_\- .]|$)', re.I)
KIND = {'confidential instructions': 'ci'}


def main():
    inbox = os.path.join(ROOT, 'inbox')
    todo = set()
    files = sorted(os.path.relpath(os.path.join(d, f), inbox) for d, _, fs in os.walk(inbox) for f in fs) \
        if os.path.isdir(inbox) else []          # sub-folders allowed (e.g. a whole '2024-may-june' folder dropped in)
    for name in files:
        m = NAME.search(os.path.basename(name))
        if not name.lower().endswith('.pdf') or not m:
            continue
        syl, ses, yy, kind, pv = m.group(1), m.group(2).lower(), m.group(3), m.group(4).lower(), m.group(5)
        kind = KIND.get(kind, kind)
        folder = f'20{yy}-{SESSION[ses]}'
        if kind in ('qp', 'in', 'ir', 'ci', 'eq') and not pv:
            continue
        if os.path.getsize(os.path.join(inbox, name)) == 0:
            print(f'EMPTY {name}', file=sys.stderr); continue
        pv_ = (pv or '').replace('+', '-')
        fname = f'{kind}.pdf' if kind in ('er', 'gt') or not pv_ else f'{kind}_{pv_}.pdf'
        dst = os.path.join(ROOT, 'raw', syl, folder, fname)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst) and os.path.getsize(dst) != os.path.getsize(os.path.join(inbox, name)):
            print(f'CLASH {name} -> {dst} (kept in inbox)', file=sys.stderr); continue
        shutil.move(os.path.join(inbox, name), dst)
        if kind in ('qp', 'ms') and pv and re.fullmatch(r'\d\d', pv):
            todo.add(f'{syl}/{folder}/{pv}')
    for t in sorted(todo):
        print(t)


if __name__ == '__main__':
    main()
