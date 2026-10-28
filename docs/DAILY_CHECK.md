# Daily check (Claude, scheduled task)

A scheduled Claude session runs this every day. It is a fresh session: everything it needs to know is
in this repo (this file, `PROGRESS.md`, `pipeline/README.md`). Goal: nothing reaches MongoDB/the website
without a careful check, and results are right first time.

How papers flow: Dhruv uploads PDFs to `inbox/` → GitHub Action files them into `raw/`, cuts them into
`bank/` and uploads SVGs to Cloudinary → the paper is **pending** → this check looks at it → `approve.py`
→ the Action syncs it to MongoDB. Re-cutting a paper (`run.py`) makes it pending again.

## 1. Get ready
```
cd /home/claude && [ -d exam-bank ] || git clone https://github.com/dhruvashara07/Exam-bank.git exam-bank
cd exam-bank && git pull -q
python3 -c "import pymupdf, pikepdf, playwright" || pip install -r requirements.txt --break-system-packages
```
Read `PROGRESS.md` (especially "Daily check log" at the end: what was last checked).
If git clone/pull fails for access reasons, attach the repo (add_repo dhruvashara07/Exam-bank, push access).

## 2. What is new
- `python3 pipeline/approve.py --pending` → papers waiting for a check.
- `gh run list --limit 5` (or the GitHub API) → did the last "Question bank" Action runs succeed? A failure
  in the Cloudinary/MongoDB steps right after setup usually means a missing secret; report it, don't guess.
- Review page https://claude.ai/artifact/LGic38rQwKjkZze9jL1zmq: read the newest feedback collection
  (`feedback`, `feedback_r2`, ... — doc id = question id, fields verdict/note) with ArtifactData. Anything
  marked wrong since the last log entry is work to do.
- `ls inbox/` — files left there have names the filer did not understand: rename them in raw/ by hand
  (`raw/<syl>/<year>-<FM|MJ|ON>/<qp|ms>_<pv>.pdf`) and process them.

If nothing is pending, no feedback is new and the Action is fine: add one log line, commit, stop. No notification.

## 3. Check each pending paper
`python3 pipeline/check.py` (or with paper ids). It prints, per paper: marks found vs cover total, flagged
items, uncovered ink, and writes contact sheets `out/check/<paper>/sheet_NN.jpg`.
Each sheet row = original page (uncleaned, so barcodes appear there; boxes = how it was cut) | rebuilt
question | figures. **Open and look at every sheet** (Read the jpg). Check:
- marks found == cover total; every question number present, in order; no question split wrongly
- part labels (a)(b)(i)(ii) match the paper; each part's own answer space (dotted lines, answer line, grid) is in it
- nothing cut off at any edge; no Cambridge barcode, corner marks or footer in the rebuilt column
- figures: complete (axes, tick labels, A–D labels, dashed/dotted lines, hatching, dots), nothing from the text inside
- MCQ: an answer letter (header shows answer=); structured: mark-scheme rows attached (see the JSON if unsure)
- uncovered ink reported by coverage: look at that spot on the page; curve control points are harmless
- new paper types (a new subject, AS/A level, IB) need extra care: layouts differ

## 4. Fix, don't patch
- Fix problems in the pipeline so they are fixed for every paper, not by editing one JSON.
- After a pipeline change: re-run **all** papers (`python3 pipeline/run.py`, ~3.5 min for 66), then
  compare with before: marks still match everywhere (`grep -v` the run log), `python3 pipeline/coverage.py`,
  and look at sheets of a sample of changed questions (figure counts, sizes). A full re-run makes every
  paper pending: re-approve the ones whose output did not change in substance, with a note.
- Render SVGs with Chromium (playwright) when looking at them; MuPDF's SVG reader ignores dashed strokes.
- If something needs Dhruv's eye (you are not sure what's right), add it to a new review round:
  `review_assets.render_items(out_dir, [(qid, 'flagged'), ...], {qid: [reason]})`, copy the review page
  `index.html` from the last round, switch it to a new collection `feedback_rN`, publish to the same
  artifact URL with the Artifact tool, and say so in the notification.

## 5. Approve and record
```
python3 pipeline/approve.py <paper ids> --note "what was checked / fixed"
```
Approve a paper only after looking at all its sheets. Leave a paper pending (and say why) if it has a
defect you could not fix. Then append to the "Daily check log" in `PROGRESS.md`, commit (end the message
with the Co-Authored-By / Claude-Session lines) and `git push`. The push triggers the Action → MongoDB.

## 6. Tell Dhruv (only if something happened)
Short and plain: which papers came in, approved or not, what was fixed, what needs him (review page
items, missing mark schemes, Action failures). He reads on his phone.

## Never
- Never put keys in the repo or in chat; they live in GitHub Secrets.
- Never delete files in `raw/`; never force-push; never rewrite history.
- Never write to MongoDB or Cloudinary directly; the Action does that.
