"""Old mark schemes (pre-2013): does every mark-scheme row label match a part of the question paper?
    python3 pipeline/ms_align.py list <session ...>          # questions whose MS labels and paper parts differ
    python3 pipeline/ms_align.py dump <qid ...>              # paper parts (label, marks, text) + MS lines, to map by eye
Mapping (by reading the question and the answer, Dhruv round 24): pipeline/ms_map.json
    {qid: [[text the MS line starts with, label], ...]} - each listed line starts a row with that label; printed labels are
    then ignored for that question. Checked by `list` again (must be empty) before a review round."""
import sys, os, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store


def qp_leaves(q):
    out = []
    def walk(n):
        ks = n.get('parts', [])
        if not ks and n.get('path'):
            out.append((n['path'], n.get('marks', 0), ' '.join(n.get('text', '').split())[:110]))
        for k in ks:
            walk(k)
    walk(q)
    return out


def ms_rows(sq):
    rows = []
    for v in (sq.get('ms_p') or {}).get('rows', [])[1:-1]:
        L = min([float(re.findall(r'M([\d.]+)', l['d'])[0]) for l in v['lines'] if re.match(r'M[\d.]+ 0', l.get('d', '')) and 5 < float(re.findall(r'M([\d.]+)', l['d'])[0]) < 200] or [44.0])
        lab = [t['t'] for t in v['text'] if t['y'] == 14.0 and t['x'] + t['w'] < L + 2 and re.match(r'\d', t['t'])]
        lines = {}
        for t in sorted(v['text'], key=lambda t: (round(t['y']), t['x'])):
            if not (t['x'] + t['w'] < L + 2 and t['y'] == 14.0 and re.match(r'\d', t['t'])):
                lines.setdefault(round(t['y']), []).append(t['t'])
        rows.append((lab[0] if lab else '', [' '.join(l) for l in lines.values()]))
    return rows


def load(qid):
    sq, _ = store.load(qid)
    if sq.get('stub'):
        return None, None
    q = json.load(open(glob.glob(f'bank/**/{qid}.json', recursive=True)[0]))
    return q, sq


def mismatch(qid):
    q, sq = load(qid)
    if not q or not sq.get('ms_p'):
        return None
    leaves = qp_leaves(q)
    if not leaves:
        return None                            # a question without parts: one row, nothing to match
    allp = set()
    def walk(n):
        for k in n.get('parts', []):
            allp.add(k['path']); walk(k)
    walk(q)
    def parts_of(l):                           # '2(a)(i)(ii)' -> 2(a)(i), 2(a)(ii); '4(b)–(g)' -> 4(b) ... 4(g)
        m = re.fullmatch(r'(\d+)\(([a-p])\)[–-]\(([a-p])\)', l)
        if m:
            return [f'{m.group(1)}({chr(c)})' for c in range(ord(m.group(2)), ord(m.group(3)) + 1)]
        R = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii']
        m = re.fullmatch(r'(\d+\([a-p]\))\(([ivx]+)\)[–-]\(([ivx]+)\)', l)
        if m and m.group(2) in R and m.group(3) in R:
            return [f'{m.group(1)}({r})' for r in R[R.index(m.group(2)):R.index(m.group(3)) + 1]]
        m = re.fullmatch(r'(\d+(?:\([a-p]\))?)((?:\([ivx]+\)){2,})', l) or re.fullmatch(r'(\d+)((?:\([a-hj-p]\)){2,})', l)
        if m:
            return [m.group(1) + f'({x})' for x in re.findall(r'\(([a-pivx]+)\)', m.group(2))]
        return [l]
    labs = [l for l, _ in ms_rows(sq) if l]
    covered = {p for l in labs for p in parts_of(l)}
    leafset = {p for p, m, _ in leaves}
    qn = str(q['number'])
    bad = [l for l in labs if l != qn and not all(p in allp for p in parts_of(l))]   # a row labelled with the bare number: a note for all parts
    import json as _j
    mp_ = _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ms_map.json')))
    mapped = qid in mp_
    original = mapped and any(e[0] == '@original' for e in mp_[qid])
    bad += [] if mapped else [l + '(parent)' for l in labs if all(p in allp for p in parts_of(l)) and not all(p in leafset for p in parts_of(l))]   # Dhruv r24: split into subparts
    if not original:          # '@original' (Dhruv round 26): Cambridge's grouping kept because the marks cannot be separated;
        # a block total printed on one part ('(g) ... [3]' for the table of (g)-(k)) need not have its own row then
        bad += [p for p, m, _ in leaves if m and not any(p == c or p.startswith(c + '(') or c.startswith(p + '(') for c in covered)]
    return bad


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'list':
        for ses in args:
            for f in sorted(glob.glob(f'store/cambridge-igcse/0625-physics/{ses}/p*/q*.json')):
                if re.search(r'/p(01|1\d)/', f):
                    continue
                a = f.split('/'); qid = '0625_' + a[3].replace('-', '') + '_' + a[4][1:] + '_' + os.path.basename(f)[:-5]
                b = mismatch(qid)
                if b:
                    print(qid, ' '.join(b))
    elif cmd == 'verify':      # every mapped question: its rows carry exactly the labels of its map (ERROR_PATTERNS 52)
        import json as _j
        mp = _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ms_map.json')))
        bad = 0
        for qid in sorted(mp):
            try:
                q, sq = load(qid)
            except Exception:
                continue
            if not sq or not sq.get('ms_p') or sq.get('stub'):
                continue
            got = {l for l, _ in ms_rows(sq) if l}
            want = {l for e in mp[qid] if not e[0].startswith('@') for l in [e[1]] + ([e[3]] if len(e) > 3 else [])}
            if got != want:
                bad += 1
                print(qid, 'rows', sorted(got), 'map', sorted(want))
        print(bad, 'mapped questions differ from their map')
    else:
        for qid in args:
            q, sq = load(qid)
            print('=====', qid, 'marks', q['marks'])
            for p, m, t in qp_leaves(q):
                print(f'QP {p} [{m}] {t[:80]}')
            for i, (l, lines) in enumerate(ms_rows(sq)):
                for k, ln in enumerate(lines):
                    print(f'MS {l if k == 0 else "":9s}| {ln[:90]}')
