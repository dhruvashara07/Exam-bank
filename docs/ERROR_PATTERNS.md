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

### Round 32 (M1: 12 of 30 ok; 14 of the 18 wrong should have been caught by me - START_HERE 2c)
181. Unit pictures were rendered WITH the page text: words under a clipped image's box were drawn twice and looked
    bold (2025 ON 61 q4 first line, 51 q4) -> pictures are rendered from a text-free copy of the page (maths).
182. Merged-font (AllAndNone) bold read from the page render mixed neighbouring ink: bold '(c)' missed, regular glyphs
    bold -> stroke weight from the font program's outline; a character's most used shape is regular (maths).
183. 'Question 11 is printed on the next page.' stayed in the question (38 questions, M0 too) -> page_bounds + checks.
184. Mark-scheme label slip '15(d)' for the paper's 15(c) -> one orphan row goes to the one free leaf at its level.
185. (repeat of 171, my own fix) a note band at the row's top got our rule over the row border: double edge.
186. Tables in MS cells: Dhruv 'make similar but proper' - rule pieces snap to one grid and join (no step at a shaded
    cell), a missing outer edge is drawn, stubs above the table dropped (2025 MJ 61 q2, 2014 MJ 31 q5). MS_TABLE_RULES 32.
187. Sub-row rules inside a row were dropped: answer lines no longer lined up with their marks (2025 ON 23 q15 'line
    between A1 and M1', 2026 MJ 62 q6) -> redrawn between the placed lines when every column is aligned there.
188. Steps with fractions never re-flowed; wrapped rows took the fraction's height ('7.5 oe' alone, 'of x' far below)
    -> re-flow allows bars / roots; rows aligned on baselines, each row as tall as its own pieces.
189. Calibri F084 (invisible, opacity 0, glyph 0) was mapped to '≤' (pattern 161): a second ≤ drawn -> dropped.
190. (repeat, left OPEN in round 32 - never again) a small pasted symbol in a text line made the cell a picture and
    the line was drawn twice (2025 FM 62 q5) -> a picture <= 24 x 90 pt inside a text line is a piece of the line.
191. A labelled rectangle beside a diagram (same band as NOT TO SCALE) was left out of the crop and redrawn as lines
    (2025 ON 23 q15) -> short-label / empty boxes on a NOT TO SCALE band join the diagram.
192. MS graphs printed as calculator screenshots (colour, blurry) -> drawn again from the function the question gives
    (pipeline/ms_graphs.py SPECS: function, window, ticks as on the question's axes; black curves, light grid, function
    in a box top right, 2nd curve dashed). New screenshot graph: add a SPECS line (the check sheet shows it).
193. MathType minus (MMTimesRoman '-') read as a hyphen left a gap ('5- 1/2x') -> mapped to '−' (store_text).
194. Re-flow joined lines across a printed sub-row rule ('... or better' + next sub-row '32.8 km/h' in one cell,
    2024 FM 62 q9(c); 25 questions) -> never join across a rule (ms_maths re-flow, CTX subrules).
195. A column that wraps more than printed (5-column Guidance) left no room for the sub-row rule: the rule was dropped
    -> the row under the rule moves down so the rule fits (2026 MJ 63 q6(b)).
198. A rule that would run through a line (a mark '1' beside the table above its '18', 2026 MJ 62 q6 - Dhruv round 32
    'all lines align with their answer'): the columns under the rule move down to their printed offsets (not to the
    same top: a centred cell stays lower), only where the rule would otherwise be dropped (everywhere broke good rows).
    Text around a table and the table itself now count for rules (placed_all).
199. Text under a table in a cell did not move down with the table (2024 ON 63 q6: a rule ran through 'or') -> it
    starts under the table as placed.
200. Maths notices 'Question 4(b) / 10(c)(i) and (ii) is/are printed on the next page' (6 papers, found by checks).
196. A task heading with no section letter ('Modelling   Helix', 2026 MJ 63) was not found: no intro, no task record
    -> extract.TASK_HEAD + 'You are advised' on the next lines; letter by order.
197. Paper 5/6 tasks as ONE record (Dhruv round 32): pipeline/tasks.py writes task_<S>.json (id ..._t<S>): intro as
    stem, every printed question as a part (printed numbers kept: renumber skips qnum/mslabel for type 'task'), one
    MS (header, section note once, one Total). Per-question records stay for the checks and point to it ('task').

## Round 33 (Dhruv, 2026-11-17: 9 of 23 wrong)
201. Graph labels in drawn MS graphs: small (7 pt), fractions as fractions, placed where no curve, axis or tick number
    is (ms_graphs); a label only where the printed graph has one.
202. 'y2 - y1' printed as one subscript chain (sign and second letter at subscript size): back to normal size, digits stay
    subscripts (ms_maths._sub_chain).
203. Signs in the 'symbol' face were drawn in DejaVu Sans, far wider than printed ('>' ran into '9'): signs use the
    paper's font, centred in their printed width (ms_maths OPS_SERIF).
204. A part label whose bold was not read ('(c)', 2025 ON 32 q15): bold + partlabel when it leads its part's first line.
205. An intro picture running on beside the first question (the scooter, 2024 FM 62 B) was cut at the question's top:
    its lower part joins the intro (store.paper_record).
206. Figure SVGs lost the width of every space (MuPDF redaction rewrites text runs: 'Reflectioninleftdiagonal'): each
    glyph goes back to its printed x (render._respace, maths only).
207. A formula with a root sign ('H1 = piD sqrt(1 + (h/t)^2)') was cut as a diagram: text + root sign (extract, maths).
208. An MS picture took the top of the text line under it, and tall-bracket pieces went into the picture: the picture
    stops above our text, bracket pieces and their line stay text (2026 MJ 63 q9).
Passed with reason: 2024 FM 62 task A empty magic squares are vector drawings (lines), already crisp - Dhruv: 'your call'.

## M2 (2026-11-19) - found while building the two-pass flow
209. fontTools was not in requirements.txt: on GitHub every `from fontTools ...` failed and was swallowed - ms_maths fell
    back to the physics layout ('wrap'/'scale'/'cell': Partial Marks inside Answer, codes in the Answer column) for 1682
    questions in the LAST M1 Action run, and bold / symbol-font reading (patterns 182, 108) never ran on GitHub. The M1
    approval committed that Action output: ~880 approved maths questions (M0 + M1) were in the fallback layout. This was
    also the real cause of 'local store.build differs from the Action (font family)'. -> fonttools pinned in
    requirements; run.py imports it; ImportError is never caught (ms_layout, store_units, store_text). Check: reasons.py
    ms_mode class must be 0 after every GitHub build; any 'No module named' in the Action log = stop.
210. (checks) ms_sweep tested 'code left of x 470' (physics columns): in maths every 'M1 for ...' of Partial Marks was a
    hit -> maths uses the table's own Answer / Marks edges. ms_align globbed the whole bank per question (20+ min for 11
    sessions) -> direct path (1 s).
211. (tool) Local ms_rebuild without the session's printed PDFs: every picture cell silently fell back, so the local result
    differed from the Action (164 'changes' of 253 were this, not my fixes). -> ms_rebuild.py exits unless the PDFs are
    fetched. Measure blast radius only with the PDFs on disk.
212. 2023 MJ 33: 'Answer all the questions.' with Question 1 printed 13 pt under it - the notice cut (y1 + 3) took Q1's label:
    0 questions; checks.py then crashed and left 10 papers unchecked. -> page_bounds stops above a question number;
    checks.py reports an empty paper as blocking instead of crashing.
213. A formula wider than the Partial Marks column (one fraction with a long numerator, a long root) was clipped at the
    column edge in the re-flow paths. -> the unbreakable piece is scaled to fit (>= 60 %, MS_TABLE_RULES 30).
214. A 2x2 px image stretched under a formula line (invisible mask) made the cell a 'picture': the formula was half picture,
    half text (2022 ON 43 q5(c)). -> images of <= 16 pixels are no pictures (store, maths). Open: the '[...]' dots there.
215. Re-flow joined a new marking point ('B1 for ...', 'FT ...', 'If ...') to the line above: open_end() looked at the widest
    line of a joined paragraph (ending 'or') instead of its last line. -> last printed line; code-led lines never join.
216. A question whose MS is mostly a small printed table (8 pt) got a small median size and the whole scheme was scaled to
    ~15 pt (2023 MJ 53 q6, 2023 FM 52 q1/q2). -> the paper's most used MS size decides when the question's is < 90 % of it.
217. MS labels: '12(a)(i)' printed twice (the second = 12(a)(ii)) -> rows past the first leaf's marks go to the one free
    leaf when the marks match (run.py); '5(a)(iv)' wrapped over '(b)' in the Q column -> one label 5(a)(iv)(b) (ms.py).
218. A sub-row rule was redrawn through text laid out under a cell picture ('[on third roll] ...' struck through, 2021 MJ 51
    q7). -> a rule is never drawn through a word (no rule rather than one through content).
219. Tables in MS cells fell apart: rules starting at the cell's left edge were taken for sub-row rules, and a table whose
    rows are cell fills (no row rules) was taken for a shaded picture (2023 FM 62 q1/q2). -> one-ended rules crossed by
    >= 2 column rules are table rules; fills count as row lines; >= 4 column rules over the grid = a table.
220. A line running on past a table ('x = 2 and y = 3 or x = 3 and y = 2' under the bins table) was half pulled into the
    table block: its tail drawn at the cell's left ('x = 22', 2022 MJ 61 q3). -> a printed line that does not fit the
    table's width is a sentence, never a table row.
221. One 16 pt equation-font letter ('m' of m²) made every 11 pt line of the cell 'small raised text' that joined the line
    above: words moved paragraphs and a big gap opened (2021 ON 63 q1(c)). -> 'small' is measured against the cell's
    normal size (most used), not its largest letter.
222. Labels inside a Venn frame ('Sandwich', 'Fruit') were taken as a heading: moved out as text, the frame's top cut
    (2023 ON 12 q20). -> text inside a drawn frame is never a heading.
223. A table printed at the very top of its row lost its top edge (dropped as the row's rule) and kept rule stubs (2022 FM 52
    q4). -> an inner rule with the table's own column rules hanging under it is the table's edge.
224. 2026 MJ (5 columns): no Total row at all (_own_total accepted 3-4 columns) - in the M1 approval too. -> 5 columns:
    Total in the Marks column (MS_TABLE_RULES 8). 256 approved questions gain their Total row.
225. Diagram crops kept question text above / below the drawing: the tail of 'shade A∪B.', part lines '(a) A′∪B′',
    '11 (a) On the Venn diagram ...', the question number, 'f(x) = ... for ...' under a graph, '... shape is 7√3/4.'
    (9 crops). -> fit_crop (maths): a line above / below all drawing ink that is a part line, a question number at the
    margin, a 'f(x) = ... for' line or a sentence running past the crop is cut off; strokes on a text line (|..|, roots,
    bars) are text, not drawing.
226. New equation-font codes: MathematicalPi-Six N Z Q R (ℕ ℤ ℚ ℝ), MMRelation 1 ; (⊂ ⩽), MMEtc k (…), MMaEtc g (⋯) were
    drawn as plain sans letters (q_font). -> MATHS_GLYPHS + maths_tex.
227. Page furniture at a page top / bottom: 'The modelling task starts on the next page.' at y 61 (rule needed y > 100) and
    an answer line '..... [3]' printed 0.2 pt into the box of 'Question 12 is printed on the next page.' was cut off with
    it (2021 ON 61 marks 57/60). -> notice at any height; the line above it stays.
Known open (M2, written down after 2-3 tries): a tree diagram cut into two crops (2023 MJ 32 q11), a box of words taken into
the circle's crop (2023 MJ 11 q3), a rounded formula box kept as a picture (2022 ON 61 q6), the dotted '[...]' of 2022 ON
43 q5(c) lost. Status 'known' in M2_reasons.json - fixed first in the next chat, never sent to Dhruv as items.
228. (pass 2) Pattern 225's cut stopped at the f(x) line's text box: its own fraction bar / numerator ('1' over
    '(2x-3)(2x+1)') stayed in the graph crop (2023 ON 41 q2, 2024 ON 41 q9 - approved, re-shown). -> the cut passes the
    line's own strokes and the stacked pieces just above / below it.
229. (pass 2) Pattern 219's 'grid of >= 4 columns = table' also took boxes around numbers ('2 x 5 x [2] x [5]', 2019 ON
    51/52 q1) for a table; a fill-only table lost its row lines and its row-name column fell over it (2022 FM 62 q1).
    -> the grid rule needs cell fills; fill edges become row lines; text left of the first column rule joins the table.
Lesson (M2): the pass-2 diff caught my own collateral (229) BEFORE Dhruv's round - the flow works; my one-off visual check
of a fix must include one 'look-alike that must NOT change' (boxes, grids) next to the target.
230. (pass 3) Pattern 225's 'sentence running past the crop' joined every word on the row: an axis title plus the mark
    '[2]' (2022 MJ 32 q10 lost its x axis) and two tree labels ('0.80' + 'on time') counted as one sentence. -> only the
    line's own words, chained by word gaps < 12 pt; marks '[n]' never count.
231. Figure grouping (maths): a tree printed as two clusters (2023 MJ 32 q11) -> stacked crops with only short labels
    between are one picture; two grids each with their own 'Step' text beside them in one 10 pt cluster (2023 MJ 53 q3 /
    63 q3) -> split at the empty band, never re-merged; a drawn box of words under a circle (2023 MJ 11 q3) -> its words
    are no labels and the box is text + rules; a formula in a ROUNDED box (2022 ON 61 q6) -> text + box, no picture.
(tool) reasons.py pass 2 re-judged 'verified' picture / table reasons against the newest fingerprints: 19 false 'not
fixed' in pass 3 -> verified stays verified.
232. (pass 4) My first versions of the 231 rules were too wide - the pass-4 diff showed 34 + 20 collateral questions:
    the 'rounded box = text' rule dropped real diagrams (a number line, a triangle, cubes with NOT TO SCALE), the tree
    merge joined grid rows / diagram pairs, the word-box rule cut 'x cm' labels of a shape beside another shape, and the
    stacked split broke a circle from its label. -> rounded box: ONE line >= 15 chars between full-width top and bottom
    edges; word box: one drawn rectangle with only text in it; tree merge: a branch of one crop ends at a label and a
    branch of the other leaves just right of it (a NODE); split: side text >= 15 chars and both halves >= 40 pt.
    Re-tested on all 28 affected questions: targets right, every other crop back to its pre-M2 (approved) box.
    Lesson: a grouping rule is tested on its target AND on the 20+ look-alikes the diff names, before any push.
233. (round 34 prep) After the 231 split, the lower 'Step 2' grid's stored crop grew up into the upper grid's x axis
    (fit_crop grows over ink crossing its edge). -> maths: a stored crop never grows into a sibling figure of the same
    page. Blast radius measured on all 423 figures with a sibling: 3 change (the target + 2 circles, all right).

## Round 34 (Dhruv: 6 wrong of 13; my 4 fixes: 2 wrong, 4 changed approved: 2 wrong, 5 calibration: 2 wrong)
234. MS 'boxes around numbers' (2019 ON 51 q1(a)(ii), approved before, changed by M2) got a rule drawn under the x signs
    between the boxes: _has_table added the lengths of SEPARATE rule pieces (four boxes 11-16 pt apart) and called the sum
    a row rule; _clean_table then 'added the missing outer edge' because the boxes' outer verticals reached it.
    -> a row rule is only pieces that TOUCH (<= 1.5 pt); the missing outer top/bottom edge is added only when the grid has a
    real row rule across (>= 60 % of its width). Same blast measured on all 20 maths sessions: 4 questions changed.
235. MS table 2023 FM 62 q1(a) (cells shaded in strips: top / middle / bottom strip + the whole cell on top): every strip
    edge became a row line (double / triple rules), the 5.6 pt stubs of the column rules were left outside the table block
    as loose ticks above the header, and the right outer edge (printed against the column rule) was lost.
    -> fill-only row lines come from the WHOLE cell's edges only (strips inside a larger fill are ignored); a column rule
    printed in pieces is one rule (stubs <= 8 pt that touch it go with the block); the right outer edge is drawn like the
    left one, over the header row too.
236. A column vector's brackets (2021 FM 22 q2 answer cell): the printed pieces (top, extender, bottom) are 13 pt apart
    but our piece glyphs are 8.7 pt tall -> a visible gap each side of the extender. -> ms_layout._close_brackets adds
    extenders between pieces more than 1.2 glyph heights apart (touching brackets stay as they are).
237. Question side (maths): fit_crop's 'ink crosses the edge' test is a pixel test and misses a SLANTED stroke (ink above
    and below the edge sit at other x): 2022 FM 42 q10(c) tree lost its top branch. -> maths: a stroked drawing > 12 pt
    each way that crosses the crop's top / bottom edge counts as cut and is taken in (store.FIT_SLANT).
238. Question side (maths): the two COLUMN HEADINGS above a tree ('Wears a sweatshirt', 'Goes for a walk') were left out
    of the stored figure (2022 FM 42 q10). -> two short non-sentence lines on one baseline, >= 40 pt apart, nothing else
    between them and the crop, within 34 pt above it, are part of the picture (store.FIT_HEAD).
239. MS pictures that are blurred RASTER screenshots: a handwriting-style tree (2023 MJ 32 q11(a)) and a calculator graph
    (2023 MJ 63 q12(c)(iii)) look poor next to our text. -> ms_graphs.SPECS: new 'tree' spec (two stages, probabilities
    on the branches, drawn as lines + text like the question's tree) and options 'xlab' / 'xlow' for graphs. Only the two
    flagged ones are redrawn; ALL other raster screenshots of M2 (about 60 graphs / Venn pictures) are an open decision
    for Dhruv (a batch of its own, every redraw needs the function read by eye).
Lesson (round 34): the 6 wrong items were 3 classes I had passed as 'matches print' - (a) MS pictures that match the print
but look blurred (239), (b) a stray edge inside a few-cell group (234), (c) crop rules blind to slanted strokes (237).
The 'look-alike that must NOT change' list for 234/235: every MS table with only strips or boxes (blast run = 0 more).
Tool note: `ms_rebuild.py` WITHOUT --write still rewrites msimg_*.png (byte noise, ~300 files): `git restore` them before
the commit (never commit msimg PNGs from a local run).
240. Stacked column vectors torn apart when a mark-scheme line wraps ('B1 for translation of (-5 / y) or (x / -3)': the
    second vector's top on line 1, its bottom on line 2; 2025 ON 22 q10, 2026 MJ 22 q4) and, found in the round-34 pass
    check of my own bracket fix (236): an extender run drawn between the bottom piece of one bracket and the top of another
    at the same x (a line down the whole cell, 2023 ON 41 q1 1(d)(ii)). -> ms_layout._close_brackets bridges ONLY a
    top/extender piece to the bottom/extender piece right below it (<= 3 glyph heights); ms_maths._cell merges the bands a
    bracket column spans (BRK_). maths_check ignores the extender glyphs it adds. STILL OPEN (3 questions, wrong in print
    layout only, found by the bracket-pieces scan): 2023 MJ 32 q8(c), 2026 MJ 11 q18(b), 2026 MJ 22 q6 Guidance - the vector
    brackets there are drawings in _cell, not glyphs: the same band merge must key on the drawn bracket (next chat first task).
Lesson (round 34 pass 2): a new layout rule needs the SCAN for its look-alikes before the push (here: stored rows whose
bracket tops have no matching bottom, rows with >= 5 extenders): that scan found the stray line and 6 more questions in 2 min.

## M3 (2018 MJ/ON, 2020 MJ/ON - 2026-11-23), GitHub pass 1: 182 reasons in 115 questions
241. 2018 ON 31: WHITE '[2]' / '[3]' text on the first line of a two-line answer ('Perimeter = ... cm' / 'Area = ... cm2 [2]')
    prints nothing but was read as a mark: marks 105 of 96. -> layout.visible_lines (maths) drops white mark brackets.
    Scan of all 0607 QPs: only this paper.
242. 2018 MJ 63 / 2018 ON 61: a 'Communication' row printed 6.5 pt under its full-width rule: the cut 4 pt above its text
    crossed the rule's column stubs and the lift climbed the sub-row column rules of the merged cell above - 'Justification',
    9(b) A1, 7(c)(iii) went into the communication row (marks 35/40, 38/40). -> ms.py (maths): a Communication cut never
    lifts above the rule it sits under. Also corrected approved 2019 ON 61 q5(c)(ii) (27 pt of it was in the C row).
243. 2020 ON 41 q2: labels printed without the number ('(a)(ii)') were accepted only after a page with rows; Q1 and Q2 share
    the first table page -> 7 rows lost. -> maths: accepted when a numbered label is above them on the same page.
244. MS label typos '(12b)' (2018 ON 22) and '1(ii)' after 1(b)(i) (2018 ON 42) -> label_text / the current letter (maths).
    Typos '6a)(i)', '3(b(ii)', '6b(ii)', '7c(ii)' were already read right (ms_words only: passed).
245. 2018 MJ 32 q14 / 33 q5: a whole answer line 'B ( ...... , ...... ) [2]' printed level with the next part's label: its
    mark went to the part below (part marks wrong, paper total right - only checks.piece saw it). -> the 'lone mark' cut
    rule (extract.raw_segments) takes answer lines ending in a mark (maths). Blast: 4 approved papers had the same
    defect and are corrected (2019 ON 43 q11, 2021 ON 42 q2, 2022 MJ 31 q3, 2022 MJ 42 q10).
246. fit_crop (maths) 'sentence BESIDE the drawing': a part's question line overlapping the crop top ('(iv) On the Venn
    diagram below, shade the region G'∩B') counted as beside because its own symbols / its '[1]' at the right looked like
    drawing ink: the crop lost its left half (2020 MJ 31 q11 Venn, 2018 MJ 63 q8 axes, 2020 ON 11 q8 chart). -> a line
    led by a part label is never beside; words are blanked before the beside pixel test.
247. A mapping diagram's 5 arrows are 20.7 pt apart; the 10 pt cluster rule joined only two (2018 ON 11 q15 lost rows).
    -> extract.diagrams (maths): a column of the same thin shape (same x, < 30 pt apart) is one cluster.
248. Hatched bars: hatch lines are long diagonals clipped by the bar; their whole boxes reached 80 pt into the next part
    (2020 ON 11 q8: the chart crop took q7's last line and the stem; part (a) got a text-only 'diagram'). -> extract.
    clipped_drawings (boxes cut to their clip path) in extract.diagrams and fit_crop (maths); a chart's small legend
    cluster beside it joins it.
249. Question text under a drawing not cut: 'f ( )x = x3 - ...' (italic pieces broke the f(x) regex, 2020 MJ 43 q4) and a
    full sentence with no part label ('On the grid, translate the triangle by the vector (4, -2).', 2020 ON 12 q15).
    -> fit_crop q_ test: 'f ( )x =' and a sentence of >= 6 lower-case words ending in '.'.
250. New equation-font codes: MMGreekItalic i a (θ α), MMEtc h (⋮), MMNegate 'Y' (the slash over a separate '=': kept as a
    drawn glyph) - drawn as sans letters before (q_font). Arial 'U' (universal set), Helvetica answer dots and the 96 pt
    Arial 'VRIEND' (a symmetry question) match the print: passed.
251. KNOWN OPEN (M3, 5 questions, written after the ~30 min budget): MS cell pictures broken in ms_maths - (a) a Venn picture
    with a light frame split into a frame strip + circles (2018 MJ 33 q8(b)(i), 2020 MJ 31 q11(a)(i)); (b) Venn letters that
    are tiny pasted images lost and the drawing drawn twice (2020 ON 33 q8(b)); (c) a partial-marks sketch lost (2020 ON 43
    q8(a)(iii)); (d) plotted crosses (4 strokes of 1.5 pt each) lost from a redrawn graph (2020 ON 62 q6(a)) - not dropped by
    _chain; look at the store's MS row lines first (store.py drawings for docname 'ms'). Status 'known' in M3_reasons.json.
252. KNOWN OPEN (M3): 2018 ON 61 MS - root-sign bars drawn through the text (7(a), 7(b)(i)) and bold bleeding into the next
    letters ('C op|portunity', 'Co|rrect': ms_overlap); 2018 ON 63 q6(d)(i) - four formula lines re-flowed into one
    paragraph (lines starting 'sin', 'cos' counted as a sentence going on).
Lesson (M3): a figure rule that looks fine on its target can change ~100 approved crops (an 'arrowhead = graph, not table'
rule turned every numbered coordinate grid into a picture): the full-batch figure blast (old vs new crop of every 0607
figure, pipeline/fig_blast.py) caught it before any push - run it for every extract/fit_crop change.

## Round 35 (Dhruv, 2026-11-24): 7 ok, 3 wrong (2 of them my calibration passes)
253. MS brace '}' drawn as one filled outline with ZERO-LENGTH lines and flat curve pieces inside: each one restarted the
    sub-path, so the fill fell apart into wedges (2019 ON 61 5(a)(i)). -> store_units.drawing_d (maths): such pieces keep
    the current sub-path. 27 pages of 0607 have such outlines; approved ones change only path joins (draw the same as print).
254. MS screenshot graph 2019 ON 61 5(a)(ii) redrawn from the question's model y = 12 - 1.8 cos t (ms_graphs.SPECS, grid as
    the screenshot: t every 20, y every 2 to 14).
255. Diagrams side by side / one above the other with no text between them are ONE picture, captions under them inside
    whole (never a '[2]' mark or answer dots); a one-square diagram joins its row (2020 ON 51 q1, q2). Dhruv's rule,
    round 35. Blast: 57 questions merge (all 0607); applied to M3 now, approved papers only on a later rebuild.
256. Dotty paper (>= 40 round dots on a grid) is drawn with the shapes on it - no crop of a part of it (2020 ON 51 q2(a)).
    A first version counted any 12 small dots and dropped real graph pictures (plotted points): the blast caught it.
Calibration lesson: I had passed 2020 ON 51 q2 as 'matches print' - a row of 3 separate crops matched the print but is
not what Dhruv wants (one picture). 2018 MJ 33 q5: the graph is drawn exactly (lines + text); Dhruv: drawn is fine.

## Round 37 work (2026-11-24): the 7 pending M3 papers fixed (Dhruv: 'show me what is wrong, redraw faint ones')
257. MS rows cut too high over a Venn of 1-pt image tiles: the Communication row-line floor now holds for every maths label
    (only when the cut was lifted more than 6 pt) - 2018 MJ 33 q8(b)(i), 2020 MJ 31 q11(a)(i), 2020 ON 33 q8(b), 2020 ON 43 q8
    and 14 other mark schemes (2018 MJ 42, 2019 ON 23, 2021 MJ 32, 2022 MJ 53/61, 2022 ON 63, 2023 MJ 63, 2023 ON 11, 2025 ON
    51/53/61 ...). Closes 251 (a)/(b) and 252's Venn part.
258. Venn letters pasted as narrow images (< 8 pt wide) were dropped: maths keeps images >= 4 pt wide when >= 20 pt tall (store.py).
259. Faint / screenshot MS graphs redrawn (ms_graphs.SPECS, no function label): 2020 ON 43 8(a)(iii) (column 3, vector),
    2020 ON 62 6(a) (12 plotted crosses, drawn over the line), 2018 ON 61 5(b)(i) and 6(c) (blurry screenshots with broken
    grid). A spec now also works for a vector picture ('vector': True) and for the partial-marks column ('col': 3).
260. A cell whose PDF text is unusable (root sign with no drawing of its bar, doubled bold letters) is kept as its printed
    picture by name: ms_maths.PRINTED_CELLS (2018 ON 61 7(a), 7(b)(i)).
261. A list of formulas is not re-flowed into one paragraph: a line ending with ':' or with 'oe' followed by a line with '='
    starts a new line (2018 ON 63 q6(d)(i)).
262. A white background box wider than our column made the text 'too wide' and shrank marks / partial marks to 70-88 %
    (2020 MJ 31 q11(a)(i) '2'): wide white boxes are not ink in a text cell (6 questions had it).
263. A blank line under a re-flowed sentence (the next line kept its printed place: 2018 ON 63 6(c), 6(d)(i), Dhruv round
    37): space a re-flow saves now moves the next lines up, unless the line lines up with another column (a line there at
    the same height) or a sub-row rule lies between; a wrap in the Partial Marks column beside it does not hold it down.
    Sample rebuild (2014 MJ 41, 2022 FM 62, 2024 FM 62, 2026 MJ 12, 2023 ON 11, 2025 ON 53): 13 questions tighter, no overlap.

