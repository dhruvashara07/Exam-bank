# exam-bank

Private question bank for Dhruv's classes. Phase 1: Cambridge IGCSE Physics 0625, 2025–2026.
Every question is cut from the original papers as exact vector SVGs (original layout and answer
space), with its structure, marks and mark scheme in JSON. Git is the master copy; Cloudinary holds
the images and MongoDB a searchable copy for the website.

## Where things are

```
inbox/                 drop new PDFs here from your phone (any Cambridge name, e.g. 0625_s25_qp_41.pdf)
raw/0625/2025-MJ/      original PDFs, renamed qp_41.pdf / ms_41.pdf   (FM = Feb/Mar, MJ = May/Jun, ON = Oct/Nov)
bank/
  index.json           one row per question: id, file, type, marks, parts, answer, topic, review status
  cambridge-igcse/
    0625-physics/
      2025-MJ/
        p41/                         paper 4, variant 1
          paper.json                 paper details + list of question ids
          q01/
            0625_2025MJ_41_q01.json  the question
            question/                exact printed pieces:   0625_2025MJ_41_q01_a-ii_s1.svg
            figures/                 diagrams/tables alone:  0625_2025MJ_41_q01a_fig1-1.svg
            markscheme/              mark-scheme rows:       0625_2025MJ_41_q01_a-ii_ms1.svg
review/queue.json      items the pipeline is unsure about
pipeline/              the scripts (see pipeline/README.md)
docs/SETUP.md          one-time Cloudinary + MongoDB setup
```

File names always start with the question id (`syllabus_yearSession_paperVariant_qNN`), so a
single SVG is identifiable on its own. Cloudinary uses the same path as the public id, so its
folders mirror `bank/`.

## How it runs (no laptop needed)
Upload PDFs into `inbox/` with the GitHub app → the **Question bank** Action files them, cuts the
questions, commits them to `bank/`, uploads SVGs to Cloudinary and syncs MongoDB.
