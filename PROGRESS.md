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
- Review page: https://claude.ai/artifact/LGic38rQwKjkZze9jL1zmq — round 1 feedback in collection
  `feedback`, round 2 (9 fixed + 15 new MCQ figure checks) in `feedback_r2`. Doc id = question id.

## Waiting on Dhruv
1. GitHub secrets `MONGO_URI`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`; Atlas network access; first run of "Question bank"
   with "Upload every SVG again" ticked (docs/SETUP.md).
2. Review round 2.
3. May/Jun 2026 variant 7: mark schemes 17 and 27 exist, question papers missing.

## Next
1. Read `feedback_r2`, fix anything wrong (the daily check does this too).
2. Topics/subtopics/keywords from the 0625 syllabus; alt text for figures.
3. Other subjects (Chemistry, Biology, Maths), then AS/A level, IB.
4. Test-paper builder on the website (reads MongoDB `question_bank.questions`).

## How to run
    pip install -r requirements.txt
    python3 pipeline/run.py                          # all papers (~3.5 min)
    python3 pipeline/run.py 2025-MJ/41               # one paper
    python3 pipeline/build_test.py out.pdf 0625_2025MJ_41_q01 0625_2025MJ_41_q05:c --ms
    python3 pipeline/coverage.py                     # check nothing on the pages was missed

## Daily check log
One line per run: date, pending papers checked/approved, feedback handled, fixes, notes.
- 2026-10-29 (setup): 66 papers approved by hand after the full check. Review round 2 published, not yet answered.
  Safe push (`pipeline/push.sh`) + CLAUDE.md added so the Action, this chat and the daily check never clash.
  Action runs fail at the MongoDB step until Dhruv adds the secrets (expected).
