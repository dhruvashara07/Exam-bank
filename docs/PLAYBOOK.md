# Playbook: how one batch is done (any subject; maths 0607 now)
Read docs/START_HERE.md first. Plan and batches: docs/MATHS_PLAN.md. Rules for mark schemes: MS_TABLE_RULES.md.
Mistakes not to repeat: ERROR_PATTERNS.md. Decisions: CONVERSATION_LOG.md. Physics 0625 is frozen.
Selectors: physics `2021-MJ/41`; maths ALWAYS with the syllabus: `0607/2021-MJ/41`, session `0607/2021-MJ`,
id `0607_2021MJ_41`. Session tools need `SYL=0607` (ms_align, ms_sweep, year_audit, audit).

## 0. Start (Claude)
`git pull --rebase`; `pip install -r requirements.txt` if a module is missing;
`python3 pipeline/batch_log.py start M1 --subject 0607 --sessions 2024-FM 2024-MJ ...` (skip if the record exists:
a batch can continue in a second chat - then keep adding to the same record).
Papers of a session: `python3 pipeline/session_papers.py 0607/2024-MJ`. Fetch the PDFs:
`python3 pipeline/raw_store.py fetch $(python3 pipeline/session_papers.py 0607/2024-MJ)`.

## 1. Build on GitHub (free; Claude only starts and waits)
`batch_log.py phase M1 build start`
`gh api -X POST repos/dhruvashara07/Exam-bank/actions/workflows/bank.yml/dispatches -f ref=main -f 'inputs[sessions]=0607/2024-FM 0607/2024-MJ ...'`
Wait: `gh api "repos/dhruvashara07/Exam-bank/actions/runs?per_page=3" -q '.workflow_runs[]|[.id,.status,.conclusion]|@tsv'`
(GraphQL `gh run ...` does not work here; use `gh api`). Then `git pull --rebase`;
`batch_log.py gh M1 <run id>`; `batch_log.py phase M1 build end`.
If the Action fails or for a few papers: build locally `JOBS=4 python3 pipeline/run.py 0607/2024-MJ/41 ...`.

## 2. Claude pass 1: check everything, fix the pipeline
`batch_log.py phase M1 claude1 start`
1. `python3 pipeline/checks.py <selectors>` -> 0 blocking. Every paper: marks found = total.
2. Every flag yourself: look at the page and our piece (small crops, `pipeline/fig_grid.py` for figure crops: ALWAYS
   compare with the page, ERROR_PATTERNS 56).
3. Mark-scheme sweep: `SYL=0607 python3 pipeline/ms_sweep.py <sessions>` (no TOTAL, no bracketed totals, no codes in
   Answer, no side notes in Answer).
4. Maths text (pilot builds this): LaTeX check report - every flagged part looked at.
5. Every problem is a PATTERN: fix the code (gated to maths when physics must not change), or ms_map.json for rows.
   Record it: `batch_log.py error M1 --pattern <n> --kind new|repeat --what "..." --fix "..."`, and write the pattern
   into ERROR_PATTERNS.md (and a rule into MS_TABLE_RULES.md if it is about layout) NOW, not at the end.
6. Collect the fixes, then rebuild ONCE following the rebuild table (MATHS_PLAN.md 8).
7. Golden: `python3 pipeline/golden.py check` = 0 changed cuts (fetch the golden PDFs first if missing:
   `raw_store.py fetch` with the ids in tests/golden/). `git status`: nothing under 0625-physics.
`batch_log.py phase M1 claude1 end`; push (`pipeline/push.sh`).

## 3. Claude pass 2: re-check, rows by meaning, prepare the round
`batch_log.py phase M1 claude2 start`
1. checks.py again (0 blocking); everything changed by pass 1 looked at again (small grids).
2. Rows by meaning (MS_TABLE_RULES 17): `SYL=0607 python3 pipeline/ms_align.py list <sessions>` must be empty;
   for each listed question `ms_align.py dump <qid>` (text, cheap), decide each MS line's part, write the map in
   pipeline/ms_map.json, rebuild those papers, list again. `ms_align.py verify` must print 0. When a line cannot be
   given ONE part without guessing keep Cambridge's group (MS_TABLE_RULES 20).
3. Look at our tables as a student: `pipeline/ms_grid.py` (order, no part twice, splits, gaps, marks, fonts).
4. Review round: `python3 pipeline/review_round.py new <n> <ids> --sample 1 --max 90 --title ... --intro ...`
   (flagged items + a few random ones per paper type; aim: short); page folder `out/review/page/`
   (`review_page.py add <n> <title>`); publish with publish_files to the review page (slug
   b3c8a710-c92b-4a33-95b2-f7eba1bc0031, mode replace). Same link every time:
   https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e
5. `batch_log.py count M1 papers=.. questions=.. flags=.. round_items=..`; `phase M1 claude2 end`;
   `phase M1 review start`; push; tell Dhruv (2 lines + the link).

## 4. Dhruv's round
He answers on the page (collection `feedback_r<n>`, read with db_list). When he says done:
`batch_log.py phase M1 review end`.

## 5. Fix, build, approve
`batch_log.py phase M1 fix start`
1. Every "wrong" item: find the pattern, ERROR_PATTERNS / MS_TABLE_RULES, fix the pipeline, look for the same
   pattern in the whole batch (and earlier maths batches: re-show those in the next round if they change).
   `batch_log.py error ... --by dhruv`.
2. Rebuild once; checks; ms_align list empty + verify 0; golden 0 changed cuts.
3. `python3 pipeline/review_round.py close <n> <answers.json>`.
4. `python3 pipeline/approve.py <ids> --note "..."` (`approve.py --pending` must not list approved papers).
5. `batch_log.py count M1 wrong_items=..`; `phase M1 fix end`; tokens (explain-usage skill if available):
   `batch_log.py tokens M1 <n>`; `batch_log.py report`.
6. Docs (START_HERE section 4) and `pipeline/push.sh "..."`.

## Batches
See docs/MATHS_PLAN.md section 5. Physics batches are all done (history in PROGRESS.md and CONVERSATION_LOG.md).
