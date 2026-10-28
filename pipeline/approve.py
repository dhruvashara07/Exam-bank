"""Mark papers as checked, so the GitHub Action sends them to MongoDB.

    python3 pipeline/approve.py 0625_2025MJ_41 0625_2025MJ_42 --note "checked: marks, coverage, figures"
    python3 pipeline/approve.py --pending            # list papers waiting for a check
    python3 pipeline/approve.py --revoke 0625_2025MJ_41
Re-processing a paper (pipeline/run.py) removes its approval automatically.
"""
import json, os, subprocess, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import paths


def all_papers():
    return {paths.paper_id(json.load(open(f))): f for f in paths.paper_files()}


def pending():
    a = paths.approvals()
    return [p for p in sorted(all_papers()) if p not in a]


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] == '--pending':
        for p in pending():
            print(p)
        sys.exit(0)
    a = paths.approvals()
    if args[0] == '--revoke':
        for p in args[1:]:
            a.pop(p, None)
        paths.save_approvals(a); sys.exit(0)
    note = ''
    if '--note' in args:
        i = args.index('--note'); note = args[i + 1]; args = args[:i] + args[i + 2:]
    known = all_papers()
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=paths.ROOT, capture_output=True, text=True).stdout.strip()
    for p in args:
        if p not in known:
            sys.exit(f'unknown paper {p}')
        a[p] = {'at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'by': 'claude', 'commit': commit, 'note': note}
    paths.save_approvals(a)
    print(f'approved {len(args)}; pending {len(pending())}')
