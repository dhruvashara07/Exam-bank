# Context for a new Claude chat (read this first, then docs/CONVERSATION_LOG.md, CLAUDE.md, PROGRESS.md, docs/V5_SPEC.md, docs/NEXT.md)

IMPORTANT: docs/CONVERSATION_LOG.md holds the dated record of what Dhruv said and decided in each session. Read it, and append to it at the end of every session.

STATUS 2026-11-03: the hourly backlog task is switched OFF (paused by Dhruv) until format v5
(docs/V5_SPEC.md) is approved and every year rebuilt. Its last run's work is in git.

## Who and what
Dhruv (teacher, India, IST; reads on his phone) is building a question bank of Cambridge IGCSE Physics 0625
past papers, 2002–2026, for his website **learnerspoint** (Next.js pages router + React + Tailwind +
MongoDB, `QuestionV2` model, `QuestionBlock`/`QuestionCard` components; code was shared as a zip).
Goals: a topic question bank like Save My Exams / Revision Village (topics later), a homework / test
builder (pick questions or parts → exam-style A4 PDF + mark scheme), full past papers as PDFs.

## How he wants to work
- Plan first, explain every decision, criticise his ideas honestly, ask before big changes.
- He reviews only flagged questions + a few spot checks on the review page; Claude does the rest.
- Short, plain answers; exact navigation steps when he must do something (phone first).

## Where things are (details: README.md)
- Original PDFs: GitHub Releases (`raw/manifest.json`); `pipeline/raw_store.py fetch`.
- `bank/` = cut records (where each question/part/MS row is on the page), checks, links.
- `store/` = THE data set (docs/STORE_DESIGN.md): per question JSON with layout units (words with
  position/size/style, lines as SVG paths, figure refs), figures one file per label at true size
  (vector SVG, photos PNG), MS rows, MCQ options, duplicates stored once, self-repair patches.
- Review page (same link every round): https://claude.ai/artifact/LGic38rQwKjkZze9jL1zmq
  (`review/portal.json`; answers in its database, collection `feedback_r<n>`).
- Tracker (public): https://dhruvashara07.github.io/Exam-bank/#batches (GitHub Pages, site/).
- Hourly backlog run: scheduled task trig_0173DCrQWm76nnTXrW52TPjC, runbook docs/BACKLOG.md, state in
  review/backlog.json (older years 2014→2002 alternating with new-format re-reviews of 2015–2026).
- MongoDB / Cloudinary: paused until everything is finalised (upload once, at the end).

## Decisions so far (newest last)
1. No per-question SVG pieces; layout data + figure files (STORE_DESIGN.md).
2. Tables are text + rules in the layout, never pictures — unless the table contains a picture/graph.
3. Checkboxes, answer boxes, empty grids, answer lines are vector lines in the layout (drawn by the UI).
4. MCQ options as a list; drawn options one figure each.
5. Dynamic numbering (docs/NEXT.md §1): captions stored as text (not inside figure files), references and
   part labels tagged; the UI/PDF renumbers (first selected part becomes (a)); references to another
   question stay as printed and are flagged.
6. Question-bank prototype v1 (docs/NEXT.md §2) after the numbering work: Next.js static on GitHub
   Pages, modes "question bank" (answer space removed) and "print" (full layout).
7. 2026-11-03: question-bank view keeps only fill-in dots, labelled last answer lines, tables and grids; mark schemes are
   re-laid-out in PORTRAIT (landscape 2016-2026 tables re-wrapped at question-paper font size). Details: docs/CONVERSATION_LOG.md.
8. Later: phone reading mode (reflow), topics/units/keywords ("talk later").

## Open feedback from review round 4 (2014), to handle
- "Table concern" on many P5/P6 questions: he could not tell tables (now layout text) from figures on the
  review page, and some tables are still stored as figure pictures when grid detection failed (e.g.
  0625_2014MJ_61_q03 Table 3.1). The review page must show clearly: each figure separately with its
  label, and tables marked "stored as text".
- Figures not split / wrong crops: 0625_2014MJ_51_q01 (Fig 1.1–1.3), 0625_2014MJ_52_q04 (Fig 4.1),
  0625_2014MJ_53_q01 (four pictures; crop must stop above the 'carry out' line), 0625_2014MJ_61_q03.
- 0625_2014MJ_21_q11: bracket notation across the first line wrong.
- He asked how empty grids / rectangles are made: they are vector lines in the layout data.
