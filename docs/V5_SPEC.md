# Store format version 5 — DRAFT for Dhruv's approval

One final format before every year is rebuilt once and reviewed. Cuts (where each question, part and
mark-scheme row is on the page) stay as they are; only how a cut is turned into data changes.
Status: draft (2026-11-03). Nothing below is built yet.

## A. Text and layout (unchanged from v4)
Words with exact position, size, font family, bold/italic, colour; lines/boxes as vector paths (answer
lines, checkboxes, empty grids, table rules, rectangles are all drawn this way — never pictures).

## B. Figures
1. One figure = one label ("Fig. 3.1"). Two labels side by side or stacked → two files. One label over
   several drawings → one file.
2. The figure file holds the drawing ONLY. The caption ("Fig. 3.1", "(not to scale)") is layout text.
3. Vector drawings → SVG (exact copy of the PDF's lines and text, sharp at any zoom). Photos / shaded
   pictures → PNG at the PDF's own resolution (300 dpi). No re-drawing, no up-scaling.
4. Each figure keeps its printed size and label data (size in mm, `measure`, scale note, source).
5. Crops stop at the drawing's own ink: never include instructions or answer lines under it (round 4:
   2014 MJ 53 Q1).

## C. Tables
1. A ruled table is text + rules in the layout. Rule: it becomes a picture ONLY if a cell contains a
   picture or a graph/diagram. Its caption "Table 2.1" is layout text.
2. Tables the detector misses today (round 4: 2014 MJ 61 Table 3.1, 62 Table 2.1, …) are fixed; every
   remaining table-as-picture is listed in the review with the reason.
3. The store records each table's cells (row/column text) as well, for search and for a reflowing
   phone view later.

## D. Dynamic numbering (docs/NEXT.md §1)
- Stored text keeps the original words in their exact place; tags say what to renumber:
  `role: qnum` (question number), `caption` + `ref {kind fig|table, q, n}`, `figref` (references in
  question text, options and mark scheme), `partlabel {path}`, `partref` ("your answer to (a)").
- Shown in the question bank: question number N, Fig. N.k / Table N.k.
- Worksheets: questions 1..n; parts relabelled in order of the selected parts (first selected becomes
  (a)); every reference follows. A reference to another question ("Fig. 2.1 in Question 2") stays as
  printed and is flagged; the question's own numbers still change.
- One shared renumbering function, used by the website and the PDF builder.

## E. Question-bank view vs print view
- Every layout unit carries `answer` bands (y ranges): dotted answer lines, "… = ………… unit" lines,
  blank working space, answer boxes. Question-bank view hides them and closes the gap; print view keeps
  the full Cambridge layout. Grids/diagrams students draw on are kept in both.

## F. Multiple choice (unchanged)
`options` A–D: table rows (cells), one figure per drawn option, text, or `options_on_figure`.

## G. Mark schemes (unchanged) + scans
Rows under the part they mark (codes, marks, layout). Scanned mark schemes (Nov 2002): page pictures.

## H. Checks
- Every unit redrawn and compared with the page (store verify, self-repair patches, exact fallback).
- New: every figure checked to hold exactly its own label's drawing (no caption, no neighbour).
- Review page: sharp previews (2x), each figure shown separately with its label, tables marked
  "stored as text", answer bands shown in a second "question bank view" picture.

## I. Not in v5 (later)
Phone reading mode (reflow), topics/units/keywords, MongoDB/hosting load.

## Order of work
1. Wait until no backlog run is active (review/backlog.json `running_since` empty); the hourly task
   trig_0173DCrQWm76nnTXrW52TPjC is switched OFF and stays off until step 6.
2. Fix round 4 findings + build v5 on a few hard papers; show Dhruv examples (question bank view, print
   view, worksheet PDF with renumbering).
3. Dhruv approves → rebuild store/ for every processed year (2013–2026 and pilots) + full verify.
4. Review page upgrade (H).
5. Update BACKLOG.md for v5 (the 2014 round 4 answers are already handled; re-check rounds use v5).
6. Switch the hourly task back on.
