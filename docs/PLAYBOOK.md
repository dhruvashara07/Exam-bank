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
