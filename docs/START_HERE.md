# Start here (every new chat, every session)

You are continuing Dhruv's exam question bank (repo dhruvashara07/Exam-bank, working copy
/home/claude/exam-bank). Physics 0625 is DONE and frozen. Now: Maths 0607, batch by batch.

## 1. First 5 minutes (in this order, nothing else)
1. `cd /home/claude/exam-bank && git pull --rebase` (clone it first if missing: `gh repo clone dhruvashara07/Exam-bank`).
2. Read `CLAUDE.md` (hard rules), then `PROGRESS.md` top section: the line **NEXT:** says which batch is yours.
3. Read `docs/MATHS_PLAN.md` (the plan, decisions, batches, rebuild rules) and `docs/PLAYBOOK.md` (the steps).
4. Read `docs/ERROR_PATTERNS.md` and `docs/MS_TABLE_RULES.md` (mistakes never to repeat, table rules).
5. Read the last 2 entries of `docs/CONVERSATION_LOG.md` (what Dhruv decided lately) and `docs/BATCH_LOG.md`
   (times and repeat errors of earlier batches: avoid them).
Only then start. Skip the other docs unless a step points to them.

## 2. The cycle of one batch (details: docs/PLAYBOOK.md)
| # | Phase | Who | Record (`pipeline/batch_log.py`) |
| --- | --- | --- | --- |
| 0 | start record, fetch PDFs | Claude | `start <batch>` |
| 1 | build on GitHub (bank.yml, sessions input) | GitHub | `phase <b> build start/end`, `gh <b> <run ids>` |
| 2 | pass 1: checks, every flag, pictures, fix the pipeline, rebuild once | Claude | `phase <b> claude1 ...`, `error ...` |
| 3 | pass 2: re-check after the rebuild, rows by meaning, grids, logic check (does each answer fit its question; solve it when in doubt), build the review round | Claude | `phase <b> claude2 ...` |
| 4 | review round on the same review page; tell Dhruv | Dhruv | `phase <b> review ...` (not counted) |
| 5 | fix what he marked wrong, rebuild, approve, docs, push | Claude | `phase <b> fix ...`, `tokens`, `report` |

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
https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e
