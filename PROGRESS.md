# Progress

Read this first in every session. Update it before ending a session.

## Done
- 2026-10-29: 134 PDFs (0625 Physics, Feb/Mar 2025 to May/Jun 2026) in `raw/`.
- 2026-10-29: Pipeline v1 (`pipeline/`): watermark removal, question/part splitting, exact SVG pieces,
  figures, mark-scheme linking, test-paper builder. All 66 papers processed: 1,200 questions,
  every paper's marks match its cover total. 21 items in `review/queue.json` (20 MCQs with
  diagram options, 1 mark-scheme row). `pipeline/coverage.py`: all 923 question pages fully covered
  (5 remaining hits are curve control points, checked by eye).
- Review page (phone): https://claude.ai/artifact/LGic38rQwKjkZze9jL1zmq — feedback is stored in its
  database collection `feedback` (doc id = question id). Read it with ArtifactData before changing the pipeline.
- GitHub Action `.github/workflows/sync.yml` written; needs secrets (see docs/SETUP.md).

## Next
1. Dhruv reviews flagged items (review page) and gives feedback on a sample of unflagged ones.
2. GitHub Action: upload `assets/` to Cloudinary, sync `data/` into MongoDB (QuestionV2) using repo Secrets.
3. Alt text for figures; topics/keywords from the 0625 syllabus.
4. Test-paper builder on the website.

## How to run
    pip install pymupdf pikepdf
    python3 pipeline/run.py                     # all papers
    python3 pipeline/run.py 2025-MJ/41          # one paper
    python3 pipeline/build_test.py out.pdf 0625_2025MJ_41_q01 0625_2025MJ_41_q05:c --ms
