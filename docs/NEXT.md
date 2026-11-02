# Next work (agreed with Dhruv, 2026-11-02)

## 1. Dynamic numbering (do first)
Today a figure's caption ("Fig. 1.1", bold, under the drawing) is drawn inside the figure file, so it cannot
be renumbered. A question in the question bank or on a worksheet gets a new number, so every number that
belongs to the question must follow it.

Store (keep the original text and exact layout; the number is replaced when shown):
- **Captions**: cut figures WITHOUT their caption; the caption becomes layout words with
  `role: "caption"`, `ref: {kind: "fig"|"table", q: 3, n: 1}` (Fig. 3.1). Table captions the same.
- **References in text**: every "Fig. 3.1" / "Table 3.2" word in question text, options and mark-scheme
  rows gets `role: "figref"` + the same `ref`. "Fig. 2.1 in Question 2" (another question): `ref.other: true`
  — left as printed, and flagged in the review (`review.flags`).
- **Question number**: already `role: "qnum"`; mark-scheme labels `role: "mslabel"`.
- **Part labels**: `role: "partlabel"` with the part path; references to parts in text ("your answer to
  (a)") `role: "partref"`.
Rules when shown (website and PDF, one shared function):
- Question bank view: the question shows with its new number N; figures/tables become Fig. N.k / Table N.k
  (k in order of the question's own figures); references follow.
- Worksheets: questions numbered 1..n; parts relabelled in order of the selected parts — if the first
  selected part is (b)(ii) it becomes (a) — and part references in the text follow the same map.
- The original number and labels stay in the data (`number`, `path`, the words' `t`), for the source line
  ("0625/42 May/June 2024 Q3(b)(ii)").
Then: rebuild store/ for all years, run the full store verify, check a worksheet PDF with renumbering.
The hourly backlog run must be PAUSED while this is done (one Claude session on the pipeline at a time):
switch off trig_0173DCrQWm76nnTXrW52TPjC first, switch it back on (hourly) when pushed.

## 2. Question-bank prototype v1 (after 1)
- Next.js + React + Tailwind like learnerspoint (Dhruv's main site, Next.js pages router, MongoDB,
  QuestionV2 model), static export on GitHub Pages (public, like the tracker), reading the finalised store/.
- One React component `StoredQuestion` (props: question JSON, mode, number) that can move into learnerspoint.
- Modes: **Question bank** (answer space removed: dotted lines, blank working space, answer boxes — the
  store marks these as `answer` bands per unit at build time; the site hides them and closes the gap) and
  **Print** (full layout). Mark scheme show/hide, MCQ options + answer, "print to measure" on measure figures.
- Browse year → session → paper → question (topics later). Basket → worksheet + mark scheme PDF (A4, exact).
- Stress list: drawn options, rotated MS, scanned 2002 MS (`ms_scan`), `exact` pieces, measure figures,
  duplicates (stubs).
## 3. Later
- Phone reading mode (words grouped into lines/paragraphs, text reflows; figures scaled).
- Topics / units / keywords (Dhruv: "talk about it later").
