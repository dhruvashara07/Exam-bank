"""Mark-scheme look check over the STORED layouts (chemistry C1, ERROR_PATTERNS 319 / chemistry 319 repeat):
  overlap  - two words of one MS row whose boxes overlap (text over text: an Answer line run into Guidance / Marks)
  black    - a filled black shape bigger than 4 x 4 pt (a rule or table box gone solid; bond strokes give false hits)

    python3 pipeline/ms_overlap.py 0620 2021-FM 2021-MJ ...        # sessions of one syllabus
Each hit is a question id to LOOK at (side by side), not a fault by itself.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import subjects


def overlaps(rows):
    n = 0
    for v in rows:
        T = [t for t in v.get('text', []) if t['t'].strip()]
        bx = [(t['x'], t['y'] - 0.7 * t['s'], t['x'] + t['w'], t['y']) for t in T]
        for a in range(len(bx)):
            for b in range(a + 1, len(bx)):
                A, B = bx[a], bx[b]
                if min(A[2], B[2]) - max(A[0], B[0]) > 2 and min(A[3], B[3]) - max(A[1], B[1]) > 2:
                    n += 1
    return n


def blacks(rows):
    n = 0
    for v in rows:
        for l in v.get('lines', []):
            if l.get('fill') not in ('#000000', '#000', 'black'):
                continue
            pts = re.findall(r'[ML]\s*(-?[\d.]+)[ ,](-?[\d.]+)', l['d'])
            hv = re.findall(r'([HV])\s*(-?[\d.]+)', l['d'])
            xs = [float(x) for x, _ in pts] + [float(a) for c, a in hv if c == 'H']
            ys = [float(y) for _, y in pts] + [float(a) for c, a in hv if c == 'V']
            if xs and ys and max(xs) - min(xs) > 4 and max(ys) - min(ys) > 4 and \
                    (max(xs) - min(xs)) * (max(ys) - min(ys)) > 40:
                n += 1
    return n


if __name__ == '__main__':
    syl, sessions = sys.argv[1], sys.argv[2:]
    base = os.path.join(paths.ROOT, 'store', 'cambridge-igcse', subjects.subject(syl)['slug'])
    for ses in sessions:
        for f in sorted(glob.glob(os.path.join(base, ses, 'p*', 'q*.json'))):
            r = json.load(open(f))
            rows = (r.get('ms_p') or {}).get('rows', [])
            o, b = overlaps(rows), blacks(rows)
            if o or b:
                print(r['id'], f'overlap={o}' if o else '', f'black={b}' if b else '')
