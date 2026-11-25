# Start here (every new chat, every session)

You are continuing Dhruv's exam question bank (repo dhruvashara07/Exam-bank, working copy
/home/claude/exam-bank). Physics 0625 and Maths 0607 are DONE and frozen. Now: Chemistry 0620 (plan: docs/CHEM_PLAN.md;
for chemistry read it instead of MATHS_PLAN in step 3; tools take SYL=0620, reasons.py reads the batch's subject).

## 1. First 5 minutes (in this order, nothing else)
1. `cd /home/claude/exam-bank && git pull --rebase` (clone it first if missing: `gh repo clone dhruvashara07/Exam-bank`).
2. `python3 pipeline/batch_log.py now`: the time now and the last task recorded (resume exactly there; a gap > 45
   min is a pause and is not counted). Then `CLAUDE.md` (hard rules), `PROGRESS.md` top: **NEXT:** says your task.
3. Read `docs/MATHS_PLAN.md` (the plan, decisions, batches, rebuild rules) and `docs/PLAYBOOK.md` (the steps).
4. Read `docs/ERROR_PATTERNS.md` and `docs/MS_TABLE_RULES.md` (mistakes never to repeat, table rules).
5. Read the last 2 entries of `docs/CONVERSATION_LOG.md` (what Dhruv decided lately) and `docs/BATCH_LOG.md`
   (times and repeat errors of earlier batches: avoid them).
Only then start. Skip the other docs unless a step points to them.

## 2. The cycle of one batch (details: docs/PLAYBOOK.md)
| # | Phase | Who | Record (`pipeline/batch_log.py`) |
| --- | --- | --- | --- |
| 0 | start record, fetch PDFs | Claude | `start <batch>` |
| 1 | GitHub pass 1: bank.yml sessions + `reasons=pass1 <b> ...` (PLAYBOOK 1a) | GitHub | `phase <b> build start/end`, `gh <b> <run ids>` |
| 1b | resolve EVERY reason (`reasons.py classes / sheets / set`), GitHub pass 2 (`reasons=pass2 <b>`), look only at its diff | Claude + GitHub | `phase <b> claude ...` |
| 2-3 | (details of the look) ONE Claude check round (PLAYBOOK 2): rules on every paper via `claude_check.py` checklist, side by side (`out/claude_check/`) only for doubtful items - pass with a reason or fix the class; rebuild once; golden; build the review round | Claude | `phase <b> claude ...`, `error ...` |
| 4 | review round on the same review page; tell Dhruv | Dhruv | `phase <b> review ...` (not counted) |
| 5 | fix what he marked wrong, rebuild, approve, docs, push | Claude | `phase <b> fix ...`, `tokens`, `report` |

## 2b. Standing rules (Dhruv 2026-11-13)
- Every new error pattern or rule: update the respective doc (ERROR_PATTERNS / MS_TABLE_RULES / MATHS_PLAN / PLAYBOOK)
  AND the batch-cycle skill at once, without being asked (propose the skill change with the skill tool).
- Loops cost tokens: a check or fix that does not converge after 3 attempts on the same pattern is written down as
  a known open item (PROGRESS + ERROR_PATTERNS) and the work moves on. Long jobs run in the background with generous
  time limits (run.py ~10 min for 60 papers) and are polled with sleeps, never restarted while still running.

## 2c. Work like it costs money (Dhruv, M1 2026-11-17: 'tokens and time are currency')
- `batch_log.py tick <b> "<task>"` at every step (start and end of every long run too): the record knows the task in
  hand and the active time; a usage-limit pause is not work.
- Understand ALL items first (every flag, every wrong item), group them into classes, write ALL the fixes, THEN verify
  once. Never 'fix one -> full rebuild -> look -> fix the next' (M1: 11 sessions re-checked ~20 times).
- Try a fix on its target questions only (`ms_rebuild.py <qid> ...`, seconds). Full-batch runs at most 3 per round:
  one after the fixes, one after the corrections they need, one final. Each full run's result is read as a diff
  (what changed), not re-read from the start.
- Nothing I have found goes to Dhruv as 'OPEN': each item is fixed, proven to match the print (reason written), or
  turned into a question with options. His round is for decisions and what vision could not settle.
- Check the QUESTION side too (stray notices 'Question 11 is on the next page', part labels, bold letters, shading),
  not only mark schemes: M1 round 32 had 4 question-side misses.

## 3. Never
- push with `git push` (use `pipeline/push.sh "msg"`; only `pipeline/store_pdfs.sh` pushes its own store-* branch);
- change physics (golden check 0 changed cuts; nothing under `0625-physics` in `git status`);
- write to MongoDB or Cloudinary; put keys anywhere; delete original PDFs;
- fix one JSON by hand (fix the pipeline or ms_map.json);
- approve without looking (approve.py only after the full visual check).

## 4. Before the chat ends (always, even if the batch is not finished)
1. `batch_log.py report` (docs/BATCH_LOG.md), PROGRESS.md (state + **NEXT:** line), CONVERSATION_LOG.md entry
   (what Dhruv said, decisions, analysis: slow phases, repeat errors and why), ERROR_PATTERNS / MS_TABLE_RULES
   for every new pattern, MATHS_PLAN.md if the plan changed, docs/NEXT_CHAT.md (prompt for the next chat).
2. `pipeline/push.sh "message"`.
3. Tell Dhruv in 3-5 short lines: done, what he must do (if anything), the prompt for the next chat is in NEXT_CHAT.md.

## 5. Talking with Dhruv
Physics teacher in India (IST), reads on his phone. Short plain messages. Ask only when you need his input
(use the question tool with options). Be honest about what is not fixed. Review page (same link every round):
https://claude.ai/artifact/8YDJDKJCXfURh5QFLnpTw8 (shared account, from round 35; rounds 1-34 were on PCdP6oibAkjQvGz8mKm73e in Dhruv's own account)

## 5. Usage budget (Dhruv 2026-11-23: the work moves to a SHARED Claude subscription - use it sparingly)
- Per batch: at most 2 GitHub passes + 1 review round. Wait for GitHub with ONE long poll, never many short ones.
- A defect class touching fewer than 5 questions with no wrong text / marks / figure data: write it in ERROR_PATTERNS as
  'known' and move on - do not fix it inside the batch. Max ~30 min per class.
- Pass-2 collateral that is only added bracket glyphs: pass without looking. Read comparison sheets in bulk, zoom only doubts.
- Run `batch_log.py phase <batch> claude|fix start/end` (M2's log shows 0.0 because it was never run).
- No Fable model. No scheduled tasks unless Dhruv asks. Never use Claude API tokens in any workflow.
- The skill text for a new account is docs/SKILL_exam-batch-cycle.md.
