# Playbook: how a batch is done (read docs/AGENT_GUIDE.md first for the why)
Goal: all 0625 papers 2002-2026 final in git, then cleanup + one MongoDB push at the end (Dhruv decides when).
State: see PROGRESS.md top. Rules for mark schemes: MS_TABLE_RULES.md. Mistakes not to repeat: ERROR_PATTERNS.md.
Decisions: CONVERSATION_LOG.md (last two days). Use the weekly limit carefully: small crops, one rebuild per batch,
GitHub builds, 3 years per batch, a new chat after each batch (long chats cost more per step).

## Steps for a batch of 3 years (e.g. 2005-2007)
1. `git pull --rebase`; `pip install -r requirements.txt` if needed; read PROGRESS.md, ERROR_PATTERNS.md.
2. Build on GitHub (free): `gh api -X POST repos/dhruvashara07/Exam-bank/actions/workflows/bank.yml/dispatches
   -f ref=main -f 'inputs[sessions]=2005-MJ 2005-ON ...'`; wait (`gh api .../actions/runs?per_page=3`); `git pull`.
3. Locally: `raw_store.py fetch` the papers; `run.py <ses/p ...>` (JOBS=4); `checks.py 0625/<ses>/<p> ...`
   (must be 0 blocking). Every paper: marks = total.
4. Fix patterns in the pipeline, never single JSONs. Gate era-specific fixes (e.g. `pre09`) so approved years do not change.
5. Mark-scheme sweep over `store.load(qid)['ms_p']`: no 'TOTAL', no bracketed totals, no codes in Answer, no side
   notes; then look at ONE MS of each paper type with `store.review_svgs` (small, 60 dpi grid).
5b. Rows by meaning (MS_TABLE_RULES 17): `python3 pipeline/ms_align.py list <sessions>`; for each question listed,
   `ms_align.py dump <qid>` (paper parts + MS lines, as text: cheap), decide the part of every MS line by reading
   both, write the map in pipeline/ms_map.json, rebuild those papers, list again until empty. Then look at a few
   with `pipeline/ms_grid.py` (our tables as students see them). On the grid check for every question: rows in the
   paper's order, no part twice, no combined part that could be split (MS_TABLE_RULES 18), no gaps or stray bars,
   every line with a mark has its mark. When a line cannot be given ONE part without guessing, keep Cambridge's
   printed group instead (MS_TABLE_RULES 20) - one row per marking point under the group label.
   After mapping, VERIFY every mapped question: its row labels must equal its map's labels (a prefix that
   matched the wrong line passes ms_align): `python3 pipeline/ms_align.py verify` must print 0 - ERROR_PATTERNS 52. Rebuild with JOBS=1 and check `git status` shows the papers changed (a JOBS=4 run left some unchanged).
6. Golden: fetch golden PDFs, rebuild them, `golden.py check` = 0 changed cuts; `git status` shows no store/bank change
   outside the batch.
7. Review round: `review_round.py new <n> <ids> --sample 1 --max 90 --title ... --intro ...`;
   page folder `out/review/page/` (`review_page.py add <n> <title>`); publish with publish_files to the review page
   (slug b3c8a710-c92b-4a33-95b2-f7eba1bc0031, portal.json review_url) in mode replace (closed rounds go).
   Same link every time: https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e
7b. Figure crop warnings: compare the stored figure with the PAGE (orig), never judge the crop alone - a crop
   missing its top half still looks like a whole picture (ERROR_PATTERNS 56).
8. Dhruv answers; read collection `feedback_r<n>` (db_list). Add every new pattern to ERROR_PATTERNS.md and a rule to
   MS_TABLE_RULES.md; fix; rebuild once; re-sweep; `review_round.py close <n> <answers.json>`.
9. Approve: `approve.py <ids> --note "..."` (a year counts as approved once its round is done and wrong items are fixed).
10. PROGRESS.md (state + usage line), CONVERSATION_LOG.md entry, NEXT_CHAT.md task line; `pipeline/push.sh "msg"`.

## Batches left
2005-2007, 2008-2010, 2011-2012, then cleanup (unneeded files in git/Cloudinary) + MongoDB push.
