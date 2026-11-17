"""Batch record for the subject cycle (docs/MATHS_PLAN.md): times per phase, GitHub run times, counts,
errors (new / repeat) and tokens. One file per batch: review/cycle/<batch>.json. docs/BATCH_LOG.md is
rebuilt from all of them by `report`, so the table is never typed by hand.

    python3 pipeline/batch_log.py start  M0 --subject 0607 --sessions 2014-MJ 2019-ON 2021-FM 2025-MJ
    python3 pipeline/batch_log.py phase  M0 build start         # build | claude | review | fix
    python3 pipeline/batch_log.py phase  M0 build end  --note "26 papers"
    python3 pipeline/batch_log.py gh     M0 43252980978 ...     # add GitHub Action run times (REST API)
    python3 pipeline/batch_log.py count  M0 papers=26 questions=310 flags=41 round_items=18
    python3 pipeline/batch_log.py error  M0 --pattern 64 --kind new --what "formula page cut as Q1" --fix "extract: skip formula list page"
    python3 pipeline/batch_log.py error  M0 --pattern 12 --kind repeat --what "..." --fix "..."
    python3 pipeline/batch_log.py tokens M0 1850000 --note "explain-usage at chat end"
    python3 pipeline/batch_log.py tick   M1 "fixing class 181: picture-cell headings"   # what I do now (every step)
    python3 pipeline/batch_log.py now                            # last task + its time + time now (read on resume)
    python3 pipeline/batch_log.py exclude M1 2026-11-16T17:29Z 2026-11-17T09:56Z --note "usage limit"   # a pause
    python3 pipeline/batch_log.py show   M0
    python3 pipeline/batch_log.py report                         # rewrite docs/BATCH_LOG.md

Phases: build = GitHub/pipeline build; claude1 = Claude pass 1 (check + fix); claude2 = Claude pass 2
(re-check after the rebuild, prepare the round); review = Dhruv's round (recorded for the calendar, NOT
counted in "our time"); fix = fixes after Dhruv's round + rebuild + approve. Times are UTC.
Pauses are not work (Dhruv, M1): every command records an event (tick = the task in hand); inside a phase a gap of
more than PAUSE_MIN minutes between two events counts as a pause, and `exclude` takes out a known pause. Tick at every
step, so a long real wait (a GitHub run) is never mistaken for a pause: tick when it starts and when it ends.
"""
import datetime, json, os, subprocess, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

DIR = os.path.join(paths.ROOT, 'review', 'cycle')
LOG = os.path.join(paths.ROOT, 'docs', 'BATCH_LOG.md')
PHASES = ['build', 'claude', 'claude1', 'claude2', 'review', 'fix']   # 'claude' = the ONE check round (round 29+); claude1/2 kept for old records
OURS = ['build', 'claude', 'claude1', 'claude2', 'fix']          # Dhruv's review time is not ours
PAUSE_MIN = 45
NOW = os.path.join(DIR, 'NOW.json')                 # last task of any batch: read first when a chat resumes
REPO = os.environ.get('GITHUB_REPOSITORY', 'dhruvashara07/Exam-bank')


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))


def path(b):
    return os.path.join(DIR, f'{b}.json')


def load(b):
    if not os.path.exists(path(b)):
        sys.exit(f'no batch {b}: run start first')
    return json.load(open(path(b)))


def save(r, task=None):
    os.makedirs(DIR, exist_ok=True)
    ev = r.setdefault('events', [])
    ev.append({'at': now(), 'task': task or ' '.join(sys.argv[1:4])})
    json.dump(r, open(path(r['batch']), 'w'), indent=1, ensure_ascii=False)
    json.dump({'batch': r['batch'], 'at': ev[-1]['at'], 'task': ev[-1]['task']}, open(NOW, 'w'), ensure_ascii=False)


_R = {}


def minutes(spans, r=None):
    """Active minutes of the spans: minus excluded pauses, minus gaps > PAUSE_MIN between events (when events exist)."""
    r = r or _R
    ev = sorted(ts(e['at']) for e in r.get('events', []))
    ex = [(ts(x['from']), ts(x['to'])) for x in r.get('excluded', [])]
    t = 0.0
    for s in spans:
        if not s.get('end'):
            continue
        a, b = ts(s['start']), ts(s['end'])
        pts = [a] + [e for e in ev if a < e < b] + [b]
        for p0, p1 in zip(pts, pts[1:]):
            g = (p1 - p0).total_seconds() / 60
            if len(pts) > 2 and g > PAUSE_MIN:
                continue                                  # no event for that long: a pause, not work
            for x0, x1 in ex:
                o = (min(p1, x1) - max(p0, x0)).total_seconds() / 60
                if o > 0:
                    g -= o
            t += max(0.0, g)
    return round(t, 1)


def args_after(a, flag, default=None):
    return a[a.index(flag) + 1] if flag in a else default


def cmd_start(a):
    b = a[0]
    sessions = a[a.index('--sessions') + 1:] if '--sessions' in a else []
    r = {'batch': b, 'subject': args_after(a, '--subject', '0607'), 'sessions': sessions, 'created': now(),
         'phases': {p: [] for p in PHASES}, 'github_runs': [], 'counts': {}, 'errors': [], 'tokens': []}
    save(r); print('started', b, ' '.join(sessions))


def cmd_phase(a):
    b, ph, what = a[0], a[1], a[2]
    assert ph in PHASES, PHASES
    r = load(b); spans = r['phases'].setdefault(ph, [])
    if what == 'start':
        spans.append({'start': now(), 'end': None})
    else:
        open_ = [s for s in spans if not s['end']]
        if not open_:
            sys.exit(f'{ph} has no open span')
        open_[-1]['end'] = now()
        if '--note' in a:
            open_[-1]['note'] = args_after(a, '--note')
    _R.clear(); _R.update(r)
    save(r); print(b, ph, what, f"{minutes(spans, r)} min so far")


def cmd_gh(a):
    b, ids = a[0], a[1:]
    r = load(b)
    for i in ids:
        j = json.loads(subprocess.run(['gh', 'api', f'repos/{REPO}/actions/runs/{i}'], capture_output=True,
                                      text=True, check=True).stdout)
        start, end = j.get('run_started_at') or j['created_at'], j['updated_at']
        run = {'id': int(i), 'name': j['name'], 'branch': j['head_branch'], 'conclusion': j['conclusion'],
               'start': start, 'end': end, 'minutes': round((ts(end) - ts(start)).total_seconds() / 60, 1)}
        r['github_runs'] = [x for x in r['github_runs'] if x['id'] != run['id']] + [run]
        print(run['name'], run['conclusion'], run['minutes'], 'min')
    save(r)


def cmd_count(a):
    r = load(a[0])
    for kv in a[1:]:
        k, v = kv.split('=', 1)
        r['counts'][k] = int(v) if v.isdigit() else v
    save(r); print(r['counts'])


def cmd_error(a):
    r = load(a[0])
    e = {'pattern': args_after(a, '--pattern'), 'kind': args_after(a, '--kind', 'new'),
         'what': args_after(a, '--what', ''), 'fix': args_after(a, '--fix', ''),
         'found_by': args_after(a, '--by', 'claude'), 'at': now()}
    assert e['kind'] in ('new', 'repeat'), 'kind: new | repeat'
    r['errors'].append(e); save(r); print('recorded', e['kind'], e['pattern'])


def cmd_tokens(a):
    r = load(a[0])
    r['tokens'].append({'n': int(a[1]), 'note': args_after(a, '--note', ''), 'at': now()})
    save(r); print('tokens', sum(t['n'] for t in r['tokens']))


def cmd_tick(a):
    r = load(a[0]); task = ' '.join(a[1:]) or 'tick'
    last = (r.get('events') or [{}])[-1]
    save(r, task)
    gap = (ts(now()) - ts(last['at'])).total_seconds() / 60 if last.get('at') else 0
    print(f"{now()}  {task}  (last: {last.get('task', '-')} {gap:.0f} min ago{' - counted as a pause' if gap > PAUSE_MIN else ''})")


def cmd_now(a):
    if not os.path.exists(NOW):
        print('no task recorded'); return
    n = json.load(open(NOW)); gap = (ts(now()) - ts(n['at'])).total_seconds() / 60
    print(f"now {now()} | last task ({n['batch']}): {n['task']} at {n['at']} ({gap:.0f} min ago)")


def cmd_exclude(a):
    r = load(a[0])
    r.setdefault('excluded', []).append({'from': a[1], 'to': a[2], 'note': args_after(a, '--note', '')})
    save(r, f'exclude {a[1]}..{a[2]}'); print('excluded', a[1], a[2])


def summary(r):
    _R.clear(); _R.update(r)
    m = {p: minutes(r['phases'].get(p, []), r) for p in PHASES}
    ghm = round(sum(x['minutes'] for x in r['github_runs']), 1)
    ours = round(sum(m[p] for p in OURS), 1)
    new = sum(1 for e in r['errors'] if e['kind'] == 'new')
    rep = sum(1 for e in r['errors'] if e['kind'] == 'repeat')
    tok = sum(t['n'] for t in r['tokens'])
    return m, ghm, ours, new, rep, tok


def cmd_show(a):
    r = load(a[0]); m, ghm, ours, new, rep, tok = summary(r)
    print(f"{r['batch']} ({r['subject']}: {' '.join(r['sessions'])})")
    for p in PHASES:
        print(f"  {p:8} {m[p]:7.1f} min" + ('   (Dhruv, not counted)' if p == 'review' else ''))
    print(f"  github   {ghm:7.1f} min in {len(r['github_runs'])} runs")
    print(f"  ours     {ours:7.1f} min   errors new {new} repeat {rep}   tokens {tok or 'n/a'}")
    print('  counts  ', r['counts'])


def cmd_report(a):
    rs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(DIR, '*.json'))) if os.path.basename(f) != 'NOW.json']
    L = ['# Batch log (generated by pipeline/batch_log.py report; do not edit by hand)', '',
         'Minutes are active time (pauses / usage limits not counted). "Ours" = build + Claude + fix (Dhruv\'s review time not counted).', '',
         '| Batch | Sessions | Papers | Build | GitHub | Claude 1 | Claude 2 | Fix | Ours | Round items | New errors | Repeats | Tokens |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rs:
        m, ghm, ours, new, rep, tok = summary(r)
        c = r['counts']
        L.append(f"| {r['batch']} | {' '.join(r['sessions'])} | {c.get('papers', '')} | {m['build']} | {ghm} | "
                 f"{m['claude'] + m['claude1']} | {m['claude2']} | {m['fix']} | {ours} | {c.get('round_items', '')} | {new} | {rep} | {tok or 'n/a'} |")
    L += ['', '## Errors per batch (new = first time, repeat = a pattern seen before: the doc or the fix failed)', '']
    for r in rs:
        if not r['errors']:
            continue
        L.append(f"### {r['batch']}")
        for e in r['errors']:
            L.append(f"- [{e['kind']}] pattern {e['pattern']}: {e['what']} → {e['fix']} (found by {e['found_by']})")
        L.append('')
    reps = [(r['batch'], e) for r in rs for e in r['errors'] if e['kind'] == 'repeat']
    L += ['## Repeats to act on', '']
    L += [f"- {b}: pattern {e['pattern']} came back: {e['what']}" for b, e in reps] or ['- none']
    open(LOG, 'w').write('\n'.join(L) + '\n')
    print('wrote', os.path.relpath(LOG, paths.ROOT), len(rs), 'batches')


if __name__ == '__main__':
    c, a = sys.argv[1], sys.argv[2:]
    {'start': cmd_start, 'phase': cmd_phase, 'gh': cmd_gh, 'count': cmd_count, 'error': cmd_error,
     'tokens': cmd_tokens, 'show': cmd_show, 'report': cmd_report, 'tick': cmd_tick, 'now': cmd_now,
     'exclude': cmd_exclude}[c](a)
