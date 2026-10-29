"""File PDFs dropped into inbox/ (any Cambridge-style name) into raw/ with the standard names.

    0625_s25_qp_41.pdf  ->  raw/0625/2025-MJ/qp_41.pdf      (m = Feb/Mar, s = May/Jun, w = Oct/Nov)
    0625_w25_ms_42.pdf  ->  raw/0625/2025-ON/ms_42.pdf
    0625_s25_er.pdf     ->  raw/0625/2025-MJ/er.pdf           (examiner report, kept for analysis)
Prints the papers to (re)process, one per line, e.g. '0625/2025-MJ/41'. Unrecognised files stay in inbox/.
"""
import os, re, shutil, sys

sys.path.insert(0, os.path.dirname(__file__))
from paths import ROOT

SESSION = {'m': 'FM', 's': 'MJ', 'w': 'ON'}
NAME = re.compile(r'(\d{4})[_\- ]?([msw])(\d\d)[_\- ]?(qp|ms|er)(?:[_\- ]?(\d\d))?', re.I)


def main():
    inbox = os.path.join(ROOT, 'inbox')
    todo = set()
    for name in sorted(os.listdir(inbox)) if os.path.isdir(inbox) else []:
        m = NAME.search(name)
        if not name.lower().endswith('.pdf') or not m:
            continue
        syl, ses, yy, kind, pv = m.group(1), m.group(2).lower(), m.group(3), m.group(4).lower(), m.group(5)
        folder = f'20{yy}-{SESSION[ses]}'
        if kind != 'er' and not pv:
            continue
        if os.path.getsize(os.path.join(inbox, name)) == 0:
            print(f'EMPTY {name}', file=sys.stderr); continue
        dst = os.path.join(ROOT, 'raw', syl, folder, 'er.pdf' if kind == 'er' else f'{kind}_{pv}.pdf')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(os.path.join(inbox, name), dst)
        if kind != 'er':
            todo.add(f'{syl}/{folder}/{pv}')
    for t in sorted(todo):
        print(t)


if __name__ == '__main__':
    main()
