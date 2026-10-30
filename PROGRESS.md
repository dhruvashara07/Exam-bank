# Progress

Read this first in every session. Update it before ending a session.

## Done
- 2026-10-29: 134 PDFs (0625 Physics, Feb/Mar 2025 to May/Jun 2026) in `raw/`.
- 2026-10-29: Pipeline v1: watermark removal, question/part splitting, exact SVG pieces, figures,
  mark-scheme linking, test-paper builder. 66 papers → 1,200 questions; every paper's marks match its cover.
- 2026-10-29: Review round 1 (57 items): 48 ok, 9 wrong. All 9 were dashed lines/hatching + 1 figure crop.
  Cause 1: review previews were rasterised by MuPDF, which ignores SVG `stroke-dasharray`; the SVGs
  themselves were right. Previews now rendered with Chromium. Cause 2: MCQ figure finder cut figures
  (zero-width lines ignored by fitz Rect union; hatch-pattern cells reported at fake positions; vertical
  gap limit). Rewritten: prose lines separate figures, labels attached, invisible ink dropped
  (pixel check), fraction-bar-only clusters ignored.
- 2026-10-29: Storage reorganised into `bank/` (one folder per question: JSON + question/, figures/,
  markscheme/ SVGs), `bank/index.json`. Cloudinary public id = `question_bank/` + path inside bank/.
  MongoDB: database `question_bank`, collections `papers`, `questions` (our format, not QuestionV2 —
  Dhruv adapts the website). Only approved papers (`review/approvals/<paper>.json`) are synced.
- 2026-10-29: Daily scheduled Claude check set up (docs/DAILY_CHECK.md, `pipeline/check.py`,
  `pipeline/approve.py`). All 66 current papers approved.
- 2026-10-29: `.github/workflows/bank.yml`: upload PDFs to `inbox/` from phone → filed to `raw/` →
  processed → committed → Cloudinary + MongoDB. Full re-run takes ~3.5 min.
- 2026-10-29: **2015–2024 added**: 477 papers (Feb/Mar 2015 – May/Jun 2026), 8,624 questions. Every
  paper's marks match its cover; pixel coverage 0 lost ink on 6,545 pages; no footer/barcode/notice text
  inside any piece; no overlapping pieces; 59 papers (one per year x paper number) sampled visually.
  Old-paper support: 2015 numbering, standard totals (no cover total before 2020), rotated/landscape and
  column-format mark schemes, two-column MCQ keys, erratum pages, A3 and 612x859 pages scaled to A4,
  mark schemes drawn in clipped pieces (text rebuilt from characters), MS label typos ('9b(i)',
  '(b)(ii)', '7(a)((i)', '3(b)(i)1.', '(h)(l)' ranges), centred 'Question N is on the back page.' notices.
  Review queue: 34 items, all genuine Cambridge labelling differences between paper and mark scheme
  (e.g. paper 2(b)/(c) = MS 2(b)(i)/(ii)), 1 erratum, 1 question removed by Cambridge (2024MJ_21 q14).
- 2026-10-29: **Editable layer** (`pipeline/editable.py`, run by run.py): `content` blocks per node:
  text (HTML b/i/sub/sup, LaTeX `\(\frac{}{}\)`), lists, tables (real cells), figure refs, answer
  space, marks, MCQ options (text, options table, or "drawn in the diagram"). Exact SVGs stay the master.
- 2026-10-29: **Review website** `site/` → GitHub Pages (`.github/workflows/site.yml`), pictures from
  Cloudinary; "Report a problem" opens a GitHub issue labelled `review`.
- 2026-10-29: **PDFs to GitHub Releases** prepared (`pipeline/raw_store.py`, `.github/workflows/raw.yml`,
  branch `incoming-raw`); new PDFs are git-ignored in main.
- Review page: https://claude.ai/artifact/LGic38rQwKjkZze9jL1zmq — round 1 feedback in collection
  `feedback`, round 2 (9 fixed + 15 new MCQ figure checks) in `feedback_r2`. Doc id = question id.

- 2026-10-30: **Professional flow** (agreed with Dhruv, portal option A, twice-daily check, editable = text
  only): `upload.yml` (PDFs on an upload branch → Releases → process → checks → batch → main), batch tracker
  (`batch.py`, stages derived from files), automatic checks (`checks.py`: marks, coverage, page furniture,
  figure crops, editable-text score; figure/text are warnings), golden set (20 papers, `golden.py`),
  approvals and Claude checks tied to a cut hash (re-runs keep them when the cut is unchanged), review rounds
  (`review_round.py` + `site/review/index.html` on the review page), website Batches tab, `docs/UPLOAD.md`.
  Figure crops rebuilt from printed ink (tight ink + grow along lines); captions stay with their figure.
  All 477 papers: marks match, coverage 0, 0 blocking problems; 46 crop + 58 text warnings (of 8,624 questions,
  editable text mean 99.9% of printed words).

## Waiting on Dhruv
1. (done 2026-10-29: all 983 PDFs in Releases.)
2. Turn on GitHub Pages (Settings → Pages → Source: GitHub Actions) for the website.
3. Review round 3 (90 questions, review page link in review/portal.json). Round 2 was replaced by it.
4. May/Jun 2026 variant 7: mark schemes 17 and 27 exist, question papers missing.

## Next
1. Daily check: read Dhruv's round 3 answers (`feedback_r3`), fix anything marked wrong, approve the 2015–2024
   backlog by the rule in docs/DAILY_CHECK.md §6. 40 flagged questions did not fit round 3 (mostly editable-text
   warnings): they go into round 4 once round 3 is closed.
2. Website issues (label `review`), fix anything wrong.
2. Topics/subtopics/keywords from the 0625 syllabus; alt text for figures.
3. Other subjects (Chemistry, Biology, Maths), then AS/A level, IB.
4. Test-paper builder on the website (reads MongoDB `question_bank.questions`).

## How to run
    pip install -r requirements.txt
    python3 pipeline/raw_store.py fetch               # original PDFs from Releases
    python3 pipeline/run.py                          # all papers (~27 min for 477)
    python3 pipeline/run.py 2025-MJ/41               # one paper
    python3 pipeline/build_test.py out.pdf 0625_2025MJ_41_q01 0625_2025MJ_41_q05:c --ms
    python3 pipeline/coverage.py                     # check nothing on the pages was missed

## Daily check log
One line per run: date, pending papers checked/approved, feedback handled, fixes, notes.
- 2026-10-29 (setup): 66 papers approved by hand after the full check. Review round 2 published, not yet answered.
  Safe push (`pipeline/push.sh`) + CLAUDE.md added so the Action, this chat and the daily check never clash.
  Action runs fail at the MongoDB step until Dhruv adds the secrets (expected).
- 2026-10-29 10:xx IST: secrets added. Cloudinary rejected 62 SVGs ("Resource is invalid") = every SVG with
  >=1000 <use> (one per glyph). render.limit_uses: drop empty-glyph uses, inline glyph paths above 900.
  Pixel-identical (Chromium, 122 files). All 66 re-approved. Run logs are not readable from Claude's
  workspace: scripts report via GitHub annotations (gh api .../check-runs/<job>/annotations).
- 2026-10-29 14:xx IST (chat session): 2015–2024 processed (see Done). 2025–26 re-approved (66): only
  whitespace at cut edges, notices/barcodes excluded, better MS codes, tighter figures, editable layer.
  411 older papers pending for the daily check. Cleaned-PDF cache now also rebuilds when clean.py changes.
- 2026-10-29 22:xx IST: figure-crop fix (axis titles / centred labels were taken as prose, so 63 of 3,483
  figure crops were cut); full re-run, all checks clean, 2025–26 re-approved (question pieces unchanged).
  2015–2024 PDFs pushed to branch `incoming-raw` → Releases. Daily check paused while Dhruv and Claude agree
  the batch/portal plan (portal A: Pages + Claude review page; twice-daily check; text-only editable layer).
- 2026-10-30 00:xx IST (chat session): new flow built (see Done). 2025–26 re-approved (66, cut hash stored).
  411 older papers at 'auto checked'; Claude-checking them via overview images, newest first.
- 2026-10-30 12:xx IST (chat session): Claude check of all 411 backlog papers (overview of every page, newest
  first). Pipeline fixes found by it: a lone '[n]' printed level with the next label is now cut below the mark
  (+ check `piece: mark at the top`); 'Question continued on next side' is page furniture; a part label printed
  in the question-number column ('(e)' on 2020 FM 52 p4) is accepted when it is the next letter; figure crops:
  bullet lists, table captions under the table, key text ('= positive particles'), cells of ruled tables,
  split prose rows ('… × 10⁶' + 'km.') and caption-only crops fixed; crops never reach past their piece.
  Full re-run (JOBS=2, ~23 min): 477 papers, 0 blocking, golden 0 changed cuts; 21 papers re-cut (11 visibly,
  each looked at again), 2025 MJ 42 re-approved (0.3 pt shift). 411 papers recorded `claude_checked`.
  Review round 3 published (90 items: 72 flagged + 18 spot checks; `--max 90` keeps a page version under 511 files).

