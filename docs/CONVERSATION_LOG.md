# Conversation log and decisions (newest at the bottom — add an entry after every working session)

Purpose: a new Claude chat reads this after CONTEXT.md so it knows what was decided, why, and what Dhruv said.
Rules for Claude: append a dated entry at the end of every session (what he asked, what he answered, what was
decided, what was built, what is open). Never rewrite his decisions; if one changes, add a new entry that says so.

## Working style (stable)
- Dhruv: teacher in India (IST), reads on his phone. Short, plain answers; exact steps when he must do something.
- Plan first, explain decisions, criticise his ideas honestly, ask before big changes, "check first, then plan, then proceed".
- He is usage-conscious: do NOT rebuild everything or run expensive jobs unless approved; prefer samples first, then year by year.
- He reviews only flagged questions and a few spot checks.

## 2026-11-03 — v5 format session (claude.ai chat, IST morning)
Asked: read the docs, go through docs/V5_SPEC.md (explain + criticise), build v5 on a few hard papers incl. his round-4
problem questions, show examples (question-bank view, print view, renumbered worksheet PDF) before any rebuild.
Hourly task trig_0173DCrQWm76nnTXrW52TPjC stays OFF until he approves.

His answers / decisions:
1. Question-bank view: remove blank working space and full-width dotted answer lines. KEEP dots inside a sentence
   (fill in the blank), the last answer line with its label/unit (`m1 = ....... g`), tables to complete, grids/graphs to draw on.
2. Review page / Claude artifacts: leave public (no need for private).
3. Final website will make the "stored as text" vs picture distinction clear (not needed on the review page now).
4. He answered more than 2 questions in review round 4 (70 items: 50 ok, 20 wrong); general instruction from him:
   tables are text built from the layout (never pictures unless a cell holds a picture/graph).
5. Pilot papers for v5: yes. Claude chooses the worksheet parts itself (incl. "(b)(ii)" -> "(a)" case, cross-question reference). Read his round-4 answers: yes.
6. Stale lock in review/backlog.json (`running_since`, from a run that crashed 2026-11-03 00:06 IST): NOT cleared.
   He said: if not necessary, leave it. It blocks nothing while the task is off; clear it when the task is switched back on.
7. Renumbering safety: tested 376 cases (pilot questions x new numbers 1, 9, 10, 12): no line overflows; the only word
   overlaps (Greek letter + "/") already exist in the original layout. Worksheet numbering = questions 1..n, parts relabelled
   in print order, figure/table numbers follow, references follow.
8. Built (pilot papers only, pushed): pipeline/store_v5.py, renumber.py, store_view.py; store.py schema 5: captions are layout
   text (figure file = drawing only); if drawing ink shares the caption row the caption is blanked in the file
   (`caption_masked`, `caption_box`) and stays layout text; tables as text; tagged numbering roles; answer bands;
   golden.py check = 0 changed cuts (2014 MJ 52 q04 now cuts Fig 4.1).
9. MARK SCHEMES -> PORTRAIT (decided 11:10 IST): Cambridge mark-scheme PDFs are portrait up to 2016 FM and mostly landscape
   (4 columns Question | Answer | Marks | Guidance) from 2016 MJ to 2026. Stored landscape width 726 pt vs portrait 523 pt.
   Dhruv's decision: make them PORTRAIT like the question paper, same table look, text at the question-paper font size,
   pictures scaled to fit; text wraps to more lines (3 -> 4-5), that is fine. Reason: consistency, no rotation, good for print.
   Claude's plan: keep the original landscape layout stored; build a second "portrait" layout by re-wrapping the cell text;
   rows that cannot be re-wrapped (stacked fractions, table in a cell, graphs) are scaled to fit and listed for review;
   check = every word present in order, nothing overflows, marks add up (pixel compare is impossible for a re-wrapped layout).
10. Process agreed 11:14 IST: build SAMPLES on 3 papers (2019 MJ 42, a 2022 paper, 2014 MJ 63), show results, he approves,
    then move YEAR BY YEAR (not one big rebuild). Add this log to the repo each session.

Open at end of this entry: practical-paper mark schemes are one block per question; MS row labels like "(a)(i)(ii)" not relabelled;
"°C" glyph in some 2014 mark schemes; 63 q02 Fig 2.1 crop edge includes the neighbour's label leader; v5 rebuild of other years,
review-page upgrade (spec H), BACKLOG.md update and switching the hourly task on all wait for his approval.

## 2026-11-03 (later, 11:30 IST) — portrait mark schemes: sample built, waiting for Dhruv's look
Dhruv: "sample, then give results, then year by year". Built `pipeline/ms_portrait.py` (+ `ms_portrait_view.py` picture tool); NOT yet part
of `store.py build` (nothing stored; the store still holds the landscape layout only).
Result over ALL stored landscape rows (2016 MJ - 2026 MJ, 9,007 rows): 8,759 (97.2%) re-wrapped to portrait at the question-paper
font size; 248 (2.8%) fall back to "scale to fit" (99 picture/drawn symbol in the row, 85 unknown rules (dashed or white boxes),
42 fraction bar, 18 table inside a cell, 4 other). Word check (all words present, nothing past the margin): 1 problem row
(2022 FM p32 q11 11(a), overflow). Wrapped rows grow in height by at most ~1.7x (2026 practical tables), typical rows +1-2 lines.
Handled: 3-, 4- and 5-column tables, marks column kept at its width and aligned to its lines, blank gaps between marking points,
bullets with hanging indent, sub/superscripts, underlines follow their words, right-aligned "Total:", grey rule colours.
Next (needs his OK on the samples): store the portrait layout as `layout_p` per row in store.build, verify (word check + spot pictures),
improve picture rows (keep the picture at natural size, wrap the text), then year by year.
