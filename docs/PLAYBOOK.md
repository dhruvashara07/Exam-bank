# Playbook: how one batch is done (any subject; chemistry 0620 now - docs/CHEM_PLAN.md)
Chemistry: selectors `0620/2024-MJ/41`, ids `0620_2024MJ_41`; `SYL=0620` for ms_rebuild / ms_align / ms_sweep; reasons.py takes
the syllabus from the batch record (`batch_log.py start C0 --subject 0620`). Chemistry runs the PHYSICS path (subjects.is_chem gates only).
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

## 1a. THE FLOW SINCE M2 (Dhruv 2026-11-17 'git, you, git, then you and review round'; MATHS_PLAN 11)
One file holds every reason: review/claude/<batch>_reasons.json (pipeline/reasons.py; statuses open / fixed / passed /
ask; pass 2 adds verified / not fixed). Its fingerprints (<batch>_fp.json) make pass 2 a diff.
1. GitHub pass 1: dispatch bank.yml with `inputs[sessions]=0607/<ses> ...` AND `inputs[reasons]=pass1 <batch> <ses ...>
   --skip-checks` (checks.py already ran per session; verify, maths_check, ms_sweep, ms_align, MS picture/table cells
   are collected). Then `git pull`; `reasons.py status <batch>`; `reasons.py classes <batch>`.
   FIRST: `ms_mode` must be 0 and the Action log must have no 'No module named' (pattern 209).
2. Claude resolves EVERY reason, class by class (never item by item): `reasons.py classes` -> for each class look at a
   few members side by side (`reasons.py sheets <batch> --check C --qid ...`, zoom with ms_compare --zoom), then
   `reasons.py set <batch> --check C [--match R] --status fixed --pattern N --note ...` (pipeline fixed, gated to
   maths, ERROR_PATTERNS now) or `--status passed --note "<why it matches the print>"` or `--status ask` (a real decision:
   Dhruv). Fixes are tried on their targets (`ms_rebuild.py <qid>`), blast radius measured before wide changes.
   `reasons.py status`: open = 0. Golden 0 + nothing under 0625-physics; push.
   (M3) `reasons.py set` changes EVERY matching reason whatever its status: run the broad 'passed' sets FIRST, the
   specific fixed / known sets after. Blast before the push: a figure-rule change (extract.diagrams, store.fit_crop) ->
   `pipeline/fig_blast.py` old worktree vs new on all 0607 figures (every BIG change looked at on the page); an ms.py
   change -> old vs new `ms.structured_rows_table` on every 0607 MS (labels + segments). Approved papers a fix corrects
   are rebuilt in pass 2 too (their sessions in `inputs[sessions]`), re-shown in the round and re-approved.
3. GitHub pass 2: dispatch the same sessions with `inputs[reasons]=pass2 <batch> --skip-checks`: rebuild + diff
   -> review/claude/<batch>_pass2.md: NOT FIXED, NEW reasons and COLLATERAL changed questions.
4. Claude looks ONLY at that list (sheets for those qids), sets each to fixed / passed / ask (a third GitHub run only if
   a fix was needed; same diff).
5. Review round (notes in PLAIN WORDS for Dhruv - what changed, what to look at; never pattern numbers): `reasons.py round <batch> --calibrate 5` prints the ids + --recheck string: every 'ask', anything still
   open, 5 calibration items (passed by me: does Dhruv agree?). Then review_round.py new / review_page.py add as in 3.
   Measure: wrong items per round (target <= 2). A wrong calibration item = my pass rule was wrong: fix the class.

## 1b. Why this order (history; the steps are now ONE Claude round, section 2) (Dhruv, round 27, 2026-11-13: 23 of 40 wrong, most of them simple)
Dhruv's round is for judgement, never for finding simple errors. Before a round EVERY question and EVERY mark-scheme
table of the batch is checked by Claude: first by automatic checks that compare our output with the PDF, then by eye on
full contact sheets (ours next to the original), not on a sample. Round 27 failed because pass 2 looked at ~15 tables
and no check compared our mark-scheme rows or question rebuilds with the paper. The exact steps (2a-2f, 3a-3e) below are
the minimum; record each in the batch log.

## 2. Claude's ONE check round (Dhruv, round 29: one round, rules + checkboxes, side by side only when in doubt)
`batch_log.py phase M1 claude start`
1. RULES on every paper - one command writes the checklist (review/claude/<batch>_check.md) with a box per rule and
   the doubtful questions: `python3 pipeline/claude_check.py M1 <paper ids>`. Before it:
   - `python3 pipeline/checks.py <selectors>` -> 0 blocking; every paper: marks found = total.
   - `SYL=0607 python3 pipeline/ms_sweep.py <sessions>` (no TOTAL / bracketed totals / codes / side notes in Answer).
   - Rows by meaning: `SYL=0607 python3 pipeline/ms_align.py list <sessions>` empty (MS_TABLE_RULES 17, 20).
   - `python3 pipeline/store.py verify <ids>` (question pieces redrawn vs the page).
   claude_check runs maths_check (content: ms_words, ms_overflow, ms_overlap, ms_font, fig_overlap, not_to_scale;
   appearance: ms_stretch, ms_edge, ms_piccut, q_font, fig_cut, fig_text) on all papers.
2. DOUBTFUL = every question with a hit, every mark-scheme cell drawn as a picture or table block, + 8 random.
   claude_check draws the side-by-side sheets for exactly these: out/claude_check/<batch>/ms_<n>.png (our mark scheme |
   printed rows) and fig_<n>.png (each diagram crop drawn on its printed page). READ EVERY SHEET line by line: same
   words, same line breaks (or a re-flowed sentence), marks beside their line, nothing touching a rule, pictures whole,
   no stray line, no question line / number / table inside a diagram crop, tables as lines + text.
   In doubt about a detail (thin rules, shading, faint grids) zoom: `python3 pipeline/ms_compare.py --zoom /tmp/z <qid>`
   (one question at 2x, ours | printed) and crop the part. Look for: lines missing in one row only, grids/curves
   faded, a heading drawn twice, labels moved out of a table, an axis missing, an empty fallback layout.
3. Tick each box. A doubtful item that matches the print is PASSED with its reason written in the checklist (Dhruv:
   'pass it, log the reason'). Anything else is a PATTERN: fix the code (gated to maths), `batch_log.py error`,
   ERROR_PATTERNS / MS_TABLE_RULES now; then search ALL papers for the same class (a repeat = the fix was too narrow).
4. Collect fixes, rebuild once (MATHS_PLAN.md 8), run claude_check again: the new sheets only for what changed.
   Budget (START_HERE 2c): triage everything first, try each fix on its targets (`ms_rebuild.py <qid>`), at most 3
   full-batch runs per round, read results as diffs; tick the batch log at every step.
   BEFORE every rebuild ask: is it needed? Mark-scheme layout only (ms_maths) -> `pipeline/ms_rebuild.py <sessions> [--write]` (minutes), never run.py;
   extract/store/ms.py -> run.py only for the papers the class touches; full run.py only when a shared step changed.
   After each fix LOOK at the cells it touches in ALL papers (a fix for one cell broke fractions elsewhere twice in round 30).
5. LaTeX (maths_tex): check ok or picture; stacked maths (fractions, brackets, tables) read against the page - KaTeX and
   the character check test form, not meaning (pattern 89).
6. Golden: `python3 pipeline/golden.py check` = 0 changed cuts; `git status`: nothing under 0625-physics. Push.
7. Only when every box is ticked: the review round (step 3 below). `batch_log.py phase M1 claude end`.
Loops: if one class needs a third rebuild, stop and write down what is not understood (ERROR_PATTERNS 'open') rather
than burning rebuilds; long runs go in the background with timeouts high enough to finish (60 papers ~ 35 min).

## 3. The review round
1. `python3 pipeline/review_round.py new <n> <ids> --sample 1 --max 40 --recheck "<wrong items>" --title ... --intro ...`
   then `python3 pipeline/review_page.py add <n> "<title>"`; publish out/review/page to the SAME review page
   (list_files first, publish_files replace). Images: question and stored figures at 192 dpi (same scale).
2. `batch_log.py count M1 papers=.. questions=.. flags=.. round_items=..`; tell Dhruv in 2 lines.

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

- Local `store.build` is NOT identical to the Action (font family 'symbol' vs 'serif' in MS text, 2026-11-17): question-side
  fixes are rebuilt by the Action only; `ms_rebuild.py` (MS layout only) matches the Action and may be written locally.
- (M2, pattern 209/211) The local / Action difference had two causes: fontTools missing on GitHub (now in requirements) and
  missing PDFs locally (ms_rebuild now refuses to run without them). With both, local = Action.
- Local `ms_rebuild.py --write` is safe only for papers where its no-write listing shows just the intended changes
  (2019 ON differed in heading font family, 2026-11-17). Restore with `git checkout -- store bank`, never `-- review`.
