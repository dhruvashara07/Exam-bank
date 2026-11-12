# Maths plan: Cambridge IGCSE International Mathematics 0607 (decided with Dhruv 2026-11-12)

Physics 0625 is finished (2002-2026 approved). Maths goes through the SAME pipeline, in the same repo, with
the same review page. This file is the plan; docs/PLAYBOOK.md has the steps of one batch; docs/START_HERE.md
is what every new chat reads first.

## 1. Decisions (Dhruv, 2026-11-12)
| Question | Decision |
| --- | --- |
| Syllabus | 0607 Cambridge International Mathematics (not 0580). |
| Repo | Same repo. Original PDFs in the same GitHub Releases (tags `raw-0607-<year>`). |
| Pipeline | Shared with physics (see 2). No copy. |
| Maths text | Editable text as LaTeX, shown with KaTeX on the site. A picture only when LaTeX cannot say it (graphs, constructions, diagrams). The exact SVG layout stays for printing, as for physics. |
| Batches | Pilot M0 first (4 sessions), then 3 years per batch, each batch in a NEW chat. |
| Cycle | GitHub build -> Claude pass 1 -> Claude pass 2 -> Dhruv's review round -> fix, build, approve. |
| Tracking | Times per phase (not Dhruv's), GitHub run times, tokens if possible, errors new/repeat + fix, per batch. |
| Docs | Updated after EVERY batch without being asked. |
| Skill | A "batch cycle" skill for these steps (approved by Dhruv). |
| MongoDB / Cloudinary | Still nothing pushed. Dhruv decides when, after he knows the data size. |
| 2019 May/June | Missing (the 2019-may-june folder held Oct/Nov copies). Dhruv will get it: REMIND HIM when batch M3 starts. |

## 2. Physics stays safe (shared pipeline, not a copy)
Why shared: most of the code (cutting, mark-scheme parsing, our table layout, checks, review page) is the same
work, and a fix found for maths can later help physics. A copy would mean two pipelines to keep right.
How physics is protected:
1. Everything that differs per subject is in `pipeline/subjects.py` (names, paper types, MCQ papers, cover
   totals). Maths-only code is gated: `if not subjects.is_physics(syl)` or `subjects.subject(syl)['maths_text']`.
2. The golden set (`tests/golden/`, 26 physics papers from 2004 to 2026, every era) must show **0 changed cuts**
   before any push (`golden.py check`). After a pipeline change also: `git status` shows nothing changed under
   `bank/cambridge-igcse/0625-physics` or `store/cambridge-igcse/0625-physics`.
3. A maths fix that would ALSO improve physics is NOT applied to physics now. Write it in docs/PHYSICS_LATER.md
   (what, which papers, why). Later a separate physics pass applies them with its own review round.
4. Selectors: `2021-MJ/41` = physics; maths always with the syllabus: `0607/2021-MJ/41`, `0607/2021-MJ` (session),
   ids `0607_2021MJ_41`. Session tools (ms_align, ms_sweep, year_audit, audit) take `SYL=0607` in the environment.

## 3. What we have (checked 2026-11-12)
- 946 PDFs, 2014 to 2026: May/June (MJ) and Oct/Nov (ON) every year, Feb/March (FM) from 2021. Papers 1-6 with
  3 variants (FM: variant 2 only, 6 papers). Examiner reports (er) too. 2019-MJ missing (see 1).
- Paper types (from the cover; `subjects.maths_paper_type`): before 2025 `core_short_answer` (1), `extended_short_answer`
  (2), `core_long_answer` (3), `extended_long_answer` (4), `core_investigation` (5), `extended_investigation_modelling` (6);
  from 2025 `*_non_calculator` (1,2), `*_calculator` (3,4), `extended_investigation_modelling` (6). No multiple choice.
- First test run (7 papers: 2014 MJ 11/41/51, 2019 ON 41, 2025 MJ 21/41/61): the physics pipeline already cuts them,
  marks = cover total on 6 of 7, mark scheme linked on 252 of 263 marked parts. Problems found (pilot work):
  1. Page 2 is a formula list: it is not a question (coverage error on every paper). -> keep it once per paper
     as `paper.formula_list` (exact SVG + LaTeX), not inside Q1.
  2. 2014 paper 5 (investigation): no [n] marks printed per part; total only in the mark scheme. -> marks from the MS.
  3. Mark schemes from about 2018 have 4 columns: Question | Answer | Marks | Partial Marks (method marks like
     'M1 for 8 x 17.5 / 100'); 2014 has an older layout. Our table needs a 4th
     column or the partial marks as notes under the answer (decide in the pilot with Dhruv: side-by-side picture).
  4. Maths in the text layer: fractions are stacked lines with a bar, powers are small raised text, roots are a
     glyph plus a bar, column vectors and big brackets are pieces (private-use glyphs ...), MathType fonts
     (MMGreek, EuclidMathTwo, 'AllAndNone' in 2025). -> LaTeX builder (section 6).
  5. Some text checks report 67-96% of printed words (q15 2025 MJ 21): maths symbols not read as words.
  6. A small header line on page 3 outside every piece (coverage) - check what it is.
  7. 2025 papers: dotted answer lines + text in the margin (same family as physics 2025: rules exist).

## 4. Pilot M0 (one chat): 4 sessions, one from each layout family
| Session | Why |
| --- | --- |
| 2014-MJ | oldest layout ('Answer(a)' style, old MS) |
| 2019-ON | 2018-2024 layout, old syllabus |
| 2021-FM | March series (variant 2 only, 6 papers) |
| 2025-MJ | 2025 syllabus (non-calculator / calculator papers, new MS) |
A pilot = a first small batch that meets every kind of paper before the big batches. It costs more per paper
(new rules are written here: formula page, 4-column MS, LaTeX), so the 3-year batches after it are mostly
routine. Pilot output: all its papers approved, MATHS rules written into MS_TABLE_RULES.md / ERROR_PATTERNS.md,
the LaTeX builder working with a check, measured times -> decide if 3 years per chat is right (Dhruv decides).

## 5. Batches after the pilot (each one new chat)
| Batch | Sessions (pilot sessions not repeated) | Papers (about) |
| --- | --- | --- |
| M1 | 2024-FM 2024-MJ 2024-ON 2025-FM 2025-ON 2026-FM 2026-MJ | 100 |
| M2 | 2021-MJ 2021-ON 2022-FM 2022-MJ 2022-ON 2023-FM 2023-MJ 2023-ON | 115 |
| M3 | 2018-MJ 2018-ON 2019-MJ (**remind Dhruv: he must upload it**) 2020-MJ 2020-ON | 85 |
| M4 | 2014-ON 2015-MJ 2015-ON 2016-MJ 2016-ON 2017-MJ 2017-ON | 115 |
Order: newest first (closest to the pilot's 2025 rules), oldest last. If the pilot shows a chat cannot hold a
batch, split it (e.g. M2a/M2b) and tell Dhruv.

## 6. Maths text as LaTeX (KaTeX on the site)
- Where: the editable content of each part (`content[]` in store JSON): a text run becomes
  `{"type": "math", "tex": "\\frac{3}{4}x^{2}"}` inline, or a display block for equations on their own line.
  The exact SVG (print) is unchanged. A part with a graph/diagram keeps it as a figure (picture/vector).
- How: from the PDF text layer (positions, sizes, fonts): stacked lines over a bar -> `\frac{}{}`; smaller raised
  text -> `^{}`, lowered -> `_{}`; radical glyph + bar -> `\sqrt{}`; big bracket pieces -> `\begin{pmatrix}`;
  symbol fonts mapped to LaTeX (`\times`, `\div`, `\leqslant`, `\pi`, `\theta`, vectors `\overrightarrow{AB}`).
  One module (e.g. `pipeline/maths_tex.py`), gated to `maths_text` subjects.
- Check (automatic, every paper): render our KaTeX in Chromium next to the PDF crop and compare (like
  `store.py verify`); a part whose maths does not match is flagged and falls back to a picture of that line.
- Mark schemes: the same for answers ('x = \frac{5}{2}', 'k = 3, n = -2').

## 7. Tracking (pipeline/batch_log.py -> review/cycle/<batch>.json -> docs/BATCH_LOG.md)
Record while working (commands in PLAYBOOK step 0/11): phase start/end for build, claude1, claude2, review (Dhruv,
not counted), fix; GitHub run ids (their minutes come from the API); counts (papers, questions, flags, round
items, wrong items); every error: pattern number, new or repeat, what, fix; tokens at the end of the chat
(the explain-usage skill if it is available; otherwise "n/a"). After the batch: `batch_log.py report`.
Per-batch analysis (in CONVERSATION_LOG entry + BATCH_LOG): what took longest, which errors repeated and why the
doc/check did not stop them, what to change before the next batch.

## 8. Rebuild rules (what to rebuild after which change)
| You changed | Rebuild | Then |
| --- | --- | --- |
| cutting: extract.py, clean.py, layout.py, coverage rules | `run.py` for the affected papers (cuts + MS link + store) | checks.py, golden check, dupes |
| mark-scheme reading: ms.py | `run.py` for the affected papers | ms_align list, golden check |
| table layout: ms_layout.py, ms_map.json, store_text.py, maths_tex.py | `store.py build <ids>` only | `store.py dupes <syl/session>`, golden check |
| checks.py / review page / docs | nothing | re-run checks only |
| a figure crop rule | `run.py` for the affected papers | fig_grid.py on the flagged crops, compare with the page |
Always: rebuild ONCE per pass (collect fixes first), JOBS=4 for many papers, JOBS=1 when you must be sure every
paper changed. After a pipeline change: golden.py check (0 changed cuts) and physics untouched in `git status`.

## 9. Saving tokens (quality first)
GitHub builds (free); one rebuild per pass; look at small crops and grids, not whole pages; `ms_align.py dump`
text instead of pictures; one new chat per batch; read only START_HERE + the files it names; short messages.
