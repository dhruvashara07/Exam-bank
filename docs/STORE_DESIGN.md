# Question store: design

Code: `pipeline/store.py` (build / dupes / verify / sheet), with `store_units.py` (text styles, lines),
`store_options.py` (tables, multiple-choice options) and `store_text.py` (fonts and symbols).
Output: `store/<syllabus>/<year>-<session>/<paper>/` — this folder is the finished data set that will be loaded
into the database and the file host at the end. `bank/` keeps only the pipeline's cut records (where each
question, part and mark-scheme row is on the page; checks; approvals).

## What the store must do
1. Topic question bank like Save My Exams / Revision Village: list questions by topic, open one, see its
   mark scheme; later: topics, keywords, worked solutions.
2. Test / homework builder: pick whole questions or single sub-parts from any papers, get an exam-style PDF
   (exact Cambridge layout and answer space) plus the matching mark-scheme rows.
3. Full past papers stay available as the original PDFs (GitHub Releases).

## Decisions
| # | Decision | Why |
|---|---|---|
| 1 | **One JSON document per question** (`q01.json`), parts inside it | A question is what a teacher picks and what a topic lists; sub-parts need their stem, so they live in the same document. 5–60 KB, one database document each. |
| 2 | **Layout stored per part, as "units"** = one exact piece of a page (a part, or its continuation on the next page) | Any subset of parts can be printed: each unit is placed on the new page at its original left margin and size. Coordinates are points relative to the piece's top-left corner. |
| 3 | Unit content = **words** (text, x, baseline, width, size, family, bold/italic, colour) + **lines/boxes** (SVG path data, clipped to the piece) + **figure references** | Text stays text (searchable, editable later, 10× smaller than drawn SVG); widths keep every line break exactly where Cambridge put it. |
| 4 | **Ruled tables are text + rules in the layout, never pictures** (MCQ option tables and "Table 2.1" alike) | Searchable, sharp at any size, small. A crop counts as a table when it is only straight rules forming a closed grid with text in the cells (graph paper with 30+ rules is not). |
| 5 | **Figures are separate files**, one per label ("Fig. 3.1" = one file however many drawings; two labels = two files, also side by side). Vector → SVG, photo/shaded picture → 300 dpi PNG | One label = one figure is how teachers and students refer to them. Shaded pictures lose parts of their shading as SVG in browsers. |
| 6 | **Multiple choice: `options` A–D** on the question. Options in a table → each row's cells (+ `option_columns` = header). Options as four drawings → one figure file per option (`…_optA` … `_optD`). Options as text → the text. Letters marking points on ONE drawing (pins on a rod) → `options_on_figure: true`, the drawing stays whole | Website can show options as a grid on a phone, later clickable quizzes; print still uses the exact layout. |
| 7 | **Every figure keeps its printed size** and carries a label: id, source paper/page/box, size in pt and mm, caption, `measure` (the question asks to measure on it), scale note | PDFs/worksheets print figures at exactly that size (line lengths equal to 0.01 pt). The website may shrink them for a phone and say "print to measure" when `measure` is true. |
| 8 | **Mark scheme stored per row under the part it marks** (label, codes B1/M1/A1, marks, text, layout unit); MCQ key on the question (`answer`) | Selecting a part brings exactly its rows. |
| 9 | **Duplicates stored once**: the same question in two variants of one session → the lowest id keeps the content, the other is a stub `{stub: true, same_as: [id]}` | No double storage; a topic list shows it once; a test never gets it twice. If only the mark scheme differs, both keep content and point to each other. |
| 10 | **No empty fields for later phases.** Topics, keywords, difficulty, solutions are added when that phase starts; `schema` (now 4) says which version a document follows | Adding fields to JSON / MongoDB later is free; empty slots now would only guess at a shape we may change. |
| 11 | Fonts: Liberation Sans/Serif/Mono (free, same letter widths as Arial/Times/Courier) | Exact line fit; can be embedded in PDFs and served on the website. |
| 12 | Bold/italic for PDFs with hidden font names (2015 subsets, 2025+): from glyph ids and stroke thickness | Text extraction alone reports everything as regular. |
| 13 | Symbols that are not real characters (✓ ✗ from dingbat fonts, unknown codes): kept as their drawn shape in the layout; ✓/✗ as characters in option/table text | Never a blank box or a wrong character. |
| 14 | Faint background watermark (2026 mark schemes) ignored | Not content. |
| 15 | **Every unit is checked against the original page** (redrawn in Chromium, compared pixel by pixel); a unit more than 1 % different goes into the review round | The store is what students get, so the store is what is checked. |
| 16 | **Nothing goes to MongoDB / file hosting until every year is finalised in git** | Upload once, in the final format, after seeing the total size. |
