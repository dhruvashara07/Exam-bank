"""Claude's ONE check round (PLAYBOOK 2, Dhruv round 29: 'make 1 round of yours, check by rules and checkbox, side by
side with the original in doubtful cases').

    python3 pipeline/claude_check.py <batch> <paper ids...>        e.g. M0 0607_2014MJ_11 0607_2014MJ_12 ...

1. RULES on every paper (each one a checkbox in review/claude/<batch>_check.md):
   - checks.py problems           (content: parts, marks = total, MS linked, figures captured)
   - maths_check.py content       (ms_words, ms_overflow, ms_overlap, ms_font, fig_overlap, not_to_scale)
   - maths_check.py appearance    (ms_stretch, ms_edge, ms_piccut, q_font, fig_cut, fig_text)
   - golden.py (physics frozen)   (0 changed cuts) - run separately before push
2. DOUBTFUL = every question with a hit + every mark-scheme cell drawn as a picture or a table block + a random sample.
3. SIDE BY SIDE for the doubtful ones only: out/claude_check/<batch>/ms_<n>.png (our mark scheme | printed rows) and
   fig_<n>.png (each diagram crop drawn on its printed page). Claude reads every sheet; a hit that matches the print is
   passed with its reason in the checklist (Dhruv: 'pass it, log the reason'); anything else is a pattern to fix.
Only when every box is ticked is the review round built.
"""
import json
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ROOT = paths.ROOT


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def main(batch, ids, sample=8):
    out_dir = os.path.join(ROOT, 'out', 'claude_check', batch)
    os.makedirs(out_dir, exist_ok=True)
    r = run([sys.executable, 'pipeline/maths_check.py'] + ids)
    hits = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith('0607_') and ' ' in line:
            qid, rest = line.split(None, 1)
            hits.setdefault(qid, []).append(rest)
    # mark-scheme cells drawn as pictures / table blocks: always looked at
    pics = []
    for pid in ids:
        sd = paths.store_dir(pid)
        if not os.path.isdir(sd):
            continue
        for f in sorted(os.listdir(sd)):
            if not (f.startswith('q') and f.endswith('.json')):
                continue
            rec = json.load(open(os.path.join(sd, f)))
            mp = rec.get('ms_p') or {}
            if any(v.get('images') for v in mp.get('rows', [])):
                pics.append(rec['id'])
    qids = sorted({q for q in hits} | set(pics))
    pool = []
    for pid in ids:
        sd = paths.store_dir(pid)
        if os.path.isdir(sd):
            pool += [f'{pid}_{f[:-5]}' for f in os.listdir(sd) if f.startswith('q') and f.endswith('.json')]
    random.seed(batch)
    extra = random.sample(sorted(set(pool) - set(qids)), min(sample, len(set(pool) - set(qids))))
    ms_ids = qids + extra
    r2 = run([sys.executable, 'pipeline/ms_compare.py', os.path.join(out_dir, 'ms')] + ms_ids)
    figs = [(q, rest.split(':')[1].split()[0]) for q, rs in hits.items() for rest in rs
            if rest.startswith(('fig_cut', 'fig_text'))]
    if figs:
        run([sys.executable, 'pipeline/ms_compare.py', '--figs', os.path.join(out_dir, 'fig')] + [f'{q}:{s}' for q, s in figs])
    md = [f'# Claude check {batch}', '', f'Papers: {len(ids)}. Doubtful questions: {len(qids)} (+{len(extra)} random).', '',
          '## Rules', '', '- [ ] checks.py: 0 blocking problems on every paper',
          '- [ ] maths_check content: 0 hits or each passed below', '- [ ] maths_check appearance: 0 hits or each passed below',
          '- [ ] golden.py: 0 changed cuts, nothing under 0625-physics', '- [ ] every side-by-side sheet read (list below)', '',
          '## Doubtful (tick = matches the print; write the reason, or the pattern number if fixed)', '']
    for q in qids:
        md.append(f"- [ ] {q}: {'; '.join(hits.get(q, [])) or 'mark-scheme picture / table'} - reason:")
    md += ['', '## Random', ''] + [f'- [ ] {q}' for q in extra]
    md += ['', '## Sheets', ''] + [l for l in r2.stdout.splitlines() if l.endswith(')')]
    path = os.path.join(ROOT, 'review', 'claude', f'{batch}_check.md')
    open(path, 'w').write('\n'.join(md) + '\n')
    print(path, len(qids), 'doubtful', len(extra), 'random')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
