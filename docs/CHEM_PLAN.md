# Chemistry plan: Cambridge IGCSE Chemistry 0620 (analysis 2026-11-25, pilot C0 next)

Physics 0625 and Maths 0607 are finished and FROZEN: nothing chemistry does may change one of their files. Chemistry goes
through the SAME pipeline, repo, Releases and review page, like maths did (docs/MATHS_PLAN.md is the model).

## 1. What we have (raw/manifest.json, 2026-11-25)
- 1599 PDFs, 2002 ON to 2026 MJ: 699 question papers, 677 mark schemes, 59 `ir_` + 59 `ci_` (confidential practical
  instructions for the supervisor), 4 `in_` inserts (2003-ON, 2009-MJ, 2015-MJ, 2018-MJ), er / gt (examiner reports,
  grade thresholds). FM (March) from 2015, variant 2 only. 2003-MJ / 2004 hold one combined `ms_1-2-3-5-6.pdf`.
- Analysed sample (fetched): 2005-MJ (all), 2015-MJ (11 21 31 51 52 61 + in_52, ir), 2024-MJ (11 21 31 41 51 61 + ci_51),
  mark schemes of 2010-MJ 31, 2019-MJ 41, 2020-ON 41, 2021-FM 42, 2022-MJ 41, 2023-MJ 41, 2026-MJ 41 + 2026-MJ qp_41.

## 2. The same as physics (no new code)
| Thing | Chemistry | Physics rule that already covers it |
| --- | --- | --- |
| Paper numbers | before 2009 one paper per component: 1 MCQ, 2 core theory, 3 extended theory, 5 practical, 6 ATP; 2009-2015 variants (11 21 31 51 61); from 2016: 1 MCQ core, 2 MCQ extended, 3 core theory, 4 extended theory, 5 practical, 6 ATP | `extract.paper_type_from_cover` + `OLD_PAPER_TYPES` (same numbering, same cover wording) |
| Totals | 40 / 80 / 40 / 40 (2005: 40 80 80 40 60 in the MS) ; printed on covers from 2020 | `STANDARD_TOTAL`, MS 'maximum mark' pre-2009 |
| Fonts | Arial / ArialMT, SymbolMT (→, °), Times, Bookman italic; 2005 nameless 'TT...o00' subsets | physics fonts of the same years (same Cambridge templates) |
| MCQ | 40 questions, A-D options, option diagrams without captions, key table in the MS | physics MCQ (answer key `answer`, T7) |
| Theory figures | 'Fig. 6.1' captions (blast furnace, apparatus, cells), tables 'Table 2.1' | physics figure / table cutting |
| Formulae in text | H2SO4, Cu2+, cm3 as Arial runs with sub / superscript spans; isotope notation (37 over 17 before Cl) like physics nuclide notation; '→' SymbolMT glyph; equations on their own line | physics store text (sub/sup runs kept, print exact) |
| Practical / ATP | tables with apparatus pictures in cells (thermometers, burettes), graph grids, 'For Examiner's Use' column (2005) | physics practical / ATP rules (patterns 6, 7, 17, 42) |
| Old MS 2002-2012 | text layout, '[1]' at the right, 'TOTAL = 12', 'accept / not / cond / ecf' notes | physics pre-2013 MS rules (patterns 11-63) |
| MS 2016-2025 | landscape table Q / Answer / Marks (3 columns), M1 M2 marking points, 'OR' lines, bullet lists | physics T1 standard table |
| MS 2013-2015 | table with Q / Answer / Marks / Guidance (A / I / R notes), page header box | physics T2 (guidance) |
| MS 2026 MJ | 4 columns Q / Answer / Marks / Guidance, marking points level with their guidance (29-page MS for paper 4) | physics 2026 Guidance rules (MS_TABLE_RULES 13) |
| Generic / Science marking principles pages | front pages of every MS | physics (not questions, skipped) |

## 3. What is new for chemistry
1. **Periodic table page** (last page of every MCQ and theory paper, rotated, 'The Periodic Table of Elements' + the
   'volume of one mole of gas is 24 dm3' line). Like the maths formula list: not a question -> coverage error on every
   paper today. Keep it ONCE per paper (`paper.data_sheet`, exact SVG), never inside the last question. (Decision D3.)
2. **Displayed / structural formulae** (C, H, O letters joined by drawn bonds, '=' double bonds, polymer brackets, dot-and-
   cross circles): with a 'Fig.' caption they are cut like physics figures; WITHOUT a caption (MCQ options, MS answer cells,
   some theory parts like 'H-C-C-C=O' in 2024 ms_41 7(d)(iii)) they must still be ONE picture with their letters, never
   text + loose lines. Questions: a chemistry 'uncaptioned structure' cluster rule (letters + bonds) gated to 0620. MS cells:
   physics T4 picture rows already keep drawings whole; the pilot checks it.
2b. **Equation arrows**: '→' is a glyph; the 2005 papers draw a long arrow as a line + head (drawing beside text) and the
   reversible arrow '⇌' was not met in the sample (pilot checks how it is printed: glyph, two half-arrows drawn, or font).
   A drawn arrow inside an equation line is text-line ink, not a figure (gate 0620).
3. **Formulae as editable text** (website): physics keeps sub/sup runs. Options in D1 (runs as physics, or LaTeX with mhchem).
4. **Practical inserts / instructions**: `in_` inserts (4) hold material the candidate uses (a data table, a key);
   `ir_` / `ci_` are supervisor instructions (not for students). Plan: ir / ci never processed (as inbox.py already does);
   the 4 inserts are attached to their paper as a picture resource (my call; tell me if you want them out).
5. **Old file names** (2002-2009): chemistry has only qp_1 / ms_5 (no qp_01 copies) and combined files
   (`ms_1-2-3-5-6.pdf`, `qp_3` holding 31 + 32 in 2008-2009?). `pipeline/old_papers.py` is hard-coded to '0625' -> give it a
   syllabus argument and run it for 0620 (writes renamed copies; originals untouched). Needed only for batches C0 (2005),
   C7, C8, and C6 (2009).

## 4. Pipeline changes (all gated, physics and maths output byte-identical)
| # | Change | Why | Safety proof |
| --- | --- | --- | --- |
| P1 | `subjects.py`: `'0620': {'subject': 'Chemistry', 'slug': '0620-chemistry', 'mcq_papers': (1, 2), 'maths_text': False, 'chem': True}` + helpers `is_maths(syl)`, `syl_of_path(name)` | one entry per subject | new key only |
| P2 | **Gate refactor**: today 12 places decide 'maths' as 'not 0625' (`layout._maths_page`, `ms._maths`, `store_text.maths_doc`, `checks.py:182`, `ms_layout` EQUAL_FLEX, `review_round:46`, `render.py:91`, `store_units:157/356`, `ms_align`, `ms_sweep`, `extract.paper_meta`). Chemistry would silently take the MATHS path. All become `subjects.is_maths(...)` (maths_text flag). | 0620 must run the physics path | only 0625 and 0607 exist today, so for them every test gives the same answer: golden 0 changed cuts + `ms_rebuild.py` over ALL maths sessions = 0 changed questions |
| P3 | `extract.paper_meta`: chemistry uses `paper_type_from_cover` (physics) | same paper numbering | gated 0620 |
| P4 | `extract.is_data_page` (periodic table) skipped like a blank page, kept as `paper.data_sheet` | D3 | gated `subjects.subject(syl).get('chem')` |
| P5 | uncaptioned structure / dot-and-cross clusters -> figures (questions, MCQ options) | section 3.2 | gated chem; fig_blast-style old vs new on the pilot only |
| P6 | `old_papers.py <syl>`; `session_papers.py` one-digit names for 0620 | section 3.5 | tool, no 0625 file written |
| P7 | tools with '0607' written in: `reasons.py` (SYL), `ms_rebuild.py` (raw/0607), `fig_blast.py`, `claude_check.py` -> `SYL` env / argument, default unchanged | two-pass flow for 0620 | default = 0607, maths runs unchanged |
| P8 | Store tree `bank|store/cambridge-igcse/0620-chemistry/`, ids `0620_2024MJ_41`, selectors `0620/2024-MJ/41` | as maths | new folders only |
| P9 | (only if D1 = LaTeX) `chem_tex.py`: runs -> `\ce{...}`; review page loads KaTeX mhchem | D1 | gated chem |
Freeze check before EVERY push: `golden.py check` = 0 changed cuts; `git status` nothing under 0625-physics or
0607-international-mathematics; for a shared-code change `ms_rebuild.py` over all maths sessions (PDFs fetched, no --write) =
0 changed questions. A shared change that moves maths or physics is gated to 0620 instead.

## 5. Pilot C0 (4 sessions, one per layout family; 56 papers, two-pass flow, ONE review round)
| Session | Why |
| --- | --- |
| 2005-MJ | one paper per component, nameless 2005 fonts, drawn arrows, old text MS (5 papers) |
| 2015-MJ | variant era, MS with Guidance (A / I / R) and page header box, practical insert in_52 (15 papers) |
| 2024-MJ | new syllabus, 3-column MS, displayed formulae in MS cells, ATP thermometer tables (18 papers) |
| 2026-MJ | newest: 4-column MS with Guidance, long MS (18 papers) |
Pilot output: every C0 paper through pass 1 / pass 2, one review round (decisions + undecided + ~5 calibration),
chemistry rules written to ERROR_PATTERNS / MS_TABLE_RULES, measured times -> confirm 3 years per batch.

## 6. Batches after the pilot (3 years each, newest first, each in a NEW chat; pilot sessions not repeated)
| Batch | Sessions | Papers |
| --- | --- | --- |
| C1 | 2024-FM 2024-ON 2025-FM 2025-MJ 2025-ON 2026-FM | 70 |
| C2 | 2021-FM .. 2023-ON (9 sessions) | 125 |
| C3 | 2018-FM .. 2020-ON (9 sessions) | 125 |
| C4 | 2015-FM 2015-ON 2016 (FM MJ ON) 2017 (FM MJ ON) | 104 |
| C5 | 2012-MJ .. 2014-ON | 90 |
| C6 | 2009-MJ .. 2011-ON (old_papers.py first for 2009) | 70 |
| C7 | 2005-ON 2006 2007 2008 | 34 |
| C8 | 2002-ON 2003 2004 (combined MS files split first) | 25 |
C2 / C3 are as big as maths M2 (117): split into a / b. C2a = 2022-ON 2023-FM 2023-MJ 2023-ON (59; 2023-ON paper 51 not in
Releases), C2b = 2021-FM 2021-MJ 2021-ON 2022-FM 2022-MJ (66).

## 7. Decisions for Dhruv (asked 2026-11-25; answers recorded in section 8)
- D1 formulae on the website: runs with sub/superscript as physics (recommended) / LaTeX mhchem.
- D2 MS columns: follow the print as physics (3 columns; Guidance as a 4th where printed: 2013-2015, 2026) / always 3.
- D3 periodic table: once per paper as a data sheet / leave it out.
- D4 pilot sessions: 2005-MJ 2015-MJ 2024-MJ 2026-MJ / other.

## 8. Decisions (Dhruv, 2026-11-25)
| # | Decision |
| --- | --- |
| D1 | Physics stores editable text as plain Unicode (cm³, not LaTeX). Chemistry the same by default (H₂SO₄, Cu²⁺, →, ⇌); Dhruv: 'we might have to use LaTeX/KaTeX in chem in some cases' -> LaTeX mhchem (`\ce{}`) ONLY for a part Unicode cannot show (stacked isotope numbers, conditions over an arrow, fractions, expressions); a check flags those parts (like the maths 'picture only when needed' rule). |
| D2 | Mark-scheme columns follow the print, as physics: 3 columns; Guidance 4th column where printed (2013-2015, 2026). |
| D3 | Periodic table: stored ONCE per paper (`paper.data_sheet`), never in a question. Later the practice-sheet tool gets an 'add periodic table' toggle that attaches it at the end (future, not now). |
| D4 | Pilot C0 = 2005-MJ, 2015-MJ, 2024-MJ, 2026-MJ. |

## 9. Pilot C0 status (2026-11-25)
Built (GitHub pass 1 + pass 2, last fixes rebuilt locally), 56/56 exact totals, round 41 published (7 items). New rules found
in the pilot (ERROR_PATTERNS 277-289): gate refactor, old one-digit files, data sheets, 2015 paper types + ATP total,
Guidance frame for empty cells, MS table under notes / page without header, label slips (orphan, marking points (i)-(iv)),
displayed formulae (end atoms in crops; one vector picture per structure in MS cells; never shrunk). Measured: ~90 min of Claude
time for 56 papers (pilot rate); a 3-year batch (~125 papers) should fit one chat now that the classes exist.
Still to build for later batches: ms_1-2-3-5-6 split (C8), qp_3 holding 31+32 (check C7), equilibrium arrow '⇌' as printed
(seen as text in 2015 MS, fine so far), LaTeX (D1) only when a part needs it - no part needed it in C0.

## 10. Round 41 (2026-11-26)
Paper numbering confirmed online: up to 2015 Paper 1 MCQ, 2 Core Theory, 3 Extended Theory, 5 Practical, 6 ATP; from 2016
Paper 1 MCQ Core, 2 MCQ Extended, 3 Theory Core, 4 Theory Extended, 5 Practical, 6 ATP. Dhruv's round-41 rules: drawings
in table cells are pictures inside their cells, table text stays text; drawn formulae are pictures, all other words text;
one standard MS column proportion (MS_TABLE_RULES 'Chemistry'); faint MS pictures redrawn properly.

## 11. C1 (2026-11-27)
Built (pass 1 + pass 2, 70 papers), 83 reasons (pilot classes hold), patterns 313-319, round 45 (10 items). Pass 1 now also gives
the Marks-column sum hint (ms_marksum). Tools: fig_blast takes SYL (MCQ figures not covered - harness on bank/ jsons).

## 12. C2a (2026-11-28)
58 papers (2023-ON 51 not in Releases). Pass 1 (8 min) + pass 2 + a local rebuild; patterns 342-346, 348; round 47 (10 items).
Lessons for every chemistry batch: zoom formulae (Cl in Bookman italic, sub/superscripts) at 2x on every sheet; editable text
for 'Cl ' / BEL; diff store/ after any local rebuild. Approved C0/C1 must be rebuilt before the MongoDB push (345, 346, 348).

