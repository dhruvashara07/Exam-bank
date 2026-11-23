# Copy of the exam-batch-cycle skill (2026-11-23). A new Claude account has no skills: follow this file the way the skill is followed.


# Exam-bank batch cycle

Use when Dhruv asks to do, continue or record a batch of papers in the Exam-bank repo (dhruvashara07/Exam-bank).
The repo's own docs are the source of truth; this skill is the checklist that keeps every chat the same.

## Before anything
1. `cd /home/claude/exam-bank && git pull --rebase` (clone with `gh repo clone dhruvashara07/Exam-bank` if missing).
2. Follow `docs/START_HERE.md` section 1 exactly (CLAUDE.md, PROGRESS.md NEXT line, MATHS_PLAN.md, PLAYBOOK.md,
   ERROR_PATTERNS.md, MS_TABLE_RULES.md, last 2 CONVERSATION_LOG entries, BATCH_LOG.md).
3. If the batch is M3: remind Dhruv to upload 2019 May/June before building.

## Record every phase (pipeline/batch_log.py)
- `start <batch> --subject 0607 --sessions ...` once (a continued batch keeps its record).
- `phase <batch> build|claude|review|fix start` / `end --note ...` at each boundary (claude = the ONE check round).
- `gh <batch> <run ids>` for every GitHub Action run used.
- `error <batch> --pattern N --kind new|repeat --what ... --fix ... [--by dhruv]` the moment a problem is understood;
  write the pattern into docs/ERROR_PATTERNS.md (and MS_TABLE_RULES.md for layout) at the same time.
- `count <batch> papers=.. questions=.. flags=.. round_items=.. wrong_items=..`.
- At the end: `tokens <batch> <n>` (use the explain-usage skill if available, otherwise skip) and `report`.

## Cycle since M2: the TWO-PASS FLOW (PLAYBOOK 1a, MATHS_PLAN 11; Dhruv: 'git, you, git, then you and review round')
One reasons file per batch: review/claude/<batch>_reasons.json (pipeline/reasons.py). Statuses: open, fixed (pattern N),
passed (reason written), ask (Dhruv decides), known (my own unfixed fault: PROGRESS + ERROR_PATTERNS, never in his round).
A. GitHub pass 1: dispatch bank.yml with `inputs[sessions]=0607/<ses> ...` AND `inputs[reasons]=pass1 <batch> <ses ...>
   --skip-checks`. First: Action log has no 'No module named' (pattern 209) and `reasons.py classes` shows ms_mode 0.
B. Resolve EVERY reason as a CLASS: `reasons.py classes <b>` -> `reasons.py sheets <b> --check C --tag t` (MS ours|printed
   + figure crop on its page + STORED figure sheets) -> fix (try on targets with ms_rebuild <qid> / run.py <paper>) ->
   `reasons.py set <b> --check C [--match R] [--qid Q] --status fixed|passed|ask|known --note ... [--pattern N]`.
   Measure the blast radius of every MS fix over ALL maths sessions with the PDFs fetched (ms_rebuild refuses without:
   pattern 211), attribute changes fix by fix (toggle script), narrow wide fixes before pushing. Golden 0; push.
C. GitHub pass 2: same sessions, `inputs[reasons]=pass2 <batch> --skip-checks` -> <batch>_pass2.md: NOT FIXED, NEW and
   COLLATERAL changed questions (approved sessions too). Look ONLY at those; set each.
D. Review round: `reasons.py round <b> --calibrate 5` (ask + still open + 5 passed items as calibration) ->
   review_round.py new ... --recheck. Target <= 2 wrong items. A wrong calibration item = a wrong pass rule: fix the class.

## Cycle details (still valid inside B; details in docs/PLAYBOOK.md)
1. Build on GitHub: dispatch bank.yml with `inputs[sessions]=0607/<ses> ...`; poll with `gh api` (GraphQL is blocked).
2. ONE Claude check round (PLAYBOOK 2; Dhruv 2026-11-16: one round, rules + checkboxes, side by side only in doubt):
   checks.py 0 blocking (marks = total), ms_sweep, ms_align list empty, `store.py verify`, LaTeX read for stacked
   maths, then `python3 pipeline/claude_check.py <batch> <paper ids>` -> checklist review/claude/<batch>_check.md and
   side-by-side sheets out/claude_check/<batch>/ for every doubtful item (every maths_check hit incl. ms_mode and
   q_rule, every MS picture/table cell, + 8 random). READ every sheet; zoom doubtful details with
   `ms_compare.py --zoom /tmp/z <qid>` (lines missing in one row, faded grids, heading twice, labels out of a table,
   lost axis, fallback layout). Tick each box: matches print = pass + reason written; else fix the CLASS (maths-only
   code gated; never one JSON), search all papers for it, ERROR_PATTERNS now. Rebuild once; golden.py = 0 changed
   cuts, nothing under 0625-physics; push.
   Layout-only fixes (ms_maths / ms_layout): `python3 pipeline/ms_rebuild.py <ALL maths sessions>` first WITHOUT --write
   to see every question the fix moves (approved batches too), zoom a few, then --write. A changed approved question
   is re-shown in the next round (--recheck). New session fonts: crop each unknown glyph code into a sheet and map it
   (store_text MATHS_GLYPHS, maths_tex SYM) before the check round. Picture cells: a text line goes WHOLE to our
   text or WHOLE into the picture, never half (patterns 169-180).
   review_page.py add on a fresh clone writes rounds.json with only the new round: merge the older rounds back
   (read the live rounds.json) before publishing.
3. Review round: `review_round.py new <n> <ids> --sample 0 --max 40 --recheck "qid=why;..."`, then
   `review_page.py add <n> "<title>"`; list_files, then publish_files (patch: keeps older rounds) to the same review
   page (slug b3c8a710-c92b-4a33-95b2-f7eba1bc0031, link https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e).
   Stored figures under the question are at the question's scale. Tell Dhruv in 2 lines.
4. Dhruv's round: read feedback_r<n>; his time is recorded as review but not counted.
5. Fix: every wrong item -> pattern -> pipeline fix -> search the whole batch; rebuild once; checks; golden;
   review_round close; approve.py; docs; push.

## Rules from Dhruv (maths)
- MS: Q | Answer | Marks | Partial Marks, Answer : Partial Marks = 60 : 40 of the free width (round 29), rows grow
  for fractions/pictures. Tables in cells are lines + shading + text as one rigid block, never a picture.
- A doubtful item that matches the print is passed, with the reason logged in the checklist.
- One font for question and MS (the paper's family, 11 pt), bold/italic only where printed.
- 'NOT TO SCALE' always inside the diagram picture. Diagram labels inside the picture.
- Upgrade the docs, this skill and the pipeline as maths rules change - every new pattern, error or upgrade, at once,
  without being asked.
- Long answers printed over several lines are re-flowed in our column (MS_TABLE_RULES 26).
- 2026 MJ+ Guidance column: 5 columns, Answer : Partial : Guidance = 40 : 30 : 30 (MS_TABLE_RULES 31).
- A section-wide note ('Throughout the modelling ...') goes on top of every later question of that section.
- Notes printed across the table (merged row / band inside a row) are one full-width cell.
- Simple errors are found by my own ONE check round, never left for Dhruv's round.
- Rebuild only the papers a fix touches when possible; long runs get timeouts high enough to finish; a check that
  loops is stopped and changed early.
- MS-only fixes: `ms_rebuild.py <sessions>` (no write) shows the blast radius first; view the biggest changes, then
  `--write`. Local `store.build` differs from the Action (font family): question-side fixes go through the Action.
- Paper 5/6 tasks are ONE record (pipeline/tasks.py, task_<S>.json, id ..._t<S>); review rounds take task ids.
- MS screenshot graphs with a function in the question: add a line to pipeline/ms_graphs.py SPECS. Blurred raster pictures in the
  MS (calculator graphs, handwriting-style probability trees) are redrawn the same way: a graph spec, or a 'tree' spec (lines + text
  like the question's tree); options 'xlab' (axis letter) and 'xlow' (numbers under the window). Dhruv round 34: only the pictures he
  flags are redrawn; redrawing ALL raster screenshots of a batch is a decision for him (a batch of its own).
- `ms_rebuild.py` WITHOUT --write still rewrites msimg_*.png (byte noise, ~300 files): `git restore` them before every commit.
- A change to question-side crops (store.fit_crop, extract.diagrams): measure it on ALL stored maths figures with a harness that toggles
  the rule (flags store.FIT_SLANT / FIT_HEAD), render old | new for every changed figure and look at each (round 34: 15 of 1580
  changed, one was collateral). Changed questions of APPROVED sessions go to the next round with --recheck.
- Review page holds at most 512 files: before publishing a new round, remove the closed round's files (publish_files
  remove) and keep rounds.json listing only open/older rounds.
- Local = Action only with fonttools installed AND the session PDFs fetched (patterns 209, 211); never trust a local
  rebuild of a session whose PDFs are missing.
- MS layout rules from M2: every maths MS ends with our Total row (5 columns too); one formula wider than its column is
  scaled (>= 60 %), never clipped; a new marking point (B1/M1/FT/If/OR) never joins the line above; text size from the
  paper's normal MS size; tables flush with the cell or with fill-only rows stay tables; never a rule through a word;
  labels inside a drawn frame are never a heading.
- Diagram crops: question text above / below all drawing ink (part line, question number, 'f(x) = ... for', a sentence
  running past the crop) is cut off; strokes on a text line (|..|, roots, bars) are text.
- New equation font: crop each unknown code (q_font hits show them) and map it in store_text MATHS_GLYPHS + maths_tex SYM.

## Never
`git push` (use pipeline/push.sh); change physics; write to MongoDB/Cloudinary; keys in repo or chat; delete
original PDFs; approve without a full look.

## Before the chat ends (always)
batch_log report; PROGRESS.md (state + NEXT line); CONVERSATION_LOG entry with the batch analysis (slowest phase,
repeat errors and why the docs or checks missed them, what to change next); ERROR_PATTERNS / MS_TABLE_RULES;
MATHS_PLAN.md if the plan changed; docs/NEXT_CHAT.md prompt; `pipeline/push.sh`; 3-5 line message to Dhruv.
## Layout-rule look-alike scan and other M2 lessons (2026-11-22)
- Before pushing any ms_layout / ms_maths rule, scan ALL stored rows for its look-alikes (bracket tops with no bottom, rows with
  >= 5 extender glyphs): one 2-minute scan found a regression of my own and 6 older defects (pattern 240).
- `ms_rebuild.py` WITHOUT --write still rewrites msimg_*.png: `git restore` them before every commit.
- Question-side crop changes (store.fit_crop): measure on ALL stored maths figures, render old | new for every changed one.
- Blurry raster MS pictures: ms_graphs.SPECS (graph or 'tree' spec). Dhruv decided 2026-11-22: redraw ALL ~60 of M2 as a batch of its own.
