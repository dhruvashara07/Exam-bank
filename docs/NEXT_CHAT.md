# Starting a new chat (Dhruv, updated 2026-11-11)

When: a new chat when this one gets long (about one 3-year batch per chat), not a fixed rule.

## Prompt to paste (next: cleanup, then the MongoDB push)
> Exam-bank (repo dhruvashara07/Exam-bank). Start with `git pull --rebase`, then read docs/AGENT_GUIDE.md, CLAUDE.md,
> docs/PLAYBOOK.md, docs/ERROR_PATTERNS.md, PROGRESS.md (top) and the last two days of docs/CONVERSATION_LOG.md.
> State: every year 2002-2026 is approved (2002-2012 on 2026-11-12, round 26 closed).
> Task: cleanup first (list what is unneeded in git and Cloudinary, show me the list before deleting anything;
> never delete original PDFs), then the one MongoDB + Cloudinary push through the GitHub Action (re-enable the paused
> steps in bank.yml), then check what landed. Keep messages short and tell me when you need my input.

General form for later tasks: same prompt, with "Task: <e.g. cleanup + MongoDB push>".

## Where things are
- Rules for every mark scheme: docs/MS_TABLE_RULES.md (sections 1-18). Decisions: docs/CONVERSATION_LOG.md.
- Review page (same link every round): https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e (review/portal.json review_url); rounds: pipeline/review_round.py + review_page.py (feedback_r<n>).
- Layout-only rebuild of all years (~23 min, 4 at a time, low memory): for each paper
  `python3 -c "import sys;sys.path.insert(0,'pipeline');import store as S;S.build('0625_2024MJ_41')"`, then
  `python3 pipeline/store.py dupes <session>`. Full re-cut only when a cut rule changes: `JOBS=4 python3 pipeline/run.py 2024-MJ/41 ...`.
- Do not run 4 builds of very old papers with the old code: one full-page 8x render used to take 3 GB (fixed: strips).
- Side-by-side check pictures: render original MS crop | our SVG with Chromium (see review_assets.py).

## Using less of the weekly limit (what costs most)
1. Long chats: every step re-reads the whole conversation, so cost per step grows. Start a new chat per year-batch / task.
2. Pictures I look at stay in the conversation: look at fewer, smaller crops (only the changed rows), not full sheets.
3. Re-running all years after every small fix: batch fixes first, then one rebuild + one diff of "what changed".
4. Let GitHub do builds (free for the weekly limit); I only check and fix.
5. Short replies and one review round per batch (2-3 years together, as for 2025-2026).
