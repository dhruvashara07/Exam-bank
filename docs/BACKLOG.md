# Backlog run (hourly Claude session) — older years 2014 → 2002

`review/backlog.json` lists the batches in order (one year, or two small years) and the state of each.
A scheduled Claude session runs this file every hour until every batch is `finalised`, then switches
itself off. Dhruv only answers the review rounds (flagged questions + a few spot checks) on the review page.
Read `CLAUDE.md` first: its rules (push.sh, never force-push, never delete originals, fix the pipeline not
single files, golden check) apply here too. Nothing goes to MongoDB or a file host in this phase.

States of a batch: `waiting` → `processing` → `claude_check` → `your_review` → `finalised`; `recheck` (2015-2026)
(or `stuck`: needs Dhruv or a bigger fix; later runs skip it).

## Every run
1. `cd /home/claude && ([ -d exam-bank ] || git clone https://github.com/dhruvashara07/Exam-bank.git exam-bank) && cd exam-bank && git pull --rebase`
   `pip install -r requirements.txt --break-system-packages -q; python3 -m playwright install chromium`
2. Read `review/backlog.json`. If every item is `finalised`: write the last log line, push, switch the
   scheduled task off (update_trigger enabled=false, the id is in the PROGRESS.md log), notify Dhruv
   ("all of 0625 is finalised"), stop.
3. **One run at a time.** If `running_since` is less than 50 minutes ago, stop at once (another run is
   working). Otherwise set `running_since` to now, commit and push it (push.sh) before working.
4. Work for at most ~45 minutes, in this order, one step per batch, then go to 9:
   a. **Answers first** (docs/DAILY_CHECK.md §3): open rounds in `review/rounds/` — read the answers
      (ArtifactData, `feedback_r<n>`), fix the pipeline for every ✗, re-run the affected papers, close
      the round when all are answered (or it is 3 days old).
   b. A batch in `your_review` whose round is closed: approve its papers by the rule in DAILY_CHECK.md §6
      (`python3 pipeline/approve.py <ids> --note ...`). When all its papers are approved: state `finalised`.
   c. A batch in `claude_check`: for every paper `python3 pipeline/overview.py <id>` and LOOK at every
      image (boxes start at labels, nothing outside a box, no page furniture, figures whole, marks match).
      Read `review/checks/<id>.json` and `review/store/<id>.json`. Fix what you can in the pipeline
      (re-run, `golden.py check` = 0 changed cuts); record `claude_check.py ok|needs_fix`. Then, if no round
      is open, `review_round.py new <n> <ids> --sample 1 --max 90` and publish it to the review page
      (DAILY_CHECK.md §5); state `your_review`, `round` = n. If a round is open, leave the batch at
      `claude_check` with note "waiting for the open round".
   d. If no batch is `processing` or `claude_check` and at most one is `your_review`: take the next
      `waiting` batch → `processing`:
      `python3 pipeline/raw_store.py fetch <year...>` (2002-2009 also need `python3 pipeline/old_papers.py`
      once: it only names files, the originals stay), `JOBS=2 python3 pipeline/run.py <papers>`,
      `python3 pipeline/checks.py <papers>`, `python3 pipeline/store.py verify <papers>`,
      `python3 pipeline/batch.py new "Backlog <name>" <papers>` (once; save its id in `batch`).
      Then state `claude_check`. If processing does not finish in this run, leave it at `processing`:
      the next run re-runs only the papers without `review/store/<id>.json`.
   If a year is fast and the run has time left, start the next `waiting` batch too (at most two per run).
   e. `recheck` items (2015-2026, already cut and checked in the old format): Dhruv reviews them again in
      the new stored format. Handle one like `claude_check` without re-processing: look at the overview of
      every paper whose `review/store/<id>.json` lists differing pieces (and fix the store if you can), then
      when no round is open and the batch before it in the list is at `your_review` or later:
      `review_round.py new <n> <ids> --sample 1 --max 90` (flagged store pieces + one spot check per paper),
      publish, state `your_review`. Approve as in b (papers approved earlier keep their approval when the
      round shows no problem in them). Rounds alternate: old year, new-format review, old year, ...
5. **Errors.** Every failed attempt at a step adds 1 to `attempts`. At 2 failed attempts of the same step:
   state `stuck`, write the reason in `note`, notify Dhruv, continue with the next batch. Never loop on it.
   A decision only Dhruv can make (a scanned paper without text, a missing mark scheme, a paper type the
   site does not know): `stuck` with the question in `note`, notify him.
6. Older papers (2002-2009) differ from 2015+: component papers 0625/01-06 without variants (ids
   `0625_2005MJ_03`), Paper 2 = core theory and Paper 3 = extended theory (paper type from the cover),
   different covers and footers. Fix the pipeline so they cut as cleanly as the new ones; 2015-2026 must
   stay unchanged (`golden.py check` = 0 changed cuts).
7. 2002 November mark schemes are scanned pictures (no text): keep the questions, and mark the paper's
   mark scheme rows as pictures if the pipeline cannot read them — ask Dhruv in `note` if unsure.
8. Clear `running_since`, add one line to PROGRESS.md "Daily check log" (what moved, what was fixed),
   push with `pipeline/push.sh`.
9. Notify Dhruv (short, plain words) only when a new review round waits for him, a batch is `stuck`, or
   everything is finalised. Otherwise no notification.

The tracker: https://dhruvashara07.github.io/Exam-bank/#batches shows every backlog batch and each paper's
stage (Uploaded → Processed → Auto-checked → Claude checked → Your review → Finalised).
