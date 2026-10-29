"""Record Claude's visual check of papers (the 'Claude checked' stage).

    python3 pipeline/claude_check.py ok <paper ids...> --note "overview: all cuts at labels, figures whole"
    python3 pipeline/claude_check.py needs_fix <paper id> --note "q3(b) figure cut at the left"
    python3 pipeline/claude_check.py list                       # papers waiting for a Claude check

Writes review/claude/<paper>.json with the paper's cut hash: if the paper is re-cut later, the record no
longer counts and the paper is back at 'auto checked'.
"""
import datetime, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
import paths
from golden import cut_hash
import batch


if __name__ == '__main__':
    a = sys.argv[1:]
    note = ''
    if '--note' in a:
        i = a.index('--note'); note = a[i + 1]; del a[i:i + 2]
    index = batch.papers_index()
    if not a or a[0] == 'list':
        for pid in sorted(index):
            if batch.stage_of(pid, index) == 'auto_checked':
                print(pid)
        sys.exit(0)
    result, pids = a[0], a[1:]
    if result not in ('ok', 'needs_fix'):
        sys.exit('result must be ok or needs_fix')
    os.makedirs(paths.CLAUDE_CHECKS, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    for pid in pids:
        if pid not in index:
            sys.exit(f'unknown paper {pid}')
        rec = {'paper': pid, 'result': result, 'checked_at': now, 'cut': cut_hash(index[pid]),
               'pipeline_version': paths.PIPELINE_VERSION, 'note': note}
        with open(os.path.join(paths.CLAUDE_CHECKS, pid + '.json'), 'w') as f:
            json.dump(rec, f, indent=1)
    print(f'{len(pids)} papers recorded as {result}')
