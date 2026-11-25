"""ONE reasons file per batch: the two-pass flow (MATHS_PLAN 11, Dhruv 2026-11-17: 'git, you, git, then you and the
review round').

    python3 pipeline/reasons.py pass1 <batch> <sessions...> [--skip-checks] [--skip-verify]
        every check on every paper of the sessions -> review/claude/<batch>_reasons.json (one entry per flagged reason,
        status 'open') + review/claude/<batch>_fp.json (fingerprint of every question: question side / mark scheme)
    python3 pipeline/reasons.py classes <batch> [--status open]
        the reasons grouped into classes (check + detail with numbers blanked): resolve a class, not an item
    python3 pipeline/reasons.py set <batch> --status fixed|passed|ask|open --note "..." [--check C] [--match REGEX]
                                             [--qid QID_REGEX] [--rid r1,r2] [--pattern N]
        Claude's decision for every matching reason (fixed = the class is fixed in the pipeline (pattern N),
        passed = matches the print / not a fault (the reason written), ask = a real decision for Dhruv)
    python3 pipeline/reasons.py sheets <batch> [--status open] [--check C] [--qid QID_REGEX]
        side-by-side sheets (ms_compare: ours | printed) for the selected reasons -> out/claude_check/<batch>/
    python3 pipeline/reasons.py pass2 <batch> [--skip-checks] [--skip-verify]
        the checks again after the rebuild with the fixes: every 'fixed' reason must be gone, new reasons are added
        ('open', from pass 2), every changed question is listed (expected = it had a fixed reason; else COLLATERAL)
        -> review/claude/<batch>_pass2.md. Claude looks only at what this lists.
    python3 pipeline/reasons.py round <batch> [--calibrate 5]
        the review round's items: every 'ask', every reason still open, + N calibration items (random passed/fixed)
        -> prints the ids and the --recheck string for review_round.py new
    python3 pipeline/reasons.py status <batch>
        counts by status and check (open must be 0 before the round)

Statuses: open (not looked at), fixed (pipeline fix, pattern N), passed (looked at: matches the print, reason
written), ask (Dhruv decides), known (my own fault not fixed yet: in PROGRESS / ERROR_PATTERNS, never in his round). Pass 2 adds 'verified' (fixed and gone) / 'not fixed' (fixed but still reported).
"""
import collections
import glob
import hashlib
import json
import os
import random
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

ROOT = paths.ROOT
SYL = '0607'
SLOW = ('checks', 'verify')
ALWAYS = ('ms_picture', 'ms_table')     # 'look at it' reasons, not faults: present in every pass


def _f(batch, kind):
    return os.path.join(paths.CLAUDE_CHECKS, f'{batch}_{kind}')


def load(batch):
    p = _f(batch, 'reasons.json')
    return json.load(open(p)) if os.path.exists(p) else {'batch': batch, 'sessions': [], 'reasons': []}


def save(batch, data):
    os.makedirs(paths.CLAUDE_CHECKS, exist_ok=True)
    data['reasons'].sort(key=lambda r: (r['qid'], r['check'], r['detail']))
    json.dump(data, open(_f(batch, 'reasons.json'), 'w'), ensure_ascii=False, indent=0)


def run(cmd, env=None):
    e = dict(os.environ, SYL=SYL, **(env or {}))
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=e)


def papers(sessions):
    out = []
    for s in sessions:
        r = run([sys.executable, 'pipeline/session_papers.py', f'{SYL}/{s}'])
        out += r.stdout.split()
    return out


def pid_of(sel):                                  # '0607/2021-MJ/41' -> '0607_2021MJ_41'
    syl, ses, pv = sel.split('/')
    return f"{syl}_{ses.replace('-', '')}_{pv}"


def norm(detail):
    """Detail with numbers blanked: the class key, stable between runs (pixel counts, positions move)."""
    return re.sub(r'\d+(?:\.\d+)?', '#', detail).strip()


PART = re.compile(r'\b\d{1,2}(?:\([a-z]{1,4}\))+')


def _reason(qid, check, detail, blocking=False):
    m = PART.search(detail)
    return {'qid': qid, 'check': check, 'detail': detail[:300], 'part': m.group(0) if m else '', 'blocking': blocking}


def collect(sessions, skip=()):
    """Every flagged reason of every paper of the sessions (one list), from every check we have."""
    sels = papers(sessions)
    pids = [pid_of(s) for s in sels]
    if 'checks' not in skip:
        run([sys.executable, 'pipeline/checks.py'] + sels)
    if 'verify' not in skip:
        run([sys.executable, 'pipeline/store.py', 'verify'] + pids)
    out = []
    import maths_check
    for pid in pids:
        try:
            sd = paths.store_dir(pid)
        except FileNotFoundError:
            out.append(_reason(pid, 'build', 'paper not built', True))
            continue
        c = os.path.join(paths.CHECKS, pid + '.json')
        if os.path.exists(c):
            res = json.load(open(c))
            for p in res['problems']:
                out.append(_reason(p['id'] if p['id'] != pid else pid, 'checks.' + p['kind'], p['detail'], p['blocking']))
            for fl in res.get('flags', []):
                if isinstance(fl, dict):
                    out.append(_reason(fl.get('id', pid), 'flag.' + fl.get('kind', 'flag'), fl.get('detail', json.dumps(fl))))
                else:
                    out.append(_reason(pid, 'flag', str(fl)))
        else:
            out.append(_reason(pid, 'checks.missing', 'checks.py result missing', True))
        for h in maths_check.check_paper(pid):
            out.append(_reason(h['id'], h['kind'], h['detail']))
        v = os.path.join(paths.STORE_CHECKS, pid + '.json')
        if os.path.exists(v):
            for d in json.load(open(v)).get('differ', []):
                out.append(_reason(d['q'], 'verify', f"{d['unit']}: missing {d['missing']:.1f}% extra {d['extra']:.1f}%"))
        for f in sorted(glob.glob(os.path.join(sd, 'q*.json'))):     # cells drawn as pictures / tables: always looked at
            rec = json.load(open(f))
            if rec.get('stub'):
                continue
            for i, v in enumerate((rec.get('ms_p') or {}).get('rows', [])):
                lab = next((t['t'] for t in v.get('text', []) if t['x'] < 40 and re.match(r'\d', t['t'])), f'row {i}')
                if v.get('images'):
                    out.append(_reason(rec['id'], 'ms_picture', f"{lab}: picture cell"))
                elif len(v.get('lines', [])) > 25:
                    out.append(_reason(rec['id'], 'ms_table', f"{lab}: table / graph drawn as lines"))
    for tool, args in (('ms_sweep', ['pipeline/ms_sweep.py'] + sessions), ('ms_align', ['pipeline/ms_align.py', 'list'] + sessions)):
        r = run([sys.executable] + args)
        for line in r.stdout.splitlines():
            if line.startswith(SYL + '_'):
                qid, _, rest = line.partition(' ')
                out.append(_reason(qid, tool, rest))
    import subjects
    if not subjects.is_maths(SYL):    # chemistry runs the physics layout in Arial: the maths-only checks do not apply
        out = [r for r in out if r['check'] not in ('q_font', 'ms_mode')     # (sans words, not laid out by ms_maths)
               and not (r['check'] == 'ms_sweep' and re.match(r'code in answer \(?M\d', r['detail']))]   # 'M1 ...' = marking point
    # one id per reason: check + question + class detail (+ n for repeats of the same class in one question)
    seen = collections.Counter()
    for r in out:
        k = f"{r['check']}|{r['qid']}|{norm(r['detail'])}"
        seen[k] += 1
        r['rid'] = hashlib.sha1(f'{k}|{seen[k]}'.encode()).hexdigest()[:10]
    return pids, out


def fingerprints(pids):
    fp = {}
    for pid in pids:
        try:
            sd = paths.store_dir(pid)
        except FileNotFoundError:
            continue
        for f in sorted(glob.glob(os.path.join(sd, 'q*.json')) + glob.glob(os.path.join(sd, 'task_*.json'))):
            rec = json.load(open(f))
            h = lambda o: hashlib.sha1(json.dumps(o, sort_keys=True).encode()).hexdigest()[:12]
            fp[rec.get('id') or f] = {'q': h({k: v for k, v in rec.items() if k != 'ms_p'}), 'ms': h(rec.get('ms_p'))}
    return fp


def opts(a):
    o, rest, i = {}, [], 0
    while i < len(a):
        if a[i].startswith('--'):
            if i + 1 < len(a) and not a[i + 1].startswith('--'):
                o[a[i][2:]] = a[i + 1]; i += 2
            else:
                o[a[i][2:]] = True; i += 1
        else:
            rest.append(a[i]); i += 1
    return o, rest


def select(data, o):
    rs = data['reasons']
    if o.get('status'):
        rs = [r for r in rs if r['status'] == o['status']]
    if o.get('check'):
        rs = [r for r in rs if re.fullmatch(o['check'], r['check'])]
    if o.get('match'):
        rs = [r for r in rs if re.search(o['match'], r['detail'])]
    if o.get('qid'):
        rs = [r for r in rs if re.search(o['qid'], r['qid'])]
    if o.get('rid'):
        ids = set(o['rid'].split(','))
        rs = [r for r in rs if r['rid'] in ids]
    return rs


def skips(o):
    return tuple(s for s in SLOW if o.get('skip-' + s))


def pass1(batch, sessions, o):
    pids, rs = collect(sessions, skips(o))
    old = {r['rid']: r for r in load(batch)['reasons']}
    for r in rs:                       # a re-run of pass 1 keeps decisions already written
        p = old.get(r['rid'])
        r.update({'status': p['status'], 'note': p['note'], 'pattern': p.get('pattern')} if p else
                 {'status': 'open', 'note': '', 'pattern': None})
        r['from'] = 'pass1'
    save(batch, {'batch': batch, 'sessions': sessions, 'papers': pids, 'reasons': rs})
    json.dump(fingerprints(pids), open(_f(batch, 'fp.json'), 'w'), indent=0)
    print(f'{batch} pass 1: {len(pids)} papers, {len(rs)} reasons ({len(set(r["qid"] for r in rs))} questions)')
    classes(batch, {})


def classes(batch, o):
    data = load(batch)
    g = collections.defaultdict(list)
    for r in select(data, o):
        g[(r['check'], norm(r['detail']) if not r['check'].startswith(('ms_picture', 'ms_table', 'verify')) else '')].append(r)
    for (c, d), rs in sorted(g.items(), key=lambda x: -len(x[1])):
        st = collections.Counter(r['status'] for r in rs)
        print(f"{len(rs):4d}  {c:16s} {d[:70]:70s} {dict(st)}  e.g. {rs[0]['qid']} {rs[0]['detail'][:50]}")


def setcmd(batch, o):
    data = load(batch)
    rs = select(data, {k: v for k, v in o.items() if k != 'status'})
    if not rs:
        sys.exit('no reason matches')
    for r in rs:
        r['status'] = o['status']
        r['note'] = o.get('note', r['note'])
        if o.get('pattern'):
            r['pattern'] = int(o['pattern'])
    save(batch, data)
    print(f"{len(rs)} reasons -> {o['status']}")


def sheets(batch, o):
    rs = select(load(batch), o)
    out = os.path.join(ROOT, 'out', 'claude_check', batch)
    os.makedirs(out, exist_ok=True)
    tag = o.get('tag', 'x')
    figs = []                          # question-side diagram reasons: the crop drawn on its printed page
    for r in rs:
        m = re.search(r'_(diagram\d+|fig[A-Za-z0-9-]+)\b', r['detail'])   # maths diagram<n>, physics / chemistry figA
        if m and (r['check'].startswith(('fig', 'checks.figure'))):
            q = '_'.join(r['qid'].split('_')[:4])
            figs.append(f'{q}:{m.group(1)}')
    if figs:
        r = run([sys.executable, 'pipeline/ms_compare.py', '--figs', os.path.join(out, f'fig_{tag}')] + sorted(set(figs)))
        print(r.stdout[-3000:], r.stderr[-800:])
        stored_sheet(sorted(set(figs)), os.path.join(out, f'figstored_{tag}'))
    qids = sorted({'_'.join(r['qid'].split('_')[:4]) for r in rs if r['qid'].count('_') >= 3
                   and not r['check'].startswith(('fig', 'checks.figure'))})
    if qids:
        r = run([sys.executable, 'pipeline/ms_compare.py', os.path.join(out, f'ms_{tag}')] + qids)
        print(r.stdout[-3000:], r.stderr[-800:])


def stored_sheet(items, out):
    """The STORED figure SVGs (what students get) in a grey frame, 6 per sheet: is anything cut at an edge?"""
    from PIL import Image, ImageDraw
    import review_assets as ra
    ims = []
    for it in items:
        qid, suf = it.split(':')
        sd = paths.store_dir(qid.rsplit('_', 1)[0])
        fs = sorted(glob.glob(os.path.join(sd, 'figures', f'{qid}*{suf}.svg')))
        if not fs:
            continue
        im = ra.svg_img(os.path.relpath(fs[0], ROOT), 110).convert('RGB')
        c = Image.new('RGB', (im.width + 24, im.height + 34), (235, 235, 235))
        c.paste(im, (12, 22))
        ImageDraw.Draw(c).text((3, 3), it, fill=(0, 0, 255))
        ims.append(c)
    for n in range(0, len(ims), 6):
        g = ims[n:n + 6]
        W, H = max(i.width for i in g), max(i.height for i in g)
        sheet = Image.new('RGB', (3 * W, ((len(g) + 2) // 3) * H), 'white')
        for i, im in enumerate(g):
            sheet.paste(im, ((i % 3) * W, (i // 3) * H))
        sheet.thumbnail((1800, 2400))
        sheet.save(f'{out}_{n // 6}.png')
        print(f'{out}_{n // 6}.png', sheet.size)


def pass2(batch, o):
    data = load(batch)
    pids, now = collect(data['sessions'], skips(o))
    nowids = {r['rid']: r for r in now}
    fp_old = json.load(open(_f(batch, 'fp.json')))
    fp_new = fingerprints(pids)
    rep = collections.defaultdict(list)
    moved = {q for q in set(fp_old) | set(fp_new) if fp_old.get(q) != fp_new.get(q)}
    for r in data['reasons']:
        here = r['rid'] in nowids
        r['pass2'] = 'present' if here else 'gone'
        if r['status'] in ('fixed', 'verified', 'not fixed'):
            if r['check'] in ALWAYS:   # a picture / table cell is listed whatever its state: fixed = the question changed
                if r['status'] == 'verified':   # verified by an EARLIER pass: unchanged since is right (pass 3 listed 19
                    continue                    # of them as 'not fixed', M2)
                here = '_'.join(r['qid'].split('_')[:4]) not in moved
            r['status'] = 'not fixed' if here else 'verified'
            rep[r['status']].append(r)
        elif not here:
            rep['gone (' + r['status'] + ')'].append(r)
    known = {r['rid'] for r in data['reasons']}
    for r in now:
        if r['rid'] not in known:
            r.update({'status': 'open', 'note': '', 'pattern': None, 'from': 'pass2'})
            data['reasons'].append(r)
            rep['NEW'].append(r)
    fixed_q = {'_'.join(r['qid'].split('_')[:4]) for r in data['reasons']
               if r['status'] in ('verified', 'not fixed')}
    changed = []
    for q in sorted(set(fp_old) | set(fp_new)):
        a, b = fp_old.get(q), fp_new.get(q)
        if a != b:
            side = 'added' if not a else 'removed' if not b else '+'.join(s for s in ('q', 'ms') if a[s] != b[s])
            changed.append((q, side, 'expected' if q in fixed_q else 'COLLATERAL'))
    save(batch, data)
    json.dump(fp_new, open(_f(batch, 'fp.json'), 'w'), indent=0)   # the next pass diffs against this one
    md = [f'# {batch} pass 2 (diff against pass 1)', '',
          f"Reasons: {len(data['reasons'])}; verified {len(rep['verified'])}, NOT FIXED {len(rep['not fixed'])}, "
          f"NEW {len(rep['NEW'])}; changed questions {len(changed)} "
          f"({sum(c[2] == 'COLLATERAL' for c in changed)} collateral).", '',
          'Look only at: NOT FIXED, NEW and COLLATERAL changes (each is set to fixed / passed / ask).', '']
    for k in ('not fixed', 'NEW'):
        md += [f'## {k}', ''] + [f"- {r['rid']} {r['qid']} {r['check']}: {r['detail'][:120]}" for r in rep[k]] + ['']
    md += ['## Changed questions', ''] + [f'- {q} [{s}] {e}' for q, s, e in changed] + ['']
    for k in sorted(k for k in rep if k.startswith('gone')):
        md += [f'## {k}', ''] + [f"- {r['qid']} {r['check']}: {r['detail'][:100]}" for r in rep[k]] + ['']
    open(_f(batch, 'pass2.md'), 'w').write('\n'.join(md) + '\n')
    print('\n'.join(md[:4]))


def round_items(batch, o):
    data = load(batch)
    ask = [r for r in data['reasons'] if r['status'] in ('ask', 'open', 'not fixed')]   # ('known' = an open fault of
    #   mine, written in PROGRESS / ERROR_PATTERNS: never in Dhruv's round)
    pool = sorted({r['qid'] for r in data['reasons'] if r['status'] in ('passed', 'verified')} - {r['qid'] for r in ask})
    random.seed(batch)
    cal = random.sample(pool, min(int(o.get('calibrate', 5)), len(pool)))
    items = collections.OrderedDict()
    for r in ask:
        q = '_'.join(r['qid'].split('_')[:4])
        items.setdefault(q, []).append(r['note'] or f"{r['check']}: {r['detail'][:80]}")
    for q in cal:
        items.setdefault('_'.join(q.split('_')[:4]), []).append('calibration: Claude passed this - is it right?')
    print(' '.join(items))
    print('--recheck "' + ';'.join(f"{q}={' / '.join(v)[:200].replace(';', ',').replace('=', ':')}" for q, v in items.items()) + '"')


def status(batch, o):
    data = load(batch)
    print(dict(collections.Counter(r['status'] for r in data['reasons'])))
    print(dict(collections.Counter((r['check'], r['status']) for r in data['reasons'])))


if __name__ == '__main__':
    cmd = sys.argv[1]
    o, rest = opts(sys.argv[2:])
    batch = rest[0]
    _rec = os.path.join(ROOT, 'review', 'cycle', batch + '.json')       # the batch's syllabus (C0 = 0620); default maths
    SYL = os.environ.get('SYL') or (json.load(open(_rec)).get('subject') if os.path.exists(_rec) else None) or SYL
    {'pass1': lambda: pass1(batch, rest[1:], o), 'pass2': lambda: pass2(batch, o), 'classes': lambda: classes(batch, o),
     'set': lambda: setcmd(batch, o), 'sheets': lambda: sheets(batch, o), 'round': lambda: round_items(batch, o),
     'status': lambda: status(batch, o)}[cmd]()
