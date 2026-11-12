"""Batch record for the subject cycle (docs/MATHS_PLAN.md): times per phase, GitHub run times, counts,
errors (new / repeat) and tokens. One file per batch: review/cycle/<batch>.json. docs/BATCH_LOG.md is
rebuilt from all of them by `report`, so the table is never typed by hand.

    python3 pipeline/batch_log.py start  M0 --subject 0607 --sessions 2014-MJ 2019-ON 2021-FM 2025-MJ
    python3 pipeline/batch_log.py phase  M0 build start         # build | claude1 | claude2 | review | fix
    python3 pipeline/batch_log.py phase  M0 build end  --note "26 papers"
    python3 pipeline/batch_log.py gh     M0 43252980978 ...     # add GitHub Action run times (REST API)
    python3 pipeline/batch_log.py count  M0 papers=26 questions=310 flags=41 round_items=18
    python3 pipeline/batch_log.py error  M0 --pattern 64 --kind new --what "formula page cut as Q1" --fix "extract: skip formula list page"
    python3 pipeline/batch_log.py error  M0 --pattern 12 --kind repeat --what "..." --fix "..."
    python3 pipeline/batch_log.py tokens M0 1850000 --note "explain-usage at chat end"
    python3 pipeline/batch_log.py show   M0
    python3 pipeline/batch_log.py report                         # rewrite docs/BATCH_LOG.md

Phases: build = GitHub/pipeline build; claude1 = Claude pass 1 (check + fix); claude2 = Claude pass 2
(re-check after the rebuild, prepare the round); review = Dhruv's round (recorded for the calendar, NOT
counted in "our time"); fix = fixes after Dhruv's round + rebuild + approve. Times are wall-clock UTC.
"""
import datetime, json, os, subprocess, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

DIR = os.path.join(paths.ROOT, 'review', 'cycle')
LOG = os.path.join(paths.ROOT, 'docs', 'BATCH_LOG.md')
PHASES = ['build', 'claude1', 'claude2', 'review', 'fix']
OURS = ['build', 'claude1', 'claude2', 'fix']          # Dhruv's review time is not ours
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


def save(r):
    os.makedirs(DIR, exist_ok=True)
    json.dump(r, open(path(r['batch']), 'w'), indent=1, ensure_ascii=False)


def minutes(spans):
    t = 0.0
    for s in spans:
        if s.get('end'):
            t += (ts(s['end']) - ts(s['start'])).total_seconds() / 60
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
    r = load(b); spans = r['phases'][ph]
    if what == 'start':
        spans.append({'start': now(), 'end': None})
    else:
        open_ = [s for s in spans if not s['end']]
        if not open_:
            sys.exit(f'{ph} has no open span')
        open_[-1]['end'] = now()
        if '--note' in a:
            open_[-1]['note'] = args_after(a, '--note')
    save(r); print(b, ph, what, f"{minutes(spans)} min so far")


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


def summary(r):
    m = {p: minutes(r['phases'][p]) for p in PHASES}
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
    rs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(DIR, '*.json')))]
    L = ['# Batch log (generated by pipeline/batch_log.py report; do not edit by hand)', '',
         'Minutes are wall clock. "Ours" = build + Claude 1 + Claude 2 + fix (Dhruv\'s review time not counted).', '',
         '| Batch | Sessions | Papers | Build | GitHub | Claude 1 | Claude 2 | Fix | Ours | Round items | New errors | Repeats | Tokens |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rs:
        m, ghm, ours, new, rep, tok = summary(r)
        c = r['counts']
        L.append(f"| {r['batch']} | {' '.join(r['sessions'])} | {c.get('papers', '')} | {m['build']} | {ghm} | "
                 f"{m['claude1']} | {m['claude2']} | {m['fix']} | {ours} | {c.get('round_items', '')} | {new} | {rep} | {tok or 'n/a'} |")
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
     'tokens': cmd_tokens, 'show': cmd_show, 'report': cmd_report}[c](a)
