# Scheduled Claude check (twice a day, 9:47 am and 10:47 pm IST)

A fresh Claude session runs this. Everything it needs is in the repo: this file, `PROGRESS.md`,
`CLAUDE.md`, `pipeline/README.md`. Goal: every paper reaches MongoDB only after (1) the automatic checks,
(2) Claude looked at every page, (3) Dhruv's review round, and with the pipeline (not single files) fixed
whenever something is wrong.

```
upload (Dhruv) -> Action: store PDFs, process, auto-check, batch record      [docs/UPLOAD.md]
   -> THIS CHECK: Claude-check papers -> review round -> read answers -> fix -> approve
   -> Action: Cloudinary + MongoDB -> 'published'
```
Stages are worked out from files (`pipeline/batch.py`): processed (bank/), auto_checked (review/checks/),
claude_checked / needs_fix (review/claude/), your_review (open round in review/rounds/), approved
(review/approvals/), published (review/published.json).

## 1. Get ready
```
cd /home/claude && [ -d exam-bank ] || git clone https://github.com/dhruvashara07/Exam-bank.git exam-bank
cd exam-bank && git pull -q --rebase
python3 -c "import pymupdf, pikepdf, playwright" || pip install -r requirements.txt --break-system-packages
python3 pipeline/batch.py status
```
Read `CLAUDE.md` and the end of `PROGRESS.md`. Original PDFs are in GitHub Releases, not git: fetch the
papers you work on with `python3 pipeline/raw_store.py fetch 0625/2025-MJ/41 ...` (or a year: `fetch 2019`).
If clone/push fails for access reasons, attach the repo (add_repo dhruvashara07/Exam-bank, push access).

## 2. What is new
- Action runs: `gh api "repos/dhruvashara07/Exam-bank/actions/runs?per_page=10"`; for a failed or
  warning run read the annotations: `gh api repos/dhruvashara07/Exam-bank/check-runs/<job id>/annotations`
  (logs are not readable from here). Branches named `upload*`/`*-patch-*` still existing = an upload with
  unrecognised file names: rename in raw/ by hand (`raw/<syl>/<year>-<FM|MJ|ON>/<qp|ms>_<pv>.pdf`) and process.
- Dhruv's answers: open rounds are `review/rounds/<n>.json` with `"status": "open"`. Read the answers with
  ArtifactData `list`, url = `review_url` in `review/portal.json`, collection `feedback_r<n>`
  (doc id = question id: verdict ok|wrong, issues, note).
- Website reports: `gh api "repos/dhruvashara07/Exam-bank/issues?labels=review&state=open"`.
- Golden set still identical: `python3 pipeline/golden.py check` (must say 0 with changed cuts).

## 3. Answers first
For every "wrong": look at the question (contact sheet: `python3 pipeline/check.py <paper>`), find the
cause, fix the pipeline, re-run the affected papers (`python3 pipeline/run.py <papers>`), then
`python3 pipeline/checks.py <papers>` and `python3 pipeline/golden.py check`. A change that alters a golden
paper: look at that paper again, then `golden.py add` it. Save the answers to a file and close the round
when every item is answered (or the round is older than 3 days):
`python3 pipeline/review_round.py close <n> answers.json`. Fixed items go into the next round as "Flagged"
with the reason "fixed: ...", so Dhruv sees the fix.

## 4. Claude-check new papers (oldest batch first, up to 40 papers per run)
For each paper at stage `auto_checked`:
1. `python3 pipeline/overview.py <papers>` → `out/overview/<paper>.png`: every question page with its cut
   boxes. **Open and look at every overview.** Check: each box starts at its label and ends before the
   next; nothing printed outside a box; no footer, barcode or "Turn over" inside; figure crops (orange)
   hold the whole diagram; question numbers in order; marks in the header match the cover.
2. Read `review/checks/<paper>.json`: blocking problems (marks, coverage, piece) must be zero (fix the
   pipeline if not); warnings (figure crop, editable text below 97%) are fixed in the pipeline when you can,
   otherwise they go into the review round (review_round.py picks them up); flags are
   Cambridge labelling differences or errata: look at those questions' contact sheets
   (`python3 pipeline/check.py <paper>`), they go into the review round.
3. Record the result: `python3 pipeline/claude_check.py ok <papers> --note "what you looked at"` or
   `python3 pipeline/claude_check.py needs_fix <paper> --note "exactly what is wrong"` (a defect you could
   not fix this run). `python3 pipeline/claude_check.py list` shows papers waiting for this step.
   The record holds the paper's cut hash: a later re-cut sends the paper back to this step by itself.
Rules: render SVGs with Chromium (`review_assets.svg_img`), never MuPDF (it drops dashed lines).
After any pipeline change re-run the affected papers and the golden check before going on.

## 5. Review round for Dhruv (when papers are Claude-checked and no round is open)
```
python3 pipeline/review_round.py new <n> <claude-checked paper ids> --sample 2
```
(n = last round + 1). Publish `out/review/round_<n>/` to the review page with the Artifact tool:
`file_path` = `site/review/index.html`, `url` = review_url from `review/portal.json`, `files` = every file
under `out/review/round_<n>/` at its relative path (round.json, items.json, <qid>/*.jpg), and `null` for
the previous round's image paths (one version holds at most 511 files). Keep capabilities as they are (db).

## 6. Approve
A paper is approved when: Claude result `ok`, no blocking automatic problem, and its items in the review round are
answered ✓ — or the round has been open 3 days and the paper had only random-sample items (no flags).
```
python3 pipeline/approve.py <ids> --note "overview checked; checks clean; round <n> ✓ (k items)"
```
(`approve.py` stores the cut hash too: re-running the pipeline keeps an approval when the pieces, marks,
answers and mark-scheme rows did not change; a changed cut makes the paper pending again.)
Then log one line in `PROGRESS.md` ("Daily check log") and push with `pipeline/push.sh "message"`
(never plain `git push`; end the message with the Co-Authored-By / Claude-Session lines). The push runs
the Action → Cloudinary + MongoDB → `review/published.json` → stage 'published'.

## 7. Tell Dhruv (only if something happened)
A short push notification, plain words, for his phone: what came in, what was approved/published,
what was fixed, and the review page link if a new round is waiting.
If nothing is pending: one log line, push, no notification.

## Never
- Never put keys in the repo or in chat; they live in GitHub Secrets.
- Never delete files in `raw/` or Releases; never force-push; never rewrite history.
- Never write to MongoDB or Cloudinary directly; the Action does that.
- Fix the pipeline, not single JSON files.
