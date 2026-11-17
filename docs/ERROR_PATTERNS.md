# Error patterns (do not repeat these)
Every mistake Dhruv found, or Claude found itself, as a pattern + the check that now catches it. Read before every batch.
Add a line whenever a review round or a check finds something new. Format: what went wrong -> fix -> how it is checked now.

## Build / GitHub
1. GitHub `bank.yml` checks step passed ids without `0625/` -> checked nothing. -> Always run `checks.py 0625/<ses>/<p>`
   locally after a GitHub build.
2. Old PDFs exist under two names (qp_3 and qp_03) -> every paper built twice. -> `session_papers.py` keeps the 2-digit one.
3. The golden check compares what is on disk: without the golden PDFs fetched, `run.py` silently does nothing.
   -> `raw_store.py fetch <golden ids>` first, then rebuild them, then `golden.py check` (0 changed cuts).

## Question papers (pre-2009)
4. Paper numbers mean other things before 2009 (1 MCQ, 2 core, 3 extended, 5 practical, 6 ATP): read as MCQ.
   -> `extract.OLD_PAPER_TYPES`. Check: every paper's marks = its total.
5. No total printed on old covers -> take 'MAXIMUM MARK' from the mark scheme (pre-2009 only, to leave approved years alone).
6. 2002 ON practical: answer booklet pages inside the PDF; 'Question 1' headings. -> dropped / read.
7. 'For Examiner's Use' column drawn as a thin line in the page picture (no vector) -> slivers in every piece.
   -> `clean.strip_examiner_rule_drawn`.
8. Invisible text (OCR layer) read as a figure caption -> bogus figure. -> captions need ink under them.
9. CMYK pictures show black in browsers -> `render.fix_cmyk_images`.
10. Figure crop stopped at a text line printed BESIDE the figure -> cut-off figure. -> band top ignores beside-text.

## Mark schemes (round 22: 20 of 33 items wrong, all mark-scheme layout)
11. Part totals shown twice (sub-totals + our Total row). -> rule 16; sweep: no bare number / [n] / M2 in Marks of a
    question with codes.
12. Mark codes left in the Answer column (fixed 0.82 threshold). -> codes column found per question. Sweep: no code
    token left of the Marks column.
13. 'TOTAL n' / '1.' left in practical answers. -> dropped.
14. F/C removal by redaction moved the next word ('8 F B1' -> 'B1' beside 8). -> never use apply_redactions on text;
    paint + hide list. Check: after any cleaning of text, compare word positions before/after.
15. My contact sheets drew the raw pieces, not our table (`ms_p`) -> I checked the wrong picture. -> check mark
    schemes with `store.review_svgs` (what the review page and students get), e.g. pipeline/ms_grid.py.
16. A new layout era (old MS) went to review before being put in our table -> Dhruv reviewed known problems.
    -> before a round: the MS sweep (PLAYBOOK step 5) must be clean, and look at one MS of each paper type.

## Batch 2 (2005-2007), found by Claude before the round
17. Practical marks only in the mark scheme as '[1]' per point + '[Total: 10]' -> marks 0. -> per-question
    '[Total: n]' (run.py ms_qtotals), else the summed '[1]'s.
18. A scale line ('-10 0 10 ... 110 C') or padded labels ('C       D') counted as the sentence above a figure ->
    crop cut at the top. -> not prose (extract.find_figures); pre-2009 figures may reach into the prose line's descent.
19. F/C column at x 482 (2006) outside the 380-480 window -> F/C shown. -> window 380-500; sweep shows no lone F/C.
20. Repeated column heads at a page top ('QU. SCHEME MARK') inside a row; '[TOTAL: 10]' in caps -> dropped (pre09).
21. Letters printed in the roman column (2005 ON 03 q11 at x 133) -> the question had no mark-scheme rows.
    -> pre-2009 letters a-h accepted up to the roman column. Sweep: 'no table' hit = look.
22. Run labels '(a)–(e)' (practical) -> one row labelled 1(a)–(e).
Known small leftover: in-text codes at the far right of an answer line ('120 gets C1 C1 A0') can land in Marks.

## Round 23 (2005-2007): 11 of 36 wrong
23. Old column rules (straight thin vertical lines) taken as braces -> '{' at the start of answers. -> pre-2009 braces
    must be curves; straight vertical rules dropped.
24. '[total: 9]' in lower case left in the answer. -> any case.
25. 'B1 x 4' printed as three words -> '4' dropped as a part total, 'x' left in the answer. -> merged to 'B1×4' first.
26. '(ii)' printed twice in the MS -> second became (b)(ii). -> pre-2009: the next roman of the same letter.
27. Parts Cambridge did not label ('sound ticked' = 7(b)) or printed together ('(b) & (c)'): by eye -> ms.MS_SPLIT.
    MS letters for paper romans (2006 ON 06 q4 (b)(c)(d) = (b)(i)(ii)(iii)) -> ms.MS_RELABEL.
28. A label alone on its line ('(a)–(g)') left an empty band at the top of the row. -> answer starts at the top.
29. Captions 'Fig. 2.1a' / 'Fig. 2.1b' not read as captions -> figure missing. Ids now fig2-1a / fig2-1b.
30. Paper prints one [Total] for two questions (2007 MJ 03 q10+q11) -> extract.TOTAL_SLIPS (no flag).

## Batch 3 (2008-2010), found by Claude before the round
31. 2008-2009 downloads hold 0625/31 + /32 in one qp_3.pdf (also split into qp_31, qp_32) -> built 3 times.
    -> session_papers skips the combined original.
32. 2008 notes page names 'Question/Answer/Mark' -> the table parser was chosen and found nothing (no MS for paper 2).
    -> fall back to the column parser when the table parser finds no rows.
33. A tall figure beside a column of text (2008 MJ 02 Fig 4.1) was cut: crops may grow only 80 pt. -> pre-2009, all
    prose beside the figure: grow up to 400 pt.
34. Table 15 pt below its caption (2010 MJ 52) was not seen as a table -> tiny crop. -> window 18 pt.
35. A sentence ending with its mark '[2]' inside a graph's band was cut into the figure (2010 ON 32). -> prose.
36. Old printed MS layouts run to 2012, not 2008: rule 16 now for all years < 2013; codes printed '[B1]' (2008).
37. Stub questions (same as another variant) have no own table: the sweep skips them.
Known: 2010 MJ 13, 23, 53 have no mark scheme file at all. MCQ labels cut at the right in 2010 ON 11 q34 /
12 q31 / 13 q35 (same figure) and 2008 MJ 02 Fig 4.1 spotlight: in round 24.

## Round 24 (2008-2010): 25 of 50 wrong - most: MS rows not matching the paper's parts
38. Old mark schemes label rows their own way (whole question '1', '(a)–(e)', '1(b)' for (b)(i)-(iv), slips like
    5(c) for 5(b)(ii)) or put several parts in one row. -> rows assigned BY MEANING: read each paper part and each
    MS line and map them in pipeline/ms_map.json ([MS line start, label], optional split inside a line).
    Check before every round: `python3 pipeline/ms_align.py list <sessions>` must print nothing
    (it flags labels not in the paper, marked parts without a row, and rows on a parent part).
    A row labelled with the bare question number is a note for all parts (kept).
39. Codes and labels drawn stretched (a width stored for '[B1]', or a guessed width for 'f', 't', 'r'): the SVG
    draws text at its stored width -> 'different font'. -> real widths (codes 6.73/char, Arial widths for labels,
    pre-2013 only; 2013-2016 labels still use the old guess until their layout is rebuilt).
40. 'B1 + B1' on one line widened the Marks column -> codes stacked one under the other.
41. A question number in the corner of a tall figure crop -> crop starts below it.

42. Old practical schemes print parts out of order ('(c) units' or 'Table' first, '(e)' before '(b)–(d)') and we kept
    the printed order. -> rows sorted into the question paper's part order (pre-2013; a note row keeps its place).
43. A map that gives the same label to rows that are not next to each other ('evidence' after (d)) or labels like
    '4(c)(d)' / '4(c)–(e)' for a step with no marks -> label each line with the part where its marks are earned
    (the table/answer part, not the instruction step); general table lines go with the last part they cover.
44. Short bars ('±' printed as '+' over a bar, underlines) went into the row below (y split 12 pt above the next
    line) -> a short bar goes with the line it sits under.
45. Old schemes double-space some lines: a gap inside a row -> gaps over 15.5 pt closed when nothing is drawn there.
46. Notes printed far right ('(ecf NO)', '(too different, wtte)') wrapped onto their own line -> moved beside the
    line (gap 8 pt), with their underline. '[M2]' beside a brace -> '(max 2)' at the end of its line.
47. Stacked codes ('B1, B1') pushed the next line down -> they hang into the lines below when those have no marks.
48. 2008 '[1]' marks in the same column as '[M1]' codes were dropped as part totals -> kept (right edge = codes').
49. One line with one mark for two parts, split ('e1 ... and e2 ...'): the mark goes where Dhruv expects it
    (map option 'marks_first'); a mark that covers two parts and cannot be split keeps the combined label.

## Batch 4 (2011-2012), found by Claude before round 26
50. A fraction printed inside a line ('R = V/I', '1/u') draws its numerator and bar ABOVE the line's text
    top. The cut between two parts ran under them, so that ink was in no piece at all (coverage, blocking:
    2011 MJ 51 p8, 2012 ON 63 p13). -> `extract.lift_over_thin_ink`: the cut moves up to the first white
    row, so a line keeps the ink hanging over it (pre-2013). Also '(d) (i)' on one line: the two cuts are
    now always merged to the higher one, instead of leaving a 3 pt sliver that is dropped with its ink.
51. 2011 MJ 52 and 61 print the question number as '1.' (with a dot). The old-layout parser only accepted
    a bare number, so it found no rows and those two papers had NO mark scheme at all - and nothing failed,
    because marks come from the question paper. -> `ms.py` accepts '1.'. Check: a paper with no `ms_p` in
    any question is a bug, not a scan (`ms_sweep` 'no table').
52. ms_map prefixes are matched against the text OUR table shows, not against the printed line: marks read
    '[1]' not '1', mark codes (B1, M1) have moved to the Marks column, the rest of a printed label
    ('& (ii)', ', (b)') is stripped, and a line of only sub/superscripts ('3', '240 240') is dropped.
    -> `ms_layout._mnorm` ignores those differences; never take a prefix from a sub/superscript-only line,
    and never cut a prefix in the middle of a word or code. Check: `ms_align.py verify` - every mapped
    question's row labels must equal the labels in its map entry (ms_align list alone does not catch a
    prefix that matched the wrong line).
53. Mapped rows were sorted by the letter only, so a mark scheme printing '(ii)' before '(i)' kept the wrong
    order inside a part. -> `ms_layout` sorts by every part of the paper, sub-parts included (round 26).
    This also corrected two approved papers (2005 MJ 05 q4, 2005 ON 05 q3).
54. Rebuilding single papers with `store.build` and no `store.py dupes <session>` afterwards empties every
    `same_as` list (614 files changed in approved years). -> always run `dupes` for each session touched.

## Round 26 (2011-2012 + round-25 re-checks), Dhruv 2026-11-12: 37 ok, 13 wrong
55. Splitting a printed group by meaning when the lines do not each mark one part (trace marks, table marks over
    readings and repeats, 'Both sets of temperatures') = guessing; Dhruv: keep Cambridge's grouping, our layout
    (MS_TABLE_RULES 20). Sign: you need a label across letters ('2(b)(c)', '4(e)(h)') -> keep the group.
    (2011 ON 51 q4, 2012 ON 51 q2, 2011 MJ 52 q1, 2009 ON 05 q2, 2011 ON 52 q4, 2005 MJ 05 q4)
56. A figure crop warning was dismissed after looking at the stored figure alone: it showed a whole-looking
    picture (a woman, a basket, a cliff) but the man at the top of the cliff was gone (2012 MJ 22/23 q4). Cause:
    the questions printed BESIDE the figure counted as prose above it, so the crop started under them. The
    pre-2009 rule for text beside a figure now holds to 2012; a label whose line was read together with that text
    ('basket of') is taken whole. ALWAYS compare a flagged crop with the page.
57. An underline under several words ('neatly and correctly') went to the next row when a row started on the
    line below: it is now owned by the words it is under (2011 MJ 62 q4(b)(v) 'line').
58. A fraction's numerators ('1  1' of 1/u, 1/v) and a superscript ('3' of cm3) are a text line of their own just
    above their line; when a mapped row started at that line they stayed in the row above (2012 ON 63 q4: '1 1'
    left in (a)(iii), the fractions in (b) without numerators). They now join the line below them (pre-2013).
59. A stray '_' printed at the end of a mark scheme became a row line (2012 ON 21 q12(c)(ii)) -> dropped.
60. '≥' printed with a re-encoded '[' in a symbol subset (2011 ON 51 'distance [ 5.0cm'): the glyph check now
    covers brackets too (pre-2013).
61. 'all 3  B1' + brace: one mark for three parts - shown as one merged Marks cell (MS_TABLE_RULES 21).
62. The paper's '[3]' after (a)(iv) is the block total of (a): stored on (a) now (MS_TABLE_RULES 23).
63. Map prefixes and printed order: entries of an '@original' map are still matched in printed order; a heading
    line ('trace:', 'Table:') starts the row of the first marked line under it, so its entry is the heading.

## Maths 0607 pilot M0 (2014 MJ, 2019 ON, 2021 FM, 2025 MJ), found by Claude in pass 1
64. Equation-editor fonts re-encode symbols: MathType 'MM*' fonts (2014-2024) and 2025 'AllAndNone' print × as '#',
    ÷ as "'", ≠ as '!', ≤/≥ as 'G'/'H', π as 'r', ∪/∩ as ','/'+'. The store drew '#' in the PRINT layout too (2025 MJ 21 q5).
    -> `store_text.MATHS_GLYPHS` (read by eye from a glyph sheet of every code) and `MATHS_WIDE` (2025: the same code is a
    digit or a symbol, told apart by its width: '2' 0.83 em = '>'), maths only. Shape matching (glyph_remap) was tried and
    is NOT reliable for these (≠ read as √). Check: maths_tex character check + store verify. New font in a later batch:
    make the glyph sheet again (/tmp script in CONVERSATION_LOG M0 entry) and add the codes.
65. Page 2 'Formula List' / 'List of formulas' is no question (coverage error on every paper); 'Answer all the questions.'
    / 'Calculators must not be used in this paper.' on the first question page was ink outside every piece.
    -> `extract.is_formula_page` (skipped like a blank page, kept as paper.formula_list), `layout.page_bounds` (maths only).
66. Investigation / modelling papers (5, 6): the introduction before Q1 and the 'B MODELLING' / 'Section B' text before the
    first question of part B belong to no question (it was lost, or glued to the last part of part A).
    -> `extract.maths_paper_parts`: paper.json `intros` (section, before, segments); store paper.json has their layout +
    LaTeX; every question of a section has `intro` = its index. Coverage counts them.
67. 2014-2024 investigation papers print no [n] per part: marks found 0. -> marks from the mark scheme (`run.py`, maths
    investigation only). Their 'Communication: seen in ...' rows are paper marks: the rows printed under them name earlier
    parts (criteria) and were taken as extra rows of those parts (2019 ON 51: 3(c) got 2+1). -> `ms.fold_communication`
    (paper.json `communication`); numbers in the 'Partial Marks' column (fractions, tables) are not marks
    (`structured_rows_table` PX). Checks: marks + communication = cover total.
68. Maths diagrams have no 'Fig.' caption (a triangle 'NOT TO SCALE', axes, grids), so no figure was cut and the
    website text would read the diagram's labels as text. -> `extract.diagrams` (maths only): clusters of drawings/images
    with their short labels, ruled tables of text excluded (they stay text + rules), grown to all ink (light grey grids
    too: `_grow_light`). Ids `..._diagram<n>`. Check: checks.py crop warnings - compare each with the page (pattern 56).
69. Mark schemes 2018+ have a 4th column 'Partial Marks' (M1 for ..., B1 for ...): the header was not recognised and rows
    with a drawn symbol had no 4-column frame to fall back to (2025 MJ 21 q3: partial marks inside the Answer cell).
    -> header name 'Partial Marks', Answer and Partial Marks the same width (Dhruv, MS_TABLE_RULES 24), 4-column default
    from the printed rules when no row can be re-wrapped.
70. 2014 maths mark schemes are portrait tables ruled into 4 columns with no header row; labels '2', '(a)', '(i)' sit
    apart and only on a question's first row. -> `ms_layout._maths_ruled`: our full label per row, our header, re-laid out
    like the landscape era (FORCE_WRAP). NOT finished in M0: rows with fractions / column vectors / long notes (2014 MJ 41
    q10, 21 q2) still break; see PROGRESS.
71. Maths mark-scheme rows full of fractions / brackets / graphs broke in the physics re-wrap (fallbacks, old paths).
    -> `pipeline/ms_maths.py`: per printed cell, lines by vertical overlap, unbreakable chunks, rows grow (Dhruv).
72. 2019 ON 11-13 schemes: header words not found -> default column limits read answers as labels; numbers of answer
    tables counted as marks. -> maths: the table's own column rules decide Q / Marks / Partial Marks columns (ms.py).
73. 2014 paper 6: part B numbers its questions from 1 again (paper and mark scheme) -> part B was glued to the last
    question of part A. -> they continue our numbering (extract.boundaries, ms 'B' token).
74. Diagram crops: tick labels beside an axis, sideways axis titles and long labels of tree diagrams were cut off; bar
    charts were taken for tables of text. -> labels taken again after growing; tables need column rules top to bottom.

## Round 27 (maths M0), Dhruv 2026-11-13: 17 ok, 23 wrong - most were simple and should have been caught by Claude
75. Process: pass 2 looked at a sample of mark-scheme tables and never ran `store.py verify` or a MS content check.
    -> PLAYBOOK 2a-2f / 3a: automatic checks against the PDF on every paper + full contact sheets before any round.
76. Dot answer lines ('.......') missing in the rebuilt question (2014 MJ 11 q11, 21 q5, 33 q3, 42 q6): 2014 dots
    are hidden ('hide') like physics working space -> the print view must keep answer lines. Check 2a.
77. Mark-scheme fractions / vectors broken in ms_maths rows: stacked pieces split into different lines or chunks
    (2014 MJ 21 q5, 22 q4, 31 q3 '1/8' '7/25', 33 q3, 62 q2; 2019 ON 43 q6 vector arrows over OA/AB). Small (raised)
    pieces must join the chunk under/over them; drawn arrows join the letters under them.
78. Mark-scheme pictures (Venn diagrams, sketches) broken in ms_maths: a shaded region drawn as a black triangle,
    a picture scaled into a strip (2019 ON 42 q8, 2021 FM 32 q9, 2019 ON 52 q3). Pictures/drawings of a cell move as ONE
    block with their clip; never split by line bands.
79. Stray short lines in Marks / Partial Marks cells (2014 MJ 11 q11(b)(ii), q12(c)): pieces of printed row rules.
80. Fonts not consistent in our MS (serif answers, sans header and bold sans marks, small 2014 text). Dhruv: ONE font
    for question and mark scheme, same size, bold/italic only where printed (MS_TABLE_RULES 25).
81. Diagram labels left outside the picture (2014 MJ 11/13 q12) and two overlapping crops of one diagram (2021 FM 62 q9,
    2025 MJ 43 q16, 53 q3, 62 q6 '2 images', 'image 2 has a line'): crops must be merged / not cut through text.
82. 'NOT TO SCALE' (2025 MJ 23 q17, 43 q6): Dhruv's rule: it is part of the diagram -> always inside the picture.
83. A MS row missing: 2021 FM 42 q4(b)(iii) has a row in the printed scheme -> parse check per part (2b).
84. Digits of a number printed with thin spaces ('0.003 094 8') drawn with a gap too wide (2025 MJ 21 q2, q3).
85. Question tables (2019 ON 61 q3(b)) and 2019 ON 52 q3 render problems in the rebuilt question -> 2a.
Fixes made in the same chat (2026-11-13, before the re-check round):
- 76: 2014 dotted answer lines are rows of tiny pictures -> drawn as dots (store, maths); 2014 nameless 'TT..o00' fonts
  are Times -> serif by the font's serif flag (the rebuilt 2014 questions were in a sans font).
- 77: ms_maths bands: a drawing-only band (fraction bar, vector arrow) and a band of small raised text join their
  neighbours; MT Extra arrows ('JJG') are drawn glyphs; mark scheme scaled so its normal text is 11 pt.
- 78: ms_maths picture cells: curves/sketches/shaded areas (> 30 pt) and pages with a broken text layer are kept as the
  printed picture of the cell (axis labels with it); ruled inner tables stay text.
- 79: row-edge rule pieces and long lines in Marks / Partial Marks with nothing written over them dropped.
- 80: one font: the question paper's family for the whole table (header, labels, marks, Total), 11 pt.
- 81/82: diagram crops: 'NOT TO SCALE' always taken (up to 200 pt away), sentences on a crop's edge cut off, a line of a
  part label is question text, crops touching across a part boundary merged, light grids (< 253) grown.
- 83: '4(b)(iii)(a)' (a 4th level) read as a row of 4(b)(iii) with its full label (ms.SUB4, maths).
- 84: digits grouped by thin spaces -> '\,' in LaTeX.
- New tool `pipeline/maths_check.py` (ms_words, ms_overflow, ms_overlap, ms_font, fig_overlap, not_to_scale) - PLAYBOOK 2b-2d.
Known open: 2025 MJ 53 q3 (the part boundary cuts through the pyramid diagram); 2014 MJ 43 q3(b) inequality signs of
the 2014 symbol font not read in the mark scheme; 2014 MJ 62 p4 kept as pictures (broken text layer); 6 questions still on
the old MS paths (2014 MJ 22 q2, 43 q9, 2019 ON 11/12 q8, 23 q3, 62 q5).
86. 2014 maths fonts are nameless subsets ('TT1F0CAo00'): bold labels, marks and codes (M1, B1, FT) were drawn regular
    (store verify: 2-8 % ink missing in 2014 MS rows). -> `store_text.nameless_bold`: a font is bold when its printed
    letter widths match Times Bold better than Times Roman (cached per document). Found by PLAYBOOK 2a (store verify),
    not by Dhruv: the strict checks work.
87. Equation editors put the operators of one formula ('−', '×') in ONE text run, far apart: the run was drawn as a
    stretched word over the digits (maths_check ms_overlap '−×' / '2'). -> maths: a run is split at a gap > 1.5 pt.
88. A long mark-scheme answer printed over several lines (the printed Answer column is wider than ours) was wrapped
    line by line: ragged lines ('previous / numerator.'). -> `ms_maths._cell` joins text-only lines with the same indent,
    a normal gap and a full previous line into one paragraph and re-flows it in our column (MS_TABLE_RULES 26).
89. Nested / continued fractions (n/(1 + n/(1 + n))) were turned into flat LaTeX that passed KaTeX AND the character
    check: both checks test form, not meaning. -> `maths_tex`: a shorter fraction bar inside an outer one with text over
    both = 'nested fraction' -> the part is shown as the printed picture. Found only because Dhruv asked how the sequence
    was treated: PLAYBOOK 2c now asks to compare the LaTeX of every part with a stacked layout against the page.
90. Ruled tables inside question text were read as one jumbled LaTeX line. -> `maths_tex`: >= 3 column rules and >= 3 row
    rules in a unit = 'table' -> printed picture (105 parts in M0). Printed layout (store units) was never affected.

### Round 28 (25 of 34 wrong) - why the strict checks missed them: they tested CONTENT (every word present, nothing
### overlapping), never APPEARANCE (font, width, spacing, cut pictures). maths_check.py now has appearance checks.
91. Q labels, header and Total of the maths MS were given GUESSED widths (0.5-0.55 x size x letters) and the renderer
    stretches text to its width: '5(a)' 22.6 pt for 17.7 pt -> a 'wider font'. -> `ms_maths.text_width` (real Times /
    Helvetica metrics) for every word we make; labels normal weight, header and Total bold (Dhruv). Check: ms_stretch.
92. Rows were cut at the top of their first text line and no space was added above tall maths: fractions touched the
    row's top rule or the line above. -> `ms_maths._pushes`: 4 pt above a row's highest ink, 3 pt above and below a line
    with stacked maths, applied across all columns at that height (labels and marks stay level with the fraction's
    middle, as printed). Check: ms_edge (ink closer than 2 pt to a row rule).
93. A MS row ended 6 pt under its last text line or image: vector drawings (Venn diagram, sketch) were not counted, the
    bottom of the drawing was cut (2019 ON 42 q8). -> ms.py (maths): drawings in the row (not table rules / shading) count.
94. 'Graph = 15 straight lines' (round 27) also counted root signs and brackets: a long answer full of square roots
    became a half picture with loose words in the Marks column (2025 MJ 61 q4). -> a grid needs >= 3 long vertical and
    >= 3 long horizontal rules; text on the same line as a drawing goes into the picture with it.
95. A printed picture lying over its own heading ('Correct diagram', 2021 FM 32 q9) was copied with the half-hidden text
    and a light grey band. -> the picture starts under the heading (heading = our text); near-white (> 232) = paper.
96. Straight lines have EMPTY boxes in PyMuPDF and `Rect |= empty` does nothing: grids and axes never widened a diagram
    crop (2014 MJ 11 q12: dots without their grid and 'Diagram 1-4'). -> line boxes get 0.3 pt each side. Check: fig_cut.
97. A diagram crop took the part's question line ('(ii) Sketch the model ...', '(b) Shade P∩Q′', 'So N(6, 4) = ...'):
    pieces of the line were each < 22 characters. -> whole printed lines are judged; a line starting with a part label,
    or a line above / below the drawing and off to its side, is question text. Check: fig_text.
98. A box of words (arc / circumference / ... 2014 MJ 11 q4) was cut as a picture. -> a cluster made only of the box's
    edges with words inside stays text + rules.
99. 2025 'AllAndNone' (one font holding regular, bold and italic Times) was read as SANS, and the one-font rule then put
    the whole 2025 mark scheme in sans too; bold labels '(a)' came out regular (glyph_styles was tuned on physics sans).
    -> maths: AllAndNone = serif; `store_text.maths_styles` reads bold / italic from Times letter widths + slant.
    Check: q_font (any sans word in a maths question).
100. 2014 nameless fonts: italic x, y, their drawn upright. -> `store_text.nameless_style` (regular / bold / italic /
    bold italic by letter widths against the four Times fonts).
101. Recurring-decimal dots are letters of equation fonts (MMEtc 'o', MT Extra code 5 and 'i'): written as the letter
    'o' squeezed to 1.8 pt they drew a blob over the digit (2019 ON 61 q3). -> kept as drawn glyphs (exact shape and
    place); EuclidMathTwo '-' = '≤'. Symbol sweep of all M0 equation fonts: no other unmapped letter left.
102. Graphs in MS cells drawn from many short straight pieces with dashed grids were not seen as drawings (no curve
    over 30 pt, no long grid lines): laid out as faint loose lines, axis numbers lost (2014 MJ 42 q2, 2019 ON 41 q11).
    -> `_picture_cell`: axes (a long vertical line crossing a long horizontal one) = a graph = picture.
103. A MS row starts 4 pt above its label, but maths prints things higher: a numerator ('144' over '233', 2014 MJ 52
    q1(b)(ii)), a rotated table label ('All pos', 2021 FM 52 q3), a table's top band (2014 MJ 62 q1) went into the row
    above. -> ms.py `_lift` (maths, both row finders): while a word or drawing crosses a row's top cut, the cut moves
    up above it (not above the previous label's line).
104. The round-27 re-flow joined separate answer lines ('... -1.241' + '[x =] 1.13 ...', 2019 ON 42 q12). -> only a line
    that goes on with a sentence (starts with a lower-case word, not 'or' / 'and') is joined.
105. The 'heading under a pasted picture' rule (pattern 95) cut the top edge of a DRAWN Venn box (2021 FM 42 q9). -> only
    for pasted pictures (images); and the whole heading line is our text (only its first word was kept).
106. Cell shading printed as many thin grey strips counted piece by piece (< 400 pt2 each): the table was laid out as
    items and the strips landed in the wrong cells (2019 ON 51 q1(b)(ii)). -> shading area is added up.
107. A long answer that wraps in our narrower column moved only its own column: the Marks / Partial Marks lines stayed
    beside the wrong answer line (2025 MJ 61 q4). -> two passes: each column's growth by printed height, then every
    column is laid out with the largest growth at each height.
108. 2014 nameless SYMBOL subsets re-use letter codes: '<' printed as <=, '.' as >, 'Y' as <=, 'I' as >= (2014 MJ 43 q6,
    q3(b)). Glyph names lie (the <= glyph is named 'less'). -> `store_text.symbol_subset`: a nameless font with a
    character far off every Times width (a '.' as wide as a '>') is a symbol font; its one-letter spans are kept drawn.
109. fit_crop (store) took a part's question line into a diagram crop again: maths part lines are indented under their
    label, so they never counted as sentences ('(ii) Sketch ...', 2021 FM 62 q9). -> fit_crop(maths=True): a line
    starting with a part label, or a full sentence, or a line above/below the drawing and off to its side, stays out.
110. A diagram crop grew down through a ruled table under it (2019 ON 62 q3). -> crops stop at tables / boxes of words.
111. A rounded box of text (curved corners, 2021 FM 62 q6) was cut as a picture. -> straight sides + small corner arcs
    = a box (pattern 98).
112. The next section's title ('MODELLING ...' 2021, 'Modelling: ...' 2025) went into the last MS row. -> it ends the
    table like a 'Question' header.
113. A printed line hanging right ('+ 8[corners]') kept its indent and crossed our column rule; two printed lines joined
    by a tall root sign were wrapped piece by piece and drawn on top of each other (2025 MJ 21 q15). -> the line moves
    left to end at our edge; joined lines are one block (scaled if wider than the column).
114. Long text lines just under a drawing went into its cell picture (2025 MJ 61 q1: a table and its notes shrank into
    one small picture). -> words longer than 6 letters join a picture only inside the drawing's own height.
115. Symbols (x, <=, ÷, °, π) were drawn in sans in maths papers. -> maths: Liberation Serif when it has the symbol.
116. Check false alarms fixed: ms_stretch only for words WE make (printed words keep printed widths); ms_piccut and
    fig_cut ignore a straight table rule beside the edge.
117. A ruled table 15 pt under a diagram joined the diagram's cluster (drawings within 20 pt), so the table test never saw
    it alone and the crop took the table (2019 ON 62 q3). -> ruled tables (>= 3 rules with the same ends, vertical rules,
    text in most rows - not a grid) are found BEFORE clustering and kept as text + rules.
118. An empty answer box beside a formula was cut as a diagram (2025 MJ 61 q5). -> an empty box < 40 pt tall is no diagram.
119. An equation line under a graph ('f(x) = (3x + 2)/...', 2019 ON 43 q12) was half inside the crop. -> a line with '='
    fully above / below the drawing is question text (extract and fit_crop).
120. Broken text layer (2014 MJ 62 p4): words outside the drawing's height were laid out as text OVER the cell picture,
    and the picture's top was clamped to the graph (the formula above it was lost). -> broken page: the whole cell is
    the picture, from its first ink.
121. Graphs traced in short pieces with no long axis line (2014 MJ 42 q2, 43 q6). -> 20+ pieces touching no text, or 5+
    slanted pieces longer than 8 pt, spread over 60 x 30 pt = a drawing (root-sign ticks are 2.7 x 5 pt, beside text).
122. A row lifted over the table header ended at the header (it counted as 'a new table below'): the first row of a page
    lost all its content (2025 MJ 61 q1(a)). -> a header above the row's label never ends the row; the first row's lift
    stops at the table top.
123. Main column rules drawn in 6 pt pieces: the lift climbed up them into the row above (2021 FM 52 q4(c)(ii) took
    4(c)(i)'s lines). -> verticals at an x where the page's verticals add up to > 30 % of the page height are main
    column rules and never lift a cut; an inner table's border does (2021 FM 52 q3(b): its top row came back).
124. Pasted pictures (images) were not seen by the lift. -> images count.
125. Notes under a table went into its picture because a root sign in them counted as part of the drawing. -> a cell
    picture takes the main clusters of drawings (>= 30 % of the largest); small marks standing apart stay text.
126. A rotated label ('All' left of 'pos', no text item) was cut at the picture's left edge. -> cell pictures grow
    sideways while ink is cut, inside the cell.
127. The header's grey shading pokes 2 pt into the first row of a page: its area made the cell a 'shaded' picture with
    the text drawn twice (2019 ON 63 q6(b)(i)). -> anything lying wholly in a row's top / bottom 3 pt is the neighbour's.
128. 2025 'AllAndNone' also re-uses letter codes for symbols ('+' printed as the cap sign, 'l' as a prime: 'P + Ql' for
    P∩Q′, 2025 MJ 43 q16). -> a glyph that is not its character's usual glyph AND matches no Times width (> 0.02 em off)
    is a symbol: kept drawn (digits and . , excluded).
129. A drawn glyph's cut (its character box) holds the ink under it too, and one cut was reused for every same glyph
    of the paper: a recurring dot cut over '0' drew '0' over '3' -> theta (2019 ON 61 q3 MS). -> maths: one cut per place.

### Round 29 (21 of 39 wrong; fractions now right)
130. 2014 prints a full-width rule between questions: kept at the end of every question. -> store (maths): a rule
    > 85 % of the width in the last 10 pt of a block is dropped.
131. A short underline in the Marks column (printed total line) drawn as a stray line. -> the Marks column holds no
    drawing (MS_TABLE_RULES 28).
132. The question number '12' went into a diagram crop through the sideways-label passes (they skip _label_like). ->
    a 1-2 digit line at the left margin (x < 62) is never a label (extract and fit_crop).
133. 2014 MJ 22 q2: grids drawn in the answer have tall lines too, the column finder found 5 'rules' and gave up -> old
    layout with stray '}' and no grids. -> when not 2-3, keep only the full-height rules.
134. Tables in MS cells were pictures (Dhruv: 'lines and box and text, as in physics'); laid out line by line they fell
    apart (shading strips, dotted rows). -> `_has_table` (>= 2 row rules running most of the width): every item inside
    the table's rules is one rigid block (`_emit_block`); boxes around numbers are no table.
135. A pasted graph covering its own heading ('Correct sketch' drawn twice, 2021 FM 62 q9(d)(ii)). -> a text line in the
    top 30 % of a pasted picture is the heading: our text, the picture starts under it.
136. A light grey band of a pasted screenshot and the cell's row rule were kept in the picture (2021 FM 32 q9). ->
    pasted pictures: lighter than 230 = paper; the picture region stops at the row / cell rule (never pixel-stripping:
    that took the Venn box too).
137. Review page: stored figures under the question were drawn at 96 dpi beside a 192 dpi question ('shrunk'). ->
    review_assets.fig_img at the question's scale.
138. (process) Two Claude passes doubled the time without catching appearance faults. -> ONE round: rules on all papers
    (claude_check.py checklist) + side by side only for doubtful items, each passed with a reason or fixed as a class.

### Round 30 - found in Claude's ONE check round (before Dhruv's round)
139. Pasted screenshots: the global 'lighter than 229 = paper' cut (136) erased graph grids and pale curves (2014 MJ 31
    q15, 33 q15). -> pasted pictures keep everything darker than 252; a light tone is paper only when it is a BAND
    (>= 10 rows/cols of one tone), a SMOOTH area (5x5 window spread <= 4) or the background tone that reaches the
    picture's edges (`ms_maths._erase_bands`). Shading inside a Venn box never reaches the edges (2025 MJ 11 q16).
140. Table lines in a cell: the rule 'thin vertical taller than half the row = a column rule' removed every vertical of a
    tall table row (2014 MJ 62 q3). -> >= 3 thin verticals with the same span inside the Answer column are the table's
    own (`grid_v`); rules are drawn over the shading.
141. A heading above a DRAWN graph ('Correct sketch') went half into the picture and half into our text -> drawn twice
    (2019 ON 41 q11, 43 q3, 43 q12, 2025 MJ 31 q18). -> a text line (> 8 chars) ending above the drawing's top, or our
    text over the top 30 % of it, is the heading: our text, the picture starts under it.
142. Column finder summed the lengths of a graph's grid line drawn 3 times over itself: it out-measured the table rules
    and the whole mark scheme fell back to the general layout (2014 MJ 43 q9) - no check looked, as every maths check
    needed the maths layout. -> covered height = UNION of the pieces; new check `ms_mode` (any fallback is a hit).
143. A tall nested root sign (sqrt of a fraction, 33 pt) counted as a 'sketch' -> Partial Marks cell became a cut
    picture (2025 MJ 21 q15). -> `_root_sign`: a bar along the top of the path is a root, never a sketch.
144. Rotated row labels ('1 neg') boxed as level text: split from their table, '3 neg' under it (2021 FM 52 q3). ->
    rotated text gets its real (vertical) box; rotated labels beside a table and whole unruled table rows right
    against it go into the table's rigid block.
145. The y-axis of a sketch standing near the column rule taken for a column rule (2025 MJ 61 q5(a)(v)). -> a vertical
    in the Answer column met by a horizontal axis inside its height is an axis.
146. A rule printed as 12 pt dashes (2014 MJ 62 p4): each dash too short for the row-rule tests -> stray lines and
    partial-marks pictures. -> pieces on one line are judged by the whole run.
147. (check) ms_words counted text printed twice on top of itself twice (tick labels of 2014 graphs): false 'missing'.
    -> the check dedups by position, like the layout.
148. (open) 2014 MJ 62: marks found 39 of 40 - q6(f)(ii) [1] is not read (QP pages 9-10 have no text for the mark
    brackets). Paper not approved until fixed.

### Round 30 (14 of 40 wrong) + round-31 Claude check
149. Stray verticals in Partial Marks (2014 MJ 11/12/13/42): the sketch-axis rule (145) took column-rule pieces for axes.
    -> axis rule only inside the Answer column (already fixed before the round-30 images were cut; verified 0 across all papers).
150. Shrunk text (2014 MJ 12 q9(c), 42 q1(e)): printed lines joined by a tall sign / a superscript were scaled as one
    block. -> (Dhruv: 'take the extra space, a whole step may start on a new line') bands split unless a fraction bar /
    stack / root joins them; a piece wider than the column wraps between parts that do not overlap in x; several
    fraction bars drawn as ONE path are split into bars; a line ending mid-step ('÷ their', '=') joins the next.
151. Boxed formula / small answer boxes as pictures (2014 MJ 62 q3, 2019 ON 53 q1) -> extract: a box around a short
    formula = text + box lines; only small empty boxes on equation lines = no diagram.
152. Two drawings side by side at one height = ONE picture (2014 MJ 43 q13).
153. Word 'double' table border drew two top edges (2021 FM 52 q4) -> corner pieces dropped, column rules reach the rule.
154. 2014 MJ 62 marks 39/40 (148): the broken text layer prints words as overlapping pieces ('(i'+'ii)', '1F'+'FT') ->
    pieces that overlap are joined; paper now 40/40.
155. Faint mark-scheme graphs (Dhruv: redraw + darken): graphs drawn as lines are redrawn by us (curves of tiny strokes
    joined into one polyline, curves darker / thicker, grey grids stay light); pasted screenshots: thin ink x 2.4
    contrast, shading keeps its tone; shaded-area sketches stay the printed picture.
156. (found in the check) a graph's grid + numbers looked like a table (coloured curve / polyline / tiny strokes =
    graph); table-rule search used fraction bars far above the grid -> grid = its verticals; rows against a table join
    it only if their cells line up with its columns and hold no words.

### Round 31 (36 of 40 ok) - M0 approved
157. A table placed at its printed height ran into OUR re-flowed text above it (2025 MJ 62 q4(b)) -> the table starts
    under our text as placed.
158. A chart's thin black frame darkened like a curve: a black box 2 pt from the y-axis (2019 ON 41 q11) -> a frame
    on the outer edges of a gridded graph is drawn light grey like the grid.
159. A Word double border's short corner pieces were outside the table-rule search (2021 FM 52 q4, 2025 MJ 62 q4(a))
    -> all rule pieces inside the grid's box (+10 pt) belong to the table.
160. (limit, not a bug) Pasted screenshot graphs (2014 MJ 31 q15 ...) are pixels only: contrast raised, never redrawn.

### M1 Claude check (2024 FM - 2026 MJ, 90 papers)
161. New equation-font codes in 2024-2026 papers: MMBinary j/k (∪ ∩), MMEtc c/g (° ⋯), EuclidMathTwo and Calibri
    F084/F085 (≤ ≥) -> MATHS_GLYPHS; maths_tex knows ⋯ ⩽ ⩾. New font: make a glyph sheet (crop each unknown code).
162. Paper-6 notice without 'task' ('The modelling starts on the next page.', 2024 MJ 61) -> layout regex.
163. MS label typo '9a)(ii)' (2024 MJ 43) -> label_text reads it as 9(a)(ii).
164. ms_align list read labels only at y == 14.0 (maths labels sit at 13.97 or lower) -> every maths question was
    listed; maths: the top Q-column word; a 4th-level label belongs to its part. (Was open since M0.)
165. 2026 MJ mark schemes: 5th column Guidance -> 5 columns, Answer : Partial : Guidance = 40 : 30 : 30 (Dhruv);
    gated by 'Guidance' in the stored MS header.
166. A fraction bar took only the numerator band; the denominator stayed its own line and another column's growth
    pushed it away -> a band ending in a bar takes the band under it (inside the bar's width).
167. Lines of one cell overlapped or ran past the row bottom when other columns' growth and the cell's own wrap met
    -> each line starts under the line placed above it (+ its printed gap); bottom = last placed ink.
168. Two fraction bars 0.06 pt apart in height (Answer and Partial Marks) joined into one rule over the Marks column
    and were dropped -> a rule run never takes a piece left of it. Also in approved M0 (2014 MJ 41 q11, 52/53 q4,
    2019 ON 42 q10, 2025 MJ 13 q7, 21 q22, 43 q17): re-shown.
169. Diagram label pieces ('Q', 'S', '65') over pasted pictures taken as a heading -> empty picture crop, crash;
    a heading line needs 4+ letters; empty crops are skipped.
170. Diagram crops: a sentence BESIDE the drawing moved the top through it (2025 ON 51 q4, half a grid lost) -> cut
    at the side (pixel test); vector pieces above (rider over scooter) chain in; axis titles up to 7 words and labels
    touching the edge are taken in (7 approved M0 crops gained their axis title / last label: re-shown).
171. A note across the table (a merged row 'For all parts accept ...', or a band inside a row 'In parts (a)(ii)(b)
    and (a)(ii)(c) ...') was cut into our columns or lost -> one full-width cell; column rules stop at a band; the
    next section's title row is never a note.
172. 4th-level labels printed without the number '(a)(ii)(b)' (2024 MJ 41 q2) -> ms.NONUM4.
173. A picture cell that fell back to text laid its heading out twice (2026 MJ 21 q7/q10, 23 q7: every word twice)
    -> the heading placement is undone when no picture is made.
174. Section-wide note 'Throughout the modelling allow ...' (2026 MJ paper 6) was glued to one question's end and
    the next's top -> ms.section_notes cuts it out and puts it on top of EVERY later question (Dhruv), one cell.
175. 2024-2025 section titles 'Modelling DELIVERIES BY SCOOTER', 'Modelling Waste Plastic', a bare 'Modelling' were
    not titles -> shown as the last row of the question before; header regex takes title words.
176. Dotted table rules printed as runs of 1 pt wide pictures were lost (2024 MJ 53 q4(a); also approved 2021 FM
    52/62: re-shown) -> 2+ thin pictures in a run = one dotted line of ours (mark schemes only).
177. A picture cell under a heading started at the drawing's top: a numerator / labels printed above the pasted piece
    were cut (2024 ON 41 q5(a)) -> the picture starts at its own first ink under the heading; a heading needs 4+
    letters (a numerator line is never a heading).
178. Every row of a table inside a cell got the fraction margin: a big gap under long tables (2024 ON 62 q1(b); also
    approved 2025 MJ 61 q1/q2: re-shown) -> table rows (2+ cell rules) are not 'tall' lines.
179. Items under a sub-row rule inside a picture cell were outside the crop and lost (2024 ON 61 q2(d) formula,
    2025 FM 62 q12 pasted '≤'); a power on the heading line was cut ('k²') -> items the crop leaves out are laid
    out as text / pictures; small raised text joins the heading line.
180. A text line under a sketch went half into the picture (short words) and half to our text: drawn twice (2025 ON
    63 q1 'Correct sketch passing through', 2025 FM 42 q9) -> the whole line goes to our text.
    Open: a small pasted symbol ('≠' image) inside a text line still makes the cell a picture and doubles the line
    (2025 FM 62 q5(b)(ii)) - sent to Dhruv's round as a recheck.
