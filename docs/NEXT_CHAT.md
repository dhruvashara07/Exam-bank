# Starting a new chat (Dhruv, updated 2026-11-16)

One batch per chat (docs/MATHS_PLAN.md section 5). Open a new chat, paste the prompt, nothing else needed.
If a batch is not finished when the chat gets long, the chat writes "continue <batch>" here and you paste that.

## THE prompt (works for every chat from now on - paste it as it is; updated 2026-11-16)
> Exam-bank (repo dhruvashara07/Exam-bank). Follow docs/START_HERE.md exactly: git pull, then read every file it lists
> (PROGRESS.md NEXT line first). Do the task the NEXT line names with the batch log (docs/PLAYBOOK.md): if a review
> round is answered, read its feedback, fix every wrong item as a CLASS (search all papers of the batch), then ONE
> Claude check round (`pipeline/claude_check.py`: rules on every paper + side-by-side sheets for every doubtful item,
> each passed with its reason or fixed), golden 0 and nothing changed under 0625-physics, then the next review round on
> the same review page, or approve.py when the round is clean; if nothing is pending start the next batch of
> docs/MATHS_PLAN.md. Update every doc the playbook names and the batch-cycle skill for every new pattern without being
> asked, push with pipeline/push.sh, write the NEXT line. Ask me with options only for real decisions. Keep messages short.

Why one prompt: the state lives in the repo (PROGRESS NEXT line, BATCH_LOG, review/rounds, ERROR_PATTERNS), not in the
chat. If the repo layout or the rules change, change START_HERE / PLAYBOOK - never this prompt.

## (2026-11-17 evening: round 33 waiting for Dhruv; the same prompt continues M1)

## (done 2026-11-16, M0 pilot approved: 60 papers; next = M1)

## (done 2026-11-16, third M0 chat) rounds 28-29 fixed, one Claude check round, round 30 published

## (done 2026-11-14, second M0 chat) continue maths pilot M0: round 27 fixed, round 28 published

## (done 2026-11-13, first M0 chat) maths pilot M0
> Exam-bank (repo dhruvashara07/Exam-bank). Follow docs/START_HERE.md exactly: git pull, then read the files it lists.
> Task: maths 0607 pilot batch M0 = sessions 2014-MJ, 2019-ON, 2021-FM, 2025-MJ (docs/MATHS_PLAN.md section 4).
> Make the pipeline handle maths (formula page, mark-scheme layout, maths text as LaTeX for KaTeX, the problems in
> MATHS_PLAN section 3) without changing physics, run the full cycle with the batch log, ONE short review round on
> the same review page, then fix, approve, update every doc and push. Ask me with options when you need a decision
> (for example the mark-scheme column layout: show me original and ours side by side). Keep messages short.

## Prompts for the next batches (same text, change the batch line)
- M1: `Task: maths 0607 batch M1 (docs/MATHS_PLAN.md section 5), full cycle as in the playbook.`
- M2: same with M2.  M3: same with M3 (it needs 2019 May/June from me: remind me first).  M4: same with M4.
- Continue an unfinished batch: `Task: continue maths batch <M?> from PROGRESS.md NEXT line.`

## Using less of the weekly limit (what costs most)
1. Long chats: every step re-reads the whole conversation. One batch per chat.
2. Pictures stay in the conversation: look at small crops and grids, not full pages.
3. Collect fixes, rebuild once per pass (GitHub builds are free).
4. Text dumps (`ms_align.py dump`) instead of pictures where text is enough.
