"""Maths paper 5/6: each task (the investigation, the modelling) as ONE record (Dhruv, round 32 / MATHS_PLAN 11).

A single question of a task has no use out of context, so the task record holds:
  - the task's intro (section heading, instructions, pictures: paper.json 'intros') as the stem = root part,
  - every printed question of the task as a part (its own parts below it, labels, marks, mark-scheme rows),
  - one mark scheme: the header once, the section note once ('Throughout the modelling ...'), the rows of every
    question in order, one Total.
The per-question records stay (every check and the review work per question) and point to their task
('task': id). The task record: store/.../p62/task_B.json, id '0607_2024FM_62_tB', type 'task'.
Built after the paper's records (store.build) and after ms_rebuild --write; idempotent.

    python3 pipeline/tasks.py <store paper dir>...     # rebuild the task records of these papers
"""
import copy
import glob
import json
import os
import re
import sys

NOTE = re.compile(r'^\s*Throughout the (modelling|investigation)', re.I)


def _rows_text(r):
    return ' '.join(t['t'] for t in r.get('text', []))


def _merge_ms(recs):
    """One mark-scheme table for the task: header from the first, section note once, rows in order, one Total."""
    out, y_rows, seen_note, total, w, info, modes = [], [], False, 0, None, None, {}
    head = head_tot = None
    for n, r in enumerate(recs):
        m = r.get('ms_p')
        if not m:
            continue
        w = w or m['w']; info = info or m.get('info'); modes.update(m.get('modes') or {})
        rows = list(m['rows'])
        if m.get('has_header') and rows:
            if head is None:
                head = rows[0]
            rows = rows[1:]
        if rows and re.match(r'^\s*Total\b', _rows_text(rows[-1])):
            head_tot = rows.pop()
        for row in rows:
            if NOTE.match(_rows_text(row)):
                if seen_note:
                    continue
                seen_note = True
            out.append(row)
        total += r.get('marks') or 0
    if not out:
        return None
    rows = ([head] if head else []) + out
    if head_tot is not None:                       # the Total row with the task's total
        tr = copy.deepcopy(head_tot)
        nums = [t for t in tr['text'] if re.fullmatch(r'\d+', t['t'])]
        if nums:
            t = nums[-1]; old = t['t']; t['t'] = str(total)
            t['x'] = round(t['x'] + t.get('w', 0) - t.get('w', 0) * len(t['t']) / max(1, len(old)), 2)
            t['w'] = round(t.get('w', 0) * len(t['t']) / max(1, len(old)), 2)
        rows.append(tr)
    return {'w': w, 'h': round(sum(r['h'] for r in rows), 2), 'rows': rows, 'modes': modes, 'info': info,
            'has_header': head is not None, 'printed_total': total, 'problems': []}


def build_paper(d):
    pf = os.path.join(d, 'paper.json')
    if not os.path.exists(pf):
        return []
    paper = json.load(open(pf))
    intros = paper.get('intros') or []
    for f in glob.glob(os.path.join(d, 'task_*.json')):
        os.remove(f)
    if not intros:
        return []
    recs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(d, 'q*.json')))]
    made = []
    for k, it in enumerate(intros):
        lo = it['before']; hi = intros[k + 1]['before'] if k + 1 < len(intros) else 10 ** 6
        mem = [r for r in recs if lo <= r['number'] < hi]
        if not mem:
            continue
        sec = it.get('section') or str(k + 1)
        base = '_'.join(mem[0]['id'].split('_')[:3])
        tid = f'{base}_t{sec}'
        if all(r.get('stub') and r.get('same_as') for r in mem):   # the same task printed in another variant (2016 ON
            canon = {'_'.join(r['same_as'][0].split('_')[:3]) for r in mem}   # 53 = 52): one stub that points to it,
            if len(canon) == 1:                                    # like its questions (store.dupes) - its figures live
                ctid = f'{canon.pop()}_t{sec}'                     # with the canonical copy
                rec = {'schema': mem[0].get('schema'), 'id': tid, 'paper': mem[0].get('paper'), 'number': mem[0]['number'],
                       'type': 'task', 'section': sec, 'questions': [r['number'] for r in mem],
                       'members': [r['id'] for r in mem], 'marks': sum(r.get('marks') or 0 for r in mem),
                       'answer': None, 'stub': True, 'same_as': [ctid]}
                json.dump(rec, open(os.path.join(d, f'task_{sec}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
                for r in mem:
                    if r.get('task') != tid:
                        r['task'] = tid
                        json.dump(r, open(os.path.join(d, f"q{r['number']:02d}.json"), 'w'), ensure_ascii=False,
                                  separators=(',', ':'))
                made.append(tid)
                continue
        root = {'path': sec, 'label': None, 'parent': None, 'marks': sum(r.get('marks') or 0 for r in mem),
                'text': '', 'layout': copy.deepcopy(it.get('layout') or []), 'ms': [],
                'content': copy.deepcopy(it.get('content') or []), 'tex_check': it.get('tex_check')}
        parts = [root]
        figs = copy.deepcopy(it.get('figures') or [])     # the intro's own pictures first (Dhruv round 46)
        for r in mem:
            for p in r.get('parts', []):
                p2 = copy.deepcopy(p)
                if p2.get('parent') is None:
                    p2['parent'] = sec
                parts.append(p2)
            figs += copy.deepcopy(r.get('figures') or [])
        rec = {'schema': mem[0].get('schema'), 'id': tid, 'paper': mem[0].get('paper'), 'number': mem[0]['number'],
               'type': 'task', 'section': sec, 'questions': [r['number'] for r in mem], 'members': [r['id'] for r in mem],
               'marks': root['marks'], 'answer': None, 'parts': parts, 'figures': figs}
        ms = _merge_ms(mem)
        if ms:
            rec['ms_p'] = ms
        json.dump(rec, open(os.path.join(d, f'task_{sec}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
        for r in mem:                                  # each question points to its task
            if r.get('task') != tid:
                r['task'] = tid
                json.dump(r, open(os.path.join(d, f"q{r['number']:02d}.json"), 'w'), ensure_ascii=False,
                          separators=(',', ':'))
        made.append(tid)
    return made


if __name__ == '__main__':
    for d in sys.argv[1:]:
        print(d, build_paper(d))
