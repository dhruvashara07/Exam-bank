# Prompt for the next chat
Exam-bank (repo dhruvashara07/Exam-bank). First add the repo with push access. Follow docs/START_HERE.md exactly: git pull,
then every file it lists (for chemistry read docs/CHEM_PLAN.md instead of MATHS_PLAN), PROGRESS.md NEXT line first. Section 5
(usage budget) applies.
Task: chemistry batch C2a = 2022-ON 2023-FM 2023-MJ 2023-ON (59 papers; C2 split, C2b = 2021-FM .. 2022-MJ next; C1 approved
2026-11-27). 2023-ON paper 51 is not in Releases (Dhruv asked to upload it; if still missing, record it as not done like maths
2019 MJ and build the other 17). Before building: maths M4 changed shared pipeline/ms.py - confirm `SYL=0620 ms_rebuild.py` over
the C0 + C1 sessions lists only 2026-MJ/p41/q04 (known). Full cycle (skill exam-batch-cycle): GitHub pass 1 (with the ms_marksum
hint), ONE Claude check round (also `python3 pipeline/ms_overlap.py 0620 <sessions>`: words overlapping / black shapes; look at
EVERY question a layout fix changes, not one twin), pass 2, my review round on the chemistry review page (own account,
PCdP6oibAkjQvGz8mKm73e), fixes as classes gated to 0620, freeze checks (golden 0, nothing under 0625/0607, maths ms_layout hash =
baseline computed in the same repo), approve, docs, push with pipeline/push.sh, write the NEXT line.

# DONE 2026-11-28 - Maths M4 finish: 2014 ON paper 5 (51 = 52 = 53) (kept for reference)
Exam-bank (repo dhruvashara07/Exam-bank). First add the repo with push access. Follow docs/START_HERE.md exactly: git pull,
then every file it lists, PROGRESS.md MATHS NEXT line first. Section 5 (usage budget) applies.
Task: make 2014 ON 51 approvable (52 and 53 are stubs of 51, so they follow). Its mark scheme is the only thing wrong
(ERROR_PATTERNS 334; see it with `python3 pipeline/ms_compare.py /tmp/rr 0607_2014ON_51_q02 0607_2014ON_51_q03 0607_2014ON_51_q04`;
PDFs: `python3 pipeline/raw_store.py fetch 0607/2014-ON/51`):
- q2: the Partial Marks column is lost (3-column 'wrap' table drawn as 2 columns plus Marks).
- q3: 3(b)(i) is pushed right into its own box with a line under it; it must sit in the Answer column like 3(a) and 3(b)(ii).
- q4: the answer table gets stray braces/edges, its cells are squashed, and the Marks column shows '1 5 1 6 2 4 5' (pieces of the
  'B1 for ... row 1 column 5' text) instead of one mark 4; the B1 lines belong in the Partial Marks column.
Fix them as CLASSES in the maths code (ms.py / ms_layout.py _maths_ruled / ms_maths.py), never single JSON files. After EVERY
ms.py change run the full MS blast over all 0607 schemes and confirm no APPROVED paper's labels or cuts change (pattern 330). Then
run.py 0607/2014-ON/51 0607/2014-ON/52 0607/2014-ON/53, look at q1-q6 of 51 (question AND mark scheme, ms_compare, every row),
check totals, golden 0, nothing under 0625/0620, check `git status review/approvals`: every approval that disappeared means a
changed cut - look at exactly what changed before re-approving. If all is right: approve 51/52/53 with pipeline/approve.py
(no round needed for 3 rows of one paper unless a decision is Dhruv's; then ask with options). Docs (START_HERE section 4), push
with pipeline/push.sh, write the MATHS NEXT line.
Lessons from the M4 chat (do not repeat): `store.py` needs `build <paper>` (run.py already stores - do not start a second store
run, never stop a run that is writing); check review/queue.json for 'store build failed' first; a fitz Rect `|=` is not in place;
judge a picture by a crop of EVERY changed item, not a sample. Keep messages short.

# Maths M3b (only when Dhruv has uploaded 2019 MJ; separate chat, shared account)
Exam-bank (repo dhruvashara07/Exam-bank). First add the repo with push access. Follow docs/START_HERE.md exactly: git pull,
then every file it lists, PROGRESS.md MATHS NEXT line first. Section 5 (usage budget) applies.
Task: maths batch M3b = 2019-MJ (docs/MATHS_PLAN.md section 5). Full cycle (skill exam-batch-cycle): GitHub build, ONE Claude
check round (also: review/queue.json 'store build failed' = 0 for the batch, pattern 340; intro figures of papers 5/6, 338),
picture redraws in the batch itself, my review round, fix as classes (maths-gated), full MS blast after every ms.py change,
golden 0, nothing under 0625/0620, approve, docs, push with pipeline/push.sh, write the NEXT line. Ask me with options only
for real decisions. Keep messages short.
