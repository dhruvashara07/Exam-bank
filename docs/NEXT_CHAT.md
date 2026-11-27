# Prompt for the next chat
Exam-bank (repo dhruvashara07/Exam-bank). First add the repo with push access. Follow docs/START_HERE.md exactly: git pull,
then every file it lists (for chemistry read docs/CHEM_PLAN.md instead of MATHS_PLAN), PROGRESS.md NEXT line first. Section 5
(usage budget) applies.
Task: chemistry batch C2 (docs/CHEM_PLAN.md section 6: 2021-FM .. 2023-ON, 125 papers - split C2a / C2b if the chat
cannot hold it; C1 approved 2026-11-27). Full cycle (skill exam-batch-cycle): GitHub pass 1 (with the ms_marksum hint), ONE
Claude check round (also a word-overlap and black-shape check over every mark scheme; look at EVERY question a layout fix
changes), pass 2, my review round on the chemistry review page (own account), fixes as classes gated to 0620, freeze checks
(golden 0, nothing under 0625/0607, maths ms_layout hash = baseline, computed in the same repo), approve, docs, push with
pipeline/push.sh, write the NEXT line. Maths runs in the shared account at the same time: pull before every push.

# Maths M4 (separate chat)
Exam-bank (repo dhruvashara07/Exam-bank). First add the repo with push access. Follow docs/START_HERE.md exactly: git pull,
then every file it lists, PROGRESS.md MATHS NEXT line first. Section 5 (usage budget) applies.
Task: maths batch M4 (docs/MATHS_PLAN.md section 5: 2014-ON 2015-MJ 2015-ON 2016-MJ 2016-ON 2017-MJ 2017-ON, ~115 papers).
Full cycle (skill exam-batch-cycle): GitHub build, ONE Claude check round, picture redraws in the batch itself (ms_graphs:
graphs on the printed grid, trees from pipeline/tree_geom.py, dot paper as whole pictures), Dhruv's review round (~10 items +
the 5 round-44 recheck items in PROGRESS), fix as classes, golden 0, nothing under 0625/0620, approve, docs, push with
pipeline/push.sh, write the NEXT line. Ask me with options only for real decisions. Keep messages short.
