# Question store: design (draft, under test — not yet the pipeline)

Experiment code: `pipeline/experiments/qstore.py` (build / dupes / verify / sheet). This file records the
decisions and why, so the plan can be agreed before the pipeline is switched over.

## What the store must do
1. Topic question bank like Save My Exams / Revision Village: list questions by topic, open one, see its
   mark scheme; later: topics, keywords, worked solutions.
2. Test / homework builder: pick whole questions or single sub-parts from any papers, get an exam-style PDF
   (exact Cambridge layout and answer space) plus the matching mark-scheme rows.
3. Full past papers stay available as the original PDFs (GitHub Releases).

## Decisions
| # | Decision | Why |
|---|---|---|
| 1 | **One JSON document per question** (`<paper>_qNN`), parts inside it | A question is what a teacher picks and what a topic lists; sub-parts need their stem, so they live in the same document. Small (5–60 KB), one MongoDB document each. |
| 2 | **Layout stored per part, as "units"** = one exact piece of a page (a part, or its continuation on the next page) | Any subset of parts can be printed: each unit is placed on the new page at its original left margin and size. Coordinates are points relative to the piece's top-left corner. |
| 3 | Unit content = **words** (text, x, baseline, width, size, family, bold/italic, colour) + **lines/boxes** (SVG path data, clipped to the piece) + **figure references** | Text stays text (searchable, editable later, 10× smaller than drawn SVG); widths keep every line break exactly where Cambridge put it. |
| 4 | **Figures are separate files**, one per caption ("Fig. 3.1" = one file however many drawings; two captions = two files, also when side by side). Vector → SVG, photo/shaded picture → 300 dpi PNG | One label = one figure is how teachers and students refer to them. Shaded pictures lose parts of their shading as SVG in browsers. |
| 5 | **Every figure keeps its printed size** and carries a label: id, source paper/page/box, size in pt and mm, caption, `measure` (the question asks to measure on it), scale note ("full size", "not to scale", "1 cm represents …") | PDFs/worksheets print figures at exactly that size (checked: line lengths equal to 0.01 pt). The website may shrink them to fit a phone and says "print to measure" when `measure` is true. |
| 6 | **Mark scheme stored per row under the part it marks** (label, codes B1/M1/A1, marks, text, layout unit); MCQ key on the question (`answer`) | Selecting a part brings exactly its rows. |
| 7 | **Duplicates stored once**: the same question in two variants of one session (same words, figure sizes, marks, mark scheme) → the lowest id keeps the content, the other is a stub `{stub: true, same_as: [id]}` | No double storage; a topic list shows it once; a test never gets it twice. If only the mark scheme differs, both keep content and point to each other. |
| 8 | **Room for later phases**: `meta` on the question and on every part (`topics`, `keywords`, `difficulty`, `solution`), plus `schema` version number | Add topics/solutions later without touching layout; the version number lets old documents be migrated. |
| 9 | Fonts: Liberation Sans/Serif/Mono (free, same letter widths as Arial/Times/Courier) | Exact line fit; can be embedded in PDFs and served on the website. |
| 10 | Bold/italic for PDFs with hidden font names (2025+): from glyph ids (each style has its own glyph shapes) | Text extraction alone reports everything as regular. |
| 11 | Symbols that are not real characters (✓ ✗ from dingbat fonts, unknown codes): kept as their drawn shape | Never a blank box or a wrong character. |
| 12 | Faint background watermark (2026 mark schemes) ignored | Not content; would bloat every unit. |
| 13 | Exact SVG pieces (today's bank) kept until the new store has passed the same page-by-page checks on every paper | Safe switch-over; nothing lost. |
