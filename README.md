# exam-bank

Private question bank for Dhruv's classes. Phase 1: Cambridge IGCSE Physics 0625, 2002–2026.
Every question is stored as data that redraws it exactly as printed (`store/`, docs/STORE_DESIGN.md):
words with position/size/style, lines, figures as separate files at true size, the mark-scheme rows of
each part, MCQ options. Git is the master copy; the database and file host are loaded at the end.

## Where things are

```
inbox/                 drop new PDFs here from your phone (any Cambridge name, e.g. 0625_s25_qp_41.pdf)
raw/manifest.json      the original PDFs, stored in GitHub Releases (raw-0625-2015, ...), not in git;
                       `pipeline/raw_store.py fetch` puts them in raw/0625/2025-MJ/qp_41.pdf etc.
                       (FM = Feb/Mar, MJ = May/Jun, ON = Oct/Nov; before 2009: qp_03 = component 3)
store/                 THE DATA SET: store/cambridge-igcse/0625-physics/2025-MJ/p41/
                         q01.json ... one per question (layout, mark scheme, options, figures' labels)
                         figures/  one file per figure label (SVG, photos as PNG), glyphs/ odd symbols
bank/                  the pipeline's cut records (where each piece is on the page, checks, links)
  index.json           one row per question
  cambridge-igcse/0625-physics/2025-MJ/p41/paper.json, q01/0625_2025MJ_41_q01.json
review/                checks (checks/, store/), Claude checks, approvals (= finalised), rounds, batches,
                       backlog.json (older years, docs/BACKLOG.md)
pipeline/              the scripts (see pipeline/README.md)
site/                  the tracker website (GitHub Pages): batches, papers drawn from store/, report problems
docs/                  STORE_DESIGN.md, DAILY_CHECK.md, BACKLOG.md, UPLOAD.md, SETUP.md
CLAUDE.md              rules for every Claude session (safe push etc.)
```

## How it runs (no laptop needed)
Upload PDFs into `inbox/` with the GitHub app → the **Question bank** Action files them, cuts the
questions, builds `store/`, checks every stored piece against the page and commits. A scheduled Claude
session looks at every page, builds a review round for Dhruv and approves (finalises) the paper.

## Review website
https://dhruvashara07.github.io/Exam-bank/ (rebuilt after every Action run by `.github/workflows/site.yml`).
Papers by year and session, each question exact / editable / side by side with its mark scheme, a
"To check" list, and "Report a problem" (opens a GitHub issue labelled `review` that the daily check reads).
