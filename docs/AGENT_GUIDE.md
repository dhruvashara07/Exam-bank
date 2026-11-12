# Agent guide: what we are building and how to work on it

Read this first in any new session (chat, scheduled check, Claude Code). It is the "why" and the judgement;
docs/PLAYBOOK.md is the "how" step by step; CLAUDE.md has the hard rules; docs/START_HERE.md is the entry point.
Updated 2026-11-12: physics 0625 finished; maths 0607 started (docs/MATHS_PLAN.md).

## 1. The vision
Dhruv is a physics teacher in India (IST; he mostly reads on his phone). He is building a question bank of
Cambridge IGCSE past papers (Physics 0625, 2002-2026: done; International Mathematics 0607, 2014-2026: in progress,
maths text as LaTeX shown with KaTeX), for his website **learnerspoint** (Next.js + React +
Tailwind + MongoDB). With it, teachers and students can:
- browse past papers and single questions (later by topic, like Save My Exams / Revision Village);
- build homework and tests: pick questions or parts, then get an exam-style A4 PDF plus its mark scheme,
  with numbering redone (the first part picked becomes (a), Fig. 3.1 becomes Fig. 1.1 and so on);
- print full past papers.

So every question is stored as **data that redraws it exactly** (words with position, size and style; lines
as vectors; figures as separate files at true size; tables as text), not as screenshots. Mark schemes are
not copied as printed: every year, from 2002 to 2026, is redrawn in **one consistent table layout of our own**.
A student should not be able to tell which era a mark scheme came from.

End state: every paper is final ("approved") in git → cleanup of unneeded files → ONE push to MongoDB and
Cloudinary by the GitHub Action (never directly). After that: the question-bank prototype, a phone reading
mode, and topics (docs/NEXT.md).

## 2. What "done" means for one question
- Text, figures and tables cut right: nothing cut off, nothing from the next question, captions as text.
- Marks add up: part marks = question total = paper maximum.
- The mark scheme is in our table (full rules: docs/MS_TABLE_RULES.md). Short version:
  - Q | Answer | Marks columns, full black frame, header once, Total as its own last row;
  - no brackets in Marks ('[1]' shows as '1'), codes (B1, C1, M1, A1) bold in Marks and never in Answer;
  - no printed TOTAL or part totals, no F/C target-grade column, no stray page headers;
  - one row per part, labelled with the part where the marks are earned (worked out by reading the question
    and the answer with subject knowledge, not only from the printed label);
  - rows in the question paper's order; the same label on rows that follow each other is shown once;
  - parts split only where the marks can be split; one mark for two parts keeps a combined label like 1(a)(i)(ii);
  - no blank gaps inside a row, side notes beside their line, real font widths (nothing looks stretched).
- It has passed: checks.py (0 blocking), ms_align.py list (empty), ms_sweep, my own look at the pictures,
  then Dhruv's review round.

## 3. How Dhruv wants to work with you
- Short, plain messages. Say clearly when you need his input; otherwise keep going.
- You check everything first (every flag, every picture that matters) so his round has little left in it.
  He reviews only a short round on the same review page every time:
  https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e (answers in its database, collection feedback_r<n>).
- Be honest: criticise his ideas when needed, and say what you could not fix and why. Never claim something
  is done that you have not checked.
- Ask before big or irreversible changes. For a small layout decision, show the original and ours side by
  side as a picture instead of a review round.
- One 3-year batch per chat; start a new chat when the chat gets long. Before ending, update the docs so the
  next session can carry on without him repeating anything.
- Use the weekly usage carefully without lowering quality: let GitHub build, look at small crops and grids,
  rebuild once per batch, and dump text (ms_align.py dump) instead of pictures where text is enough.

## 4. How to decide things
- **Fix the pipeline, never one JSON.** Every complaint is a pattern: find what caused it, fix it in code or
  data (ms_map.json), and look for the same pattern in other questions before the round.
- **Never repeat a mistake.** Each new mistake goes into docs/ERROR_PATTERNS.md, and a rule into
  MS_TABLE_RULES.md when it is about layout. Read ERROR_PATTERNS before starting.
- **Approved years must not move.** Gate era-specific fixes (pre09 = year < 2013 in ms_layout). Before every
  push, `golden.py check` must show 0 changed cuts, and `approve.py --pending` must not list approved papers.
- **Use subject knowledge.** Old mark schemes print labels loosely; read the question and decide which part
  each answer belongs to. If you are unsure, put that question in the round with a note rather than guess.
- **Look at it as a student would.** Render our tables (ms_grid.py, review_svgs with Chromium) and read them:
  order, labels, marks in the right place, gaps, stray lines, fonts.

## 5. Where things are
| Need | File |
|---|---|
| Entry point for every chat | docs/START_HERE.md |
| Maths plan, batches, rebuild rules | docs/MATHS_PLAN.md |
| Times / errors per batch | docs/BATCH_LOG.md (pipeline/batch_log.py) |
| Subject differences | pipeline/subjects.py |
| Maths fixes kept for a later physics pass | docs/PHYSICS_LATER.md |
| Hard rules (push, keys, PDFs, MongoDB) | CLAUDE.md |
| Steps for a batch | docs/PLAYBOOK.md |
| Current state, what is next | PROGRESS.md (top section) |
| What Dhruv decided, by date | docs/CONVERSATION_LOG.md (read the last two days; append before ending) |
| Mistakes never to repeat | docs/ERROR_PATTERNS.md |
| Mark-scheme layout rules | docs/MS_TABLE_RULES.md |
| Prompt for the next chat | docs/NEXT_CHAT.md |
| Data format | docs/STORE_DESIGN.md, docs/V5_SPEC.md; layout code pipeline/ms_layout.py |
| Old-paper row map | pipeline/ms_map.json (+ ms_align.py list/dump) |

## 6. State on 2026-11-12
Physics 0625: every year 2002-2026 approved and frozen (golden set guards it). Cleanup done (Cloudinary empty).
Maths 0607: plan agreed (docs/MATHS_PLAN.md): pilot M0 (2014-MJ, 2019-ON, 2021-FM, 2025-MJ), then batches M1-M4,
one new chat each. Nothing goes to MongoDB/Cloudinary until Dhruv says so.
