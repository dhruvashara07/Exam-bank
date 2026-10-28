#!/usr/bin/env bash
# Safe commit + push. EVERY writer uses this: this chat, the daily Claude check, Claude Code on a
# laptop, and the GitHub Action. It never force-pushes and never loses anyone's work:
#   1. waits while a "Question bank" Action is running (it may be about to push its own commit)
#   2. commits, then pulls with rebase and pushes; retries if someone pushed in between
#   3. a clash in a generated file (bank/index.json, review/queue.json) is rebuilt/merged automatically;
#      a clash anywhere else stops with a message (nothing is pushed, nothing is lost)
# Usage: pipeline/push.sh "commit message"        (SKIP_WAIT=1 inside the Action itself)
set -uo pipefail
cd "$(dirname "$0")/.."
msg="${1:?commit message}"
REPO=dhruvashara07/Exam-bank

if [ -z "${SKIP_WAIT:-}" ] && command -v gh >/dev/null 2>&1; then
  for i in $(seq 1 60); do
    busy=$(gh run list -R "$REPO" --workflow bank.yml --limit 10 --json status \
           -q '[.[] | select(.status=="in_progress" or .status=="queued")] | length' 2>/dev/null || echo 0)
    [ "$busy" = "0" ] && break
    echo "a Question bank Action is running; waiting 30 s ($i/60)"; sleep 30
  done
fi

git add -A
git diff --cached --quiet || git commit -q -m "$msg"

resolve_generated() {
  local files; files=$(git diff --name-only --diff-filter=U)
  for f in $files; do
    case "$f" in
      bank/index.json|review/queue.json) ;;
      *) echo "CONFLICT in $f: needs a human/Claude decision. Rebase aborted, your commit is kept locally."
         git rebase --abort; return 1 ;;
    esac
  done
  python3 - <<'PY'
import json, subprocess, sys
sys.path.insert(0, 'pipeline')
def ver(stage, path):
    try: return json.loads(subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True, text=True, check=True).stdout)
    except Exception: return []
q = {x['id']: x for x in ver(2, 'review/queue.json') + ver(3, 'review/queue.json')}
json.dump(list(q.values()), open('review/queue.json', 'w'), ensure_ascii=False, indent=1)
import run; run.write_index()
PY
  git add bank/index.json review/queue.json
  GIT_EDITOR=true git rebase --continue
}

for attempt in 1 2 3 4 5 6; do
  if git pull -q --rebase origin main; then
    if git push -q origin main; then echo "pushed"; exit 0; fi
  elif git diff --name-only --diff-filter=U | grep -q .; then
    resolve_generated || exit 1
    git push -q origin main && { echo "pushed (generated files rebuilt)"; exit 0; }
  fi
  echo "push attempt $attempt failed; retrying"; sleep $((attempt * 5))
done
echo "could not push after 6 attempts"; exit 1
