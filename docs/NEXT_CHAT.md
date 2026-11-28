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

# Maths M3b (only when Dhruv has uploaded 2019 MJ; separate chat, shared account)
Exam-bank (repo dhruvashara07/Exam-bank). First add the repo with push access. Follow docs/START_HERE.md exactly: git pull,
then every file it lists, PROGRESS.md MATHS NEXT line first. Section 5 (usage budget) applies.
Task: maths batch M3b = 2019-MJ (docs/MATHS_PLAN.md section 5). Full cycle (skill exam-batch-cycle): GitHub build, ONE Claude
check round (also: review/queue.json 'store build failed' = 0 for the batch, pattern 340; intro figures of papers 5/6, 338),
picture redraws in the batch itself, my review round, fix as classes (maths-gated), full MS blast after every ms.py change,
golden 0, nothing under 0625/0620, approve, docs, push with pipeline/push.sh, write the NEXT line. Ask me with options only
for real decisions. Keep messages short.
